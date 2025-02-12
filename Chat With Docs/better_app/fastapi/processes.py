import pandas as pd
import json
from itertools import chain
from file_processor import get_file_text, save_uploaded_file_to_disk
from llm_calls import generate_embeddings, generate_query_embeddings, generate_prompt, generate_response,get_chunks,generate_context,perform_pca_call
from database import Database
db = Database()

def add_knowledgebase(kb_id,KB_NAME,model,description):
    db.create_kb(kb_id,KB_NAME,model,description)

def ingest_files(id,model,file_paths):    
    text_blob = ''
    print("Getting file text...")
    for file_path in file_paths:        
        text = get_file_text(file_path)
        text_blob += text + '\n'
    print("Splitting into chunks...")
    chunks = get_chunks(text_blob)
    print("Embeddings chunks...")
    embedded_chunks,embedding_tokens = generate_embeddings(chunks)
    print("Inserting into Database...")
    db.insert_chunks(id,chunks, embedded_chunks,embedding_tokens,model)
    print("Completed Ingesetion")

def get_kb_from_id(kb_id):
    return db.get_kb_from_id(kb_id)

def check_if_kb_already_exist(KB_NAME):
    return db.check_already_exist(KB_NAME)

def get_conversation_ids():
    return db.get_conversation_ids()['conversation_id'].tolist()  

def check_if_conversation_exists(conversation_id):
    return db.check_if_conversation_exists(conversation_id)

def get_conversation_from_id(conversation_id):
    return db.get_conversation_from_id(conversation_id)      

def get_conversation_df(conversation_id):
    conversation_df = db.get_conversation_from_id(conversation_id)
    conversation_df['timestamp'] = pd.to_datetime(conversation_df['timestamp'])
    conversation_df = conversation_df.sort_values(by='timestamp',ascending=True)    
    return conversation_df

def chat_with_kb(conversation_id,kb_id,query,model="gpt-4o-mini"):
    chunk_df = db.retrieve_KB(kb_id)
    
    if chunk_df is None:
        return 'No Knowledge base found.'
    chunk_df.drop(columns=['_score'],inplace=True)
    history = []
    if check_if_conversation_exists(conversation_id):        
        history = get_conversation_df(conversation_id)['text'].tail(4).tolist()
        
    
    query_response = generate_query_embeddings(query) 
    embedded_query = query_response.data[0].embedding    
    embedding_token = query_response.usage.total_tokens
    db.add_to_conversation(
        conversation_id=conversation_id,
        sender='user',
        text=query,
        kb_id=chunk_df.iloc[0]['kb_id'],
        embedding_tokens=embedding_token,
        prompt_tokens=0,
        completition_tokens=0,
        chunk_id=[],
    )    
    context = generate_context(embedded_query,chunk_df)
    prompt = generate_prompt(query,context)    
    response = generate_response(prompt,history)          
    response_text = response.choices[0].message.content  
    db.add_to_conversation(
        conversation_id=conversation_id,
        sender='system',
        text=response_text,
        kb_id=chunk_df.iloc[0]['kb_id'],
        chunk_id=list(chunk_df['chunk_id']),
        embedding_tokens=0,
        prompt_tokens=response.usage.prompt_tokens,
        completition_tokens=response.usage.completion_tokens,        
    )    
    return response_text

def perform_pca(conversation_id):
    conversation_df = get_conversation_df(conversation_id)
    print("Getting history")
    history = conversation_df['text'].tolist()
    print("Getting chunk ids")
    chunk_id_list = list(conversation_df['chunk_id'])
    unique_chunk_ids = list(set(list(chain(*chunk_id_list))))
    print("Getting chunks")
    chunks = db.get_chunks_from_id(unique_chunk_ids)
    print("Performing pca call")
    response = perform_pca_call(history,chunks)
    response_text = response.choices[0].message.content  
    prompt_tokens = response.usage.prompt_tokens
    completition_tokens = response.usage.completion_tokens
    print("Inserting to db")
    db.insert_pca(conversation_id,json.loads(response_text),prompt_tokens,completition_tokens)
    print("Inserted")
    return response_text

def get_all_kbs():
    return db.get_all_kbs()