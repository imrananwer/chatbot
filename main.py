# main.py
import os
import json
import datetime
import sys

# MODE: streamlit or chainlit
MODE = os.getenv("MODE", "streamlit").lower()
IS_STREAMLIT = MODE == "streamlit"

# --- Conditional imports ---
if IS_STREAMLIT:
    import streamlit as st
else:
    import chainlit as cl

from litellm import completion

# --- Load API Key ---
if IS_STREAMLIT:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
else:
    from dotenv import load_dotenv
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("\u274c GEMINI_API_KEY not found.")

# --- Shared Response Function ---
def get_gemini_response(history, message_text):
    history.append({"role": "user", "content": message_text})
    response = completion(
        model="gemini/gemini-2.0-flash",
        api_key=gemini_api_key,
        messages=history
    )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    return reply, history

# =============================
# CHAINLIT MODE
# =============================
if not IS_STREAMLIT:
    @cl.on_chat_start
    async def start():
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r") as f:
                cl.user_session.set("chat_history", json.load(f))
        else:
            cl.user_session.set("chat_history", [])
        await cl.Message(content="🤖 Welcome to Imran AI (Chainlit)! Ask me anything.").send()

    @cl.on_message
    async def main(message: cl.Message):
        msg = cl.Message(content="Thinking...")
        await msg.send()

        history = cl.user_session.get("chat_history") or []
        try:
            reply, updated_history = get_gemini_response(history, message.content)
            msg.content = reply
            await msg.update()
            cl.user_session.set("chat_history", updated_history)
        except Exception as e:
            msg.content = f"\u274c Error: {str(e)}"
            await msg.update()

    @cl.on_chat_end
    async def end():
        history = cl.user_session.get("chat_history") or []
        filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(history, f, indent=2)

# =============================
# STREAMLIT MODE
# =============================
if IS_STREAMLIT:
    st.set_page_config(page_title="Imran AI", page_icon="🤖")

    # Custom Dark Theme Styling
    st.markdown("""
        <style>
        body {
            background-color: #0e1117;
            color: white;
        }
        .stChatMessage, .stTextInput, .stTextArea {
            background-color: #1c1f26;
            color: white;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton>button {
            background-color: #4a90e2;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🤖 Imran AI Assistant")

    if "history" not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("Ask anything...")
    if user_input:
        with st.spinner("Thinking..."):
            try:
                reply, updated_history = get_gemini_response(st.session_state.history, user_input)
                st.session_state.history = updated_history
                st.chat_message("user").markdown(user_input)
                st.chat_message("assistant").markdown(reply)
            except Exception as e:
                st.error(f"\u274c Error: {str(e)}")
