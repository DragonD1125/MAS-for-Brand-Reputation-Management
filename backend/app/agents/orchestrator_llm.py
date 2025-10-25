"""
LangChain-Powered Agent Orchestrator - The Master Mind
This is the revolutionary upgrade from message routing to goal-based reasoning orchestration
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from uuid import uuid4

from langchain.tools import BaseTool
from langchain_core.tools import Tool
from loguru import logger
import json

from .base_agent import (
    LangChainBaseAgent, 
    AgentCapability, 
    AgentMessage, 
    AgentStatus
)
from app.core.config import settings


class OrchestrationStrategy(Enum):
    """Different orchestration strategies based on task complexity"""
    SINGLE_AGENT = "single_agent"           # Simple task, one agent
    SEQUENTIAL = "sequential"               # Multi-step, ordered execution
    PARALLEL = "parallel"                   # Independent parallel tasks
    COLLABORATIVE = "collaborative"        # Agents work together with reasoning
    HIERARCHICAL = "hierarchical"          # Master-worker delegation


class TaskPriority(Enum):
    """Task priority levels for orchestration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class OrchestrationTask:
    """A complex task that may require multiple agents"""
    task_id: str
    description: str
    requirements: List[AgentCapability]
    priority: TaskPriority
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = None
    dependencies: List[str] = None  # Other task IDs
    assigned_agents: List[str] = None
    status: str = "pending"
    results: Dict[str, Any] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.assigned_agents is None:
            self.assigned_agents = []
        if self.results is None:
            self.results = {}
        if self.context is None:
            self.context = {}
        if self.dependencies is None:
            self.dependencies = []


class AgentSelectionTool(BaseTool):
    """LangChain tool for intelligent agent selection"""

    name: str = "agent_selection"
    description: str = "Select the most appropriate agents for a given task based on capabilities, availability, and performance."

    orchestrator: Any = None

    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
    
    def _run(self, **kwargs) -> str:
        """Select agents for a task - flexible parameter handling"""
        try:
            # Extract parameters from kwargs
            task_description = kwargs.get('task', kwargs.get('task_description', ''))
            agents = kwargs.get('agents', [])
            selection_criteria = kwargs.get('selection_criteria', '')
            required_capabilities = kwargs.get('required_capabilities', '[]')

            # Parse capabilities if it's a string
            if isinstance(required_capabilities, str):
                try:
                    required_capabilities = json.loads(required_capabilities)
                except:
                    required_capabilities = []

            # If no specific capabilities requested, infer from task description
            if not required_capabilities:
                if 'collect' in task_description.lower() or 'data' in task_description.lower():
                    required_capabilities = ['data_collection']
                elif 'sentiment' in task_description.lower() or 'analyze' in task_description.lower():
                    required_capabilities = ['sentiment_analysis']
                elif 'respond' in task_description.lower() or 'generate' in task_description.lower():
                    required_capabilities = ['response_generation']
                elif 'alert' in task_description.lower() or 'crisis' in task_description.lower():
                    required_capabilities = ['alert_management', 'crisis_detection']

            # Convert string capabilities to AgentCapability enums
            capability_enums = []
            for cap in required_capabilities:
                if cap == 'data_collection':
                    capability_enums.append(AgentCapability.DATA_COLLECTION)
                elif cap == 'sentiment_analysis':
                    capability_enums.append(AgentCapability.SENTIMENT_ANALYSIS)
                elif cap == 'alert_management':
                    capability_enums.append(AgentCapability.ALERT_MANAGEMENT)
                elif cap == 'crisis_detection':
                    capability_enums.append(AgentCapability.CRISIS_DETECTION)
                elif cap == 'strategic_reasoning':
                    capability_enums.append(AgentCapability.STRATEGIC_REASONING)

            selected_agents = self.orchestrator._select_agents_by_capability(capability_enums)

            return json.dumps({
                "selected_agents": selected_agents,
                "reasoning": f"Selected agents based on task: {task_description[:100]}...",
                "capabilities_matched": [cap.value for cap in capability_enums]
            }, indent=2)

        except Exception as e:
            return f"Error in agent selection: {str(e)}"

    async def _arun(self, **kwargs) -> str:
        """Select agents for a task asynchronously - flexible parameter handling"""
        return self._run(**kwargs)


