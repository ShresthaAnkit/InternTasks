from models import KnowledgeBase, Chunk, Conversation, PCA
import lancedb
import uuid
import datetime


class Database():
    def __init__(self,DB_NAME='mydb'):
        self.db = lancedb.connect(DB_NAME)
        # Create the table if it doesn't already exist
        if "KnowledgeBase" not in self.db.table_names():
            self.db.create_table("KnowledgeBase", schema=KnowledgeBase)
        if "Chunk" not in self.db.table_names():
            self.db.create_table("Chunk", schema=Chunk)
        if "Conversation" not in self.db.table_names():
            self.db.create_table("Conversation", schema=Conversation)
        if "PCA" not in self.db.table_names():
            self.db.create_table("PCA", schema=PCA)

    def create_kb(self,kb_id,KB_NAME,model,description):
        kb_table = self.db.open_table('KnowledgeBase')
        # Create a new knowledge base        
        kb_table.add([KnowledgeBase(
            kb_id=kb_id,
            name=KB_NAME,
            description=description,
            model=model,
            status = "Pending",
            created_at=datetime.datetime.now().isoformat()
        )])
    def insert_chunks(self,kb_id,chunks, embedded_chunks,embedding_tokens,model):
        kb_table = self.db.open_table('KnowledgeBase')
        kb_table.create_fts_index("name", use_tantivy=False,replace=True)  
          
        
        chunk_table = self.db.open_table('Chunk')
        # Save each chunk and its vector into LanceDB
        for chunk, embedding,tokens in zip(chunks, embedded_chunks,embedding_tokens):
            #padded_vector = np.pad(embedding, (0, 1536 - len(embedding)), 'constant', constant_values=0)
            chunk_table.add([Chunk(chunk_id=str(uuid.uuid4()),kb_id=kb_id,text=chunk, vector=embedding,embedding_tokens=tokens)])
        kb_table.update(where=f"kb_id = '{kb_id}'",values={'status': 'Completed'})            
    
    def check_already_exist(self,KB_NAME):
        kb_table = self.db.open_table('KnowledgeBase')
        kb_table.create_fts_index("name", use_tantivy=False,replace=True)
        existing_kb = kb_table.search(KB_NAME,vector_column_name='name').select(["kb_id"]).to_list()
        if existing_kb: 
            return True
        return False
    
    def check_if_conversation_exists(self,conversation_id):
        table = self.db.open_table("Conversation")
        table.create_fts_index("conversation_id", use_tantivy=False,replace=True)
        existing_conversastion = table.search(conversation_id,vector_column_name='conversation_id').select(["conversation_id"]).to_list()
        if existing_conversastion: 
            return True
        return False

    # Get the id of the knowledge give the KB_NAME
    def get_kb_id(self,KB_NAME):
        try:
            table = self.db.open_table("KnowledgeBase")
            table.create_fts_index("name", use_tantivy=False,replace=True)
            return table.search(KB_NAME,vector_column_name='name').select(["kb_id"]).to_list()[0]['kb_id']    
        except Exception as e:
            return None
        
    # Retrieve the knowledge base given the KB_NAME
    def retrieve_KB(self,KB_NAME):    
        kb_id = self.get_kb_id(KB_NAME)
        if kb_id is None:
            return None
        kb_table = self.db.open_table("Chunk")
        kb_table.create_fts_index("kb_id", use_tantivy=False,replace=True)
        chunk_df = kb_table.search(
            kb_id,
            vector_column_name='kb_id'
        ).select(["chunk_id","kb_id","text","vector"]).to_pandas()    
        return chunk_df
    
    # Get all the chunks of a particular knowledgebase
    def get_kb_chunks(self,KB_NAME):
        kb_id = self.get_kb_id(KB_NAME)
        if kb_id is None:
            return None
        kb_table = self.db.open_table("Chunk")
        kb_table.create_fts_index("kb_id", use_tantivy=False,replace=True)
        chunk_df = kb_table.search(
            kb_id,
            vector_column_name='kb_id'
        ).select(["chunk_id","kb_id","text"]).to_pandas()    
        return chunk_df
    
    def add_to_conversation(self,conversation_id,sender,text,kb_id,chunk_id,embedding_tokens,prompt_tokens,completition_tokens):
        table = self.db.open_table("Conversation")
        table.add([
            Conversation(
                conversation_id=conversation_id,
                kb_id=kb_id,
                chunk_id=chunk_id,
                sender=sender,
                text=text,
                embedding_tokens=embedding_tokens,
                prompt_tokens=prompt_tokens,
                completition_tokens=completition_tokens,
                timestamp=datetime.datetime.now().isoformat()
            )])

    def delete_conversation(self,conversation_id):
        table = self.db.open_table("Conversation")
        table.delete(conversation_id)
    
    def get_conversation_ids(self):
        table = self.db.open_table("Conversation")        
        return table.to_pandas()

    def get_kb_from_id(self,kb_id):
        table = self.db.open_table("KnowledgeBase")
        table.create_fts_index("kb_id", use_tantivy=False,replace=True)
        kb_df = table.search(kb_id,vector_column_name='kb_id').select(["kb_id","name","description","model","status","created_at"]).to_pandas()       
        kb_df.drop(columns=['_score'],inplace=True)         
        return kb_df

    def get_conversation_from_id(self,conversation_id):        
        table = self.db.open_table("Conversation")
        table.create_fts_index("conversation_id", use_tantivy=False,replace=True)
        conversation_df = table.search(conversation_id,vector_column_name='conversation_id').select(["conversation_id","kb_id","chunk_id","sender","text","embedding_tokens","prompt_tokens","completition_tokens","timestamp"]).to_pandas()       
        conversation_df.drop(columns=['_score'],inplace=True)         
        return conversation_df
    
    def insert_pca(self,conversation_id,pca_response,prompt_tokens,completition_tokens):
        table = self.db.open_table("PCA")
        table.add([PCA(conversation_id=conversation_id,
                       sentiment_score=pca_response['sentiment_score'],
                       sentiment_feedback=pca_response['sentiment_feedback'],
                       context_gap=pca_response['context_gap'],
                       tags=pca_response['tags'],
                       prompt_tokens=prompt_tokens,
                       completition_tokens=completition_tokens)])