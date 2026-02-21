"""
Load Balancer Management API Endpoints
Super admin endpoints for managing dynamic load balancing
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_super_admin
from app.services.load_balancer_service import load_balancer_service
from app.models.server import Server, LoadBalancerConfig
from app.models.user import User

router = APIRouter()

# Pydantic models for request/response
class ServerCreate(BaseModel):
    hostname: str = Field(..., description="Server hostname")
    ip_address: str = Field(..., description="Server IP address")
    port: int = Field(..., description="Server port", ge=1, le=65535)
    server_type: str = Field(..., description="Server type: backend, frontend, database")
    weight: int = Field(1, description="Load balancing weight", ge=1, le=100)
    max_fails: int = Field(3, description="Maximum failures before marking unhealthy", ge=1, le=10)
    fail_timeout: int = Field(30, description="Timeout in seconds", ge=5, le=300)
    region: str = Field(None, description="Server region")
    availability_zone: str = Field(None, description="Availability zone")
    instance_type: str = Field(None, description="Instance type")
    cpu_cores: int = Field(None, description="CPU cores", ge=1)
    memory_gb: int = Field(None, description="Memory in GB", ge=1)
    storage_gb: int = Field(None, description="Storage in GB", ge=1)
    ssl_enabled: bool = Field(False, description="SSL enabled")
    notes: str = Field(None, description="Additional notes")
    tags: str = Field(None, description="Comma-separated tags")

class ServerUpdate(BaseModel):
    weight: int = Field(None, description="Load balancing weight", ge=1, le=100)
    max_fails: int = Field(None, description="Maximum failures", ge=1, le=10)
    fail_timeout: int = Field(None, description="Timeout in seconds", ge=5, le=300)
    status: str = Field(None, description="Server status: active, inactive, maintenance")
    notes: str = Field(None, description="Additional notes")
    tags: str = Field(None, description="Comma-separated tags")

class LoadBalancerConfigCreate(BaseModel):
    name: str = Field(..., description="Configuration name")
    description: str = Field(None, description="Configuration description")
    algorithm: str = Field("least_conn", description="Load balancing algorithm")
    health_check_interval: int = Field(30, description="Health check interval in seconds")
    health_check_timeout: int = Field(5, description="Health check timeout in seconds")
    rate_limit_requests: int = Field(100, description="Rate limit requests per window")
    rate_limit_window: int = Field(60, description="Rate limit window in seconds")
    connect_timeout: int = Field(5, description="Connect timeout in seconds")
    send_timeout: int = Field(60, description="Send timeout in seconds")
    read_timeout: int = Field(60, description="Read timeout in seconds")

@router.post("/servers", response_model=Dict[str, Any])
async def add_server(
    server_data: ServerCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Add a new server to the load balancer pool"""
    
    # Convert Pydantic model to dict and add admin info
    server_dict = server_data.dict()
    server_dict['admin_id'] = current_admin.id
    
    # Validate server type
    valid_types = ['backend', 'frontend', 'database']
    if server_dict['server_type'] not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid server type. Must be one of: {', '.join(valid_types)}"
        )
    
    result = await load_balancer_service.add_server(db, server_dict)
    return result

@router.delete("/servers/{server_id}", response_model=Dict[str, Any])
async def remove_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Remove a server from the load balancer pool"""
    
    result = await load_balancer_service.remove_server(db, server_id, current_admin.id)
    return result

@router.put("/servers/{server_id}/weight", response_model=Dict[str, Any])
async def update_server_weight(
    server_id: int,
    weight: int = Field(..., description="New weight value", ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Update server weight for load balancing"""
    
    result = await load_balancer_service.update_server_weight(db, server_id, weight)
    return result

