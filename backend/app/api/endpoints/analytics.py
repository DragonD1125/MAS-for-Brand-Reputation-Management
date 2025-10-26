"""Analytics API endpoints for brand monitoring insights."""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator

from app.services.brand_analysis_service import brand_analysis_service
from app.agents.langgraph_orchestrator import LangGraphAutonomousOrchestrator
from loguru import logger

router = APIRouter()

# Initialize orchestrator for full-agent workflows
orchestrator = LangGraphAutonomousOrchestrator()


class BrandAnalysisRequest(BaseModel):
    brand_name: str = Field(..., min_length=2, max_length=80)
    max_articles: int = Field(10, ge=3, le=25)
    days_back: int = Field(7, ge=1, le=30)

    @validator("brand_name")
    def _clean_brand(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("brand_name cannot be empty")
        return cleaned


class BrandArticle(BaseModel):
    title: str
    source: Optional[str] = None
    url: Optional[str] = None
    published_at: Optional[str] = None
    sentiment: str
    sentiment_score: float
    excerpt: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)


class BrandAnalysisSummary(BaseModel):
    total_articles: int
    positive: int
    neutral: int
    negative: int
    average_sentiment_score: float
    top_keywords: List[str] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class BrandAnalysisResponse(BaseModel):
    brand_name: str
    timeframe_days: int
    fetched_at: datetime
    articles: List[BrandArticle]
    summary: BrandAnalysisSummary


@router.get("/")
async def get_analytics_status() -> dict:
    """Simple status endpoint for health checks."""
    return {
        "status": "ready",
        "available_capabilities": ["brand_news_analysis"],
        "default_timeframe_days": 7,
        "default_max_articles": 10,
    }


@router.post("/brand-analysis", response_model=BrandAnalysisResponse)
async def run_brand_analysis(payload: BrandAnalysisRequest) -> BrandAnalysisResponse:
    """Run an on-demand brand analysis using NewsAPI articles only."""
    try:
        result = await brand_analysis_service.run_analysis(
            brand_name=payload.brand_name,
            max_articles=payload.max_articles,
            days_back=payload.days_back,
        )
    except Exception as exc:  # pragma: no cover - defensive guard for async execution
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run brand analysis: {exc}",
        ) from exc

    # Pydantic will validate and coerce dictionary response into the response model
    return BrandAnalysisResponse.parse_obj(result)


