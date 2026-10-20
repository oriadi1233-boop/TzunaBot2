import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# This version checks EVERY possible place for the key
# 1. Checks Streamlit Secrets
# 2. Checks System Environment Variables
# 3. Falls back to the hardcoded key for local testing
API_KEY = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "YOUR_API_KEY_HERE"
MODEL_NAME = "gemini-3.1-flash-lite"

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    st.error("🔑 API Key not found!")
    st.info("To fix this: Go to 'Manage App' -> 'Secrets' and add: GOOGLE_API_KEY = 'your_key_here'")
    st.stop()

genai.configure(api_key=API_KEY)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are a precise, evidence-based nutrition and behavior coach (Nutrition Coach Bot v1.1).
CRITICAL: This is a web interface. IGNORE ALL JSON OUTPUT CONTRACTS. Reply in normal, conversational text.
Maintain all safety, identity, and coaching rules from the v1.1 prompt.
Be friendly, approachable, and demanding.
"""

# --- UI SETUP ---
st.set_page_config(page_title="Nutrition Coach AI", page_icon="🍏")
st.title("🍏 Nutrition Coach AI")
st.markdown("Your evidence-based guide to health and discipline.")

if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tell me about your meals..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")
            full_response = "Sorry, I hit a snag. Try again!"

    st.session_state.messages.append({"role": "assistant", "content": full_response})
