from transformers import AlbertTokenizer, AlbertForSequenceClassification
tokenizer = AlbertTokenizer.from_pretrained('albert')
model = AlbertForSequenceClassification.from_pretrained('albert')

# Set the model to evaluation mode
model.eval()

# Prepare input tensor (batch_size=1, sequence_length=5)
input_text = "Hello, this is a test sentence."
inputs = tokenizer(input_text, return_tensors="pt")
input_ids = inputs['input_ids']

# Generate response
output = model.generate(input_ids, max_new_tokens = 50, num_return_sequences=1)

# Decode and print the response
response = tokenizer.decode(output[0], skip_special_tokens=True)
print(response)