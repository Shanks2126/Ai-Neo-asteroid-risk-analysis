"""
Alert system for high-risk asteroid predictions.
Sends notifications via webhook when threats are detected.
"""

import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.utils.config import settings
from src.utils.logging import logger


@dataclass
class Alert:
    """Alert data structure."""
    timestamp: datetime
    risk_level: str
    impact_probability: float
    asteroid_name: Optional[str]
    distance_km: float
    diameter_m: float
    message: str


class AlertManager:
    """
    Manages alert notifications for high-risk predictions.
    
    Supports:
    - Webhook notifications (Slack, Discord, custom)
    - Email notifications (future)
    - Rate limiting to prevent spam
    """
    
    def __init__(
        self,
        webhook_url: Optional[str] = None,
        min_risk_level: str = "High",
        cooldown_seconds: int = 300  # 5 minutes between alerts
    ):
        """
        Initialize alert manager.
        
        Args:
            webhook_url: URL for webhook notifications
            min_risk_level: Minimum risk level to trigger alerts
            cooldown_seconds: Minimum time between alerts
        """
        self.webhook_url = webhook_url or settings.alert_webhook_url
        self.min_risk_level = min_risk_level
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time: Optional[datetime] = None
        
        # Risk level ordering
        self.risk_order = {"Low": 0, "Medium": 1, "High": 2}
    
    def should_alert(self, risk_level: str) -> bool:
        """
        Check if an alert should be sent based on risk level and cooldown.
        
        Args:
            risk_level: Prediction risk level
            
        Returns:
            True if alert should be sent
        """
        # Check risk level threshold
        if self.risk_order.get(risk_level, 0) < self.risk_order.get(self.min_risk_level, 2):
            return False
        
        # Check cooldown
        if self.last_alert_time:
            elapsed = (datetime.utcnow() - self.last_alert_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                logger.debug(f"Alert cooldown active, {self.cooldown_seconds - elapsed:.0f}s remaining")
                return False
        
        return True
    
    def create_alert(
        self,
        risk_level: str,
        impact_probability: float,
        distance_km: float,
        diameter_m: float,
        asteroid_name: Optional[str] = None
    ) -> Alert:
        """Create an alert object."""
        # Generate alert message
        threat_emoji = "🔴" if risk_level == "High" else "🟡"
        
        message = f"""
{threat_emoji} **NEO RISK ALERT** {threat_emoji}

**Risk Level**: {risk_level}
**Impact Probability**: {impact_probability:.1%}
**Asteroid**: {asteroid_name or 'Unknown'}
**Distance**: {distance_km:,.0f} km
**Diameter**: {diameter_m:,.0f} m

Timestamp: {datetime.utcnow().isoformat()}
        """.strip()
        
        return Alert(
            timestamp=datetime.utcnow(),
            risk_level=risk_level,
            impact_probability=impact_probability,
            asteroid_name=asteroid_name,
            distance_km=distance_km,
            diameter_m=diameter_m,
            message=message
        )
    
    async def send_webhook_async(self, alert: Alert) -> bool:
        """
        Send alert via webhook asynchronously.
        
        Args:
            alert: Alert to send
            
        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            logger.warning("No webhook URL configured, skipping alert")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                # Generic webhook payload (works with Slack, Discord, etc.)
                payload = {
                    "content": alert.message,  # Discord
                    "text": alert.message,  # Slack
                }
                
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
                self.last_alert_time = datetime.utcnow()
                logger.info(f"Alert sent successfully: {alert.risk_level} risk for {alert.asteroid_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def send_webhook_sync(self, alert: Alert) -> bool:
        """
        Send alert via webhook synchronously.
        
        Args:
            alert: Alert to send
            
        Returns:
            True if sent successfully
        """
        if not self.webhook_url:
            logger.warning("No webhook URL configured, skipping alert")
            return False
        
        try:
            with httpx.Client() as client:
                payload = {
                    "content": alert.message,
                    "text": alert.message,
                }
                
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
                self.last_alert_time = datetime.utcnow()
                logger.info(f"Alert sent: {alert.risk_level} risk")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def check_and_alert(
        self,
        risk_level: str,
        impact_probability: float,
        distance_km: float,
        diameter_m: float,
        asteroid_name: Optional[str] = None
    ) -> Optional[Alert]:
        """
        Check if alert should be sent and send it.
        
        Returns:
            Alert object if sent, None otherwise
        """
        if not self.should_alert(risk_level):
            return None
        
        alert = self.create_alert(
            risk_level=risk_level,
            impact_probability=impact_probability,
            distance_km=distance_km,
            diameter_m=diameter_m,
            asteroid_name=asteroid_name
        )
        
        if self.send_webhook_sync(alert):
            return alert
        
        return None


# Singleton instance
alert_manager = AlertManager()
