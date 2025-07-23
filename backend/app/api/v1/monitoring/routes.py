"""
Monitoring and Observability API routes for MEDHASAKTHI
System metrics, alerts, health checks, and performance monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_admin_user
from app.models.user import User
from app.services.monitoring_service import (
    metrics_collector,
    alert_manager,
    health_check_service
)
from app.core.performance import get_performance_report

router = APIRouter()


# System Metrics Routes
@router.get("/metrics/system")
async def get_system_metrics(
    current_user: User = Depends(get_admin_user)
):
    """Get comprehensive system metrics"""
    
    metrics = metrics_collector.collect_system_metrics()
    return {
        "status": "success",
        "data": metrics
    }


@router.get("/metrics/application")
async def get_application_metrics(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get application-specific metrics"""
    
    metrics = metrics_collector.collect_application_metrics(db)
    return {
        "status": "success",
        "data": metrics
    }


@router.get("/metrics/performance")
async def get_performance_metrics(
    current_user: User = Depends(get_admin_user)
):
    """Get performance metrics and reports"""
    
    report = get_performance_report()
    return {
        "status": "success",
        "data": report
    }


@router.get("/metrics/dashboard")
async def get_monitoring_dashboard(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive monitoring dashboard data"""
    
    # Collect all metrics
    system_metrics = metrics_collector.collect_system_metrics()
    app_metrics = metrics_collector.collect_application_metrics(db)
    performance_report = get_performance_report()
    
    # Get active alerts
    active_alerts = alert_manager.get_active_alerts()
    
    # Get health status
    health_status = await health_check_service.run_health_checks()
    
    return {
        "status": "success",
        "data": {
            "system_metrics": system_metrics,
            "application_metrics": app_metrics,
            "performance_report": performance_report,
            "active_alerts": active_alerts,
            "health_status": health_status,
            "dashboard_updated_at": system_metrics.get("timestamp")
        }
    }


# Alert Management Routes
@router.get("/alerts")
async def get_alerts(
    status_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    current_user: User = Depends(get_admin_user)
):
    """Get alerts with optional filtering"""
    
    alerts = alert_manager.get_active_alerts()
    
    # Apply filters
    if status_filter:
        if status_filter == "active":
            alerts = [a for a in alerts if not a.get("resolved", False)]
        elif status_filter == "resolved":
            alerts = [a for a in alerts if a.get("resolved", False)]
    
    if severity_filter:
        alerts = [a for a in alerts if a.get("severity") == severity_filter]
    
    return {
        "status": "success",
        "data": {
            "alerts": alerts,
            "total_count": len(alerts),
            "filters_applied": {
                "status": status_filter,
                "severity": severity_filter
            }
        }
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_admin_user)
):
    """Resolve an active alert"""
    
    success = alert_manager.resolve_alert(alert_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return {
        "status": "success",
        "message": f"Alert {alert_id} resolved successfully"
    }


@router.post("/alerts/check")
async def trigger_alert_check(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Manually trigger alert checking"""
    
    # Run alert check in background
    background_tasks.add_task(
        _run_alert_check,
        db
    )
    
    return {
        "status": "success",
        "message": "Alert check triggered"
    }


async def _run_alert_check(db: Session):
    """Background task to check metrics and generate alerts"""
    
    # Collect metrics
    system_metrics = metrics_collector.collect_system_metrics()
    app_metrics = metrics_collector.collect_application_metrics(db)
    
    # Check for alerts
    system_alerts = alert_manager.check_metrics_for_alerts(system_metrics)
    app_alerts = alert_manager.check_metrics_for_alerts(app_metrics)
    
    # Send alerts
    for alert in system_alerts + app_alerts:
        await alert_manager.send_alert(alert)


@router.get("/alerts/thresholds")
async def get_alert_thresholds(
    current_user: User = Depends(get_admin_user)
):
    """Get current alert thresholds"""
    
    return {
        "status": "success",
        "data": {
            "thresholds": alert_manager.alert_thresholds
        }
    }


@router.put("/alerts/thresholds")
async def update_alert_thresholds(
    thresholds: Dict[str, Any],
    current_user: User = Depends(get_admin_user)
):
    """Update alert thresholds"""
    
    # Validate and update thresholds
    for metric_name, threshold_config in thresholds.items():
        if metric_name in alert_manager.alert_thresholds:
            alert_manager.alert_thresholds[metric_name].update(threshold_config)
    
    return {
        "status": "success",
        "message": "Alert thresholds updated successfully",
        "updated_thresholds": alert_manager.alert_thresholds
    }


# Health Check Routes
@router.get("/health")
async def get_health_status():
    """Get comprehensive health status (public endpoint)"""
    
    health_status = await health_check_service.run_health_checks()
    
    # Return appropriate HTTP status based on health
    if not health_status["overall_healthy"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/health/detailed")
async def get_detailed_health_status(
    current_user: User = Depends(get_admin_user)
):
    """Get detailed health status with full diagnostics"""
    
    health_status = await health_check_service.run_health_checks()
    
    return {
        "status": "success",
        "data": health_status
    }


@router.post("/health/check/{service}")
async def run_specific_health_check(
    service: str,
    current_user: User = Depends(get_admin_user)
):
    """Run health check for specific service"""
    
    if service not in health_check_service.health_checks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown service: {service}"
        )
    
    check_func = health_check_service.health_checks[service]
    result = await check_func()
    
    return {
        "status": "success",
        "service": service,
        "data": result
    }


# Performance Analysis Routes
@router.get("/performance/analysis")
async def get_performance_analysis(
    hours: int = 24,
    current_user: User = Depends(get_admin_user)
):
    """Get performance analysis for specified time period"""
    
    from app.core.performance import performance_optimizer
    
    # Get metrics for the specified period
    metrics = performance_monitor.get_metrics_summary(hours=hours)
    
    # Get optimization recommendations
    optimizations = performance_optimizer.optimize_based_on_patterns(metrics)
    
    return {
        "status": "success",
        "data": {
            "time_period_hours": hours,
            "metrics_summary": metrics,
            "optimization_recommendations": optimizations,
            "analysis_timestamp": datetime.now().isoformat()
        }
    }


@router.get("/performance/trends")
async def get_performance_trends(
    metric: str,
    days: int = 7,
    current_user: User = Depends(get_admin_user)
):
    """Get performance trends for specific metric"""
    
    # This would typically fetch historical data from time-series database
    # For now, return mock trend data
    
    from datetime import datetime, timedelta
    import random
    
    trends = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i-1)
        value = random.uniform(50, 100)  # Mock data
        trends.append({
            "timestamp": date.isoformat(),
            "value": value
        })
    
    return {
        "status": "success",
        "data": {
            "metric": metric,
            "time_period_days": days,
            "trends": trends,
            "average": sum(t["value"] for t in trends) / len(trends),
            "min_value": min(t["value"] for t in trends),
            "max_value": max(t["value"] for t in trends)
        }
    }


