"""
Dynamic Load Balancer Management Service
Allows super admin to add/remove servers and automatically update nginx configuration
"""

import os
import json
import subprocess
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.database import get_db
from app.models.server import Server
from app.core.config import settings

logger = logging.getLogger(__name__)

class LoadBalancerService:
    """Service for managing dynamic load balancing"""
    
    def __init__(self):
        self.nginx_config_path = "/etc/nginx/conf.d/upstream.conf"
        self.nginx_template_path = "/app/templates/nginx-upstream.template"
        self.consul_enabled = getattr(settings, 'CONSUL_ENABLED', False)
        self.consul_url = getattr(settings, 'CONSUL_URL', 'http://consul:8500')
        
    async def add_server(self, db: Session, server_data: Dict) -> Dict:
        """Add a new server to the load balancer pool"""
        try:
            # Validate server data
            required_fields = ['hostname', 'ip_address', 'port', 'server_type', 'weight']
            for field in required_fields:
                if field not in server_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            # Check if server is reachable
            if not await self._health_check_server(server_data['ip_address'], server_data['port']):
                raise HTTPException(status_code=400, detail="Server is not reachable")
            
            # Create server record in database
            server = Server(
                hostname=server_data['hostname'],
                ip_address=server_data['ip_address'],
                port=server_data['port'],
                server_type=server_data['server_type'],  # 'backend', 'frontend', 'database'
                weight=server_data.get('weight', 1),
                max_fails=server_data.get('max_fails', 3),
                fail_timeout=server_data.get('fail_timeout', 30),
                status='active',
                added_by=server_data.get('admin_id'),
                added_at=datetime.utcnow()
            )
            
            db.add(server)
            db.commit()
            db.refresh(server)
            
            # Update nginx configuration
            await self._update_nginx_config(db)
            
            # Register with service discovery (if enabled)
            if self.consul_enabled:
                await self._register_with_consul(server)
            
            logger.info(f"Server {server.hostname} added successfully")
            
            return {
                "success": True,
                "message": f"Server {server.hostname} added successfully",
                "server_id": server.id,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error adding server: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def remove_server(self, db: Session, server_id: int, admin_id: int) -> Dict:
        """Remove a server from the load balancer pool"""
        try:
            server = db.query(Server).filter(Server.id == server_id).first()
            if not server:
                raise HTTPException(status_code=404, detail="Server not found")
            
            # Mark server as inactive (soft delete)
            server.status = 'inactive'
            server.removed_by = admin_id
            server.removed_at = datetime.utcnow()
            
            db.commit()
            
            # Update nginx configuration
            await self._update_nginx_config(db)
            
            # Deregister from service discovery
            if self.consul_enabled:
                await self._deregister_from_consul(server)
            
            logger.info(f"Server {server.hostname} removed successfully")
            
            return {
                "success": True,
                "message": f"Server {server.hostname} removed successfully",
                "server_id": server.id,
                "status": "inactive"
            }
            
        except Exception as e:
            logger.error(f"Error removing server: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update_server_weight(self, db: Session, server_id: int, weight: int) -> Dict:
        """Update server weight for load balancing"""
        try:
            server = db.query(Server).filter(
                Server.id == server_id,
                Server.status == 'active'
            ).first()
            
            if not server:
                raise HTTPException(status_code=404, detail="Active server not found")
            
            server.weight = weight
            server.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Update nginx configuration
            await self._update_nginx_config(db)
            
            return {
                "success": True,
                "message": f"Server {server.hostname} weight updated to {weight}",
                "server_id": server.id,
                "new_weight": weight
            }
            
        except Exception as e:
            logger.error(f"Error updating server weight: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_server_status(self, db: Session) -> Dict:
        """Get status of all servers in the load balancer pool"""
        try:
            servers = db.query(Server).filter(Server.status == 'active').all()
            
            server_status = []
            for server in servers:
                # Perform health check
                is_healthy = await self._health_check_server(server.ip_address, server.port)
                
                server_status.append({
                    "id": server.id,
                    "hostname": server.hostname,
                    "ip_address": server.ip_address,
                    "port": server.port,
                    "server_type": server.server_type,
                    "weight": server.weight,
                    "status": "healthy" if is_healthy else "unhealthy",
                    "added_at": server.added_at.isoformat(),
                    "last_checked": datetime.utcnow().isoformat()
                })
            
            return {
                "success": True,
                "total_servers": len(servers),
                "healthy_servers": len([s for s in server_status if s["status"] == "healthy"]),
                "servers": server_status
            }
            
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _update_nginx_config(self, db: Session):
        """Update nginx upstream configuration"""
        try:
            # Get active servers by type
            backend_servers = db.query(Server).filter(
                Server.status == 'active',
                Server.server_type == 'backend'
            ).all()
            
            frontend_servers = db.query(Server).filter(
                Server.status == 'active',
                Server.server_type == 'frontend'
            ).all()
            
            # Generate nginx upstream configuration
            config_content = self._generate_nginx_upstream_config(backend_servers, frontend_servers)
            
            # Write configuration to file
            with open(self.nginx_config_path, 'w') as f:
                f.write(config_content)
            
            # Reload nginx configuration
            await self._reload_nginx()
            
            logger.info("Nginx configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating nginx config: {e}")
            raise
    
    def _generate_nginx_upstream_config(self, backend_servers: List, frontend_servers: List) -> str:
        """Generate nginx upstream configuration"""
        config = """
# Auto-generated upstream configuration
# DO NOT EDIT MANUALLY - Managed by LoadBalancerService

upstream backend_pool {
    least_conn;
    
"""
        
        # Add backend servers
        for server in backend_servers:
            config += f"    server {server.ip_address}:{server.port} "
            config += f"max_fails={server.max_fails} "
            config += f"fail_timeout={server.fail_timeout}s "
            config += f"weight={server.weight};\n"
        
        # Fallback if no backend servers
        if not backend_servers:
            config += "    server 127.0.0.1:8000 backup;\n"
        
        config += """
    keepalive 32;
    keepalive_requests 100;
    keepalive_timeout 60s;
}

upstream frontend_pool {
    least_conn;
    
"""
        
        # Add frontend servers
        for server in frontend_servers:
            config += f"    server {server.ip_address}:{server.port} "
            config += f"max_fails={server.max_fails} "
            config += f"fail_timeout={server.fail_timeout}s "
            config += f"weight={server.weight};\n"
        
        # Fallback if no frontend servers
        if not frontend_servers:
            config += "    server 127.0.0.1:3000 backup;\n"
        
        config += """
    keepalive 16;
    keepalive_requests 100;
    keepalive_timeout 60s;
}

# Health check endpoints
upstream health_check {
    server 127.0.0.1:8000;
}
"""
        
        return config
    
    async def _reload_nginx(self):
        """Reload nginx configuration"""
        try:
            # Test configuration first
            result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Nginx configuration test failed: {result.stderr}")
            
            # Reload nginx
            result = subprocess.run(['nginx', '-s', 'reload'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Nginx reload failed: {result.stderr}")
            
            logger.info("Nginx reloaded successfully")
            
        except Exception as e:
            logger.error(f"Error reloading nginx: {e}")
            raise
    
    async def _health_check_server(self, ip_address: str, port: int) -> bool:
        """Perform health check on a server"""
        try:
            import aiohttp
            import asyncio
            
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://{ip_address}:{port}/health") as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.warning(f"Health check failed for {ip_address}:{port} - {e}")
            return False
    
    async def _register_with_consul(self, server):
        """Register server with Consul service discovery"""
        try:
            import aiohttp
            
            service_data = {
                "ID": f"{server.server_type}-{server.hostname}",
                "Name": f"medhasakthi-{server.server_type}",
                "Tags": [server.server_type, "medhasakthi"],
                "Address": server.ip_address,
                "Port": server.port,
                "Check": {
                    "HTTP": f"http://{server.ip_address}:{server.port}/health",
                    "Interval": "30s",
                    "Timeout": "5s"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.consul_url}/v1/agent/service/register",
                    json=service_data
                ) as response:
                    if response.status == 200:
                        logger.info(f"Server {server.hostname} registered with Consul")
                    else:
                        logger.error(f"Failed to register with Consul: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error registering with Consul: {e}")
    
    async def _deregister_from_consul(self, server):
        """Deregister server from Consul service discovery"""
        try:
            import aiohttp
            
            service_id = f"{server.server_type}-{server.hostname}"
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.consul_url}/v1/agent/service/deregister/{service_id}"
                ) as response:
                    if response.status == 200:
                        logger.info(f"Server {server.hostname} deregistered from Consul")
                    else:
                        logger.error(f"Failed to deregister from Consul: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error deregistering from Consul: {e}")

# Global service instance
load_balancer_service = LoadBalancerService()
