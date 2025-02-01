from flask import jsonify, make_response, request
import os
from flask_restx import Resource, reqparse
from webserver.api_models import inference_chat_api, create_index_parser, delete_index_model, inference_api_model
from webserver.extensions import api
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Blueprint
import json
import requests
from chromadb_handler.chromadb_handler import ChromaDBHandler
from utils.gemini_handler import GeminiLLMHandler
from utils.constants import EMBED_MODEL, OLLAMA_URL
from utils.groq_custom_llm import GroqLLMHandler
from utils import prompt_reader



import chromadb

from sentence_transformers import SentenceTransformer

import os
CHROMADB_PATH = os.getenv("CHROMADB_PATH")
TMP_DIR = os.getenv("TMP_DIR")

# Load sentence transformer model
embedding_model = SentenceTransformer(EMBED_MODEL)


# Constants
API_VERSION = '/api/v1'
CATALOG_MODULE = '/imdb-chatbot-svc'
CORE_PREFIX = CATALOG_MODULE + API_VERSION


blueprint = Blueprint('api', __name__, url_prefix=CORE_PREFIX)
api.init_app(blueprint)

SWAGGER_URL = CORE_PREFIX
API_URL = CORE_PREFIX + '/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={'app_name': 'GenAI'}
)

# Define API namespace
chat_namespace = api.namespace(name='imdb-chatbot-svc', description="LLM Inference API endpoints")
api.add_namespace(chat_namespace)

index_namespace = api.namespace(name='index', description="Create Index in Vector Store")
api.add_namespace(index_namespace)




@chat_namespace.route("/chat")
class InferenceChatBot(Resource):

    @api.expect(inference_chat_api)
    def post(self):
        try:
            request_data = request.get_json()
            user_message = request_data.get('message')
            model = request_data.get('model', 'llama3.2')
            stream = request_data.get('stream', False)

            if not user_message:
                return make_response(
                    jsonify({"error": "Message field is required."}), 400
                )

            payload = {
                "model": model,
                "prompt": user_message,
                "stream": stream
            }

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                return make_response(jsonify(response.json()), 200)
            else:
                return make_response(
                    jsonify({
                        "error": "Failed to process the request.",
                        "details": response.text
                    }), response.status_code
                )
        except Exception as e:
            return make_response(
                jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
            )



@chat_namespace.route("/imdb-chat")
class IMDBChatBot(Resource):
    @api.expect(inference_chat_api)

    def post(self):
        try:
            request_data = request.get_json()
            user_message = request_data.get("message")

            chroma_client = chromadb.PersistentClient(
                path=CHROMADB_PATH)

            collection = chroma_client.get_collection(name="imdb_chatbot")

            if not user_message:
                return make_response(
                    jsonify({"error": "Message field is required."}), 400
                )

            query_embedding = embedding_model.encode(user_message).tolist()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )

            if not results["documents"] or not results["documents"][0]:
                return make_response(jsonify({"response": "No relevant movies found."}), 200)

            context = "\n\n".join([
                f"Title: {doc['title']}\n"
                f"Year: {doc['year']}\n"
                f"Certificate: {doc['certificate']}\n"
                f"Runtime: {doc['runtime']}\n"
                f"Genre: {doc['genre']}\n"
                f"IMDB Rating: {doc['rating']}\n"
                f"Overview: {doc['overview']}\n"
                f"Meta Score: {doc['meta_score']}\n"
                f"Director: {doc['director']}\n"
                f"Stars: {(doc['stars'])}\n"
                f"Number of Votes: {doc['votes']}\n"
                f"Gross Revenue: {doc['gross']}"
                for doc in results["metadatas"][0]
            ])


            prompt = prompt_reader.load_prompts()["imdb_chat_prompt"].format(user_message=user_message, context=context)


            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(OLLAMA_URL, headers=headers, data=json.dumps(payload))


            # Handle response
            if response.status_code == 200:
                return make_response(jsonify(response.json()), 200)
            else:
                return make_response(
                    jsonify({
                        "error": "Failed to process the request via Ollama.",
                        "details": response.text
                    }), response.status_code
                )

        except Exception as e:
            return make_response(
                jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
            )


@chat_namespace.route('/gemini-text-inference')
class GeminiTextInference(Resource):
    @api.expect(inference_api_model)
    def post(self):
        try:
            data = request.json
            input_query = data['message']

            llm_handler = GeminiLLMHandler()

            llm_response = llm_handler.gemini_api_call(input_query)

            return {'response': llm_response}, 200
        except Exception as e:
            return {'error': str(e)}, 500

