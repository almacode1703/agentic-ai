from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """You are a highly intelligent mathematical assistant. You will only respond to queries related to mathematics, including solving problems, explaining concepts, and providing mathematical insights. If a query is not related to mathematics, politely inform the user that you can only assist with mathematical topics."""

response = client.chat.completions.create(
    model="gpt-4o-mini", 
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Whats the capital of France?"}
    ]
)

print(response.choices[0].message.content)

# zero-shot-prompting :
#  
# Few-shot prompting :