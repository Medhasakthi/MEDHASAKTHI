"""
WebSocket API routes for MEDHASAKTHI
Real-time communication endpoints
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.websocket_manager import (
    connection_manager,
    notification_manager,
    exam_monitoring_manager,
    analytics_manager
)
from app.api.v1.auth.dependencies import get_current_user_from_token
from app.models.user import User

router = APIRouter()


@router.websocket("/connect/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    connection_type: str = "general",
    db: Session = Depends(get_db)
):
    """Main WebSocket connection endpoint"""
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=4004, reason="User not found")
        return
    
    await connection_manager.connect(websocket, user_id, connection_type)
    
    try:
        # Send offline notifications if any
        offline_notifications = await notification_manager.get_offline_notifications(user_id)
        for notification in offline_notifications:
            await connection_manager.send_personal_message(notification, websocket)
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_websocket_message(websocket, user_id, message, db)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)


@router.websocket("/exam/{session_id}")
async def exam_websocket(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for exam sessions"""
    
    # Verify exam session exists and get user
    from app.models.talent_exam import TalentExamSession, TalentExamRegistration
    
    session = db.query(TalentExamSession).filter(
        TalentExamSession.id == session_id
    ).first()
    
    if not session:
        await websocket.close(code=4004, reason="Exam session not found")
        return
    
    registration = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.id == session.registration_id
    ).first()
    
    if not registration:
        await websocket.close(code=4004, reason="Registration not found")
        return
    
    user_id = str(registration.student_id) if registration.student_id else registration.student_email
    
    await connection_manager.connect(websocket, user_id, "exam_session")
    
    # Start exam monitoring
    await exam_monitoring_manager.start_exam_monitoring(
        session_id, user_id, str(session.exam_id)
    )
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_exam_message(websocket, session_id, user_id, message, db)
            
    except WebSocketDisconnect:
        await exam_monitoring_manager.end_exam_monitoring(session_id)
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"Exam WebSocket error: {e}")
        await exam_monitoring_manager.end_exam_monitoring(session_id)
        connection_manager.disconnect(websocket)


