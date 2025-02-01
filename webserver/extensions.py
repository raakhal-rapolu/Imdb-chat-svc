import tomllib

from flask_restx import Api

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

api = Api(version=data['tool']['poetry']['version'], title='IMDB Conversation Chatbot', description='Building chatbot on IMDB Dataset')