@chat_namespace.route("/gemini-imdb-chat")
class GeminiIMDBChatBot(Resource):
    @api.expect(inference_api_model)
    def post(self):
        try:
            request_data = request.get_json()
            user_message = request_data.get("message")

            if not user_message:
                return make_response(
                    jsonify({"error": "Message field is required."}), 400
                )

            chroma_client = chromadb.PersistentClient(
                path=CHROMADB_PATH
            )
            collection = chroma_client.get_or_create_collection(name="imdb_chatbot")

            query_embedding = embedding_model.encode(user_message).tolist()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )

            if not results["documents"] or not results["documents"][0]:

                return make_response(jsonify({"response": "No relevant movies found."}), 200)

            context = "\n\n".join([
                f"Title: {doc['title']}\n"
                f"Year: {doc['year']}\n"
                f"Certificate: {doc['certificate']}\n"
                f"Runtime: {doc['runtime']}\n"
                f"Genre: {doc['genre']}\n"
                f"IMDB Rating: {doc['rating']}\n"
                f"Overview: {doc['overview']}\n"
                f"Meta Score: {doc['meta_score']}\n"
                f"Director: {doc['director']}\n"
                f"Stars: {(doc['stars'])}\n"
                f"Number of Votes: {doc['votes']}\n"
                f"Gross Revenue: {doc['gross']}"
                for doc in results["metadatas"][0]
            ])

            prompt = prompt_reader.load_prompts()["imdb_chat_prompt"].format(user_message=user_message, context=context)


            llm_handler = GeminiLLMHandler()
            gemini_response = llm_handler.gemini_api_call(prompt)

            return make_response(jsonify({"response": gemini_response}), 200)

        except Exception as e:
            return make_response(
                jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
            )


@chat_namespace.route("/groq-imdb-chat")
class GroqIMDBChatBot(Resource):
    @api.expect(inference_api_model)

    def post(self):
        try:
            request_data = request.get_json()
            user_message = request_data.get("message")

            if not user_message:
                return make_response(
                    jsonify({"error": "Message field is required."}), 400
                )

            chroma_client = chromadb.PersistentClient(
                path=CHROMADB_PATH
            )
            collection = chroma_client.get_collection(name="imdb_chatbot")

            query_embedding = embedding_model.encode(user_message).tolist()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )

            if not results["documents"] or not results["documents"][0]:

                return make_response(jsonify({"response": "No relevant movies found."}), 200)

            context = "\n\n".join([
                f"Title: {doc['title']}\n"
                f"Year: {doc['year']}\n"
                f"Certificate: {doc['certificate']}\n"
                f"Runtime: {doc['runtime']}\n"
                f"Genre: {doc['genre']}\n"
                f"IMDB Rating: {doc['rating']}\n"
                f"Overview: {doc['overview']}\n"
                f"Meta Score: {doc['meta_score']}\n"
                f"Director: {doc['director']}\n"
                f"Stars: {(doc['stars'])}\n"
                f"Number of Votes: {doc['votes']}\n"
                f"Gross Revenue: {doc['gross']}"
                for doc in results["metadatas"][0]
            ])

            prompt = prompt_reader.load_prompts()["imdb_chat_prompt"].format(user_message=user_message, context=context)

            groq_handler = GroqLLMHandler()
            groq_response = groq_handler.groq_api_call(prompt)

            return make_response(jsonify({"response": groq_response}), 200)

        except Exception as e:
            return make_response(
                jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
            )

@index_namespace.route("/create_index")
class CreateIndex(Resource):
    @api.expect(create_index_parser)
    def post(self):
        try:
            if 'file' not in request.files:
                return make_response(jsonify({"error": "No file provided."}), 400)

            file = request.files['file']
            collection_name = request.args.get("collection_name")  # FIXED
            print(collection_name)

            if file.filename == '':
                return make_response(jsonify({"error": "Empty file name."}), 400)

            file_path = os.path.join(TMP_DIR, file.filename)
            file.save(file_path)

            db_handler = ChromaDBHandler(
                db_path=CHROMADB_PATH,
                collection_name=str(collection_name))

            df = db_handler.load_and_process_csv(file_path)
            db_handler.index_data_into_chroma(df)

            return make_response(jsonify({"message": "Index created successfully."}), 200)
        except Exception as e:
            return make_response(jsonify({"error": "Failed to create index.", "details": str(e)}), 500)


@index_namespace.route("/delete_index")
class DeleteIndex(Resource):
    @api.expect(delete_index_model)
    def post(self):
        try:
            request_data = request.get_json()
            collection_name = request_data.get('collection_name')

            if not collection_name:
                return make_response(jsonify({"error": "Collection name is required."}), 400)

            db_handler = ChromaDBHandler(
                db_path=CHROMADB_PATH,
                collection_name=collection_name)

            db_handler.chroma_client.delete_collection(name=collection_name)

            return make_response(jsonify({"message": "Index deleted successfully."}), 200)
        except Exception as e:
            return make_response(jsonify({"error": "Failed to delete index.", "details": str(e)}), 500)


@index_namespace.route("/collections")
class GetCollections(Resource):
    def get(self):
        try:
            db_handler = ChromaDBHandler(db_path=CHROMADB_PATH)
            collections = db_handler.get_all_collections()

            return make_response(jsonify({"collections": collections}), 200)
        except Exception as e:
            return make_response(jsonify({"error": "Failed to fetch collections.", "details": str(e)}), 500)
