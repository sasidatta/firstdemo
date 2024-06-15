import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Environment variables for authentication and configuration
DUMMY_USER = os.getenv('DUMMY_USER')
DUMMY_PASSWORD = os.getenv('DUMMY_PASSWORD')
MAX_UPTIME_MIN = os.getenv('MAX_UPTIME_MIN')

# Check if required environment variables are set
if not DUMMY_USER or not DUMMY_PASSWORD or not MAX_UPTIME_MIN:
    print("Required DUMMY_USERNAME, DUMMY_PASSWORD and MAX_UPTIME_MIN to be set via environment.")
    exit(1)

TOKEN_URL = "https://dummyjson.com/docs/auth"

# Authenticate and get bearer token
def get_bearer_token():
    response = requests.post(TOKEN_URL, auth=(DUMMY_USER, DUMMY_PASSWORD))
    if response.status_code == 200:
        return response.json().get('token')
    return None

# Initialize bearer token
bearer_token = get_bearer_token()

# Headers for authenticated requests
headers = {
    'Authorization': f'Bearer {bearer_token}'
}

@app.route('/api/products', methods=['GET'])
def get_products():
    limit = request.args.get('limit', 10)
    skip = request.args.get('skip', 0)
    
    response = requests.get(f'https://dummyjson.com/products?limit={limit}&skip={skip}', headers=headers)
    
    if response.status_code == 200:
        products = response.json().get('products', [])
        return jsonify([{"id": p["id"], "title": p["title"], "description": p["description"]} for p in products])
    return jsonify({"error": "Failed to fetch products"}), response.status_code

@app.route('/api/product/<id>', methods=['GET'])
def get_product(id):
    if not id.isdigit():
        return jsonify({"error": "invalid value for 'id'"}), 400
    
    response = requests.get(f'https://dummyjson.com/products/{id}', headers=headers)
    
    if response.status_code == 200:
        return jsonify(response.json())
    elif response.status_code == 404:
        return jsonify({"error": "not found"}), 404
    return jsonify({"error": "Failed to fetch product"}), response.status_code

@app.route('/api/health', methods=['GET'])
def health_check():
    uptime = datetime.now() - app.config['START_TIME']
    max_uptime_min = int(os.getenv('MAX_UPTIME_MIN', 60))
    
    if uptime.total_seconds() < max_uptime_min * 60:
        return jsonify({"health": "ok"})
    return jsonify({"health": "degraded"}), 500

if __name__ == '__main__':
    app.config['START_TIME'] = datetime.now()
    app.run(debug=True, host='0.0.0.0')