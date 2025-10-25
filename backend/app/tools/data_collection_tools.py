"""
Advanced Data Collection Tools for Live Social Media Monitoring
These tools give our AI system "eyes and ears" to see the digital world
"""

import asyncio
import aiohttp
import time
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re
from urllib.parse import quote_plus

import tweepy
import praw
from langchain.tools import BaseTool
from loguru import logger

from app.core.config import settings


@dataclass
class SocialMediaMention:
    """Standardized format for all social media mentions"""
    platform: str
    external_id: str
    author: str
    content: str
    url: str
    created_at: datetime
    engagement_metrics: Dict[str, int]
    metadata: Dict[str, Any]
    brand_keywords_found: List[str]


class TwitterDataTool(BaseTool):
    """LangChain tool for collecting Twitter data using Twitter API v2"""
    
    name: str = "collect_twitter_data"
    description: str = "Collect recent tweets mentioning specific keywords or brands. Returns formatted tweet data with engagement metrics."
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = None
        self._initialize_twitter_client()
    
    @property
    def client(self):
        """Property to access the Twitter client"""
        return self._client
    
    def _initialize_twitter_client(self):
        """Initialize Twitter API client"""
        try:
            if settings.TWITTER_BEARER_TOKEN:
                self._client = tweepy.Client(
                    bearer_token=settings.TWITTER_BEARER_TOKEN,
                    wait_on_rate_limit=True
                )
                logger.info("✅ Twitter API client initialized")
            else:
                logger.warning("⚠️ Twitter Bearer Token not configured - using mock data")
        except Exception as e:
            logger.error(f"❌ Twitter API initialization failed: {e}")
    
    def _run(self, keywords: str, max_results: int = 20, hours_back: int = 24) -> str:
        """Collect Twitter data synchronously"""
        try:
            if not self.client:
                return self._mock_twitter_data(keywords, max_results)
            
            # Build search query
            keyword_list = [k.strip() for k in keywords.split(",")]
            query = " OR ".join([f'"{kw}"' for kw in keyword_list]) + " -is:retweet"
            
            # Search for tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=["id", "text", "created_at", "public_metrics", "author_id", "context_annotations"],
                user_fields=["username", "name", "verified"],
                expansions=["author_id"]
            )
            
            if not tweets.data:
                return json.dumps({
                    "platform": "twitter",
                    "mentions_found": 0,
                    "keywords_searched": keyword_list,
                    "message": "No tweets found for the specified keywords"
                })
            
            # Process tweets
            mentions = []
            users_dict = {user.id: user for user in tweets.includes.get('users', [])}
            
            for tweet in tweets.data:
                author_info = users_dict.get(tweet.author_id, {})
                
                mention = {
                    "platform": "twitter",
                    "external_id": str(tweet.id),
                    "author": getattr(author_info, 'username', 'unknown'),
                    "author_name": getattr(author_info, 'name', 'Unknown User'),
                    "content": tweet.text,
                    "url": f"https://twitter.com/{getattr(author_info, 'username', 'unknown')}/status/{tweet.id}",
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "engagement_metrics": {
                        "likes": getattr(tweet.public_metrics, 'like_count', 0),
                        "retweets": getattr(tweet.public_metrics, 'retweet_count', 0),
                        "replies": getattr(tweet.public_metrics, 'reply_count', 0),
                        "quotes": getattr(tweet.public_metrics, 'quote_count', 0)
                    },
                    "metadata": {
                        "author_verified": getattr(author_info, 'verified', False),
                        "context_annotations": tweet.context_annotations or []
                    },
                    "brand_keywords_found": [kw for kw in keyword_list if kw.lower() in tweet.text.lower()]
                }
                mentions.append(mention)
            
            result = {
                "platform": "twitter",
                "mentions_found": len(mentions),
                "keywords_searched": keyword_list,
                "collection_timestamp": datetime.utcnow().isoformat(),
                "mentions": mentions
            }
            
            logger.info(f"✅ Collected {len(mentions)} Twitter mentions for keywords: {keyword_list}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Twitter data collection failed: {e}")
            return json.dumps({
                "platform": "twitter",
                "error": str(e),
                "fallback_data": self._mock_twitter_data(keywords, max_results)
            })
    
    async def _arun(self, keywords: str, max_results: int = 20, hours_back: int = 24) -> str:
        """Collect Twitter data asynchronously"""
        return self._run(keywords, max_results, hours_back)
    
    def _mock_twitter_data(self, keywords: str, max_results: int) -> Dict[str, Any]:
        """Generate realistic mock Twitter data"""
        keyword_list = [k.strip() for k in keywords.split(",")]
        
        mock_mentions = []
        for i in range(min(max_results, 5)):  # Generate up to 5 mock tweets
            mention = {
                "platform": "twitter",
                "external_id": f"mock_tweet_{int(time.time())}_{i}",
                "author": f"user_{i + 1}",
                "author_name": f"Test User {i + 1}",
                "content": f"Just had an experience with {keyword_list[0] if keyword_list else 'the brand'}. {'Great service!' if i % 2 == 0 else 'Could be improved.'}",
                "url": f"https://twitter.com/user_{i+1}/status/mock_{i}",
                "created_at": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "engagement_metrics": {
                    "likes": (i + 1) * 10,
                    "retweets": i * 5,
                    "replies": i * 2,
                    "quotes": i
                },
                "metadata": {
                    "author_verified": i == 0,
                    "context_annotations": []
                },
                "brand_keywords_found": keyword_list[:1]
            }
            mock_mentions.append(mention)
        
        return {
            "platform": "twitter",
            "mentions_found": len(mock_mentions),
            "keywords_searched": keyword_list,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "mentions": mock_mentions,
            "mock_mode": True
        }


