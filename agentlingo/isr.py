from pydantic import BaseModel, Field, field_validator
from typing import Dict, Optional
from datetime import datetime, timedelta

INTENTS = {
    "schedule.propose": ["window_start","window_end","duration_min","constraints"],
    "schedule.counter": ["window_start","window_end","duration_min","constraints"],
    "schedule.accept":  ["slot_start","slot_end"],
    "schedule.confirm": ["slot_start","slot_end"]
}

class ISR(BaseModel):
    intent: str
    slots: Dict[str, object] = Field(default_factory=dict)
    reason: Optional[Dict[str, object]] = None

    @field_validator("intent")
    @classmethod
    def ok(cls, v):
        if v not in INTENTS: raise ValueError(f"unknown intent: {v}")
        return v

def now_iso(): return datetime.utcnow().isoformat()+"Z"

def parse_iso(s): return datetime.fromisoformat(s.replace("Z",""))

def intersect(a_start, a_end, b_start, b_end):
    s = max(a_start, b_start); e = min(a_end, b_end)
    return (s, e) if s < e else None

def choose_earliest(overlap, duration_min):
    if not overlap: return None
    s, e = overlap
    if s + timedelta(minutes=duration_min) <= e:
        return (s, s + timedelta(minutes=duration_min))
    return None
