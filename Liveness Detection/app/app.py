from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import json
from processes import get_text

app = FastAPI(
    title="OCR API",
    description="""
    This API allows you to upload an image and get a formatted response with account details and image information.
    """
)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Load the uploaded image
        image = Image.open(io.BytesIO(await file.read()))
        
        # Example: Get image details
        image_details = {
            "filename": file.filename,
            "format": image.format,
            "size": image.size,  # (width, height)
            "mode": image.mode
        }
        response = get_text(image).choices[0].message.content
        # Step 1: Convert the escaped JSON string to a proper dictionary        

        # Process image (example: return metadata)
        return JSONResponse(content={"response": json.loads(response), "details": image_details})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)