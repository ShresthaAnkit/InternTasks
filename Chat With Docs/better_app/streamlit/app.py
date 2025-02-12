import streamlit as st
from streamlit_option_menu import option_menu
import random
import time
from models import *
import numpy as np
import pandas as pd
from api import *

@st.dialog("Conversation",width='large')
def open_conversation(conversation_id):
    conversation = get_full_conversation(conversation_id)
    st.code(f"Conversation ID: {conversation_id}")
        # Display chat messages from history on app rerun
    print(conversation)
    for message in conversation:
        
        with st.chat_message(message["sender"]):            
            st.markdown(message["text"])
    
if 'embedding_model' not in st.session_state:
    st.session_state['embedding_model'] = ''
if 'completion_model' not in st.session_state:
    st.session_state['completion_model'] = 'gpt-4o-mini'
if 'kb_error' not in st.session_state:
    st.session_state['kb_error'] = False
if 'kb_processing' not in st.session_state:
    st.session_state['kb_processing'] = False
if 'kb_success' not in st.session_state:
    st.session_state['kb_success'] = False
if 'conversation_id' not in st.session_state:
    st.session_state['conversation_id'] = ''
# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state['chat_messages'] = []

# Define navigation
st.set_page_config(page_title="My Streamlit App", layout="wide")

with st.sidebar:
    selected = option_menu("Navigation", ["Landing Page", "Ingestion Page", "Query Page", "PCA Page"],
                           icons=["house", "cloud-upload", "search", "graph-up"],
                           menu_icon="menu-up", default_index=3)

if selected == "Landing Page":
    st.title("Welcome to My Streamlit App")
    st.write("Navigate using the sidebar to explore different features.")

elif selected == "Ingestion Page":

    st.title("Data Ingestion")
    
    name = st.text_input("Enter Name")
    description = st.text_input("Enter Description")
    model = st.selectbox("Select Model", ["text-embedding-3-small","text-embedding-ada-002"])
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)
    
    if st.button("Submit"):
        if name and model and uploaded_files:
            response = ingest(Ingest(name=name, model=model,description=description),uploaded_files=uploaded_files)
            if response.status_code == 200 or response.status_code == 201:
                st.success("Upload successful!")
                st.success(response.json()['response'])  # Display response
            else:
                st.error(f"Upload failed! Status: {response.status_code}")
                st.error(response.json()['error'])            
        else:
            st.warning("Please fill all fields before submitting.")

elif selected == "Query Page":
    kbs = get_all_kbs()    
    st.code("Conversation ID: "+st.session_state['conversation_id'])
    with st.sidebar:        
        kb_list = ["Choose a Knowledge base",*[f"{kb.name}" for kb in kbs]]
        selected_kb = st.selectbox("Select Knowledge Base",kb_list, index=0)
        if selected_kb != "Choose a Knowledge base":            
            st.session_state['embedding_model'] = kbs[kb_list.index(selected_kb)-1].model
        else:
            st.session_state['embedding_model'] = ''
        #st.subheader("Model Selection")
        model = st.selectbox("Select Completition Model", ["gpt-4o-mini"])
        st.text("Embedding Model:")
        st.code(f"{st.session_state['embedding_model']}")
        create_chat = st.button("Create Chat")        
        if st.session_state['kb_error']:
            st.error("Please choose a Knowledge base.")
        if st.session_state['kb_processing']:
            st.info("Still Processing...")
        if st.session_state['kb_success']:
            st.success("Chat created successfully.")
    
    if create_chat:
        if kb_list.index(selected_kb) == 0:
            st.session_state['kb_error'] = True
            st.session_state['kb_success'] = False        
            st.session_state['kb_processing'] = False
            st.session_state['conversation_id'] = ''
        else:
            if kbs[kb_list.index(selected_kb)-1].status == 'Pending':
                st.session_state['kb_processing'] = True
                st.session_state['kb_error'] = False
            else:
                st.session_state['kb_processing'] = False
                st.session_state['kb_error'] = False
                st.session_state['kb_success'] = True
                st.session_state['conversation_id'] = get_conversation_id()
        if "chat_messages" in st.session_state:
            st.session_state['chat_messages'] = []
        st.rerun()            


    # Display chat messages from history on app rerun
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):            
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Type your query..."):
        if st.session_state['conversation_id'] == '':
            with st.chat_message("assistant"):
                st.markdown("Please create a chat first.")
        else:
            # Add user message to chat history
            st.session_state['chat_messages'].append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            queryModel = QueryModel(conversation_id=st.session_state['conversation_id'], kb_id=kbs[kb_list.index(selected_kb)-1].kb_id, question=prompt, model=st.session_state['completion_model'])            
            response = chat(queryModel)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state['chat_messages'].append({"role": "assistant", "content": response})                


elif selected == "PCA Page":
    st.title("PCA Analysis")
    # Add content to the modal
    conversations_list = get_all_conversations_with_kb_name()
    
    header_object = {"conversation_id":"Conversation ID","kb_name":"Knowledge Base Name","pca_done":"PCA Status"}
   # Create a DataFrame from the stored results
    conversations_list.insert(0,header_object)    
    # Display the DataFrame with "Perform PCA" buttons beside each row
    for idx,conversation in enumerate(conversations_list):
        col1, col2, col3, col4 = st.columns([2, 2, 1,1])  # Create columns for each row
        with col1:
            st.write(conversation['conversation_id'])
        with col2:
            st.write(conversation['kb_name'])
        with col3:
            if not idx == 0:
                if conversation['pca_done'] == 1:
                    st.write("✅")
                else:
                    st.write("❌")
            else:
                st.write(conversation['pca_done'])
        with col4:
            if not idx == 0:       
                if st.button(f"Open Conversation",key=f"Button {conversation['conversation_id']}"):
                    open_conversation(conversation_id=conversation['conversation_id'])
          