class RedditDataTool(BaseTool):
    """LangChain tool for collecting Reddit data"""
    
    name: str = "collect_reddit_data"
    description: str = "Collect recent Reddit posts and comments mentioning specific keywords or brands. Returns formatted Reddit data."
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._reddit = None
        self._initialize_reddit_client()
    
    @property
    def reddit(self):
        """Property to access the Reddit client"""
        return self._reddit
    
    def _initialize_reddit_client(self):
        """Initialize Reddit API client"""
        try:
            if all([settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET, settings.REDDIT_USER_AGENT]):
                self._reddit = praw.Reddit(
                    client_id=settings.REDDIT_CLIENT_ID,
                    client_secret=settings.REDDIT_CLIENT_SECRET,
                    user_agent=settings.REDDIT_USER_AGENT
                )
                logger.info("✅ Reddit API client initialized")
            else:
                logger.warning("⚠️ Reddit API credentials not configured - using mock data")
        except Exception as e:
            logger.error(f"❌ Reddit API initialization failed: {e}")
    
    def _run(self, keywords: str, max_results: int = 20, subreddits: str = "all") -> str:
        """Collect Reddit data synchronously"""
        try:
            if not self.reddit:
                return json.dumps(self._mock_reddit_data(keywords, max_results))
            
            keyword_list = [k.strip() for k in keywords.split(",")]
            subreddit_list = [s.strip() for s in subreddits.split(",")]
            
            mentions = []
            
            # Search in specified subreddits
            for subreddit_name in subreddit_list:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for posts containing keywords
                    for keyword in keyword_list:
                        search_results = subreddit.search(keyword, limit=max_results//len(keyword_list)//len(subreddit_list), time_filter="week")
                        
                        for submission in search_results:
                            mention = {
                                "platform": "reddit",
                                "external_id": submission.id,
                                "author": str(submission.author) if submission.author else "[deleted]",
                                "content": f"{submission.title}\n\n{submission.selftext}",
                                "url": f"https://reddit.com{submission.permalink}",
                                "created_at": datetime.fromtimestamp(submission.created_utc).isoformat(),
                                "engagement_metrics": {
                                    "upvotes": submission.ups,
                                    "downvotes": submission.downs,
                                    "comments": submission.num_comments,
                                    "score": submission.score
                                },
                                "metadata": {
                                    "subreddit": submission.subreddit.display_name,
                                    "post_type": "submission",
                                    "over_18": submission.over_18,
                                    "stickied": submission.stickied
                                },
                                "brand_keywords_found": [kw for kw in keyword_list if kw.lower() in (submission.title + " " + submission.selftext).lower()]
                            }
                            mentions.append(mention)
                            
                            if len(mentions) >= max_results:
                                break
                        
                        if len(mentions) >= max_results:
                            break
                    
                    if len(mentions) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error searching subreddit {subreddit_name}: {e}")
                    continue
            
            result = {
                "platform": "reddit",
                "mentions_found": len(mentions),
                "keywords_searched": keyword_list,
                "subreddits_searched": subreddit_list,
                "collection_timestamp": datetime.utcnow().isoformat(),
                "mentions": mentions
            }
            
            logger.info(f"✅ Collected {len(mentions)} Reddit mentions")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Reddit data collection failed: {e}")
            return json.dumps({
                "platform": "reddit",
                "error": str(e),
                "fallback_data": self._mock_reddit_data(keywords, max_results)
            })
    
    async def _arun(self, keywords: str, max_results: int = 20, subreddits: str = "all") -> str:
        """Collect Reddit data asynchronously"""
        return self._run(keywords, max_results, subreddits)
    
    def _mock_reddit_data(self, keywords: str, max_results: int) -> Dict[str, Any]:
        """Generate mock Reddit data"""
        keyword_list = [k.strip() for k in keywords.split(",")]
        
        mock_mentions = []
        for i in range(min(max_results, 3)):
            mention = {
                "platform": "reddit",
                "external_id": f"mock_reddit_{int(time.time())}_{i}",
                "author": f"redditor_{i + 1}",
                "content": f"Discussion about {keyword_list[0] if keyword_list else 'the brand'}: {'Positive experience here!' if i % 2 == 0 else 'Had some issues but support helped.'}",
                "url": f"https://reddit.com/r/test/comments/mock_{i}",
                "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "engagement_metrics": {
                    "upvotes": (i + 1) * 15,
                    "downvotes": i * 2,
                    "comments": i * 8,
                    "score": (i + 1) * 13
                },
                "metadata": {
                    "subreddit": "test",
                    "post_type": "submission",
                    "over_18": False,
                    "stickied": False
                },
                "brand_keywords_found": keyword_list[:1]
            }
            mock_mentions.append(mention)
        
        return {
            "platform": "reddit",
            "mentions_found": len(mock_mentions),
            "keywords_searched": keyword_list,
            "subreddits_searched": ["test"],
            "collection_timestamp": datetime.utcnow().isoformat(),
            "mentions": mock_mentions,
            "mock_mode": True
        }


