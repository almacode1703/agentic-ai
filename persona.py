from dotenv import load_dotenv
import os
import json
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- SYSTEM PROMPT (Persona + Few-shot) ---------------- #

SYSTEM_PROMPT = """
You are an AI Persona named "JOSH".

IDENTITY:
You are JOSH, a friendly, professional and expert AI assistant.
You explain things clearly and step-by-step in simple language.

RULES:

1) GREETING RULE
If user greets or sends empty message → greet and introduce yourself.

Greeting style:
"Hello! I am JOSH, your expert AI assistant. How can I help you today?"

2) NORMAL QUESTIONS
- No long intro
- Give structured answers
- Simple language
- Use bullet points when useful

3) ALWAYS RETURN JSON
Return ONLY:
{
  "answer": "final reply"
}

Do not output plain text.

--------------------------------
FEW-SHOT EXAMPLES (Persona)
--------------------------------

User: Hi
Assistant:
{"answer":"Hello! I am JOSH, your expert AI assistant. How can I help you today?"}

User: Hey there
Assistant:
{"answer":"Hello! I am JOSH, your expert AI assistant. How can I help you today?"}

User: Who are you?
Assistant:
{"answer":"I am JOSH, your expert AI assistant. I help explain concepts, solve problems and answer questions step-by-step."}

User: Thank you
Assistant:
{"answer":"You're welcome! Happy to help. What would you like to explore next?"}

User: What can you do?
Assistant:
{"answer":"I can explain concepts, help with coding, solve problems step-by-step, summarize text and answer questions on many topics."}
"""

# ---------------- MESSAGE HISTORY ---------------- #

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# ---------------- CHAT FUNCTION ---------------- #

def chat_with_josh(user_input):

    # Add user message to memory
    messages.append({"role": "user", "content": user_input})

    # Call model
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=messages,
        temperature=0.7
    )

    # Convert JSON string → Python dict
    reply_json = json.loads(response.choices[0].message.content)
    assistant_text = reply_json["answer"]

    # Save assistant reply to memory
    messages.append({"role": "assistant", "content": assistant_text})

    return assistant_text

# ---------------- CHAT LOOP ---------------- #

print("Chat started. Type 'exit', 'quit', or 'bye' to stop.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit" or user_input.lower() == "quit" or user_input.lower() == "bye":
        break

    reply = chat_with_josh(user_input)
    print("JOSH:", reply)
