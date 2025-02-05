from dotenv import load_dotenv
import os
import openai
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI()
openai.api_key = OPENAI_API_KEY
import asyncio
async def call_openai(prompt):
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"system", "content": "Answer in 1 sentence."},{"role": "user", "content": prompt}]
)
    return response.choices[0].message.content

async def main():
    prompts = ["Tell me a joke", "What is AI?", "Explain quantum computing"]
    
    # Run multiple API calls concurrently
    responses = await asyncio.gather(*(call_openai(prompt) for prompt in prompts))
    
    for i, response in enumerate(responses):
        print(f"Response {i+1}: {response}")
asyncio.run(main())