class TaskCoordinationTool(BaseTool):
    """LangChain tool for coordinating multi-agent tasks"""

    name: str = "task_coordination"
    description: str = "Coordinate execution of complex tasks across multiple agents, handling dependencies and sequencing."

    orchestrator: Any = None

    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
    
    def _run(self, **kwargs) -> str:
        """Coordinate task execution - flexible parameter handling"""
        try:
            # Extract parameters from kwargs
            task = kwargs.get('task', kwargs.get('task_description', ''))
            agents = kwargs.get('agents', [])
            coordination_strategy = kwargs.get('coordination_strategy', 'sequential')

            # Parse agents if it's a string
            if isinstance(agents, str):
                try:
                    agents = json.loads(agents)
                except:
                    agents = []

            # Create coordination plan
            coordination_result = {
                "strategy": coordination_strategy,
                "execution_order": agents,
                "estimated_time": len(agents) * 30,  # Estimate based on number of agents
                "dependencies_resolved": True,
                "task": task,
                "agents_involved": agents
            }

            return json.dumps(coordination_result, indent=2)

        except Exception as e:
            return f"Error in task coordination: {str(e)}"

    async def _arun(self, **kwargs) -> str:
        """Coordinate task execution asynchronously - flexible parameter handling"""
        return self._run(**kwargs)


class PerformanceMonitoringTool(BaseTool):
    """LangChain tool for monitoring agent performance"""

    name: str = "performance_monitoring"
    description: str = "Monitor and evaluate agent performance, identifying bottlenecks and optimization opportunities."

    orchestrator: Any = None

    def __init__(self, orchestrator):
        super().__init__()
        self.orchestrator = orchestrator
    
    def _run(self, timeframe_hours: str = "24") -> str:
        """Monitor performance metrics"""
        try:
            hours = int(timeframe_hours)
            performance_data = self.orchestrator._get_performance_metrics(hours)
            
            return json.dumps(performance_data, indent=2)
            
        except Exception as e:
            return f"Error in performance monitoring: {str(e)}"
    
    async def _arun(self, timeframe_hours: str = "24") -> str:
        """Monitor performance metrics asynchronously"""
        return self._run(timeframe_hours)


