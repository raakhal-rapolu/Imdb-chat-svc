import os
from groq import Groq
from utils.constants import groq_api_key

class GroqLLMHandler:
    def __init__(self):
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"

    def groq_api_call(self, input_query):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": input_query}],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"