# services/collaboration.py
import asyncio
from fastapi import WebSocket
from typing import Dict

from socketio import AsyncServer

sio = AsyncServer(async_mode='asgi', cors_allowed_origins=[])

@sio.on("annotation_add")
async def handle_annotation(sid, data):
    # Broadcast to all collaborators
    await sio.emit("annotation_update", data, room=data["doc_id"])

class CollaborationService:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.document_states = {}

    async def connect(self, doc_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[doc_id] = websocket

    async def broadcast(self, doc_id: str, message: dict):
        if conn := self.active_connections.get(doc_id):
            await conn.send_json(message)

    async def handle_edit(self, doc_id: str, edit_data: dict):
        # Apply edit to document state
        self.document_states.setdefault(doc_id, {}).update(edit_data)
        
        # Broadcast to all collaborators
        await self.broadcast(doc_id, {
            "type": "edit",
            "data": edit_data
        })

        


  