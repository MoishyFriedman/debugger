from fastapi import WebSocket
import os

class Manager:
    def __init__(self):
        self.active_connections = []
        self. path = ""

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, path: str):
        self.active_connections.remove(path)
        self.path = ""

    def file_path(self, path: str):
        self.path = path

    def remove_file_path(self):
        if os.path.exists(self.path):
            os.remove(self.path)
            self.path = ""
            print("File removed")