import streamlit as st
import helper_functions as hf

def main():
    st.title('Chat with Docs')
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])
    prompt = None
    if uploaded_file is not None and 'df' not in st.session_state:
        st.sidebar.write("PDF uploaded successfully!")
        df = hf.process_pdf(uploaded_file)
        # Mark the PDF as processed in session state
        st.session_state.df = df        
    
    search_query = st.text_input("Enter your search query")

    if st.button("Search"):
        prompt = hf.process_query(search_query,st.session_state.df)

    if prompt:
        response_placeholder = st.empty()  # Create a placeholder for streaming response
        full_response = ""
        # Stream the response to the user
        for chunk in hf.generate_response(prompt):
            full_response += chunk
            response_placeholder.text(full_response)
    # Reset file processing state if the user wants to upload another file
    if st.sidebar.button('Reset PDF'):
        if 'df' in st.session_state:
            del st.session_state['df']  # Remove the stored dataframe        
        st.sidebar.write("PDF reset successfully!")

if __name__=='__main__':
    main()