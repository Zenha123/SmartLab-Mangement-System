"""
WebSocket Client for Real-time Student Monitoring
Connects to Django Channels WebSocket for live status updates
"""
import websocket
import json
import threading
from typing import Callable, Optional


class WebSocketClient:
    """WebSocket client for live monitoring"""
    
    def __init__(self, batch_id: int, jwt_token: str, base_url: str = "ws://localhost:8000"):
        self.batch_id = batch_id
        self.jwt_token = jwt_token
        self.base_url = base_url
        self.ws: Optional[websocket.WebSocketApp] = None
        self.on_message_callback: Optional[Callable] = None
        self.connected = False
        self.thread: Optional[threading.Thread] = None
    
    def connect(self, on_message: Callable):
        """
        Connect to WebSocket server
        on_message: callback function(data: dict) called when message received
        """
        self.on_message_callback = on_message
        url = f"{self.base_url}/ws/monitor/{self.batch_id}/?token={self.jwt_token}"
        
        self.ws = websocket.WebSocketApp(
            url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # Run WebSocket in separate thread
        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()
    
    def _on_open(self, ws):
        """Called when WebSocket connection is established"""
        self.connected = True
        print(f"WebSocket connected to batch {self.batch_id}")
    
    def _on_message(self, ws, message):
        """Called when message is received from server"""
        try:
            data = json.loads(message)
            if self.on_message_callback:
                self.on_message_callback(data)
        except json.JSONDecodeError:
            print(f"Failed to parse WebSocket message: {message}")
    
    def _on_error(self, ws, error):
        """Called when WebSocket error occurs"""
        print(f"WebSocket error: {error}")
        self.connected = False
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection is closed"""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
    
    def send_status_update(self, student_id: int, status: str, mode: str):
        """Send student status update to server"""
        if self.ws and self.connected:
            message = {
                "type": "status_update",
                "student_id": student_id,
                "status": status,
                "mode": mode
            }
            self.ws.send(json.dumps(message))
    
    def disconnect(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
            self.connected = False
