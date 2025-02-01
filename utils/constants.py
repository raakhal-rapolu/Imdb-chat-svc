import os
from dotenv import load_dotenv

load_dotenv()

gemini_url = os.environ.get('GEMINI_URL')
gemini_api_key = os.environ["GEMINI_API_KEY"]
groq_api_key = os.environ["GROQ_API_KEY"]