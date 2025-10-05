import os
import re
import streamlit as st
from deep_translator import GoogleTranslator
import google.generativeai as genai

# ================================================================
#  CONFIGURATION
# ================================================================
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("❌ Missing API key. Please set GEMINI_API_KEY in Streamlit Secrets.")
else:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="Gemini Healthcare Chatbot", page_icon="🩺", layout="wide")

# ================================================================
#  HELPER FUNCTIONS
# ================================================================
def safe_translate(text, source_lang, target_lang):
    """Splits long text into 5000-character chunks for safe translation."""
    chunks = [text[i:i + 4900] for i in range(0, len(text), 4900)]
    translated_chunks = []
    for chunk in chunks:
        try:
            translated_chunk = GoogleTranslator(source=source_lang, target=target_lang).translate(chunk)
            translated_chunks.append(translated_chunk)
        except Exception as e:
            translated_chunks.append(f"[Translation error: {str(e)}]")
    return " ".join(translated_chunks)


def healthcare_chatbot(query_text):
    """Handles bilingual query and generates response using Gemini."""
    is_tamil = bool(re.search(r'[\u0B80-\u0BFF]', query_text))

    try:
        # Tamil → English
        if is_tamil:
            query_en = safe_translate(query_text, 'ta', 'en')
        else:
            query_en = query_text

        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(query_en)
        answer_en = response.text.strip()

        # English → Tamil
        if is_tamil:
            answer_ta = safe_translate(answer_en, 'en', 'ta')
            return f"**தமிழ் பதில்:** {answer_ta}"
        else:
            return f"**Answer:** {answer_en}"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ================================================================
#  STREAMLIT UI
# ================================================================
st.markdown(
    """
    <h2 style='text-align:center;color:#007BFF;'>
        🤖 Gemini Healthcare Chatbot
    </h2>
    <p style='text-align:center;'>Chat in <b>English</b> or <b>தமிழ்</b> about diseases, fitness, or healthcare 🩺</p>
    """,
    unsafe_allow_html=True
)

user_query = st.text_area("💬 Enter your health-related question:", height=100,
                          placeholder="E.g. இதய நோயின் ஆரம்ப அறிகுறிகள் என்ன? or What are early signs of heart disease?")

if st.button("Ask Gemini 🧠"):
    if user_query.strip():
        with st.spinner("💡 Thinking... please wait..."):
            reply = healthcare_chatbot(user_query)
            st.markdown(reply)
    else:
        st.warning("⚠️ Please enter a question before asking Gemini.")

st.markdown(
    """
    <hr>
    <div style='text-align:center; color:gray;'>
        <b>Powered by Google Gemini 2.5 Pro | Built with Streamlit</b>
    </div>
    """,
    unsafe_allow_html=True
)
