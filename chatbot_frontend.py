# ================================================================
#  GEMINI HEALTHCARE CHATBOT - STREAMLIT FRONTEND
# ================================================================
# Requirements:
# pip install streamlit requests googletrans==4.0.0-rc1
# Run this app with:
#    streamlit run chatbot_frontend.py
# ================================================================

import streamlit as st
import requests
from googletrans import Translator

# ================================================================
#  CONFIG
# ================================================================
API_URL = "http://127.0.0.1:8000/ask"  # FastAPI backend URL
translator = Translator()

st.set_page_config(page_title="💊 Gemini HealthBot", page_icon="🧠", layout="wide")

# ================================================================
#  UI HEADER
# ================================================================
st.title("🤖 Gemini Healthcare Chatbot")
st.markdown("""
This AI chatbot helps answer **medical and healthcare-related queries** in both **English 🇬🇧** and **Tamil 🇮🇳**.  
Powered by **Gemini 2.5 Pro** and your FastAPI backend.
""")

# Add a horizontal line
st.markdown("---")

# ================================================================
#  CHAT INTERFACE
# ================================================================
# Store chat history in Streamlit session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Text input
query_text = st.text_area("💬 Ask your health question:", placeholder="Type your question in English or Tamil...")

# Send button
if st.button("Ask"):
    if query_text.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing your query with Gemini..."):
            try:
                # Send request to FastAPI backend
                response = requests.get(API_URL, params={"q": query_text})
                data = response.json()

                # Handle API errors
                if "error" in data:
                    st.error("⚠️ " + data["error"])
                else:
                    answer = data.get("answer", "")
                    language = data.get("language", "english")

                    # Translate if needed (for Tamil/English mix inputs)
                    if language == "tamil":
                        display_text = f"**தமிழ் பதில்:** {answer}"
                    else:
                        display_text = f"**Answer:** {answer}"

                    # Append to history
                    st.session_state.chat_history.append({"question": query_text, "answer": display_text})

            except Exception as e:
                st.error(f"⚠️ Request failed: {e}")

# ================================================================
#  DISPLAY CHAT HISTORY
# ================================================================
if st.session_state.chat_history:
    st.markdown("### 🩺 Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**🧍‍♂️ You:** {chat['question']}")
        st.markdown(f"🤖 {chat['answer']}")
        st.markdown("---")
