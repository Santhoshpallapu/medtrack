import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get AWS credentials from environment
access_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_REGION')

if not all([access_key, secret_key, region]):
    print("Error: Missing AWS credentials in environment variables")
    print("Please set the following environment variables:")
    print("AWS_ACCESS_KEY_ID")
    print("AWS_SECRET_ACCESS_KEY")
    print("AWS_REGION")
    exit(1)

# Configure AWS credentials
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region
)

# Test the connection
def test_aws_connection():
    try:
        # List S3 buckets (safe test that requires minimal permissions)
        s3 = session.client('s3')
        response = s3.list_buckets()
        print("AWS connection successful!")
        print("Available S3 buckets:")
        for bucket in response['Buckets']:
            print(f"- {bucket['Name']}")
        return True
    except Exception as e:
        print(f"Error testing AWS connection: {str(e)}")
        return False

# Create IAM role for EC2 instance
def create_iam_role():
    try:
        iam = session.client('iam')
        
        # Create role
        role_name = 'MedTrackEC2Role'
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }
        
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        print(f"Created IAM role: {role_name}")
        
        # Attach necessary policies
        policies = [
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/AmazonSNSFullAccess",
            "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
        ]
        
        for policy in policies:
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy
            )
            print(f"Attached policy: {policy}")
        
        return role_name
    except Exception as e:
        print(f"Error creating IAM role: {str(e)}")
        return None

if __name__ == '__main__':
    print("\n=== AWS Credentials Setup ===")
    print("Testing AWS connection...")
    if test_aws_connection():
        print("\nCreating IAM role for EC2 instance...")
        role_name = create_iam_role()
        if role_name:
            print("\nSetup complete!")
            print(f"IAM Role created: {role_name}")
            print("You can now proceed to launch the EC2 instance.")
        else:
            print("Failed to create IAM role.")
    else:
        print("Failed to connect to AWS.")
        print("Please verify your AWS credentials and try again.")
