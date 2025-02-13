import os
import re
from dotenv import load_dotenv
import openai
load_dotenv()

from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import PCAModel
import yaml

def load_config(file_path=r"Chat With Docs\better_app\fastapi\config.yaml"):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

config = load_config()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_KEY)

# Function to generate embeddings using OpenAI
# text-embedding-ada-002
def generate_embeddings(texts,model="text-embedding-3-small"):        
    embeddings = []
    embedding_tokens = []
    for text in texts:
        response = client.embeddings.create(input=text, model=model)
        embeddings.append(response.data[0].embedding)
        embedding_tokens.append(response.usage.total_tokens)
    
    return embeddings,embedding_tokens

def generate_query_embeddings(query,model="text-embedding-3-small"):
    response = client.embeddings.create(input=query, model=model)
    return response

def get_chunks(text,chunk_size=1000):
    # Create an instance of RecursiveCharacterTextSplitter
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['constants']['chunk_size'],  # Define the chunk size
        chunk_overlap=100,  # Define the overlap size
        length_function=len  # Defines how length is measured
    )

    #Split the document into chunks
    chunks = recursive_splitter.split_text(text)
    return chunks

def generate_context(chunk_df):    
    context = ''
    if chunk_df.empty:
        return ''
    for txt in chunk_df['text']:

        context+=txt
        context+='\n'    
    return context
def generate_prompt(query,context):        
    prompt = f"""
    "QUESTION:" {query}\n
    "CONTEXT:" {context}
    """
    return prompt

def create_history_message(message_history):
    messages = []
    for idx,message in enumerate(message_history):
        if (idx+1) % 2 == 0:
            messages.append({"role": "assistant", "content": message})
        else:
            messages.append({"role": "user", "content": message})
    return messages

def generate_response(prompt,message_history,model="gpt-4o-mini"):
    premable = config['prompts']['chat_prompt']

    messages = [{'role':'system','content':premable}]
    history = create_history_message(message_history)
    messages.extend(history)
    messages.append({'role':'user','content':prompt})    
    
    response = client.chat.completions.create(
        model=model, 
        messages=messages,
        max_tokens=150,  # You can adjust the max tokens based on your needs
        temperature=0.5,  # Adjust temperature for randomness (optional)
    )
    return response

def perform_pca_call(history,chunks):
    PCA_PROMPT = config['prompts']['pca_prompt']
    message_history = create_history_message(history)

    kb = '\n'.join(chunks) + "\n Here is the conversation history:"

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content":PCA_PROMPT
            },
            {
                "role":"user",
                "content":kb
            },
            *message_history
        ],
        response_format=PCAModel,
    )
    return response