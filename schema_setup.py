import boto3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Get table names from environment
USERS_TABLE = os.getenv('DYNAMODB_TABLE_USERS')
MEDS_TABLE = os.getenv('DYNAMODB_TABLE_MEDICATIONS')

# Create Users table
def create_users_table():
    try:
        dynamodb.create_table(
            TableName=USERS_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"Created table: {USERS_TABLE}")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table {USERS_TABLE} already exists")

# Create Medications table
def create_medications_table():
    try:
        dynamodb.create_table(
            TableName=MEDS_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'med_id',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'med_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"Created table: {MEDS_TABLE}")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table {MEDS_TABLE} already exists")

# Create SNS topic
def create_sns_topic():
    try:
        response = sns.create_topic(
            Name='MedTrackReminders'
        )
        topic_arn = response['TopicArn']
        print(f"Created SNS topic: {topic_arn}")
        return topic_arn
    except sns.exceptions.ResourceAlreadyExistsException:
        print("SNS topic already exists")
        topics = sns.list_topics()
        for topic in topics['Topics']:
            if topic['TopicArn'].endswith(':MedTrackReminders'):
                return topic['TopicArn']

if __name__ == '__main__':
    print("Setting up AWS resources...")
    create_users_table()
    create_medications_table()
    topic_arn = create_sns_topic()
    if topic_arn:
        print(f"SNS Topic ARN: {topic_arn}")
        print("\nAdd this Topic ARN to your .env file:")
        print(f"SNS_TOPIC_ARN={topic_arn}")
