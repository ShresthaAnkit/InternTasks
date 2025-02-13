import lancedb
from lancedb.pydantic import LanceModel, Vector
from typing import List,Optional
from pydantic import BaseModel, Field
# Connect to the LanceDB database
db = lancedb.connect("mydb")

class KnowledgeBase(LanceModel):
    kb_id: str  # Unique knowledge base ID
    name: str  # Knowledge base name
    description: str  # Optional description
    model: str  # Embedding model used        
    status: str
    created_at: str

class Chunk(LanceModel):
    chunk_id: str  # Unique chunk ID
    kb_id: str  # Foreign key to `KnowledgeBase`    
    text: str  # Chunked text
    vector: Vector(1536)  # type: ignore # Embedding vector
    embedding_tokens: int

class Conversation(LanceModel):
    conversation_id: str  # Conversation ID of a particular conversation    
    kb_id: str  # Foreign key to `KnowledgeBase`    
    pca_done: int = 0
    
class Message(LanceModel):
    message_id: str
    conversation_id: str  # Conversation ID of a particular conversation    
    sender: str # User or system
    text: str  # Conversation text
    chunk_id: List[str]  # List of chunk IDs,
    embedding_tokens: int
    prompt_tokens: int
    completion_tokens: int
    timestamp: str

    def to_json(self):
        return {
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "sender": self.sender,
            "text": self.text,
            "chunk_id": self.chunk_id,
            "embedding_tokens": self.embedding_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "timestamp": self.timestamp
        }

class PCA(LanceModel):
    conversation_id: str
    sentiment_score: int
    sentiment_feedback: str
    context_gap: List[str]
    tags: List[str]
    prompt_tokens: int
    completion_tokens: int

class PCAModel(BaseModel):    
    sentiment_score: int
    sentiment_feedback: str
    context_gap: List[str]
    tags: List[str]