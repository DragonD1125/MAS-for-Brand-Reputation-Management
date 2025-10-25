"""
LLM-Powered Response Generation Agent - The System's Voice
This agent generates intelligent, fact-based, on-brand responses using RAG technology
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain.tools import BaseTool
from langchain_core.tools import Tool
from loguru import logger
import json
import time

from .base_agent import LangChainBaseAgent, AgentCapability
from app.tools.rag_tools import BrandKnowledgeManager
from app.tools.analysis_tools import AnalysisTools
from app.core.config import settings


class ResponseQualityTool(BaseTool):
    """Tool for evaluating response quality and brand alignment"""
    
    name: str = "evaluate_response_quality"
    description: str = "Evaluate the quality, brand alignment, and appropriateness of a generated response before sending."
    
    def _run(self, response: str, original_mention: str, brand_name: str = "") -> str:
        """Evaluate response quality"""
        try:
            # Quality evaluation criteria
            quality_score = 0.0
            feedback = []
            
            # Length check
            if 10 <= len(response) <= 280:  # Twitter-appropriate length
                quality_score += 0.2
            else:
                feedback.append("Consider adjusting response length for social media appropriateness")
            
            # Tone check
            positive_indicators = ["thank", "appreciate", "help", "sorry", "understand", "glad", "happy"]
            negative_indicators = ["no", "can't", "won't", "impossible", "never"]
            
            positive_count = sum(1 for word in positive_indicators if word in response.lower())
            negative_count = sum(1 for word in negative_indicators if word in response.lower())
            
            if positive_count > negative_count:
                quality_score += 0.3
            else:
                feedback.append("Consider using more positive language")
            
            # Professional language check
            if not any(word in response.lower() for word in ["damn", "hell", "stupid", "ridiculous"]):
                quality_score += 0.2
            else:
                feedback.append("Remove unprofessional language")
            
            # Brand mention check
            if brand_name and brand_name.lower() in response.lower():
                quality_score += 0.1
            
            # Call-to-action or next steps
            action_words = ["contact", "visit", "email", "call", "dm", "message", "support"]
            if any(word in response.lower() for word in action_words):
                quality_score += 0.2
            else:
                feedback.append("Consider adding clear next steps for the customer")
            
            # Overall assessment
            if quality_score >= 0.8:
                assessment = "excellent"
            elif quality_score >= 0.6:
                assessment = "good"
            elif quality_score >= 0.4:
                assessment = "needs_improvement"
            else:
                assessment = "poor"
            
            result = {
                "quality_score": quality_score,
                "assessment": assessment,
                "feedback": feedback,
                "response_length": len(response),
                "brand_mentioned": brand_name.lower() in response.lower() if brand_name else False,
                "evaluation_timestamp": datetime.utcnow().isoformat()
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _arun(self, response: str, original_mention: str, brand_name: str = "") -> str:
        """Evaluate response quality asynchronously"""
        return self._run(response, original_mention, brand_name)


class ResponsePersonalizationTool(BaseTool):
    """Tool for personalizing responses based on customer context"""
    
    name: str = "personalize_response"
    description: str = "Personalize a response based on customer information, sentiment, and interaction history."
    
    def _run(self, base_response: str, customer_info: str, sentiment: str = "neutral") -> str:
        """Personalize response based on context"""
        try:
            # Parse customer info
            customer_data = json.loads(customer_info) if customer_info.startswith('{') else {"info": customer_info}
            
            personalized_response = base_response
            
            # Adjust tone based on sentiment
            if sentiment.lower() == "negative":
                # Add empathetic language for negative sentiment
                if not any(word in base_response.lower() for word in ["sorry", "understand", "apologize"]):
                    personalized_response = "I understand your concern. " + personalized_response
            
            elif sentiment.lower() == "positive":
                # Add appreciation for positive sentiment
                if not any(word in base_response.lower() for word in ["thank", "appreciate", "glad"]):
                    personalized_response = "Thank you for your positive feedback! " + personalized_response
            
            # Add customer name if available
            customer_name = customer_data.get("name", "").strip()
            if customer_name and not customer_name.lower() in personalized_response.lower():
                personalized_response = f"Hi {customer_name}, " + personalized_response
            
            # Adjust formality based on platform
            platform = customer_data.get("platform", "").lower()
            if platform in ["twitter", "instagram"]:
                # More casual tone
                personalized_response = personalized_response.replace("We would be happy to", "We'd love to")
                personalized_response = personalized_response.replace("Please do not hesitate", "Feel free")
            
            result = {
                "personalized_response": personalized_response,
                "personalization_applied": {
                    "sentiment_adjustment": sentiment != "neutral",
                    "name_added": bool(customer_name),
                    "platform_optimization": bool(platform),
                    "tone_adjustment": True
                },
                "original_length": len(base_response),
                "personalized_length": len(personalized_response)
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e), "fallback_response": base_response})
    
    async def _arun(self, base_response: str, customer_info: str, sentiment: str = "neutral") -> str:
        """Personalize response asynchronously"""
        return self._run(base_response, customer_info, sentiment)


class IntelligentResponseAgent(LangChainBaseAgent):
    """
    Revolutionary Response Generation Agent powered by LLM + RAG
    This agent generates intelligent, fact-based, on-brand responses
    """
    
    def __init__(self, agent_id: str = "response_generator"):
        super().__init__(
            agent_id=agent_id,
            capabilities=[
                AgentCapability.STRATEGIC_REASONING,
                AgentCapability.SENTIMENT_ANALYSIS,
                AgentCapability.CRISIS_DETECTION
            ],
            temperature=0.4  # Balanced creativity and consistency
        )
        
        # Initialize RAG system and analysis tools
        self.knowledge_manager = BrandKnowledgeManager()
        self.analysis_tools = AnalysisTools()
        
        # Response generation metrics
        self.response_history = []
        self.response_metrics = {
            "total_responses_generated": 0,
            "successful_responses": 0,
            "avg_generation_time": 0.0,
            "avg_quality_score": 0.0,
            "knowledge_retrieval_success_rate": 0.0
        }
        
        # Response templates for different scenarios
        self.response_templates = {
            "positive_feedback": "Thank you for your positive feedback about {brand_name}! We're delighted to hear about your experience.",
            "negative_feedback": "Thank you for bringing this to our attention. We sincerely apologize for any inconvenience.",
            "question": "Thank you for reaching out to {brand_name}. We're here to help with your question.",
            "complaint": "We understand your frustration and want to make this right. Your concern is important to us.",
            "general": "Thank you for contacting {brand_name}. We appreciate you taking the time to reach out."
        }
        
        logger.info(f"🤖 Intelligent Response Agent {agent_id} initialized")
    
    async def create_tools(self) -> List[BaseTool]:
        """Create response generation and quality tools"""
        tools = []
        
        # Add RAG tools for knowledge retrieval
        tools.extend(self.knowledge_manager.get_rag_tools())
        
        # Add response quality and personalization tools
        tools.extend([
            ResponseQualityTool(),
            ResponsePersonalizationTool()
        ])
        
        return tools
    
    def get_system_prompt(self) -> str:
        """Get the agent's system prompt defining its role as intelligent response generator"""
        return f"""You are "BrandBot", an advanced AI response generation specialist with expertise in creating intelligent, empathetic, and fact-based customer responses.

CORE MISSION:
Generate intelligent, on-brand responses to customer mentions that are:
- FACTUALLY ACCURATE (always use knowledge base)
- EMPATHETIC and PROFESSIONAL
- STRATEGICALLY APPROPRIATE for the situation
- COMPLIANT with brand guidelines
- ACTIONABLE with clear next steps

YOUR MANDATORY PROCESS:
1. **ANALYZE THE MENTION**: Understand the customer's sentiment, emotion, intent, and specific concerns
2. **RETRIEVE BRAND KNOWLEDGE**: Use the 'retrieve_brand_knowledge' tool to find relevant policies, FAQs, or approved responses
3. **ASSESS CONTEXT**: Consider the platform, customer history, urgency level, and potential business impact
4. **GENERATE RESPONSE**: Create a response based ONLY on retrieved knowledge and brand guidelines
5. **QUALITY CHECK**: Use 'evaluate_response_quality' tool to ensure response meets standards
6. **PERSONALIZE**: Use 'personalize_response' tool to tailor the response to the specific customer and context

CRITICAL RULES:
- NEVER make up facts or policies - always retrieve from knowledge base first
- If no relevant knowledge is found, acknowledge limitation and offer to connect with support
- Always maintain professional, empathetic tone regardless of customer sentiment
- For negative sentiment: Lead with empathy, then solutions
- For positive sentiment: Show appreciation, reinforce positive experience
- Include clear next steps or call-to-action when appropriate

ESCALATION TRIGGERS:
Immediately recommend escalation for:
- Legal threats or compliance issues
- Media/influencer inquiries
- Extreme customer dissatisfaction
- Technical issues beyond general support
- Requests exceeding standard resolution limits

PLATFORM OPTIMIZATION:
- Twitter: Concise, engaging, use appropriate hashtags sparingly
- Facebook/Instagram: More conversational, can be slightly longer
- Reddit: Community-focused, authentic tone
- News/PR: Professional, official brand voice

QUALITY STANDARDS:
- Response length: 10-280 characters for social media
- Tone: Professional yet warm and approachable
- Include brand name when natural
- Provide actionable next steps
- Use positive language even when addressing problems

Remember: You represent the brand's voice and values. Every response should enhance the brand's reputation and provide genuine value to the customer.
"""
    
    async def generate_intelligent_response(
        self, 
        mention: Dict[str, Any], 
        brand_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent response using LLM reasoning + RAG
        This is the main method for creating fact-based, strategic responses
        """
        
        start_time = time.time()
        brand_name = brand_context.get("brand_name", "") if brand_context else ""
        
        # Prepare comprehensive context for LLM
        response_context = {
            "mention": mention,
            "brand_context": brand_context or {},
            "platform": mention.get("platform", "unknown"),
            "customer_sentiment": mention.get("sentiment", "neutral"),
            "urgency_level": self._assess_urgency(mention),
            "generation_timestamp": datetime.utcnow().isoformat()
        }
        
        # Create strategic response generation prompt
        generation_prompt = f"""
I need to generate an intelligent response to this customer mention:

CUSTOMER MENTION:
Platform: {mention.get('platform', 'unknown')}
Author: {mention.get('author', 'anonymous')}
Content: "{mention.get('content', '')}"
Sentiment: {mention.get('sentiment', 'unknown')}
Engagement: {mention.get('engagement_metrics', {})}

BRAND CONTEXT:
Brand Name: {brand_name}
Context: {brand_context or {}}

ANALYSIS:
Urgency Level: {response_context['urgency_level']}
Response Needed: {self._determine_response_type(mention)}

Following my mandatory process:
1. First, I'll retrieve relevant brand knowledge to ensure factual accuracy
2. Analyze the customer's specific needs and emotional state
3. Generate a response that addresses their concerns with empathy and professionalism
4. Ensure the response meets quality standards and brand guidelines
5. Personalize based on context and platform

Generate an intelligent, fact-based response that enhances our brand reputation and provides genuine value to the customer.
"""
        
        logger.info(f"🤖 Generating intelligent response for mention from {mention.get('author', 'unknown')} on {mention.get('platform', 'unknown')}")
        
        # Let the LLM generate the response using RAG and tools
        response = await self.think_and_act(generation_prompt, response_context)
        
        if not response["success"]:
            logger.error(f"❌ Response generation failed: {response.get('error', 'Unknown error')}")
            return await self._generate_fallback_response(mention, brand_context)
        
        # Extract the generated response and tools used
        generated_response = self._extract_generated_response(response["response"])
        tools_used = response.get("tools_used", [])
        
        # Validate response quality
        quality_assessment = await self._validate_response_quality(
            generated_response, mention, brand_name
        )
        
        # INTELLIGENT HUMAN-IN-THE-LOOP DECISION
        approval_decision = await self._make_autonomous_approval_decision(
            generated_response, mention, quality_assessment, brand_context
        )
        
        generation_time = time.time() - start_time
        
        final_result = {
            "success": True,
            "mention_id": mention.get("id", "unknown"),
            "brand_name": brand_name,
            "platform": mention.get("platform", "unknown"),
            "generated_response": generated_response,
            "llm_reasoning": response["response"],
            "tools_used": tools_used,
            "knowledge_retrieved": "retrieve_brand_knowledge" in tools_used,
            "quality_assessment": quality_assessment,
            "approval_decision": approval_decision,  # NEW: Intelligent HITL decision
            "generation_time": generation_time,
            "response_metadata": {
                "response_type": self._determine_response_type(mention),
                "urgency_level": response_context["urgency_level"],
                "personalization_applied": "personalize_response" in tools_used,
                "quality_checked": "evaluate_response_quality" in tools_used,
                "autonomous_approval": approval_decision.get("autonomous_decision", False),
                "requires_human_review": approval_decision.get("requires_human_review", True),
                "risk_score": approval_decision.get("risk_analysis", {}).get("overall_risk_score", 0.5)
            },
            "recommendations": self._generate_response_recommendations(mention, generated_response),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update metrics and history
        self._update_response_metrics(final_result, generation_time)
        self._add_to_response_history(final_result)
        
        logger.info(f"✅ Intelligent response generated successfully in {generation_time:.2f}s - Quality: {quality_assessment.get('assessment', 'unknown')}")
        
        return final_result
    
    def _assess_urgency(self, mention: Dict[str, Any]) -> str:
        """Assess the urgency level of a mention"""
        content = mention.get("content", "").lower()
        engagement = mention.get("engagement_metrics", {})
        
        # High urgency indicators
        high_urgency_keywords = [
            "urgent", "emergency", "asap", "immediately", "crisis", "lawsuit",
            "media", "press", "reporter", "boycott", "viral", "trending"
        ]
        
        # Medium urgency indicators
        medium_urgency_keywords = [
            "complaint", "problem", "issue", "disappointed", "angry", "frustrated",
            "refund", "compensation", "manager", "supervisor"
        ]
        
        # Check for high urgency
        if any(keyword in content for keyword in high_urgency_keywords):
            return "high"
        
        # Check for viral potential (high engagement)
        if (engagement.get("likes", 0) > 100 or 
            engagement.get("retweets", 0) > 50 or 
            engagement.get("shares", 0) > 25):
            return "high"
        
        # Check for medium urgency
        if any(keyword in content for keyword in medium_urgency_keywords):
            return "medium"
        
        return "low"
    
    def _determine_response_type(self, mention: Dict[str, Any]) -> str:
        """Determine the type of response needed"""
        content = mention.get("content", "").lower()
        sentiment = mention.get("sentiment", "neutral")
        
        if sentiment == "negative" or any(word in content for word in ["complaint", "problem", "issue", "disappointed"]):
            return "complaint"
        elif sentiment == "positive" or any(word in content for word in ["love", "great", "amazing", "excellent"]):
            return "positive_feedback"
        elif "?" in content or any(word in content for word in ["how", "what", "when", "where", "why"]):
            return "question"
        else:
            return "general"
    
    def _extract_generated_response(self, llm_response: str) -> str:
        """Extract the actual response from LLM reasoning"""
        lines = llm_response.split('\n')
        
        # Look for common response indicators
        response_indicators = [
            "final response:",
            "response:",
            "generated response:",
            "my response:",
            "reply:",
            "suggested response:"
        ]
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if this line contains a response indicator
            for indicator in response_indicators:
                if indicator in line_lower:
                    # The response should be on this line or the next
                    if len(line.split(':')) > 1:
                        response = line.split(':', 1)[1].strip()
                        if response and len(response) > 10:
                            return response
                    
                    # Check next lines for the response
                    for j in range(i + 1, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and len(next_line) > 10 and not next_line.lower().startswith(('note:', 'explanation:', 'reasoning:')):
                            return next_line
        
        # If no clear response found, try to find the longest meaningful sentence
        sentences = [line.strip() for line in lines if len(line.strip()) > 20]
        if sentences:
            # Return the longest sentence that looks like a response
            return max(sentences, key=len)
        
        # Fallback: return a portion of the LLM response
        return llm_response[:200] + "..." if len(llm_response) > 200 else llm_response
    
    async def _validate_response_quality(
        self, 
        generated_response: str, 
        mention: Dict[str, Any], 
        brand_name: str
    ) -> Dict[str, Any]:
        """Validate the quality of generated response"""
        try:
            # Use the response quality tool
            quality_tool = ResponseQualityTool()
            quality_result = await quality_tool._arun(
                response=generated_response,
                original_mention=mention.get("content", ""),
                brand_name=brand_name
            )
            
            return json.loads(quality_result)
            
        except Exception as e:
            logger.error(f"❌ Response quality validation failed: {e}")
            return {
                "quality_score": 0.5,
                "assessment": "unknown",
                "error": str(e)
            }
    
    async def _make_autonomous_approval_decision(
        self, 
        response: str, 
        mention: Dict[str, Any], 
        quality_assessment: Dict[str, Any],
        brand_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make intelligent autonomous decisions about response approval
        This is the HITL intelligence that separates this system from basic chatbots
        """
        
        try:
            # Calculate comprehensive risk score
            risk_analysis = await self._calculate_comprehensive_risk_score(
                response, mention, quality_assessment, brand_context
            )
            
            risk_score = risk_analysis["overall_risk_score"]
            risk_factors = risk_analysis["risk_factors"]
            
            # AUTONOMOUS DECISION LOGIC
            if risk_score < settings.AUTO_RESPONSE_RISK_THRESHOLD:
                # LOW RISK: Auto-approve
                decision = {
                    "approval_status": "approved_auto",
                    "decision_reasoning": f"Low risk score ({risk_score:.3f}) below auto-approval threshold ({settings.AUTO_RESPONSE_RISK_THRESHOLD}). Safe for autonomous publishing.",
                    "autonomous_decision": True,
                    "requires_human_review": False,
                    "recommended_action": "publish_immediately",
                    "confidence": "high"
                }
                
                logger.info(f"🤖 AUTONOMOUS APPROVAL: Risk {risk_score:.3f} - Auto-approving response")
                
            elif risk_score > settings.HUMAN_REVIEW_RISK_THRESHOLD:
                # HIGH RISK: Require human approval
                decision = {
                    "approval_status": "pending_approval",
                    "decision_reasoning": f"High risk score ({risk_score:.3f}) above human review threshold ({settings.HUMAN_REVIEW_RISK_THRESHOLD}). Requires human oversight due to: {', '.join(risk_factors)}",
                    "autonomous_decision": True,
                    "requires_human_review": True,
                    "recommended_action": "escalate_for_approval",
                    "confidence": "high",
                    "escalation_triggers": risk_factors,
                    "suggested_reviewers": await self._suggest_appropriate_reviewers(risk_factors)
                }
                
                logger.warning(f"🚨 HUMAN REVIEW REQUIRED: Risk {risk_score:.3f} - Escalating for approval")
                
                # Trigger alert for human review
                await self._trigger_human_review_alert(response, mention, risk_analysis, decision)
                
            else:
                # MEDIUM RISK: Smart review based on context
                contextual_decision = await self._make_contextual_risk_decision(
                    response, mention, risk_analysis, brand_context
                )
                
                decision = {
                    "approval_status": contextual_decision["status"],
                    "decision_reasoning": f"Medium risk score ({risk_score:.3f}). {contextual_decision['reasoning']}",
                    "autonomous_decision": True,
                    "requires_human_review": contextual_decision["requires_review"],
                    "recommended_action": contextual_decision["action"],
                    "confidence": "medium",
                    "contextual_factors": contextual_decision["factors"]
                }
                
                logger.info(f"🎯 CONTEXTUAL DECISION: Risk {risk_score:.3f} - {contextual_decision['status']}")
            
            # Add comprehensive decision metadata
            decision.update({
                "risk_analysis": risk_analysis,
                "decision_timestamp": datetime.utcnow().isoformat(),
                "decision_agent": "IntelligentResponseAgent",
                "thresholds_used": {
                    "auto_approve": settings.AUTO_RESPONSE_RISK_THRESHOLD,
                    "human_review": settings.HUMAN_REVIEW_RISK_THRESHOLD
                }
            })
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Autonomous approval decision failed: {e}")
            # Fail safely - require human review
            return {
                "approval_status": "pending_approval",
                "decision_reasoning": f"Decision system error: {str(e)}. Defaulting to human review for safety.",
                "autonomous_decision": False,
                "requires_human_review": True,
                "recommended_action": "escalate_for_approval",
                "confidence": "low",
                "error": str(e)
            }
    
    async def _calculate_comprehensive_risk_score(
        self, 
        response: str, 
        mention: Dict[str, Any], 
        quality_assessment: Dict[str, Any],
        brand_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk score for autonomous decision making"""
        
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Response Quality (30% weight)
        quality_score = quality_assessment.get("quality_score", 0.5)
        quality_risk = (1.0 - quality_score) * 0.3
        risk_score += quality_risk
        
        if quality_score < 0.6:
            risk_factors.append("low_response_quality")
        
        # Factor 2: Mention Sentiment and Urgency (25% weight)
        mention_sentiment = mention.get("sentiment", "neutral")
        if mention_sentiment == "negative":
            sentiment_risk = 0.2 * 0.25
            risk_factors.append("negative_customer_sentiment")
        elif mention_sentiment == "positive":
            sentiment_risk = 0.05 * 0.25
        else:
            sentiment_risk = 0.1 * 0.25
        
        risk_score += sentiment_risk
        
        # Factor 3: Engagement and Virality Potential (20% weight)
        engagement = mention.get("engagement_metrics", {})
        high_engagement = (
            engagement.get("likes", 0) > 100 or 
            engagement.get("retweets", 0) > 50 or 
            engagement.get("shares", 0) > 25
        )
        
        if high_engagement:
            virality_risk = 0.3 * 0.2
            risk_factors.append("high_visibility_mention")
        else:
            virality_risk = 0.1 * 0.2
        
        risk_score += virality_risk
        
        # Factor 4: Content Risk Analysis (15% weight)
        content_risks = await self._analyze_content_risk(response, mention)
        content_risk = content_risks["risk_score"] * 0.15
        risk_score += content_risk
        risk_factors.extend(content_risks["risk_factors"])
        
        # Factor 5: Crisis Detection (10% weight)
        crisis_indicators = mention.get("crisis_indicators", {})
        if crisis_indicators.get("crisis_detected", False):
            crisis_risk = 0.4 * 0.1
            risk_factors.append("crisis_situation_detected")
        else:
            crisis_risk = 0.05 * 0.1
        
        risk_score += crisis_risk
        
        # Normalize risk score to 0-1 range
        risk_score = min(1.0, max(0.0, risk_score))
        
        return {
            "overall_risk_score": risk_score,
            "risk_factors": list(set(risk_factors)),
            "component_risks": {
                "quality_risk": quality_risk,
                "sentiment_risk": sentiment_risk,
                "virality_risk": virality_risk,
                "content_risk": content_risk,
                "crisis_risk": crisis_risk
            },
            "risk_category": "low" if risk_score < 0.3 else "medium" if risk_score < 0.7 else "high"
        }
    
    async def _analyze_content_risk(self, response: str, mention: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content-specific risks in the response"""
        risk_factors = []
        risk_score = 0.0
        
        response_lower = response.lower()
        mention_content = mention.get("content", "").lower()
        
        # Check for potentially problematic content
        high_risk_topics = [
            "lawsuit", "legal", "court", "sue", "attorney", "lawyer",
            "discrimination", "harassment", "bias", "racist", "sexist",
            "medical", "health", "diagnosis", "treatment", "medication",
            "financial", "investment", "stock", "price", "earnings"
        ]
        
        for topic in high_risk_topics:
            if topic in response_lower or topic in mention_content:
                risk_score += 0.1
                risk_factors.append(f"high_risk_topic_{topic}")
        
        # Check for commitment or promise language
        commitment_words = ["guarantee", "promise", "will definitely", "absolutely will", "we ensure"]
        for word in commitment_words:
            if word in response_lower:
                risk_score += 0.05
                risk_factors.append("strong_commitment_language")
        
        # Check response length (very short or very long responses are riskier)
        if len(response) < 20:
            risk_score += 0.1
            risk_factors.append("response_too_short")
        elif len(response) > 500:
            risk_score += 0.05
            risk_factors.append("response_very_long")
        
        return {
            "risk_score": min(1.0, risk_score),
            "risk_factors": risk_factors
        }
    
    async def _make_contextual_risk_decision(
        self, 
        response: str, 
        mention: Dict[str, Any], 
        risk_analysis: Dict[str, Any],
        brand_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make intelligent contextual decisions for medium-risk responses"""
        
        # Analyze contextual factors
        platform = mention.get("platform", "unknown").lower()
        time_of_day = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        
        contextual_factors = []
        
        # Platform-specific decisions
        if platform == "twitter":
            # Twitter moves fast, slightly more aggressive auto-approval
            auto_approve_bias = 0.1
            contextual_factors.append("twitter_fast_paced_platform")
        elif platform == "linkedin":
            # LinkedIn is professional, be more cautious
            auto_approve_bias = -0.1
            contextual_factors.append("linkedin_professional_platform")
        else:
            auto_approve_bias = 0.0
        
        # Time-based decisions
        if 9 <= time_of_day <= 17 and not is_weekend:
            # Business hours - human reviewers likely available
            auto_approve_bias -= 0.05
            contextual_factors.append("business_hours_reviewers_available")
        else:
            # Outside business hours - lean towards auto-approval for efficiency
            auto_approve_bias += 0.1
            contextual_factors.append("outside_business_hours")
        
        # Brand context considerations
        if brand_context and brand_context.get("crisis_mode", False):
            auto_approve_bias -= 0.2
            contextual_factors.append("brand_in_crisis_mode")
        
        # Make final contextual decision
        adjusted_threshold = settings.AUTO_RESPONSE_RISK_THRESHOLD + auto_approve_bias
        risk_score = risk_analysis["overall_risk_score"]
        
        if risk_score < adjusted_threshold:
            return {
                "status": "approved_contextual",
                "reasoning": f"Contextual analysis suggests auto-approval (adjusted threshold: {adjusted_threshold:.3f})",
                "requires_review": False,
                "action": "publish_immediately",
                "factors": contextual_factors
            }
        else:
            return {
                "status": "pending_approval",
                "reasoning": f"Contextual analysis suggests human review (adjusted threshold: {adjusted_threshold:.3f})",
                "requires_review": True,
                "action": "escalate_for_approval",
                "factors": contextual_factors
            }
    
    async def _suggest_appropriate_reviewers(self, risk_factors: List[str]) -> List[str]:
        """Suggest appropriate human reviewers based on risk factors"""
        reviewers = []
        
        # Map risk factors to appropriate reviewer types
        if any("crisis" in factor for factor in risk_factors):
            reviewers.extend(["crisis_manager", "brand_director", "ceo"])
        
        if any("legal" in factor for factor in risk_factors):
            reviewers.extend(["legal_team", "compliance_officer"])
        
        if any("medical" in factor or "health" in factor for factor in risk_factors):
            reviewers.extend(["medical_affairs", "regulatory_team"])
        
        if any("financial" in factor for factor in risk_factors):
            reviewers.extend(["investor_relations", "cfo"])
        
        if any("high_visibility" in factor for factor in risk_factors):
            reviewers.extend(["social_media_manager", "pr_manager"])
        
        # Default reviewers if no specific expertise needed
        if not reviewers:
            reviewers = ["social_media_manager", "customer_service_manager"]
        
        return list(set(reviewers))  # Remove duplicates
    
    async def _trigger_human_review_alert(
        self, 
        response: str, 
        mention: Dict[str, Any], 
        risk_analysis: Dict[str, Any],
        decision: Dict[str, Any]
    ):
        """Trigger alerts for human review of high-risk responses"""
        
        alert_data = {
            "alert_type": "human_review_required",
            "priority": "high" if risk_analysis["overall_risk_score"] > 0.8 else "medium",
            "response_content": response[:200] + "..." if len(response) > 200 else response,
            "mention_summary": {
                "platform": mention.get("platform"),
                "author": mention.get("author"),
                "content_preview": mention.get("content", "")[:100] + "...",
                "sentiment": mention.get("sentiment")
            },
            "risk_analysis": risk_analysis,
            "suggested_reviewers": decision.get("suggested_reviewers", []),
            "escalation_triggers": decision.get("escalation_triggers", []),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Log the alert (in production, this would trigger actual notifications)
        logger.warning(f"🚨 HUMAN REVIEW ALERT: {alert_data['alert_type']} - Risk: {risk_analysis['overall_risk_score']:.3f}")
        logger.info(f"   Suggested reviewers: {alert_data['suggested_reviewers']}")
        logger.info(f"   Escalation triggers: {alert_data['escalation_triggers']}")
        
        # In production, integrate with:
        # - Slack/Teams notifications
        # - Email alerts
        # - Dashboard notifications
        # - SMS for critical alerts
        # - CRM system updates
    
    def _generate_response_recommendations(
        self, 
        mention: Dict[str, Any], 
        response: str
    ) -> List[str]:
        """Generate recommendations for response improvement"""
        recommendations = []
        
        urgency = self._assess_urgency(mention)
        if urgency == "high":
            recommendations.append("Consider escalating to human agent due to high urgency level")
        
        if len(response) > 280:
            recommendations.append("Consider shortening response for social media platforms")
        
        sentiment = mention.get("sentiment", "neutral")
        if sentiment == "negative" and "sorry" not in response.lower():
            recommendations.append("Consider adding empathetic language for negative sentiment")
        
        if not any(word in response.lower() for word in ["contact", "support", "help", "visit", "email"]):
            recommendations.append("Consider adding clear next steps or contact information")
        
        return recommendations
    
    async def _generate_fallback_response(
        self, 
        mention: Dict[str, Any], 
        brand_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate fallback response when LLM fails"""
        brand_name = brand_context.get("brand_name", "our team") if brand_context else "our team"
        response_type = self._determine_response_type(mention)
        
        # Use appropriate template
        template = self.response_templates.get(response_type, self.response_templates["general"])
        fallback_response = template.format(brand_name=brand_name)
        
        # Add generic helpful ending
        fallback_response += " Please DM us or visit our support page for assistance."
        
        return {
            "success": True,
            "generated_response": fallback_response,
            "fallback_mode": True,
            "llm_reasoning": "Fallback response due to LLM generation failure",
            "quality_assessment": {"quality_score": 0.6, "assessment": "acceptable"},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _update_response_metrics(self, result: Dict[str, Any], generation_time: float):
        """Update response generation metrics"""
        self.response_metrics["total_responses_generated"] += 1
        
        if result["success"]:
            self.response_metrics["successful_responses"] += 1
        
        # Update average generation time
        current_avg = self.response_metrics["avg_generation_time"]
        total_responses = self.response_metrics["total_responses_generated"]
        self.response_metrics["avg_generation_time"] = (
            (current_avg * (total_responses - 1) + generation_time) / total_responses
        )
        
        # Update average quality score
        quality_score = result.get("quality_assessment", {}).get("quality_score", 0.0)
        current_quality_avg = self.response_metrics["avg_quality_score"]
        self.response_metrics["avg_quality_score"] = (
            (current_quality_avg * (total_responses - 1) + quality_score) / total_responses
        )
        
        # Update knowledge retrieval success rate
        if result.get("knowledge_retrieved", False):
            successful_retrievals = self.response_metrics.get("successful_knowledge_retrievals", 0) + 1
            self.response_metrics["successful_knowledge_retrievals"] = successful_retrievals
            self.response_metrics["knowledge_retrieval_success_rate"] = (
                successful_retrievals / total_responses
            )
    
    def _add_to_response_history(self, result: Dict[str, Any]):
        """Add response to history for learning"""
        self.response_history.append({
            "timestamp": datetime.utcnow(),
            "mention_id": result.get("mention_id"),
            "platform": result.get("platform"),
            "response_quality": result.get("quality_assessment", {}).get("quality_score", 0.0),
            "generation_time": result.get("generation_time", 0.0),
            "knowledge_used": result.get("knowledge_retrieved", False)
        })
        
        # Keep history manageable
        if len(self.response_history) > 1000:
            self.response_history = self.response_history[-500:]
    
    async def batch_generate_responses(
        self, 
        mentions: List[Dict[str, Any]], 
        brand_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Generate responses for multiple mentions efficiently"""
        
        logger.info(f"🚀 Starting batch response generation for {len(mentions)} mentions")
        
        # Process in parallel for efficiency (with reasonable concurrency limit)
        semaphore = asyncio.Semaphore(5)  # Limit concurrent generations
        
        async def generate_single_response(mention):
            async with semaphore:
                return await self.generate_intelligent_response(mention, brand_context)
        
        # Execute all generations
        tasks = [generate_single_response(mention) for mention in mentions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch generation failed for mention {i}: {result}")
                failed_count += 1
                successful_results.append({
                    "success": False,
                    "mention_id": mentions[i].get("id", f"mention_{i}"),
                    "error": str(result)
                })
            else:
                successful_results.append(result)
        
        success_count = len([r for r in successful_results if r.get("success", False)])
        logger.info(f"✅ Batch generation complete: {success_count}/{len(mentions)} successful")
        
        return successful_results
    
    def get_response_insights(self) -> Dict[str, Any]:
        """Get insights about response generation performance"""
        return {
            "response_metrics": self.response_metrics,
            "knowledge_base_stats": self.knowledge_manager.get_system_status(),
            "recent_response_quality": [
                h["response_quality"] for h in self.response_history[-10:]
            ],
            "platform_distribution": self._get_platform_distribution(),
            "response_type_distribution": self._get_response_type_distribution(),
            "avg_response_length": self._get_avg_response_length()
        }
    
    def _get_platform_distribution(self) -> Dict[str, int]:
        """Get distribution of responses by platform"""
        distribution = {}
        for entry in self.response_history:
            platform = entry.get("platform", "unknown")
            distribution[platform] = distribution.get(platform, 0) + 1
        return distribution
    
    def _get_response_type_distribution(self) -> Dict[str, int]:
        """Get distribution of response types"""
        # This would require storing response type in history
        # For now, return placeholder data
        return {
            "complaint": len([h for h in self.response_history if h.get("response_quality", 0) < 0.6]),
            "positive_feedback": len([h for h in self.response_history if h.get("response_quality", 0) > 0.8]),
            "question": len([h for h in self.response_history if 0.6 <= h.get("response_quality", 0) <= 0.8]),
            "general": len(self.response_history) // 4  # Rough estimate
        }
    
    def _get_avg_response_length(self) -> float:
        """Calculate average response length (would need to store in history)"""
        # Placeholder - would require storing response length in history
        return 150.0  # Average social media response length


# Legacy wrapper for backward compatibility
class ResponseGenerationAgent(IntelligentResponseAgent):
    """Legacy wrapper - now powered by LLM + RAG intelligence"""
    
    def __init__(self, agent_id: str = "response_generator"):
        super().__init__(agent_id)
        logger.info(f"Legacy Response Generation Agent {agent_id} initialized with RAG intelligence")
    
    async def generate_response(
        self, 
        mention_text: str, 
        brand_name: str, 
        platform: str = "social"
    ) -> Dict[str, Any]:
        """Legacy method - now uses intelligent generation with RAG"""
        
        # Convert to new format
        mention = {
            "content": mention_text,
            "platform": platform,
            "author": "user",
            "sentiment": "neutral"  # Would be analyzed by sentiment agent
        }
        
        brand_context = {"brand_name": brand_name}
        
        result = await self.generate_intelligent_response(mention, brand_context)
        
        # Convert to legacy format
        return {
            "status": "success" if result["success"] else "error",
            "response": result.get("generated_response", ""),
            "brand_name": brand_name,
            "platform": platform,
            "generation_time": result.get("generation_time", 0.0),
            "quality_score": result.get("quality_assessment", {}).get("quality_score", 0.0),
            "rag_used": result.get("knowledge_retrieved", False),
            "llm_reasoning": result.get("llm_reasoning", "")
        }
