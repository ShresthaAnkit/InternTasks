import os
import re
from dotenv import load_dotenv
import cohere
load_dotenv()

COHERE_KEY = os.getenv('COHERE_KEY')
co = cohere.Client(COHERE_KEY)

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
