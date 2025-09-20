import os, json
from google import genai
from .isr import ISR

_client = None

def set_gemini_key(api_key: str = None):
    global _client
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY env var or call set_gemini_key(api_key)")
    _client = genai.Client(api_key=api_key)

PROMPT = """You are a planner. Convert the user text into JSON of this shape ONLY:
{ "intent": "schedule.propose",
  "slots": { "window_start": ISO8601, "window_end": ISO8601, "duration_min": int, "constraints": [] },
  "reason": { "assumptions":[], "preferences":[], "conflicts":[], "confidence":0.8, "justification":"" }
}
User: <<<{}>>>
Return only JSON with double quotes and valid fields.
"""

def nl_to_isr(text: str) -> ISR:
    global _client
    if _client is None:
        set_gemini_key()
    resp = _client.models.generate_content(
        model="gemini-1.5-flash",
        contents=PROMPT.format(text),
        config={"temperature":0.2}
    )
    txt = resp.candidates[0].content.parts[0].text
    data = json.loads(txt)
    # tolerate missing optional fields
    data.setdefault("reason", None)
    return ISR(**data)
