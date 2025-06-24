import json
import boto3
from datetime import datetime, timedelta
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    sns = boto3.client('sns')
    
    # Get table names from environment
    MEDS_TABLE = os.getenv('DYNAMODB_TABLE_MEDICATIONS')
    SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
    
    # Get the current time
    current_time = datetime.utcnow()
    
    # Get medications that need to be reminded
    table = dynamodb.Table(MEDS_TABLE)
    
    # Scan all medications
    response = table.scan()
    medications = response.get('Items', [])
    
    for med in medications:
        # Parse the frequency string (HH:MM,HH:MM format)
        try:
            times = med.get('frequency', '').split(',')
            for time_str in times:
                if not time_str.strip():
                    continue
                
                # Parse the time
                reminder_hour, reminder_minute = map(int, time_str.split(':'))
                reminder_time = current_time.replace(hour=reminder_hour, minute=reminder_minute, second=0, microsecond=0)
                
                # Check if this reminder is due
                if current_time >= reminder_time and current_time < reminder_time + timedelta(minutes=1):
                    # Send SNS notification
                    message = f"Medication reminder: {med['name']} ({med['dosage']})"
                    sns.publish(
                        TopicArn=SNS_TOPIC_ARN,
                        Message=message,
                        Subject="Medication Reminder"
                    )
        except Exception as e:
            print(f"Error processing medication {med.get('med_id', 'unknown')}: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Reminders processed successfully')
    }
