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
    print(f"Response: {response.choices[0].message.content}")  # Print as soon as done

async def get_input():
    """Run input in a separate thread to prevent blocking the event loop."""
    loop = asyncio.get_running_loop()
    return await asyncio.to_thread(input, "Enter a prompt (or 'exit' to stop): ")

async def main():
    tasks = set()
    while True:
        prompt = await get_input()  # Non-blocking input
        if prompt.lower() == "exit":
            break

        # Create and track tasks dynamically
        task = asyncio.create_task(call_openai(prompt))
        tasks.add(task)
        task.add_done_callback(tasks.discard)  # Remove completed tasks

    if tasks:
        await asyncio.gather(*tasks)  # Ensure all tasks finish before exiting

asyncio.run(main())
