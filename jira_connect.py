import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
from dotenv import load_dotenv

load_dotenv()

class JiraConnect:
    """
    A class to connect to Jira API and retrieve project information,
    specifically focused on getting the next release date for a given project.
    """

    def __init__(self, jira_url: Optional[str] = None, username: Optional[str] = None,
                 api_token: Optional[str] = None):
        """
        Initialize the Jira connector.

        Args:
            jira_url: Jira instance URL (e.g., 'https://yourcompany.atlassian.net')
            username: Jira username/email
            api_token: Jira API token
        """
        self.jira_url = jira_url or os.getenv('JIRA_URL')
        self.username = username or os.getenv('JIRA_USERNAME')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')

        if not all([self.jira_url, self.username, self.api_token]):
            raise ValueError("Jira URL, username, and API token are required")

        # Remove trailing slash from URL if present
        self.jira_url = self.jira_url.rstrip('/')

        # Setup authentication
        self.auth = (self.username, self.api_token)

        # Setup headers
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a request to the Jira API.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            JSON response or None if request failed
        """
        url = f"{self.jira_url}/rest/api/3/{endpoint}"

        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to {url}: {e}")
            return None

    def get_project_info(self, project_key: str) -> Optional[Dict]:
        """
        Get basic project information.

        Args:
            project_key: Jira project key (e.g., 'PROJ')

        Returns:
            Project information dictionary or None if not found
        """
        return self._make_request(f"project/{project_key}")

    def get_project_versions(self, project_key: str) -> List[Dict]:
        """
        Get all versions for a project.

        Args:
            project_key: Jira project key

        Returns:
            List of version dictionaries
        """
        result = self._make_request(f"project/{project_key}/versions")
        return result if result else []

    def get_next_release_date(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        Get the next release date for a given project.

        Args:
            project_key: Jira project key

        Returns:
            Dictionary containing next release information:
            {
                'version_name': str,
                'release_date': str (YYYY-MM-DD format),
                'description': str,
                'is_released': bool,
                'days_until_release': int
            }
            Returns None if no upcoming releases found
        """
        try:
            # Get project info first to validate project exists
            project_info = self.get_project_info(project_key)
            if not project_info:
                self.logger.error(f"Project {project_key} not found")
                return None

            # Get all versions for the project
            versions = self.get_project_versions(project_key)
            if not versions:
                self.logger.warning(f"No versions found for project {project_key}")
                return None

            # Filter unreleased versions with release dates
            upcoming_releases = []
            current_date = datetime.now().date()

            for version in versions:
                # Skip if already released
                if version.get('released', False):
                    continue

                # Skip if no release date set
                release_date_str = version.get('releaseDate')
                if not release_date_str:
                    continue

                try:
                    # Parse release date
                    release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()

                    # Only include future releases
                    if release_date >= current_date:
                        days_until = (release_date - current_date).days
                        upcoming_releases.append({
                            'version_name': version.get('name', 'Unknown'),
                            'release_date': release_date_str,
                            'description': version.get('description', ''),
                            'is_released': version.get('released', False),
                            'days_until_release': days_until,
                            'version_id': version.get('id'),
                            'project_id': version.get('projectId')
                        })
                except ValueError as e:
                    self.logger.warning(f"Invalid date format for version {version.get('name')}: {e}")
                    continue

            if not upcoming_releases:
                self.logger.info(f"No upcoming releases found for project {project_key}")
                return None

            # Sort by release date and return the next one
            upcoming_releases.sort(key=lambda x: x['release_date'])
            next_release = upcoming_releases[0]

            self.logger.info(f"Next release for {project_key}: {next_release['version_name']} on {next_release['release_date']}")
            return next_release

        except Exception as e:
            self.logger.error(f"Error getting next release date for {project_key}: {e}")
            return None

    def get_all_upcoming_releases(self, project_key: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get all upcoming releases for a project, sorted by release date.

        Args:
            project_key: Jira project key
            limit: Maximum number of releases to return

        Returns:
            List of release dictionaries
        """
        try:
            versions = self.get_project_versions(project_key)
            if not versions:
                return []

            upcoming_releases = []
            current_date = datetime.now().date()

            for version in versions:
                if version.get('released', False):
                    continue

                release_date_str = version.get('releaseDate')
                if not release_date_str:
                    continue

                try:
                    release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                    if release_date >= current_date:
                        days_until = (release_date - current_date).days
                        upcoming_releases.append({
                            'version_name': version.get('name', 'Unknown'),
                            'release_date': release_date_str,
                            'description': version.get('description', ''),
                            'is_released': version.get('released', False),
                            'days_until_release': days_until,
                            'version_id': version.get('id'),
                            'project_id': version.get('projectId')
                        })
                except ValueError:
                    continue

            # Sort by release date and return limited results
            upcoming_releases.sort(key=lambda x: x['release_date'])
            return upcoming_releases[:limit]

        except Exception as e:
            self.logger.error(f"Error getting upcoming releases for {project_key}: {e}")
            return []

    def test_connection(self) -> bool:
        """
        Test the Jira connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            result = self._make_request("myself")
            if result:
                self.logger.info(f"Successfully connected to Jira as {result.get('displayName', 'Unknown')}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


# Example usage and utility functions
def format_release_info(release_info: Dict[str, Any]) -> str:
    """
    Format release information for display.

    Args:
        release_info: Release information dictionary

    Returns:
        Formatted string
    """
    if not release_info:
        return "No upcoming releases found"

    days = release_info['days_until_release']
    day_text = "day" if days == 1 else "days"

    return (f"Next Release: {release_info['version_name']}\n"
            f"Date: {release_info['release_date']}\n"
            f"Days until release: {days} {day_text}\n"
            f"Description: {release_info['description'] or 'No description'}")


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize Jira connector
        jira = JiraConnect()

        # Test connection
        if jira.test_connection():
            print("✅ Jira connection successful!")

            # Example: Get next release for a project
            project_key = "PROJ"  # Replace with your project key
            next_release = jira.get_next_release_date(project_key)

            if next_release:
                print(f"\n{format_release_info(next_release)}")
            else:
                print(f"No upcoming releases found for project {project_key}")

        else:
            print("❌ Jira connection failed!")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file and ensure JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN are set")
