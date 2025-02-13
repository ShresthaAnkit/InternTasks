from typing import List

class Ingest:
    name: str
    model: str
    description: str = ''    
    def __init__(self, name: str, model: str, description: str):
        self.name = name
        self.model = model
        self.description = description        

class KnowledgeBase:    
    kb_id: str  # Unique knowledge base ID
    name: str  # Knowledge base name
    description: str  # Optional description
    model: str  # Embedding model used        
    status: str
    created_at: str

    def __init__(self, kb_id: str, name: str, description: str, model: str, status: str, created_at: str):
        self.kb_id = kb_id
        self.name = name
        self.description = description
        self.model = model        
        self.status = status
        self.created_at = created_at

    @classmethod
    def from_json(cls,json_object):
        return KnowledgeBase(
            kb_id=json_object['kb_id'],
            name=json_object['name'],
            description=json_object['description'],
            model=json_object['model'],
            status=json_object['status'],
            created_at=json_object['created_at']
        )
class ChunkModel:
    chunk_id: str
    text: str
    embedding_tokens: int

    def __init__(self, chunk_id: str, text: str, embedding_tokens: int):
        self.chunk_id = chunk_id
        self.text = text
        self.embedding_tokens = embedding_tokens
    @classmethod
    def from_json(cls,json_object):
        return ChunkModel(
            chunk_id=json_object['chunk_id'],
            text=json_object['text'],
            embedding_tokens=json_object['embedding_tokens']
    )    
class QueryModel:
    conversation_id: str
    kb_id: str
    text: str
    model: str

    def __init__(self, conversation_id: str, kb_id: str, text: str, model: str):
        self.conversation_id = conversation_id
        self.kb_id = kb_id
        self.text = text
        self.model = model
    def to_json(self):
        return {
            'conversation_id': self.conversation_id,
            'kb_id': self.kb_id,
            'question': self.text,
            'model': self.model
        }
    def __repr__(self):
        return f"QueryModel(conversation_id={self.conversation_id}, kb_id={self.kb_id}, question={self.text}, model={self.model})"
class ChatResponseModel:
    message_id: str
    conversation_id: str  # Conversation ID of a particular conversation    
    sender: str # User or system
    text: str  # Conversation text
    chunk_id: List[str]  # List of chunk IDs,
    embedding_tokens: int
    prompt_tokens: int
    completion_tokens: int
    timestamp: str

    def __init__(self,message_id:str,conversation_id: str, sender: str, text: str, chunk_id: List[str], embedding_tokens: int, prompt_tokens: int, completion_tokens: int, timestamp: str):
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.sender = sender
        self.text = text
        self.chunk_id = chunk_id
        self.embedding_tokens = embedding_tokens
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.timestamp = timestamp

    @classmethod
    def from_json(cls,json_object):
        return ChatResponseModel(
            message_id=json_object['message_id'],
            conversation_id=json_object['conversation_id'],
            sender=json_object['sender'],
            text=json_object['text'],
            chunk_id=json_object['chunk_id'],
            embedding_tokens=json_object['embedding_tokens'],
            prompt_tokens=json_object['prompt_tokens'],
            completion_tokens=json_object['completion_tokens'],
            timestamp=json_object['timestamp']
        )

class PCAResponseModel:
    sentiment_score: int
    sentiment_feedback: str
    context_gap: List[str]
    tags: List[str]
    prompt_tokens: int
    completition_tokens: int
               
    def __init__(self, sentiment_score: int, sentiment_feedback: str, context_gap: List[str], tags: List[str], prompt_tokens: int, completition_tokens: int):
        self.sentiment_score = sentiment_score
        self.sentiment_feedback = sentiment_feedback
        self.context_gap = context_gap
        self.tags = tags
        self.prompt_tokens = prompt_tokens
        self.completition_tokens = completition_tokens
    
    def from_json(json_object):
        return PCAResponseModel(
            sentiment_score=json_object['sentiment_score'],
            sentiment_feedback=json_object['sentiment_feedback'],
            context_gap=json_object['context_gap'],
            tags=json_object['tags'],
            prompt_tokens=json_object['prompt_tokens'],
            completition_tokens=json_object['completition_tokens']
        )