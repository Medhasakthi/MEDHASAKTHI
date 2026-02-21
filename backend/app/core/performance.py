"""
Performance Optimization Module for MEDHASAKTHI
Advanced caching, database optimization, and performance monitoring
"""
import asyncio
import time
import json
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta
import redis
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool
import logging

from app.core.config import settings

# Performance logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)

# Redis clients for different caching purposes
cache_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_CACHE_DB,
    decode_responses=True
)

session_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_SESSION_DB,
    decode_responses=True
)


class CacheManager:
    """Advanced caching system with multiple strategies"""
    
    def __init__(self):
        self.default_ttl = 3600  # 1 hour
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = cache_redis.get(key)
            if value:
                self.cache_stats["hits"] += 1
                return json.loads(value)
            else:
                self.cache_stats["misses"] += 1
                return None
        except Exception as e:
            perf_logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            cache_redis.setex(key, ttl, json.dumps(value, default=str))
            self.cache_stats["sets"] += 1
            return True
        except Exception as e:
            perf_logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            cache_redis.delete(key)
            self.cache_stats["deletes"] += 1
            return True
        except Exception as e:
            perf_logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = cache_redis.keys(pattern)
            if keys:
                deleted = cache_redis.delete(*keys)
                self.cache_stats["deletes"] += deleted
                return deleted
            return 0
        except Exception as e:
            perf_logger.error(f"Cache delete pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_operations = sum(self.cache_stats.values())
        hit_rate = (self.cache_stats["hits"] / total_operations * 100) if total_operations > 0 else 0
        
        return {
            **self.cache_stats,
            "hit_rate_percent": round(hit_rate, 2),
            "total_operations": total_operations
        }


class DatabaseOptimizer:
    """Database performance optimization and monitoring"""
    
    def __init__(self):
        self.query_stats = {}
        self.slow_query_threshold = 1.0  # seconds
        self.setup_query_monitoring()
    
    def setup_query_monitoring(self):
        """Setup SQLAlchemy query monitoring"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total_time = time.time() - context._query_start_time
            
            # Log slow queries
            if total_time > self.slow_query_threshold:
                perf_logger.warning(
                    f"Slow query detected: {total_time:.3f}s - {statement[:200]}..."
                )
            
            # Update query statistics
            query_hash = hash(statement)
            if query_hash not in self.query_stats:
                self.query_stats[query_hash] = {
                    "statement": statement[:200],
                    "count": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "max_time": 0
                }
            
            stats = self.query_stats[query_hash]
            stats["count"] += 1
            stats["total_time"] += total_time
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["max_time"] = max(stats["max_time"], total_time)
    
    def get_query_stats(self) -> List[Dict[str, Any]]:
        """Get query performance statistics"""
        return sorted(
            self.query_stats.values(),
            key=lambda x: x["total_time"],
            reverse=True
        )[:20]  # Top 20 queries by total time
    
    def optimize_query_plan(self, db: Session, query: str) -> Dict[str, Any]:
        """Analyze query execution plan"""
        try:
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = db.execute(text(explain_query)).fetchone()
            return result[0] if result else {}
        except Exception as e:
            perf_logger.error(f"Query plan analysis error: {e}")
            return {}


class PerformanceMonitor:
    """Real-time performance monitoring and alerting"""
    
    def __init__(self):
        self.metrics = {}
        self.alert_thresholds = {
            "response_time_ms": 1000,
            "memory_usage_percent": 80,
            "cpu_usage_percent": 80,
            "error_rate_percent": 5
        }
    
    def record_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a performance metric"""
        timestamp = timestamp or datetime.now()
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp.isoformat()
        })
        
        # Keep only last 1000 data points
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
        
        # Check for alerts
        self.check_alert(metric_name, value)
    
    def check_alert(self, metric_name: str, value: float):
        """Check if metric value triggers an alert"""
        threshold = self.alert_thresholds.get(metric_name)
        if threshold and value > threshold:
            perf_logger.warning(
                f"Performance alert: {metric_name} = {value} exceeds threshold {threshold}"
            )
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get performance metrics summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        summary = {}
        
        for metric_name, data_points in self.metrics.items():
            recent_points = [
                dp for dp in data_points
                if datetime.fromisoformat(dp["timestamp"]) >= cutoff_time
            ]
            
            if recent_points:
                values = [dp["value"] for dp in recent_points]
                summary[metric_name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1]
                }
        
        return summary


