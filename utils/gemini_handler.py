import os
import requests
import json
from utils.constants import gemini_url, gemini_api_key
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai




class GeminiLLMHandler:

    def gemini_api_call(self, input_query):

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(input_query)

        return response.text
