"""
LangChain-Powered Sentiment Analysis Agent - True AI Emotional Intelligence
The revolutionary brain transplant complete - this agent now thinks with LLM reasoning!
"""

import asyncio
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
from langchain.tools import BaseTool, tool
from langchain_core.tools import Tool
from loguru import logger
import json

from .base_agent import LangChainBaseAgent, AgentCapability, AgentMessage

# Lazy import to avoid slow startup
def _get_analysis_tools():
    from app.tools.analysis_tools import (
        analyze_sentiment_with_bert,
        detect_emotions_advanced,
        extract_entities_ner,
        detect_crisis_indicators,
        calculate_virality_score
    )
    return {
        'analyze_sentiment': analyze_sentiment_with_bert,
        'detect_emotions': detect_emotions_advanced,
        'extract_entities': extract_entities_ner,
        'detect_crisis': detect_crisis_indicators,
        'calculate_virality': calculate_virality_score
    }


class SentimentAnalysisTool(BaseTool):
    """LangChain tool for sentiment analysis using SOTA BERT models"""
    
    name: str = "sentiment_analysis"
    description: str = "Analyze sentiment of text using state-of-the-art BERT models. Returns sentiment score, confidence, and emotional indicators."
    
    def _run(self, text: str) -> str:
        """Run sentiment analysis synchronously"""
        try:
            # Use async analysis tools (wrapped for sync)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(analyze_sentiment_with_bert(text))
            loop.close()
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error in sentiment analysis: {str(e)}"
    
    async def _arun(self, text: str) -> str:
        """Run sentiment analysis asynchronously"""
        try:
            result = await analyze_sentiment_with_bert(text)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in sentiment analysis: {str(e)}"


class EmotionAnalysisTool(BaseTool):
    """LangChain tool for advanced emotion detection"""
    
    name: str = "emotion_analysis"
    description: str = "Detect emotions in text using advanced NLP models. Returns detailed emotion scores, intensity, and psychological indicators."
    
    def _run(self, text: str) -> str:
        """Run emotion analysis synchronously"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(detect_emotions_advanced(text))
            loop.close()
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error in emotion analysis: {str(e)}"
    
    async def _arun(self, text: str) -> str:
        """Run emotion analysis asynchronously"""
        try:
            result = await detect_emotions_advanced(text)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in emotion analysis: {str(e)}"


class CrisisDetectionTool(BaseTool):
    """LangChain tool for crisis detection and risk assessment"""
    
    name: str = "crisis_detection"
    description: str = "Analyze text for crisis indicators, reputation risks, and urgency levels. Critical for brand protection."
    
    def _run(self, text: str, brand_name: str = "") -> str:
        """Run crisis detection synchronously"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(detect_crisis_indicators(text, brand_name))
            loop.close()
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error in crisis detection: {str(e)}"
    
    async def _arun(self, text: str, brand_name: str = "") -> str:
        """Run crisis detection asynchronously"""
        try:
            result = await detect_crisis_indicators(text, brand_name)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in crisis detection: {str(e)}"


