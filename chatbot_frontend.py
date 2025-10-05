import streamlit as st
import google.generativeai as genai
from deep_translator import GoogleTranslator
import re
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Page setup
st.set_page_config(page_title="Gemini HealthBot", page_icon="🩺", layout="wide")
st.markdown("<h2 style='text-align:center;color:#007BFF;'>🤖 Gemini Healthcare Chatbot</h2>", unsafe_allow_html=True)
st.write("Chat in **English** or **தமிழ்** about health, symptoms, and wellness 💬")

# Function
def healthcare_chatbot(query_text):
    # Detect Tamil
    is_tamil = bool(re.search(r'[\u0B80-\u0BFF]', query_text))

    # Translate Tamil → English
    if is_tamil:
        query_en = GoogleTranslator(source='ta', target='en').translate(query_text)
    else:
        query_en = query_text

    # Get answer from Gemini
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    response = model.generate_content(query_en)
    answer_en = response.text

    # Translate back to Tamil if input was Tamil
    if is_tamil:
        answer_ta = GoogleTranslator(source='en', target='ta').translate(answer_en)
        return f"**தமிழ் பதில்:** {answer_ta}"
    else:
        return f"**Answer:** {answer_en}"

# Streamlit UI
user_query = st.text_input("💬 Ask your health-related question:")
if st.button("Ask Gemini 🧠"):
    if user_query.strip():
        with st.spinner("Thinking... 🤔"):
            try:
                reply = healthcare_chatbot(user_query)
                st.markdown(reply)
            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
    else:
        st.warning("Please enter a question to ask Gemini.")
