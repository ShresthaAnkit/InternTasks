from fastapi import FastAPI, File, UploadFile,BackgroundTasks, Query
from fastapi.responses import JSONResponse
import uuid
from database import Database
from processes import *
import json
import ast
import numpy as np
app = FastAPI(
    title="Chat with Docs",
    description="""
    This API allows you to upload files and chat with them.
    """
)

@app.post("/ingest")
async def ingest_route(name: str, model: str, description: str,background_tasks: BackgroundTasks, file_list: list[UploadFile] = File(...)):        
    try:                
        if check_if_kb_already_exist(name): 
            return JSONResponse(content={"error": "Knowledge base already exists."}, status_code=400)
        if not file_list:
            return JSONResponse(content={"error": "No files uploaded."}, status_code=400)
        file_paths = []
        for file in file_list:
            file_paths.append(save_uploaded_file_to_disk(file))
        process_id = str(uuid.uuid4())
        add_knowledgebase(process_id,name,model,description)
        print("Adding Background task.")
        background_tasks.add_task(ingest_files,process_id,model,file_paths)                            
        return JSONResponse(content={"response": f"Successfully added for ingestion with id: {process_id}"}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@app.get('/get_all_kbs')
def get_all_kbs_route():
    try:
        df = get_all_kbs()
        json_data = df.to_json(orient='records')
        return JSONResponse(content=json.loads(json_data), status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get('/get_kb_status')
def get_kb_status_route(kb_id):
    df = get_kb_from_id(kb_id)
    json_data = df.to_json(orient='records')
    return JSONResponse(content=json.loads(json_data)[0], status_code=200)
@app.get("/get_new_conversation_id")
def get_new_conversation_id_route():
    return JSONResponse(content={"conversation_id": str(uuid.uuid4())}, status_code=200)

@app.get("/chat")
def chat_route(conversation_id:str, kb_id:str,model:str,question:str):        
    try:                
        response = chat_with_kb(conversation_id,kb_id,question,model=model)                     
        return JSONResponse(content= response.to_json(), status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get('/get_conversation_ids')
def get_conversation_ids_route():
    try:
        conversation_ids = get_conversation_ids() 
        return JSONResponse(content={'conversations_ids':conversation_ids}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@app.get('/get_full_conversation')
def get_full_conversation_route(conversation_id: str):
    try:
        conversation_df = get_conversation_df(conversation_id) 
        conversation_df["timestamp"] = conversation_df["timestamp"].astype(str)
        # Convert DataFrame to list of dictionaries
        conversations_json = conversation_df.to_dict(orient='records')
        # Convert NumPy arrays to lists        
        for item in conversations_json:
            if isinstance(item.get("chunk_id"), np.ndarray):
                item["chunk_id"] = item["chunk_id"].tolist()          
        
        return JSONResponse(content=conversations_json, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@app.get('/perform_pca')
def pca_route(conversation_id: str):
    try:
        response_text = perform_pca(conversation_id)
        
        return JSONResponse(content=json.loads(response_text), status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@app.get('/get_pca')
def get_pca_route(conversation_id: str):
    try:
        response_text = get_pca(conversation_id)
        
        return JSONResponse(content=response_text, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get('/get_all_conversations')
def get_all_conversations_route():
    try:
        all_conversations_df = get_all_conversations()
        conversations = all_conversations_df.to_dict(orient='records')
        return JSONResponse(content=conversations, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get('/get_all_conversations_with_kb_name')
def get_all_conversations_with_kb_name_route():
    try:
        conversations = get_all_conversations_with_kb_name()
        return JSONResponse(content=conversations, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get('/get_chunks_from_ids')
def get_chunks_from_ids_route(chunk_ids: list[str] = Query(...)):    
    try:
        chunks_df = get_chunks_from_ids(chunk_ids)        
        chunks = chunks_df.to_dict(orient='records')
        return JSONResponse(content=chunks, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000)



