import requests
import os

import yaml
from flask import Flask, jsonify, Response, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

PORT = 3333
thisUrl = "http://127.0.0.1:3333"
verificationTokens = {
    "OPENAI": "c772228fc2e84ecb83d298089f9fd4d0",
    "OPENPLUGIN": "4ca3ef06e7c5429f9140e02c0d67133e"
}

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
    for key, value in verificationTokens.items():
        modified_content = modified_content.replace(key+"_VERIFICATION_TOKEN", value)

    
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

# this is the key to getting authenticated and I was not able to find it in any of the client fetches 
OPENAI_TOKEN = "def456"

@app.route('/todos', methods=['GET', 'POST'])
def wrapper():
    global _TODO
    # verify header contains the correct token
    if request.headers.get('Authorization') != f"Bearer {OPENAI_TOKEN}":
        return jsonify(error="Unauthorized"), 401

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

OPENAI_CODE = "123"

@app.get("/oauth")
def oauth():
    # print headers
    headers = request.headers
    print("Headers: ", headers)
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

@app.post("/auth/oauth_exchange")
def oauth_exchange():
    print(f"Request headers: {request.headers}")
    print(f"Request data: {request.data}")
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
