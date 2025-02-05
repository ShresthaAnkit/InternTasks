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
    model="deepseek-r1:7b",
    messages=[{"role":"system", "content": "Answer in 1 sentence."},{"role": "user", "content": prompt}]
)
    return response.choices[0].message.content

async def main():
    tasks = set()  # Store running tasks

    while True:
        prompt = input("Enter a prompt (or type 'exit' to stop): ")
        if prompt.lower() == "exit":
            break

        # Create a new task and add it to the set
        task = asyncio.create_task(call_openai(prompt))
        tasks.add(task)

        # Remove completed tasks to prevent memory leaks
        task.add_done_callback(tasks.discard)

        # Print response when done
        task.add_done_callback(lambda t: print(f"Response: {t.result()}"))

    # Wait for all tasks to finish before exiting
    if tasks:
        await asyncio.gather(*tasks)

# Run in an interactive environment
asyncio.run(main())
