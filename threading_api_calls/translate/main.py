from fastapi import UploadFile, BackgroundTasks, File
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import chardet
import uuid
import sqlite3
from utils import split_and_translate
app = FastAPI()

# API to upload file and start background translation
@app.post("/translate/")
async def translate_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        # Step 1: Read the file content
        raw_contents = await file.read()
 
        # Step 2: Detect encoding
        detected_encoding = chardet.detect(raw_contents)['encoding']
        if detected_encoding is None:
            return JSONResponse(content={"error": "Could not detect file encoding."}, status_code=400)
 
        # Step 3: Decode the file content
        contents = raw_contents.decode(detected_encoding)
 
        # Step 4: Generate a unique task ID
        task_id = str(uuid.uuid4())
 
        # Step 5: Start background translation
        background_tasks.add_task(split_and_translate, contents, task_id=task_id)
 
        # Step 6: Return the task ID immediately
        return {"task_id": task_id, "status": "processing"}
 
    except UnicodeDecodeError as e:
        return JSONResponse(content={"error": f"Unicode decode error: {str(e)}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
 
# API to check the translation status and retrieve the result@app.get("/status/{task_id}")
# API to check the translation status and retrieve the result
@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    **Description:**  
    This endpoint allows users to check the status of the translation task and retrieve the translated text if the task is completed.
 
    **Path Parameters:**
 
    - `task_id` (required): The unique identifier for the translation task, which is provided when the file is uploaded.
 
    **Response:**
 
    - **Status 200** (Success - Task Completed):
    - `task_id` (string): The unique task ID.
    - `status`: `"completed"` if the translation is done.
    - `translated_text` (string): The translated English text.
 
    - **Status 200** (Success - Task In Progress):
    - `task_id` (string): The unique task ID.
    - `status`: `"processing"` if the translation is still in progress.
 
    - **Status 404** (Task Not Found):
    - `detail`: `"Task ID not found"` if no task with the given ID exists.
 
    **Example Request:**
 
    ```bash
    curl "http://127.0.0.1:8000/status/e1f06e6d-82a0-4f6d-9b79-b4d35c7bb8af"
    ```
 
    **Example Response (Task Completed):**
 
    ```json
    {
    "task_id": "e1f06e6d-82a0-4f6d-9b79-b4d35c7bb8af",
    "status": "completed",
    "translated_text": "This is the translated English text."
    }
    ```
 
    **Example Response (Task In Progress):**
 
    ```json
    {
    "task_id": "e1f06e6d-82a0-4f6d-9b79-b4d35c7bb8af",
    "status": "processing"
    }
    ```
    """
    # Query the SQLite database for the translation result
    conn = sqlite3.connect('translations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT translated_text FROM translations WHERE task_id = ?', (task_id,))
    row = cursor.fetchone()
    conn.close()
 
    if row:
        # If the task is done, return the translated content
        return {"task_id": task_id, "status": "completed", "translated_text": row[0]}
    else:
        # If the task is still processing
        return {"task_id": task_id, "status": "processing"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)