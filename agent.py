from dotenv import load_dotenv
import os
from openai import OpenAI
import requests
from pydantic import BaseModel, Field
from typing import Optional
from colorama import Fore, Style

load_dotenv()

# ---------------- CONFIG ----------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_URL = "https://api.weatherapi.com/v1/current.json"

# ---------------- WEATHER TOOL ----------------
def get_weather(location: str) -> str:
    url = f"{WEATHER_URL}?key={WEATHER_API_KEY}&q={location}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return f"{location}: {data['current']['temp_c']}°C, {data['current']['condition']['text']}"
    else:
        return "Weather API failed."

available_tools = {
    "get_weather": get_weather
}

tool_aliases = {
    "weather": "get_weather",
    "getweather": "get_weather",
    "get_weather": "get_weather"
}

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are JOSH, an AI agent that solves problems step-by-step.

Workflow:
START → PLAN → TOOL (optional) → PLAN → OUTPUT

Rules:
- Always reply ONLY in JSON.
- Only ONE step per response.
- Use TOOL step for weather questions.

JSON format:
{
 "step": "START | PLAN | TOOL | OUTPUT",
 "content": "text",
 "tool": "tool_name (only if TOOL step)",
 "input": "tool input (only if TOOL step)"
}
"""

# ---------------- STRUCTURED OUTPUT MODEL ----------------
class MyOutputFormat(BaseModel):
    step: str = Field(..., description="START, PLAN, TOOL, OUTPUT")
    content: Optional[str] = None
    tool: Optional[str] = None
    input: Optional[str] = None


# ---------------- CHAT LOOP ----------------
print("-" * 50)

messages = [{"role": "system", "content": SYSTEM_PROMPT}]

user_query = input("Ask: ")
messages.append({"role": "user", "content": user_query})

while True:

    response = client.chat.completions.parse(
        model="gpt-4.1-mini",
        response_format=MyOutputFormat,
        messages=messages
    )

    result = response.choices[0].message.parsed
    step = result.step

    # Always send assistant JSON back into history
    messages.append({
        "role": "assistant",
        "content": result.model_dump_json()
    })

    # -------- START --------
    if step == "START":
        print("🚀 Starting reasoning...")
        continue

    # -------- PLAN --------
    elif step == "PLAN":
        print("🧠 PLAN:", result.content)
        continue

    # -------- TOOL --------
    elif step == "TOOL":
        tool_name = result.tool.lower().strip()
        tool_input = result.input

        tool_name = tool_aliases.get(tool_name, tool_name)

        if tool_name not in available_tools:
            print("❌ Unknown tool:", tool_name)
            break

        print(f"🔧 Calling tool → {tool_name}({tool_input})")
        tool_result = available_tools[tool_name](tool_input)
        print("📡 Tool result:", tool_result)

        # Send tool result back to model
        messages.append({
            "role": "assistant",
            "content": f"Tool result: {tool_result}"
        })
        continue

    # -------- OUTPUT --------
    elif step == "OUTPUT":
        print(Fore.GREEN + "\nFINAL ANSWER:")
        print(result.content + Style.RESET_ALL)
        break
