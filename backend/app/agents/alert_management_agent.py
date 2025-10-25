"""
Alert Management Agent for crisis detection and notifications
"""

import asyncio
from typing import List, Dict, Any
import time
from datetime import datetime, timedelta
from loguru import logger

from .base_agent import BaseAgent, AgentMessage
from app.core.config import settings

# Simple message type enum for legacy code
class MessageType:
    TASK = "task"
    RESULT = "result"
    STATUS = "status"

# Legacy Message class for backwards compatibility
class Message:
    def __init__(self, sender: str, receiver: str, content: Dict[str, Any], timestamp: float, message_type: str, correlation_id: str = None):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp
        self.message_type = message_type
        self.correlation_id = correlation_id


class AlertManagementAgent(BaseAgent):
    """Agent responsible for alert management and crisis detection"""
    
    def __init__(self, agent_id: str = "alert_manager"):
        super().__init__(agent_id, [
            "alert_management",
            "crisis_detection", 
            "notification_management",
            "escalation_handling"
        ])
        
        # Alert configuration
        self.alert_rules = {
            "negative_sentiment_spike": {
                "threshold": settings.NEGATIVE_SENTIMENT_THRESHOLD,
                "volume_threshold": settings.CRISIS_MENTION_THRESHOLD,
                "timeframe": "1h"
            },
            "crisis_keywords": {
                "immediate_alert": True,
                "escalation_required": True
            },
            "volume_spike": {
                "multiplier": settings.VOLUME_SPIKE_MULTIPLIER,
                "timeframe": "30m"
            },
            "sentiment_deterioration": {
                "threshold_change": 0.3,  # 30% increase in negative sentiment
                "timeframe": "2h"
            }
        }
        
        # Alert history for tracking patterns
        self.alert_history = {}
        self.active_alerts = {}
        self.alert_stats = {
            "total_alerts": 0,
            "alerts_by_type": {},
            "alerts_by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }
        
        # Historical data for trend analysis
        self.historical_data = {}
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process alert management task"""
        try:
            analyzed_data = task.get("analyzed_data", [])
            platform = task.get("platform")
            brand_id = task.get("brand_id")
            
            logger.info(f"Processing alerts for {len(analyzed_data)} items from {platform}")
            
            alerts = []
            
            # Check for various alert conditions
            alerts.extend(await self._check_negative_sentiment_spike(analyzed_data, platform, brand_id))
            alerts.extend(await self._check_crisis_keywords(analyzed_data, platform, brand_id))
            alerts.extend(await self._check_volume_spike(analyzed_data, platform, brand_id))
            alerts.extend(await self._check_sentiment_deterioration(analyzed_data, platform, brand_id))
            
            # Process and prioritize alerts
            processed_alerts = await self._process_alerts(alerts, brand_id)
            
            # Update statistics
            self.alert_stats["total_alerts"] += len(processed_alerts)
            for alert in processed_alerts:
                alert_type = alert.get("type", "unknown")
                severity = alert.get("severity", "low")
                self.alert_stats["alerts_by_type"][alert_type] = \
                    self.alert_stats["alerts_by_type"].get(alert_type, 0) + 1
                self.alert_stats["alerts_by_severity"][severity] += 1
            
            self.metrics["tasks_processed"] += 1
            
            return {
                "status": "success",
                "platform": platform,
                "brand_id": brand_id,
                "alerts": processed_alerts,
                "alert_count": len(processed_alerts),
                "total_mentions": len(analyzed_data),
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in alert management task: {e}")
            self.metrics["errors"] += 1
            return {
                "status": "error",
                "message": str(e),
                "platform": task.get("platform", "unknown")
            }
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        try:
            if message.message_type == MessageType.DATA_TRANSFER.value:
                # Process alerts
                result = await self.process_task(message.content)
                
                if result["status"] == "success" and result["alerts"]:
                    # Send notifications for alerts
                    for alert in result["alerts"]:
                        await self._send_alert_notification(alert, message.content.get("brand_id"))
                    
                    # Send to notification service if configured
                    notification_message = Message(
                        sender=self.agent_id,
                        receiver="notification_service",
                        content=result,
                        timestamp=time.time(),
                        message_type=MessageType.ALERT.value,
                        correlation_id=message.correlation_id
                    )
                    await self.send_message(notification_message)
                
        except Exception as e:
            logger.error(f"Error handling message in AlertManagementAgent: {e}")
    
    async def _check_negative_sentiment_spike(self, data: List[Dict], platform: str, brand_id: str) -> List[Dict]:
        """Check for spikes in negative sentiment"""
        alerts = []
        
        negative_mentions = [
            item for item in data 
            if item.get("sentiment", {}).get("overall") == "negative" 
            and item.get("sentiment", {}).get("confidence", 0) > self.alert_rules["negative_sentiment_spike"]["threshold"]
        ]
        
        if len(negative_mentions) >= self.alert_rules["negative_sentiment_spike"]["volume_threshold"]:
            # Calculate severity based on volume and sentiment strength
            avg_confidence = sum(item["sentiment"]["confidence"] for item in negative_mentions) / len(negative_mentions)
            severity = "critical" if avg_confidence > 0.8 else "high"
            
            alerts.append({
                "type": "negative_sentiment_spike",
                "severity": severity,
                "platform": platform,
                "count": len(negative_mentions),
                "average_confidence": round(avg_confidence, 3),
                "details": negative_mentions[:5],  # Top 5 for review
                "description": f"High volume of negative sentiment detected: {len(negative_mentions)} mentions with avg confidence {avg_confidence:.2f}",
                "timestamp": time.time()
            })
        
        return alerts
    
    async def _check_crisis_keywords(self, data: List[Dict], platform: str, brand_id: str) -> List[Dict]:
        """Check for crisis-related keywords"""
        alerts = []
        
        crisis_mentions = [
            item for item in data 
            if item.get("crisis_indicators", {}).get("has_indicators", False)
        ]
        
        if crisis_mentions:
            # Group by risk level
            risk_groups = {}
            for mention in crisis_mentions:
                risk_level = mention.get("crisis_indicators", {}).get("risk_level", "low")
                if risk_level not in risk_groups:
                    risk_groups[risk_level] = []
                risk_groups[risk_level].append(mention)
            
            # Create alerts based on highest risk level
            max_risk = max(risk_groups.keys(), key=lambda x: {"low": 1, "medium": 2, "high": 3, "critical": 4}[x])
            
            alerts.append({
                "type": "crisis_keywords_detected",
                "severity": max_risk,
                "platform": platform,
                "count": len(crisis_mentions),
                "risk_distribution": {risk: len(mentions) for risk, mentions in risk_groups.items()},
                "details": crisis_mentions[:3],  # Top 3 for immediate review
                "keywords_detected": self._extract_detected_keywords(crisis_mentions),
                "description": f"Crisis indicators detected in {len(crisis_mentions)} mentions with {max_risk} risk level",
                "requires_immediate_attention": max_risk in ["high", "critical"],
                "timestamp": time.time()
            })
        
        return alerts
    
    async def _check_volume_spike(self, data: List[Dict], platform: str, brand_id: str) -> List[Dict]:
        """Check for unusual volume spikes"""
        alerts = []
        
        current_volume = len(data)
        
        # Get historical average for this platform and brand
        historical_key = f"{brand_id}_{platform}"
        if historical_key not in self.historical_data:
            self.historical_data[historical_key] = []
        
        # Store current volume
        self.historical_data[historical_key].append({
            "volume": current_volume,
            "timestamp": time.time()
        })
        
        # Keep only recent data (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        self.historical_data[historical_key] = [
            entry for entry in self.historical_data[historical_key] 
            if entry["timestamp"] > cutoff_time
        ]
        
        # Calculate average if we have enough data
        if len(self.historical_data[historical_key]) >= 10:
            avg_volume = sum(entry["volume"] for entry in self.historical_data[historical_key]) / len(self.historical_data[historical_key])
            
            if current_volume > avg_volume * self.alert_rules["volume_spike"]["multiplier"]:
                spike_factor = current_volume / avg_volume
                severity = "critical" if spike_factor > 5 else "high" if spike_factor > 3 else "medium"
                
                alerts.append({
                    "type": "volume_spike",
                    "severity": severity,
                    "platform": platform,
                    "current_volume": current_volume,
                    "average_volume": round(avg_volume, 1),
                    "spike_factor": round(spike_factor, 2),
                    "description": f"Volume spike detected: {current_volume} mentions (vs avg {avg_volume:.1f}, {spike_factor:.1f}x increase)",
                    "timestamp": time.time()
                })
        
        return alerts
    
    async def _check_sentiment_deterioration(self, data: List[Dict], platform: str, brand_id: str) -> List[Dict]:
        """Check for sentiment deterioration over time"""
        alerts = []
        
        if not data:
            return alerts
        
        # Calculate current sentiment distribution
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for item in data:
            sentiment = item.get("sentiment", {}).get("overall", "neutral")
            sentiment_counts[sentiment] += 1
        
        total_items = len(data)
        current_negative_ratio = sentiment_counts["negative"] / total_items if total_items > 0 else 0
        
        # Compare with historical data
        historical_key = f"{brand_id}_{platform}_sentiment"
        if historical_key not in self.historical_data:
            self.historical_data[historical_key] = []
        
        # Store current sentiment data
        self.historical_data[historical_key].append({
            "negative_ratio": current_negative_ratio,
            "timestamp": time.time()
        })
        
        # Keep only recent data (last 24 hours)
        cutoff_time = time.time() - (24 * 60 * 60)
        self.historical_data[historical_key] = [
            entry for entry in self.historical_data[historical_key] 
            if entry["timestamp"] > cutoff_time
        ]
        
        # Check for deterioration if we have enough historical data
        if len(self.historical_data[historical_key]) >= 5:
            avg_negative_ratio = sum(entry["negative_ratio"] for entry in self.historical_data[historical_key][:-1]) / (len(self.historical_data[historical_key]) - 1)
            
            deterioration = current_negative_ratio - avg_negative_ratio
            
            if deterioration > self.alert_rules["sentiment_deterioration"]["threshold_change"]:
                severity = "high" if deterioration > 0.5 else "medium"
                
                alerts.append({
                    "type": "sentiment_deterioration",
                    "severity": severity,
                    "platform": platform,
                    "current_negative_ratio": round(current_negative_ratio, 3),
                    "historical_average": round(avg_negative_ratio, 3),
                    "deterioration": round(deterioration, 3),
                    "description": f"Sentiment deterioration detected: {deterioration:.1%} increase in negative sentiment",
                    "timestamp": time.time()
                })
        
        return alerts
    
    async def _process_alerts(self, alerts: List[Dict], brand_id: str) -> List[Dict]:
        """Process and deduplicate alerts"""
        if not alerts:
            return []
        
        # Add brand_id to all alerts
        for alert in alerts:
            alert["brand_id"] = brand_id
            alert["alert_id"] = f"{brand_id}_{alert['type']}_{int(time.time())}"
        
        # Sort by severity and timestamp
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        alerts.sort(key=lambda x: (-severity_order.get(x.get("severity", "low"), 1), -x.get("timestamp", 0)))
        
        # Store active alerts
        for alert in alerts:
            self.active_alerts[alert["alert_id"]] = alert
        
        return alerts
    
    async def _send_alert_notification(self, alert: Dict[str, Any], brand_id: str):
        """Send alert notification"""
        try:
            # Log the alert
            logger.warning(f"ALERT [{alert['severity'].upper()}] - {alert['type']}: {alert.get('description', '')}")
            
            # Here you would integrate with actual notification services
            # For now, we'll just log and update internal state
            
            if alert["severity"] in ["critical", "high"]:
                logger.critical(f"HIGH PRIORITY ALERT for brand {brand_id}: {alert['description']}")
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
    
    def _extract_detected_keywords(self, crisis_mentions: List[Dict]) -> List[str]:
        """Extract all detected crisis keywords from mentions"""
        keywords = set()
        for mention in crisis_mentions:
            crisis_indicators = mention.get("crisis_indicators", {})
            keywords.update(crisis_indicators.get("keywords", []))
        return list(keywords)
    
    def get_active_alerts(self, brand_id: str = None) -> List[Dict]:
        """Get currently active alerts"""
        if brand_id:
            return [alert for alert in self.active_alerts.values() if alert.get("brand_id") == brand_id]
        return list(self.active_alerts.values())
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id]["acknowledged"] = True
            self.active_alerts[alert_id]["acknowledged_by"] = acknowledged_by
            self.active_alerts[alert_id]["acknowledged_at"] = time.time()
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts.pop(alert_id)
            alert["resolved"] = True
            alert["resolved_by"] = resolved_by
            alert["resolved_at"] = time.time()
            alert["resolution_notes"] = resolution_notes
            
            # Store in alert history
            if alert["brand_id"] not in self.alert_history:
                self.alert_history[alert["brand_id"]] = []
            self.alert_history[alert["brand_id"]].append(alert)
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
            return True
        return False
