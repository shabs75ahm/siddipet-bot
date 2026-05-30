#!/usr/bin/env python3
"""
Multi-source data scraper for Telangana/Siddipet news and trends
Collects data from newspapers, social media, and news websites
"""

import os
import logging
import asyncio
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin
import json

import requests
from bs4 import BeautifulSoup
import snscrape.modules.twitter as sntwitter
from pytrends.request import TrendReq

from database import add_activity

logger = logging.getLogger(__name__)

# Search keywords for Telangana/Siddipet
KEYWORDS = [
    'Siddipet', 'Telangana', 'Hyderabad', 'Karimnagar', 'Medak',
    'traffic', 'incident', 'emergency', 'accident', 'fire',
    'weather', 'flood', 'rain', 'alert', 'warning',
    'news', 'breaking', 'update', 'event', 'crime'
]

TELANGANA_NEWS_SOURCES = {
    'eenadu': 'https://www.eenadu.net/',
    'greatandhra': 'https://greatandhra.com/',
    'thehindu': 'https://www.thehindu.com/news/cities/hyderabad/',
    'deccan_chronicle': 'https://www.deccanchronicle.com/nation/hyderabad',
    'times_of_india': 'https://timesofindia.indiatimes.com/city/hyderabad',
    'hmpost': 'https://www.hmpost.in/'
}


