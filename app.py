import os
import re
import streamlit as st
from deep_translator import GoogleTranslator
import google.generativeai as genai

# ================================================================
#  CONFIGURATION
# ================================================================

# Get Gemini API key securely from Streamlit Secrets
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if not api_key:
    st.error("❌ Missing API key. Please set GEMINI_API_KEY in Streamlit Secrets.")
else:
    genai.configure(api_key=api_key)

# Streamlit page setup
st.set_page_config(page_title="Gemini Healthcare Chatbot", page_icon="🩺", layout="wide")

# ================================================================
#  CHATBOT FUNCTION
# ================================================================
def healthcare_chatbot(query_text):
    """
    Handles multilingual input (Tamil/English) and returns an AI-generated answer.
    """
    # Detect Tamil input
    is_tamil = bool(re.search(r'[\u0B80-\u0BFF]', query_text))

    try:
        # Translate Tamil → English
        if is_tamil:
            query_en = GoogleTranslator(source='ta', target='en').translate(query_text)
        else:
            query_en = query_text

        # Initialize Gemini model
        model = genai.GenerativeModel("models/gemini-2.5-pro")

        # Generate response
        response = model.generate_content(query_en)
        answer_en = response.text.strip()

        # Translate back to Tamil if needed
        if is_tamil:
            answer_ta = GoogleTranslator(source='en', target='ta').translate(answer_en)
            return f"**தமிழ் பதில்:** {answer_ta}"
        else:
            return f"**Answer:** {answer_en}"

    except Exception as e:
        return f"⚠️ Error generating answer: {str(e)}"

# ================================================================
#  UI DESIGN
# ================================================================
st.markdown(
    """
    <h2 style='text-align:center;color:#007BFF;'>
        🤖 Gemini Healthcare Chatbot
    </h2>
    <p style='text-align:center;'>Chat in <b>English</b> or <b>தமிழ்</b> about health, fitness, or diseases 🩺</p>
    """,
    unsafe_allow_html=True
)

# Text input box
user_query = st.text_area("💬 Enter your health-related question:", height=100, placeholder="E.g. What are the early signs of heart disease?")

# Ask button
if st.button("Ask Gemini 🧠"):
    if user_query.strip():
        with st.spinner("💡 Thinking... please wait..."):
            reply = healthcare_chatbot(user_query)
            st.markdown(reply)
    else:
        st.warning("⚠️ Please enter a question before asking Gemini.")

# ================================================================
#  FOOTER
# ================================================================
st.markdown(
    """
    <hr>
    <div style='text-align:center; color:gray;'>
        <b>Powered by Google Gemini 2.5 Pro | Built with Streamlit</b>
    </div>
    """,
    unsafe_allow_html=True
)
