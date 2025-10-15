import json
import os
from agents import Agent, Runner
from app.services.bot_service import config
from app.db.connection import SessionLocal
from sqlalchemy import select
from app.models.memory import MemoryFact
from mem0 import MemoryClient


# ✅ Initialize Mem0 Client
memo_api_key = os.getenv("MEM0_API_KEY")
mem_client = MemoryClient(memo_api_key)

# ✅ Save in NeonDB
async def save_memory_fact(user_id: str, key: str, value: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(MemoryFact).where(
                MemoryFact.user_id == user_id,
                MemoryFact.key == key
            )
        )
        obj = result.scalars().first()

        if obj:
            obj.value = value  # type: ignore
        else:
            obj = MemoryFact(user_id=user_id, key=key, value=value)
            session.add(obj)

        await session.commit()
        return obj


# ✅ Get Memories from NeonDB
async def get_memory_facts(user_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(MemoryFact.key, MemoryFact.value).where(MemoryFact.user_id == user_id)
        )
        return dict([tuple(row) for row in result.all()])


# ✅ Memory Agent Instructions
memory_agent: Agent = Agent(
    name="Memory Agent",
    instructions=(
        """
        You are an intelligent Memory Extraction Assistant named Yaram Kazmi.
        Your role is to analyze user messages and decide—using your own reasoning—what should be stored in memory for future use.

        ✅ Use your own intelligence (like mem0AI) to identify:
        - User preferences (likes, dislikes, tone, style)
        - Long-term goals or plans
        - Ongoing projects or tasks
        - Personal instructions from the user
        - Habits or routines
        - Anything that may help in future conversations

        ✅ If something seems useful for later, set "should_save": true.
        ✅ If the message is irrelevant, temporary, or not useful, set "should_save": false.

        ✅ Output Rules:
        You must return ONLY a valid JSON object in one of the following formats:

        If something should be saved:
        {
            "should_save": true,
            "key": "string",
            "value": "string"
        }

        If nothing should be saved:
        {
            "should_save": false,
            "key": "",
            "value": ""
        }

        ❌ Do NOT add:
        - Explanations
        - Extra text
        - Markdown
        - Quotes
        - Commentary

        ✅ You are allowed to decide what to save even if the user does not explicitly ask.
        Always think intelligently about whether the information is valuable in the future.
        """
    )
)


# ✅ Main Function
async def extract_and_save_memory(user_id, user_text):

    memory_prompt = f"""
You are a smart memory extraction assistant.
Analyze the user's message and decide if something should be stored for future use.
Use your intelligence to detect preferences, instructions, ongoing tasks, habits, or personal details that may help later.

Return ONLY valid JSON in exactly one of these formats:

If something should be saved:
{{
  "should_save": true,
  "key": "string",
  "value": "string"
}}

If nothing should be saved:
{{
  "should_save": false,
  "key": "",
  "value": ""
}}

Do NOT add explanations, notes, markdown, or extra text.

User message: "{user_text}"
"""

    memory_result = await Runner.run(memory_agent, memory_prompt, run_config=config)
    print("🟡 MEMORY RAW RESPONSE:", memory_result.final_output)

    try:
        cleaned = memory_result.final_output.strip().replace("```json", "").replace("```", "").strip()
        response_json = json.loads(cleaned)

        if response_json.get("should_save"):
            key = response_json.get("key")
            value = response_json.get("value")

            if key and value:
                # ✅ Step 1: Save in Mem0AI
                content = f"{key}: {value}"
                mem_client.add(
                    [{"role": "user", "content": content}],
                    user_id=user_id
                )

                # ✅ Step 2: Save in Neon DB
                await save_memory_fact(user_id, key, value)

        return user_id  # ✅ Return user_id if needed later

    except Exception as e:
        print("❌ JSON Error:", e)
        print("RAW:", memory_result.final_output)
        return user_id  # Return user_id even if exception