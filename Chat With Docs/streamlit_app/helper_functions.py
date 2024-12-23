from PyPDF2 import PdfReader
import re
import ollama
from ollama import ChatResponse
import numpy as np
import pandas as pd
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

def chunk_by_sentence(text, max_length):
    # Regular expression to match sentence-ending punctuation: . ? !
    sentence_endings = re.compile(r'([.!?])')
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

def embed_chunks(chunks,batch_size=500):
    embeddings = []
    for i in range(0,len(chunks),batch_size):
        batch = chunks[i:i+batch_size]
        embeddings.extend(ollama.embed(model='llama3.2', input=batch).embeddings)
    return embeddings

def embed_query(query):
    return ollama.embed(model='llama3.2',input=query).embeddings[0]

def generate_response(prompt):
    response_generator: ChatResponse = ollama.chat(model='llama3.2', messages=[
    {
        'role': 'user',
        'content': prompt,
    },
    ],stream=True)
    for chunk in response_generator:
        # Each chunk is a part of the response
        yield chunk.message.content

def process_pdf(uploaded_file):
    text = get_pdf_text(uploaded_file)
    chunks = chunk_by_sentence(text,400)
    embedded_chunks = embed_chunks(chunks)
    df = pd.DataFrame({'text':chunks,'embedding':embedded_chunks})
    return df

def process_query(query,df):
    embedded_query = embed_query(query)
    df['similarity'] = df.apply(lambda x: calculate_similarity(embedded_query,x[1]),axis=1)
    top_5_similar = df.sort_values(by='similarity', ascending=False)
    # Input prompt for the model
    prompt = f"""
    Use only the context provided to answer the following question. If the answer is not present in the context, say you don't know.
    Context: {' '.join(top_5_similar.iloc[:,0])}
    Question: {query}
    """
    return prompt