import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Union

import requests


@dataclass
class ProjectBugCount:
    """Data class to hold project bug count information"""
    project_id: int
    project_key: str
    project_name: str
    open_bug_count: int


class BacklogBugCounter:
    """
    A Python class to interact with Backlog API and get open bug counts for projects.
    
    Supports both API key and OAuth 2.0 authentication methods.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, access_token: Optional[str] = None):
        """
        Initialize the Backlog Bug Counter.
        
        Args:
            base_url: Your Backlog space URL (e.g., 'https://yourspace.backlog.com')
            api_key: API key for authentication (alternative to access_token)
            access_token: OAuth 2.0 access token for authentication (alternative to api_key)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.access_token = access_token
        
        if not (api_key or access_token):
            raise ValueError("Either api_key or access_token must be provided")
        
        # Set up authentication headers
        self.headers = {'Content-Type': 'application/json'}
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make an authenticated request to the Backlog API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/api/v2{endpoint}"
        
        # Add API key to params if using API key authentication
        if self.api_key:
            if params is None:
                params = {}
            params['apiKey'] = self.api_key
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def get_all_projects(self, include_archived: bool = False) -> List[Dict]:
        """
        Get all projects from Backlog.
        
        Args:
            include_archived: Whether to include archived projects
            
        Returns:
            List of project dictionaries
        """
        params = {}
        if not include_archived:
            params['archived'] = 0
            
        return self._make_request('/projects', params)
    
    def get_project_statuses(self, project_id_or_key: Union[str, int]) -> List[Dict]:
        """
        Get all statuses for a specific project.
        
        Args:
            project_id_or_key: Project ID (int) or project key (str)
            
        Returns:
            List of status dictionaries
        """
        return self._make_request(f'/projects/{project_id_or_key}/statuses')
    
    def get_open_statuses(self, project_id_or_key: Union[str, int]) -> List[int]:
        """
        Get status IDs that are considered "open" for a project.
        
        By default, this looks for statuses with names containing:
        - "Open"
        - "In Progress" 
        - "To Do"
        - "New"
        
        Args:
            project_id_or_key: Project ID (int) or project key (str)
            
        Returns:
            List of status IDs that are considered "open"
        """
        statuses = self.get_project_statuses(project_id_or_key)
        
        open_keywords = ['open', 'in progress', 'to do', 'new', 'todo', 'active']
        open_status_ids = []
        
        for status in statuses:
            status_name = status['name'].lower()
            if any(keyword in status_name for keyword in open_keywords):
                open_status_ids.append(status['id'])
                self.logger.info(f"Found open status: {status['name']} (ID: {status['id']})")
        
        return open_status_ids
    
    def count_issues(self, project_id: int, status_ids: List[int] = None, 
                    issue_type_ids: List[int] = None, **kwargs) -> int:
        """
        Count issues for a project with given filters.
        
        Args:
            project_id: Project ID
            status_ids: List of status IDs to filter by
            issue_type_ids: List of issue type IDs to filter by (e.g., bug types)
            **kwargs: Additional filter parameters supported by the API
            
        Returns:
            Number of issues matching the criteria
        """
        params = {'projectId[]': project_id}
        
        if status_ids:
            params['statusId[]'] = status_ids
            
        if issue_type_ids:
            params['issueTypeId[]'] = issue_type_ids
        
        # Add any additional filters
        params.update(kwargs)
        
        response = self._make_request('/issues/count', params)
        return response.get('count', 0)
    
    def get_open_bug_count_for_project(self, project_id_or_key: Union[str, int], 
                                     bug_type_ids: List[int] = None) -> ProjectBugCount:
        """
        Get the count of open bugs for a specific project.
        
        Args:
            project_id_or_key: Project ID (int) or project key (str)
            bug_type_ids: List of issue type IDs that represent bugs. 
                         If None, counts all issue types with open status.
            
        Returns:
            ProjectBugCount object with project info and open bug count
        """
        # First get project info
        if isinstance(project_id_or_key, str):
            # If it's a project key, we need to get projects to find the ID
            projects = self.get_all_projects()
            project = next((p for p in projects if p['projectKey'] == project_id_or_key), None)
            if not project:
                raise ValueError(f"Project with key '{project_id_or_key}' not found")
        else:
            # If it's a project ID, get the specific project info
            projects = self.get_all_projects()
            project = next((p for p in projects if p['id'] == project_id_or_key), None)
            if not project:
                raise ValueError(f"Project with ID '{project_id_or_key}' not found")
        
        # Get open statuses for this project
        open_status_ids = self.get_open_statuses(project['id'])
        
        if not open_status_ids:
            self.logger.warning(f"No open statuses found for project {project['name']}")
            return ProjectBugCount(
                project_id=project['id'],
                project_key=project['projectKey'],
                project_name=project['name'],
                open_bug_count=0
            )
        
        # Count open issues (bugs)
        open_bug_count = self.count_issues(
            project_id=project['id'],
            status_ids=open_status_ids,
            issue_type_ids=bug_type_ids
        )
        
        return ProjectBugCount(
            project_id=project['id'],
            project_key=project['projectKey'],
            project_name=project['name'],
            open_bug_count=open_bug_count
        )
    
    def get_open_bug_count_for_all_projects(self, bug_type_ids: List[int] = None, 
                                          include_archived: bool = False) -> List[ProjectBugCount]:
        """
        Get the count of open bugs for all projects.
        
        Args:
            bug_type_ids: List of issue type IDs that represent bugs. 
                         If None, counts all issue types with open status.
            include_archived: Whether to include archived projects
            
        Returns:
            List of ProjectBugCount objects for all projects
        """
        projects = self.get_all_projects(include_archived=include_archived)
        results = []
        
        for project in projects:
            try:
                bug_count = self.get_open_bug_count_for_project(
                    project['id'], 
                    bug_type_ids=bug_type_ids
                )
                results.append(bug_count)
                self.logger.info(f"Project '{project['name']}': {bug_count.open_bug_count} open bugs")
            except Exception as e:
                self.logger.error(f"Failed to get bug count for project {project['name']}: {e}")
                # Continue with other projects
                continue
        
        return results
    
    def get_total_open_bug_count(self, bug_type_ids: List[int] = None, 
                               include_archived: bool = False) -> int:
        """
        Get the total count of open bugs across all projects.
        
        Args:
            bug_type_ids: List of issue type IDs that represent bugs
            include_archived: Whether to include archived projects
            
        Returns:
            Total number of open bugs across all projects
        """
        project_bug_counts = self.get_open_bug_count_for_all_projects(
            bug_type_ids=bug_type_ids,
            include_archived=include_archived
        )
        
        total_count = sum(pbc.open_bug_count for pbc in project_bug_counts)
        self.logger.info(f"Total open bugs across all projects: {total_count}")
        
        return total_count


# Example usage
if __name__ == "__main__":
    # Initialize with API key
    counter = BacklogBugCounter(
        base_url="https://ilabs.backlog.com/",
        api_key="nNWwAGp2cC3DLXLMoMOYHpcP9G05kaJdVHaC3QYuuh05ezZ8L9w3iE4EMq8ajiwI"
    )

    try:
        # Get open bug count for a specific project
        project_bugs = counter.get_open_bug_count_for_project("CMIC_SFC")  # Using project key
        print(f"Project {project_bugs.project_name} has {project_bugs.open_bug_count} open bugs")

    except Exception as e:
        print(f"Error: {e}")

