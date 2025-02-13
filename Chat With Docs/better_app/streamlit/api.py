from dotenv import load_dotenv
import os
from models import *
import requests
from streamlit.runtime.uploaded_file_manager import UploadedFile
load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
URL = f"http://{HOST}:{PORT}"
def ingest(ingestModel: Ingest,uploaded_files: list[UploadedFile]):
    files = [("file_list", (file.name, file)) for file in uploaded_files] 
    data = {
        "name": ingestModel.name,
        "model": ingestModel.model,
        "description": ingestModel.description
    }    
    response = requests.post(f"{URL}/ingest", params=data, files=files)
    return response

def get_all_kbs():
    response = requests.get(f"{URL}/get_all_kbs")
    kb_models: KnowledgeBase = [KnowledgeBase.from_json(json_object) for json_object in response.json()]
    return kb_models

def get_conversation_id():
    response = requests.get(f"{URL}/get_new_conversation_id")        
    return response.json()['conversation_id']

def chat(queryModel: QueryModel):        
    response = requests.get(f"{URL}/chat",params=queryModel.to_json())
    responseModel = ChatResponseModel.from_json(response.json())
    return responseModel

def get_all_conversations_with_kb_name():
    response = requests.get(f"{URL}/get_all_conversations_with_kb_name")
    return response.json()

def get_full_conversation(conversation_id):
    response = requests.get(f"{URL}/get_full_conversation",params={"conversation_id": conversation_id})
    return response.json()

def perform_pca(conversation_id):
    response = requests.get(f"{URL}/perform_pca",params={"conversation_id": conversation_id})
    return response.json()

def get_pca(conversation_id):
    response = requests.get(f"{URL}/get_pca",params={"conversation_id": conversation_id})
    return response.json()

def get_chunks_from_ids(chunk_ids):
    print("API: ",chunk_ids)
    response = requests.get(f"{URL}/get_chunks_from_ids",params=[("chunk_ids", chunk_id) for chunk_id in chunk_ids])
    print(response.json())
    responseModel = [ChunkModel.from_json(json_object) for json_object in response.json()]
    return responseModel