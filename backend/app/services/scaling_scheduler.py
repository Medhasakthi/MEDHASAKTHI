"""
Scaling Scheduler Service
Background task scheduler for auto-scaling and load balancer management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.server import Server, ServerMetrics
from app.core.config import settings

logger = logging.getLogger(__name__)

class ScalingScheduler:
    """Background scheduler for auto-scaling and monitoring tasks"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
        
        # Configuration
        self.health_check_interval = getattr(settings, 'HEALTH_CHECK_INTERVAL_SECONDS', 30)
        self.metrics_collection_interval = getattr(settings, 'METRICS_COLLECTION_INTERVAL_SECONDS', 60)
        self.scaling_check_interval = getattr(settings, 'SCALING_CHECK_INTERVAL_SECONDS', 300)  # 5 minutes
        self.cleanup_interval = getattr(settings, 'CLEANUP_INTERVAL_SECONDS', 3600)  # 1 hour
        
    async def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info("Starting scaling scheduler...")
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._scaling_check_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]
        
        logger.info("Scaling scheduler started successfully")
    
    async def stop(self):
        """Stop the background scheduler"""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping scaling scheduler...")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks = []
        logger.info("Scaling scheduler stopped")
    
    async def _health_check_loop(self):
        """Periodic health check for all servers"""
        while self.running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _metrics_collection_loop(self):
        """Periodic metrics collection from all servers"""
        while self.running:
            try:
                await self._collect_server_metrics()
                await asyncio.sleep(self.metrics_collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(self.metrics_collection_interval)
    
    async def _scaling_check_loop(self):
        """Periodic auto-scaling checks"""
        while self.running:
            try:
                await self._perform_scaling_check()
                await asyncio.sleep(self.scaling_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scaling check loop: {e}")
                await asyncio.sleep(self.scaling_check_interval)
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old metrics and logs"""
        while self.running:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(self.cleanup_interval)
    
    async def _perform_health_checks(self):
        """Perform health checks on all active servers"""
        try:
            db = next(get_db())
            
            # Get all active servers
            servers = db.query(Server).filter(Server.status == 'active').all()
            
            health_results = []
            for server in servers:
                try:
                    # Perform health check
                    from app.services.load_balancer_service import load_balancer_service
                    is_healthy = await load_balancer_service._health_check_server(
                        server.ip_address,
                        server.port
                    )
                    
                    # Update server health status
                    old_status = server.health_status
                    server.update_health_status(is_healthy)
                    
                    # Log status changes
                    if old_status != server.health_status:
                        logger.info(f"Server {server.hostname} health status changed: {old_status} -> {server.health_status}")
                        
                        # If server became unhealthy, trigger nginx config update
                        if server.health_status == 'unhealthy':
                            from app.services.load_balancer_service import load_balancer_service
                            await load_balancer_service._update_nginx_config(db)
                    
                    health_results.append({
                        'server_id': server.id,
                        'hostname': server.hostname,
                        'health_status': server.health_status,
                        'response_time_ms': server.response_time_ms
                    })
                    
                except Exception as e:
                    logger.error(f"Health check failed for server {server.hostname}: {e}")
                    server.health_status = 'unhealthy'
                    server.error_count += 1
            
            db.commit()
            
            # Log summary
            healthy_count = len([r for r in health_results if r['health_status'] == 'healthy'])
            logger.debug(f"Health check completed: {healthy_count}/{len(health_results)} servers healthy")
            
        except Exception as e:
            logger.error(f"Error performing health checks: {e}")
        finally:
            db.close()
    
    async def _collect_server_metrics(self):
        """Collect performance metrics from all servers"""
        try:
            db = next(get_db())
            
            # Get all healthy servers
            servers = db.query(Server).filter(
                Server.status == 'active',
                Server.health_status == 'healthy'
            ).all()
            
            for server in servers:
                try:
                    # Collect metrics from server
                    metrics = await self._get_server_metrics(server)
                    
                    if metrics:
                        # Store metrics in database
                        server_metric = ServerMetrics(
                            server_id=server.id,
                            recorded_at=datetime.utcnow(),
                            cpu_usage_percent=metrics.get('cpu_usage_percent'),
                            memory_usage_percent=metrics.get('memory_usage_percent'),
                            disk_usage_percent=metrics.get('disk_usage_percent'),
                            network_in_mbps=metrics.get('network_in_mbps'),
                            network_out_mbps=metrics.get('network_out_mbps'),
                            active_connections=metrics.get('active_connections'),
                            requests_per_second=metrics.get('requests_per_second'),
                            response_time_avg_ms=metrics.get('response_time_avg_ms'),
                            error_rate_percent=metrics.get('error_rate_percent'),
                            requests_handled=metrics.get('requests_handled', 0),
                            bytes_transferred=metrics.get('bytes_transferred', 0)
                        )
                        
                        db.add(server_metric)
                        
                        # Update server's latest response time
                        if metrics.get('response_time_avg_ms'):
                            server.response_time_ms = metrics['response_time_avg_ms']
                
                except Exception as e:
                    logger.error(f"Metrics collection failed for server {server.hostname}: {e}")
            
            db.commit()
            logger.debug(f"Metrics collected for {len(servers)} servers")
            
        except Exception as e:
            logger.error(f"Error collecting server metrics: {e}")
        finally:
            db.close()
    
    async def _get_server_metrics(self, server: Server) -> Dict:
        """Get metrics from a specific server"""
        try:
            import aiohttp
            import random
            
            # For demo purposes, generate realistic mock metrics
            # In production, this would query actual server metrics endpoints
            
            base_cpu = 30 + random.randint(-10, 40)  # 20-70% CPU
            base_memory = 40 + random.randint(-15, 30)  # 25-70% Memory
            
            # Simulate higher load during business hours
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:  # Business hours
                base_cpu += random.randint(0, 20)
                base_memory += random.randint(0, 15)
            
            metrics = {
                'cpu_usage_percent': min(95, max(5, base_cpu)),
                'memory_usage_percent': min(90, max(10, base_memory)),
                'disk_usage_percent': random.randint(20, 60),
                'network_in_mbps': random.randint(1, 50),
                'network_out_mbps': random.randint(1, 30),
                'active_connections': random.randint(10, 200),
                'requests_per_second': random.randint(5, 100),
                'response_time_avg_ms': random.randint(50, 500),
                'error_rate_percent': random.randint(0, 5),
                'requests_handled': random.randint(100, 1000),
                'bytes_transferred': random.randint(1000000, 10000000)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics from server {server.hostname}: {e}")
            return {}
    
    async def _perform_scaling_check(self):
        """Perform auto-scaling check"""
        try:
            db = next(get_db())
            
            # Run auto-scaling analysis
            from app.services.auto_scaling_service import auto_scaling_service
            result = await auto_scaling_service.monitor_and_scale(db)
            
            if result.get('success'):
                logger.info(f"Auto-scaling action completed: {result}")
            elif 'error' in result:
                logger.error(f"Auto-scaling error: {result['error']}")
            else:
                logger.debug(f"Auto-scaling check: {result.get('message', 'No action needed')}")
            
        except Exception as e:
            logger.error(f"Error performing scaling check: {e}")
        finally:
            db.close()
    
    async def _perform_cleanup(self):
        """Perform cleanup of old data"""
        try:
            db = next(get_db())
            
            # Clean up old metrics (keep last 7 days)
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            
            deleted_metrics = db.query(ServerMetrics).filter(
                ServerMetrics.recorded_at < cutoff_date
            ).delete()
            
            if deleted_metrics > 0:
                logger.info(f"Cleaned up {deleted_metrics} old metric records")
            
            # Clean up inactive servers (older than 30 days)
            inactive_cutoff = datetime.utcnow() - timedelta(days=30)
            
            deleted_servers = db.query(Server).filter(
                Server.status == 'inactive',
                Server.removed_at < inactive_cutoff
            ).delete()
            
            if deleted_servers > 0:
                logger.info(f"Cleaned up {deleted_servers} old inactive server records")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error performing cleanup: {e}")
        finally:
            db.close()
    
    async def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'active_tasks': len([t for t in self.tasks if not t.done()]),
            'health_check_interval': self.health_check_interval,
            'metrics_collection_interval': self.metrics_collection_interval,
            'scaling_check_interval': self.scaling_check_interval,
            'last_health_check': getattr(self, '_last_health_check', None),
            'last_metrics_collection': getattr(self, '_last_metrics_collection', None),
            'last_scaling_check': getattr(self, '_last_scaling_check', None)
        }

# Global scheduler instance
scaling_scheduler = ScalingScheduler()
