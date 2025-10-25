"""
Autonomous Multi-Agent AI Brand Reputation Management System
Revolutionary autonomous system with Master Control Loop
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import engine, create_tables
from app.agents.orchestrator_llm import LangChainOrchestrator
from app.agents.data_collection_agent_llm import SmartDataCollectionAgent
# Heavy ML agent imports disabled for fast startup - can be imported when needed
# from app.agents.sentiment_analysis_agent_llm import LangChainSentimentAnalysisAgent
# from app.agents.response_generation_agent import ResponseGenerationAgent
from app.agents.alert_management_agent import AlertManagementAgent
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = None
master_control_task = None

class MasterControlLoop:
    """
    The Autonomous Brain - Proactive System Controller
    This is the missing piece that transforms reactive tools into an autonomous AI system
    """
    
    def __init__(self, orchestrator: LangChainOrchestrator, check_interval: int = 300):
        self.orchestrator = orchestrator
        self.check_interval = check_interval  # 5 minutes default
        self.is_running = False
        self.loop_count = 0
        
    async def start(self):
        """Start the master control loop - the system's heartbeat"""
        self.is_running = True
        logger.info("🚀 MASTER CONTROL LOOP STARTING - System is now autonomous!")
        
        while self.is_running:
            try:
                self.loop_count += 1
                logger.info(f"🔄 Master Control Loop #{self.loop_count} - {datetime.now()}")
                
                # The autonomous goal - this is where the magic happens
                autonomous_goal = f"""
Conduct autonomous brand reputation management cycle #{self.loop_count}:

PRIMARY MISSION: Proactively monitor, analyze, and respond to brand reputation developments across all platforms.

AUTONOMOUS DECISION FRAMEWORK:
1. Check all active brands for new mentions and developments
2. Analyze sentiment, engagement, and crisis indicators using SOTA NLP
3. Identify mentions requiring responses (direct questions, complaints, opportunities)
4. Generate appropriate responses with risk-based approval workflow
5. Escalate high-risk situations to human oversight
6. Log all activities and maintain system health

DECISION AUTHORITY: You are empowered to make autonomous decisions about:
- Data collection priorities and frequency
- Sentiment analysis depth and urgency
- Response generation and auto-approval for low-risk situations
- Alert escalation for high-risk scenarios
- System optimization recommendations

AVAILABLE AGENTS:
- SmartDataCollectionAgent: For intelligent data collection and monitoring
- SentimentAnalysisAgent: For advanced sentiment and emotion analysis
- IntelligentResponseAgent: For generating and managing responses
- AlertManagementAgent: For crisis detection and escalation

CURRENT TIMESTAMP: {datetime.now().isoformat()}
LOOP COUNT: {self.loop_count}
AUTONOMOUS MODE: ACTIVE

Execute this autonomous mission using your available agents and report comprehensive results.
"""
                
                # Execute the autonomous mission
                result = await self.orchestrator.execute_strategic_goal(autonomous_goal)
                
                if result.get("success"):
                    logger.info(f"✅ Autonomous cycle #{self.loop_count} completed successfully")
                    logger.info(f"   Actions taken: {len(result.get('executed_plan', []))}")
                    logger.info(f"   Agents involved: {result.get('agents_used', [])}")
                else:
                    logger.warning(f"⚠️ Autonomous cycle #{self.loop_count} had issues: {result.get('error', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"❌ Master Control Loop error: {e}")
                # Continue running despite errors - resilience is key
            
            # Wait for next cycle
            logger.info(f"💤 Sleeping for {self.check_interval} seconds until next autonomous cycle...")
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the master control loop"""
        self.is_running = False
        logger.info("🛑 Master Control Loop stopping...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - starts and stops the autonomous system"""
    global orchestrator, master_control_task
    
    # Startup
    logger.info("🚀 Starting Autonomous Multi-Agent AI Brand Reputation Management System...")
    
    try:
        # Initialize database
        await create_tables()
        logger.info("✅ Database initialized")
        
        # Initialize the LLM Orchestrator
        orchestrator = LangChainOrchestrator("autonomous_orchestrator")
        await orchestrator.initialize_agent()
        
        # Create and register specialized agents
        data_agent = SmartDataCollectionAgent("smart_data_collector")
        await data_agent.initialize_agent()
        await orchestrator.register_agent(data_agent)
        
        # Heavy ML agents temporarily disabled for fast startup
        # They can be lazy-loaded when needed
        # sentiment_agent = LangChainSentimentAnalysisAgent("sentiment_analyzer_llm")
        # await sentiment_agent.initialize_agent()
        # await orchestrator.register_agent(sentiment_agent)
        
        # response_agent = ResponseGenerationAgent("response_generator")
        # await response_agent.initialize_agent()
        # await orchestrator.register_agent(response_agent)
        
        alert_agent = AlertManagementAgent("alert_manager")
        await alert_agent.initialize_agent()
        await orchestrator.register_agent(alert_agent)
        
        logger.info("🧠 LLM Orchestrator initialized (ML-heavy agents available on-demand for fast startup)")
        
        # Create and start the Master Control Loop if enabled
        if settings.AUTONOMOUS_ENABLED:
            master_control_loop = MasterControlLoop(
                orchestrator=orchestrator,
                check_interval=settings.AUTONOMOUS_CHECK_INTERVAL
            )
            
            # Start the autonomous loop as a background task
            master_control_task = asyncio.create_task(master_control_loop.start())
            logger.info("🔄 Master Control Loop started - System is now AUTONOMOUS!")
        else:
            logger.info("⏸️ Autonomous mode disabled - System will operate in manual mode")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start autonomous system: {e}")
        yield
    
    finally:
        # Shutdown
        logger.info("� Shutting down autonomous system...")
        if master_control_task and not master_control_task.done():
            master_control_task.cancel()
            try:
                await master_control_task
            except asyncio.CancelledError:
                logger.info("✅ Master Control Loop stopped")
        
        if orchestrator:
            await orchestrator.shutdown()
            logger.info("✅ Orchestrator shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Autonomous Multi-Agent AI Brand Reputation Management System",
    description="""
    Revolutionary autonomous AI system for proactive brand reputation monitoring and management.
    
    ## Revolutionary Features
    - **🤖 Autonomous Operation** - Master Control Loop runs 24/7 without human intervention
    - **🧠 LLM-Powered Intelligence** - Google Gemini Pro reasoning across all agents
    - **📚 RAG Knowledge System** - Fact-based responses with ChromaDB vector search
    - **🔍 SOTA NLP Analysis** - Advanced sentiment, emotion, and crisis detection
    - **⚡ Real-time Multi-Platform Monitoring** - Twitter, Reddit, Instagram, Facebook, News
    - **🎯 Intelligent Response Generation** - Quality-assessed, brand-aligned responses
    - **🛡️ Smart Human-in-the-Loop** - Risk-based approval workflow
    - **📊 Comprehensive Analytics** - Performance monitoring and insights
    
    ## Autonomous Intelligence
    The system proactively monitors brand reputation, analyzes developments, and takes appropriate 
    actions without waiting for human commands. The Master Control Loop ensures continuous vigilance.
    """,
    version="2.0.0 - Autonomous Edition",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with autonomous system status"""
    autonomous_status = "active" if master_control_task and not master_control_task.done() else "inactive"
    
    return {
        "message": "Autonomous Multi-Agent AI Brand Reputation Management System",
        "version": "2.0.0 - Autonomous Edition",
        "status": "active",
        "autonomous_mode": settings.AUTONOMOUS_ENABLED,
        "autonomous_status": autonomous_status,
        "master_control_loop": {
            "running": autonomous_status == "active",
            "check_interval": settings.AUTONOMOUS_CHECK_INTERVAL,
            "next_check": f"Every {settings.AUTONOMOUS_CHECK_INTERVAL} seconds"
        },
        "agents_status": orchestrator.get_system_status() if orchestrator else "not_initialized"
    }


@app.get("/health")
async def health_check():
    """Enhanced health check with autonomous system monitoring"""
    try:
        # Check agent system status
        agent_status = orchestrator.get_system_status() if orchestrator else "not_available"
        
        # Check autonomous system status
        autonomous_health = {
            "enabled": settings.AUTONOMOUS_ENABLED,
            "master_control_loop_running": master_control_task and not master_control_task.done(),
            "check_interval": settings.AUTONOMOUS_CHECK_INTERVAL
        }
        
        return {
            "status": "healthy",
            "database": "connected",
            "agents": agent_status,
            "autonomous_system": autonomous_health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/autonomous/status")
async def autonomous_system_status():
    """Get detailed autonomous system status"""
    if not settings.AUTONOMOUS_ENABLED:
        return {"autonomous_mode": "disabled", "message": "Autonomous mode is disabled in configuration"}
    
    loop_running = master_control_task and not master_control_task.done()
    
    return {
        "autonomous_mode": "enabled",
        "master_control_loop": {
            "running": loop_running,
            "task_status": "active" if loop_running else "stopped",
            "check_interval_seconds": settings.AUTONOMOUS_CHECK_INTERVAL,
            "check_interval_minutes": settings.AUTONOMOUS_CHECK_INTERVAL / 60
        },
        "orchestrator": {
            "initialized": orchestrator is not None,
            "status": orchestrator.get_system_status() if orchestrator else "not_available"
        },
        "configuration": {
            "auto_response_threshold": settings.AUTO_RESPONSE_RISK_THRESHOLD,
            "human_review_threshold": settings.HUMAN_REVIEW_RISK_THRESHOLD
        }
    }


@app.post("/autonomous/trigger")
async def trigger_autonomous_cycle():
    """Manually trigger an autonomous cycle for testing"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        manual_goal = f"""
Execute a manual autonomous brand reputation management cycle:

MISSION: Comprehensive brand reputation check triggered manually at {datetime.now().isoformat()}

TASKS:
1. Collect recent mentions across all platforms
2. Analyze sentiment and detect any issues
3. Generate responses for mentions requiring attention
4. Report findings and actions taken

This is a manual trigger for testing the autonomous capabilities.
"""
        
        result = await orchestrator.execute_strategic_goal(manual_goal)
        
        return {
            "success": True,
            "message": "Manual autonomous cycle completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute autonomous cycle: {str(e)}")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
