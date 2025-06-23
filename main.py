import os
import json
import datetime
from dotenv import load_dotenv
import chainlit as cl
from litellm import completion

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Ensure the API key is provided
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

# Triggered when a new chat session starts
@cl.on_chat_start
async def start():
    """Initialize the chat session."""

    # Optionally load existing history if file exists
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r") as f:
            previous_history = json.load(f)
            cl.user_session.set("chat_history", previous_history)
    else:
        cl.user_session.set("chat_history", [])

    await cl.Message(content="🤖 Welcome to the Imran AI Assistant! How can I help you today?").send()

# Triggered when a user sends a message
@cl.on_message
async def main(message: cl.Message):
    """Handle incoming user message and respond using Gemini."""

    # Show a temporary 'Thinking...' message
    msg = cl.Message(content="Thinking...")
    await msg.send()

    # Retrieve history or initialize if empty
    history = cl.user_session.get("chat_history") or []

    # Add user's message to history
    history.append({"role": "user", "content": message.content})

    try:
        # Get response from Gemini via LiteLLM (no await here!)
        response = completion(
            model="gemini/gemini-2.0-flash",
            api_key=gemini_api_key,
            messages=history
        )

        # Extract the response text
        response_content = response.choices[0].message.content

        # Update the thinking message with the real response
        msg.content = response_content
        await msg.update()

        # Add assistant's reply to history
        history.append({"role": "assistant", "content": response_content})

        # Save updated history back to the session
        cl.user_session.set("chat_history", history)

        # Optional logging to console
        print(f"User: {message.content}")
        print(f"Assistant: {response_content}")

    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
        print(f"Error occurred: {str(e)}")

# Triggered when chat ends
@cl.on_chat_end
async def on_chat_end():
    """Save chat history when the session ends."""
    history = cl.user_session.get("chat_history") or []
    filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Chat history saved to {filename}.")
