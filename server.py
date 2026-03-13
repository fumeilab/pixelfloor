"""PixelFloor Server — Lightweight FastAPI WebSocket relay.

Usage:
  python server.py                          # Serve on port 3000
  python server.py --port 3000              # Custom port
  python server.py --log-file app.log       # Tail a log file and broadcast
"""

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketState
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("pixelfloor")

app = FastAPI(title="PixelFloor Server")
_clients: set[WebSocket] = set()

HTML_PATH = Path(__file__).parent / "index.html"


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _clients.add(ws)
    logger.info(f"Client connected ({len(_clients)} total)")
    try:
        while True:
            data = await ws.receive_text()
            # Client can send events too — broadcast to others
            try:
                msg = json.loads(data)
                await broadcast(msg, exclude=ws)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        _clients.discard(ws)
        logger.info(f"Client disconnected ({len(_clients)} total)")


async def broadcast(msg: dict, exclude: WebSocket = None):
    payload = json.dumps(msg)
    dead = set()
    for client in _clients:
        if client is exclude:
            continue
        try:
            if client.client_state == WebSocketState.CONNECTED:
                await client.send_text(payload)
        except Exception:
            dead.add(client)
    _clients -= dead


class AgentEvent(BaseModel):
    type: str = "agent_state"
    agent: str
    state: str = "working"
    speech: Optional[str] = None
    duration: Optional[int] = 300


class LogEvent(BaseModel):
    text: str
    level: Optional[str] = "info"


class ParticleEvent(BaseModel):
    type: str = "particle"
    from_agent: str
    to_agent: str


@app.post("/api/event")
async def post_event(event: AgentEvent):
    await broadcast(event.model_dump())
    return {"ok": True}


@app.post("/api/log")
async def post_log(event: LogEvent):
    await broadcast({"type": "log", "text": event.text, "level": event.level})
    return {"ok": True}


@app.post("/api/particle")
async def post_particle(event: ParticleEvent):
    await broadcast(
        {"type": "particle", "from": event.from_agent, "to": event.to_agent}
    )
    return {"ok": True}


@app.post("/api/flash")
async def post_flash(duration: int = 600):
    await broadcast({"type": "flash", "duration": duration})
    return {"ok": True}


# --- Log file tailing ---


async def tail_log_file(path: str):
    """Tail a log file and broadcast new lines via WebSocket."""
    logger.info(f"Tailing log file: {path}")
    while not os.path.exists(path):
        await asyncio.sleep(1)

    with open(path, "r") as f:
        # Seek to end
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                line = line.strip()
                if line:
                    await broadcast({"type": "log_line", "data": line})
            else:
                await asyncio.sleep(0.2)


_log_file_path = None


@app.on_event("startup")
async def startup():
    if _log_file_path:
        asyncio.create_task(tail_log_file(_log_file_path))


def main():
    global _log_file_path
    parser = argparse.ArgumentParser(description="PixelFloor Server")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument(
        "--log-file", type=str, default=None, help="Log file to tail and broadcast"
    )
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    _log_file_path = args.log_file
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
