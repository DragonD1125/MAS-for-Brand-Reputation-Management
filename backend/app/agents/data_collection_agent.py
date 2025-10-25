"""
Data Collection Agent for Social Media and Web Monitoring
"""

import aiohttp
import asyncio
from typing import List, Dict, Any
import time
from datetime import datetime, timedelta
from loguru import logger

from .base_agent import BaseAgent, Message, MessageType
from app.core.config import settings


class DataCollectionAgent(BaseAgent):
    """Agent responsible for collecting data from various platforms"""
    
    def __init__(self, agent_id: str = "data_collector"):
        super().__init__(agent_id, [
            "data_collection", 
            "social_media_monitoring",
            "web_scraping",
            "api_integration"
        ])
        
        self.platforms = {
            "twitter": self._collect_twitter_data,
            "facebook": self._collect_facebook_data,
            "instagram": self._collect_instagram_data,
            "news": self._collect_news_data,
            "reddit": self._collect_reddit_data,
        }
        
        self.active_monitoring = {}
        self.collection_stats = {
            "total_collected": 0,
            "platform_stats": {},
            "last_collection": None
        }
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a data collection task"""
        try:
            platform = task.get("platform")
            keywords = task.get("keywords", [])
            timeframe = task.get("timeframe", "1h")
            brand_id = task.get("brand_id")
            
            logger.info(f"Starting data collection for {platform} with keywords: {keywords}")
            
            if platform not in self.platforms:
                return {
                    "status": "error",
                    "message": f"Unsupported platform: {platform}",
                    "platform": platform
                }
            
            # Collect data from the specified platform
            data = await self.platforms[platform](keywords, timeframe, brand_id)
            
            # Update statistics
            self.collection_stats["total_collected"] += len(data)
            self.collection_stats["platform_stats"][platform] = \
                self.collection_stats["platform_stats"].get(platform, 0) + len(data)
            self.collection_stats["last_collection"] = time.time()
            
            self.metrics["tasks_processed"] += 1
            
            return {
                "status": "success",
                "platform": platform,
                "data_count": len(data),
                "data": data,
                "collection_timestamp": time.time(),
                "brand_id": brand_id
            }
            
        except Exception as e:
            logger.error(f"Error in data collection task: {e}")
            self.metrics["errors"] += 1
            return {
                "status": "error",
                "message": str(e),
                "platform": task.get("platform", "unknown")
            }
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        try:
            if message.message_type == MessageType.TASK_REQUEST.value:
                # Process collection request
                result = await self.process_task(message.content)
                
                # Send result to sentiment analysis agent
                if result["status"] == "success" and result["data"]:
                    analysis_message = Message(
                        sender=self.agent_id,
                        receiver="sentiment_analyzer",
                        content=result,
                        timestamp=time.time(),
                        message_type=MessageType.DATA_TRANSFER.value,
                        correlation_id=message.correlation_id
                    )
                    await self.send_message(analysis_message)
                
                # Send response back to requester
                response = Message(
                    sender=self.agent_id,
                    receiver=message.sender,
                    content=result,
                    timestamp=time.time(),
                    message_type=MessageType.TASK_RESPONSE.value,
                    correlation_id=message.correlation_id
                )
                await self.send_message(response)
                
            elif message.message_type == "start_monitoring":
                await self._start_continuous_monitoring(message.content)
                
            elif message.message_type == "stop_monitoring":
                await self._stop_continuous_monitoring(message.content)
                
        except Exception as e:
            logger.error(f"Error handling message in DataCollectionAgent: {e}")
    
    async def _collect_twitter_data(self, keywords: List[str], timeframe: str, brand_id: str) -> List[Dict]:
        """Collect data from Twitter"""
        collected_data = []
        
        # Simulate Twitter data collection (replace with actual API calls)
        try:
            if not settings.TWITTER_BEARER_TOKEN:
                logger.warning("Twitter API credentials not configured")
                return self._generate_mock_twitter_data(keywords)
            
            # TODO: Implement actual Twitter API integration
            # For now, return mock data
            return self._generate_mock_twitter_data(keywords)
            
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {e}")
            return []
    
    async def _collect_facebook_data(self, keywords: List[str], timeframe: str, brand_id: str) -> List[Dict]:
        """Collect data from Facebook"""
        try:
            if not settings.FACEBOOK_ACCESS_TOKEN:
                logger.warning("Facebook API credentials not configured")
                return self._generate_mock_facebook_data(keywords)
            
            # TODO: Implement actual Facebook API integration
            return self._generate_mock_facebook_data(keywords)
            
        except Exception as e:
            logger.error(f"Error collecting Facebook data: {e}")
            return []
    
    async def _collect_instagram_data(self, keywords: List[str], timeframe: str, brand_id: str) -> List[Dict]:
        """Collect data from Instagram"""
        try:
            # TODO: Implement Instagram scraping/API integration
            return self._generate_mock_instagram_data(keywords)
            
        except Exception as e:
            logger.error(f"Error collecting Instagram data: {e}")
            return []
    
    async def _collect_news_data(self, keywords: List[str], timeframe: str, brand_id: str) -> List[Dict]:
        """Collect data from news sources"""
        try:
            # TODO: Implement news API integration (NewsAPI, Google News, etc.)
            return self._generate_mock_news_data(keywords)
            
        except Exception as e:
            logger.error(f"Error collecting news data: {e}")
            return []
    
    async def _collect_reddit_data(self, keywords: List[str], timeframe: str, brand_id: str) -> List[Dict]:
        """Collect data from Reddit"""
        try:
            # TODO: Implement Reddit API integration
            return self._generate_mock_reddit_data(keywords)
            
        except Exception as e:
            logger.error(f"Error collecting Reddit data: {e}")
            return []
    
    def _generate_mock_twitter_data(self, keywords: List[str]) -> List[Dict]:
        """Generate mock Twitter data for testing"""
        mock_data = []
        for i, keyword in enumerate(keywords[:5]):  # Limit to 5 for demo
            mock_data.append({
                "id": f"twitter_{i}_{int(time.time())}",
                "platform": "twitter",
                "text": f"Just tried {keyword} and it's amazing! Really impressed with the quality. #brandlove",
                "author": f"user_{i}",
                "created_at": datetime.utcnow().isoformat(),
                "url": f"https://twitter.com/user_{i}/status/{1000000000 + i}",
                "metrics": {
                    "likes": 15 + i * 3,
                    "retweets": 5 + i,
                    "replies": 2 + i
                },
                "source": "twitter_api"
            })
        return mock_data
    
    def _generate_mock_facebook_data(self, keywords: List[str]) -> List[Dict]:
        """Generate mock Facebook data for testing"""
        mock_data = []
        for i, keyword in enumerate(keywords[:3]):
            mock_data.append({
                "id": f"facebook_{i}_{int(time.time())}",
                "platform": "facebook",
                "text": f"Has anyone tried {keyword}? Looking for honest reviews.",
                "author": f"facebook_user_{i}",
                "created_at": datetime.utcnow().isoformat(),
                "url": f"https://facebook.com/posts/{1000000 + i}",
                "metrics": {
                    "likes": 25 + i * 5,
                    "comments": 8 + i * 2,
                    "shares": 3 + i
                },
                "source": "facebook_api"
            })
        return mock_data
    
    def _generate_mock_instagram_data(self, keywords: List[str]) -> List[Dict]:
        """Generate mock Instagram data for testing"""
        mock_data = []
        for i, keyword in enumerate(keywords[:4]):
            mock_data.append({
                "id": f"instagram_{i}_{int(time.time())}",
                "platform": "instagram",
                "text": f"Loving my new {keyword}! Perfect for the weekend ✨ #{keyword.replace(' ', '')}",
                "author": f"insta_user_{i}",
                "created_at": datetime.utcnow().isoformat(),
                "url": f"https://instagram.com/p/{1000000 + i}",
                "metrics": {
                    "likes": 50 + i * 10,
                    "comments": 12 + i * 3
                },
                "source": "instagram_scraper"
            })
        return mock_data
    
    def _generate_mock_news_data(self, keywords: List[str]) -> List[Dict]:
        """Generate mock news data for testing"""
        mock_data = []
        for i, keyword in enumerate(keywords[:2]):
            mock_data.append({
                "id": f"news_{i}_{int(time.time())}",
                "platform": "news",
                "text": f"Industry Analysis: {keyword} shows strong market performance in Q4 with innovative features driving customer satisfaction.",
                "author": f"Tech Reporter {i+1}",
                "created_at": datetime.utcnow().isoformat(),
                "url": f"https://technews.com/articles/{keyword.replace(' ', '-')}-analysis-{i}",
                "source_name": f"Tech News {i+1}",
                "source": "news_api"
            })
        return mock_data
    
    def _generate_mock_reddit_data(self, keywords: List[str]) -> List[Dict]:
        """Generate mock Reddit data for testing"""
        mock_data = []
        for i, keyword in enumerate(keywords[:3]):
            mock_data.append({
                "id": f"reddit_{i}_{int(time.time())}",
                "platform": "reddit",
                "text": f"Anyone else think {keyword} is overrated? I tried it and wasn't impressed.",
                "author": f"reddit_user_{i}",
                "created_at": datetime.utcnow().isoformat(),
                "url": f"https://reddit.com/r/reviews/comments/{1000000 + i}",
                "subreddit": "reviews",
                "metrics": {
                    "upvotes": 45 + i * 8,
                    "downvotes": 12 + i * 2,
                    "comments": 18 + i * 4
                },
                "source": "reddit_api"
            })
        return mock_data
    
    async def _start_continuous_monitoring(self, config: Dict[str, Any]):
        """Start continuous monitoring for a brand"""
        brand_id = config.get("brand_id")
        if brand_id not in self.active_monitoring:
            self.active_monitoring[brand_id] = {
                "config": config,
                "task": asyncio.create_task(self._monitoring_loop(config))
            }
            logger.info(f"Started continuous monitoring for brand {brand_id}")
    
    async def _stop_continuous_monitoring(self, config: Dict[str, Any]):
        """Stop continuous monitoring for a brand"""
        brand_id = config.get("brand_id")
        if brand_id in self.active_monitoring:
            self.active_monitoring[brand_id]["task"].cancel()
            del self.active_monitoring[brand_id]
            logger.info(f"Stopped continuous monitoring for brand {brand_id}")
    
    async def _monitoring_loop(self, config: Dict[str, Any]):
        """Continuous monitoring loop"""
        while True:
            try:
                # Collect data from all configured platforms
                for platform in config.get("platforms", []):
                    task = {
                        "platform": platform,
                        "keywords": config.get("keywords", []),
                        "timeframe": "15m",
                        "brand_id": config.get("brand_id")
                    }
                    await self.process_task(task)
                
                # Wait for next collection interval
                await asyncio.sleep(settings.MONITORING_INTERVAL * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Brief pause before retry
