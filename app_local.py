from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory storage for local testing
USERS = {
    'Santhosh': {
        'password': 'password',
        'email': '',
        'phone': ''
    }
}
MEDICATIONS = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    
    if username in USERS:
        return jsonify({'error': 'Username already exists'}), 400
    
    USERS[username] = {
        'password': data['password'],
        'email': data.get('email', ''),
        'phone': data.get('phone', '')
    }
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    
    user = USERS.get(username)
    if user and user['password'] == data['password']:
        return jsonify({'token': username}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/medications', methods=['POST'])
def add_medication():
    data = request.json
    username = data['username']
    
    if username not in USERS:
        return jsonify({'error': 'User not found'}), 401
    
    med_id = str(uuid.uuid4())
    
    if username not in MEDICATIONS:
        MEDICATIONS[username] = {}
    
    MEDICATIONS[username][med_id] = {
        'name': data['name'],
        'dosage': data['dosage'],
        'frequency': data['frequency'],
        'created_at': datetime.utcnow().isoformat()
    }
    
    return jsonify({'med_id': med_id}), 201

@app.route('/api/medications', methods=['GET'])
def get_medications():
    username = request.args.get('username')
    if not username or username not in MEDICATIONS:
        return jsonify([]), 200
    
    return jsonify(list(MEDICATIONS[username].values())), 200

@app.route('/users')
def list_users():
    return render_template('users.html', users=USERS)

@app.route('/api/users')
def get_users():
    return jsonify(list(USERS.keys()))

if __name__ == '__main__':
    print("\n=== Running in Local Mode ===")
    print("No AWS credentials needed")
    print("Application available at: http://localhost:5000")
    print("Pre-configured user:")
    print("Username: Santhosh")
    print("Password: password")
    app.run(host='0.0.0.0', port=5000, debug=True)
