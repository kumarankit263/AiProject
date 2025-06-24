
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Imports
import os
import streamlit as st
import google.generativeai as genai

# Configure Gemini API key
genai.configure(api_key=os.getenv(""))

# Initialize Gemini model and chat object
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
chat = model.start_chat(history=[])

# Function to get response from Gemini
def get_gemini_response(user_input):
    response = chat.send_message(user_input, stream=True)
    return response

# Streamlit page setup
st.set_page_config(page_title="Gemini Chatbot Demo")
st.header("Gemini LLM Chat App with Chat History")

# Initialize session state for storing chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Text input for user
user_input = st.text_input("Enter your message:", key="input")

# Button to submit user input
if st.button("Start the chat") and user_input:
    # Get response from Gemini
    response_chunks = get_gemini_response(user_input)

    # Store user input in session state
    st.session_state["chat_history"].append(("You", user_input))

    # Display Gemini's response
    st.subheader("Gemini's Response:")
    full_response = ""
    for chunk in response_chunks:
        st.write(chunk.text)
        full_response += chunk.text

    # Store Gemini's response in session state
    st.session_state["chat_history"].append(("Gemini", full_response))

# Display full chat history
if st.session_state["chat_history"]:
    st.subheader("Chat History:")
    for speaker, message in st.session_state["chat_history"]:
        st.write(f"**{speaker}**: {message}")
