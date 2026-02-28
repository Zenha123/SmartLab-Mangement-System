import websocket
import json
import threading
import time
from PyQt6.QtCore import QThread, pyqtSignal
from api_client import ACCESS_TOKEN
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc import RTCIceCandidate
import asyncio
import threading
from lab import data
from screen_track import ScreenVideoTrack

# WS_URL should match your backend routing
WS_URL = "ws://127.0.0.1:8000/ws/student/"

class WebSocketClient(QThread):
    message_signal = pyqtSignal(dict)  # Generic signal for all events
    
    def __init__(self):
        super().__init__()
        self.ws = None
        self.is_running = True
        self.reconnect_delay = 5
        self.pc = None
        self.faculty_channel = None

    def run(self):
        """Main thread loop"""
        while self.is_running:
            try:
                # Append JWT token to URL for authentication
                import api_client
                token = api_client.ACCESS_TOKEN
                if not token:
                    time.sleep(2)
                    continue
                    
                url = f"{WS_URL}?token={token}"
                
                self.ws = websocket.WebSocketApp(
                    url,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close
                )
                
                # Run forever (blocks until close)
                self.ws.run_forever()
                
            except Exception as e:
                print(f"WebSocket Error: {e}")
            
            # Reconnect delay
            if self.is_running:
                time.sleep(self.reconnect_delay)

    def on_open(self, ws):
        print("WebSocket Connected")

    def on_message(self, ws, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            event_type = data.get("type")
            self.message_signal.emit(data)
            if event_type == "monitor_offer":
                threading.Thread(
                    target=self.handle_offer,
                    args=(data,),
                    daemon=True
                ).start()
                print("student recived", data)
        except json.JSONDecodeError:
            pass

    def handle_offer(self, data):
        asyncio.run(self._handle_offer_async(data))

    async def _handle_offer_async(self, data):
        offer = data.get("offer")

        self.pc = RTCPeerConnection()
        #self.pc.addTrack(ScreenVideoTrack())

        @self.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                self.send_json({
                    "type": "monitor_ice",
                    "candidate": {
                        "candidate": candidate.to_sdp(),
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex
                    }
                })

        await self.pc.setRemoteDescription(
            RTCSessionDescription(
                sdp=offer["sdp"],
                type=offer["type"]
            )
        )
        self.pc.addTrack(ScreenVideoTrack())

        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        self.send_json({
            "type": "monitor_answer",
            "answer": {
                "sdp": self.pc.localDescription.sdp,
                "type": self.pc.localDescription.type
            }
        })

    def send_json(self, data):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(data))
        else:
            print("WebSocket is not connected. Cannot send message.")

    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket Closed")

    def stop(self):
        """Stop the client"""
        self.is_running = False
        if self.ws:
            self.ws.close()
        self.quit()
        self.wait()
