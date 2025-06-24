import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AWS clients
elasticbeanstalk = boto3.client('elasticbeanstalk')
r53 = boto3.client('route53')

# Get AWS region
region = os.getenv('AWS_REGION', 'ap-south-1')

# Create Elastic Beanstalk environment
def create_eb_environment():
    try:
        # Create application if it doesn't exist
        app_name = 'MedTrackApp'
        try:
            elasticbeanstalk.create_application(
                ApplicationName=app_name,
                Description='MedTrack Medication Management System'
            )
        except elasticbeanstalk.exceptions.AlreadyExistsException:
            pass
        
        # Create environment
        env_name = 'MedTrackEnv'
        response = elasticbeanstalk.create_environment(
            ApplicationName=app_name,
            EnvironmentName=env_name,
            SolutionStackName='64bit Amazon Linux 2 v3.7.12 running Python 3.11',
            OptionSettings=[
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'AWS_ACCESS_KEY_ID',
                    'Value': os.getenv('AWS_ACCESS_KEY_ID')
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'AWS_SECRET_ACCESS_KEY',
                    'Value': os.getenv('AWS_SECRET_ACCESS_KEY')
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'AWS_REGION',
                    'Value': region
                }
            ]
        )
        
        print(f"Created Elastic Beanstalk environment: {env_name}")
        return env_name
    except Exception as e:
        print(f"Error creating EB environment: {str(e)}")
        return None

# Configure custom domain
def configure_custom_domain(env_name, domain_name):
    try:
        # Get environment URL
        response = elasticbeanstalk.describe_environments(
            EnvironmentNames=[env_name]
        )
        eb_url = response['Environments'][0]['CNAME']
        
        # Create Route53 record
        response = r53.change_resource_record_sets(
            HostedZoneId='Z1111111111111111111',  # Replace with your hosted zone ID
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': domain_name,
                            'Type': 'CNAME',
                            'TTL': 300,
                            'ResourceRecords': [
                                {
                                    'Value': eb_url
                                }
                            ]
                        }
                    }
                ]
            }
        )
        
        print(f"Configured custom domain: {domain_name}")
        return True
    except Exception as e:
        print(f"Error configuring custom domain: {str(e)}")
        return False

# Deploy application to Elastic Beanstalk
def deploy_to_eb():
    try:
        # Create zip file of application
        import zipfile
        import os
        
        with zipfile.ZipFile('application.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk('.'):  # Include all files in current directory
                for file in files:
                    if file != 'application.zip':  # Skip the zip file itself
                        zipf.write(os.path.join(root, file))
        
        # Create application version
        version_label = f'version-{int(time.time())}'
        with open('application.zip', 'rb') as f:
            response = elasticbeanstalk.create_application_version(
                ApplicationName='MedTrackApp',
                VersionLabel=version_label,
                SourceBundle={
                    'S3Bucket': 'medtrack-deployments',  # Replace with your S3 bucket
                    'S3Key': f'v1/{version_label}.zip'
                }
            )
        
        # Update environment with new version
        elasticbeanstalk.update_environment(
            EnvironmentName='MedTrackEnv',
            VersionLabel=version_label
        )
        
        print("Deployment complete!")
        return True
    except Exception as e:
        print(f"Error deploying application: {str(e)}")
        return False

if __name__ == '__main__':
    print("\n=== AWS Deployment ===")
    
    # Create EB environment
    env_name = create_eb_environment()
    if not env_name:
        print("Failed to create EB environment. Exiting.")
        exit(1)
    
    # Configure custom domain
    domain_name = 'medtrack.example.com'  # Replace with your domain
    if not configure_custom_domain(env_name, domain_name):
        print("Failed to configure custom domain.")
    
    # Deploy application
    if deploy_to_eb():
        print(f"\nApplication deployed successfully!")
        print(f"Access the application at: http://{domain_name}")
    else:
        print("\nDeployment failed. Please check the error messages above.")