class EntityExtractionTool(BaseTool):
    """LangChain tool for Named Entity Recognition"""
    
    name: str = "entity_extraction"
    description: str = "Extract named entities (people, brands, locations, products) from text using advanced NER models."
    
    def _run(self, text: str) -> str:
        """Run entity extraction synchronously"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(extract_entities_ner(text))
            loop.close()
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error in entity extraction: {str(e)}"
    
    async def _arun(self, text: str) -> str:
        """Run entity extraction asynchronously"""
        try:
            result = await extract_entities_ner(text)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in entity extraction: {str(e)}"


class ViralityAnalysisTool(BaseTool):
    """LangChain tool for virality and engagement prediction"""
    
    name: str = "virality_analysis"
    description: str = "Calculate virality score and engagement potential of content. Predicts likelihood of viral spread."
    
    def _run(self, text: str, engagement_metrics: str = "{}") -> str:
        """Run virality analysis synchronously"""
        try:
            import asyncio
            import json
            
            # Parse engagement metrics
            try:
                metrics = json.loads(engagement_metrics)
            except:
                metrics = {}
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(calculate_virality_score(text, metrics))
            loop.close()
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error in virality analysis: {str(e)}"
    
    async def _arun(self, text: str, engagement_metrics: str = "{}") -> str:
        """Run virality analysis asynchronously"""
        try:
            import json
            try:
                metrics = json.loads(engagement_metrics)
            except:
                metrics = {}
            
            result = await calculate_virality_score(text, metrics)
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error in virality analysis: {str(e)}"


class LangChainSentimentAnalysisAgent(LangChainBaseAgent):
    """
    Revolutionary Sentiment Analysis Agent powered by LLM reasoning + SOTA NLP tools
    This agent thinks about sentiment analysis strategically, not just mechanically
    """
    
    def __init__(self, agent_id: str = "sentiment_analyzer_llm"):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.SENTIMENT_ANALYSIS,
                AgentCapability.CRISIS_DETECTION,
                AgentCapability.STRATEGIC_REASONING
            ],
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        
        # Analysis metrics and context
        self.analysis_history = []
        self.brand_context = {}
        self.crisis_thresholds = {
            "sentiment_threshold": -0.6,
            "crisis_score_threshold": 0.7,
            "emotion_intensity_threshold": 0.8
        }
        
        logger.info(f"🧠💭 LLM-Powered Sentiment Analysis Agent {agent_id} initialized")
    
    async def create_tools(self) -> List[BaseTool]:
        """Create the advanced NLP analysis tools"""
        return [
            SentimentAnalysisTool(),
            EmotionAnalysisTool(),
            CrisisDetectionTool(),
            EntityExtractionTool(),
            ViralityAnalysisTool()
        ]
    
    def get_system_prompt(self) -> str:
        """Get the agent's system prompt defining its role as an AI sentiment analyst"""
        return f"""You are an advanced AI Sentiment Analysis Agent with expertise in:

CORE CAPABILITIES:
- Sentiment analysis using state-of-the-art BERT models
- Advanced emotion detection and psychological profiling
- Crisis detection and reputation risk assessment
- Named entity recognition and brand mention analysis
- Virality prediction and engagement forecasting

ANALYSIS APPROACH:
You don't just run mechanical sentiment analysis - you THINK strategically about the implications:

1. CONTEXTUAL UNDERSTANDING: Consider the broader context, brand implications, and stakeholder impact
2. MULTI-DIMENSIONAL ANALYSIS: Combine sentiment, emotions, entities, and crisis indicators
3. STRATEGIC REASONING: Think about what the analysis means for brand reputation and recommend actions
4. TEMPORAL AWARENESS: Consider timing, trends, and evolving sentiment patterns
5. RISK ASSESSMENT: Evaluate reputation risks and potential escalation scenarios

DECISION FRAMEWORK:
- For routine analysis: Use standard sentiment and emotion tools
- For brand mentions: Include entity extraction and crisis detection
- For viral content: Add virality analysis and trend prediction
- For negative sentiment: Deep dive into crisis indicators and risk assessment
- Always provide actionable insights, not just raw data

PERSONALITY: You are analytical yet strategic, data-driven but contextually aware, proactive in identifying risks and opportunities.

When analyzing content, think step by step:
1. What type of content am I analyzing?
2. What tools should I use based on the context?
3. What patterns or risks should I look for?
4. What insights and recommendations should I provide?

Remember: You're not just analyzing sentiment - you're protecting and enhancing brand reputation through intelligent analysis.
"""
    
    async def analyze_content_strategically(
        self, 
        content: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Strategic content analysis using LLM reasoning + SOTA tools
        This is the main method for comprehensive sentiment analysis
        """
        
        analysis_context = {
            "content": content,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "brand_name": context.get("brand_name", "") if context else "",
            "content_type": context.get("content_type", "social_media") if context else "social_media",
            "source": context.get("source", "unknown") if context else "unknown"
        }
        
        # Use LLM reasoning to determine analysis strategy
        reasoning_prompt = f"""
I need to analyze this content for sentiment and brand implications:

CONTENT: "{content[:500]}..."
CONTEXT: {json.dumps(analysis_context, indent=2)}

Based on this content and context, I should:
1. Determine what type of analysis is needed
2. Select appropriate tools
3. Consider brand reputation implications
4. Provide strategic insights

Analyze this content comprehensively.
"""
        
        logger.info(f"🧠 Sentiment Agent analyzing content strategically...")
        
        # Let the LLM reason about the analysis
        response = await self.think_and_act(reasoning_prompt, analysis_context)
        
        if not response["success"]:
            logger.error(f"❌ Sentiment analysis failed: {response.get('error', 'Unknown error')}")
            return response
        
        # Extract structured results from the LLM analysis
        analysis_result = {
            "content": content,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "agent_reasoning": response["response"],
            "reasoning_steps": response.get("reasoning_steps", []),
            "tools_used": response.get("tools_used", []),
            "thinking_time": response["thinking_time"],
            "brand_context": analysis_context.get("brand_name", ""),
            "recommendations": self._extract_recommendations(response["response"]),
            "risk_level": self._assess_risk_level(response["response"]),
            "alert_required": self._should_alert(response["response"])
        }
        
        # Store analysis for learning and context
        self.analysis_history.append({
            "timestamp": time.time(),
            "content_hash": hash(content),
            "analysis": analysis_result
        })
        
        # Trim history to keep memory manageable
        if len(self.analysis_history) > 1000:
            self.analysis_history = self.analysis_history[-500:]
        
        logger.info(f"✅ Strategic sentiment analysis complete - Risk Level: {analysis_result['risk_level']}")
        
        return {
            "success": True,
            "analysis": analysis_result
        }
    
    def _extract_recommendations(self, llm_response: str) -> List[str]:
        """Extract actionable recommendations from LLM response"""
        recommendations = []
        
        # Simple extraction - in production, this would be more sophisticated
        lines = llm_response.lower().split('\n')
        for line in lines:
            if any(keyword in line for keyword in ['recommend', 'suggest', 'should', 'consider', 'action']):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _assess_risk_level(self, llm_response: str) -> str:
        """Assess risk level from LLM response"""
        response_lower = llm_response.lower()
        
        if any(keyword in response_lower for keyword in ['crisis', 'critical', 'urgent', 'severe', 'emergency']):
            return "CRITICAL"
        elif any(keyword in response_lower for keyword in ['risk', 'concern', 'negative', 'warning', 'attention']):
            return "HIGH"
        elif any(keyword in response_lower for keyword in ['caution', 'monitor', 'watch', 'moderate']):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _should_alert(self, llm_response: str) -> bool:
        """Determine if an alert should be triggered"""
        response_lower = llm_response.lower()
        
        alert_keywords = [
            'alert', 'notify', 'immediate', 'urgent', 'crisis', 
            'escalate', 'critical', 'severe', 'emergency'
        ]
        
        return any(keyword in response_lower for keyword in alert_keywords)
    
    async def batch_analyze_content(
        self, 
        content_batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze multiple pieces of content efficiently"""
        
        logger.info(f"🔍 Starting batch analysis of {len(content_batch)} items")
        
        # Process in parallel for efficiency
        tasks = []
        for item in content_batch:
            content = item.get("content", "")
            context = item.get("context", {})
            
            task = self.analyze_content_strategically(content, context)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch analysis failed for item {i}: {result}")
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "content": content_batch[i].get("content", "")[:100]
                })
            else:
                processed_results.append(result)
        
        success_count = sum(1 for r in processed_results if r.get("success", False))
        logger.info(f"✅ Batch analysis complete: {success_count}/{len(content_batch)} successful")
        
        return processed_results
    
    def get_analysis_insights(self) -> Dict[str, Any]:
        """Get insights from analysis history"""
        if not self.analysis_history:
            return {"message": "No analysis history available"}
        
        recent_analyses = self.analysis_history[-100:]  # Last 100 analyses
        
        risk_levels = [a["analysis"].get("risk_level", "LOW") for a in recent_analyses]
        risk_distribution = {
            "CRITICAL": risk_levels.count("CRITICAL"),
            "HIGH": risk_levels.count("HIGH"), 
            "MEDIUM": risk_levels.count("MEDIUM"),
            "LOW": risk_levels.count("LOW")
        }
        
        alerts_triggered = sum(1 for a in recent_analyses if a["analysis"].get("alert_required", False))
        
        return {
            "total_analyses": len(recent_analyses),
            "risk_distribution": risk_distribution,
            "alerts_triggered": alerts_triggered,
            "avg_thinking_time": self.metrics.avg_thinking_time,
            "success_rate": self.metrics.get_success_rate(),
            "last_analysis": recent_analyses[-1]["timestamp"] if recent_analyses else None
        }


