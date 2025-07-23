"""
Advanced Database Optimization for MEDHASAKTHI
Enterprise-grade database performance optimization, connection pooling, and query optimization
"""
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import create_engine, event, text, MetaData, Table, Index
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.sql import func
import redis
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.performance import performance_monitor

# Database performance logger
db_logger = logging.getLogger("database_performance")
db_logger.setLevel(logging.INFO)


class DatabaseConnectionManager:
    """Advanced database connection management with pooling and monitoring"""
    
    def __init__(self):
        self.engines = {}
        self.session_factories = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "pool_size": 0,
            "overflow_size": 0,
            "checked_out": 0,
            "checked_in": 0,
            "invalidated": 0
        }
        self.query_cache = {}
        self.setup_engines()
    
    def setup_engines(self):
        """Setup database engines with optimized configurations"""
        
        # Primary database engine (read/write)
        self.engines["primary"] = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,  # Base number of connections
            max_overflow=30,  # Additional connections when needed
            pool_pre_ping=True,  # Validate connections before use
            pool_recycle=3600,  # Recycle connections every hour
            echo=settings.DEBUG,  # Log SQL queries in debug mode
            connect_args={
                "connect_timeout": 10,
                "command_timeout": 30,
                "application_name": "MEDHASAKTHI_PRIMARY"
            }
        )
        
        # Read-only replica engine (if available)
        if hasattr(settings, 'DATABASE_READ_URL') and settings.DATABASE_READ_URL:
            self.engines["replica"] = create_engine(
                settings.DATABASE_READ_URL,
                poolclass=QueuePool,
                pool_size=15,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
                connect_args={
                    "connect_timeout": 10,
                    "command_timeout": 30,
                    "application_name": "MEDHASAKTHI_REPLICA"
                }
            )
        
        # Setup session factories
        for name, engine in self.engines.items():
            self.session_factories[name] = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # Setup connection monitoring
            self._setup_connection_monitoring(engine, name)
    
    def _setup_connection_monitoring(self, engine: Engine, name: str):
        """Setup connection pool monitoring"""
        
        @event.listens_for(engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            self.connection_stats["total_connections"] += 1
            db_logger.info(f"New connection established to {name}")
        
        @event.listens_for(engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            self.connection_stats["checked_out"] += 1
            self.connection_stats["active_connections"] += 1
        
        @event.listens_for(engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            self.connection_stats["checked_in"] += 1
            self.connection_stats["active_connections"] -= 1
        
        @event.listens_for(engine, "invalidate")
        def on_invalidate(dbapi_connection, connection_record, exception):
            self.connection_stats["invalidated"] += 1
            db_logger.warning(f"Connection invalidated: {exception}")
    
    def get_session(self, read_only: bool = False) -> Session:
        """Get database session with read/write routing"""
        if read_only and "replica" in self.engines:
            return self.session_factories["replica"]()
        return self.session_factories["primary"]()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        stats = self.connection_stats.copy()
        
        # Add pool-specific stats
        for name, engine in self.engines.items():
            pool = engine.pool
            stats[f"{name}_pool_size"] = pool.size()
            stats[f"{name}_checked_out"] = pool.checkedout()
            stats[f"{name}_overflow"] = pool.overflow()
            stats[f"{name}_checked_in"] = pool.checkedin()
        
        return stats


class QueryOptimizer:
    """Advanced query optimization and analysis"""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.slow_queries = {}
        self.query_plans = {}
        self.optimization_suggestions = []
        self.slow_query_threshold = 1.0  # seconds
    
    def analyze_query_performance(self, db: Session) -> Dict[str, Any]:
        """Analyze database query performance"""
        
        # Get slow queries from PostgreSQL
        slow_queries = self._get_slow_queries(db)
        
        # Analyze query plans
        query_plans = self._analyze_query_plans(db, slow_queries)
        
        # Generate optimization suggestions
        suggestions = self._generate_optimization_suggestions(slow_queries, query_plans)
        
        return {
            "slow_queries": slow_queries,
            "query_plans": query_plans,
            "optimization_suggestions": suggestions,
            "performance_metrics": self._get_performance_metrics(db)
        }
    
    def _get_slow_queries(self, db: Session) -> List[Dict[str, Any]]:
        """Get slow queries from pg_stat_statements"""
        try:
            query = text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements 
                WHERE mean_time > :threshold
                ORDER BY total_time DESC 
                LIMIT 20
            """)
            
            result = db.execute(query, {"threshold": self.slow_query_threshold * 1000})
            return [dict(row) for row in result]
        except Exception as e:
            db_logger.warning(f"Could not fetch slow queries: {e}")
            return []
    
    def _analyze_query_plans(self, db: Session, slow_queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze execution plans for slow queries"""
        plans = []
        
        for query_info in slow_queries[:5]:  # Analyze top 5 slow queries
            try:
                query = query_info["query"]
                if query and not query.strip().upper().startswith(("EXPLAIN", "SELECT pg_stat")):
                    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                    result = db.execute(text(explain_query))
                    plan = result.fetchone()
                    
                    if plan:
                        plans.append({
                            "query": query[:200] + "..." if len(query) > 200 else query,
                            "plan": plan[0],
                            "total_time": query_info.get("total_time", 0),
                            "mean_time": query_info.get("mean_time", 0)
                        })
            except Exception as e:
                db_logger.warning(f"Could not analyze query plan: {e}")
        
        return plans
    
    def _generate_optimization_suggestions(
        self, 
        slow_queries: List[Dict[str, Any]], 
        query_plans: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on analysis"""
        suggestions = []
        
        # Analyze slow queries
        for query in slow_queries:
            if query.get("hit_percent", 100) < 95:
                suggestions.append({
                    "type": "cache_optimization",
                    "priority": "high",
                    "description": "Low cache hit ratio detected",
                    "recommendation": "Consider increasing shared_buffers or optimizing query patterns",
                    "query": query.get("query", "")[:100]
                })
            
            if query.get("mean_time", 0) > 5000:  # 5 seconds
                suggestions.append({
                    "type": "query_optimization",
                    "priority": "critical",
                    "description": "Very slow query detected",
                    "recommendation": "Review query structure and add appropriate indexes",
                    "query": query.get("query", "")[:100]
                })
        
        # Analyze query plans
        for plan_info in query_plans:
            plan = plan_info.get("plan", [])
            if plan and isinstance(plan, list) and len(plan) > 0:
                execution_plan = plan[0].get("Plan", {})
                
                # Check for sequential scans
                if self._has_sequential_scan(execution_plan):
                    suggestions.append({
                        "type": "index_suggestion",
                        "priority": "medium",
                        "description": "Sequential scan detected",
                        "recommendation": "Consider adding indexes to improve query performance",
                        "query": plan_info.get("query", "")
                    })
                
                # Check for high cost operations
                if execution_plan.get("Total Cost", 0) > 10000:
                    suggestions.append({
                        "type": "cost_optimization",
                        "priority": "high",
                        "description": "High-cost query operation",
                        "recommendation": "Review query logic and consider optimization",
                        "query": plan_info.get("query", "")
                    })
        
        return suggestions
    
    def _has_sequential_scan(self, plan: Dict[str, Any]) -> bool:
        """Check if execution plan contains sequential scans"""
        if plan.get("Node Type") == "Seq Scan":
            return True
        
        # Check child plans recursively
        for child in plan.get("Plans", []):
            if self._has_sequential_scan(child):
                return True
        
        return False
    
    def _get_performance_metrics(self, db: Session) -> Dict[str, Any]:
        """Get database performance metrics"""
        try:
            # Database size
            size_query = text("SELECT pg_size_pretty(pg_database_size(current_database())) as size")
            db_size = db.execute(size_query).scalar()
            
            # Connection count
            conn_query = text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            active_connections = db.execute(conn_query).scalar()
            
            # Cache hit ratio
            cache_query = text("""
                SELECT 
                    round(100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2) as cache_hit_ratio
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            cache_hit_ratio = db.execute(cache_query).scalar()
            
            # Transaction statistics
            txn_query = text("""
                SELECT 
                    xact_commit,
                    xact_rollback,
                    tup_returned,
                    tup_fetched,
                    tup_inserted,
                    tup_updated,
                    tup_deleted
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            txn_stats = db.execute(txn_query).fetchone()
            
            return {
                "database_size": db_size,
                "active_connections": active_connections,
                "cache_hit_ratio": float(cache_hit_ratio or 0),
                "transaction_stats": dict(txn_stats) if txn_stats else {}
            }
        except Exception as e:
            db_logger.warning(f"Could not fetch performance metrics: {e}")
            return {}


class IndexManager:
    """Intelligent index management and optimization"""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.suggested_indexes = []
    
    def analyze_missing_indexes(self, db: Session) -> List[Dict[str, Any]]:
        """Analyze and suggest missing indexes"""
        try:
            # Query to find missing indexes based on query patterns
            missing_indexes_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                AND n_distinct > 100
                AND correlation < 0.1
                ORDER BY n_distinct DESC
                LIMIT 20
            """)
            
            result = db.execute(missing_indexes_query)
            suggestions = []
            
            for row in result:
                suggestions.append({
                    "table": f"{row.schemaname}.{row.tablename}",
                    "column": row.attname,
                    "n_distinct": row.n_distinct,
                    "correlation": row.correlation,
                    "suggested_index": f"CREATE INDEX idx_{row.tablename}_{row.attname} ON {row.tablename} ({row.attname});",
                    "priority": "high" if row.n_distinct > 1000 else "medium"
                })
            
            return suggestions
        except Exception as e:
            db_logger.warning(f"Could not analyze missing indexes: {e}")
            return []
    
    def get_unused_indexes(self, db: Session) -> List[Dict[str, Any]]:
        """Find unused indexes that can be dropped"""
        try:
            unused_indexes_query = text("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_size_pretty(pg_relation_size(indexrelid)) as size
                FROM pg_stat_user_indexes 
                WHERE idx_scan = 0
                AND schemaname = 'public'
                ORDER BY pg_relation_size(indexrelid) DESC
            """)
            
            result = db.execute(unused_indexes_query)
            unused = []
            
            for row in result:
                unused.append({
                    "schema": row.schemaname,
                    "table": row.tablename,
                    "index": row.indexname,
                    "size": row.size,
                    "scans": row.idx_scan,
                    "drop_statement": f"DROP INDEX {row.indexname};"
                })
            
            return unused
        except Exception as e:
            db_logger.warning(f"Could not find unused indexes: {e}")
            return []
    
    def create_recommended_indexes(self, db: Session, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create recommended indexes"""
        created = []
        failed = []
        
        for suggestion in suggestions:
            try:
                if suggestion.get("priority") == "high":
                    db.execute(text(suggestion["suggested_index"]))
                    db.commit()
                    created.append(suggestion["suggested_index"])
                    db_logger.info(f"Created index: {suggestion['suggested_index']}")
            except Exception as e:
                failed.append({
                    "index": suggestion["suggested_index"],
                    "error": str(e)
                })
                db_logger.error(f"Failed to create index: {e}")
        
        return {
            "created": created,
            "failed": failed,
            "total_suggestions": len(suggestions)
        }


class DatabaseMaintenanceManager:
    """Automated database maintenance and optimization"""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.connection_manager = connection_manager
        self.maintenance_schedule = {}
    
    def run_maintenance_tasks(self, db: Session) -> Dict[str, Any]:
        """Run automated maintenance tasks"""
        results = {}
        
        # Update table statistics
        results["analyze"] = self._run_analyze(db)
        
        # Vacuum tables
        results["vacuum"] = self._run_vacuum(db)
        
        # Reindex if needed
        results["reindex"] = self._run_reindex(db)
        
        # Clean up old data
        results["cleanup"] = self._cleanup_old_data(db)
        
        return results
    
    def _run_analyze(self, db: Session) -> Dict[str, Any]:
        """Update table statistics"""
        try:
            db.execute(text("ANALYZE;"))
            db.commit()
            return {"status": "success", "message": "Table statistics updated"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _run_vacuum(self, db: Session) -> Dict[str, Any]:
        """Vacuum tables to reclaim space"""
        try:
            # Get tables that need vacuuming
            vacuum_query = text("""
                SELECT schemaname, tablename, n_dead_tup, n_live_tup
                FROM pg_stat_user_tables 
                WHERE n_dead_tup > 1000
                ORDER BY n_dead_tup DESC
                LIMIT 10
            """)
            
            result = db.execute(vacuum_query)
            vacuumed_tables = []
            
            for row in result:
                table_name = f"{row.schemaname}.{row.tablename}"
                db.execute(text(f"VACUUM {table_name};"))
                vacuumed_tables.append(table_name)
            
            db.commit()
            return {
                "status": "success", 
                "message": f"Vacuumed {len(vacuumed_tables)} tables",
                "tables": vacuumed_tables
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _run_reindex(self, db: Session) -> Dict[str, Any]:
        """Reindex tables if needed"""
        try:
            # This is a simplified implementation
            # In production, you'd want more sophisticated logic
            return {"status": "skipped", "message": "Reindex not needed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _cleanup_old_data(self, db: Session) -> Dict[str, Any]:
        """Clean up old data based on retention policies"""
        try:
            cleaned_records = 0
            
            # Clean old security logs (older than 90 days)
            old_logs_query = text("""
                DELETE FROM security_logs 
                WHERE timestamp < NOW() - INTERVAL '90 days'
            """)
            result = db.execute(old_logs_query)
            cleaned_records += result.rowcount
            
            # Clean old device sessions (expired)
            old_sessions_query = text("""
                DELETE FROM device_sessions 
                WHERE expires_at < NOW()
            """)
            result = db.execute(old_sessions_query)
            cleaned_records += result.rowcount
            
            db.commit()
            return {
                "status": "success",
                "message": f"Cleaned {cleaned_records} old records"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Global instances
db_connection_manager = DatabaseConnectionManager()
query_optimizer = QueryOptimizer(db_connection_manager)
index_manager = IndexManager(db_connection_manager)
maintenance_manager = DatabaseMaintenanceManager(db_connection_manager)
