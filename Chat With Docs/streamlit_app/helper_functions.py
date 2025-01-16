import numpy as np
import pandas as pd
from data_preparation import *
from data_embeddings_cohere import *
from data_embeddings_llama import *

MODEL = "LLAMA"
#MODEL = "COHERE"

def calculate_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def process_pdf(uploaded_file):
    text = get_pdf_text(uploaded_file)
    chunks = chunk_by_sentence(text)
    if MODEL == "COHERE":
        embedded_chunks = embed_chunks_cohere(chunks)
    elif MODEL == "LLAMA":
        embedded_chunks = embed_chunks_llama(chunks)
    else:
        raise Exception("Model not supported")
    df = pd.DataFrame({'text':chunks,'embedding':embedded_chunks})
    return df

def process_query(query,df):
    if MODEL == "COHERE":
        embedded_query = embed_query_cohere(query)
    elif MODEL == "LLAMA":
        print("QUERY")
        print(query)
        embedded_query = embed_query_llama(query)
    else:
        raise Exception("Model not supported")
    context = ''
    if df is not None:
        df['similarity'] = df.apply(lambda x: calculate_similarity(embedded_query,x.iloc[1]),axis=1)
        df_top = df[df['similarity'] > df['similarity'].quantile(0.8)]    
        for txt in df_top['text']:
            context+=txt
            context+='\n'
    prompt = f"""
    "QUESTION:" {query}\n
    "CONTEXT:" {context}
    """
    return prompt

def generate_response(prompt):
    if MODEL == "COHERE":
        return generate_response_cohere(prompt)
    elif MODEL == "LLAMA":
        return generate_response_llama(prompt)
    else:
        raise Exception("Model not supported")