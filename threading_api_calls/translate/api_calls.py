from dotenv import load_dotenv
import os
import openai
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.AsyncOpenAI()
openai.api_key = OPENAI_API_KEY

async def answer_question(prompt,model='gpt-4o-mini'):
    response = await client.chat.completions.create(
    model=model,
    messages=[{"role":"system", "content": "You are a translator from nepali to english. Give me the exact translation. Don't give any other text."},{"role": "user", "content": prompt}]
)
    print('Done: ',response.choices[0].message.content)
    return response.choices[0].message.content
