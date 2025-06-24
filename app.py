from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import boto3
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Get table names from environment
USERS_TABLE = os.getenv('DYNAMODB_TABLE_USERS')
MEDS_TABLE = os.getenv('DYNAMODB_TABLE_MEDICATIONS')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')

# Get DynamoDB tables
users_table = dynamodb.Table(USERS_TABLE)
meds_table = dynamodb.Table(MEDS_TABLE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        users_table.put_item(
            Item={
                'username': data['username'],
                'password': data['password'],
                'email': data.get('email', ''),
                'phone': data.get('phone', '')
            },
            ConditionExpression='attribute_not_exists(username)'
        )
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    try:
        response = users_table.get_item(
            Key={'username': data['username']}
        )
        user = response.get('Item')
        if user and user.get('password') == data['password']:
            return jsonify({'token': user['username']}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/medications', methods=['POST'])
def add_medication():
    data = request.json
    try:
        # Generate unique medication ID
        med_id = str(uuid.uuid4())
        
        # Store medication in DynamoDB
        meds_table.put_item(
            Item={
                'username': data['username'],
                'med_id': med_id,
                'name': data['name'],
                'dosage': data['dosage'],
                'frequency': data['frequency'],
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        # Send SNS notification
        message = f"Medication reminder: {data['name']} ({data['dosage']})"
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Medication Reminder"
        )
        
        return jsonify({'med_id': med_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/medications', methods=['GET'])
def get_medications():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    try:
        response = meds_table.query(
            KeyConditionExpression='username = :username',
            ExpressionAttributeValues={
                ':username': username
            }
        )
        return jsonify(response['Items']), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
