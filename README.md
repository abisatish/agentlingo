# AgentLingo P2P (Gemini-Edge)

Two peer agents negotiate a meeting **without a coordinator**.
They talk in a compact **latent format** on the wire, while using **Gemini** at the edges to map natural language ↔ structured ISR.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Start the broker
uvicorn broker.server:app --reload --port 8765

# 2) Set your Gemini key
export GEMINI_API_KEY=YOUR_KEY

# 3) Run the two peers in separate terminals
python demos/phone_b.py
python demos/phone_a.py
```

You should see Phone A propose (from NL via Gemini), Phone B counter (from its own NL via Gemini), A accepts, B confirms.
All packets can be made **latent-only** after the first template registration.
# agentlingo
