"""
Agent Orchestrator - Central coordination system for Multi-Agent AI
"""

import asyncio
from typing import Dict, List, Any, Optional
import time
from loguru import logger

from .base_agent import BaseAgent, Message, MessageType
from .data_collection_agent import DataCollectionAgent
from .sentiment_analysis_agent import SentimentAnalysisAgent
from .alert_management_agent import AlertManagementAgent


class AgentOrchestrator:
    """Central orchestrator for managing all agents in the system"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_router = asyncio.Queue(maxsize=10000)
        self.running = False
        self.system_metrics = {
            "start_time": None,
            "total_messages_routed": 0,
            "active_agents": 0,
            "system_errors": 0
        }
        self._router_task = None
        self._agent_tasks = []
    
    async def initialize(self):
        """Initialize the orchestrator and all agents"""
        try:
            logger.info("Initializing Agent Orchestrator...")
            
            # Create and register agents
            self.agents["data_collector"] = DataCollectionAgent("data_collector")
            self.agents["sentiment_analyzer"] = SentimentAnalysisAgent("sentiment_analyzer")
            self.agents["alert_manager"] = AlertManagementAgent("alert_manager")
            
            # Set orchestrator reference for all agents
            for agent in self.agents.values():
                agent.set_orchestrator(self)
            
            logger.info(f"Initialized {len(self.agents)} agents: {list(self.agents.keys())}")
            
        except Exception as e:
            logger.error(f"Error initializing orchestrator: {e}")
            raise
    
    async def start_system(self):
        """Start the entire multi-agent system"""
        if self.running:
            logger.warning("System is already running")
            return
        
        try:
            self.running = True
            self.system_metrics["start_time"] = time.time()
            self.system_metrics["active_agents"] = len(self.agents)
            
            logger.info("Starting Multi-Agent System...")
            
            # Start message router
            self._router_task = asyncio.create_task(self._route_messages())
            
            # Start all agents
            for agent_id, agent in self.agents.items():
                task = asyncio.create_task(agent.start())
                self._agent_tasks.append(task)
                logger.info(f"Started agent: {agent_id}")
            
            logger.info("✅ Multi-Agent System started successfully")
            
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            self.system_metrics["system_errors"] += 1
            await self.shutdown()
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down Multi-Agent System...")
        
        self.running = False
        
        # Stop all agents
        for agent_id, agent in self.agents.items():
            try:
                await agent.shutdown()
                logger.info(f"Stopped agent: {agent_id}")
            except Exception as e:
                logger.error(f"Error stopping agent {agent_id}: {e}")
        
        # Cancel agent tasks
        for task in self._agent_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Stop message router
        if self._router_task and not self._router_task.done():
            self._router_task.cancel()
            try:
                await self._router_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Multi-Agent System shutdown complete")
    
    async def _route_messages(self):
        """Message routing loop"""
        logger.info("Message router started")
        
        while self.running:
            try:
                # Get message from queue with timeout
                message = await asyncio.wait_for(
                    self.message_router.get(), timeout=1.0
                )
                
                await self._deliver_message(message)
                self.system_metrics["total_messages_routed"] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in message router: {e}")
                self.system_metrics["system_errors"] += 1
                await asyncio.sleep(0.1)
    
    async def _deliver_message(self, message: Message):
        """Deliver message to target agent"""
        try:
            target_agent = self.agents.get(message.receiver)
            
            if target_agent:
                await target_agent.receive_message(message)
                logger.debug(f"Message delivered: {message.sender} -> {message.receiver}")
            else:
                logger.warning(f"Unknown receiver: {message.receiver}")
                
        except Exception as e:
            logger.error(f"Error delivering message: {e}")
            self.system_metrics["system_errors"] += 1
    
    async def route_message(self, message: Message):
        """Route a message through the system"""
        try:
            await self.message_router.put(message)
        except asyncio.QueueFull:
            logger.error("Message router queue is full, dropping message")
            self.system_metrics["system_errors"] += 1
    
    async def initiate_monitoring_cycle(self, brand_config: Dict[str, Any]) -> str:
        """Initiate a brand monitoring cycle"""
        try:
            correlation_id = f"monitoring_{brand_config.get('brand_id', 'unknown')}_{int(time.time())}"
            
            logger.info(f"Initiating monitoring cycle for brand {brand_config.get('brand_id')} - {correlation_id}")
            
            # Send collection tasks to data collection agent
            for platform in brand_config.get("platforms", []):
                collection_task = Message(
                    sender="orchestrator",
                    receiver="data_collector",
                    content={
                        "platform": platform,
                        "keywords": brand_config.get("keywords", []),
                        "timeframe": brand_config.get("timeframe", "1h"),
                        "brand_id": brand_config.get("brand_id")
                    },
                    timestamp=time.time(),
                    message_type=MessageType.TASK_REQUEST.value,
                    correlation_id=correlation_id
                )
                
                await self.route_message(collection_task)
            
            return correlation_id
            
        except Exception as e:
            logger.error(f"Error initiating monitoring cycle: {e}")
            self.system_metrics["system_errors"] += 1
            raise
    
    async def start_continuous_monitoring(self, brand_config: Dict[str, Any]) -> bool:
        """Start continuous monitoring for a brand"""
        try:
            brand_id = brand_config.get("brand_id")
            if not brand_id:
                raise ValueError("Brand ID is required for continuous monitoring")
            
            logger.info(f"Starting continuous monitoring for brand: {brand_id}")
            
            # Send monitoring start message to data collector
            start_message = Message(
                sender="orchestrator",
                receiver="data_collector",
                content=brand_config,
                timestamp=time.time(),
                message_type="start_monitoring"
            )
            
            await self.route_message(start_message)
            return True
            
        except Exception as e:
            logger.error(f"Error starting continuous monitoring: {e}")
            return False
    
    async def stop_continuous_monitoring(self, brand_id: str) -> bool:
        """Stop continuous monitoring for a brand"""
        try:
            logger.info(f"Stopping continuous monitoring for brand: {brand_id}")
            
            stop_message = Message(
                sender="orchestrator",
                receiver="data_collector",
                content={"brand_id": brand_id},
                timestamp=time.time(),
                message_type="stop_monitoring"
            )
            
            await self.route_message(stop_message)
            return True
            
        except Exception as e:
            logger.error(f"Error stopping continuous monitoring: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self.running:
            return {"status": "stopped"}
        
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = agent.get_status()
        
        uptime = time.time() - self.system_metrics["start_time"] if self.system_metrics["start_time"] else 0
        
        return {
            "status": "running",
            "uptime_seconds": uptime,
            "system_metrics": self.system_metrics,
            "agents": agent_statuses,
            "message_queue_size": self.message_router.qsize(),
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status.value == "active"])
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        agent = self.agents.get(agent_id)
        return agent.get_status() if agent else None
    
    async def get_active_alerts(self, brand_id: str = None) -> List[Dict]:
        """Get active alerts from alert manager"""
        alert_agent = self.agents.get("alert_manager")
        if isinstance(alert_agent, AlertManagementAgent):
            return alert_agent.get_active_alerts(brand_id)
        return []
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        alert_agent = self.agents.get("alert_manager")
        if isinstance(alert_agent, AlertManagementAgent):
            return alert_agent.acknowledge_alert(alert_id, acknowledged_by)
        return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        alert_agent = self.agents.get("alert_manager")
        if isinstance(alert_agent, AlertManagementAgent):
            return alert_agent.resolve_alert(alert_id, resolved_by, resolution_notes)
        return False
    
    async def send_system_message(self, receiver: str, content: Dict[str, Any], message_type: str = "system_message") -> bool:
        """Send a system message to an agent"""
        try:
            message = Message(
                sender="orchestrator",
                receiver=receiver,
                content=content,
                timestamp=time.time(),
                message_type=message_type
            )
            
            await self.route_message(message)
            return True
            
        except Exception as e:
            logger.error(f"Error sending system message: {e}")
            return False
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all agents"""
        metrics = {
            "total_tasks_processed": 0,
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "total_errors": 0,
            "agent_metrics": {}
        }
        
        for agent_id, agent in self.agents.items():
            agent_metrics = agent.metrics
            metrics["agent_metrics"][agent_id] = agent_metrics
            metrics["total_tasks_processed"] += agent_metrics.get("tasks_processed", 0)
            metrics["total_messages_sent"] += agent_metrics.get("messages_sent", 0)
            metrics["total_messages_received"] += agent_metrics.get("messages_received", 0)
            metrics["total_errors"] += agent_metrics.get("errors", 0)
        
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "system_running": self.running,
            "timestamp": time.time(),
            "overall_health": "healthy"
        }
        
        # Check each agent's health
        agent_health = {}
        unhealthy_agents = 0
        
        for agent_id, agent in self.agents.items():
            agent_status = agent.get_status()
            is_healthy = (
                agent_status["status"] in ["active", "idle"] and
                agent_status["queue_size"] < 1000 and  # Queue not too full
                agent_status["metrics"]["errors"] < 100  # Not too many errors
            )
            
            agent_health[agent_id] = {
                "healthy": is_healthy,
                "status": agent_status["status"],
                "queue_size": agent_status["queue_size"],
                "errors": agent_status["metrics"]["errors"]
            }
            
            if not is_healthy:
                unhealthy_agents += 1
        
        health_status["agents"] = agent_health
        
        # Determine overall health
        if not self.running:
            health_status["overall_health"] = "critical"
        elif unhealthy_agents > 0:
            health_status["overall_health"] = "degraded"
        elif self.system_metrics["system_errors"] > 50:
            health_status["overall_health"] = "warning"
        
        return health_status
