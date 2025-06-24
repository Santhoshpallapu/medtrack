import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AWS clients
cw_events = boto3.client('events')
lambda_client = boto3.client('lambda')

# Get AWS region
region = os.getenv('AWS_REGION', 'ap-south-1')

def create_lambda_role():
    try:
        iam = boto3.client('iam')
        
        # Create role
        role_name = 'MedTrackLambdaRole'
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        
        # Attach necessary policies
        policies = [
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/AmazonSNSFullAccess",
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
        ]
        
        for policy in policies:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy
            )
        
        return response['Role']['Arn']
    except Exception as e:
        print(f"Error creating Lambda role: {str(e)}")
        return None

def create_cloudwatch_rule():
    try:
        # Create CloudWatch Events rule
        response = cw_events.put_rule(
            Name='MedTrackReminderRule',
            ScheduleExpression='rate(1 minute)',
            State='ENABLED',
            Description='Triggers the medication reminder Lambda function every minute'
        )
        
        return response['RuleArn']
    except Exception as e:
        print(f"Error creating CloudWatch rule: {str(e)}")
        return None

def setup_lambda_trigger(lambda_arn, rule_arn):
    try:
        # Add permission for CloudWatch to invoke Lambda
        lambda_client.add_permission(
            FunctionName='MedTrackReminderFunction',
            StatementId='AllowCloudWatchToInvoke',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn
        )
        
        # Add target to CloudWatch rule
        cw_events.put_targets(
            Rule='MedTrackReminderRule',
            Targets=[
                {
                    'Id': 'MedTrackReminderTarget',
                    'Arn': lambda_arn
                }
            ]
        )
        
        print("Lambda trigger setup complete!")
    except Exception as e:
        print(f"Error setting up Lambda trigger: {str(e)}")

def main():
    print("\n=== Setting up Medication Reminders ===")
    
    # Create Lambda role
    role_arn = create_lambda_role()
    if not role_arn:
        print("Failed to create Lambda role. Exiting.")
        return
    
    # Create CloudWatch rule
    rule_arn = create_cloudwatch_rule()
    if not rule_arn:
        print("Failed to create CloudWatch rule. Exiting.")
        return
    
    # Get Lambda function ARN
    try:
        response = lambda_client.get_function(FunctionName='MedTrackReminderFunction')
        lambda_arn = response['Configuration']['FunctionArn']
        
        # Setup Lambda trigger
        setup_lambda_trigger(lambda_arn, rule_arn)
        
        print("\nReminder system setup complete!")
        print("Medication reminders will now be sent at the specified times.")
    except Exception as e:
        print(f"Error getting Lambda function: {str(e)}")

if __name__ == '__main__':
    main()
