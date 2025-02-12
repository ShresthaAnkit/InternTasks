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
    
class QueryModel:
    conversation_id: str
    kb_id: str
    question: str
    model: str

    def __init__(self, conversation_id: str, kb_id: str, question: str, model: str):
        self.conversation_id = conversation_id
        self.kb_id = kb_id
        self.question = question
        self.model = model
    def to_json(self):
        return {
            'conversation_id': self.conversation_id,
            'kb_id': self.kb_id,
            'question': self.question,
            'model': self.model
        }
    def __repr__(self):
        return f"QueryModel(conversation_id={self.conversation_id}, kb_id={self.kb_id}, question={self.question}, model={self.model})"
class ChatResponseModel:
    response: str