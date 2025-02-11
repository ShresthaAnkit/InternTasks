import pandas as pd
import json
from file_processor import get_file_text, save_uploaded_file_to_disk
from llm_calls import generate_embeddings, generate_query_embeddings, generate_prompt, generate_response,get_chunks,generate_context,perform_pca_call
from database import Database
db = Database()

def ingest_files(id,name,model,description,file_paths):    
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
    db.insert_chunks(id,chunks, embedded_chunks,embedding_tokens,name,model,description)
    print("Completed Ingesetion")

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

def chat_with_kb(conversation_id,KB_NAME,query,model="gpt-4o-mini"):
    chunk_df = db.retrieve_KB(KB_NAME)
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
    history = get_conversation_df(conversation_id)['text'].tolist()
    print("Performing pca call")
    response = perform_pca_call(history)
    response_text = response.choices[0].message.content  
    prompt_tokens = response.usage.prompt_tokens
    completition_tokens = response.usage.completion_tokens
    print("Inserting to db")
    db.insert_pca(conversation_id,json.loads(response_text),prompt_tokens,completition_tokens)
    print("Inserted")
    return response_text