@router.websocket("/admin/monitoring")
async def admin_monitoring_websocket(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for admin monitoring"""
    
    # Verify admin user
    try:
        user = await get_current_user_from_token(token, db)
        if not user.is_superuser:
            await websocket.close(code=4003, reason="Admin access required")
            return
    except:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await connection_manager.connect(websocket, str(user.id), "admin_monitoring")
    await connection_manager.join_room(websocket, "admin_monitoring")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await handle_admin_message(websocket, str(user.id), message, db)
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        print(f"Admin WebSocket error: {e}")
        connection_manager.disconnect(websocket)


async def handle_websocket_message(
    websocket: WebSocket,
    user_id: str,
    message: Dict[str, Any],
    db: Session
):
    """Handle general WebSocket messages"""
    
    message_type = message.get("type")
    
    if message_type == "ping":
        await connection_manager.send_personal_message(
            {"type": "pong", "timestamp": message.get("timestamp")},
            websocket
        )
    
    elif message_type == "join_room":
        room_id = message.get("room_id")
        if room_id:
            await connection_manager.join_room(websocket, room_id)
            await connection_manager.send_personal_message(
                {"type": "room_joined", "room_id": room_id},
                websocket
            )
    
    elif message_type == "leave_room":
        room_id = message.get("room_id")
        if room_id:
            await connection_manager.leave_room(websocket, room_id)
            await connection_manager.send_personal_message(
                {"type": "room_left", "room_id": room_id},
                websocket
            )
    
    elif message_type == "send_message":
        # Handle chat messages or other user communications
        recipient_id = message.get("recipient_id")
        content = message.get("content")
        
        if recipient_id and content:
            chat_message = {
                "type": "chat_message",
                "sender_id": user_id,
                "content": content,
                "timestamp": message.get("timestamp")
            }
            await connection_manager.send_user_message(chat_message, recipient_id)


async def handle_exam_message(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    message: Dict[str, Any],
    db: Session
):
    """Handle exam-specific WebSocket messages"""
    
    message_type = message.get("type")
    
    if message_type == "answer_update":
        # Handle answer updates
        question_id = message.get("question_id")
        answer = message.get("answer")
        
        if question_id and answer is not None:
            # Update exam progress
            await exam_monitoring_manager.update_exam_progress(session_id, {
                "question_id": question_id,
                "answer": answer,
                "timestamp": message.get("timestamp")
            })
    
    elif message_type == "violation_report":
        # Handle proctoring violations
        violation_type = message.get("violation_type")
        details = message.get("details", {})
        
        if violation_type:
            await exam_monitoring_manager.report_violation(
                session_id, violation_type, details
            )
    
    elif message_type == "heartbeat":
        # Handle exam session heartbeat
        await connection_manager.send_personal_message(
            {
                "type": "heartbeat_ack",
                "session_id": session_id,
                "timestamp": message.get("timestamp")
            },
            websocket
        )
    
    elif message_type == "submit_exam":
        # Handle exam submission
        await exam_monitoring_manager.end_exam_monitoring(session_id)
        await connection_manager.send_personal_message(
            {
                "type": "exam_submitted",
                "session_id": session_id,
                "message": "Exam submitted successfully"
            },
            websocket
        )


async def handle_admin_message(
    websocket: WebSocket,
    user_id: str,
    message: Dict[str, Any],
    db: Session
):
    """Handle admin monitoring messages"""
    
    message_type = message.get("type")
    
    if message_type == "get_stats":
        # Send connection statistics
        stats = connection_manager.get_connection_stats()
        await connection_manager.send_personal_message(
            {
                "type": "connection_stats",
                "stats": stats
            },
            websocket
        )
    
    elif message_type == "send_announcement":
        # Send system announcement
        title = message.get("title")
        content = message.get("message")
        priority = message.get("priority", "normal")
        
        if title and content:
            await notification_manager.send_system_announcement(title, content, priority)
    
    elif message_type == "broadcast_notification":
        # Send notification to specific users
        user_ids = message.get("user_ids", [])
        notification_type = message.get("notification_type")
        title = message.get("title")
        content = message.get("message")
        data = message.get("data")
        
        if user_ids and title and content:
            await notification_manager.send_bulk_notification(
                user_ids, notification_type, title, content, data
            )


# REST endpoints for WebSocket management
@router.get("/connections/stats")
async def get_connection_stats(
    current_user: User = Depends(get_current_user_from_token)
):
    """Get WebSocket connection statistics"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return connection_manager.get_connection_stats()


@router.post("/notifications/send")
async def send_notification(
    notification_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Send real-time notification"""
    
    user_id = notification_data.get("user_id")
    notification_type = notification_data.get("type", "general")
    title = notification_data.get("title")
    message = notification_data.get("message")
    data = notification_data.get("data")
    
    if not user_id or not title or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id, title, and message are required"
        )
    
    await notification_manager.send_notification(
        user_id, notification_type, title, message, data
    )
    
    return {"message": "Notification sent successfully"}


@router.post("/notifications/broadcast")
async def broadcast_notification(
    notification_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Broadcast notification to multiple users"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    user_ids = notification_data.get("user_ids", [])
    notification_type = notification_data.get("type", "general")
    title = notification_data.get("title")
    message = notification_data.get("message")
    data = notification_data.get("data")
    
    if not user_ids or not title or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_ids, title, and message are required"
        )
    
    await notification_manager.send_bulk_notification(
        user_ids, notification_type, title, message, data
    )
    
    return {
        "message": f"Notification sent to {len(user_ids)} users",
        "user_count": len(user_ids)
    }


@router.post("/announcements/system")
async def send_system_announcement(
    announcement_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_from_token)
):
    """Send system-wide announcement"""
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    title = announcement_data.get("title")
    message = announcement_data.get("message")
    priority = announcement_data.get("priority", "normal")
    
    if not title or not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title and message are required"
        )
    
    await notification_manager.send_system_announcement(title, message, priority)
    
    return {"message": "System announcement sent successfully"}
