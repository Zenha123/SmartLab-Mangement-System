from aiortc import VideoStreamTrack
import numpy as np
from av import VideoFrame

class ScreenVideoTrack(VideoStreamTrack):

    async def recv(self):
        '''pts, time_base = await self.next_timestamp()

        # Temporary black frame (testing)
        img = np.zeros((480, 640, 3), dtype=np.uint8)

        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame'''
        # This method should capture the screen and return a VideoFrame
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
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        #frame = np.zeros((480, 640, 3), dtype=np.uint8)
        #frame[:] = (0, 0, 255)  # red screen
        #saved = cv2.imwrite("C:/Users/shadi/Desktop/test_capture.jpg", frame)  # Debugging
        #print("saved:", saved)

        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        await asyncio.sleep(1 / 20)  # 20 FPS
        return video_frame

