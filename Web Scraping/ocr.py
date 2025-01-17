from io import BytesIO
import easyocr
import os

reader = easyocr.Reader(['en'])

# Apply EasyOCR to each image URL
def process_images(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if the file is an image
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing Image: {file_path}")
            try:
                # OCR processing
                result = reader.readtext(file_path,detail=0,paragraph=True)
                with open(f"{folder_path}\..\ocr_text\{filename.split('.')[0]}.txt", 'w') as f:
                    for text in result:                        
                        f.write(text+'\n')                                              
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Process all URLs
process_images('Web Scraping\images')