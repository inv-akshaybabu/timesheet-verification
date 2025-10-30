import random
import feedparser
import json
from datetime import datetime


class CategorizedRSSFeedAggregator:
    """
    A class to aggregate RSS feeds by categories based on days of the week.
    """
    
    def __init__(self, tracking_file="sent_links.json"):
        """
        Initialize the Categorized RSS Feed Aggregator with day-based feeds.
        
        Args:
            tracking_file (str): File to store sent article links for deduplication.
        """
        # Day-based categorized feeds
        self.categorized_feeds = {
            'monday': {  # Infrastructure/DevOps
                'name': 'Infrastructure & DevOps',
                'feeds': [
                    "https://devops.com/feed",
                    "https://atlassian.com/blog/devops/feed",
                    "https://www.docker.com/blog/feed/",
                    "https://devblogs.microsoft.com/devops/feed/",
                    "https://feed.infoq.com/devops",
                    "https://kubernetes.io/feed.xml",
                    "https://www.cncf.io/feed/?post_type=lf_kubeweekly",
                    "https://devopsdigest.com/blog/feed",
                    "https://aws.amazon.com/blogs/devops/feed/",
                    "https://cloud.google.com/blog/products/devops-sre/rss",
                    "https://www.redhat.com/en/rss/blog/channel/red-hat-blog"
                ]
            },
            'tuesday': {  # Python/Backend
                'name': 'Python & Backend Technologies',
                'feeds': [
                    "https://realpython.com/atom.xml",
                    "https://planetpython.org/rss20.xml",
                    "https://www.python.org/jobs/feed/rss/",
                    "https://pyfound.blogspot.com/feeds/posts/default",
                    "https://fastapi.tiangolo.com/rss.xml",
                    "https://flask.palletsprojects.com/en/2.3.x/blog/feed.atom",
                    "https://django-news.com/issues.rss",
                    "https://feeds.feedburner.com/oreilly/python",
                    "https://www.fullstackpython.com/feeds/all.atom.xml",
                    "https://blog.python.org/feeds/posts/default",
                    "https://pypi.org/rss/updates.xml"
                ]
            },
            'wednesday': {  # React/Frontend
                'name': 'React & Frontend Technologies',
                'feeds': [
                    "https://reactjs.org/feed.xml",
                    "https://blog.logrocket.com/feed/",
                    "https://css-tricks.com/feed/",
                    "https://www.smashingmagazine.com/feed/",
                    "https://blog.bitsrc.io/feed",
                    "https://dev.to/feed/tag/react",
                    "https://blog.angular.io/feed",
                    "https://vuejs.org/feed.rss",
                    "https://blog.vuejs.org/feed.rss",
                    "https://web.dev/feed.xml",
                    "https://hacks.mozilla.org/feed/",
                    "https://blog.chromium.org/feeds/posts/default"
                ]
            },
            'thursday': {  # Testing/QA
                'name': 'Testing & QA Tools',
                'feeds': [
                    "https://blog.qasource.com/rss.xml",
                    "https://dotcom-monitor.com/blog/feed",
                    "https://webomates.com/blog/feed",
                    "https://kualitatem.com/blog",
                    "https://testhouse.net/resources",
                    "https://testfort.com/blog",
                    "https://smartbear.com/blog",
                    "https://softwaretestingmagazine.com/feed",
                    "https://www.satisfice.com/blog",
                    "https://lisacrispin.com/",
                    "https://adventuresinqa.com/",
                    "https://qualityremarks.com/",
                    "https://browserstack.com/blog/rss",
                    "https://synapse-qa.com/feed",
                    "https://xndev.com/feed",
                    "https://qameta.io/blog",
                    "https://kobiton.com/blog",
                    "https://toolsqa.com/categories/blogs",
                    "https://parasoft.com/blog",
                    "https://angiejones.tech/blog",
                    "https://qainsights.com/feed",
                    "https://gatling.io/blog",
                    "https://pflb.us/blog",
                    "https://blog.octoperf.com",
                    "https://testguild.com/performance-testing/",
                    "https://blog.qamentor.com/feed",
                    "https://proqc.com/blog/feed",
                    "https://qualio.com/blog/rss.xml",
                    "https://annemariecharrett.com/rss",
                ]
            },
            'friday': {  # Fun/Interesting
                'name': 'Fun & Interesting Tech',
                'feeds': [
                    "https://xkcd.com/rss.xml",
                    "https://www.commitstrip.com/en/feed/",
                    "https://blog.codinghorror.com/rss/",
                    "https://www.joelonsoftware.com/feed/",
                    "https://blog.stackoverflow.com/feed/",
                    "https://github.blog/feed/",
                    "https://www.techmeme.com/feed.xml",
                    "https://news.ycombinator.com/rss",
                    "https://lobste.rs/rss",
                    "https://www.reddit.com/r/programming/.rss",
                    "https://www.producthunt.com/feed"
                ]
            }
        }
        
        
        # Link tracking for deduplication
        self.tracking_file = tracking_file
        self.sent_links = self._load_sent_links()
        
        # Category-specific emojis
        self.category_emojis = {
            'monday': ["🚀", "🛠️", "⚙️", "🔧", "🐳", "☸️", "🌐", "🔥"],
            'tuesday': ["🐍", "⚡", "🔥", "💻", "🚀", "📊", "🛡️", "⚙️"],
            'wednesday': ["⚛️", "🎨", "💡", "🌟", "🎯", "🔥", "📱", "✨"],
            'thursday': ["🧪", "🔍", "🎯", "✅", "🛡️", "🔧", "📊", "⚡"],
            'friday': ["😄", "🎉", "🤖", "🎮", "🎨", "💡", "🚀", "⭐"]
        }
        
        # Category-specific intro messages
        self.category_intros = {
            'monday': [
                "🚀 Monday Motivation: Infrastructure & DevOps Edition! Let's build something amazing:",
                "🛠️ Start your week strong with the latest in DevOps and Infrastructure:",
                "⚙️ Monday's DevOps digest - fuel for your infrastructure journey:",
                "🌐 Kick off the week with cutting-edge DevOps insights:",
                "🔥 Monday's infrastructure fire! Here's what's trending in DevOps:"
            ],
            'tuesday': [
                "🐍 Tuesday's Python Power! Backend technologies that'll boost your skills:",
                "⚡ Backend Tuesday: Python and server-side magic awaits:",
                "💻 Dive deep into Python and backend tech this Tuesday:",
                "🚀 Tuesday's backend bonanza - Python edition:",
                "🔥 Python & Backend Tuesday: Level up your server-side game:"
            ],
            'wednesday': [
                "⚛️ React Wednesday: Frontend frameworks and UI magic:",
                "🎨 Wednesday's frontend feast - React and beyond:",
                "💡 Mid-week frontend inspiration: React, CSS, and UI trends:",
                "🌟 Wednesday's web wonders: Frontend technologies that shine:",
                "✨ React & Frontend Wednesday: Build beautiful user experiences:"
            ],
            'thursday': [
                "🧪 Testing Thursday: QA tools and quality assurance insights:",
                "🔍 Thursday's testing toolkit: Ensure quality in every release:",
                "🎯 Quality Thursday: Testing strategies and QA innovations:",
                "✅ Thursday's QA quest: Tools and techniques for better testing:",
                "🛡️ Testing Thursday: Defend your code with quality assurance:"
            ],
            'friday': [
                "🎉 Fun Friday: Tech humor, interesting projects, and weekend inspiration:",
                "😄 Friday Fun: Lighthearted tech content to end the week:",
                "🤖 TGIF! Fun tech stories and interesting discoveries:",
                "🎮 Friday's tech playground: Fun projects and cool discoveries:",
                "⭐ Fun Friday finale: Entertaining tech content for the weekend:"
            ]
        }
        
        # Category-specific body messages
        self.category_bodies = {
            'monday': [
                "From container orchestration to cloud automation, these reads will supercharge your infrastructure game!",
                "DevOps never sleeps - stay ahead with these infrastructure insights and automation strategies.",
                "Build, deploy, scale, repeat! These articles cover the full DevOps lifecycle.",
                "Infrastructure as code, CI/CD pipelines, and cloud-native solutions await your exploration."
            ],
            'tuesday': [
                "From Django to FastAPI, async programming to microservices - Python's got it all covered!",
                "Backend brilliance awaits! Dive into APIs, databases, and server-side architecture.",
                "Python's versatility shines in these backend-focused articles and tutorials.",
                "Scale your backend knowledge with these Python and server-side technology insights."
            ],
            'wednesday': [
                "Component libraries, state management, and modern CSS - frontend development at its finest!",
                "React hooks, performance optimization, and UI/UX best practices in one place.",
                "Frontend frameworks evolve fast - stay current with these cutting-edge insights.",
                "From responsive design to progressive web apps, frontend technology keeps advancing!"
            ],
            'thursday': [
                "Test automation, quality metrics, and QA best practices to ensure bulletproof software!",
                "From unit tests to end-to-end automation - comprehensive testing strategies inside.",
                "Quality assurance tools and techniques that every developer should know.",
                "Testing isn't just about finding bugs - it's about building confidence in your code!"
            ],
            'friday': [
                "End the week with a smile! Tech humor, cool projects, and interesting discoveries.",
                "Friday fun: From coding memes to fascinating tech stories that'll brighten your day.",
                "Lighten up your Friday with entertaining tech content and weekend project inspiration!",
                "Fun tech discoveries and interesting projects to spark your weekend creativity!"
            ]
        }
        
        # Category-specific hashtags
        self.category_hashtags = {
            'monday': "#DevOps #Infrastructure #Docker #Kubernetes #AWS #CloudNative #CICD #Automation #Monitoring #SRE",
            'tuesday': "#Python #Backend #API #Django #FastAPI #Flask #Database #Microservices #ServerSide #WebDev",
            'wednesday': "#React #Frontend #JavaScript #CSS #WebDev #UI #UX #Angular #Vue #WebComponents #ResponsiveDesign",
            'thursday': "#Testing #QA #Automation #Selenium #Cypress #TestDrivenDevelopment #QualityAssurance #BugTesting #TestStrategy",
            'friday': "#TechFun #Programming #GitHub #OpenSource #TechHumor #WeekendProjects #Innovation #TechNews #Coding"
        }
    
    def _load_sent_links(self):
        try:
            with open(self.tracking_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_sent_links(self):
        with open(self.tracking_file, 'w') as f:
            json.dump(self.sent_links, f)
    
    def get_current_day_category(self):
        """
        Get the current day's category based on the day of the week.
        
        Returns:
            str: Day category (monday, tuesday, wednesday, thursday, friday)
        """
        day_mapping = {
            0: 'monday',    # Monday
            1: 'tuesday',   # Tuesday  
            2: 'wednesday', # Wednesday
            3: 'thursday',  # Thursday
            4: 'friday',    # Friday
            5: 'monday',    # Saturday -> Monday (DevOps)
            6: 'monday'     # Sunday -> Monday (DevOps)
        }
        current_day = datetime.now().weekday()
        return day_mapping[current_day]
    
    def fetch_articles_by_category(self, category):
        """
        Fetch articles from RSS feeds for a specific category.
        
        Args:
            category (str): Category name (monday, tuesday, wednesday, thursday, friday)
            
        Returns:
            list: List of dictionaries containing article titles and links.
        """
        if category not in self.categorized_feeds:
            raise ValueError(f"Category '{category}' not found. Available categories: {list(self.categorized_feeds.keys())}")
        
        articles = []
        feeds = self.categorized_feeds[category]['feeds']
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "category": category
                    })
            except Exception as e:
                print(f"Error fetching from {feed_url}: {e}")
                continue
        return articles
    
    def fetch_all_articles(self, category=None):
        """
        Fetch articles from RSS feeds. If no category specified, uses current day's category.
        
        Args:
            category (str, optional): Specific category to fetch. If None, uses current day.
            
        Returns:
            list: List of dictionaries containing article titles and links.
        """
        if category is None:
            category = self.get_current_day_category()
        
        return self.fetch_articles_by_category(category)
    
    def format_for_linkedin(self, articles, category=None):
        """
        Format articles for LinkedIn posting with category-specific styling.
        
        Args:
            articles (list): List of article dictionaries.
            category (str, optional): Category for styling. If None, uses current day.
            
        Returns:
            str: Formatted LinkedIn post content.
        """
        if category is None:
            category = self.get_current_day_category()
        
        # Get category-specific content
        intro = random.choice(self.category_intros[category])
        body = random.choice(self.category_bodies[category])
        emojis = self.category_emojis[category]
        hashtags = self.category_hashtags[category]
        
        post = intro + "\n\n" + body + "\n\n"
        
        for idx, art in enumerate(articles, 1):
            emoji = random.choice(emojis)
            post += f"{idx}. {emoji} {art['title']}  \n{art['link']}\n\n"
        
        post += f"\n{hashtags}\n"
        return post
    
    def get_random_articles(self, count=5, category=None):
        """
        Get a random selection of articles from feeds for a specific category.
        
        Args:
            count (int): Number of articles to return (default: 5).
            category (str, optional): Category to fetch from. If None, uses current day.
            
        Returns:
            list: Random selection of articles.
        """
        all_articles = self.fetch_all_articles(category)
        filtered_articles = [art for art in all_articles if art['link'] not in self.sent_links]
        if len(filtered_articles) >= count:
            return random.sample(filtered_articles, count)
        return filtered_articles
    
    def generate_linkedin_post(self, article_count=5, category=None):
        """
        Generate a complete LinkedIn post with random articles for a specific category.
        
        Args:
            article_count (int): Number of articles to include (default: 5).
            category (str, optional): Category to generate post for. If None, uses current day.
            
        Returns:
            str: Complete LinkedIn post content.
        """
        if category is None:
            category = self.get_current_day_category()
            
        articles = self.get_random_articles(article_count, category)
        post = self.format_for_linkedin(articles, category)
        
        # Track sent links
        for art in articles:
            self.sent_links.append(art['link'])
        self._save_sent_links()
        
        return post
    
    def add_feed(self, feed_url, category):
        """
        Add a new RSS feed URL to a specific category.
        
        Args:
            feed_url (str): RSS feed URL to add.
            category (str): Category to add the feed to.
        """
        if category not in self.categorized_feeds:
            raise ValueError(f"Category '{category}' not found. Available categories: {list(self.categorized_feeds.keys())}")
        
        if feed_url not in self.categorized_feeds[category]['feeds']:
            self.categorized_feeds[category]['feeds'].append(feed_url)
    
    def remove_feed(self, feed_url, category=None):
        """
        Remove an RSS feed URL from a category or all categories.
        
        Args:
            feed_url (str): RSS feed URL to remove.
            category (str, optional): Specific category to remove from. If None, removes from all.
        """
        if category:
            if category in self.categorized_feeds and feed_url in self.categorized_feeds[category]['feeds']:
                self.categorized_feeds[category]['feeds'].remove(feed_url)
        else:
            # Remove from all categories
            for cat in self.categorized_feeds:
                if feed_url in self.categorized_feeds[cat]['feeds']:
                    self.categorized_feeds[cat]['feeds'].remove(feed_url)
    
    def list_categories(self):
        """
        List all available categories and their descriptions.
        
        Returns:
            dict: Dictionary of categories with their names and feed counts.
        """
        categories = {}
        for key, value in self.categorized_feeds.items():
            categories[key] = {
                'name': value['name'],
                'feed_count': len(value['feeds']),
                'day': key.capitalize()
            }
        return categories
    
    def generate_weekly_schedule(self):
        """
        Generate a summary of the weekly RSS feed schedule.
        
        Returns:
            str: Formatted weekly schedule.
        """
        schedule = "📅 Weekly RSS Feed Schedule:\n\n"
        
        day_names = {
            'monday': 'Monday',
            'tuesday': 'Tuesday', 
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday'
        }
        
        for day, info in self.categorized_feeds.items():
            schedule += f"🗓️ {day_names[day]}: {info['name']} ({len(info['feeds'])} feeds)\n"
        
        schedule += "\n📝 Weekend posts default to Monday's DevOps content.\n"
        return schedule


