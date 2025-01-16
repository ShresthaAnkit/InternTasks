import re
from PyPDF2 import PdfReader

def get_pdf_text(pdf_path):    
    reader = PdfReader(pdf_path)    
    text_body = []    
    def visitor_body(text, cm, tm, fontDict, fontSize):
        y = tm[5]        
        if y > 50 and y < 800:            
            text_body.append(text)
    for page in reader.pages:        
        page.extract_text(visitor_text=visitor_body)        
    return ''.join(text_body)    

def chunk_by_sentence(text):
    sentence_endings = re.compile(r'([.!?])(?=\s)')
    sentences = sentence_endings.split(text)
    sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') for i in range(0, len(sentences), 2)]
    sentences = [re.sub(r'\n', ' ', sentence) for sentence in sentences]    
    sentences = [re.sub(r'\s+', ' ', sentence).strip() for sentence in sentences]
    return sentences

def chunk_by_sentence_groups(text, max_length):
    # Regular expression to match sentence-ending punctuation: . ? !
    sentence_endings = re.compile(r'([.!?])(?=\s)')
    text = re.sub(r'\s+', ' ', text).strip()
    # Split the text into sentences based on the sentence-ending punctuation
    sentences = sentence_endings.split(text)
    
    # Recombine punctuation with the sentences
    sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') for i in range(0, len(sentences), 2)]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding the sentence exceeds max_length, start a new chunk
        if len(current_chunk) + len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence.strip()
        else:
            current_chunk += sentence  # Add the sentence to the current chunk

    if current_chunk:  # Append the last chunk
        chunks.append(current_chunk)
    
    return chunks