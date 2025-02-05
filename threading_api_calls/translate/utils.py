import sqlite3
from api_calls import answer_question
import asyncio
import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timer
        result = func(*args, **kwargs)
        end_time = time.time()  # End timer
        print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper

# Store translations in memory for simplicity (you can replace this with a database)
def init_db():
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS translations (
                task_id TEXT PRIMARY KEY,
                original_text TEXT,
                translated_text TEXT
                )
        ''')
    c.execute("""
        CREATE TABLE IF NOT EXISTS memos (
            uuid TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
    conn.commit()
    conn.close()
 
init_db() # Initialize the database

def chunk_by_line_break(text):
    return text.split("\n")  # Splits text into a list of lines


# Function to split text into chunks and translate each chunk
async def split_and_translate(full_text, chunk_size=20, task_id=None):
    #full_text = convert(full_text)
    #chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]
    chunks = chunk_by_line_break(full_text)
    start_time = time.time()  # Start timer
    translated_chunks = await asyncio.gather(*(answer_question(chunk) for chunk in chunks))
    # translated_chunks = []
    # for i, chunk in enumerate(chunks):
    #     # print(f"Contents of chunk {i + 1}: {chunk}")
    #     translated_chunk = answer_question(chunk)
    #     translated_chunks.append(translated_chunk)    
    end_time = time.time()  # End timer
    print(f"Total time taken: {end_time - start_time:.6f} seconds")

    print(translated_chunks)
    translated_full_text = ' '.join(translated_chunks)
 
    ## Store result in the SQLite database
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO translations (task_id, original_text, translated_text)
        VALUES (?, ?, ?)
    ''', (task_id, full_text, translated_full_text))
    conn.commit()
    conn.close()