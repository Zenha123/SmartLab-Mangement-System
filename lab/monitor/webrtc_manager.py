import asyncio
import threading
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from PyQt6.QtCore import pyqtSignal, QObject


class FacultyWebRTCManager(QObject):
    frame_signal = pyqtSignal(int, object)

    def __init__(self, ws_client, frame_callback):
        super().__init__()
        self.ws_client = ws_client
        self.video_callback = frame_callback
        self.frame_signal.connect(frame_callback)
        self.connections = {}

        self.ws_client.monitor_signal.connect(self._handle_signal_async)

        self.loop = asyncio.new_event_loop()
        threading.Thread(
            target=self._run_loop,
            daemon=True
        ).start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_monitoring(self, student_id):
        if student_id in self.connections:
            print(f"Already monitoring student {student_id}")
            return

        asyncio.run_coroutine_threadsafe(
            self._offer_async(student_id),
            self.loop
        )

    async def _offer_async(self, student_id):
        pc = RTCPeerConnection()
        pc.addTransceiver("video", direction="recvonly")
        self.connections[student_id] = pc

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"[Student {student_id}] Connection state: {pc.connectionState}")

        @pc.on("track")
        def on_track(track):
            print(f"[Student {student_id}] Track received: {track.kind}")
            if track.kind == "video":
                # FIX 1: Use ensure_future instead of run_coroutine_threadsafe
                # because on_track is already firing inside self.loop.
                # run_coroutine_threadsafe on the same loop causes a deadlock.
                asyncio.ensure_future(
                    self._consume_video(track, student_id),
                    loop=self.loop
                )

        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                self.ws_client.send_json({
                    "type": "monitor_ice",
                    "student_id": student_id,
                    "candidate": {
                        "candidate": candidate.to_sdp(),
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex,
                    }
                })

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        self.ws_client.send_json({
            "type": "monitor_offer",
            "student_id": student_id,
            "offer": {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
        })

    def _handle_signal_async(self, data):
        asyncio.run_coroutine_threadsafe(
            self.__handle_signal(data),
            self.loop
        )

    async def __handle_signal(self, data):
        student_id = data.get("student_id")
        pc = self.connections.get(student_id)

        if not pc:
            print(f"[Signal] No PC found for student {student_id}")
            return

        msg_type = data.get("type")

        if msg_type == "monitor_answer":
            answer = data["answer"]
            if pc.signalingState != "have-local-offer":
                print(f"[Signal] Ignoring answer: PC in state '{pc.signalingState}'")
                return
            await pc.setRemoteDescription(
                RTCSessionDescription(
                    sdp=answer["sdp"],
                    type=answer["type"]
                )
            )
            print(f"[Student {student_id}] Remote description set (answer)")

        elif msg_type == "monitor_ice":
            candidate = data.get("candidate")
            if not candidate or not candidate.get("candidate"):
                return  # ignore empty end-of-candidates signal
            try:
                await pc.addIceCandidate(
                    RTCIceCandidate(
                        sdpMid=candidate["sdpMid"],
                        sdpMLineIndex=candidate["sdpMLineIndex"],
                        candidate=candidate["candidate"]
                    )
                )
            except Exception as e:
                print(f"[ICE] Failed to add candidate: {e}")

    async def _consume_video(self, track, student_id):
        print(f"[Student {student_id}] Starting video consumption loop")
        while True:
            try:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")
                self.frame_signal.emit(student_id, img)
            except Exception as e:
                print(f"[Student {student_id}] Video stream ended: {e}")
                break

    def stop_monitoring(self, student_id):
        pc = self.connections.get(student_id)
        if not pc:
            return

        self.ws_client.send_json({
            "type": "monitor_stop",
            "student_id": student_id
        })

        asyncio.run_coroutine_threadsafe(
            pc.close(),
            self.loop
        )

        del self.connections[student_id]
        print(f"Stopped monitoring student {student_id}")

    def cleanup_connection(self, student_id):
        pc = self.connections.get(student_id)
        if pc:
            asyncio.run_coroutine_threadsafe(
                pc.close(),
                self.loop
            )
            del self.connections[student_id]
            print(f"Cleaned up connection for student {student_id}")