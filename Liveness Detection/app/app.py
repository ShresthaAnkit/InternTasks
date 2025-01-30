from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import tempfile
import os
from processes import detect_liveness

app = FastAPI(
    title="Liveness Detection",
    description="""
    This API allows you to upload a video and check if the person in the video is real or fake.
    """
)

@app.get("/")
def read_root():    
    """
    Root endpoint that returns a welcome message indicating that the app is running.

    This endpoint provides a simple message to let users know that the
    application is operational and directs them to the Swagger API documentation
    for further details on available endpoints and their usage.
    """
    return {"message": "Hello, the app is running! \n Go to /docs for swagger api docs"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):    
    """
    Upload a video file and check if the person in the video is real or fake.

    This endpoint accepts a video file and stores it in the `UPLOAD_DIR` directory.
    The video is then passed to the `detect_liveness` function which returns a boolean
    indicating whether the person in the video is real or fake.

    The response is a JSON object with a single key-value pair. The key is "response"
    and the value is another JSON object with a single key-value pair. The key is
    "liveness" and the value is a boolean indicating whether the person in the video
    is real or fake.

    If an error occurs, the response is a JSON object with a single key-value pair.
    The key is "error" and the value is a string describing the error.

    Parameters:
        file (str or file-like object): The video file to be uploaded.

    Returns:
        dict: A JSON response containing the result of the liveness detection.
    """    
    try:          
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(await file.read())
            temp_video_path = temp_video.name  # Store the temporary file path   
            # Process video
            response = detect_liveness(temp_video_path)
        
        return JSONResponse(content={"liveness": response}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)