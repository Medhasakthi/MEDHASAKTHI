"""
WebSocket Manager for Real-time Features in MEDHASAKTHI
Handles real-time notifications, live exam monitoring, and collaborative features
"""
import json
import asyncio
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import redis
import logging

from app.core.config import settings
from app.models.user import User
from app.models.talent_exam import TalentExamSession

# WebSocket logger
ws_logger = logging.getLogger("websocket")
ws_logger.setLevel(logging.INFO)

# Redis for WebSocket message broadcasting
ws_redis = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_WEBSOCKET_DB,
    decode_responses=True
)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        # Room-based connections (for group features)
        self.rooms: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_type: str = "general"):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connection_type": connection_type,
            "connected_at": datetime.now(),
            "last_activity": datetime.now()
        }
        
        ws_logger.info(f"User {user_id} connected via WebSocket ({connection_type})")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket connection established",
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            user_id = metadata["user_id"]
            
            # Remove from user connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from rooms
            for room_connections in self.rooms.values():
                room_connections.discard(websocket)
            
            # Remove metadata
            del self.connection_metadata[websocket]
            
            ws_logger.info(f"User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
            # Update last activity
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["last_activity"] = datetime.now()
        except Exception as e:
            ws_logger.error(f"Error sending personal message: {e}")
    
    async def send_user_message(self, message: Dict[str, Any], user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected_connections = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    ws_logger.error(f"Error sending user message: {e}")
                    disconnected_connections.add(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                self.disconnect(websocket)
    
    async def join_room(self, websocket: WebSocket, room_id: str):
        """Add connection to a room for group messaging"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(websocket)
        
        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["room_id"] = room_id
        
        ws_logger.info(f"Connection joined room: {room_id}")
    
    async def leave_room(self, websocket: WebSocket, room_id: str):
        """Remove connection from a room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(websocket)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
        
        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket].pop("room_id", None)
        
        ws_logger.info(f"Connection left room: {room_id}")
    
    async def broadcast_to_room(self, message: Dict[str, Any], room_id: str):
        """Broadcast message to all connections in a room"""
        if room_id in self.rooms:
            disconnected_connections = set()
            for websocket in self.rooms[room_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    ws_logger.error(f"Error broadcasting to room: {e}")
                    disconnected_connections.add(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                self.disconnect(websocket)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all active connections"""
        all_connections = set()
        for user_connections in self.active_connections.values():
            all_connections.update(user_connections)
        
        disconnected_connections = set()
        for websocket in all_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                ws_logger.error(f"Error broadcasting to all: {e}")
                disconnected_connections.add(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            self.disconnect(websocket)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "total_connections": total_connections,
            "unique_users": len(self.active_connections),
            "active_rooms": len(self.rooms),
            "connections_by_type": self._get_connections_by_type()
        }
    
    def _get_connections_by_type(self) -> Dict[str, int]:
        """Get connection count by type"""
        type_counts = {}
        for metadata in self.connection_metadata.values():
            conn_type = metadata.get("connection_type", "unknown")
            type_counts[conn_type] = type_counts.get(conn_type, 0) + 1
        return type_counts


class NotificationManager:
    """Manages real-time notifications"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send real-time notification to user"""
        notification = {
            "type": "notification",
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.send_user_message(notification, user_id)
        
        # Store notification in Redis for offline users
        await self._store_offline_notification(user_id, notification)
    
    async def send_bulk_notification(
        self,
        user_ids: List[str],
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Send notification to multiple users"""
        for user_id in user_ids:
            await self.send_notification(user_id, notification_type, title, message, data)
    
    async def send_system_announcement(
        self,
        title: str,
        message: str,
        priority: str = "normal"
    ):
        """Send system-wide announcement"""
        announcement = {
            "type": "system_announcement",
            "title": title,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.broadcast_to_all(announcement)
    
    async def _store_offline_notification(self, user_id: str, notification: Dict[str, Any]):
        """Store notification for offline users"""
        key = f"offline_notifications:{user_id}"
        ws_redis.lpush(key, json.dumps(notification))
        ws_redis.ltrim(key, 0, 99)  # Keep last 100 notifications
        ws_redis.expire(key, 86400 * 7)  # Expire after 7 days
    
    async def get_offline_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Get stored notifications for user"""
        key = f"offline_notifications:{user_id}"
        notifications = ws_redis.lrange(key, 0, -1)
        ws_redis.delete(key)  # Clear after retrieval
        
        return [json.loads(notif) for notif in notifications]


class ExamMonitoringManager:
    """Manages real-time exam monitoring and proctoring"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.active_exam_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def start_exam_monitoring(self, session_id: str, user_id: str, exam_id: str):
        """Start monitoring an exam session"""
        room_id = f"exam_session_{session_id}"
        
        # Store session info
        self.active_exam_sessions[session_id] = {
            "user_id": user_id,
            "exam_id": exam_id,
            "room_id": room_id,
            "started_at": datetime.now(),
            "violations": [],
            "status": "active"
        }
        
        # Join exam monitoring room
        user_connections = self.connection_manager.active_connections.get(user_id, set())
        for websocket in user_connections:
            await self.connection_manager.join_room(websocket, room_id)
        
        ws_logger.info(f"Started exam monitoring for session {session_id}")
    
    async def report_violation(self, session_id: str, violation_type: str, details: Dict[str, Any]):
        """Report exam violation"""
        if session_id not in self.active_exam_sessions:
            return
        
        session_info = self.active_exam_sessions[session_id]
        violation = {
            "type": violation_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        session_info["violations"].append(violation)
        
        # Send real-time alert to proctors
        alert = {
            "type": "exam_violation",
            "session_id": session_id,
            "user_id": session_info["user_id"],
            "violation": violation
        }
        
        # Broadcast to exam monitoring room
        await self.connection_manager.broadcast_to_room(
            alert,
            f"exam_monitoring_{session_info['exam_id']}"
        )
        
        ws_logger.warning(f"Exam violation reported: {violation_type} in session {session_id}")
    
    async def update_exam_progress(self, session_id: str, progress_data: Dict[str, Any]):
        """Update exam progress in real-time"""
        if session_id not in self.active_exam_sessions:
            return
        
        session_info = self.active_exam_sessions[session_id]
        
        progress_update = {
            "type": "exam_progress",
            "session_id": session_id,
            "progress": progress_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to exam monitoring room
        await self.connection_manager.broadcast_to_room(
            progress_update,
            session_info["room_id"]
        )
    
    async def end_exam_monitoring(self, session_id: str):
        """End exam monitoring"""
        if session_id in self.active_exam_sessions:
            session_info = self.active_exam_sessions[session_id]
            session_info["status"] = "completed"
            session_info["ended_at"] = datetime.now()
            
            # Leave monitoring room
            user_connections = self.connection_manager.active_connections.get(
                session_info["user_id"], set()
            )
            for websocket in user_connections:
                await self.connection_manager.leave_room(websocket, session_info["room_id"])
            
            ws_logger.info(f"Ended exam monitoring for session {session_id}")


class LiveAnalyticsManager:
    """Manages real-time analytics and dashboard updates"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def broadcast_analytics_update(self, analytics_type: str, data: Dict[str, Any]):
        """Broadcast analytics update to dashboard users"""
        update = {
            "type": "analytics_update",
            "analytics_type": analytics_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to analytics room
        await self.connection_manager.broadcast_to_room(update, "analytics_dashboard")
    
    async def send_performance_alert(self, alert_type: str, message: str, severity: str):
        """Send performance alert to administrators"""
        alert = {
            "type": "performance_alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to admin monitoring room
        await self.connection_manager.broadcast_to_room(alert, "admin_monitoring")


# Global WebSocket managers
connection_manager = ConnectionManager()
notification_manager = NotificationManager(connection_manager)
exam_monitoring_manager = ExamMonitoringManager(connection_manager)
analytics_manager = LiveAnalyticsManager(connection_manager)
