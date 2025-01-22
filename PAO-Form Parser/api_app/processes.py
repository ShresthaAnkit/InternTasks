from dotenv import load_dotenv
import os
import openai
from models import PersonalAccountForm
from prompt import system_prompt
import base64
from io import BytesIO
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI()
openai.api_key = OPENAI_API_KEY



# Function to encode the image
def encode_image(image):    
    buffer = BytesIO()
    # Save the image to the buffer in its format (e.g., PNG, JPEG)
    image.save(buffer, format=image.format)
    # Get the byte data
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")

def get_text(image):    
    # Getting the base64 string
    base64_image = encode_image(image)

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"system",
                "content":system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the information in this bank account opening form and output into JSON.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        response_format=PersonalAccountForm,
    )
    return response