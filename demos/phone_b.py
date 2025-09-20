import asyncio
from agentlingo import Agent, set_gemini_key, nl_to_isr
from agentlingo.codec import register_template
from agentlingo.isr import ISR

async def main():
    set_gemini_key()
    b = Agent("phone-b")
    await b.connect()

    # Phone B will turn its NL into an ISR *after* receiving A's proposal, then respond with a counter
    @b.on("schedule.propose")
    async def on_propose(agent, msg):
        # Suppose user B has: "I can only do before 4pm."
        isr_local = nl_to_isr("I can only do before 4pm, 30 to 60 minutes.")
        counter = ISR(intent="schedule.counter", slots=isr_local.slots)
        lat = Agent.register(counter)
        await agent.send_isr(["agent://phone-a"], "reply", counter, latent=lat)

    @b.on("schedule.accept")
    async def on_accept(agent, msg):
        # Finalize by confirming
        confirm = ISR(intent="schedule.confirm", slots=msg["isr"]["slots'])
        lat = Agent.register(confirm)
        await agent.send_isr(["agent://phone-a"], "reply", confirm, latent=lat)
        print("[B] Confirmed:", confirm.slots)

    await b.loop()

if __name__ == "__main__":
    asyncio.run(main())
