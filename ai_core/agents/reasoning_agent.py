from ai_core.agents.base_agent import BaseAgent
from ai_core.config import ai_config

class ReasoningAgent(BaseAgent):
    """
    Takes the rewritten query and retrieved context to generate a comprehensive,
    step-by-step emergency response.
    """

    async def execute(self, query: str, context: str) -> str:
        """
        Generates the final answer based ONLY on the context.
        """
        prompt = (
            f"User Question: {query}\n\n"
            f"Available Safety Context:\n{context}\n\n"
            "Based strictly on the provided context, answer the user's question. "
            "If the answer is not in the context, state that clearly."
        )
        
        answer = self._generate_content(
            prompt=prompt,
            system_instruction=ai_config.REASONING_PROMPT
        )
        
        return answer.strip()

    def _get_mock_response(self) -> str:
        return (
            "🚨 **FIRE EMERGENCY — Immediate Action Protocol**\n\n"
            "**For Guests:**\n"
            "1. **Activate the alarm** — Pull the nearest fire alarm pull station.\n"
            "2. **Alert others** — Knock on nearby doors and shout 'Fire!' as you exit.\n"
            "3. **Use stairs only** — Do NOT use elevators during a fire evacuation.\n"
            "4. **Feel doors before opening** — If a door is hot, do not open it. Find an alternate exit.\n"
            "5. **Stay low** — Crawl below smoke if visibility is reduced.\n"
            "6. **Proceed to assembly point** — Go to the designated assembly area in the main parking lot.\n"
            "7. **Call 911** — Once safely outside, call emergency services immediately.\n\n"
            "**For Staff:**\n"
            "1. **Call Fire Department** — Dial 911 immediately; do not assume someone else has called.\n"
            "2. **Activate the alarm** — Trigger the fire alarm panel at the front desk.\n"
            "3. **Evacuate guests** — Begin floor-by-floor guest evacuation using the buddy system.\n"
            "4. **Report to Incident Commander** — Assemble at the front lobby command post.\n"
            "5. **Account for all guests** — Use the guest registry to confirm all guests are out.\n"
            "6. **Log the incident** — Record the event in the CrisisBridge system to trigger coordinated response.\n\n"
            "⚠️ *Never re-enter the building until the fire department gives the all-clear.*\n\n"
            "📞 **Emergency Contacts:** Fire/Police/Medical → **911** | Front Desk → **0**"
        )
