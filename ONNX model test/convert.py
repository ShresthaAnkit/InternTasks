from transformers import GPT2Model, GPT2Tokenizer
from pathlib import Path
from transformers.convert_graph_to_onnx import convert

# Load pre-trained DistilGPT-2 model and tokenizer
model_name = "distilgpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2Model.from_pretrained(model_name)
dynamic_axes = {
    'input_ids': {0: 'batch_size', 1: 'sequence_length'},  # Batch and sequence dimensions
    'output_1': {0: 'batch_size', 1: 'sequence_length'}  # Same for output
}

# Convert to ONNX
onnx_path = Path(r"D:\Programming\Python\AI\Basics\AMNIL Tech\ONNX model test\model\distilgpt2.onnx")
convert(
    framework="pt",  # PyTorch
    model=model,
    tokenizer=tokenizer,
    output=onnx_path,
    opset=12,  # Use opset 12 for compatibility
    dynamic_axes=dynamic_axes  # Pass dynamic axes

)

print(f"Model saved at: {onnx_path}")
