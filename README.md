# 🤖 Imran AI Chatbot

This is a smart chatbot powered by Gemini and built with:

- 🔹 Chainlit (for local, fast prototyping)
- 🔹 Streamlit (for deploying on web)
- 🔐 Secure API via `.streamlit/secrets.toml`

## 🚀 How to run

### 🔹 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

python -m venv venv

venv\Scripts\activate  # (Windows)
pip install -r requirements.txt
GEMINI_API_KEY = "your-real-api-key"

streamlit run main.py





