from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Load pre-trained model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
model = GPT2LMHeadModel.from_pretrained("distilgpt2")

# Encode input text
input_text = "Once upon a time there was a"
input_ids = tokenizer.encode(input_text, return_tensors="pt")

# Generate response
output = model.generate(input_ids, max_new_tokens = 50, num_return_sequences=1)

# Decode and print the response
response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)
