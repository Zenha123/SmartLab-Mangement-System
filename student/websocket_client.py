import websocket
import json
import threading
import time
from PyQt6.QtCore import QThread, pyqtSignal
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
import asyncio

from screen_track import ScreenVideoTrack
from config import BASE_WS

# WS_URL should match your backend routing
WS_URL = f"{BASE_WS}/ws/student/"


class WebSocketClient(QThread):
    message_signal = pyqtSignal(dict)  # Generic signal for all events

    def __init__(self):
        super().__init__()
        self.ws = None
        self.is_running = True
        self.reconnect_delay = 5
        self.pc = None
        self.screen_track = None  # FIX 5: Keep reference to prevent GC
        self.loop = asyncio.new_event_loop()

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self):
        """Main thread loop"""
        threading.Thread(target=self.start_async_loop, daemon=True).start()

        while self.is_running:
            try:
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

                self.ws.run_forever()

            except Exception as e:
                print(f"WebSocket Error: {e}")

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
                print("Student received monitor_offer")
                # FIX 2: Never use asyncio.run() when self.loop is already running.
                # Use run_coroutine_threadsafe to schedule on the existing loop.
                asyncio.run_coroutine_threadsafe(
                    self._handle_offer_and_send(data),
                    self.loop
                )

            elif event_type == "monitor_ice":
                asyncio.run_coroutine_threadsafe(
                    self._handle_ice_async(data),
                    self.loop
                )

            elif event_type == "monitor_stop":
                asyncio.run_coroutine_threadsafe(
                    self._handle_stop_async(),
                    self.loop
                )

        except json.JSONDecodeError:
            pass

    async def _handle_offer_and_send(self, data):
        """Handle offer and send answer back — runs on self.loop"""
        try:
            answer_data = await self._handle_offer_async(data)
            print("Answer ready, sending to backend")
            self.send_json(answer_data)
            print("Answer sent to backend")
        except Exception as e:
            print(f"Error in _handle_offer_and_send: {e}")

    async def _handle_offer_async(self, data):
        offer = data.get("offer")

        if self.pc:
            await self.pc.close()

        self.pc = RTCPeerConnection()

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"[Student PC] Connection state: {self.pc.connectionState}")

        @self.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                self.send_json({
                    "type": "monitor_ice",
                    "student_id": data.get("student_id"),
                    "candidate": {
                        "candidate": candidate.to_sdp(),
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex,
                    }
                })

        # Step 1: Set remote description (offer) first
        await self.pc.setRemoteDescription(
            RTCSessionDescription(
                sdp=offer["sdp"],
                type=offer["type"]
            )
        )

        # Step 2: Create screen track and store reference to prevent GC
        # FIX 5: self.screen_track keeps it alive for the full session
        self.screen_track = ScreenVideoTrack()
        self.pc.addTrack(self.screen_track)

        # Step 3: Create and set answer
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        print("===== STUDENT FINAL SDP =====")
        print(self.pc.localDescription.sdp)
        print("=============================")

        return {
            "type": "monitor_answer",
            "student_id": data.get("student_id"),
            "answer": {
                "sdp": self.pc.localDescription.sdp,
                "type": self.pc.localDescription.type
            }
        }

    async def _handle_ice_async(self, data):
        if not self.pc:
            print("[ICE] No PC available, skipping candidate")
            return

        candidate = data.get("candidate")
        if not candidate or not candidate.get("candidate"):
            return  # ignore empty end-of-candidates

        try:
            await self.pc.addIceCandidate(
                RTCIceCandidate(
                    sdpMid=candidate["sdpMid"],
                    sdpMLineIndex=candidate["sdpMLineIndex"],
                    candidate=candidate["candidate"]
                )
            )
        except Exception as e:
            print(f"[ICE] Failed to add candidate: {e}")

    async def _handle_stop_async(self):
        if self.pc:
            await self.pc.close()
            self.pc = None
            self.screen_track = None  # Release track reference too
            print("Streaming stopped by faculty")

    def send_json(self, data):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(data))
        else:
            print("WebSocket not connected. Cannot send message.")

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