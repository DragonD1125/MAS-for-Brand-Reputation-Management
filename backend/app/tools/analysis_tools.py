"""
Advanced Analysis Tools powered by State-of-the-Art NLP Models
These tools provide the LLM agents with access to sophisticated AI models
for sentiment analysis, emotion detection, and crisis identification.

NOTE: Uses lazy loading to avoid slow startup from heavy ML imports
"""

import asyncio
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from loguru import logger

from app.core.config import settings

# Lazy imports for heavy ML libraries
_torch = None
_transformers = None

def _get_torch():
    global _torch
    if _torch is None:
        import torch
        _torch = torch
    return _torch

def _get_transformers():
    global _transformers
    if _transformers is None:
        import transformers
        _transformers = transformers
    return _transformers


class AnalysisTools:
    """Collection of AI-powered analysis tools for LLM agents (with lazy loading)"""
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self.crisis_pipeline = None
        self.device = None
        self._models_initialized = False
    
    def _initialize_models(self):
        """Initialize all AI models (lazy loaded on first use)"""
        if self._models_initialized:
            return
            
        try:
            torch = _get_torch()
            transformers = _get_transformers()
            pipeline = transformers.pipeline
            
            self.device = "cuda" if torch.cuda.is_available() and settings.ENABLE_GPU else "cpu"
            logger.info(f"Initializing AI models on device: {self.device}")
            
            # Sentiment Analysis - State-of-the-art Twitter RoBERTa
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True,
                device=0 if self.device == "cuda" else -1
            )
            
            # Emotion Detection - Advanced emotion classifier
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True,
                device=0 if self.device == "cuda" else -1
            )
            
            # Crisis Detection - Custom fine-tuned model (fallback to general classifier)
            self.crisis_pipeline = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                return_all_scores=True,
                device=0 if self.device == "cuda" else -1
            )
            
            self._models_initialized = True
            logger.info("✅ All AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            # Fallback to simpler models or CPU
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Initialize simpler models as fallback"""
        try:
            transformers = _get_transformers()
            logger.info("Initializing fallback models...")
            self.sentiment_pipeline = transformers.pipeline("sentiment-analysis", device=-1)
            self._models_initialized = True
            logger.info("✅ Fallback models initialized")
        except Exception as e:
            logger.error(f"Failed to initialize fallback models: {e}")
            self.sentiment_pipeline = None
            self._models_initialized = True  # Mark as tried


async def analyze_sentiment_with_bert(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment using state-of-the-art BERT-based models.
    This function is designed to be used as a LangChain Tool.
    
    Args:
        text: The text content to analyze
        
    Returns:
        Comprehensive sentiment analysis results
    """
    try:
        tools = AnalysisTools()
        tools._initialize_models()  # Lazy load models on first use
        
        if not tools.sentiment_pipeline:
            raise ValueError("Sentiment analysis model not available")
        
        # Preprocess text
        cleaned_text = _preprocess_text(text)
        
        if len(cleaned_text.strip()) == 0:
            return {
                "overall_sentiment": "neutral",
                "confidence": 0.1,
                "scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                "error": "Empty or invalid text"
            }
        
        # Run sentiment analysis
        sentiment_results = tools.sentiment_pipeline(cleaned_text)
        
        # Process results
        sentiment_scores = {}
        for result in sentiment_results[0]:
            label = result['label'].lower()
            score = result['score']
            
            # Map model labels to our standard format
            if 'positive' in label or label == 'pos':
                sentiment_scores['positive'] = score
            elif 'negative' in label or label == 'neg':
                sentiment_scores['negative'] = score
            else:
                sentiment_scores['neutral'] = score
        
        # Determine overall sentiment
        overall_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])[0]
        confidence = max(sentiment_scores.values())
        
        # Add metadata
        analysis_result = {
            "overall_sentiment": overall_sentiment,
            "confidence": round(confidence, 4),
            "scores": {k: round(v, 4) for k, v in sentiment_scores.items()},
            "model_used": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "text_length": len(text),
            "processed_text_length": len(cleaned_text)
        }
        
        logger.debug(f"Sentiment analysis completed: {overall_sentiment} (confidence: {confidence:.3f})")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in BERT sentiment analysis: {e}")
        return {
            "overall_sentiment": "neutral",
            "confidence": 0.0,
            "scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
            "error": str(e),
            "fallback_used": True
        }


async def analyze_emotions_with_ai(text: str) -> Dict[str, Any]:
    """
    Analyze emotions using advanced AI models.
    This function is designed to be used as a LangChain Tool.
    
    Args:
        text: The text content to analyze
        
    Returns:
        Detailed emotion analysis results
    """
    try:
        tools = AnalysisTools()
        
        if not tools.emotion_pipeline:
            return await _fallback_emotion_analysis(text)
        
        cleaned_text = _preprocess_text(text)
        
        if len(cleaned_text.strip()) == 0:
            return {
                "dominant_emotion": "neutral",
                "confidence": 0.1,
                "emotions": {},
                "error": "Empty or invalid text"
            }
        
        # Run emotion analysis
        emotion_results = tools.emotion_pipeline(cleaned_text)
        
        # Process results
        emotions = {}
        for result in emotion_results[0]:
            emotions[result['label'].lower()] = round(result['score'], 4)
        
        # Find dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        
        analysis_result = {
            "dominant_emotion": dominant_emotion[0],
            "confidence": dominant_emotion[1],
            "emotions": emotions,
            "model_used": "j-hartmann/emotion-english-distilroberta-base",
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "emotion_diversity": len([e for e in emotions.values() if e > 0.1])  # Number of emotions above threshold
        }
        
        logger.debug(f"Emotion analysis completed: {dominant_emotion[0]} (confidence: {dominant_emotion[1]:.3f})")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in AI emotion analysis: {e}")
        return await _fallback_emotion_analysis(text)


