from flask import Flask
from flask_cors import CORS
import os

from webserver import endpoints

app = Flask(__name__)
CORS(app)


# Register Blueprints for endpoints and Swagger UI
app.register_blueprint(endpoints.swagger_ui_blueprint)
app.register_blueprint(endpoints.blueprint)

@app.route("/check-alive")
def check_status():
    return "I am here"

if __name__ == '__main__':
    port = 5000
    app.run(debug=True, port = port, host = '0.0.0.0')