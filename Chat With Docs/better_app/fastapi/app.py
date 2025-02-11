from fastapi import FastAPI, File, UploadFile,BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
from database import Database
from processes import ingest_files,chat_with_kb
from file_processor import save_uploaded_file_to_disk

app = FastAPI(
    title="Chat with Docs",
    description="""
    
    """
)
db = Database()

@app.post("/ingest")
async def ingest(name: str, model: str, description: str,background_tasks: BackgroundTasks, file_list: list[UploadFile] = File(...)):        
    try:                
        if db.check_already_exist(name): return JSONResponse(content={"error": "Knowledge base already exists."}, status_code=400)
        file_paths = []
        for file in file_list:
            file_paths.append(save_uploaded_file_to_disk(file))
        process_id = str(uuid.uuid4())
        print("Adding Background task.")
        background_tasks.add_task(ingest_files,process_id,db,name,model,description,file_paths)                            
        return JSONResponse(content={"response": f"Successfully added for ingestion with id: {process_id}"}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@app.get("/get_new_conversation_id")
def get_new_conversation_id():
    return JSONResponse(content={"conversation_id": str(uuid.uuid4())}, status_code=200)

@app.get("/chat")
def chat(conversation_id:str, name:str,model:str,question:str):
    try:                
        response = chat_with_kb(conversation_id,db,name,question)        
        return JSONResponse(content={"response": response}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)