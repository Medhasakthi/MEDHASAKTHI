"""
Auto-Scaling Service for MEDHASAKTHI
Automatically provisions and deprovisions servers based on load metrics
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.server import Server, ServerMetrics
from app.core.config import settings

logger = logging.getLogger(__name__)

class AutoScalingService:
    """Service for automatic server scaling based on metrics"""
    
    def __init__(self):
        self.scaling_enabled = getattr(settings, 'AUTO_SCALING_ENABLED', False)
        self.min_servers = getattr(settings, 'MIN_SERVERS', 1)
        self.max_servers = getattr(settings, 'MAX_SERVERS', 10)
        self.scale_up_threshold = getattr(settings, 'SCALE_UP_CPU_THRESHOLD', 70)
        self.scale_down_threshold = getattr(settings, 'SCALE_DOWN_CPU_THRESHOLD', 30)
        self.scale_up_duration = getattr(settings, 'SCALE_UP_DURATION_MINUTES', 5)
        self.scale_down_duration = getattr(settings, 'SCALE_DOWN_DURATION_MINUTES', 15)
        self.cloud_provider = getattr(settings, 'CLOUD_PROVIDER', 'aws')  # aws, digitalocean, gcp
        
        # Cloud provider configurations
        self.aws_config = {
            'region': getattr(settings, 'AWS_REGION', 'ap-south-1'),
            'instance_type': getattr(settings, 'AWS_INSTANCE_TYPE', 't3.large'),
            'ami_id': getattr(settings, 'AWS_AMI_ID', 'ami-0c02fb55956c7d316'),
            'key_name': getattr(settings, 'AWS_KEY_NAME', 'medhasakthi-key'),
            'security_group': getattr(settings, 'AWS_SECURITY_GROUP', 'medhasakthi-sg')
        }
        
        self.do_config = {
            'region': getattr(settings, 'DO_REGION', 'blr1'),
            'size': getattr(settings, 'DO_DROPLET_SIZE', 's-2vcpu-4gb'),
            'image': getattr(settings, 'DO_IMAGE', 'ubuntu-20-04-x64'),
            'ssh_keys': getattr(settings, 'DO_SSH_KEYS', [])
        }
    
    async def monitor_and_scale(self, db: Session) -> Dict:
        """Main monitoring and scaling function"""
        if not self.scaling_enabled:
            return {"message": "Auto-scaling is disabled"}
        
        try:
            # Get current server metrics
            metrics = await self._get_current_metrics(db)
            
            # Analyze scaling needs
            scaling_decision = await self._analyze_scaling_needs(db, metrics)
            
            # Execute scaling actions
            if scaling_decision['action'] == 'scale_up':
                result = await self._scale_up(db, scaling_decision['count'])
            elif scaling_decision['action'] == 'scale_down':
                result = await self._scale_down(db, scaling_decision['servers'])
            else:
                result = {"action": "no_action", "message": "No scaling needed"}
            
            # Log scaling activity
            await self._log_scaling_activity(db, scaling_decision, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in auto-scaling monitor: {e}")
            return {"error": str(e)}
    
    async def _get_current_metrics(self, db: Session) -> Dict:
        """Get current server metrics for scaling decisions"""
        try:
            # Get active backend servers
            servers = db.query(Server).filter(
                Server.status == 'active',
                Server.server_type == 'backend'
            ).all()
            
            if not servers:
                return {"servers": [], "avg_cpu": 0, "avg_memory": 0, "total_rps": 0}
            
            # Calculate aggregate metrics
            total_cpu = 0
            total_memory = 0
            total_rps = 0
            healthy_servers = 0
            
            for server in servers:
                # Get latest metrics (mock data for now)
                cpu_usage = await self._get_server_cpu_usage(server)
                memory_usage = await self._get_server_memory_usage(server)
                rps = await self._get_server_rps(server)
                
                if server.health_status == 'healthy':
                    total_cpu += cpu_usage
                    total_memory += memory_usage
                    total_rps += rps
                    healthy_servers += 1
            
            avg_cpu = total_cpu / healthy_servers if healthy_servers > 0 else 0
            avg_memory = total_memory / healthy_servers if healthy_servers > 0 else 0
            
            return {
                "servers": servers,
                "healthy_servers": healthy_servers,
                "total_servers": len(servers),
                "avg_cpu": avg_cpu,
                "avg_memory": avg_memory,
                "total_rps": total_rps
            }
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {"servers": [], "avg_cpu": 0, "avg_memory": 0, "total_rps": 0}
    
    async def _analyze_scaling_needs(self, db: Session, metrics: Dict) -> Dict:
        """Analyze if scaling is needed based on metrics"""
        try:
            current_servers = metrics.get('total_servers', 0)
            healthy_servers = metrics.get('healthy_servers', 0)
            avg_cpu = metrics.get('avg_cpu', 0)
            avg_memory = metrics.get('avg_memory', 0)
            
            # Check if we need to scale up
            if (avg_cpu > self.scale_up_threshold or avg_memory > 80) and current_servers < self.max_servers:
                # Check if high load has been sustained
                if await self._is_high_load_sustained(db, self.scale_up_duration):
                    scale_count = min(2, self.max_servers - current_servers)  # Scale up by 1-2 servers
                    return {
                        "action": "scale_up",
                        "count": scale_count,
                        "reason": f"High CPU ({avg_cpu:.1f}%) or memory usage",
                        "current_servers": current_servers
                    }
            
            # Check if we need to scale down
            elif avg_cpu < self.scale_down_threshold and avg_memory < 50 and current_servers > self.min_servers:
                # Check if low load has been sustained
                if await self._is_low_load_sustained(db, self.scale_down_duration):
                    # Identify servers to remove (prefer newest, least loaded)
                    servers_to_remove = await self._select_servers_for_removal(db, 1)
                    return {
                        "action": "scale_down",
                        "servers": servers_to_remove,
                        "reason": f"Low CPU ({avg_cpu:.1f}%) usage",
                        "current_servers": current_servers
                    }
            
            return {
                "action": "no_action",
                "reason": f"Metrics within normal range (CPU: {avg_cpu:.1f}%)",
                "current_servers": current_servers
            }
            
        except Exception as e:
            logger.error(f"Error analyzing scaling needs: {e}")
            return {"action": "no_action", "reason": f"Analysis error: {e}"}
    
    async def _scale_up(self, db: Session, count: int) -> Dict:
        """Scale up by adding new servers"""
        try:
            results = []
            
            for i in range(count):
                # Provision new server based on cloud provider
                if self.cloud_provider == 'aws':
                    server_info = await self._provision_aws_instance()
                elif self.cloud_provider == 'digitalocean':
                    server_info = await self._provision_do_droplet()
                else:
                    raise Exception(f"Unsupported cloud provider: {self.cloud_provider}")
                
                if server_info:
                    # Add server to load balancer
                    server_data = {
                        'hostname': server_info['hostname'],
                        'ip_address': server_info['ip_address'],
                        'port': 8000,
                        'server_type': 'backend',
                        'weight': 1,
                        'region': server_info.get('region'),
                        'instance_type': server_info.get('instance_type'),
                        'cpu_cores': server_info.get('cpu_cores', 2),
                        'memory_gb': server_info.get('memory_gb', 4),
                        'notes': 'Auto-provisioned by scaling service',
                        'admin_id': 1  # System admin
                    }
                    
                    # Import here to avoid circular import
                    from app.services.load_balancer_service import load_balancer_service
                    result = await load_balancer_service.add_server(db, server_data)
                    results.append(result)
                    
                    logger.info(f"Auto-scaled up: Added server {server_info['hostname']}")
            
            return {
                "action": "scale_up",
                "servers_added": len(results),
                "results": results,
                "message": f"Successfully scaled up by {len(results)} servers"
            }
            
        except Exception as e:
            logger.error(f"Error scaling up: {e}")
            return {"action": "scale_up", "error": str(e)}
    
    async def _scale_down(self, db: Session, servers_to_remove: List[Server]) -> Dict:
        """Scale down by removing servers"""
        try:
            results = []
            
            for server in servers_to_remove:
                # Gracefully drain connections first
                await self._drain_server_connections(server)
                
                # Remove from load balancer
                # Import here to avoid circular import
                from app.services.load_balancer_service import load_balancer_service
                result = await load_balancer_service.remove_server(db, server.id, 1)  # System admin
                results.append(result)
                
                # Terminate cloud instance
                if self.cloud_provider == 'aws':
                    await self._terminate_aws_instance(server)
                elif self.cloud_provider == 'digitalocean':
                    await self._terminate_do_droplet(server)
                
                logger.info(f"Auto-scaled down: Removed server {server.hostname}")
            
            return {
                "action": "scale_down",
                "servers_removed": len(results),
                "results": results,
                "message": f"Successfully scaled down by {len(results)} servers"
            }
            
        except Exception as e:
            logger.error(f"Error scaling down: {e}")
            return {"action": "scale_down", "error": str(e)}
    
    async def _provision_aws_instance(self) -> Optional[Dict]:
        """Provision new AWS EC2 instance"""
        try:
            import boto3
            
            ec2 = boto3.client('ec2', region_name=self.aws_config['region'])
            
            # User data script to setup MEDHASAKTHI
            user_data = """#!/bin/bash
            # Install Docker and dependencies
            apt-get update
            apt-get install -y docker.io docker-compose git
            systemctl start docker
            systemctl enable docker
            
            # Clone and deploy MEDHASAKTHI
            cd /opt
            git clone https://github.com/your-org/medhasakthi.git
            cd medhasakthi
            
            # Deploy backend only
            docker-compose -f docker-compose.backend-only.yml up -d
            """
            
            response = ec2.run_instances(
                ImageId=self.aws_config['ami_id'],
                MinCount=1,
                MaxCount=1,
                InstanceType=self.aws_config['instance_type'],
                KeyName=self.aws_config['key_name'],
                SecurityGroups=[self.aws_config['security_group']],
                UserData=user_data,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'medhasakthi-auto-{datetime.now().strftime("%Y%m%d-%H%M%S")}'},
                            {'Key': 'Project', 'Value': 'MEDHASAKTHI'},
                            {'Key': 'AutoScaled', 'Value': 'true'}
                        ]
                    }
                ]
            )
            
            instance = response['Instances'][0]
            instance_id = instance['InstanceId']
            
            # Wait for instance to be running
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id])
            
            # Get instance details
            instances = ec2.describe_instances(InstanceIds=[instance_id])
            instance_info = instances['Reservations'][0]['Instances'][0]
            
            return {
                'hostname': f"medhasakthi-auto-{instance_id}",
                'ip_address': instance_info['PrivateIpAddress'],
                'public_ip': instance_info.get('PublicIpAddress'),
                'instance_id': instance_id,
                'region': self.aws_config['region'],
                'instance_type': self.aws_config['instance_type'],
                'cpu_cores': 2,  # Based on t3.large
                'memory_gb': 8
            }
            
        except Exception as e:
            logger.error(f"Error provisioning AWS instance: {e}")
            return None
    
    async def _provision_do_droplet(self) -> Optional[Dict]:
        """Provision new DigitalOcean droplet"""
        try:
            import digitalocean
            
            manager = digitalocean.Manager(token=getattr(settings, 'DO_API_TOKEN'))
            
            # User data script
            user_data = """#!/bin/bash
            # Install Docker and dependencies
            apt-get update
            apt-get install -y docker.io docker-compose git
            systemctl start docker
            systemctl enable docker
            
            # Clone and deploy MEDHASAKTHI
            cd /opt
            git clone https://github.com/your-org/medhasakthi.git
            cd medhasakthi
            
            # Deploy backend only
            docker-compose -f docker-compose.backend-only.yml up -d
            """
            
            droplet = digitalocean.Droplet(
                token=manager.token,
                name=f"medhasakthi-auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                region=self.do_config['region'],
                image=self.do_config['image'],
                size_slug=self.do_config['size'],
                ssh_keys=self.do_config['ssh_keys'],
                user_data=user_data,
                tags=['medhasakthi', 'auto-scaled']
            )
            
            droplet.create()
            
            # Wait for droplet to be active
            actions = droplet.get_actions()
            for action in actions:
                action.wait()
            
            return {
                'hostname': droplet.name,
                'ip_address': droplet.private_ip_address,
                'public_ip': droplet.ip_address,
                'droplet_id': droplet.id,
                'region': self.do_config['region'],
                'instance_type': self.do_config['size'],
                'cpu_cores': 2,
                'memory_gb': 4
            }
            
        except Exception as e:
            logger.error(f"Error provisioning DO droplet: {e}")
            return None
    
    async def _get_server_cpu_usage(self, server: Server) -> float:
        """Get server CPU usage (mock implementation)"""
        # In real implementation, this would query monitoring system
        import random
        return random.uniform(20, 90)
    
    async def _get_server_memory_usage(self, server: Server) -> float:
        """Get server memory usage (mock implementation)"""
        import random
        return random.uniform(30, 80)
    
    async def _get_server_rps(self, server: Server) -> int:
        """Get server requests per second (mock implementation)"""
        import random
        return random.randint(10, 100)
    
    async def _is_high_load_sustained(self, db: Session, duration_minutes: int) -> bool:
        """Check if high load has been sustained for specified duration"""
        # Mock implementation - in real scenario, check historical metrics
        return True  # For demo purposes
    
    async def _is_low_load_sustained(self, db: Session, duration_minutes: int) -> bool:
        """Check if low load has been sustained for specified duration"""
        # Mock implementation
        return True  # For demo purposes
    
    async def _select_servers_for_removal(self, db: Session, count: int) -> List[Server]:
        """Select servers for removal (prefer newest, least loaded)"""
        servers = db.query(Server).filter(
            Server.status == 'active',
            Server.server_type == 'backend'
        ).order_by(Server.added_at.desc()).limit(count).all()
        
        return servers
    
    async def _drain_server_connections(self, server: Server):
        """Gracefully drain connections from server"""
        # Implementation would mark server as draining in load balancer
        # and wait for existing connections to complete
        await asyncio.sleep(30)  # Mock drain time
    
    async def _terminate_aws_instance(self, server: Server):
        """Terminate AWS EC2 instance"""
        try:
            import boto3
            ec2 = boto3.client('ec2', region_name=self.aws_config['region'])
            
            # Extract instance ID from server configuration
            instance_id = server.configuration.get('instance_id') if server.configuration else None
            if instance_id:
                ec2.terminate_instances(InstanceIds=[instance_id])
                logger.info(f"Terminated AWS instance {instance_id}")
        except Exception as e:
            logger.error(f"Error terminating AWS instance: {e}")
    
    async def _terminate_do_droplet(self, server: Server):
        """Terminate DigitalOcean droplet"""
        try:
            import digitalocean
            manager = digitalocean.Manager(token=getattr(settings, 'DO_API_TOKEN'))
            
            # Extract droplet ID from server configuration
            droplet_id = server.configuration.get('droplet_id') if server.configuration else None
            if droplet_id:
                droplet = manager.get_droplet(droplet_id)
                droplet.destroy()
                logger.info(f"Terminated DO droplet {droplet_id}")
        except Exception as e:
            logger.error(f"Error terminating DO droplet: {e}")
    
    async def _log_scaling_activity(self, db: Session, decision: Dict, result: Dict):
        """Log scaling activity for audit purposes"""
        try:
            # In real implementation, this would log to a scaling_events table
            logger.info(f"Scaling activity: {decision} -> {result}")
        except Exception as e:
            logger.error(f"Error logging scaling activity: {e}")

# Global service instance
auto_scaling_service = AutoScalingService()