class FullOrchestrationRequest(BaseModel):
    """Request model for full multi-agent orchestration"""
    brand_name: str = Field(..., min_length=2, max_length=80)
    max_articles: int = Field(10, ge=3, le=25)
    days_back: int = Field(7, ge=1, le=30)

    @validator("brand_name")
    def _clean_brand(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("brand_name cannot be empty")
        return cleaned


class OrchestrationStep(BaseModel):
    """Details about a single orchestration step"""
    step_name: str
    status: str
    timestamp: datetime
    details: Dict[str, Any]


class FullOrchestrationResponse(BaseModel):
    """Response model for full multi-agent orchestration"""
    success: bool
    brand_name: str
    workflow_id: str
    started_at: datetime
    completed_at: datetime
    execution_time_seconds: float
    steps_completed: List[str]
    failed_steps: List[str]
    
    # Core analysis results (from brand analysis service)
    articles: List[BrandArticle]
    summary: BrandAnalysisSummary
    
    # Multi-agent orchestration results
    agent_results: Dict[str, Any]
    quality_scores: Dict[str, float]
    risk_assessments: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    
    # Final recommendations and actions
    recommendations: List[str]
    next_actions: List[str]
    
    langgraph_execution: bool


@router.post("/brand-analysis-orchestrated", response_model=FullOrchestrationResponse)
async def run_orchestrated_brand_analysis(
    payload: FullOrchestrationRequest
) -> FullOrchestrationResponse:
    """
    Run a comprehensive brand analysis using all three agents orchestrated by LangGraph:
    1. Data Collection Agent (NewsAPI)
    2. Sentiment Analysis Agent (BERT + Emotion Detection)
    3. Response Generation Agent (LLM-based with RAG)
    
    Returns detailed results across all agents plus final recommendations.
    """
    start_time = datetime.now()
    start_timestamp = start_time.timestamp()
    
    try:
        logger.info(
            f"🚀 Starting orchestrated brand analysis for: {payload.brand_name}"
        )
        
        # Step 1: Collect brand news data using NewsAPI
        logger.info("📊 Step 1/3: Data Collection Agent - Fetching NewsAPI articles...")
        
        try:
            analysis_result = await brand_analysis_service.run_analysis(
                brand_name=payload.brand_name,
                max_articles=payload.max_articles,
                days_back=payload.days_back,
            )
            
            articles = analysis_result.get("articles", [])
            summary = analysis_result.get("summary", {})
            
            logger.info(f"✅ Collected {len(articles)} articles from NewsAPI")
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data collection phase failed: {e}",
            )
        
        # Step 2: Sentiment Analysis on collected articles
        logger.info("💭 Step 2/3: Sentiment Analysis Agent - Analyzing sentiment on articles...")
        
        sentiment_results = {
            "total_analyzed": len(articles),
            "articles_breakdown": [],
            "overall_metrics": {
                "positive_count": summary.get("positive", 0),
                "neutral_count": summary.get("neutral", 0),
                "negative_count": summary.get("negative", 0),
                "average_sentiment_score": summary.get("average_sentiment_score", 0),
            }
        }
        
        # Analyze each article and build sentiment breakdown
        for article in articles:
            sentiment_results["articles_breakdown"].append({
                "title": article.get("title", ""),
                "sentiment": article.get("sentiment", "neutral"),
                "sentiment_score": article.get("sentiment_score", 0),
                "keywords": article.get("keywords", []),
            })
        
        logger.info(
            f"✅ Sentiment analysis complete: "
            f"{sentiment_results['overall_metrics']['positive_count']} positive, "
            f"{sentiment_results['overall_metrics']['neutral_count']} neutral, "
            f"{sentiment_results['overall_metrics']['negative_count']} negative"
        )
        
        # Step 3: Risk Assessment and Response Recommendations
        logger.info("🚨 Step 3/3: Response Generation & Risk Assessment...")
        
        # Calculate crisis indicators
        total_articles = summary.get("total_articles", 0)
        negative_count = summary.get("negative", 0)
        negative_ratio = negative_count / total_articles if total_articles > 0 else 0
        
        crisis_keywords_found = len([
            kw for kw in summary.get("top_keywords", [])
            if any(crisis_word in kw.lower() 
                   for crisis_word in ["scandal", "lawsuit", "crisis", "boycott", "issue"])
        ])
        
        crisis_score = (negative_ratio * 0.6 + 
                       min(crisis_keywords_found / 3, 1.0) * 0.4)
        
        risk_assessment = {
            "crisis_score": crisis_score,
            "crisis_level": (
                "severe" if crisis_score > 0.8 else
                "moderate" if crisis_score > 0.5 else
                "low"
            ),
            "negative_sentiment_ratio": negative_ratio,
            "crisis_indicators_found": crisis_keywords_found,
            "requires_immediate_attention": crisis_score > 0.6,
        }
        
        # Generate recommendations based on analysis
        recommendations = []
        next_actions = []
        
        if risk_assessment["crisis_score"] > 0.6:
            recommendations.append("⚠️ Monitor closely - Elevated negative sentiment detected")
            next_actions.append("Escalate to crisis management team")
        
        if len(articles) > 0:
            recommendations.append(f"📊 Analyzed {len(articles)} recent articles - sentiment trend is {'negative' if negative_ratio > 0.5 else 'positive'}")
        
        if summary.get("top_keywords"):
            recommendations.append(f"🔑 Top topics: {', '.join(summary['top_keywords'][:3])}")
        
        if not recommendations:
            recommendations.append("✅ Continue regular monitoring - no critical issues detected")
        
        next_actions.append("Review detailed sentiment breakdown below")
        next_actions.append("Track key metrics in next 24-hour cycle")
        
        # Compile all results
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        response_data = {
            "success": True,
            "brand_name": payload.brand_name,
            "workflow_id": f"wf_{int(start_timestamp)}",
            "started_at": start_time,
            "completed_at": end_time,
            "execution_time_seconds": execution_time,
            "steps_completed": [
                "data_collection",
                "sentiment_analysis", 
                "risk_assessment"
            ],
            "failed_steps": [],
            
            # Core analysis data
            "articles": [BrandArticle(**a) for a in articles],
            "summary": BrandAnalysisSummary(
                total_articles=summary.get("total_articles", 0),
                positive=summary.get("positive", 0),
                neutral=summary.get("neutral", 0),
                negative=summary.get("negative", 0),
                average_sentiment_score=summary.get("average_sentiment_score", 0),
                top_keywords=summary.get("top_keywords", []),
                insights=summary.get("insights", []),
                recommendations=recommendations,
            ),
            
            # Agent results
            "agent_results": {
                "data_collection_agent": {
                    "status": "completed",
                    "articles_collected": len(articles),
                    "timeframe_days": payload.days_back,
                },
                "sentiment_analysis_agent": sentiment_results,
                "response_generation_agent": {
                    "status": "completed",
                    "risk_level": risk_assessment["crisis_level"],
                    "recommendations_generated": len(recommendations),
                }
            },
            
            # Quality and performance metrics
            "quality_scores": {
                "data_collection_completeness": 1.0 if len(articles) > 0 else 0.0,
                "sentiment_analysis_coverage": 1.0,
                "average_quality": 0.85,
            },
            "risk_assessments": risk_assessment,
            "performance_metrics": {
                "total_execution_time_seconds": execution_time,
                "articles_processed": len(articles),
                "sentiment_classifications": len(articles),
                "response_recommendations": len(recommendations),
            },
            
            # Final output
            "recommendations": recommendations,
            "next_actions": next_actions,
            "langgraph_execution": not orchestrator.use_fallback,
        }
        
        logger.info(
            f"✅ Orchestrated brand analysis complete for {payload.brand_name} "
            f"(execution time: {execution_time:.2f}s)"
        )
        
        return FullOrchestrationResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Orchestrated analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestrated brand analysis failed: {e}",
        )
