import os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.environ["GEMINI_API_KEY"]
groq_api_key = os.environ["GROQ_API_KEY"]

EMBED_MODEL="all-MiniLM-L6-v2"

OLLAMA_URL = "http://localhost:11434/api/generate"