"""
LangChain-Powered Base Agent - The Foundation of True Agentic AI
This represents the evolution from message-passing to LLM-driven reasoning
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import time
from datetime import datetime

from langchain_core.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import BaseCallbackHandler
from loguru import logger

from app.core.config import settings


class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    RESPONDING = "responding"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentCapability(Enum):
    DATA_COLLECTION = "data_collection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CRISIS_DETECTION = "crisis_detection"
    ALERT_MANAGEMENT = "alert_management"
    STRATEGIC_REASONING = "strategic_reasoning"


@dataclass
class AgentMessage:
    """Enhanced message structure for LLM-powered agents"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: float
    message_type: str
    correlation_id: Optional[str] = None
    requires_reasoning: bool = True
    priority: str = "normal"  # low, normal, high, critical


class AgentMetrics:
    """Enhanced metrics for LLM-powered agents"""
    def __init__(self):
        self.reasoning_cycles = 0
        self.successful_actions = 0
        self.failed_actions = 0
        self.avg_thinking_time = 0.0
        self.llm_tokens_used = 0
        self.tools_called = 0
        self.start_time = time.time()
        self.last_activity = None
        
    def update_thinking_time(self, duration: float):
        """Update average thinking time"""
        self.reasoning_cycles += 1
        self.avg_thinking_time = (
            (self.avg_thinking_time * (self.reasoning_cycles - 1) + duration) 
            / self.reasoning_cycles
        )
        self.last_activity = time.time()
    
    def record_action(self, success: bool, tokens_used: int = 0):
        """Record action result"""
        if success:
            self.successful_actions += 1
        else:
            self.failed_actions += 1
        
        self.llm_tokens_used += tokens_used
        self.last_activity = time.time()
    
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        total = self.successful_actions + self.failed_actions
        return self.successful_actions / total if total > 0 else 0.0


class AgentCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for agent monitoring"""
    
    def __init__(self, agent_id: str, metrics: AgentMetrics):
        self.agent_id = agent_id
        self.metrics = metrics
        self.current_thinking_start = None
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Called when the agent starts thinking"""
        self.current_thinking_start = time.time()
        logger.debug(f"Agent {self.agent_id} started thinking about: {inputs.get('input', '')[:100]}...")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Called when the agent finishes thinking"""
        if self.current_thinking_start:
            thinking_duration = time.time() - self.current_thinking_start
            self.metrics.update_thinking_time(thinking_duration)
            logger.debug(f"Agent {self.agent_id} finished thinking in {thinking_duration:.2f}s")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Called when a tool is invoked"""
        tool_name = serialized.get("name", "unknown")
        self.metrics.tools_called += 1
        logger.debug(f"Agent {self.agent_id} using tool: {tool_name}")
    
    def on_chain_error(self, error: Exception, **kwargs: Any) -> Any:
        """Called when an error occurs"""
        self.metrics.record_action(success=False)
        logger.error(f"Agent {self.agent_id} encountered error: {error}")


