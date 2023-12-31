import requests
import os

import yaml
from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

PORT = 3333
thisUrl = "http://127.0.0.1:3333"

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
CORS(app, origins=[thisUrl, "https://chat.openai.com"])

api_url = 'https://example.com'

_TODO = []


@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    scheme = request.headers.get('X-Forwarded-Proto', 'http')
    thisUrl = f"{scheme}://{request.host}"
    
    # print headers
    print("\nmanifest headers: \n",request.headers)
    # get current host
    scheme = request.headers.get('X-Forwarded-Proto', 'http')
    thisUrl = f"{scheme}://{request.host}"
    
    with open(os.path.join(os.path.dirname(__file__), 'ai-plugin.json'), 'r') as f:
        content = f.read()
    
    # Replace PLUGIN_HOSTNAME with thisUrl
    modified_content = content.replace('PLUGIN_HOSTNAME', thisUrl)

    
    return Response(modified_content, content_type='application/json')


@app.route('/openapi.yaml')
def serve_openapi_yaml():
    scheme = request.headers.get('X-Forwarded-Proto', 'http')
    thisUrl = f"{scheme}://{request.host}"

    with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r') as f:
        yaml_data = f.read()

    # Replace PLUGIN_HOSTNAME with thisUrl
    modified_yaml_data = yaml_data.replace('PLUGIN_HOSTNAME', thisUrl)

    # Convert the YAML string to a Python dictionary and then jsonify it
    yaml_dict = yaml.load(modified_yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_dict)

# /openapi.json not supported 
@app.route('/openapi.json')
def serve_openapi_json():
    return send_from_directory(os.path.dirname(__file__), 'openapi.json')



@app.route('/todos', methods=['GET', 'POST'])
def wrapper():
    global _TODO

    print("\n/todo headers: \n",request.headers)

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