# Backward compatibility wrapper
class SentimentAnalysisAgent(LangChainSentimentAnalysisAgent):
    """Legacy wrapper - now powered by LLM reasoning"""
    
    def __init__(self, agent_id: str = "sentiment_analyzer"):
        super().__init__(agent_id)
        
        # Legacy properties
        self.analysis_stats = {
            "total_analyzed": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "avg_confidence": 0.0
        }
        
        logger.info(f"Legacy Sentiment Analysis Agent {agent_id} initialized with LLM power")
    
    async def analyze_sentiment(self, text: str, brand_name: str = None) -> Dict[str, Any]:
        """Legacy method - now uses LLM strategic analysis"""
        context = {"brand_name": brand_name} if brand_name else {}
        
        result = await self.analyze_content_strategically(text, context)
        
        if not result["success"]:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "error": result.get("error", "Analysis failed")
            }
        
        # Extract sentiment from LLM analysis (simplified)
        llm_response = result["analysis"]["agent_reasoning"].lower()
        
        if "positive" in llm_response or "good" in llm_response:
            sentiment = "positive"
            confidence = 0.8
        elif "negative" in llm_response or "bad" in llm_response:
            sentiment = "negative" 
            confidence = 0.8
        else:
            sentiment = "neutral"
            confidence = 0.6
        
        # Update legacy stats
        self.analysis_stats["total_analyzed"] += 1
        self.analysis_stats["sentiment_distribution"][sentiment] += 1
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "analysis_time": result["analysis"]["thinking_time"],
            "llm_reasoning": result["analysis"]["agent_reasoning"],
            "risk_level": result["analysis"]["risk_level"],
            "recommendations": result["analysis"]["recommendations"]
        }