class LangChainBaseAgent(ABC):
    """
    Revolutionary Base Agent powered by LLM reasoning
    This is the brain transplant - moving from rules to reasoning
    """
    
    def __init__(
        self, 
        agent_id: str, 
        capabilities: List[AgentCapability],
        model_name: str = None,
        temperature: float = None
    ):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.metrics = AgentMetrics()
        
        # LLM Configuration
        self.model_name = model_name or settings.LLM_MODEL_NAME
        self.temperature = temperature or settings.LLM_TEMPERATURE
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Agent components
        self.tools: List[BaseTool] = []
        self.callback_handler = AgentCallbackHandler(self.agent_id, self.metrics)
        
        # Message queue for communication
        self.message_queue = asyncio.Queue(maxsize=1000)
        self.orchestrator = None
        
        # Agent context and memory
        self.context = {
            "agent_id": self.agent_id,
            "capabilities": [cap.value for cap in capabilities],
            "session_start": datetime.utcnow().isoformat(),
            "conversation_history": []
        }
        
        logger.info(f"🧠 LLM-Powered Agent {self.agent_id} initialized with capabilities: {[cap.value for cap in capabilities]}")
    
    def _initialize_llm(self) -> BaseLanguageModel:
        """Initialize the LLM brain"""
        try:
            if not settings.GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY not configured, using mock responses")
                return None
            
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                google_api_key=settings.GEMINI_API_KEY,
                max_output_tokens=settings.LLM_MAX_TOKENS
            )
            
            logger.info(f"✅ LLM initialized: {self.model_name} (temp: {self.temperature})")
            return llm
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None
    
    @abstractmethod
    async def create_tools(self) -> List[BaseTool]:
        """Create the tools this agent can use"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the agent's system prompt that defines its personality and role"""
        pass
    
    async def initialize_agent(self):
        """Initialize the agent tools"""
        try:
            # Create tools
            self.tools = await self.create_tools()
            
            if not self.llm:
                logger.warning(f"Agent {self.agent_id} running in mock mode (no LLM)")
                return
            
            logger.info(f"✅ Agent {self.agent_id} initialized with {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            raise
    
    async def think_and_act(self, input_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        The core reasoning method - this is where the magic happens
        The agent thinks about the problem and decides what actions to take
        """
        start_time = time.time()
        self.status = AgentStatus.THINKING
        
        try:
            if not self.llm:
                return await self._mock_response(input_message, context)
            
            # Add context to the input
            enhanced_input = self._enhance_input_with_context(input_message, context)
            
            # Create the system prompt
            system_prompt = self.get_system_prompt()
            
            # Create the full prompt
            full_prompt = f"{system_prompt}\n\nTask: {enhanced_input}\n\nPlease reason step by step and provide a helpful response."
            
            # Let the LLM think and respond
            logger.info(f"🤔 Agent {self.agent_id} thinking about: {input_message[:100]}...")
            
            self.status = AgentStatus.ACTING
            
            # Direct LLM call
            response = await self.llm.ainvoke(full_prompt)
            
            self.status = AgentStatus.RESPONDING
            
            # Process and structure the response
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            result = {
                "success": True,
                "agent_id": self.agent_id,
                "input": input_message,
                "response": response_text,
                "reasoning_steps": [],  # Simplified for now
                "tools_used": [],  # Simplified for now
                "thinking_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.metrics.record_action(success=True)
            logger.info(f"✅ Agent {self.agent_id} completed task in {result['thinking_time']:.2f}s")
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.metrics.record_action(success=False)
            logger.error(f"❌ Agent {self.agent_id} failed: {e}")
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "input": input_message,
                "error": str(e),
                "thinking_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            self.status = AgentStatus.IDLE
    
    async def _mock_response(self, input_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Mock response when LLM is not available"""
        await asyncio.sleep(0.5)  # Simulate thinking time
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "input": input_message,
            "response": f"Mock response from {self.agent_id}: I would analyze '{input_message}' but LLM is not configured",
            "mock_mode": True,
            "thinking_time": 0.5,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _enhance_input_with_context(self, input_message: str, context: Dict[str, Any] = None) -> str:
        """Enhance input with contextual information"""
        enhanced = f"Input: {input_message}\n\n"
        
        if context:
            enhanced += "Context:\n"
            for key, value in context.items():
                enhanced += f"- {key}: {value}\n"
            enhanced += "\n"
        
        enhanced += f"Agent Capabilities: {[cap.value for cap in self.capabilities]}\n"
        enhanced += f"Available Tools: {[tool.name for tool in self.tools]}\n"
        
        return enhanced
    
    async def start(self):
        """Start the agent's message processing loop"""
        await self.initialize_agent()
        
        logger.info(f"🚀 Starting LLM Agent {self.agent_id}")
        
        while self.status != AgentStatus.SHUTDOWN:
            try:
                # Wait for messages
                message = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                
                await self.handle_message(message)
                
            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue
            except Exception as e:
                logger.error(f"Error in agent {self.agent_id} message loop: {e}")
                await asyncio.sleep(1)
    
    async def handle_message(self, message: AgentMessage):
        """Handle incoming messages with LLM reasoning"""
        try:
            logger.info(f"📨 Agent {self.agent_id} received message from {message.sender}")
            
            # Prepare input for LLM reasoning
            reasoning_input = f"""
I received a message from {message.sender}:

Message Type: {message.message_type}
Content: {message.content}
Priority: {message.priority}

Based on my capabilities {[cap.value for cap in self.capabilities]}, 
how should I respond to this message?
"""
            
            # Use LLM to reason about the response
            response = await self.think_and_act(
                reasoning_input, 
                context={"message": message.__dict__}
            )
            
            # Send response back to orchestrator or sender
            await self.send_response(message, response)
            
        except Exception as e:
            logger.error(f"Error handling message in agent {self.agent_id}: {e}")
    
    async def send_response(self, original_message: AgentMessage, response: Dict[str, Any]):
        """Send response back to the message sender"""
        if self.orchestrator:
            response_message = AgentMessage(
                sender=self.agent_id,
                receiver=original_message.sender,
                content=response,
                timestamp=time.time(),
                message_type="agent_response",
                correlation_id=original_message.correlation_id
            )
            await self.orchestrator.route_message(response_message)
    
    async def receive_message(self, message: AgentMessage):
        """Receive a message and add to queue"""
        await self.message_queue.put(message)
    
    def set_orchestrator(self, orchestrator):
        """Set reference to orchestrator for communication"""
        self.orchestrator = orchestrator
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        uptime = time.time() - self.metrics.start_time
        
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "llm_model": self.model_name,
            "uptime_seconds": uptime,
            "queue_size": self.message_queue.qsize(),
            "metrics": {
                "reasoning_cycles": self.metrics.reasoning_cycles,
                "success_rate": self.metrics.get_success_rate(),
                "avg_thinking_time": self.metrics.avg_thinking_time,
                "tokens_used": self.metrics.llm_tokens_used,
                "tools_called": self.metrics.tools_called,
                "last_activity": self.metrics.last_activity
            },
            "tools_available": len(self.tools),
            "has_llm": self.llm is not None
        }
    
    async def shutdown(self):
        """Gracefully shutdown the agent"""
        self.status = AgentStatus.SHUTDOWN
        logger.info(f"🔄 Agent {self.agent_id} shutting down...")
        
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break


# Backward compatibility - keep old classes for now
class AgentStatus_Old(Enum):
    IDLE = "idle"
    ACTIVE = "active" 
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class Message:
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: float
    message_type: str
    correlation_id: str = None


# Legacy BaseAgent for backward compatibility
class BaseAgent(LangChainBaseAgent):
    """Legacy base agent - now powered by LLM but maintains API compatibility"""
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        # Convert string capabilities to enum
        capability_enums = []
        for cap in capabilities:
            if cap == "data_collection":
                capability_enums.append(AgentCapability.DATA_COLLECTION)
            elif cap == "sentiment_analysis":
                capability_enums.append(AgentCapability.SENTIMENT_ANALYSIS)
            elif cap == "alert_management":
                capability_enums.append(AgentCapability.ALERT_MANAGEMENT)
            else:
                # Default capability
                capability_enums.append(AgentCapability.STRATEGIC_REASONING)
        
        super().__init__(agent_id, capability_enums)
        
        # Legacy properties
        self.capabilities_str = capabilities
        self.context = {}
        
        logger.info(f"Legacy Agent {agent_id} initialized with capabilities: {capabilities}")
    
    async def create_tools(self) -> List[BaseTool]:
        """Default empty tools for legacy agents"""
        return []
    
    def get_system_prompt(self) -> str:
        """Default system prompt for legacy agents"""
        return f"""You are a helpful AI agent with ID '{self.agent_id}'. 
Your capabilities include: {', '.join(self.capabilities_str)}.
You should respond helpfully to any requests within your capabilities."""
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - now uses LLM reasoning"""
        task_description = f"Process this task: {task}"
        response = await self.think_and_act(task_description, {"task": task})
        
        # Convert to legacy format
        if response["success"]:
            return {
                "status": "success",
                "result": response["response"],
                "agent_id": self.agent_id
            }
        else:
            return {
                "status": "error", 
                "error": response.get("error", "Unknown error"),
                "agent_id": self.agent_id
            }
