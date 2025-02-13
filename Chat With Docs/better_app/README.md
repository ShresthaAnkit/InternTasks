# **Post-Conversation Analysis & RAG app**  

This Streamlit-based web app allows users to ingest files such as pdf, images and text files and store their embeddings in a vector database allowing users to query information from them. Then, it enables **Post Conversation Analysis (PCA)** on chatbot interactions. Users can select conversations, perform PCA, and visualize key insights such as:  

✅ **Token Usage** – Embedding, prompt, and completion tokens  
✅ **Sentiment Analysis** – Sentiment score (0-10) with feedback  
✅ **Context Gaps** – Missing information that could improve responses  
✅ **Topic Tags** – Key subjects extracted from conversations  

### **Features**  
🔹 **Ingest files** – Take various file types and convert them into vector embeddings
🔹 **Vector Storage** – Store the embeddings in a vector database
🔹 **Chat with Docs** – Converse with the ingested files
🔹 **Conversation Selection** – List of past chatbot conversations  
🔹 **PCA Execution** – Perform PCA per conversation with a single click  
🔹 **Modal View** – Displays token usage, sentiment, context gaps, and tags  
🔹 **Dynamic UI** – Uses dynamic content for clean visualization  

### **Tech Stack**  
- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **Data Handling:** Pandas, Requests  

### **Usage**  
1. Install the required libraries
2. Run the fastapi app with `python fastapi/app.py`
3. Run the streamlit app with `streamlit run streamlit/app.py`  


