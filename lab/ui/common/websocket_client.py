import websocket
import json
import threading
import time
from PyQt6.QtCore import QThread, pyqtSignal
from config import BASE_WS

# WS_URL should match your backend routing
WS_URL = f"{BASE_WS}/ws/monitor/"
# Generic signal for all events

class FacultyWebSocketClient(QThread):
    student_status_signal = pyqtSignal(dict)  # Signal for student online/offline
    monitor_signal = pyqtSignal(dict)  # Signal for all monitor events

    def __init__(self, batch_id, token):
        super().__init__()
        self.batch_id = batch_id
        self.token = token
        self.ws = None
        self.is_running = True
        self.reconnect_delay = 5

        self.connected = False

    def run(self):
        """Main thread loop"""
        while self.is_running:
            try:
                if not self.token:
                    print("No token provided for WebSocket")
                    break
                    
                url = f"{WS_URL}{self.batch_id}/?token={self.token}"
                
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
        print(f"WebSocket Connected to batch {self.batch_id}")
        self.connected = True

    def send_json(self, data):
        if self.ws and self.connected:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("WebSocket is not connected. Cannot send message.")

    def on_message(self, ws, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            event_type = data.get('type')
            
            print("Faculty received message:", data)

            if event_type == 'student_status':
                self.student_status_signal.emit(data)
            elif event_type == 'status_broadcast':
                # Handle generic status broadcast if used
                self.student_status_signal.emit(data)
            elif event_type in ['monitor_answer', 'monitor_ice']:
                self.monitor_signal.emit(data)
        except json.JSONDecodeError:
            pass

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
