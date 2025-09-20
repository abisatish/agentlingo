import json, asyncio, websockets, uuid
from typing import Callable, Dict, Any, List
from .isr import ISR, now_iso
from .codec import register_template, decode_latent

class Agent:
    def __init__(self, agent_id: str, broker_ws="ws://localhost:8765/ws"):
        self.id = agent_id
        self.url = f"{broker_ws}/{agent_id}"
        self.ws = None
        self.handlers: Dict[str, Callable[[Dict[str,Any]], Any]] = {}

    async def connect(self, topics: List[str] = None):
        self.ws = await websockets.connect(self.url)
        if topics:
            await self.ws.send(json.dumps({"kind":"control.subscribe","topics":topics}))

    def on(self, intent: str):
        def deco(fn): self.handlers[intent] = fn; return fn
        return deco

    async def send_isr(self, to: List[str], kind: str, isr: ISR, latent=None, meta=None):
        env = {
            "from": f"agent://{self.id}",
            "to": to,
            "ts": now_iso(),
            "kind": kind,          # ask|reply|reason|event
            "cap": isr.intent,     # route by intent
            "isr": isr.model_dump(mode="json"),
            "latent": latent or {},
            "meta": meta or {"corr_id": str(uuid.uuid4())}
        }
        await self.ws.send(json.dumps(env))

    async def send_latent_only(self, to: List[str], kind: str, latent: dict, cap: str, meta=None):
        env = {
            "from": f"agent://{self.id}",
            "to": to,
            "ts": now_iso(),
            "kind": kind,
            "cap": cap,
            "latent": latent,
            "meta": meta or {"corr_id": str(uuid.uuid4())}
        }
        await self.ws.send(json.dumps(env))

    async def loop(self):
        while True:
            raw = await self.ws.recv()
            msg = json.loads(raw)
            # hydrate ISR from latent if necessary
            isr = msg.get("isr")
            if not isr and msg.get("latent"):
                isr = decode_latent(msg["latent"])  # may be None until template shared
                if isr: msg["isr"] = isr
            cap = (msg.get("cap") or (msg.get("isr") or {}).get("intent"))
            h = self.handlers.get(cap)
            if h: await h(self, msg)

    @staticmethod
    def register(isr: ISR):
        return register_template(isr.model_dump(mode="json"))
