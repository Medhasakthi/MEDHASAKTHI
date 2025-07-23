"""
Server Model for Dynamic Load Balancing
Stores information about servers in the load balancer pool
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class Server(Base):
    """Server model for load balancer management"""
    
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)  # Supports IPv4 and IPv6
    port = Column(Integer, nullable=False)
    server_type = Column(String(50), nullable=False, index=True)  # 'backend', 'frontend', 'database'
    
    # Load balancing configuration
    weight = Column(Integer, default=1)
    max_fails = Column(Integer, default=3)
    fail_timeout = Column(Integer, default=30)  # seconds
    
    # Status and metadata
    status = Column(String(20), default='active', index=True)  # 'active', 'inactive', 'maintenance'
    region = Column(String(50), nullable=True)
    availability_zone = Column(String(50), nullable=True)
    instance_type = Column(String(50), nullable=True)
    
    # Resource specifications
    cpu_cores = Column(Integer, nullable=True)
    memory_gb = Column(Integer, nullable=True)
    storage_gb = Column(Integer, nullable=True)
    
    # Health check configuration
    health_check_path = Column(String(255), default='/health')
    health_check_interval = Column(Integer, default=30)  # seconds
    health_check_timeout = Column(Integer, default=5)   # seconds
    
    # SSL/TLS configuration
    ssl_enabled = Column(Boolean, default=False)
    ssl_cert_path = Column(String(500), nullable=True)
    ssl_key_path = Column(String(500), nullable=True)
    
    # Monitoring and metrics
    last_health_check = Column(DateTime, nullable=True)
    health_status = Column(String(20), default='unknown')  # 'healthy', 'unhealthy', 'unknown'
    response_time_ms = Column(Integer, nullable=True)
    error_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    
    # Audit fields
    added_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    removed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    removed_at = Column(DateTime, nullable=True)
    
    # Configuration and notes
    configuration = Column(Text, nullable=True)  # JSON configuration
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Relationships
    added_by_user = relationship("User", foreign_keys=[added_by], back_populates="added_servers")
    removed_by_user = relationship("User", foreign_keys=[removed_by], back_populates="removed_servers")
    
    def __repr__(self):
        return f"<Server(hostname='{self.hostname}', ip='{self.ip_address}', type='{self.server_type}', status='{self.status}')>"
    
    @property
    def endpoint(self):
        """Get the full endpoint URL"""
        protocol = "https" if self.ssl_enabled else "http"
        return f"{protocol}://{self.ip_address}:{self.port}"
    
    @property
    def health_check_url(self):
        """Get the health check URL"""
        return f"{self.endpoint}{self.health_check_path}"
    
    def to_dict(self):
        """Convert server to dictionary"""
        return {
            "id": self.id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "port": self.port,
            "server_type": self.server_type,
            "weight": self.weight,
            "max_fails": self.max_fails,
            "fail_timeout": self.fail_timeout,
            "status": self.status,
            "region": self.region,
            "availability_zone": self.availability_zone,
            "instance_type": self.instance_type,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "storage_gb": self.storage_gb,
            "health_status": self.health_status,
            "response_time_ms": self.response_time_ms,
            "endpoint": self.endpoint,
            "health_check_url": self.health_check_url,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "tags": self.tags.split(',') if self.tags else []
        }
    
    def update_health_status(self, is_healthy: bool, response_time_ms: int = None):
        """Update health status and metrics"""
        self.last_health_check = datetime.utcnow()
        self.health_status = 'healthy' if is_healthy else 'unhealthy'
        
        if response_time_ms is not None:
            self.response_time_ms = response_time_ms
        
        if is_healthy:
            self.success_count += 1
        else:
            self.error_count += 1
        
        self.updated_at = datetime.utcnow()


class ServerMetrics(Base):
    """Server metrics for monitoring and analytics"""
    
    __tablename__ = "server_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Performance metrics
    cpu_usage_percent = Column(Integer, nullable=True)
    memory_usage_percent = Column(Integer, nullable=True)
    disk_usage_percent = Column(Integer, nullable=True)
    network_in_mbps = Column(Integer, nullable=True)
    network_out_mbps = Column(Integer, nullable=True)
    
    # Application metrics
    active_connections = Column(Integer, nullable=True)
    requests_per_second = Column(Integer, nullable=True)
    response_time_avg_ms = Column(Integer, nullable=True)
    error_rate_percent = Column(Integer, nullable=True)
    
    # Load balancer metrics
    requests_handled = Column(Integer, default=0)
    bytes_transferred = Column(Integer, default=0)
    
    # Relationship
    server = relationship("Server", back_populates="metrics")
    
    def __repr__(self):
        return f"<ServerMetrics(server_id={self.server_id}, recorded_at='{self.recorded_at}')>"


class LoadBalancerConfig(Base):
    """Load balancer configuration settings"""
    
    __tablename__ = "load_balancer_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configuration name and description
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Load balancing algorithm
    algorithm = Column(String(50), default='least_conn')  # 'round_robin', 'least_conn', 'ip_hash', 'weighted'
    
    # Health check settings
    health_check_enabled = Column(Boolean, default=True)
    health_check_interval = Column(Integer, default=30)
    health_check_timeout = Column(Integer, default=5)
    health_check_retries = Column(Integer, default=3)
    
    # Session persistence
    session_persistence = Column(Boolean, default=False)
    session_timeout = Column(Integer, default=3600)  # seconds
    
    # SSL/TLS settings
    ssl_termination = Column(Boolean, default=True)
    ssl_redirect = Column(Boolean, default=True)
    
    # Rate limiting
    rate_limit_enabled = Column(Boolean, default=True)
    rate_limit_requests = Column(Integer, default=100)
    rate_limit_window = Column(Integer, default=60)  # seconds
    
    # Timeouts
    connect_timeout = Column(Integer, default=5)
    send_timeout = Column(Integer, default=60)
    read_timeout = Column(Integer, default=60)
    
    # Active configuration
    is_active = Column(Boolean, default=False)
    
    # Audit fields
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    created_by_user = relationship("User", back_populates="load_balancer_configs")
    
    def __repr__(self):
        return f"<LoadBalancerConfig(name='{self.name}', algorithm='{self.algorithm}', active={self.is_active})>"


# Add relationships to User model (to be added to user.py)
"""
Add these to the User model:

added_servers = relationship("Server", foreign_keys="Server.added_by", back_populates="added_by_user")
removed_servers = relationship("Server", foreign_keys="Server.removed_by", back_populates="removed_by_user")
load_balancer_configs = relationship("LoadBalancerConfig", back_populates="created_by_user")
"""

class ServerMetrics(Base):
    """Server performance metrics for monitoring and auto-scaling"""

    __tablename__ = "server_metrics"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Performance metrics
    cpu_usage_percent = Column(Integer, nullable=True)
    memory_usage_percent = Column(Integer, nullable=True)
    disk_usage_percent = Column(Integer, nullable=True)
    network_in_mbps = Column(Integer, nullable=True)
    network_out_mbps = Column(Integer, nullable=True)

    # Application metrics
    active_connections = Column(Integer, nullable=True)
    requests_per_second = Column(Integer, nullable=True)
    response_time_avg_ms = Column(Integer, nullable=True)
    error_rate_percent = Column(Integer, nullable=True)

    # Traffic metrics
    requests_handled = Column(Integer, default=0)
    bytes_transferred = Column(Integer, default=0)

    # Relationship
    server = relationship("Server", back_populates="metrics")

    def __repr__(self):
        return f"<ServerMetrics(server_id={self.server_id}, recorded_at={self.recorded_at})>"


# Add relationship to Server model
Server.metrics = relationship("ServerMetrics", back_populates="server", cascade="all, delete-orphan")