@router.patch("/servers/{server_id}", response_model=Dict[str, Any])
async def update_server(
    server_id: int,
    server_update: ServerUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Update server configuration"""
    
    try:
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        
        # Update only provided fields
        update_data = server_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(server, field, value)
        
        db.commit()
        db.refresh(server)
        
        # Update nginx configuration if weight or status changed
        if 'weight' in update_data or 'status' in update_data:
            await load_balancer_service._update_nginx_config(db)
        
        return {
            "success": True,
            "message": f"Server {server.hostname} updated successfully",
            "server": server.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/servers", response_model=Dict[str, Any])
async def get_servers(
    server_type: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Get list of all servers with optional filtering"""
    
    query = db.query(Server)
    
    if server_type:
        query = query.filter(Server.server_type == server_type)
    
    if status:
        query = query.filter(Server.status == status)
    
    servers = query.all()
    
    return {
        "success": True,
        "total_servers": len(servers),
        "servers": [server.to_dict() for server in servers]
    }

@router.get("/servers/{server_id}", response_model=Dict[str, Any])
async def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Get detailed information about a specific server"""
    
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return {
        "success": True,
        "server": server.to_dict()
    }

@router.get("/status", response_model=Dict[str, Any])
async def get_load_balancer_status(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Get overall load balancer status and health"""
    
    result = await load_balancer_service.get_server_status(db)
    return result

@router.post("/health-check", response_model=Dict[str, Any])
async def trigger_health_check(
    server_id: int = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Trigger manual health check for specific server or all servers"""
    
    try:
        if server_id:
            # Health check specific server
            server = db.query(Server).filter(
                Server.id == server_id,
                Server.status == 'active'
            ).first()
            
            if not server:
                raise HTTPException(status_code=404, detail="Active server not found")
            
            is_healthy = await load_balancer_service._health_check_server(
                server.ip_address, 
                server.port
            )
            
            server.update_health_status(is_healthy)
            db.commit()
            
            return {
                "success": True,
                "message": f"Health check completed for {server.hostname}",
                "server_id": server.id,
                "health_status": server.health_status
            }
        else:
            # Health check all active servers
            servers = db.query(Server).filter(Server.status == 'active').all()
            results = []
            
            for server in servers:
                is_healthy = await load_balancer_service._health_check_server(
                    server.ip_address, 
                    server.port
                )
                
                server.update_health_status(is_healthy)
                results.append({
                    "server_id": server.id,
                    "hostname": server.hostname,
                    "health_status": server.health_status
                })
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Health check completed for {len(servers)} servers",
                "results": results
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload-config", response_model=Dict[str, Any])
async def reload_nginx_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Manually reload nginx configuration"""
    
    try:
        await load_balancer_service._update_nginx_config(db)
        
        return {
            "success": True,
            "message": "Nginx configuration reloaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config", response_model=Dict[str, Any])
async def get_load_balancer_config(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Get current load balancer configuration"""
    
    config = db.query(LoadBalancerConfig).filter(
        LoadBalancerConfig.is_active == True
    ).first()
    
    if not config:
        # Return default configuration
        return {
            "success": True,
            "config": {
                "name": "default",
                "algorithm": "least_conn",
                "health_check_interval": 30,
                "health_check_timeout": 5,
                "rate_limit_requests": 100,
                "rate_limit_window": 60
            }
        }
    
    return {
        "success": True,
        "config": {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "algorithm": config.algorithm,
            "health_check_interval": config.health_check_interval,
            "health_check_timeout": config.health_check_timeout,
            "rate_limit_requests": config.rate_limit_requests,
            "rate_limit_window": config.rate_limit_window,
            "connect_timeout": config.connect_timeout,
            "send_timeout": config.send_timeout,
            "read_timeout": config.read_timeout,
            "created_at": config.created_at.isoformat(),
            "updated_at": config.updated_at.isoformat()
        }
    }

@router.post("/config", response_model=Dict[str, Any])
async def create_load_balancer_config(
    config_data: LoadBalancerConfigCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_super_admin)
):
    """Create new load balancer configuration"""
    
    try:
        # Deactivate current active config
        current_config = db.query(LoadBalancerConfig).filter(
            LoadBalancerConfig.is_active == True
        ).first()
        
        if current_config:
            current_config.is_active = False
        
        # Create new config
        new_config = LoadBalancerConfig(
            **config_data.dict(),
            created_by=current_admin.id,
            is_active=True
        )
        
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
        # Update nginx configuration
        await load_balancer_service._update_nginx_config(db)
        
        return {
            "success": True,
            "message": f"Load balancer configuration '{new_config.name}' created and activated",
            "config_id": new_config.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
