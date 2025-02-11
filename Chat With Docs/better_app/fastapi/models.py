import lancedb
from lancedb.pydantic import LanceModel, Vector
from typing import List
# Connect to the LanceDB database
db = lancedb.connect("mydb")

class KnowledgeBase(LanceModel):
    kb_id: str  # Unique knowledge base ID
    name: str  # Knowledge base name
    description: str  # Optional description
    model: str  # Embedding model used    

class Chunk(LanceModel):
    chunk_id: str  # Unique chunk ID
    kb_id: str  # Foreign key to `KnowledgeBase`    
    text: str  # Chunked text
    vector: Vector(1536)  # Embedding vector

class Conversation(LanceModel):
    conversation_id: str  # Unique conversation ID
    kb_id: str  # Foreign key to `KnowledgeBase`    
    chunk_id: List[str]  # List of chunk IDs,
    sender: str # User or system
    text: str  # Conversation text