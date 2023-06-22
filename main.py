import requests
import os

import yaml
from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

PORT = 3333
thisUrl = "http://localhost:3333"

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
CORS(app, origins=[thisUrl, "https://chat.openai.com"])

api_url = 'https://example.com'

_TODO = []


@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__), 'ai-plugin.json')


@app.route('/openapi.yaml')
def serve_openapi_yaml():
    # with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r') as f:
    #     yaml_data = f.read()
    # yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    # return jsonify(yaml_data)
    return send_from_directory(os.path.dirname(__file__), 'openapi.json')


@app.route('/openapi.json')
def serve_openapi_json():
    return send_from_directory(os.path.dirname(__file__), 'openapi.json')


@app.route('/todos', methods=['GET', 'POST'])
def wrapper():
    global _TODO

    headers = {
        'Content-Type': 'application/json',
    }

    if request.method == 'GET':
        # Get the list of todos
        return jsonify(todos=_TODO), 200

    elif request.method == 'POST':
        # Add a todo to the list
        todo = request.json.get('todo')
        _TODO.append(todo)
        return jsonify(todo=todo), 200

    else:
        raise NotImplementedError(f'Method {request.method} not implemented in wrapper for /todos')


# Serve the logo located at ./logo.png in /logo.png
@app.route('/logo.png')
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), 'logo.png')


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