if __name__ == '__main__':
    # Create an instance of the Categorized RSS Feed Aggregator
    rss_aggregator = CategorizedRSSFeedAggregator()
    
    # Display weekly schedule
    print(rss_aggregator.generate_weekly_schedule())
    
    # Show current day's category
    current_category = rss_aggregator.get_current_day_category()
    print(f"\n🗓️ Today's category: {current_category.capitalize()} - {rss_aggregator.categorized_feeds[current_category]['name']}")
    
    # Get random articles for today's category
    print(f"\n📰 Fetching articles for {current_category}...")
    picked_articles = rss_aggregator.get_random_articles(3, current_category)
    
    if picked_articles:
        print(f"\n✅ Found {len(picked_articles)} articles:")
        for i, article in enumerate(picked_articles, 1):
            print(f"{i}. {article['title'][:80]}...")
            print(f"   🔗 {article['link']}")
    else:
        print("❌ No new articles found (all may have been sent before)")
    
    # Example: Generate a complete LinkedIn post for current day
    print(f"\n📝 Generating LinkedIn post for {current_category}...")
    try:
        linkedin_post = rss_aggregator.generate_linkedin_post(3, current_category)
        print("\n" + "="*50)
        print("GENERATED LINKEDIN POST:")
        print("="*50)
        print(linkedin_post)
        print("="*50)
    except Exception as e:
        print(f"❌ Error generating post: {e}")
    
    # Show all categories
    print(f"\n📋 Available categories:")
    categories = rss_aggregator.list_categories()
    for key, info in categories.items():
        print(f"  • {info['day']}: {info['name']} ({info['feed_count']} feeds)")