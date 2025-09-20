import asyncio
from agentlingo import Agent, set_gemini_key, nl_to_isr
from agentlingo.codec import register_template
from agentlingo.isr import parse_iso, intersect, choose_earliest, ISR

async def main():
    set_gemini_key()  # expects GEMINI_API_KEY env var
    a = Agent("phone-a")
    await a.connect()

    text = "can we meet tomorrow afternoon for 45 minutes?"
    isr = nl_to_isr(text)
    lat = Agent.register(isr)
    await a.send_isr(["agent://phone-b"], "ask", isr, latent=lat)

    @a.on("schedule.counter")
    async def on_counter(agent, msg):
        other = msg["isr"]
        ow = intersect(parse_iso(isr.slots["window_start"]),
                       parse_iso(isr.slots["window_end"]),
                       parse_iso(other["slots"]["window_start"]),
                       parse_iso(other["slots"]["window_end"]))        
        slot = choose_earliest(ow, isr.slots["duration_min"]) if ow else None
        if slot:
            reply = ISR(intent="schedule.accept", slots={
                "slot_start": slot[0].isoformat()+"Z",
                "slot_end": slot[1].isoformat()+"Z"
            })
            lat2 = Agent.register(reply)
            await agent.send_isr(["agent://phone-b"], "reply", reply, latent=lat2)

    @a.on("schedule.confirm")
    async def on_confirm(agent, msg):
        print("[A] Confirmed:", msg["isr"]["slots"])

    await a.loop()

if __name__ == "__main__":
    asyncio.run(main())
