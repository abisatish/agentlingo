import json
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AgentLingo P2P Broker")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUBS: Dict[str, Set[WebSocket]] = {}
AGENTS: Dict[str, WebSocket] = {}

@app.websocket("/ws/{agent_id}")
async def ws(agent_id: str, ws: WebSocket):
    await ws.accept()
    AGENTS[agent_id] = ws
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            if msg.get("kind") == "control.subscribe":
                for t in msg.get("topics", []):
                    SUBS.setdefault(t, set()).add(ws)
                await ws.send_text(json.dumps({"kind":"ack"}))
                continue

            delivered = 0
            for r in msg.get("to", []):
                if r.startswith("agent://"):
                    aid = r.split("agent://",1)[1]
                    w = AGENTS.get(aid)
                    if w: await w.send_text(json.dumps(msg)); delivered += 1
                elif r.startswith("topic://"):
                    t = r.split("topic://",1)[1]
                    for w in SUBS.get(t, set()):
                        await w.send_text(json.dumps(msg)); delivered += 1
            await ws.send_text(json.dumps({"kind":"delivered","count":delivered}))
    except WebSocketDisconnect:
        for s in SUBS.values(): s.discard(ws)
        AGENTS.pop(agent_id, None)
