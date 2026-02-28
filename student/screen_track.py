import cv2
import numpy as np
import mss
from aiortc import VideoStreamTrack
from av import VideoFrame
import asyncio


class ScreenVideoTrack(VideoStreamTrack):
    """
    Captures screen and sends frames over WebRTC.
    """

    def __init__(self):
        super().__init__()
        self.sct = mss.mss()

        # Capture full primary monitor
        self.monitor = self.sct.monitors[0]

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        img = np.array(self.sct.grab(self.monitor))
        #frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:] = (0, 0, 255)  # red screen
        saved = cv2.imwrite("C:/Users/shadi/Desktop/test_capture.jpg", frame)  # Debugging
        print("saved:", saved)

        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        await asyncio.sleep(1 / 20)  # 20 FPS
        return video_frame



'''import cv2
import mss
import numpy as np
import asyncio

from aiortc import VideoStreamTrack
from av import VideoFrame


class ScreenVideoTrack(VideoStreamTrack):
    """
    A VideoStreamTrack that captures the screen and sends frames via WebRTC.
    """

    def __init__(self):
        super().__init__()
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        # Performance controls
        self.width = 1280
        self.height = 720
        self.fps = 15  # DO NOT increase for now

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # Capture screen
        img = self.sct.grab(self.monitor)
        frame = np.array(img)

        
        # Convert BGRA → BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


        # Resize for performance
        frame = cv2.resize(frame, (self.width, self.height))
        cv2.imwrite("c:/Users/shadi/Desktop/test_capture.jpg", frame)  # Debugging

        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        # FPS limiting
        await asyncio.sleep(1 / self.fps)

        return video_frame'''