class NewsDataTool(BaseTool):
    """LangChain tool for collecting news articles and press coverage using NewsAPI"""
    
    name: str = "collect_news_data"
    description: str = "Collect recent news articles mentioning specific keywords or brands using NewsAPI. Returns formatted news data."
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api_key = settings.NEWSAPI_KEY
        self._base_url = "https://newsapi.org/v2/everything"
        logger.debug(f"NewsDataTool initialized with API key: {self._api_key[:10] if self._api_key else 'None'}...")
    
    def _run(self, keywords: str, max_results: int = 10, days_back: int = 7) -> str:
        """Collect news data using NewsAPI"""
        try:
            keyword_list = [k.strip() for k in keywords.split(",")]
            
            # Check if API key is configured
            if not self._api_key or self._api_key.startswith("your_"):
                logger.warning("⚠️ NewsAPI key not configured - using mock data")
                return self._mock_news_data(keywords, max_results)
            
            # Build search query
            query = " OR ".join([f'"{kw}"' for kw in keyword_list])
            
            # Calculate date range
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            # Make API request
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'pageSize': min(max_results, 100),  # API limit
                'language': 'en',
                'apiKey': self._api_key
            }
            
            response = requests.get(self._base_url, params=params, timeout=10)
            
            if response.status_code == 401:
                logger.error(f"❌ NewsAPI authentication failed. Please verify your API key at https://newsapi.org/")
                logger.error(f"Current key: {self._api_key[:8]}...{self._api_key[-4:]}")
                return self._mock_news_data(keywords, max_results)
            
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return self._mock_news_data(keywords, max_results)
            
            articles_data = data.get('articles', [])
            
            if not articles_data:
                result = {
                    "platform": "news",
                    "articles_found": 0,
                    "keywords_searched": keyword_list,
                    "collection_timestamp": datetime.utcnow().isoformat(),
                    "articles": [],
                    "message": "No articles found for the specified keywords"
                }
                return json.dumps(result, indent=2)
            
            # Process articles
            articles = []
            for article in articles_data[:max_results]:
                processed_article = {
                    "platform": "news",
                    "external_id": article.get('url', ''),
                    "author": article.get('author', 'Unknown'),
                    "title": article.get('title', ''),
                    "description": article.get('description', ''),
                    "content": article.get('content', ''),
                    "url": article.get('url', ''),
                    "published_date": article.get('publishedAt', ''),
                    "created_at": article.get('publishedAt', ''),
                    "metadata": {
                        "source": article.get('source', {}).get('name', 'Unknown'),
                        "source_id": article.get('source', {}).get('id', ''),
                        "url_to_image": article.get('urlToImage', '')
                    },
                    "brand_keywords_found": [kw for kw in keyword_list if kw.lower() in (article.get('title', '') + ' ' + article.get('description', '')).lower()]
                }
                articles.append(processed_article)
            
            result = {
                "platform": "news",
                "articles_found": len(articles),
                "keywords_searched": keyword_list,
                "collection_timestamp": datetime.utcnow().isoformat(),
                "articles": articles,
                "api_source": "NewsAPI",
                "total_results": data.get('totalResults', 0)
            }
            
            logger.info(f"✅ Collected {len(articles)} news articles from NewsAPI (total available: {data.get('totalResults', 0)})")
            return json.dumps(result, indent=2)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ NewsAPI request failed: {e}")
            return self._mock_news_data(keywords, max_results)
        except Exception as e:
            logger.error(f"❌ News data collection failed: {e}")
            return json.dumps({"platform": "news", "error": str(e)})
    
    def _mock_news_data(self, keywords: str, max_results: int) -> str:
        """Generate mock news data as fallback"""
        keyword_list = [k.strip() for k in keywords.split(",")]
        
        mock_articles = []
        for i in range(min(max_results, 3)):
            article = {
                "platform": "news",
                "external_id": f"news_article_{int(time.time())}_{i}",
                "author": f"Reporter {i + 1}",
                "title": f"Breaking: {keyword_list[0] if keyword_list else 'Company'} Makes Strategic Move",
                "content": f"In recent developments, {keyword_list[0] if keyword_list else 'the company'} has been making headlines with {'positive' if i % 2 == 0 else 'mixed'} industry reactions.",
                "url": f"https://news-example.com/article_{i}",
                "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "engagement_metrics": {
                    "shares": (i + 1) * 100,
                    "comments": i * 25,
                    "views": (i + 1) * 5000
                },
                "metadata": {
                    "source": f"News Source {i + 1}",
                    "category": "business",
                    "sentiment_bias": "neutral"
                },
                "brand_keywords_found": keyword_list[:1]
            }
            mock_articles.append(article)
        
        result = {
            "platform": "news",
            "articles_found": len(mock_articles),
            "keywords_searched": keyword_list,
            "collection_timestamp": datetime.utcnow().isoformat(),
            "articles": mock_articles,
            "mock_mode": True
        }
        
        logger.info(f"✅ Collected {len(mock_articles)} news articles (mock data - NewsAPI not available)")
        return json.dumps(result, indent=2)
    
    async def _arun(self, keywords: str, max_results: int = 10, days_back: int = 7) -> str:
        """Collect news data asynchronously"""
        return self._run(keywords, max_results, days_back)


