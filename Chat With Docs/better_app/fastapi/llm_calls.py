import os
import re
from dotenv import load_dotenv
import openai
load_dotenv()
from utils import calculate_similarity
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import PCAModel

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
        chunk_size=chunk_size,  # Define the chunk size
        chunk_overlap=100,  # Define the overlap size
        length_function=len  # Defines how length is measured
    )

    #Split the document into chunks
    chunks = recursive_splitter.split_text(text)
    return chunks

def generate_context(embedded_query,chunk_df):
    chunk_df['similarity'] = chunk_df.apply(lambda x: calculate_similarity(embedded_query,x.iloc[3]),axis=1)    
    df_top = chunk_df[chunk_df['similarity'] > chunk_df['similarity'].quantile(0.8)]      
    context = ''
    for txt in df_top['text']:
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
    premable = """
    You are a friendly bot. Don\'t ask for extra context. Read the "QUESTION:" and reply. 
    If the question demands some information, 
    answer the question provided as "QUESTION:"
    using the context provided as "CONTEXT:" 
    If the answer is not present, say you don\'t know.
    The history maybe be provided as a chat between the user and the assistant.
    If history is provided, take reference from it to answer the question but don't provide facts based on that history.
    """   

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
    PCA_PROMPT = """
        You are a friendly assistant that performs analysis on conversation history. Based on the user's conversation history, generate the following information:
        1. Sentiment score: A score from 0 to 10 where 0 means negative and 10 means positive. Provide a brief feedback to justify the score.
        2. Context gaps: A list of gaps in the context of the conversation that might affect the quality of the generated response. Identify any missing context from the conversation history that could improve the response using the knowledge base provided below.
        3. Tags: A list of topics that are being discussed in the conversation. Include keywords or important subjects that should be tagged.

        Please use the conversation history provided below to generate these three pieces of information:
        - Sentiment (score and feedback)
        - Context gaps (if any)
        - Tags (list of relevant topics)

        The conversation history and knowledge base will be provided as a chat between the user and the assistant.

        Here is the knowledge base:
    """
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