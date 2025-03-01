from transformers import GPT2Model, GPT2Tokenizer
import torch
import torch.onnx
from pathlib import Path

# Load pre-trained DistilGPT-2 model and tokenizer
model_name = "distilgpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2Model.from_pretrained(model_name)

# Set the model to evaluation mode
model.eval()

# Prepare input tensor (batch_size=1, sequence_length=5)
input_text = "Hello, this is a test sentence."
inputs = tokenizer(input_text, return_tensors="pt")
input_ids = inputs['input_ids']

# Define dynamic axes
dynamic_axes = {
    'input_ids': {0: 'batch_size', 1: 'sequence_length'},  # Dynamic batch size and sequence length
    'last_hidden_state': {0: 'batch_size', 1: 'sequence_length'}  # Same for output
}

# Specify the output ONNX path
onnx_path = Path(r"D:\Programming\Python\AI\Basics\AMNIL Tech\ONNX model test\model\distilgpt2.onnx")

# Export the model to ONNX format
torch.onnx.export(
    model,  # Model to export
    (input_ids,),  # Input tensor (we need to pass it as a tuple)
    onnx_path,  # Path to save the ONNX model
    input_names=['input_ids'],  # Input tensor name
    output_names=['last_hidden_state'],  # Output tensor name
    opset_version=14,  # Opset version for compatibility
    dynamic_axes=dynamic_axes  # Dynamic axes for both input and output
)

print(f"Model saved at: {onnx_path}")
