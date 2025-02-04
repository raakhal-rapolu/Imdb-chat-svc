from autogen import UserProxyAgent
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from utils.intent_classifier import classify_query
from query_agents import sql_agent, vector_agent

user_proxy = UserProxyAgent(name="User", human_input_mode="ALWAYS")


def route_query(user_query):
    intent = classify_query(user_query)

    message_history = [{"role": "user", "content": user_query}]

    if intent == "SQL":
        return sql_agent.generate_reply(messages=message_history)
    elif intent == "VECTOR":
        return vector_agent.generate_reply(messages=message_history)
    else:
        return "Query type not recognized."



# Example Queries
query1 = "What are the top 5 movies of 2019 only by meta score? "
query2 = "Summarize the movie plots of Steven Spielberg’s top-rated sci-fi movies."

print(route_query(query1))
print(route_query(query2))