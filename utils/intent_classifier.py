from autogen import AssistantAgent
from utils.constants import gemini_api_key


intent_classifier = AssistantAgent(
    name="QueryRouter",
    llm_config={
        "config_list": [
            {
                "model": "gemini-pro",
                 "api_key": f'{gemini_api_key}',
                "api_type": "google"
            }
        ],
        "temperature": 0.3,
    },
    system_message="Classify if the query is best suited for 'SQLQueryAgent' (structured queries) or 'VectorSearchAgent' (semantic searches). Respond with 'SQL' or 'VECTOR'."
)


def classify_query(user_query):
    message_history = [{"role": "user", "content": user_query}]

    response = intent_classifier.generate_reply(messages=message_history)

    if isinstance(response, str):
        response = {"content": response.strip().upper()}

    return response.get("content", "").upper()



