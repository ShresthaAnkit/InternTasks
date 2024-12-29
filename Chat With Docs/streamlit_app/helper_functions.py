from PyPDF2 import PdfReader
import re
import ollama
from ollama import ChatResponse
import numpy as np
import pandas as pd
import os
import cohere
from dotenv import load_dotenv
load_dotenv()
COHERE_KEY = os.getenv('COHERE_KEY')
co = cohere.Client(COHERE_KEY)
def get_pdf_text(pdf_path):    
    reader = PdfReader(pdf_path)    
    text_body = []    
    def visitor_body(text, cm, tm, fontDict, fontSize):
        y = tm[5]        
        if y > 50 and y < 800:            
            text_body.append(text)
    for page in reader.pages:        
        page.extract_text(visitor_text=visitor_body)        
    return ''.join(text_body)    

def chunk_by_sentence(text):
    sentence_endings = re.compile(r'([.!?])(?=\s)')
    sentences = sentence_endings.split(text)
    sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') for i in range(0, len(sentences), 2)]
    sentences = [re.sub(r'\n', ' ', sentence) for sentence in sentences]    
    sentences = [re.sub(r'\s+', ' ', sentence).strip() for sentence in sentences]
    return sentences

def chunk_by_sentence_groups(text, max_length):
    # Regular expression to match sentence-ending punctuation: . ? !
    sentence_endings = re.compile(r'([.!?])(?=\s)')
    text = re.sub(r'\s+', ' ', text).strip()
    # Split the text into sentences based on the sentence-ending punctuation
    sentences = sentence_endings.split(text)
    
    # Recombine punctuation with the sentences
    sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') for i in range(0, len(sentences), 2)]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding the sentence exceeds max_length, start a new chunk
        if len(current_chunk) + len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence.strip()
        else:
            current_chunk += sentence  # Add the sentence to the current chunk

    if current_chunk:  # Append the last chunk
        chunks.append(current_chunk)
    
    return chunks

def calculate_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def embed_chunks_llama(chunks,batch_size=500):
    embeddings = []
    for i in range(0,len(chunks),batch_size):
        batch = chunks[i:i+batch_size]
        embeddings.extend(ollama.embed(model='llama3.2', input=batch).embeddings)
    return embeddings

def embed_query_llama(query):
    return ollama.embed(model='llama3.2',input=query).embeddings[0]

def embed_query_cohere(query):
    input_type = 'search_query'    
    model = "embed-english-v3.0"
    query_embedding = co.embed(
        texts = [query],
        model = model,
        input_type = input_type,
        embedding_types= ['float']
    )
    return query_embedding.embeddings.float[0]

def embed_chunks_cohere(chunks,batch_size=500):
    model = "embed-english-v3.0"
    input_type = "search_document"

    chunk_embeddings = co.embed(
        texts = chunks,
        model = model,
        input_type = input_type,
        embedding_types=['float']
    )
    return chunk_embeddings.embeddings.float

def generate_response_llama(prompt):
    response_generator: ChatResponse = ollama.chat(model='llama3.2', messages=[
    {
        'role': 'system',
        'content': """
            You are a helpful AI assistant. Have a conversation with the user.    
        """
    },
    {
        'role': 'user',
        'content': prompt,
    },
    ],stream=True,
    options={
        'temperature':0.5
    })
    for chunk in response_generator:
        # Each chunk is a part of the response
        yield chunk.message.content

def generate_response_cohere(prompt):
    premable = 'You are a friendly bot. Don\'t ask for extra context. Read the "QUESTION:" and reply. If the question demands some information, answer the question provided as "QUESTION:" using the context provided as "CONTEXT:" If the answer is not present, say you don\'t know.'
    for event in co.chat_stream(
        model="command-r-plus-08-2024",
        message= prompt,
        preamble= premable,
        max_tokens=200,  # Control the length of the response
        temperature=0.3,  
    ):
        if event.event_type == "text-generation":
            yield event.text

def process_pdf(uploaded_file):
    text = get_pdf_text(uploaded_file)
    chunks = chunk_by_sentence(text)
    embedded_chunks = embed_chunks_cohere(chunks)
    df = pd.DataFrame({'text':chunks,'embedding':embedded_chunks})
    return df

def process_query(query,df):
    embedded_query = embed_query_cohere(query)
    df['similarity'] = df.apply(lambda x: calculate_similarity(embedded_query,x[1]),axis=1)
    df_top = df[df['similarity'] > df['similarity'].quantile(0.8)]
    context = ''
    for txt in df_top['text']:
        context+=txt
        context+='\n'
    prompt = f"""
    "QUESTION:" {query}\n
    "CONTEXT:" {context}
    """
    return prompt