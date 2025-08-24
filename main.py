from http.client import HTTPException
from fastapi import FastAPI, WebSocketDisconnect, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import tempfile
import uuid
import json
from manager import Manager
from debugger import Debugger
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = FastAPI()
debugger = Debugger()
manager = Manager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/path")
async def code_to_file(code: dict):
    execution_dir_path = Path(tempfile.mkdtemp())
    file_path = execution_dir_path / f"script-{uuid.uuid1()}.py"
    file_path.write_text(code.get("code"))
    normalized_path = str(file_path).replace("\\", "/")
    logger.debug(f"Created debug file at: {normalized_path}")
    
    # וידוא שהקובץ קיים
    if not file_path.exists():
        logger.error(f"Failed to create file at: {normalized_path}")
        raise HTTPException(status_code=500, message="Failed to create debug file")
    manager.file_path(file_path)
    return normalized_path

@app.websocket("/ws/debug")
async def debug(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            message = json.loads(text)
            logger.debug(f"Received message: {message}")
            debugger.start(websocket, message)
            debugger.send_message(message)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        debugger.stop()
        manager.disconnect(websocket)
        manager.remove_file_path()
    except Exception as e:
        logger.error(f"Error in debug session: {str(e)}")
        raise



if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000)
