import streamlit as st

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

load_dotenv(override=True)

google_api_key = os.getenv('GOOGLE_API_KEY')

if google_api_key:
    print(f"Google API Key exists and begins with {google_api_key[:2]}")
else:
    print("Google API Key not set (and this is optional)")

gemini = OpenAI(api_key=google_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model_name = "gemini-2.0-flash"

###################################################################################################################3
# Set the page layout
st.set_page_config(page_title=" Chatbot", page_icon="💬", layout="centered")

st.title("💬 My RAG based Chatbot Interface")

with st.sidebar:
    st.header("📁 Upload Document")
    uploaded_files = st.file_uploader("Upload a PDF or txt file",accept_multiple_files=True, type=["pdf","txt"])
    submit_file = st.button("Submit File")


extracted_texts=[]

if uploaded_files and submit_file:

    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split(".")[-1].lower()

        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        extracted_texts.append(text)

        st.session_state.extracted_text = "\n\n---\n\n".join(extracted_texts)
        st.session_state.submitted = True
        st.session_state.uploaded_files = uploaded_files
        
        # st.session_state["pdf_text"] = text
        st.sidebar.success("✅ PDF uploaded and processed!")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input from user
user_input = st.chat_input("Say something...")

if user_input:
    # Store user message

    sys_prompt = f"""
                You are a RAG based chatbot assistant. You will be given a document content on which you have to reply with correct information only. 
                If you dont have any information that is related to the document or the current chat history then straight forward reply as sorry I do not have relevant information for that topic.  
                Please dont hallucinate with wrong answers. Be a helpful and polite assistant. 
                The system's hsitory information is passed here -- {st.session_state.messages}
                """

    # st.session_state.messages.append({"role": "system", "content": sys_prompt})    
    messages = [{"role": "system", "content": sys_prompt},
                {"role":"user", "content": user_input + st.session_state.extracted_text }]
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response (LLM response here)
    with st.spinner("Generating response..."):
        response = gemini.chat.completions.create(model=model_name, messages=messages)
        bot_response = response.choices[0].message.content


    # Store bot message
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        st.markdown(bot_response)
