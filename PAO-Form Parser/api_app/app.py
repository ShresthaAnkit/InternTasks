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
    """
    ### Endpoint Description:
    Extract form data from an uploaded image and return the extracted data in JSON format.

    #### Request Parameters:
    - `file`: The image file to extract data from. (Required)

    ### Example Response:
    ```json
    {
        {
            "date": "str",
            "branch": "str",
            "account_type": "str",
            "product_name": "str",
            "currency": "str",
            "salutation": "str",
            "full_name": "str",
            "date_of_birth_bs": "str",
            "date_of_birth_ad": "str",
            "gender": "str",
            "marital_status": "str",
            "nationality": "str",
            "resident": "str",
            "education": "str",
            "existing_account": "str",
            "account_no": "str",
            "identification_details": [
                {
                "legal_id": "str",
                "number_type": "str",
                "issuing_office": "str",
                "date_of_issue": "str",
                "expiry_date": "str",
                "primary_secondary": "str"
                }
            ],
            "related_parties": [
                {
                "relation": "str",
                "full_name": "str",
                "id_type": "str",
                "id_no": "str",
                "have_account": "str",
                "customer_no": "str"
                }
            ]
        },
        {
            "filename": "str",
            "format": "str",
            "size": ["int","int"],
            "mode": "str"
        }
    }
    ```
    ### Notes:
    - The image should be in a supported format (e.g., PNG, JPEG).
    - The data extracted will vary depending on the image content.
    """
    
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