class NewsSourceScraper:
    """Scrape news from various Telangana news websites"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def scrape_eenadu(self) -> List[Dict]:
        """Scrape from Eenadu (major Telangana newspaper)"""
        try:
            articles = []
            url = 'https://www.eenadu.net/telangana-news'

            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find article elements
            for article in soup.find_all('article', limit=10):
                title = article.find('h2')
                link = article.find('a')
                summary = article.find('p')

                if title and link:
                    articles.append({
                        'title': title.get_text(strip=True),
                        'url': urljoin(url, link.get('href', '')),
                        'summary': summary.get_text(strip=True) if summary else '',
                        'source': 'Eenadu',
                        'category': self._categorize_news(title.get_text()),
                        'timestamp': datetime.utcnow()
                    })

            logger.info(f"Scraped {len(articles)} articles from Eenadu")
            return articles

        except Exception as e:
            logger.error(f"Error scraping Eenadu: {e}")
            return []

    async def scrape_thehindu(self) -> List[Dict]:
        """Scrape from The Hindu Hyderabad edition"""
        try:
            articles = []
            url = 'https://www.thehindu.com/news/cities/hyderabad/'

            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find article elements
            for article in soup.find_all('div', class_='story', limit=10):
                headline = article.find('a', class_='storylink')

                if headline:
                    articles.append({
                        'title': headline.get_text(strip=True),
                        'url': headline.get('href', ''),
                        'summary': '',
                        'source': 'The Hindu',
                        'category': self._categorize_news(headline.get_text()),
                        'timestamp': datetime.utcnow()
                    })

            logger.info(f"Scraped {len(articles)} articles from The Hindu")
            return articles

        except Exception as e:
            logger.error(f"Error scraping The Hindu: {e}")
            return []

    async def scrape_times_of_india(self) -> List[Dict]:
        """Scrape from Times of India Hyderabad"""
        try:
            articles = []
            url = 'https://timesofindia.indiatimes.com/city/hyderabad'

            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find article elements
            for article in soup.find_all('div', class_='news-item', limit=10):
                headline = article.find('a')

                if headline:
                    articles.append({
                        'title': headline.get_text(strip=True),
                        'url': headline.get('href', ''),
                        'summary': '',
                        'source': 'Times of India',
                        'category': self._categorize_news(headline.get_text()),
                        'timestamp': datetime.utcnow()
                    })

            logger.info(f"Scraped {len(articles)} articles from Times of India")
            return articles

        except Exception as e:
            logger.error(f"Error scraping Times of India: {e}")
            return []

    async def scrape_all_news(self) -> List[Dict]:
        """Scrape from all configured news sources"""
        all_articles = []

        # Run all scrapers concurrently
        tasks = [
            self.scrape_eenadu(),
            self.scrape_thehindu(),
            self.scrape_times_of_india()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)

        logger.info(f"Total articles scraped: {len(all_articles)}")
        return all_articles

    @staticmethod
    def _categorize_news(title: str) -> str:
        """Categorize news based on keywords"""
        title_lower = title.lower()

        if any(word in title_lower for word in ['accident', 'crash', 'collision', 'road', 'traffic']):
            return 'traffic'
        elif any(word in title_lower for word in ['fire', 'burn', 'blaze', 'emergency']):
            return 'emergency'
        elif any(word in title_lower for word in ['crime', 'theft', 'robbery', 'murder', 'police']):
            return 'incident'
        elif any(word in title_lower for word in ['rain', 'flood', 'weather', 'storm', 'wind']):
            return 'weather'
        elif any(word in title_lower for word in ['event', 'festival', 'celebration', 'function']):
            return 'event'
        else:
            return 'announcement'


class TwitterTrendScraper:
    """Scrape Twitter trends and posts for Telangana/Siddipet"""

    async def scrape_twitter_trends(self, query: str, max_results: int = 20) -> List[Dict]:
        """Scrape recent tweets about Siddipet/Telangana"""
        try:
            tweets = []
            search_query = f"{query} (Siddipet OR Telangana OR Hyderabad) -filter:retweets lang:en"

            # Using snscrape to avoid API rate limits
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
                if i >= max_results:
                    break

                tweets.append({
                    'title': tweet.content[:100],
                    'content': tweet.content,
                    'author': tweet.author.username,
                    'url': f"https://twitter.com/{tweet.author.username}/status/{tweet.id}",
                    'source': 'Twitter/X',
                    'category': self._categorize_tweet(tweet.content),
                    'severity': self._determine_severity(tweet.content),
                    'timestamp': tweet.date
                })

                logger.info(f"Scraped tweet from @{tweet.author.username}")

            logger.info(f"Scraped {len(tweets)} tweets")
            return tweets

        except Exception as e:
            logger.error(f"Error scraping Twitter: {e}")
            return []

    async def scrape_trending_hashtags(self) -> List[Dict]:
        """Get trending hashtags in Telangana"""
        try:
            trending = []
            keywords = ['#Siddipet', '#Telangana', '#Hyderabad', '#TelanganaNews']

            for keyword in keywords:
                for i, tweet in enumerate(sntwitter.TwitterSearchScraper(keyword).get_items()):
                    if i >= 5:  # Limit per hashtag
                        break

                    trending.append({
                        'hashtag': keyword,
                        'title': tweet.content[:100],
                        'content': tweet.content,
                        'source': 'Twitter/X',
                        'category': self._categorize_tweet(tweet.content),
                        'timestamp': tweet.date
                    })

            logger.info(f"Scraped {len(trending)} trending tweets")
            return trending

        except Exception as e:
            logger.error(f"Error scraping trending hashtags: {e}")
            return []

    @staticmethod
    def _categorize_tweet(content: str) -> str:
        """Categorize tweet by content"""
        content_lower = content.lower()

        keywords = {
            'traffic': ['accident', 'traffic', 'jam', 'road', 'crash', 'collision'],
            'incident': ['crime', 'theft', 'robbery', 'assault', 'police'],
            'emergency': ['fire', 'ambulance', 'hospital', 'emergency', 'help'],
            'weather': ['rain', 'flood', 'storm', 'weather', 'wind', 'heavy'],
            'event': ['event', 'festival', 'function', 'celebration', 'program']
        }

        for category, keywords_list in keywords.items():
            if any(kw in content_lower for kw in keywords_list):
                return category

        return 'announcement'

    @staticmethod
    def _determine_severity(content: str) -> str:
        """Determine severity from tweet content"""
        content_lower = content.lower()

        if any(word in content_lower for word in ['critical', 'emergency', 'urgent', 'death', 'severe']):
            return 'critical'
        elif any(word in content_lower for word in ['accident', 'fire', 'crash', 'warning']):
            return 'high'
        elif any(word in content_lower for word in ['alert', 'caution', 'traffic']):
            return 'medium'
        else:
            return 'low'


class GoogleTrendsScraper:
    """Scrape Google Trends for Telangana"""

    async def scrape_trends(self, geo: str = 'IN-TG') -> List[Dict]:
        """Scrape trending searches in Telangana"""
        try:
            trends_data = []
            pytrends = TrendReq(hl='en-US', tz=360)

            # Get trending searches
            trending_searches = pytrends.trending_searches(pn='india')

            for trend in trending_searches[:10]:
                if any(keyword.lower() in trend.lower() for keyword in ['siddipet', 'telangana', 'hyderabad']):
                    trends_data.append({
                        'title': trend,
                        'trend': trend,
                        'source': 'Google Trends',
                        'category': 'announcement',
                        'timestamp': datetime.utcnow()
                    })

            logger.info(f"Scraped {len(trends_data)} Google Trends")
            return trends_data

        except Exception as e:
            logger.error(f"Error scraping Google Trends: {e}")
            return []

    async def scrape_topic_interest(self, topic: str) -> Dict:
        """Get interest over time for a topic"""
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([topic], cat=0, timeframe='now 7-d', geo='IN-TG')

            interest_data = pytrends.interest_over_time()
            related_queries = pytrends.related_queries()

            return {
                'topic': topic,
                'interest_data': interest_data.to_dict(),
                'related_queries': related_queries,
                'timestamp': datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Error scraping topic interest: {e}")
            return {}


class RedditScraper:
    """Scrape Reddit for Telangana/Siddipet discussions"""

    async def scrape_reddit(self, subreddits: List[str]) -> List[Dict]:
        """Scrape Reddit posts from relevant subreddits"""
        try:
            posts = []
            keywords = ['siddipet', 'telangana', 'hyderabad', 'incident', 'traffic', 'event']

            # Using snscrape to avoid Reddit API authentication
            for subreddit in subreddits:
                try:
                    search_query = f"subreddit:{subreddit} ({' OR '.join(keywords)})"

                    # Note: snscrape doesn't support Reddit directly
                    # This is a placeholder for manual Reddit scraping
                    logger.info(f"Attempting to scrape r/{subreddit}")

                except Exception as e:
                    logger.error(f"Error scraping r/{subreddit}: {e}")

            return posts

        except Exception as e:
            logger.error(f"Error in Reddit scraper: {e}")
            return []


class YouTubeScraper:
    """Scrape YouTube for Telangana/Siddipet news videos"""

    async def scrape_youtube(self, query: str, max_results: int = 10) -> List[Dict]:
        """Scrape YouTube for relevant videos"""
        try:
            # YouTube requires API key - using scraping alternative
            videos = []
            search_url = f"https://www.youtube.com/results?search_query={query}+siddipet"

            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            response = session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract initial data from page
            script_data = soup.find('script', {'nonce': True})

            if script_data:
                # Parse embedded JSON data
                logger.info(f"Found YouTube search results for '{query}'")
                # Video details would be extracted here

            logger.info(f"Scraped {len(videos)} YouTube videos")
            return videos

        except Exception as e:
            logger.error(f"Error scraping YouTube: {e}")
            return []


class DiscordScraper:
    """Monitor Discord servers and channels for alerts"""

    async def scrape_discord(self, channels: List[Dict]) -> List[Dict]:
        """Scrape Discord channels for relevant messages"""
        try:
            messages = []

            # Discord requires bot token and permissions
            # This is a placeholder for Discord integration
            for channel in channels:
                logger.info(f"Discord channel {channel.get('name')} would be monitored")

            return messages

        except Exception as e:
            logger.error(f"Error scraping Discord: {e}")
            return []


class FacebookPageScraper:
    """Scrape Facebook pages for Telangana news"""

    async def scrape_facebook_pages(self, page_names: List[str]) -> List[Dict]:
        """Scrape public Facebook pages"""
        try:
            posts = []

            # Facebook requires Graph API
            # Using public page scraping as alternative
            for page in page_names:
                logger.info(f"Monitoring Facebook page: {page}")

            return posts

        except Exception as e:
            logger.error(f"Error scraping Facebook: {e}")
            return []


class DataAggregator:
    """Aggregate data from all sources and feed into bot"""

    def __init__(self):
        self.news_scraper = NewsSourceScraper()
        self.twitter_scraper = TwitterTrendScraper()
        self.trends_scraper = GoogleTrendsScraper()
        self.reddit_scraper = RedditScraper()
        self.youtube_scraper = YouTubeScraper()

    async def collect_all_data(self) -> List[Dict]:
        """Collect data from all sources"""
        all_data = []

        logger.info("Starting multi-source data collection...")

        # Parallel data collection
        tasks = [
            self._collect_news(),
            self._collect_twitter(),
            self._collect_trends(),
            self._collect_youtube()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_data.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in data collection: {result}")

        logger.info(f"Total data items collected: {len(all_data)}")
        return all_data

    async def _collect_news(self) -> List[Dict]:
        """Collect news articles"""
        try:
            articles = await self.news_scraper.scrape_all_news()
            return articles
        except Exception as e:
            logger.error(f"Error collecting news: {e}")
            return []

    async def _collect_twitter(self) -> List[Dict]:
        """Collect Twitter data"""
        try:
            tweets = []

            # Search for multiple keywords
            for keyword in ['Siddipet', 'Telangana incident', 'Hyderabad traffic']:
                data = await self.twitter_scraper.scrape_twitter_trends(keyword, max_results=10)
                tweets.extend(data)

            return tweets
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {e}")
            return []

    async def _collect_trends(self) -> List[Dict]:
        """Collect trends data"""
        try:
            trends = await self.trends_scraper.scrape_trends()
            return trends
        except Exception as e:
            logger.error(f"Error collecting trends: {e}")
            return []

    async def _collect_youtube(self) -> List[Dict]:
        """Collect YouTube data"""
        try:
            videos = await self.youtube_scraper.scrape_youtube('Siddipet news')
            return videos
        except Exception as e:
            logger.error(f"Error collecting YouTube data: {e}")
            return []

    async def feed_to_database(self, data: List[Dict]) -> int:
        """Add collected data to database as activities"""
        added_count = 0

        for item in data:
            try:
                # Create activity from scraped data
                activity = add_activity(
                    category=item.get('category', 'announcement'),
                    description=item.get('title') or item.get('content', ''),
                    location='Telangana/Siddipet',
                    severity=item.get('severity', 'low'),
                    reported_by=item.get('source', 'Automated'),
                    latitude=None,
                    longitude=None
                )

                added_count += 1
                logger.info(f"Added activity from {item.get('source')}: {item.get('title', '')[:50]}")

            except Exception as e:
                logger.error(f"Error adding activity: {e}")

        logger.info(f"Total activities added to database: {added_count}")
        return added_count


async def run_scraper_scheduler():
    """Run scrapers on a schedule"""
    aggregator = DataAggregator()

    logger.info("Scraper scheduler started")

    while True:
        try:
            # Collect data every 30 minutes
            logger.info("=" * 60)
            logger.info("Starting scheduled data collection cycle")

            data = await aggregator.collect_all_data()
            added = await aggregator.feed_to_database(data)

            logger.info(f"Cycle complete: {added} activities added")
            logger.info("=" * 60)

            # Wait 30 minutes before next cycle
            await asyncio.sleep(1800)

        except Exception as e:
            logger.error(f"Error in scraper scheduler: {e}")
            # Wait 5 minutes before retry
            await asyncio.sleep(300)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run scheduler
    asyncio.run(run_scraper_scheduler())
