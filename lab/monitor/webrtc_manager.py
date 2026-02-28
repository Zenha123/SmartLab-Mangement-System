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

    def _run_offer(self, student_id):
        asyncio.run(self._offer_async(student_id))

    async def _offer_async(self, student_id):
        pc = RTCPeerConnection()

        pc.addTransceiver("video", direction="recvonly")

        self.connections[student_id] = pc

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
    

        @pc.on("track")
        def on_track(track):
            if track.kind == "video":
                print("Video track received")
                asyncio.run_coroutine_threadsafe(
                    self._consume_video(track, student_id),
                    self.loop
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
                        "sdpMLineIndex": candidate.sdpMLineIndex
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
            return

        if data["type"] == "monitor_answer":
            answer = data["answer"]

            if pc.signalingState != "have-local-offer":
                print("Ignoring answer: PC not in have-local-offer state")
                return
            await pc.setRemoteDescription(
                RTCSessionDescription(
                    sdp=answer["sdp"],
                    type=answer["type"]
                )
            )

        elif data["type"] == "monitor_ice":
            candidate = data["candidate"]
            await pc.addIceCandidate(
                RTCIceCandidate(
                    sdpMid=candidate["sdpMid"],
                    sdpMLineIndex=candidate["sdpMLineIndex"],
                    candidate=candidate["candidate"]
                )
            )

    async def _consume_video(self, track, student_id):
        while True:
            try:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")
                self.frame_signal.emit(student_id, img)
            except Exception as e:
                print("video ended", e)
                break
            