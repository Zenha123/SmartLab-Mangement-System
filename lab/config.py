import os

# Default to local backend. Override with env vars when backend runs on another machine.
SERVER_IP = os.getenv("SMARTLAB_SERVER_IP", "127.0.0.1")
PORT = os.getenv("SMARTLAB_SERVER_PORT", "8000")

BASE_HTTP = f"http://{SERVER_IP}:{PORT}"
BASE_WS = f"ws://{SERVER_IP}:{PORT}"
