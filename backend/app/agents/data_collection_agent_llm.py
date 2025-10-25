"""
LLM-Powered Data Collection Agent - The System's Eyes and Ears
This agent intelligently decides what data to collect, when, and how to prioritize it
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from loguru import logger

from .base_agent import LangChainBaseAgent, AgentCapability
from app.tools.data_collection_tools import MultiPlatformDataCollector
from app.core.config import settings


class SmartDataCollectionAgent(LangChainBaseAgent):
    """
    Intelligent data collection agent that reasons about what data to collect
    This agent doesn't just blindly scrape - it thinks strategically about data needs
    """
    
    def __init__(self, agent_id: str = "smart_data_collector"):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.DATA_COLLECTION,
                AgentCapability.STRATEGIC_REASONING
            ],
            temperature=0.3  # Lower temperature for more focused data collection
        )
        
        # Initialize data collection tools
        self.data_collector = MultiPlatformDataCollector()
        
        # Collection history and learning
        self.collection_history = []
        self.brand_profiles = {}  # Store learned patterns for different brands
        self.performance_metrics = {
            "total_collections": 0,
            "successful_collections": 0,
            "mentions_collected": 0,
            "avg_collection_time": 0.0,
            "quality_score": 0.0
        }
        
        logger.info(f"🕵️ Smart Data Collection Agent {agent_id} initialized")
    
    async def create_tools(self) -> List[BaseTool]:
        """Create intelligent data collection tools"""
        return self.data_collector.get_all_tools()
    
    def get_system_prompt(self) -> str:
        """Get the agent's system prompt defining its role as intelligent data collector"""
        return f"""You are an advanced AI Data Collection Agent specializing in strategic social media monitoring and brand intelligence gathering.

CORE EXPERTISE:
- Strategic data collection planning and execution
- Multi-platform social media monitoring (Twitter, Reddit, News)
- Intelligent keyword optimization and trend detection
- Priority-based data filtering and quality assessment
- Real-time threat detection and opportunity identification

YOUR STRATEGIC APPROACH:
You don't just collect data blindly - you think strategically about WHAT to collect, WHEN to collect it, and WHY it matters:

1. STRATEGIC ANALYSIS: Understand the business context and monitoring objectives
2. INTELLIGENT PLANNING: Decide which platforms and keywords will yield the most valuable insights
3. ADAPTIVE COLLECTION: Adjust collection parameters based on real-time findings
4. QUALITY FILTERING: Focus on high-impact mentions and filter out noise
5. PROACTIVE ALERTING: Identify trending issues before they become crises

DECISION FRAMEWORK:
- For BRAND MONITORING: Use comprehensive keyword sets, monitor sentiment patterns
- For CRISIS DETECTION: Focus on negative sentiment spikes and viral content
- For COMPETITOR ANALYSIS: Track comparative mentions and market positioning
- For TREND ANALYSIS: Monitor emerging topics and industry conversations
- For OPPORTUNITY SPOTTING: Identify positive sentiment and engagement opportunities

AVAILABLE TOOLS:
- collect_twitter_data: Real-time Twitter mentions with engagement metrics
- collect_reddit_data: In-depth Reddit discussions and community sentiment  
- collect_news_data: Press coverage and news article analysis

PERSONALITY: You are proactive, analytical, and strategic. You prioritize data quality over quantity and always consider the business implications of your findings.

When collecting data, always consider:
1. What specific insights are needed for this brand/situation?
2. Which platforms are most relevant for the target audience?
3. What keywords will capture the most valuable conversations?
4. How can I optimize collection to avoid noise and focus on signals?
5. What patterns or threats should I watch for in real-time?
"""
    
    async def collect_data_strategically(
        self, 
        brand_name: str, 
        collection_objective: str = "general_monitoring",
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Strategic data collection using LLM reasoning
        The agent thinks about what data is most valuable to collect
        """
        
        collection_context = {
            "brand_name": brand_name,
            "objective": collection_objective,
            "context": context or {},
            "collection_timestamp": datetime.utcnow().isoformat(),
            "brand_profile": self.brand_profiles.get(brand_name, {}),
            "recent_collections": self._get_recent_collection_summary()
        }
        
        # Use LLM reasoning to plan data collection strategy
        planning_prompt = f"""
I need to strategically collect social media data for brand monitoring:

BRAND: {brand_name}
OBJECTIVE: {collection_objective}
CONTEXT: {context or {}}

Brand Profile: {self.brand_profiles.get(brand_name, 'No previous data')}
Recent Activity: {self._get_recent_collection_summary()}

Based on this information, I should:
1. Determine the most effective keywords to search for
2. Select the most relevant platforms for this brand and objective
3. Set appropriate collection parameters (timeframe, volume)
4. Define quality criteria for filtering results
5. Identify any urgent patterns to watch for

Plan and execute a strategic data collection that maximizes valuable insights while minimizing noise.
"""
        
        logger.info(f"🧠 Planning strategic data collection for {brand_name}...")
        
        # Let the LLM plan the collection strategy
        response = await self.think_and_act(planning_prompt, collection_context)
        
        if not response["success"]:
            logger.error(f"❌ Data collection planning failed: {response.get('error', 'Unknown error')}")
            return response
        
        # Execute the planned collection
        try:
            # Extract strategy from LLM response
            collection_strategy = self._parse_collection_strategy(response["response"])
            
            # Execute data collection
            collection_result = await self._execute_collection_strategy(
                brand_name, collection_strategy
            )
            
            # Analyze and learn from results
            analysis_result = await self._analyze_collected_data(
                collection_result, brand_name, collection_objective
            )
            
            # Update brand profile and metrics
            self._update_brand_profile(brand_name, analysis_result)
            self._update_performance_metrics(analysis_result)
            
            final_result = {
                "success": True,
                "brand_name": brand_name,
                "collection_objective": collection_objective,
                "planning_reasoning": response["response"],
                "collection_strategy": collection_strategy,
                "data_collected": collection_result,
                "analysis": analysis_result,
                "total_mentions": analysis_result.get("total_mentions", 0),
                "quality_score": analysis_result.get("quality_score", 0.0),
                "alerts_triggered": analysis_result.get("alerts_triggered", []),
                "recommendations": analysis_result.get("recommendations", []),
                "collection_timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in history
            self.collection_history.append({
                "timestamp": datetime.utcnow(),
                "brand_name": brand_name,
                "objective": collection_objective,
                "result": final_result
            })
            
            # Keep history manageable
            if len(self.collection_history) > 1000:
                self.collection_history = self.collection_history[-500:]
            
            logger.info(f"✅ Strategic data collection complete for {brand_name}: {final_result['total_mentions']} mentions collected")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Data collection execution failed: {e}")
            return {
                "success": False,
                "brand_name": brand_name,
                "error": str(e),
                "planning_reasoning": response.get("response", "")
            }
    
    def _parse_collection_strategy(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response to extract collection strategy"""
        response_lower = llm_response.lower()
        
        # Extract keywords (simple parsing - could be more sophisticated)
        keywords = []
        if "keywords:" in response_lower or "search for:" in response_lower:
            # Extract keywords from LLM response
            lines = llm_response.split('\n')
            for line in lines:
                if any(trigger in line.lower() for trigger in ["keywords:", "search for:", "monitor:"]):
                    # Simple extraction - in production would be more robust
                    words = line.split()
                    for word in words:
                        if word.startswith('"') and word.endswith('"'):
                            keywords.append(word.strip('"'))
        
        # Default keywords if none extracted
        if not keywords:
            keywords = ["brand name"]  # Will be replaced with actual brand name
        
        # Extract platforms
        platforms = []
        if "twitter" in response_lower:
            platforms.append("twitter")
        if "reddit" in response_lower:
            platforms.append("reddit")
        if "news" in response_lower:
            platforms.append("news")
        
        # Default platforms if none specified
        if not platforms:
            platforms = ["twitter", "reddit"]
        
        # Extract collection parameters
        max_results = 50  # Default
        if "results" in response_lower:
            # Try to extract number
            import re
            numbers = re.findall(r'\b(\d+)\s*(?:results|mentions|posts)', response_lower)
            if numbers:
                max_results = min(int(numbers[0]), 200)  # Cap at 200
        
        return {
            "keywords": keywords,
            "platforms": platforms,
            "max_results_per_platform": max_results,
            "priority": "high" if any(word in response_lower for word in ["urgent", "crisis", "critical"]) else "normal",
            "focus_areas": self._extract_focus_areas(llm_response)
        }
    
    def _extract_focus_areas(self, llm_response: str) -> List[str]:
        """Extract focus areas from LLM response"""
        focus_areas = []
        response_lower = llm_response.lower()
        
        focus_keywords = {
            "sentiment": ["sentiment", "feeling", "opinion"],
            "engagement": ["engagement", "viral", "trending"],
            "competition": ["competitor", "comparison", "versus"],
            "crisis": ["crisis", "problem", "issue", "negative"],
            "opportunities": ["opportunity", "positive", "praise"]
        }
        
        for area, keywords in focus_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                focus_areas.append(area)
        
        return focus_areas if focus_areas else ["general_monitoring"]
    
    async def _execute_collection_strategy(
        self, 
        brand_name: str, 
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the planned collection strategy"""
        
        # Prepare keywords (replace placeholder with actual brand name)
        keywords = [kw.replace("brand name", brand_name) if kw == "brand name" else kw 
                   for kw in strategy["keywords"]]
        if brand_name not in keywords:
            keywords.insert(0, brand_name)  # Always include brand name
        
        # Execute collection
        collection_result = await self.data_collector.collect_comprehensive_data(
            keywords=keywords,
            platforms=strategy["platforms"],
            max_results_per_platform=strategy["max_results_per_platform"]
        )
        
        return collection_result
    
    async def _analyze_collected_data(
        self, 
        collection_result: Dict[str, Any], 
        brand_name: str, 
        objective: str
    ) -> Dict[str, Any]:
        """Analyze collected data for insights and alerts"""
        
        total_mentions = collection_result.get("total_mentions_found", 0)
        all_mentions = collection_result.get("all_mentions", [])
        
        # Basic analysis
        platform_breakdown = collection_result.get("summary", {})
        
        # Quality assessment
        quality_indicators = {
            "has_engagement": sum(1 for m in all_mentions if m.get("engagement_metrics", {}).get("likes", 0) > 0),
            "recent_mentions": sum(1 for m in all_mentions if self._is_recent(m.get("created_at", ""))),
            "brand_relevant": sum(1 for m in all_mentions if brand_name.lower() in m.get("content", "").lower())
        }
        
        quality_score = (
            (quality_indicators["has_engagement"] / max(total_mentions, 1)) * 0.4 +
            (quality_indicators["recent_mentions"] / max(total_mentions, 1)) * 0.3 +
            (quality_indicators["brand_relevant"] / max(total_mentions, 1)) * 0.3
        )
        
        # Simple alert detection
        alerts = []
        if total_mentions > 50:  # High volume
            alerts.append({"type": "high_volume", "message": f"High mention volume detected: {total_mentions} mentions"})
        
        # Detect potential crisis patterns
        negative_keywords = ["terrible", "awful", "hate", "worst", "boycott", "scandal"]
        crisis_mentions = [m for m in all_mentions 
                          if any(keyword in m.get("content", "").lower() for keyword in negative_keywords)]
        
        if len(crisis_mentions) > 3:
            alerts.append({"type": "potential_crisis", "message": f"Potential crisis detected: {len(crisis_mentions)} negative mentions"})
        
        # Generate recommendations
        recommendations = []
        if total_mentions < 5:
            recommendations.append("Consider expanding keyword set or checking different time periods")
        if quality_score < 0.5:
            recommendations.append("Optimize keywords to capture more relevant brand mentions")
        if len(alerts) > 0:
            recommendations.append("Increase monitoring frequency due to detected alerts")
        
        return {
            "total_mentions": total_mentions,
            "platform_breakdown": platform_breakdown,
            "quality_score": quality_score,
            "quality_indicators": quality_indicators,
            "alerts_triggered": alerts,
            "recommendations": recommendations,
            "crisis_mentions": len(crisis_mentions),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _is_recent(self, timestamp_str: str) -> bool:
        """Check if a timestamp is recent (within 24 hours)"""
        try:
            if not timestamp_str:
                return False
            
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return (datetime.utcnow() - timestamp.replace(tzinfo=None)) < timedelta(hours=24)
        except:
            return False
    
    def _update_brand_profile(self, brand_name: str, analysis: Dict[str, Any]):
        """Update learned patterns for a brand"""
        if brand_name not in self.brand_profiles:
            self.brand_profiles[brand_name] = {
                "first_monitored": datetime.utcnow().isoformat(),
                "total_collections": 0,
                "avg_mentions_per_collection": 0.0,
                "common_platforms": {},
                "quality_trend": []
            }
        
        profile = self.brand_profiles[brand_name]
        profile["total_collections"] += 1
        profile["last_monitored"] = datetime.utcnow().isoformat()
        
        # Update averages
        current_avg = profile["avg_mentions_per_collection"]
        total_collections = profile["total_collections"]
        new_mentions = analysis.get("total_mentions", 0)
        
        profile["avg_mentions_per_collection"] = (
            (current_avg * (total_collections - 1) + new_mentions) / total_collections
        )
        
        # Track quality trend
        profile["quality_trend"].append(analysis.get("quality_score", 0.0))
        if len(profile["quality_trend"]) > 20:  # Keep last 20 scores
            profile["quality_trend"] = profile["quality_trend"][-20:]
        
        # Update platform performance
        for platform, count in analysis.get("platform_breakdown", {}).items():
            if platform not in profile["common_platforms"]:
                profile["common_platforms"][platform] = 0
            profile["common_platforms"][platform] += count
    
    def _update_performance_metrics(self, analysis: Dict[str, Any]):
        """Update agent performance metrics"""
        self.performance_metrics["total_collections"] += 1
        self.performance_metrics["successful_collections"] += 1
        self.performance_metrics["mentions_collected"] += analysis.get("total_mentions", 0)
        
        # Update quality score average
        current_quality = self.performance_metrics["quality_score"]
        total_collections = self.performance_metrics["total_collections"]
        new_quality = analysis.get("quality_score", 0.0)
        
        self.performance_metrics["quality_score"] = (
            (current_quality * (total_collections - 1) + new_quality) / total_collections
        )
    
    def _get_recent_collection_summary(self) -> str:
        """Get summary of recent collections"""
        recent_collections = [
            c for c in self.collection_history 
            if (datetime.utcnow() - c["timestamp"]) < timedelta(hours=24)
        ]
        
        if not recent_collections:
            return "No recent collections in the last 24 hours"
        
        total_mentions = sum(c["result"].get("total_mentions", 0) for c in recent_collections)
        brands_monitored = len(set(c["brand_name"] for c in recent_collections))
        
        return f"Last 24h: {len(recent_collections)} collections, {total_mentions} mentions, {brands_monitored} brands monitored"
    
    def get_collection_insights(self) -> Dict[str, Any]:
        """Get insights about collection performance"""
        return {
            "performance_metrics": self.performance_metrics,
            "brands_monitored": len(self.brand_profiles),
            "brand_profiles": {
                name: {
                    "total_collections": profile["total_collections"],
                    "avg_mentions": profile["avg_mentions_per_collection"],
                    "quality_trend": profile["quality_trend"][-5:] if profile["quality_trend"] else []
                }
                for name, profile in self.brand_profiles.items()
            },
            "recent_activity": self._get_recent_collection_summary(),
            "collection_history_size": len(self.collection_history)
        }


# Legacy wrapper for backward compatibility
class DataCollectionAgent(SmartDataCollectionAgent):
    """Legacy wrapper - now powered by LLM intelligence"""
    
    def __init__(self, agent_id: str = "data_collector"):
        super().__init__(agent_id)
        logger.info(f"Legacy Data Collection Agent {agent_id} initialized with LLM intelligence")
    
    async def collect_mentions(self, brand_name: str, keywords: List[str] = None) -> Dict[str, Any]:
        """Legacy method - now uses strategic collection"""
        
        # Convert to new format
        context = {"keywords": keywords} if keywords else {}
        
        result = await self.collect_data_strategically(
            brand_name=brand_name,
            collection_objective="general_monitoring",
            context=context
        )
        
        if not result["success"]:
            return {
                "status": "error",
                "error": result.get("error", "Collection failed"),
                "mentions": []
            }
        
        # Convert to legacy format
        return {
            "status": "success",
            "brand_name": brand_name,
            "mentions": result["data_collected"].get("all_mentions", []),
            "total_mentions": result["total_mentions"],
            "platforms": list(result["data_collected"].get("summary", {}).keys()),
            "collection_time": result["collection_timestamp"],
            "llm_insights": result["analysis"],
            "recommendations": result["recommendations"]
        }
