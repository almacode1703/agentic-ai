import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an expert AI assistant that solves user queries using a structured reasoning workflow.

Workflow:
1) START
2) PLAN (can repeat)
3) OUTPUT (final answer)

Rules:
- Always respond ONLY in valid JSON.
- Execute ONLY one step per response.
- Format:
{ "step": "START | PLAN | OUTPUT", "content": "string" }
"""



messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

user_query = input("Enter your question: ")

messages.append({"role": "user", "content": user_query})




print("\nAgent started...\n")

while True:     
    response = client.responses.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        input=messages
    )

    reply_text = response.output_text.strip()
    print("RAW:", reply_text)

    # 🔥 Convert string → Python dict
    try:
        reply_json = json.loads(reply_text)
    except json.JSONDecodeError:
        print("Model did not return valid JSON")
        break

    # Pretty print JSON
    print("PARSED:", json.dumps(reply_json, indent=2))

    # Add assistant message back to conversation
    messages.append({
        "role": "assistant",
        "content": json.dumps(reply_json)  # 🔥 send back as JSON string
    })

    # Stop when OUTPUT step arrives
    if reply_json["step"] == "OUTPUT":
        print("\nFinal Answer Reached ✅")
        break