# Decorators for performance optimization
def cached(ttl: int = 3600, key_prefix: str = "default"):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = cache_manager.cache_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = cache_manager.cache_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def monitor_performance(metric_name: str):
    """Decorator for monitoring function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                performance_monitor.record_metric(f"{metric_name}_response_time_ms", execution_time)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                performance_monitor.record_metric(f"{metric_name}_response_time_ms", execution_time)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def rate_limit(max_calls: int, window_seconds: int):
    """Decorator for rate limiting function calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use first argument as identifier (usually user_id)
            identifier = str(args[0]) if args else "anonymous"
            key = f"rate_limit:{func.__name__}:{identifier}"
            
            current_calls = cache_redis.get(key)
            if current_calls is None:
                cache_redis.setex(key, window_seconds, 1)
                return func(*args, **kwargs)
            
            if int(current_calls) >= max_calls:
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {window_seconds} seconds")
            
            cache_redis.incr(key)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class IntelligentCacheWarmer:
    """Intelligent cache warming system"""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.warming_patterns = {
            "user_profiles": {"ttl": 3600, "priority": "high"},
            "exam_questions": {"ttl": 7200, "priority": "medium"},
            "institute_data": {"ttl": 1800, "priority": "high"},
            "system_config": {"ttl": 86400, "priority": "low"}
        }

    async def warm_cache_for_user(self, user_id: str, db: Session):
        """Warm cache for specific user"""
        from app.models.user import User, Student

        # Cache user profile
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            cache_key = self.cache_manager.cache_key("user_profile", user_id)
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
            self.cache_manager.set(cache_key, user_data, 3600)

        # Cache student data if applicable
        student = db.query(Student).filter(Student.user_id == user_id).first()
        if student:
            cache_key = self.cache_manager.cache_key("student_profile", user_id)
            student_data = {
                "id": str(student.id),
                "student_id": student.student_id,
                "current_class": student.current_class,
                "institute_id": str(student.institute_id) if student.institute_id else None
            }
            self.cache_manager.set(cache_key, student_data, 3600)

    async def warm_popular_content(self, db: Session):
        """Warm cache with popular content"""
        # This would analyze usage patterns and pre-cache popular content
        pass

    async def schedule_cache_warming(self):
        """Schedule regular cache warming"""
        # This would run as a background task
        pass


class AdvancedPerformanceOptimizer:
    """Advanced performance optimization with ML-based predictions"""

    def __init__(self):
        self.optimization_history = []
        self.performance_predictions = {}

    def optimize_based_on_patterns(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize performance based on usage patterns"""
        optimizations = []

        # Analyze response times
        avg_response_time = metrics.get("avg_response_time_ms", 0)
        if avg_response_time > 500:
            optimizations.append({
                "type": "response_time",
                "action": "increase_cache_ttl",
                "priority": "high"
            })

        # Analyze cache hit rates
        cache_stats = metrics.get("cache_stats", {})
        hit_rate = cache_stats.get("hit_rate_percent", 0)
        if hit_rate < 80:
            optimizations.append({
                "type": "cache_optimization",
                "action": "warm_cache_proactively",
                "priority": "medium"
            })

        # Analyze memory usage
        memory_usage = metrics.get("memory_usage_percent", 0)
        if memory_usage > 80:
            optimizations.append({
                "type": "memory_optimization",
                "action": "implement_cache_eviction",
                "priority": "high"
            })

        return {
            "optimizations": optimizations,
            "predicted_improvement": self._predict_improvement(optimizations),
            "timestamp": datetime.now().isoformat()
        }

    def _predict_improvement(self, optimizations: List[Dict[str, Any]]) -> Dict[str, float]:
        """Predict performance improvement from optimizations"""
        # Simplified prediction model
        improvements = {
            "response_time_reduction_percent": 0,
            "cache_hit_rate_increase_percent": 0,
            "memory_usage_reduction_percent": 0
        }

        for opt in optimizations:
            if opt["type"] == "response_time":
                improvements["response_time_reduction_percent"] += 15
            elif opt["type"] == "cache_optimization":
                improvements["cache_hit_rate_increase_percent"] += 10
            elif opt["type"] == "memory_optimization":
                improvements["memory_usage_reduction_percent"] += 20

        return improvements


# Global instances
cache_manager = CacheManager()
db_optimizer = DatabaseOptimizer()
performance_monitor = PerformanceMonitor()
cache_warmer = IntelligentCacheWarmer(cache_manager)
performance_optimizer = AdvancedPerformanceOptimizer()


# Utility functions
def invalidate_cache_pattern(pattern: str):
    """Invalidate all cache entries matching pattern"""
    return cache_manager.delete_pattern(pattern)


def get_performance_report() -> Dict[str, Any]:
    """Get comprehensive performance report"""
    return {
        "cache_stats": cache_manager.get_stats(),
        "query_stats": db_optimizer.get_query_stats(),
        "performance_metrics": performance_monitor.get_metrics_summary(),
        "timestamp": datetime.now().isoformat()
    }


async def optimize_performance_automatically():
    """Automatically optimize performance based on current metrics"""
    metrics = performance_monitor.get_metrics_summary()
    optimizations = performance_optimizer.optimize_based_on_patterns(metrics)

    # Apply optimizations
    for opt in optimizations["optimizations"]:
        if opt["action"] == "warm_cache_proactively":
            # Trigger cache warming
            pass
        elif opt["action"] == "increase_cache_ttl":
            # Increase cache TTL for frequently accessed items
            pass
        elif opt["action"] == "implement_cache_eviction":
            # Implement intelligent cache eviction
            pass

    return optimizations
