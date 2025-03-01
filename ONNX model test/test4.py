# Load model directly
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch 
from transformers.convert_graph_to_onnx import convert
from pathlib import Path
from huggingface_hub import login

login()  # This will prompt you to enter your Hugging Face token
tokenizer = AutoTokenizer.from_pretrained("cybert79/spamai")
model = AutoModelForSequenceClassification.from_pretrained("cybert79/spamai") 

onnx_path = Path(r"D:\Programming\Python\AI\Basics\AMNIL Tech\ONNX model test\model2\again\spamai.onnx")
convert(
    framework="pt",  # PyTorch
    model=model,
    tokenizer=tokenizer,
    output=onnx_path,
    opset=14,
)

print(f"Model saved at: {onnx_path}")
from huggingface_hub import HfApi, Repository

# Define model repo
repo_name = "spamdetect"  # Change to your desired repo name
username = "Xenserv"  # Replace with your Hugging Face username
model_repo_url = f"https://huggingface.co/{username}/{repo_name}"

# Create a new repository
api = HfApi()
api.create_repo(repo_name, private=False)  # Set private=True if you want the repo to be private

# Initialize a repository object and push the model
repo = Repository(local_dir=".", clone_from=model_repo_url)
#repo.git_pull()  # Pull the latest changes from the repo

# Copy your ONNX model to the repo folder
import shutil
shutil.copy(onnx_path, repo.local_dir)

# Commit and push the model
repo.git_add()
repo.git_commit("Initial commit of ONNX model")
repo.git_push()
# def predict(text):
#     inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
#     predicted_class = torch.argmax(probabilities).item()
#     return predicted_class, probabilities

# # Example usage
# #text = "Congratulations! You've won a prize. Click here to claim."
# text = """
# Subject: 🎉 Congratulations! You’ve Won a $1,000 Gift Card!

# Dear Valued Customer,

# We are excited to inform you that you have been selected as the lucky winner of a $1,000 Amazon Gift Card! 🎁

# To claim your prize, simply click the link below and verify your details:

# 👉 Claim Your Gift Now 👈

# Hurry! This exclusive offer expires in 24 hours!

# Best regards,
# Amazon Rewards Team
# support@amazon-giveaways.com
# """
# label, prob = predict(text)
# print(f"Predicted label: {label}, Probabilities: {prob.tolist()}")