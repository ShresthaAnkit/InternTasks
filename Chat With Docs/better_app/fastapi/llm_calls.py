import os
import re
from dotenv import load_dotenv
import openai
load_dotenv()
from utils import calculate_similarity
from langchain.text_splitter import RecursiveCharacterTextSplitter

OPENAI_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=OPENAI_KEY)

# Function to generate embeddings using OpenAI
# text-embedding-ada-002
def generate_embeddings(texts):        
    embeddings = []
    for text in texts:
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        embeddings.append(response.data[0].embedding)
    
    return embeddings

def generate_query_embeddings(query):
    response = client.embeddings.create(input=query, model="text-embedding-ada-002")
    return response.data[0].embedding

def get_chunks(text,chunk_size=1000):
    # Create an instance of RecursiveCharacterTextSplitter
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,  # Define the chunk size
        chunk_overlap=100,  # Define the overlap size
        length_function=len  # Defines how length is measured
    )

    #Split the document into chunks
    chunks = recursive_splitter.split_text(text)
    return chunks

def generate_prompt(query,chunk_df):
    embedded_query = generate_query_embeddings(query) 
    chunk_df['similarity'] = chunk_df.apply(lambda x: calculate_similarity(embedded_query,x.iloc[3]),axis=1)    
    df_top = chunk_df[chunk_df['similarity'] > chunk_df['similarity'].quantile(0.8)]      
    context = ''
    for txt in df_top['text']:
        context+=txt
        context+='\n'
    prompt = f"""
    "QUESTION:" {query}\n
    "CONTEXT:" {context}
    """
    return prompt

def generate_response(prompt):
    premable = 'You are a friendly bot. Don\'t ask for extra context. Read the "QUESTION:" and reply. If the question demands some information, answer the question provided as "QUESTION:" using the context provided as "CONTEXT:" If the answer is not present, say you don\'t know.'
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[{'role':'system','content':premable},{'role':'user','content':prompt}],
        max_tokens=150,  # You can adjust the max tokens based on your needs
        temperature=0.5,  # Adjust temperature for randomness (optional)
    )
    return response.choices[0].message.content