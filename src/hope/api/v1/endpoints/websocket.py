"""
WebSocket endpoint for real-time panic state communication.

Provides bidirectional connection for:
- Panic session start/end
- Intensity updates
- AI messages during panic
- Heartbeat (ping/pong)
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from uuid import uuid4
import json

from hope.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Active WebSocket connections
_connections: dict[str, WebSocket] = {}


@router.websocket("/ws/panic")
async def panic_websocket(websocket: WebSocket, user_id: str = "anonymous"):
    """
    WebSocket endpoint for panic session communication.
    
    Expected message types:
    - ping: Heartbeat check
    - panic_start: Begin panic session
    - user_message: User input during panic
    - intensity_update: Panic intensity change
    - panic_end: End session
    """
    await websocket.accept()
    
    session_id = str(uuid4())
    _connections[user_id] = websocket
    
    logger.info(
        "WebSocket connected",
        user_id=user_id,
        session_id=session_id,
    )
    
    # Send session started message
    await websocket.send_json({
        "type": "session_started",
        "session_id": session_id,
        "user_id": user_id,
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "unknown")
            
            if msg_type == "ping":
                # Heartbeat response
                await websocket.send_json({"type": "pong"})
                
            elif msg_type == "panic_start":
                # Acknowledge panic session start
                intensity = message.get("intensity", 5.0)
                await websocket.send_json({
                    "type": "panic_acknowledged",
                    "session_id": session_id,
                    "initial_intensity": intensity,
                    "message": "I'm here with you. Let's take this one breath at a time.",
                })
                
            elif msg_type == "user_message":
                # Echo acknowledgment (AI response would come from IntelligenceService)
                text = message.get("text", "")
                await websocket.send_json({
                    "type": "ai_response",
                    "text": "I hear you. Take a slow breath with me.",
                    "session_id": session_id,
                })
                
            elif msg_type == "intensity_update":
                intensity = message.get("intensity", 5.0)
                # Acknowledge intensity update
                await websocket.send_json({
                    "type": "intensity_acknowledged",
                    "intensity": intensity,
                })
                
            elif msg_type == "panic_end":
                outcome = message.get("outcome", "resolved")
                await websocket.send_json({
                    "type": "session_ended",
                    "session_id": session_id,
                    "outcome": outcome,
                })
                
            else:
                # Unknown message type - acknowledge
                await websocket.send_json({
                    "type": "ack",
                    "received": msg_type,
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected", user_id=user_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
    finally:
        if user_id in _connections:
            del _connections[user_id]
