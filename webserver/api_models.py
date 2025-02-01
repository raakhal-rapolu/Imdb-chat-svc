from flask_restx import reqparse, fields
from werkzeug.datastructures import FileStorage

from webserver.extensions import api

inference_chat_api = api.model('ChatRequest', {
    'message': fields.String(required=True, description="User's input message to the chat model."),
    'stream': fields.Boolean(default=False, description="Flag to enable/disable streaming responses."),
    'model': fields.String(default="llama3.2", description="The model to use for inference.")
})

create_index_parser = reqparse.RequestParser()
create_index_parser.add_argument('file', type=FileStorage, location='files', required=True, help="File to be uploaded.")
create_index_parser.add_argument('collection_name', type=str, required=True,
                                 help="Name of the collection to index the data into.")

delete_index_model = api.model('DeleteIndex', {
    'collection_name': fields.String(required=True, description="Name of the collection to be deleted.")
})

inference_api_model = api.model('InferenceModel', {
    'message': fields.String(required=True, description='Input text message')
})
