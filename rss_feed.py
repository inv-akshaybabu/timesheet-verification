import random
import feedparser
import json


class RSSFeedAggregator:
    """
    A class to aggregate RSS feeds and format them for social media posting.
    """
    
    def __init__(self, feeds=None, tracking_file="sent_links.json"):
        """
        Initialize the RSS Feed Aggregator with link deduplication.
        
        Args:
            feeds (list): List of RSS feed URLs. If None, uses default DevOps feeds.
            tracking_file (str): File to store sent article links for deduplication.
        """
        self.feeds = feeds or [
            "https://devops.com/feed",
            "https://atlassian.com/blog/devops/feed",
            "https://www.docker.com/blog/feed/",
            "https://devblogs.microsoft.com/devops/feed/",
            "https://feed.infoq.com/devops",
            "https://kubernetes.io/feed.xml",
            "https://www.cncf.io/feed/?post_type=lf_kubeweekly",
            "https://devopsdigest.com/blog/feed"
        ]
        
        # Link tracking for deduplication
        self.tracking_file = tracking_file
        self.sent_links = self._load_sent_links()
        
        self.emojis = ["🚀", "🛠️", "💡", "⚡", "🔥", "📢", "🌐", "🔧", "🔍", "📰", "🤖", "🎯"]
        
        self.intro_flavors = [
            "🔥 Here's your daily hit of DevOps fire! Check out what's trending in the tech world today:",
            "🚀 Ready to power up your DevOps game? Dive into the latest and greatest from the tech frontier:",
            "💡 Curated DevOps wisdom for your feed! Here are a few fresh reads for your day:",
            "🛠️ DevOps never sleeps—see what's making waves right now:",
            "🔔 Hot off the press! DevOps stories that caught our eye:",
            "🌐 A quick scan of DevOps news to keep you sharp:",
            "📈 Stay on the bleeding edge: today's most-discussed DevOps updates:",
            "🎯 Sharpen your skills! The best DevOps articles we found today:",
            "🤖 Embrace automation and innovation: check these out!",
            "⚡ Supercharge your Day with the latest DevOps news:",
        ]
        
        self.body_flavors = [
            "From cloud-native revolutions to CI/CD game-changers, these articles pack some serious engineering inspiration. 🚦",
            "Stay informed, get inspired, and join in the conversation—your next big idea may be in one of these stories!",
            "Level up your DevOps journey—explore lessons, trends, and innovations taking teams by storm.",
            "Your learning shouldn't stop—these reads might just lead to your next breakthrough solution.",
            "Big ideas, tough lessons, clever hacks: every link is handpicked to amplify your DevOps thinking!",
            "Momentum in tech never slows—catch up with this batch of insightful, actionable reading.",
            "Innovation is only a click away. Open, read, and stay ahead of the curve.",
            "Unleash your curiosity—today's topics cut across automation, security, containers and more.",
            "Bite-sized brilliance for busy engineers! Start a conversation or solve a problem with these picks.",
            "Whether you're scaling or just starting, there's wisdom here for every DevOps journey.",
        ]
    
    def _load_sent_links(self):
        try:
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_sent_links(self):
        with open(self.tracking_file, 'w') as f:
            json.dump(self.sent_links, f)
    
    def fetch_all_articles(self):
        """
        Fetch articles from all configured RSS feeds.
        
        Returns:
            list: List of dictionaries containing article titles and links.
        """
        articles = []
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    articles.append({
                        "title": entry.title,
                        "link": entry.link
                    })
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        return articles
    
    def format_for_linkedin(self, articles):
        """
        Format articles for LinkedIn posting.
        
        Args:
            articles (list): List of article dictionaries.
            
        Returns:
            str: Formatted LinkedIn post content.
        """
        intro = random.choice(self.intro_flavors)
        body = random.choice(self.body_flavors)
        post = intro + "\n\n" + body + "\n\n"
        
        for idx, art in enumerate(articles, 1):
            emoji = random.choice(self.emojis)
            post += f"{idx}. {emoji} {art['title']}  \n{art['link']}\n\n"
        
        post += "\n#DevOps #TechNews #Automation #Cloud #GitOps #CICD #Kubernetes #Linux\n"
        return post
    
    def get_random_articles(self, count=5):
        """
        Get a random selection of articles from all feeds.
        
        Args:
            count (int): Number of articles to return (default: 5).
            
        Returns:
            list: Random selection of articles.
        """
        all_articles = self.fetch_all_articles()
        filtered_articles = [art for art in all_articles if art['link'] not in self.sent_links]
        if len(filtered_articles) >= count:
            return random.sample(filtered_articles, count)
        return filtered_articles
    
    def generate_linkedin_post(self, article_count=5):
        """
        Generate a complete LinkedIn post with random articles.
        
        Args:
            article_count (int): Number of articles to include (default: 5).
            
        Returns:
            str: Complete LinkedIn post content.
        """
        articles = self.get_random_articles(article_count)
        post = self.format_for_linkedin(articles)
        for art in articles:
            self.sent_links.append(art['link'])
        self._save_sent_links()
        return post
    
    def add_feed(self, feed_url):
        """
        Add a new RSS feed URL to the aggregator.
        
        Args:
            feed_url (str): RSS feed URL to add.
        """
        if feed_url not in self.feeds:
            self.feeds.append(feed_url)
    
    def remove_feed(self, feed_url):
        """
        Remove an RSS feed URL from the aggregator.
        
        Args:
            feed_url (str): RSS feed URL to remove.
        """
        if feed_url in self.feeds:
            self.feeds.remove(feed_url)


if __name__ == '__main__':
    # Create an instance of the RSS Feed Aggregator
    rss_aggregator = RSSFeedAggregator()
    
    # Get random articles and print them
    picked_articles = rss_aggregator.get_random_articles(5)
    print(picked_articles)
    
    # Example: Generate a complete LinkedIn post
    # linkedin_post = rss_aggregator.generate_linkedin_post()
    # print(linkedin_post)