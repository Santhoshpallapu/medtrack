# MedTrack AWS Setup Instructions

## Step 1: Create IAM User
1. Go to AWS Console: https://console.aws.amazon.com
2. Navigate to IAM (Identity & Access Management)
3. Click on "Users" in the left sidebar
4. Click "Add user"
5. Enter username: `medtrack-user`
6. Select "Programmatic access" and "AWS Management Console access"
7. Click "Next: Permissions"
8. Click "Attach existing policies directly"
9. Search and select these policies:
   - AmazonDynamoDBFullAccess
   - AmazonSNSFullAccess
   - AmazonEC2FullAccess
10. Click "Next: Tags" (optional)
11. Click "Next: Review"
12. Click "Create user"
13. Download the credentials file (important!)

## Step 2: Note Down Your Credentials
After creating the user, you'll see a page with your credentials:
- Access key ID
- Secret access key
- Region (use `ap-south-1` for Mumbai region)

## Step 3: Update .env File
Copy the credentials to your `.env` file:
```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-south-1
```

## Step 4: Run Setup Scripts
1. First, run the AWS credentials setup script:
```bash
python aws_credentials_setup.py
```
2. Then run the schema setup script:
```bash
python schema_setup.py
```
3. Finally, start the Flask application:
```bash
python app.py
```

## Step 5: Access the Application
Once everything is running, you can access the application at:
http://localhost:5000

## Important Notes
- Keep your credentials secure and never share them
- Download the credentials immediately after creating the user
- If you lose the credentials, you'll need to create a new access key
- The application will use these credentials to create and manage AWS resources
