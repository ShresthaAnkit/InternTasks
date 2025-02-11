from file_processor import get_file_text, save_uploaded_file_to_disk
from llm_calls import generate_embeddings, generate_query_embeddings, generate_prompt, generate_response,get_chunks


def ingest_files(id,db,name,model,description,file_paths):    
    text_blob = ''
    print("Getting file text...")
    for file_path in file_paths:        
        text = get_file_text(file_path)
        text_blob += text + '\n'
    print("Splitting into chunks...")
    chunks = get_chunks(text_blob)
    print("Embeddings chunks...")
    embedded_chunks = generate_embeddings(chunks)
    print("Inserting into Database...")
    db.insert_chunks(id,chunks, embedded_chunks,name,model,description)
    print("Completed Ingesetion")

def chat_with_kb(conversation_id,db,KB_NAME,query,model="gpt-4o-mini"):
    chunk_df = db.retrieve_KB(KB_NAME)
    if chunk_df is None:
        return 'No Knowledge base found.'
    chunk_df.drop(columns=['_score'],inplace=True)
    prompt = generate_prompt(query,chunk_df)    
    response = generate_response(prompt)        
    return response