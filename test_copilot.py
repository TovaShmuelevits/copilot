import asyncio
import random
import sys
from copilot import CopilotClient
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType
from pydantic import BaseModel, Field

# --- הגדרת פרמטרים לכלי ---
class GetWeatherParams(BaseModel):
    city: str = Field(description="The name of the city to get weather for")

# --- כלי מותאם אישית: מזג אוויר ---
@define_tool(description="Get the current weather for a city")
async def get_weather(params: GetWeatherParams) -> dict:
    conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
    temp = random.randint(50, 80)
    condition = random.choice(conditions)
    return {"city": params.city, "temperature": f"{temp}°F", "condition": condition}

# --- פונקציה ראשית ---
async def main():
    # יצירת client
    client = CopilotClient()
    await client.start()

    # יצירת session עם מודל, כלי, MCP וסוכן מותאם אישית
    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": [get_weather],
        "mcp_servers": {
            "github": {
                "type": "http",
                "url": "https://api.githubcopilot.com/mcp/",
            },
        },
        "custom_agents": [{
            "name": "pr-reviewer",
            "display_name": "PR Reviewer",
            "description": "Reviews pull requests for best practices",
            "prompt": "You are an expert code reviewer. Focus on security, performance, and maintainability.",
        }],
    })

    # --- טיפול באירועי streaming ---
    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        if event.type == SessionEventType.SESSION_IDLE:
            print()  # שורה חדשה בסיום תשובה

    session.on(handle_event)

    # --- CLI אינטראקטיבי ---
    print("Weather & GitHub Assistant (type 'exit' to quit)")
    print("Try: 'What's the weather in Paris?' or 'Check the last PR'\n")

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            break

        if user_input.lower() == "exit":
            break

        sys.stdout.write("Assistant: ")
        await session.send_and_wait({"prompt": user_input})
        print("\n")

    # --- סיום client ---
    await client.stop()

# הפעלת הפונקציה הראשית
asyncio.run(main())
