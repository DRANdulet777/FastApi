from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.connection_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Вы сказали: {data}", websocket)
            await manager.broadcast(f"Кто-то сказал: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("Кто-то отключился")