async def detect_crisis_indicators_with_ai(text: str, brand_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Detect crisis indicators using AI models and contextual analysis.
    This function is designed to be used as a LangChain Tool.
    
    Args:
        text: The text content to analyze
        brand_context: Optional brand-specific context for analysis
        
    Returns:
        Crisis detection analysis results
    """
    try:
        cleaned_text = _preprocess_text(text)
        
        if len(cleaned_text.strip()) == 0:
            return {
                "has_crisis_indicators": False,
                "risk_level": "low",
                "confidence": 0.1,
                "indicators": [],
                "error": "Empty or invalid text"
            }
        
        # Multi-layered crisis detection
        crisis_analysis = {
            "keyword_indicators": await _detect_keyword_crisis_indicators(cleaned_text),
            "pattern_indicators": await _detect_pattern_crisis_indicators(cleaned_text),
            "sentiment_severity": await _assess_sentiment_severity(cleaned_text),
            "urgency_signals": await _detect_urgency_signals(cleaned_text)
        }
        
        # Calculate overall risk score
        risk_score = _calculate_crisis_risk_score(crisis_analysis)
        
        # Determine risk level
        risk_level = "low"
        if risk_score >= 0.8:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        
        # Compile all detected indicators
        all_indicators = []
        for category, indicators in crisis_analysis.items():
            if isinstance(indicators, dict) and indicators.get("detected"):
                all_indicators.extend(indicators.get("indicators", []))
        
        result = {
            "has_crisis_indicators": risk_score > 0.3,
            "risk_level": risk_level,
            "risk_score": round(risk_score, 4),
            "confidence": min(0.9, risk_score + 0.1),  # Higher risk = higher confidence
            "indicators": all_indicators,
            "detailed_analysis": crisis_analysis,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "requires_immediate_attention": risk_score >= 0.7
        }
        
        if brand_context:
            result["brand_context_applied"] = True
            result["brand_id"] = brand_context.get("brand_id")
        
        logger.debug(f"Crisis detection completed: {risk_level} risk (score: {risk_score:.3f})")
        return result
        
    except Exception as e:
        logger.error(f"Error in AI crisis detection: {e}")
        return {
            "has_crisis_indicators": False,
            "risk_level": "unknown",
            "confidence": 0.0,
            "error": str(e),
            "fallback_used": True
        }


def _preprocess_text(text: str) -> str:
    """Preprocess text for AI analysis"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Clean up mentions and hashtags (keep the text, remove symbols)
    text = re.sub(r'[@#](\w+)', r'\1', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate if too long (BERT models have token limits)
    if len(text) > 500:
        text = text[:500]
    
    return text


async def _fallback_emotion_analysis(text: str) -> Dict[str, Any]:
    """Fallback emotion analysis using keyword matching"""
    emotion_keywords = {
        "joy": ["happy", "excited", "thrilled", "delighted", "cheerful", "elated"],
        "anger": ["angry", "frustrated", "furious", "mad", "irritated", "rage"],
        "sadness": ["sad", "disappointed", "upset", "depressed", "unhappy", "grief"],
        "fear": ["scared", "worried", "anxious", "nervous", "afraid", "panic"],
        "surprise": ["surprised", "amazed", "shocked", "astonished", "stunned"],
        "trust": ["trust", "confidence", "reliable", "dependable", "faith"],
        "disgust": ["disgusted", "revolting", "awful", "terrible", "gross"]
    }
    
    text_lower = text.lower()
    emotion_scores = {}
    
    for emotion, keywords in emotion_keywords.items():
        score = sum(1 for word in keywords if word in text_lower)
        emotion_scores[emotion] = score / len(keywords)
    
    if not emotion_scores or max(emotion_scores.values()) == 0:
        return {
            "dominant_emotion": "neutral",
            "confidence": 0.3,
            "emotions": emotion_scores,
            "fallback_used": True
        }
    
    dominant = max(emotion_scores.items(), key=lambda x: x[1])
    return {
        "dominant_emotion": dominant[0],
        "confidence": min(0.8, dominant[1] * 2),  # Scale up but cap at 0.8
        "emotions": emotion_scores,
        "fallback_used": True
    }


async def _detect_keyword_crisis_indicators(text: str) -> Dict[str, Any]:
    """Detect crisis indicators using keyword analysis"""
    crisis_keywords = {
        "legal": ["lawsuit", "sue", "court", "legal action", "attorney", "lawyer"],
        "safety": ["dangerous", "toxic", "poison", "death", "injury", "harm", "unsafe"],
        "reputation": ["boycott", "scandal", "controversy", "fraud", "scam", "fake"],
        "operational": ["recall", "defective", "broken", "failure", "outage", "down"],
        "financial": ["bankruptcy", "fraud", "embezzlement", "loss", "debt", "collapse"]
    }
    
    text_lower = text.lower()
    detected_indicators = []
    category_scores = {}
    
    for category, keywords in crisis_keywords.items():
        matches = [kw for kw in keywords if kw in text_lower]
        if matches:
            detected_indicators.extend(matches)
            category_scores[category] = len(matches) / len(keywords)
    
    return {
        "detected": len(detected_indicators) > 0,
        "indicators": detected_indicators,
        "category_scores": category_scores,
        "severity": "high" if len(detected_indicators) >= 3 else "medium" if detected_indicators else "low"
    }


async def _detect_pattern_crisis_indicators(text: str) -> Dict[str, Any]:
    """Detect crisis patterns using regex analysis"""
    crisis_patterns = [
        (r"\b(?:never\s+again|never\s+buying)\b", "boycott_intent"),
        (r"\b(?:going\s+viral|spread\s+the\s+word)\b", "viral_spread"),
        (r"\b(?:class\s+action|mass\s+lawsuit)\b", "legal_action"),
        (r"\b(?:everyone\s+knows|public\s+knowledge)\b", "reputation_damage"),
        (r"\b(?:urgent|immediate|emergency)\b", "urgency")
    ]
    
    detected_patterns = []
    text_lower = text.lower()
    
    for pattern, indicator_type in crisis_patterns:
        if re.search(pattern, text_lower):
            detected_patterns.append({
                "pattern": pattern,
                "type": indicator_type,
                "severity": "high" if indicator_type in ["legal_action", "viral_spread"] else "medium"
            })
    
    return {
        "detected": len(detected_patterns) > 0,
        "patterns": detected_patterns,
        "severity": "high" if any(p["severity"] == "high" for p in detected_patterns) else "medium"
    }


async def _assess_sentiment_severity(text: str) -> Dict[str, Any]:
    """Assess the severity of negative sentiment"""
    # Use the sentiment analysis tool
    sentiment_result = await analyze_sentiment_with_bert(text)
    
    negative_score = sentiment_result.get("scores", {}).get("negative", 0)
    confidence = sentiment_result.get("confidence", 0)
    
    # Calculate severity based on negative sentiment strength
    severity_score = negative_score * confidence
    
    return {
        "detected": negative_score > 0.6,
        "negative_score": negative_score,
        "severity_score": severity_score,
        "severity": "high" if severity_score > 0.7 else "medium" if severity_score > 0.4 else "low"
    }


async def _detect_urgency_signals(text: str) -> Dict[str, Any]:
    """Detect urgency and escalation signals"""
    urgency_indicators = [
        "urgent", "immediate", "asap", "emergency", "breaking", "alert",
        "right now", "immediately", "crisis", "critical", "help"
    ]
    
    text_lower = text.lower()
    detected_urgency = [word for word in urgency_indicators if word in text_lower]
    
    # Check for time-sensitive language
    time_sensitive_patterns = [
        r"\b(?:today|tonight|now|quickly|fast)\b",
        r"\b(?:deadline|expires|urgent|emergency)\b"
    ]
    
    pattern_matches = []
    for pattern in time_sensitive_patterns:
        if re.search(pattern, text_lower):
            pattern_matches.append(pattern)
    
    urgency_score = (len(detected_urgency) + len(pattern_matches)) / 10  # Normalize
    
    return {
        "detected": urgency_score > 0.1,
        "urgency_words": detected_urgency,
        "time_patterns": pattern_matches,
        "urgency_score": min(1.0, urgency_score),
        "severity": "high" if urgency_score > 0.5 else "medium" if urgency_score > 0.2 else "low"
    }


def _calculate_crisis_risk_score(crisis_analysis: Dict[str, Any]) -> float:
    """Calculate overall crisis risk score from all indicators"""
    weights = {
        "keyword_indicators": 0.3,
        "pattern_indicators": 0.25,
        "sentiment_severity": 0.25,
        "urgency_signals": 0.2
    }
    
    total_score = 0.0
    
    for category, weight in weights.items():
        analysis = crisis_analysis.get(category, {})
        
        if category == "sentiment_severity":
            # Use severity score directly
            score = analysis.get("severity_score", 0)
        else:
            # Convert severity levels to numeric scores
            severity = analysis.get("severity", "low")
            if severity == "high":
                score = 1.0
            elif severity == "medium":
                score = 0.6
            else:
                score = 0.2 if analysis.get("detected", False) else 0.0
        
        total_score += score * weight
    
    return min(1.0, total_score)  # Cap at 1.0


# Initialize global tools instance for performance
_tools_instance = None

def get_analysis_tools() -> AnalysisTools:
    """Get global analysis tools instance"""
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = AnalysisTools()
    return _tools_instance
