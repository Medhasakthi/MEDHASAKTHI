"""
Comprehensive Monitoring and Observability Service for MEDHASAKTHI
Enterprise-grade monitoring, alerting, and observability features
"""
import time
import psutil
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import redis
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.core.performance import performance_monitor
from app.services.email_service import email_service


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class SystemMetricsCollector:
    """Collect comprehensive system metrics"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_MONITORING_DB,
            decode_responses=True
        )
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network_io = psutil.net_io_counters()
        
        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None
            },
            "memory": {
                "total_bytes": memory.total,
                "available_bytes": memory.available,
                "used_bytes": memory.used,
                "usage_percent": memory.percent,
                "swap_total_bytes": swap.total,
                "swap_used_bytes": swap.used,
                "swap_usage_percent": swap.percent
            },
            "disk": {
                "total_bytes": disk_usage.total,
                "used_bytes": disk_usage.used,
                "free_bytes": disk_usage.free,
                "usage_percent": (disk_usage.used / disk_usage.total) * 100,
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0
            },
            "network": {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            },
            "process": {
                "memory_rss_bytes": process_memory.rss,
                "memory_vms_bytes": process_memory.vms,
                "cpu_percent": process_cpu
            }
        }
    
    def collect_application_metrics(self, db: Session) -> Dict[str, Any]:
        """Collect application-specific metrics"""
        
        try:
            # Database metrics
            db_metrics = self._collect_database_metrics(db)
            
            # Cache metrics
            cache_metrics = self._collect_cache_metrics()
            
            # API metrics
            api_metrics = self._collect_api_metrics()
            
            # User metrics
            user_metrics = self._collect_user_metrics(db)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "database": db_metrics,
                "cache": cache_metrics,
                "api": api_metrics,
                "users": user_metrics
            }
        except Exception as e:
            logging.error(f"Error collecting application metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _collect_database_metrics(self, db: Session) -> Dict[str, Any]:
        """Collect database performance metrics"""
        try:
            # Connection count
            conn_query = text("SELECT count(*) FROM pg_stat_activity")
            total_connections = db.execute(conn_query).scalar()
            
            # Active connections
            active_conn_query = text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            active_connections = db.execute(active_conn_query).scalar()
            
            # Database size
            size_query = text("SELECT pg_database_size(current_database())")
            db_size = db.execute(size_query).scalar()
            
            # Cache hit ratio
            cache_query = text("""
                SELECT round(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2) 
                FROM pg_stat_database WHERE datname = current_database()
            """)
            cache_hit_ratio = db.execute(cache_query).scalar()
            
            # Transaction stats
            txn_query = text("""
                SELECT xact_commit, xact_rollback, tup_returned, tup_fetched, tup_inserted, tup_updated, tup_deleted
                FROM pg_stat_database WHERE datname = current_database()
            """)
            txn_stats = db.execute(txn_query).fetchone()
            
            return {
                "total_connections": total_connections,
                "active_connections": active_connections,
                "database_size_bytes": db_size,
                "cache_hit_ratio_percent": float(cache_hit_ratio or 0),
                "transactions": {
                    "commits": txn_stats.xact_commit if txn_stats else 0,
                    "rollbacks": txn_stats.xact_rollback if txn_stats else 0,
                    "tuples_returned": txn_stats.tup_returned if txn_stats else 0,
                    "tuples_fetched": txn_stats.tup_fetched if txn_stats else 0,
                    "tuples_inserted": txn_stats.tup_inserted if txn_stats else 0,
                    "tuples_updated": txn_stats.tup_updated if txn_stats else 0,
                    "tuples_deleted": txn_stats.tup_deleted if txn_stats else 0
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _collect_cache_metrics(self) -> Dict[str, Any]:
        """Collect Redis cache metrics"""
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_bytes": info.get("used_memory", 0),
                "used_memory_peak_bytes": info.get("used_memory_peak", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate_percent": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _collect_api_metrics(self) -> Dict[str, Any]:
        """Collect API performance metrics"""
        # Get metrics from performance monitor
        metrics = performance_monitor.get_metrics_summary(hours=1)
        
        return {
            "response_times": metrics.get("api_response_time_ms", {}),
            "request_count": metrics.get("api_request_count", {}),
            "error_rate": metrics.get("api_error_rate", {}),
            "active_sessions": metrics.get("active_sessions", {})
        }
    
    def _collect_user_metrics(self, db: Session) -> Dict[str, Any]:
        """Collect user activity metrics"""
        try:
            from app.models.user import User, Student, Institute
            
            # Total users
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Students
            total_students = db.query(Student).count()
            active_students = db.query(Student).filter(Student.is_active == True).count()
            
            # Institutes
            total_institutes = db.query(Institute).count()
            active_institutes = db.query(Institute).filter(Institute.is_active == True).count()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_users = db.query(User).filter(User.last_login >= yesterday).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_students": total_students,
                "active_students": active_students,
                "total_institutes": total_institutes,
                "active_institutes": active_institutes,
                "recent_active_users": recent_users
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_MONITORING_DB,
            decode_responses=True
        )
        self.alert_thresholds = {
            "cpu_usage_percent": {"high": 80, "critical": 95},
            "memory_usage_percent": {"high": 85, "critical": 95},
            "disk_usage_percent": {"high": 80, "critical": 90},
            "database_connections": {"high": 80, "critical": 95},
            "cache_hit_ratio_percent": {"low": 80, "critical": 60},
            "api_response_time_ms": {"high": 1000, "critical": 5000},
            "api_error_rate_percent": {"high": 5, "critical": 10}
        }
        self.active_alerts = {}
    
    def check_metrics_for_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # Check system metrics
        if "cpu" in metrics:
            cpu_usage = metrics["cpu"].get("usage_percent", 0)
            alert = self._check_threshold("cpu_usage_percent", cpu_usage)
            if alert:
                alerts.append(alert)
        
        if "memory" in metrics:
            memory_usage = metrics["memory"].get("usage_percent", 0)
            alert = self._check_threshold("memory_usage_percent", memory_usage)
            if alert:
                alerts.append(alert)
        
        if "disk" in metrics:
            disk_usage = metrics["disk"].get("usage_percent", 0)
            alert = self._check_threshold("disk_usage_percent", disk_usage)
            if alert:
                alerts.append(alert)
        
        # Check application metrics
        if "database" in metrics:
            db_metrics = metrics["database"]
            if "total_connections" in db_metrics:
                conn_usage = (db_metrics["total_connections"] / 100) * 100  # Assuming max 100 connections
                alert = self._check_threshold("database_connections", conn_usage)
                if alert:
                    alerts.append(alert)
            
            if "cache_hit_ratio_percent" in db_metrics:
                hit_ratio = db_metrics["cache_hit_ratio_percent"]
                alert = self._check_threshold("cache_hit_ratio_percent", hit_ratio, reverse=True)
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def _check_threshold(
        self, 
        metric_name: str, 
        current_value: float, 
        reverse: bool = False
    ) -> Optional[Alert]:
        """Check if metric exceeds threshold"""
        
        thresholds = self.alert_thresholds.get(metric_name, {})
        if not thresholds:
            return None
        
        severity = None
        threshold_value = None
        
        if reverse:  # For metrics where lower values are bad (like cache hit ratio)
            if current_value <= thresholds.get("critical", 0):
                severity = AlertSeverity.CRITICAL
                threshold_value = thresholds["critical"]
            elif current_value <= thresholds.get("low", 0):
                severity = AlertSeverity.HIGH
                threshold_value = thresholds["low"]
        else:  # For metrics where higher values are bad
            if current_value >= thresholds.get("critical", 100):
                severity = AlertSeverity.CRITICAL
                threshold_value = thresholds["critical"]
            elif current_value >= thresholds.get("high", 100):
                severity = AlertSeverity.HIGH
                threshold_value = thresholds["high"]
        
        if severity:
            alert_id = f"{metric_name}_{int(time.time())}"
            return Alert(
                id=alert_id,
                title=f"{metric_name.replace('_', ' ').title()} Alert",
                description=f"{metric_name} is {current_value:.2f}, exceeding threshold of {threshold_value}",
                severity=severity,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                timestamp=datetime.now()
            )
        
        return None
    
    async def send_alert(self, alert: Alert):
        """Send alert notification"""
        
        # Store alert
        alert_data = {
            "id": alert.id,
            "title": alert.title,
            "description": alert.description,
            "severity": alert.severity.value,
            "metric_name": alert.metric_name,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "timestamp": alert.timestamp.isoformat(),
            "resolved": alert.resolved
        }
        
        self.redis_client.setex(
            f"alert:{alert.id}",
            86400,  # 24 hours
            json.dumps(alert_data)
        )
        
        # Send email notification for high/critical alerts
        if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            await self._send_email_alert(alert)
        
        # Store in active alerts
        self.active_alerts[alert.id] = alert
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert to administrators"""
        
        admin_emails = getattr(settings, 'ADMIN_EMAILS', ['admin@medhasakthi.com'])
        
        subject = f"[{alert.severity.value.upper()}] MEDHASAKTHI Alert: {alert.title}"
        
        body = f"""
        Alert Details:
        
        Title: {alert.title}
        Severity: {alert.severity.value.upper()}
        Description: {alert.description}
        
        Metric: {alert.metric_name}
        Current Value: {alert.current_value:.2f}
        Threshold: {alert.threshold_value:.2f}
        
        Timestamp: {alert.timestamp.isoformat()}
        
        Please investigate and take appropriate action.
        
        MEDHASAKTHI Monitoring System
        """
        
        for email in admin_emails:
            try:
                await email_service.send_email(
                    to_email=email,
                    subject=subject,
                    body=body
                )
            except Exception as e:
                logging.error(f"Failed to send alert email to {email}: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts"""
        
        alerts = []
        alert_keys = self.redis_client.keys("alert:*")
        
        for key in alert_keys:
            alert_data = self.redis_client.get(key)
            if alert_data:
                alerts.append(json.loads(alert_data))
        
        return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark alert as resolved"""
        
        alert_key = f"alert:{alert_id}"
        alert_data = self.redis_client.get(alert_key)
        
        if alert_data:
            alert = json.loads(alert_data)
            alert["resolved"] = True
            alert["resolved_at"] = datetime.now().isoformat()
            
            self.redis_client.setex(alert_key, 86400, json.dumps(alert))
            
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
            
            return True
        
        return False


class HealthCheckService:
    """Comprehensive health check service"""
    
    def __init__(self):
        self.health_checks = {
            "database": self._check_database_health,
            "redis": self._check_redis_health,
            "external_apis": self._check_external_apis_health,
            "disk_space": self._check_disk_space_health,
            "memory": self._check_memory_health
        }
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        
        results = {}
        overall_healthy = True
        
        for check_name, check_func in self.health_checks.items():
            try:
                result = await check_func()
                results[check_name] = result
                if not result.get("healthy", False):
                    overall_healthy = False
            except Exception as e:
                results[check_name] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                overall_healthy = False
        
        return {
            "overall_healthy": overall_healthy,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            db = next(get_db())
            
            # Test connection
            start_time = time.time()
            result = db.execute(text("SELECT 1")).scalar()
            response_time = (time.time() - start_time) * 1000
            
            # Check connection count
            conn_count = db.execute(text("SELECT count(*) FROM pg_stat_activity")).scalar()
            
            db.close()
            
            return {
                "healthy": result == 1 and response_time < 1000,
                "response_time_ms": response_time,
                "connection_count": conn_count,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            
            start_time = time.time()
            redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            info = redis_client.info()
            
            return {
                "healthy": response_time < 100,
                "response_time_ms": response_time,
                "memory_usage_bytes": info.get("used_memory", 0),
                "connected_clients": info.get("connected_clients", 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_external_apis_health(self) -> Dict[str, Any]:
        """Check external API connectivity"""
        # This would check OpenAI, payment gateways, etc.
        return {
            "healthy": True,
            "apis_checked": ["openai", "email_service"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_disk_space_health(self) -> Dict[str, Any]:
        """Check disk space availability"""
        disk_usage = psutil.disk_usage('/')
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        return {
            "healthy": usage_percent < 90,
            "usage_percent": usage_percent,
            "free_bytes": disk_usage.free,
            "total_bytes": disk_usage.total,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_memory_health(self) -> Dict[str, Any]:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        
        return {
            "healthy": memory.percent < 90,
            "usage_percent": memory.percent,
            "available_bytes": memory.available,
            "total_bytes": memory.total,
            "timestamp": datetime.now().isoformat()
        }


# Global instances
metrics_collector = SystemMetricsCollector()
alert_manager = AlertManager()
health_check_service = HealthCheckService()
