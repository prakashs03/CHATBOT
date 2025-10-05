import os
import re
import streamlit as st
from deep_translator import GoogleTranslator
import google.generativeai as genai

# ================================================================
# CONFIGURATION
# ================================================================
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("❌ Missing API key. Please set GEMINI_API_KEY in Streamlit Secrets.")
else:
    genai.configure(api_key=api_key)

st.set_page_config(page_title="🩺 Gemini Healthcare Chatbot", page_icon="🤖", layout="wide")

# ================================================================
# HELPER FUNCTIONS
# ================================================================
def safe_translate(text, source_lang, target_lang):
    """Translate safely even if text > 5000 characters by chunking."""
    chunks = [text[i:i + 4900] for i in range(0, len(text), 4900)]
    translated_chunks = []
    for chunk in chunks:
        try:
            translated_chunks.append(
                GoogleTranslator(source=source_lang, target=target_lang).translate(chunk)
            )
        except Exception as e:
            translated_chunks.append(f"[Translation error: {e}]")
    return " ".join(translated_chunks)


def healthcare_chatbot(query_text):
    """Gemini chatbot that adapts between short and detailed answers."""
    is_tamil = bool(re.search(r'[\u0B80-\u0BFF]', query_text))

    try:
        # Translate Tamil → English if needed
        query_en = safe_translate(query_text, 'ta', 'en') if is_tamil else query_text

        # Detect detail level from user intent
        if any(word in query_en.lower() for word in ["detail", "explain", "more", "elaborate", "in depth", "full"]):
            prompt = (
                f"Provide a detailed, medically accurate response to this healthcare question:\n{query_en}\n"
                "Include causes, symptoms, prevention, and treatments where relevant."
            )
        else:
            prompt = (
                f"Answer briefly in 1–2 sentences, in clear and simple language, medically correct:\n{query_en}"
            )

        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(prompt)
        answer_en = response.text.strip()

        # Translate English → Tamil if user asked in Tamil
        if is_tamil:
            answer_ta = safe_translate(answer_en, 'en', 'ta')
            return f"**தமிழ் பதில்:** {answer_ta}"
        else:
            return f"**Answer:** {answer_en}"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


# ================================================================
# STREAMLIT UI
# ================================================================
st.markdown(
    """
    <h2 style='text-align:center;color:#007BFF;'>
        🤖 Gemini Healthcare Chatbot
    </h2>
    <p style='text-align:center;'>Ask questions in <b>English</b> or <b>தமிழ்</b></p>
    <p style='text-align:center;color:gray;'>For short answers, ask normally. For detailed info, say “explain” or “in detail.”</p>
    """,
    unsafe_allow_html=True
)

query = st.text_area("💬 Enter your health question:", height=100,
                     placeholder="e.g., What are early signs of heart disease? / இதய நோயின் அறிகுறிகள் என்ன?")

if st.button("Ask Gemini 🧠"):
    if query.strip():
        with st.spinner("💡 Thinking... please wait..."):
            response = healthcare_chatbot(query)
            st.markdown(response)
    else:
        st.warning("⚠️ Please enter a question first.")

st.markdown(
    """
    <hr>
    <div style='text-align:center;color:gray;'>
        <b>Powered by Gemini 2.5 Pro | Built with Streamlit</b>
    </div>
    """,
    unsafe_allow_html=True
)
