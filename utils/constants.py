import os

from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.environ["GEMINI_API_KEY"]
groq_api_key = os.environ["GROQ_API_KEY"]

chroma_path =os.environ["CHROMADB_PATH"]

temp_dir = os.environ["TMP_DIR"]

EMBED_MODEL="all-MiniLM-L6-v2"

ollama_url =os.environ["OLLAMA_URL"]

RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

DB_CONFIG = {
    "dbname": "imdb",
    "user": "imdb_user",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

