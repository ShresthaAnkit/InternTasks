from models import KnowledgeBase, Chunk, Conversation
import lancedb
import uuid

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

    def insert_chunks(self,kb_id,chunks, embedded_chunks,KB_NAME,model,description):
        kb_table = self.db.open_table('KnowledgeBase')
        kb_table.create_fts_index("name", use_tantivy=False,replace=True)        
        # Create a new knowledge base
        kb_table.add([KnowledgeBase(
            kb_id=kb_id,
            name=KB_NAME,
            description=description,
            model=model
        )])
        chunk_table = self.db.open_table('Chunk')
        # Save each chunk and its vector into LanceDB
        for chunk, embedding in zip(chunks, embedded_chunks):
            #padded_vector = np.pad(embedding, (0, 1536 - len(embedding)), 'constant', constant_values=0)
            chunk_table.add([Chunk(chunk_id=str(uuid.uuid4()),kb_id=kb_id,text=chunk, vector=embedding)])
        return f"Knowledge base '{KB_NAME}' created successfully."
    
    def check_already_exist(self,KB_NAME):
        kb_table = self.db.open_table('KnowledgeBase')
        kb_table.create_fts_index("name", use_tantivy=False,replace=True)
        existing_kb = kb_table.search(KB_NAME,vector_column_name='name').select(["kb_id"]).to_list()
        if existing_kb: 
            return True
        return False

    def get_kb_id(self,KB_NAME):
        try:
            table = self.db.open_table("KnowledgeBase")
            table.create_fts_index("name", use_tantivy=False,replace=True)
            return table.search(KB_NAME,vector_column_name='name').select(["kb_id"]).to_list()[0]['kb_id']    
        except Exception as e:
            return None
        
    def retrieve_KB(self,KB_NAME):    
        kb_id = self.get_kb_id(KB_NAME)
        if kb_id is None:
            return None
        kb_table = self.db.open_table("Chunk")
        kb_table.create_fts_index("kb_id", use_tantivy=False,replace=True)
        chunk_df = kb_table.search(kb_id,vector_column_name='kb_id').select(["chunk_id","kb_id","text","vector"]).to_pandas()    
        return chunk_df
    
    def get_kb_chunks(self,KB_NAME):
        kb_id = self.get_kb_id(KB_NAME)
        if kb_id is None:
            return None
        kb_table = self.db.open_table("Chunk")
        kb_table.create_fts_index("kb_id", use_tantivy=False,replace=True)
        chunk_df = kb_table.search(kb_id,vector_column_name='kb_id').select(["chunk_id","kb_id","text"]).to_pandas()    
        return chunk_df
    
    def get_conversation_history(self,conversation_id):
        table = self.db.open_table("Conversation")
        table.create_fts_index("conversation_id", use_tantivy=False,replace=True)
        conversation_df = table.search(conversation_id,vector_column_name='conversation_id').select(["conversation_id","kb_id","chunk_id","sender","text"]).to_pandas()    
        return conversation_df
    
    # I WAS DOING THIS FUNCTION PLEASE CONTINUE TOMORROW
    def add_to_conversation(self,conversastion_id,sender,text,kb_id,chunk_id):
        table = self.db.open_table("Conversation")
        table.add([Conversation(conversation_id=conversastion_id,kb_id=kb_id,chunk_id=chunk_id,sender=sender,text=text)])