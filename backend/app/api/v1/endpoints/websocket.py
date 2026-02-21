"""
WebSocket endpoints for real-time features
"""

import json
import logging
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user_ws
from app.services.proctoring_service import proctoring_service
from app.services.notification_service import notification_service
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.proctoring_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a user's WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        
        # Register with notification service
        await notification_service.register_websocket(user_id, websocket)
        
        logger.info(f"WebSocket connected for user: {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a user's WebSocket"""
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            except ValueError:
                pass
        
        # Remove from proctoring connections if exists
        for exam_session_id, ws in list(self.proctoring_connections.items()):
            if ws == websocket:
                del self.proctoring_connections[exam_session_id]
                break
        
        logger.info(f"WebSocket disconnected for user: {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {str(e)}")
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected users"""
        for user_connections in self.active_connections.values():
            for websocket in user_connections:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {str(e)}")

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications"""
    try:
        # Verify user authentication
        user = await get_current_user_ws(websocket, user_id, db)
        if not user:
            await websocket.close(code=4001, reason="Unauthorized")
            return
        
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
                elif message.get("type") == "mark_notification_read":
                    notification_id = message.get("notification_id")
                    if notification_id:
                        await notification_service.mark_notification_as_read(notification_id)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            await notification_service.unregister_websocket(user_id, websocket)
        
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        await websocket.close(code=4000, reason="Internal error")

@router.websocket("/ws/proctoring/{exam_session_id}")
async def websocket_proctoring(
    websocket: WebSocket,
    exam_session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for exam proctoring"""
    try:
        await websocket.accept()
        
        # Start proctoring session
        success = await proctoring_service.start_proctoring_session(
            exam_session_id, websocket, db
        )
        
        if not success:
            await websocket.close(code=4002, reason="Failed to start proctoring")
            return
        
        manager.proctoring_connections[exam_session_id] = websocket
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == "VIDEO_FRAME":
                    # Process video frame for face detection
                    frame_data = message.get("data", "").encode()
                    await proctoring_service.process_video_frame(
                        exam_session_id, frame_data, db
                    )
                
                elif message_type == "SCREEN_CAPTURE":
                    # Process screen capture
                    screen_data = message.get("data", "").encode()
                    await proctoring_service.process_screen_capture(
                        exam_session_id, screen_data, db
                    )
                
                elif message_type == "BROWSER_EVENT":
                    # Handle browser events (tab switch, etc.)
                    event_type = message.get("event_type")
                    event_data = message.get("event_data", {})
                    await proctoring_service.handle_browser_event(
                        exam_session_id, event_type, event_data, db
                    )
                
                elif message_type == "HEARTBEAT":
                    # Update last activity timestamp
                    await websocket.send_text(json.dumps({"type": "heartbeat_ack"}))
                
                elif message_type == "END_PROCTORING":
                    # End proctoring session
                    await proctoring_service.stop_proctoring_session(exam_session_id, db)
                    break
        
        except WebSocketDisconnect:
            await proctoring_service.stop_proctoring_session(exam_session_id, db)
            if exam_session_id in manager.proctoring_connections:
                del manager.proctoring_connections[exam_session_id]
        
    except Exception as e:
        logger.error(f"Proctoring WebSocket error for session {exam_session_id}: {str(e)}")
        await websocket.close(code=4000, reason="Internal error")

@router.websocket("/ws/live-analytics/{user_id}")
async def websocket_live_analytics(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for live analytics updates"""
    try:
        # Verify user is admin/super admin
        user = await get_current_user_ws(websocket, user_id, db)
        if not user or user.role not in ["admin", "super_admin"]:
            await websocket.close(code=4003, reason="Insufficient permissions")
            return
        
        await websocket.accept()
        
        try:
            while True:
                # Send live analytics updates every 30 seconds
                import asyncio
                await asyncio.sleep(30)
                
                # Get real-time metrics
                live_metrics = {
                    "type": "live_metrics",
                    "data": {
                        "active_users": len(manager.active_connections),
                        "active_proctoring_sessions": len(manager.proctoring_connections),
                        "timestamp": "2024-01-01T00:00:00Z"  # Current timestamp
                    }
                }
                
                await websocket.send_text(json.dumps(live_metrics))
        
        except WebSocketDisconnect:
            pass
        
    except Exception as e:
        logger.error(f"Live analytics WebSocket error for user {user_id}: {str(e)}")
        await websocket.close(code=4000, reason="Internal error")

@router.websocket("/ws/exam-monitor/{exam_id}")
async def websocket_exam_monitor(
    websocket: WebSocket,
    exam_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time exam monitoring by proctors"""
    try:
        await websocket.accept()
        
        # This would be used by proctors to monitor ongoing exams
        # Send real-time updates about exam progress, violations, etc.
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "get_exam_status":
                    # Get current exam status
                    exam_status = {
                        "type": "exam_status",
                        "data": {
                            "exam_id": exam_id,
                            "active_sessions": 0,  # Would get from database
                            "violations": [],  # Would get recent violations
                            "timestamp": "2024-01-01T00:00:00Z"
                        }
                    }
                    await websocket.send_text(json.dumps(exam_status))
        
        except WebSocketDisconnect:
            pass
        
    except Exception as e:
        logger.error(f"Exam monitor WebSocket error for exam {exam_id}: {str(e)}")
        await websocket.close(code=4000, reason="Internal error")

@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat (support, collaboration)"""
    try:
        user = await get_current_user_ws(websocket, user_id, db)
        if not user:
            await websocket.close(code=4001, reason="Unauthorized")
            return
        
        await websocket.accept()
        
        # Add to chat room
        chat_room_key = f"chat:{room_id}"
        if chat_room_key not in manager.active_connections:
            manager.active_connections[chat_room_key] = []
        
        manager.active_connections[chat_room_key].append(websocket)
        
        # Notify others that user joined
        join_message = {
            "type": "user_joined",
            "user_id": user_id,
            "user_name": f"{user.profile.first_name} {user.profile.last_name}" if user.profile else user.email,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        for ws in manager.active_connections[chat_room_key]:
            if ws != websocket:
                try:
                    await ws.send_text(json.dumps(join_message))
                except:
                    pass
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "chat_message":
                    # Broadcast message to all users in the room
                    chat_message = {
                        "type": "chat_message",
                        "user_id": user_id,
                        "user_name": f"{user.profile.first_name} {user.profile.last_name}" if user.profile else user.email,
                        "message": message.get("message", ""),
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                    
                    for ws in manager.active_connections[chat_room_key]:
                        try:
                            await ws.send_text(json.dumps(chat_message))
                        except:
                            pass
        
        except WebSocketDisconnect:
            # Remove from chat room
            try:
                manager.active_connections[chat_room_key].remove(websocket)
                if not manager.active_connections[chat_room_key]:
                    del manager.active_connections[chat_room_key]
            except:
                pass
            
            # Notify others that user left
            leave_message = {
                "type": "user_left",
                "user_id": user_id,
                "user_name": f"{user.profile.first_name} {user.profile.last_name}" if user.profile else user.email,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            if chat_room_key in manager.active_connections:
                for ws in manager.active_connections[chat_room_key]:
                    try:
                        await ws.send_text(json.dumps(leave_message))
                    except:
                        pass
        
    except Exception as e:
        logger.error(f"Chat WebSocket error for room {room_id}, user {user_id}: {str(e)}")
        await websocket.close(code=4000, reason="Internal error")
