import streamlit as st
import helper_functions as hf
import shutil
import os
import numpy as np
from speech import *
import pandas as pd

file_path = r"D:\Programming\AI\Basics\intern-assignments\Chat With Docs\streamlit_app\temp_files\output.wav"
def main():    
    st.session_state.setdefault('df', None)
    st.session_state.setdefault('recording', 0)
    st.session_state.setdefault('query','')
    prompt = None    
    st.title('Chat with Docs')

    # PDF Upload
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded_file:
        st.sidebar.write("PDF uploaded successfully!")                
    # Process the uploaded pdf
    if st.sidebar.button('Process PDF'):
        st.session_state.df = hf.process_pdf(uploaded_file)

    # Search functionality
    col1,col2 = st.columns([3,1])     
    with col1:
        st.session_state.query = st.text_input("Enter your search query")
    
    with col2:       
        if st.button('Record Audio') and st.session_state.recording == 0:                        
            st.session_state.query = ''
            start_recording()   
            print('Started')
            st.session_state.recording = 1
        if st.button('Stop Recording') and st.session_state.recording == 1:            
            stop_recording()                             
            print('Stopped')
            st.session_state.recording = 0                  
            if file_path is not None:                      
                st.session_state.query = text_to_speech(file_path)               
                if st.session_state.query:     
                    prompt = hf.process_query(st.session_state.query,st.session_state.df)    
    st.write(st.session_state.query)      
    if st.session_state.query:                 
        prompt = hf.process_query(st.session_state.query,st.session_state.df)       

    if prompt:
        response_placeholder = st.empty()  # Create a placeholder for streaming response
        full_response = ""
        # Stream the response to the user
        for chunk in hf.generate_response(prompt):
            full_response += chunk
            response_placeholder.markdown(full_response)        
    


if __name__=='__main__':
    main()