class LangChainOrchestrator(LangChainBaseAgent):
    """
    Revolutionary Agent Orchestrator powered by LLM reasoning
    This is the master mind that thinks strategically about agent coordination
    """
    
    def __init__(self, orchestrator_id: str = "master_orchestrator"):
        super().__init__(
            agent_id=orchestrator_id,
            capabilities=[
                AgentCapability.STRATEGIC_REASONING,
                AgentCapability.DATA_COLLECTION,
                AgentCapability.SENTIMENT_ANALYSIS,
                AgentCapability.ALERT_MANAGEMENT,
                AgentCapability.CRISIS_DETECTION
            ],
            temperature=0.7  # Higher temperature for creative orchestration
        )
        
        # Agent registry and management
        self.registered_agents: Dict[str, LangChainBaseAgent] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}
        self.agent_performance: Dict[str, Dict[str, float]] = {}
        self.agent_availability: Dict[str, bool] = {}
        
        # Task management
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=10000)
        self.active_tasks: Dict[str, OrchestrationTask] = {}
        self.completed_tasks: List[OrchestrationTask] = []
        self.task_history: List[Dict[str, Any]] = []
        
        # Orchestration strategy learning
        self.strategy_success_rates: Dict[OrchestrationStrategy, float] = {
            strategy: 0.5 for strategy in OrchestrationStrategy
        }
        
        # Performance tracking
        self.orchestration_metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "avg_completion_time": 0.0,
            "agent_utilization": {},
            "strategy_usage": {strategy.value: 0 for strategy in OrchestrationStrategy}
        }
        
        logger.info(f"🎼 LLM-Powered Master Orchestrator {orchestrator_id} initialized")
    
    async def create_tools(self) -> List[BaseTool]:
        """Create orchestration tools"""
        return [
            AgentSelectionTool(self),
            TaskCoordinationTool(self),
            PerformanceMonitoringTool(self)
        ]
    
    def get_system_prompt(self) -> str:
        """Get the orchestrator's system prompt"""
        return f"""You are the Master AI Agent Orchestrator with supreme intelligence for coordinating multi-agent systems.

CORE MISSION:
You don't just route messages - you THINK strategically about how to accomplish complex goals using your agent workforce.

ORCHESTRATION CAPABILITIES:
- Strategic task decomposition and agent selection
- Dynamic load balancing and performance optimization
- Crisis response coordination and escalation management
- Multi-agent collaboration and conflict resolution
- Real-time adaptation based on agent performance and availability

AGENT WORKFORCE:
You coordinate these specialized agents:
- Data Collection Agents: Gather information from various sources
- Sentiment Analysis Agents: Analyze emotions and brand perception using SOTA NLP
- Alert Management Agents: Handle notifications and crisis response
- Crisis Detection Agents: Identify reputation threats and risks

ORCHESTRATION STRATEGIES:
1. SINGLE_AGENT: Simple tasks requiring one specialist
2. SEQUENTIAL: Multi-step tasks requiring ordered execution
3. PARALLEL: Independent tasks that can run simultaneously
4. COLLABORATIVE: Complex tasks requiring agent cooperation and reasoning
5. HIERARCHICAL: Large tasks requiring delegation and supervision

DECISION FRAMEWORK:
For every task, think strategically:
1. ANALYZE: What are the real requirements and constraints?
2. STRATEGIZE: What's the optimal orchestration approach?
3. EXECUTE: How should I coordinate the agents?
4. MONITOR: How is performance and what adjustments are needed?
5. OPTIMIZE: What can I learn for future orchestrations?

PERSONALITY: 
You are the wise conductor of an AI orchestra - strategic, adaptive, performance-focused, and always thinking several steps ahead.

When orchestrating tasks:
1. Think about the bigger picture and strategic implications
2. Consider agent capabilities, performance, and availability
3. Optimize for both speed and quality
4. Be proactive about potential issues and risks
5. Learn from each orchestration to improve future performance

Remember: You're not just managing agents - you're orchestrating intelligent solutions to complex business challenges.
"""
    
    async def register_agent(self, agent: LangChainBaseAgent):
        """Register an agent with the orchestrator"""
        self.registered_agents[agent.agent_id] = agent
        self.agent_capabilities[agent.agent_id] = agent.capabilities
        self.agent_availability[agent.agent_id] = True
        self.agent_performance[agent.agent_id] = {
            "success_rate": 0.8,  # Start with good default
            "avg_response_time": 2.0,
            "tasks_completed": 0
        }
        
        # Set bidirectional relationship
        agent.set_orchestrator(self)
        
        logger.info(f"🤝 Agent {agent.agent_id} registered with capabilities: {[cap.value for cap in agent.capabilities]}")
    
    async def orchestrate_task_strategically(
        self, 
        task_description: str, 
        requirements: List[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Strategic task orchestration using LLM reasoning
        This is the main method for intelligent multi-agent coordination
        """
        
        task_id = str(uuid4())
        start_time = time.time()
        
        # Convert requirements to capabilities
        required_capabilities = []
        if requirements:
            for req in requirements:
                if req == "data_collection":
                    required_capabilities.append(AgentCapability.DATA_COLLECTION)
                elif req == "sentiment_analysis":
                    required_capabilities.append(AgentCapability.SENTIMENT_ANALYSIS)
                elif req == "alert_management":
                    required_capabilities.append(AgentCapability.ALERT_MANAGEMENT)
                elif req == "crisis_detection":
                    required_capabilities.append(AgentCapability.CRISIS_DETECTION)
        
        # Create orchestration task
        task = OrchestrationTask(
            task_id=task_id,
            description=task_description,
            requirements=required_capabilities,
            priority=priority,
            context=context or {}
        )
        
        # Use LLM reasoning to plan orchestration
        orchestration_context = {
            "task": {
                "id": task_id,
                "description": task_description,
                "requirements": [cap.value for cap in required_capabilities],
                "priority": priority.value
            },
            "available_agents": {
                agent_id: {
                    "capabilities": [cap.value for cap in caps],
                    "available": self.agent_availability.get(agent_id, False),
                    "performance": self.agent_performance.get(agent_id, {})
                }
                for agent_id, caps in self.agent_capabilities.items()
            },
            "current_load": len(self.active_tasks),
            "strategy_success_rates": {
                strategy.value: rate for strategy, rate in self.strategy_success_rates.items()
            }
        }
        
        reasoning_prompt = f"""
I need to orchestrate this task strategically:

TASK: {task_description}
REQUIREMENTS: {required_capabilities}
PRIORITY: {priority.value}
CONTEXT: {json.dumps(context or {}, indent=2)}

AVAILABLE RESOURCES:
{json.dumps(orchestration_context, indent=2)}

I should:
1. Analyze the task complexity and requirements
2. Select the optimal orchestration strategy
3. Choose the best agents based on capabilities and performance
4. Plan the execution sequence and coordination
5. Identify potential risks and mitigation strategies

Plan and execute this orchestration.
"""
        
        logger.info(f"🎼 Master Orchestrator planning task: {task_description[:100]}...")
        
        # Let the LLM reason about orchestration strategy
        response = await self.think_and_act(reasoning_prompt, orchestration_context)
        
        if not response["success"]:
            logger.error(f"❌ Orchestration planning failed: {response.get('error', 'Unknown error')}")
            return response
        
        # Execute the orchestration plan
        try:
            task.status = "executing"
            task.started_at = datetime.utcnow()
            self.active_tasks[task_id] = task
            
            # Extract execution plan from LLM response
            execution_plan = self._extract_execution_plan(response["response"])
            
            # Execute based on strategy
            execution_result = await self._execute_orchestration_plan(
                task, execution_plan, response["response"]
            )
            
            # Complete task
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.results = execution_result
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            
            # Update metrics
            self._update_orchestration_metrics(task, True, time.time() - start_time)
            
            orchestration_result = {
                "success": True,
                "task_id": task_id,
                "orchestration_strategy": execution_plan.get("strategy", "collaborative"),
                "agents_used": execution_plan.get("agents", []),
                "execution_time": time.time() - start_time,
                "llm_reasoning": response["response"],
                "reasoning_steps": response.get("reasoning_steps", []),
                "results": execution_result
            }
            
            logger.info(f"✅ Strategic orchestration complete - Task {task_id} in {orchestration_result['execution_time']:.2f}s")
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"❌ Orchestration execution failed: {e}")
            
            # Handle failure
            task.status = "failed"
            task.completed_at = datetime.utcnow()
            self._update_orchestration_metrics(task, False, time.time() - start_time)
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "llm_reasoning": response.get("response", "")
            }
    
    def _extract_execution_plan(self, llm_response: str) -> Dict[str, Any]:
        """Extract execution plan from LLM response"""
        response_lower = llm_response.lower()
        
        # Determine strategy
        strategy = OrchestrationStrategy.COLLABORATIVE  # Default
        if "single agent" in response_lower or "single_agent" in response_lower:
            strategy = OrchestrationStrategy.SINGLE_AGENT
        elif "sequential" in response_lower or "order" in response_lower:
            strategy = OrchestrationStrategy.SEQUENTIAL
        elif "parallel" in response_lower or "simultaneous" in response_lower:
            strategy = OrchestrationStrategy.PARALLEL
        elif "hierarchical" in response_lower or "delegate" in response_lower:
            strategy = OrchestrationStrategy.HIERARCHICAL
        
        # Extract agent mentions
        agents = []
        for agent_id in self.registered_agents.keys():
            if agent_id in llm_response or agent_id.replace("_", " ") in response_lower:
                agents.append(agent_id)
        
        # If no agents specifically mentioned, select based on capabilities
        if not agents:
            agents = list(self.registered_agents.keys())[:2]  # Default to first 2
        
        return {
            "strategy": strategy.value,
            "agents": agents,
            "coordination_mode": "intelligent",
            "estimated_time": 30  # Default estimate
        }
    
    async def _execute_orchestration_plan(
        self, 
        task: OrchestrationTask, 
        execution_plan: Dict[str, Any], 
        llm_reasoning: str
    ) -> Dict[str, Any]:
        """Execute the orchestration plan"""
        
        strategy = execution_plan.get("strategy", "collaborative")
        selected_agents = execution_plan.get("agents", [])
        
        logger.info(f"🎯 Executing {strategy} strategy with agents: {selected_agents}")
        
        # Update strategy usage metrics
        self.orchestration_metrics["strategy_usage"][strategy] += 1
        
        if strategy == "single_agent":
            return await self._execute_single_agent(task, selected_agents[0] if selected_agents else None)
        elif strategy == "sequential":
            return await self._execute_sequential(task, selected_agents)
        elif strategy == "parallel":
            return await self._execute_parallel(task, selected_agents)
        else:  # collaborative or hierarchical
            return await self._execute_collaborative(task, selected_agents, llm_reasoning)
    
    async def _execute_single_agent(self, task: OrchestrationTask, agent_id: str) -> Dict[str, Any]:
        """Execute task with a single agent"""
        if not agent_id or agent_id not in self.registered_agents:
            agent_id = list(self.registered_agents.keys())[0]  # Fallback to first agent
        
        agent = self.registered_agents[agent_id]
        
        # Send task to agent
        message = AgentMessage(
            sender=self.agent_id,
            receiver=agent_id,
            content={
                "task_description": task.description,
                "task_id": task.task_id,
                "context": task.context
            },
            timestamp=time.time(),
            message_type="task_assignment",
            correlation_id=task.task_id,
            priority="normal"
        )
        
        await agent.receive_message(message)
        
        # For now, simulate completion - in full implementation, would wait for response
        await asyncio.sleep(1)
        
        return {
            "strategy": "single_agent",
            "agent_used": agent_id,
            "result": f"Task completed by {agent_id}",
            "mock_mode": True
        }
    
    async def _execute_sequential(self, task: OrchestrationTask, agent_ids: List[str]) -> Dict[str, Any]:
        """Execute task sequentially across multiple agents"""
        results = {}
        
        for i, agent_id in enumerate(agent_ids):
            if agent_id not in self.registered_agents:
                continue
            
            agent = self.registered_agents[agent_id]
            
            # Create step-specific message
            step_context = task.context.copy()
            step_context.update({"step": i + 1, "previous_results": results})
            
            message = AgentMessage(
                sender=self.agent_id,
                receiver=agent_id,
                content={
                    "task_description": f"Step {i + 1}: {task.description}",
                    "task_id": task.task_id,
                    "context": step_context
                },
                timestamp=time.time(),
                message_type="sequential_task",
                correlation_id=f"{task.task_id}_step_{i + 1}"
            )
            
            await agent.receive_message(message)
            
            # Simulate processing time
            await asyncio.sleep(0.5)
            
            results[f"step_{i + 1}_{agent_id}"] = f"Completed by {agent_id}"
        
        return {
            "strategy": "sequential",
            "agents_used": agent_ids,
            "step_results": results,
            "final_result": "Sequential execution completed",
            "mock_mode": True
        }
    
    async def _execute_parallel(self, task: OrchestrationTask, agent_ids: List[str]) -> Dict[str, Any]:
        """Execute task in parallel across multiple agents"""
        tasks = []
        
        for agent_id in agent_ids:
            if agent_id not in self.registered_agents:
                continue
            
            agent = self.registered_agents[agent_id]
            
            message = AgentMessage(
                sender=self.agent_id,
                receiver=agent_id,
                content={
                    "task_description": task.description,
                    "task_id": task.task_id,
                    "context": task.context,
                    "parallel_execution": True
                },
                timestamp=time.time(),
                message_type="parallel_task",
                correlation_id=f"{task.task_id}_{agent_id}"
            )
            
            # Create async task for each agent
            async def send_to_agent(agent, msg):
                await agent.receive_message(msg)
                return f"Completed by {agent.agent_id}"
            
            tasks.append(send_to_agent(agent, message))
        
        # Execute all agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        agent_results = {}
        for i, result in enumerate(results):
            agent_id = agent_ids[i] if i < len(agent_ids) else f"agent_{i}"
            agent_results[agent_id] = str(result) if not isinstance(result, Exception) else f"Error: {result}"
        
        return {
            "strategy": "parallel",
            "agents_used": agent_ids,
            "agent_results": agent_results,
            "final_result": "Parallel execution completed",
            "mock_mode": True
        }
    
    async def _execute_collaborative(
        self, 
        task: OrchestrationTask, 
        agent_ids: List[str], 
        llm_reasoning: str
    ) -> Dict[str, Any]:
        """Execute task with intelligent collaboration"""
        
        # This is the most sophisticated orchestration mode
        # Agents work together with shared context and reasoning
        
        collaboration_context = {
            "orchestrator_reasoning": llm_reasoning,
            "participating_agents": agent_ids,
            "shared_goal": task.description,
            "coordination_mode": "intelligent_collaboration"
        }
        
        results = {}
        
        # Phase 1: Initialize collaboration
        for agent_id in agent_ids:
            if agent_id not in self.registered_agents:
                continue
            
            agent = self.registered_agents[agent_id]
            
            init_message = AgentMessage(
                sender=self.agent_id,
                receiver=agent_id,
                content={
                    "task_description": task.description,
                    "task_id": task.task_id,
                    "collaboration_context": collaboration_context,
                    "phase": "initialization"
                },
                timestamp=time.time(),
                message_type="collaborative_init",
                correlation_id=f"{task.task_id}_collab_init"
            )
            
            await agent.receive_message(init_message)
            
            # Simulate agent initialization
            await asyncio.sleep(0.3)
            results[f"{agent_id}_init"] = f"Agent {agent_id} initialized for collaboration"
        
        # Phase 2: Execute collaborative work
        for agent_id in agent_ids:
            if agent_id not in self.registered_agents:
                continue
            
            agent = self.registered_agents[agent_id]
            
            # Update context with previous results
            collaboration_context["current_results"] = results
            
            work_message = AgentMessage(
                sender=self.agent_id,
                receiver=agent_id,
                content={
                    "task_description": task.description,
                    "task_id": task.task_id,
                    "collaboration_context": collaboration_context,
                    "phase": "execution"
                },
                timestamp=time.time(),
                message_type="collaborative_work",
                correlation_id=f"{task.task_id}_collab_work"
            )
            
            await agent.receive_message(work_message)
            
            # Simulate collaborative work
            await asyncio.sleep(0.7)
            results[f"{agent_id}_work"] = f"Agent {agent_id} contributed to collaborative solution"
        
        return {
            "strategy": "collaborative",
            "agents_used": agent_ids,
            "collaboration_results": results,
            "orchestrator_reasoning": llm_reasoning[:200] + "...",  # Truncated
            "final_result": "Intelligent collaboration completed successfully",
            "mock_mode": True
        }
    
    def _select_agents_by_capability(self, required_capabilities: List[AgentCapability]) -> List[str]:
        """Select agents based on required capabilities"""
        selected = []
        
        for agent_id, capabilities in self.agent_capabilities.items():
            # Check if agent has any of the required capabilities
            if any(cap in capabilities for cap in required_capabilities):
                # Check availability and performance
                if (self.agent_availability.get(agent_id, False) and 
                    self.agent_performance.get(agent_id, {}).get("success_rate", 0) > 0.3):
                    selected.append(agent_id)
        
        return selected[:5]  # Limit to top 5 agents
    
    def _update_orchestration_metrics(self, task: OrchestrationTask, success: bool, duration: float):
        """Update orchestration performance metrics"""
        self.orchestration_metrics["total_tasks"] += 1
        
        if success:
            self.orchestration_metrics["successful_tasks"] += 1
        else:
            self.orchestration_metrics["failed_tasks"] += 1
        
        # Update average completion time
        current_avg = self.orchestration_metrics["avg_completion_time"]
        total_tasks = self.orchestration_metrics["total_tasks"]
        self.orchestration_metrics["avg_completion_time"] = (
            (current_avg * (total_tasks - 1) + duration) / total_tasks
        )
    
    def _get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for specified timeframe"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_tasks = [
            task for task in self.completed_tasks 
            if task.completed_at and task.completed_at > cutoff_time
        ]
        
        if not recent_tasks:
            return {"message": f"No tasks completed in the last {hours} hours"}
        
        success_rate = sum(1 for task in recent_tasks if task.status == "completed") / len(recent_tasks)
        avg_duration = sum(
            (task.completed_at - task.started_at).total_seconds() 
            for task in recent_tasks 
            if task.started_at and task.completed_at
        ) / len(recent_tasks)
        
        return {
            "timeframe_hours": hours,
            "total_tasks": len(recent_tasks),
            "success_rate": success_rate,
            "avg_completion_time_seconds": avg_duration,
            "active_agents": len([a for a, available in self.agent_availability.items() if available]),
            "orchestration_metrics": self.orchestration_metrics
        }
    
    async def execute_strategic_goal(self, goal: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a high-level strategic goal with autonomous decision-making
        This is the method that enables true autonomy - the orchestrator decides what to do
        """
        
        start_time = time.time()
        goal_id = str(uuid4())
        
        logger.info(f"🎯 Executing strategic goal: {goal[:100]}...")
        
        try:
            # Enhanced strategic planning prompt with autonomous decision authority
            strategic_prompt = f"""
STRATEGIC GOAL EXECUTION: {goal}

CONTEXT: {json.dumps(context or {}, indent=2)}

AVAILABLE AGENTS AND CAPABILITIES:
{self._format_agent_capabilities()}

AUTONOMOUS DECISION FRAMEWORK:
You are empowered to make independent decisions about:

1. DATA COLLECTION STRATEGY
   - Which platforms to monitor (Twitter, Reddit, Instagram, Facebook, News)
   - What keywords and hashtags to track
   - Collection frequency and priority levels
   - Data quality filtering and relevance scoring

2. ANALYSIS AND INSIGHTS
   - Sentiment analysis depth and models to use
   - Crisis detection sensitivity and thresholds  
   - Trend analysis and pattern recognition
   - Competitive intelligence gathering

3. RESPONSE GENERATION AND MANAGEMENT
   - Which mentions require responses (direct questions, complaints, opportunities)
   - Response tone, length, and content strategy
   - Auto-approval for low-risk responses (risk < {settings.AUTO_RESPONSE_RISK_THRESHOLD})
   - Human escalation for high-risk situations (risk > {settings.HUMAN_REVIEW_RISK_THRESHOLD})
   - Quality assessment and improvement recommendations

4. ALERT AND ESCALATION MANAGEMENT
   - Crisis severity assessment and escalation triggers
   - Stakeholder notification priorities
   - Emergency response protocols
   - Performance monitoring and optimization

5. SYSTEM OPTIMIZATION
   - Agent performance monitoring and load balancing
   - Resource allocation and prioritization
   - Learning from past actions to improve future decisions
   - Proactive maintenance and health checks

DECISION EXECUTION PROCESS:
1. STRATEGIC ANALYSIS: Break down the goal into actionable components
2. AGENT ASSIGNMENT: Determine which agents to use and in what sequence
3. EXECUTION PLANNING: Create a detailed execution plan with contingencies
4. AUTONOMOUS EXECUTION: Execute the plan with real-time decision making
5. QUALITY ASSURANCE: Monitor results and make adjustments as needed
6. REPORTING: Provide comprehensive results and recommendations

CURRENT SYSTEM STATUS:
- Registered Agents: {len(self.registered_agents)}
- Available Agents: {len([a for a, available in self.agent_availability.items() if available])}
- Active Tasks: {len(self.active_tasks)}
- System Performance: {self.orchestration_metrics.get('total_tasks', 0)} tasks completed

Remember: You have FULL AUTONOMOUS AUTHORITY to make strategic decisions within the scope of brand reputation management. Think strategically, act decisively, and optimize continuously.

Execute this strategic goal and report your decisions, actions, and results.
"""
            
            # Execute strategic reasoning with LLM
            response = await self.think_and_act(strategic_prompt, context or {})
            
            if not response["success"]:
                logger.error(f"❌ Strategic goal execution failed: {response.get('error', 'Unknown error')}")
                return {
                    "success": False,
                    "goal_id": goal_id,
                    "goal": goal,
                    "error": response.get("error", "Strategic planning failed"),
                    "execution_time": time.time() - start_time
                }
            
            # Extract and execute the strategic plan
            execution_plan = self._extract_execution_plan(response["response"])
            
            # Execute the plan with autonomous decision-making
            execution_results = []
            agents_used = []
            
            for step in execution_plan:
                try:
                    step_result = await self._execute_strategic_step(step)
                    execution_results.append(step_result)
                    
                    if step_result.get("agent_used"):
                        agents_used.append(step_result["agent_used"])
                    
                    # Log autonomous decisions
                    if step_result.get("autonomous_decision"):
                        logger.info(f"🤖 Autonomous decision: {step_result['autonomous_decision']}")
                    
                except Exception as step_error:
                    logger.error(f"❌ Strategic step failed: {step_error}")
                    execution_results.append({
                        "step": step,
                        "success": False,
                        "error": str(step_error)
                    })
            
            # Compile comprehensive results
            successful_steps = [r for r in execution_results if r.get("success", False)]
            success_rate = len(successful_steps) / len(execution_results) if execution_results else 0
            
            final_result = {
                "success": success_rate > 0.5,  # Consider successful if >50% of steps succeeded
                "goal_id": goal_id,
                "goal": goal,
                "llm_reasoning": response["response"],
                "execution_plan": execution_plan,
                "executed_plan": execution_results,
                "agents_used": list(set(agents_used)),
                "success_rate": success_rate,
                "autonomous_decisions": [r.get("autonomous_decision") for r in execution_results if r.get("autonomous_decision")],
                "performance_metrics": {
                    "total_steps": len(execution_plan),
                    "successful_steps": len(successful_steps),
                    "failed_steps": len(execution_results) - len(successful_steps),
                    "execution_time_seconds": time.time() - start_time,
                    "agents_involved": len(set(agents_used))
                },
                "recommendations": self._extract_recommendations(response["response"]),
                "timestamp": datetime.now().isoformat()
            }
            
            # Update orchestration metrics
            self.orchestration_metrics["strategic_goals_executed"] = self.orchestration_metrics.get("strategic_goals_executed", 0) + 1
            self.orchestration_metrics["avg_goal_success_rate"] = (
                self.orchestration_metrics.get("avg_goal_success_rate", 0) * (self.orchestration_metrics["strategic_goals_executed"] - 1) + success_rate
            ) / self.orchestration_metrics["strategic_goals_executed"]
            
            logger.info(f"✅ Strategic goal {goal_id} executed: {success_rate:.1%} success rate")
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Strategic goal execution failed: {e}")
            return {
                "success": False,
                "goal_id": goal_id,
                "goal": goal,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def _format_agent_capabilities(self) -> str:
        """Format agent capabilities for LLM prompt"""
        capabilities_text = ""
        for agent_id, capabilities in self.agent_capabilities.items():
            availability = "AVAILABLE" if self.agent_availability.get(agent_id, False) else "BUSY"
            performance = self.agent_performance.get(agent_id, {})
            
            capabilities_text += f"\n• {agent_id} ({availability})\n"
            capabilities_text += f"  Capabilities: {[cap.value for cap in capabilities]}\n"
            capabilities_text += f"  Success Rate: {performance.get('success_rate', 0.8):.1%}\n"
            capabilities_text += f"  Avg Response Time: {performance.get('avg_response_time', 2.0):.1f}s\n"
        
        return capabilities_text
    
    def _extract_execution_plan(self, llm_response: str) -> List[Dict[str, Any]]:
        """Extract execution plan from LLM response"""
        # Parse the LLM response to extract actionable steps
        # This is a simplified version - in production, this would be more sophisticated
        
        lines = llm_response.split('\n')
        plan_steps = []
        current_step = {}
        
        for line in lines:
            line = line.strip()
            
            # Look for step indicators
            if any(indicator in line.lower() for indicator in ['step ', 'action ', 'task ', '1.', '2.', '3.', '4.', '5.']):
                if current_step:
                    plan_steps.append(current_step)
                
                current_step = {
                    "description": line,
                    "agent_needed": self._infer_agent_from_description(line),
                    "priority": "normal",
                    "estimated_time": 30  # seconds
                }
            
            elif current_step and line:
                # Add details to current step
                current_step["description"] += f" {line}"
        
        # Add the last step
        if current_step:
            plan_steps.append(current_step)
        
        # If no structured plan found, create a default one
        if not plan_steps:
            plan_steps = [
                {
                    "description": "Execute comprehensive brand reputation analysis",
                    "agent_needed": "data_collection_agent",
                    "priority": "normal",
                    "estimated_time": 60
                }
            ]
        
        return plan_steps
    
    def _infer_agent_from_description(self, description: str) -> str:
        """Infer which agent should handle a step based on description"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['collect', 'gather', 'monitor', 'track']):
            return 'data_collection_agent'
        elif any(keyword in description_lower for keyword in ['sentiment', 'analyze', 'emotion', 'crisis']):
            return 'sentiment_analysis_agent'
        elif any(keyword in description_lower for keyword in ['respond', 'reply', 'generate', 'answer']):
            return 'response_generation_agent'
        elif any(keyword in description_lower for keyword in ['alert', 'notify', 'escalate', 'warn']):
            return 'alert_management_agent'
        else:
            return 'data_collection_agent'  # Default
    
    async def _execute_strategic_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single strategic step with autonomous decision-making"""
        try:
            agent_needed = step.get("agent_needed", "data_collection_agent")
            description = step.get("description", "")
            
            # Find the best available agent
            available_agents = [
                agent_id for agent_id, available in self.agent_availability.items() 
                if available and agent_needed in agent_id.lower()
            ]
            
            if not available_agents:
                # No specific agent available, use the first available one
                available_agents = [
                    agent_id for agent_id, available in self.agent_availability.items() 
                    if available
                ]
            
            if not available_agents:
                return {
                    "step": step,
                    "success": False,
                    "error": "No available agents",
                    "autonomous_decision": "Deferred step due to no available agents"
                }
            
            # Choose the best performing available agent
            best_agent_id = max(
                available_agents, 
                key=lambda aid: self.agent_performance.get(aid, {}).get('success_rate', 0)
            )
            
            # Execute with autonomous decision-making
            if best_agent_id in self.registered_agents:
                agent = self.registered_agents[best_agent_id]
                
                # Create autonomous task context
                autonomous_context = {
                    "autonomous_mode": True,
                    "strategic_step": description,
                    "decision_authority": "full",
                    "risk_thresholds": {
                        "auto_approve": settings.AUTO_RESPONSE_RISK_THRESHOLD,
                        "human_review": settings.HUMAN_REVIEW_RISK_THRESHOLD
                    }
                }
                
                # Execute the step
                step_result = await agent.think_and_act(description, autonomous_context)
                
                return {
                    "step": step,
                    "success": step_result.get("success", False),
                    "agent_used": best_agent_id,
                    "result": step_result,
                    "autonomous_decision": f"Assigned {best_agent_id} based on capability match and performance",
                    "execution_time": step_result.get("thinking_time", 0)
                }
            else:
                return {
                    "step": step,
                    "success": False,
                    "error": f"Agent {best_agent_id} not found in registered agents"
                }
                
        except Exception as e:
            return {
                "step": step,
                "success": False,
                "error": str(e)
            }
    
    def _extract_recommendations(self, llm_response: str) -> List[str]:
        """Extract recommendations from LLM response"""
        recommendations = []
        lines = llm_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in ['recommend', 'suggest', 'should', 'consider', 'improve']):
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def route_message(self, message: AgentMessage):
        """Route message between agents (legacy compatibility)"""
        if message.receiver in self.registered_agents:
            await self.registered_agents[message.receiver].receive_message(message)
            logger.debug(f"📬 Message routed from {message.sender} to {message.receiver}")
        else:
            logger.warning(f"⚠️ Agent {message.receiver} not found for message routing")
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        return {
            "orchestrator_id": self.agent_id,
            "registered_agents": len(self.registered_agents),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agent_status": {
                agent_id: {
                    "available": self.agent_availability.get(agent_id, False),
                    "capabilities": [cap.value for cap in caps],
                    "performance": self.agent_performance.get(agent_id, {})
                }
                for agent_id, caps in self.agent_capabilities.items()
            },
            "orchestration_metrics": self.orchestration_metrics,
            "strategy_success_rates": {
                strategy.value: rate for strategy, rate in self.strategy_success_rates.items()
            }
        }