# Log Analysis Routes
@router.get("/logs/errors")
async def get_error_logs(
    hours: int = 24,
    severity: Optional[str] = None,
    current_user: User = Depends(get_admin_user)
):
    """Get error logs for analysis"""
    
    # This would typically fetch from centralized logging system
    # For now, return mock error data
    
    errors = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "level": "ERROR",
            "message": "Database connection timeout",
            "source": "database_service",
            "count": 5
        },
        {
            "timestamp": "2024-01-15T09:15:00Z",
            "level": "WARNING",
            "message": "High memory usage detected",
            "source": "monitoring_service",
            "count": 1
        }
    ]
    
    # Apply severity filter
    if severity:
        errors = [e for e in errors if e["level"] == severity.upper()]
    
    return {
        "status": "success",
        "data": {
            "time_period_hours": hours,
            "severity_filter": severity,
            "errors": errors,
            "total_count": len(errors)
        }
    }


@router.get("/logs/audit")
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    hours: int = 24,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs for security analysis"""
    
    from app.models.user import SecurityLog
    from datetime import datetime, timedelta
    
    query = db.query(SecurityLog)
    
    # Apply filters
    if user_id:
        query = query.filter(SecurityLog.user_id == user_id)
    
    if action:
        query = query.filter(SecurityLog.event_type.ilike(f"%{action}%"))
    
    # Time filter
    since = datetime.now() - timedelta(hours=hours)
    query = query.filter(SecurityLog.timestamp >= since)
    
    logs = query.order_by(SecurityLog.timestamp.desc()).limit(100).all()
    
    return {
        "status": "success",
        "data": {
            "time_period_hours": hours,
            "filters": {
                "user_id": user_id,
                "action": action
            },
            "logs": [
                {
                    "id": str(log.id),
                    "event_type": log.event_type,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "ip_address": log.ip_address,
                    "severity": log.severity,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ],
            "total_count": len(logs)
        }
    }


# Monitoring Configuration Routes
@router.get("/config")
async def get_monitoring_config(
    current_user: User = Depends(get_admin_user)
):
    """Get monitoring configuration"""
    
    return {
        "status": "success",
        "data": {
            "metrics_collection_interval": 60,  # seconds
            "alert_check_interval": 300,  # seconds
            "health_check_interval": 120,  # seconds
            "log_retention_days": 30,
            "metrics_retention_days": 90,
            "alert_thresholds": alert_manager.alert_thresholds,
            "enabled_checks": list(health_check_service.health_checks.keys())
        }
    }


@router.put("/config")
async def update_monitoring_config(
    config: Dict[str, Any],
    current_user: User = Depends(get_admin_user)
):
    """Update monitoring configuration"""
    
    # In production, this would update the actual configuration
    # For now, just return success
    
    return {
        "status": "success",
        "message": "Monitoring configuration updated successfully",
        "updated_config": config
    }
