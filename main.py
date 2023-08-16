import requests
import os

import yaml
from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

PORT = 3333
thisUrl = "YOUR_ROOT_URL_HERE"
verificationToken = "YOUR_VERIFICATION_TOKEN_HERE"

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
CORS(app, origins=[thisUrl, "https://chat.openai.com"])

api_url = 'https://example.com'

_TODO = []


@app.route('/.well-known/ai-plugin.json')
def serve_manifest():
    with open(os.path.join(os.path.dirname(__file__), 'ai-plugin.json'), 'r') as f:
        content = f.read()
    
    # Replace PLUGIN_HOSTNAME with thisUrl
    modified_content = content.replace('PLUGIN_HOSTNAME', thisUrl).replace('VERIFICATION_TOKEN', verificationToken)

    
    return Response(modified_content, content_type='application/json')



@app.route('/openapi.yaml')
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), 'openapi.yaml'), 'r') as f:
        yaml_data = f.read()

    # Replace PLUGIN_HOSTNAME with thisUrl
    modified_yaml_data = yaml_data.replace('PLUGIN_HOSTNAME', thisUrl)

    # Convert the YAML string to a Python dictionary and then jsonify it
    yaml_dict = yaml.load(modified_yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_dict)



@app.route('/openapi.json')
def serve_openapi_json():
    with open(os.path.join(os.path.dirname(__file__), 'openapi.json'), 'r') as f:
        json_data = f.read()

    # Replace PLUGIN_HOSTNAME with thisUrl
    modified_json_data = json_data.replace('PLUGIN_HOSTNAME', thisUrl)

    return Response(modified_json_data, content_type='application/json')



@app.route('/todos', methods=['GET', 'POST'])
def wrapper():
    global _TODO

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

OPENAI_CODE = "abc123"

@app.get("/oauth")
def oauth():
    query_string = request.query_string.decode('utf-8')
    parts = query_string.split('&')
    kvps = {}
    for part in parts:
        k, v = part.split('=')
        v = v.replace("%2F", "/").replace("%3A", ":")
        kvps[k] = v
    print("OAuth key value pairs from the ChatGPT Request: ", kvps)
    url = kvps["redirect_uri"] + f"?code={OPENAI_CODE}&state={kvps['state']}"
    print("URL: ", url)
    return f'<a href="{url}">Click to authorize</a>'

# Sample names
OPENAI_CLIENT_ID = "id"
OPENAI_CLIENT_SECRET = "secret"
# this is the key to getting authenticated and I was not able to find it in any of the client fetches 
OPENAI_TOKEN = "def456"

@app.post("/auth/oauth_exchange")
def oauth_exchange():
    newRequest = request.get_json(force=True)

    print(f"oauth_exchange {newRequest=}")

    if newRequest["client_id"] != OPENAI_CLIENT_ID:
        raise RuntimeError("bad client ID")
    if newRequest["client_secret"] != OPENAI_CLIENT_SECRET:
        raise RuntimeError("bad client secret")
    if newRequest["code"] != OPENAI_CODE:
        raise RuntimeError("bad code")

    return {
        "access_token": OPENAI_TOKEN,
        "token_type": "bearer"
    }


if __name__ == '__main__':
    app.run(port=PORT, debug=True)
