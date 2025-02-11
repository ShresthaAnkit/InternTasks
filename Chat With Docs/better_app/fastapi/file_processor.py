from unstructured.partition.auto import partition
import tempfile
import shutil
def get_file_text(file_path):
    elements = partition(file_path)
    text = "\n\n".join([str(el) for el in elements])
    return text

def save_uploaded_file_to_disk(file):
    temp_path = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
        temp_path = temp_file.name
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return temp_path