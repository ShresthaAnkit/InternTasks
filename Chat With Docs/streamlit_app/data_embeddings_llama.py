import ollama
from ollama import ChatResponse

def embed_chunks_llama(chunks,batch_size=500):
    embeddings = []
    for i in range(0,len(chunks),batch_size):
        batch = chunks[i:i+batch_size]
        embeddings.extend(ollama.embed(model='llama3.2', input=batch).embeddings)
    return embeddings

def embed_query_llama(query):
    return ollama.embed(model='llama3.2',input=query).embeddings[0]


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