class MultiPlatformDataCollector:
    """Orchestrator for collecting data from multiple platforms simultaneously"""
    
    def __init__(self):
        self.twitter_tool = TwitterDataTool()
        self.reddit_tool = RedditDataTool()
        self.news_tool = NewsDataTool()
        
        logger.info("🌐 Multi-platform data collector initialized")
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all data collection tools for LangChain agent"""
        return [
            self.twitter_tool,
            self.reddit_tool,
            self.news_tool
        ]
    
    async def collect_comprehensive_data(
        self, 
        keywords: List[str], 
        platforms: List[str] = ["twitter", "reddit", "news"],
        max_results_per_platform: int = 20
    ) -> Dict[str, Any]:
        """Collect data from multiple platforms simultaneously"""
        
        keywords_str = ", ".join(keywords)
        collection_tasks = []
        
        # Create async tasks for each platform
        if "twitter" in platforms:
            collection_tasks.append(
                ("twitter", self.twitter_tool._arun(keywords_str, max_results_per_platform))
            )
        
        if "reddit" in platforms:
            collection_tasks.append(
                ("reddit", self.reddit_tool._arun(keywords_str, max_results_per_platform, "technology,business,news"))
            )
        
        if "news" in platforms:
            collection_tasks.append(
                ("news", self.news_tool._arun(keywords_str, max_results_per_platform))
            )
        
        # Execute all collections simultaneously
        results = {}
        for platform, task in collection_tasks:
            try:
                result_json = await task
                results[platform] = json.loads(result_json)
            except Exception as e:
                logger.error(f"❌ Failed to collect data from {platform}: {e}")
                results[platform] = {"error": str(e)}
        
        # Aggregate results
        total_mentions = 0
        all_mentions = []
        
        for platform, data in results.items():
            if "mentions" in data:
                total_mentions += len(data["mentions"])
                all_mentions.extend(data["mentions"])
            elif "articles" in data:
                total_mentions += len(data["articles"])
                all_mentions.extend(data["articles"])
        
        aggregated_result = {
            "collection_timestamp": datetime.utcnow().isoformat(),
            "keywords_searched": keywords,
            "platforms_searched": platforms,
            "total_mentions_found": total_mentions,
            "platform_results": results,
            "all_mentions": all_mentions,
            "summary": {
                "twitter_mentions": len(results.get("twitter", {}).get("mentions", [])),
                "reddit_mentions": len(results.get("reddit", {}).get("mentions", [])),
                "news_articles": len(results.get("news", {}).get("articles", [])),
            }
        }
        
        logger.info(f"🎯 Comprehensive data collection complete: {total_mentions} mentions from {len(platforms)} platforms")
        
        return aggregated_result


# Export the main class for use by agents
__all__ = ["MultiPlatformDataCollector", "TwitterDataTool", "RedditDataTool", "NewsDataTool"]
