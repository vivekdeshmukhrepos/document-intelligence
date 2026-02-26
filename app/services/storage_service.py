# Import boto3 to interact with AWS services like S3
import boto3 
# Import ClientError exception handler for AWS-specific errors
from botocore.exceptions import ClientError 
# Import Config to access AWS credentials and bucket name from environment variables
from config import Config 

# Define S3Storage class to encapsulate all S3 storage operations
class S3Storage:
    # Initialize S3Storage by creating a connection to AWS S3
    def __init__(self):
        # Create a boto3 S3 client with AWS credentials retrieved from Config
        # aws_access_key_id and aws_secret_access_key authenticate with AWS
        # This client is used to perform all S3 operations (upload, download, etc.)
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY
        )

        # Store the S3 bucket name from Config for use in upload/download operations
        # This bucket is where all files will be stored and retrieved from
        self.bucket = Config.AWS_BUCKET_NAME

    

    # Method to upload a file to S3 bucket
    def upload_file(self, file_obj, filename):
        # Wrap the upload logic in a try-except block to handle errors gracefully
        try: 
            # Use boto3's upload_fileobj to upload a file object directly to S3
            # file_obj is the file content (from request), filename is the destination name
            # self.bucket specifies which S3 bucket to upload to
            self.s3.upload_fileobj(file_obj, self.bucket, filename)
            # Return True to indicate successful upload
            return True
        # Catch AWS-specific errors that may occur during upload (permission denied, bucket not found, etc.)
        except ClientError as e:
            # Log the error details for debugging
            print(f"Error uploading file: {e}")
            # Return False to indicate the upload failed
            return False
        
    
    # Method to retrieve a file from S3 bucket
    def get_file(self, filename):
        # Wrap the retrieval logic in a try-except block to handle errors gracefully
        try:
            # Use boto3's get_object to retrieve a file from S3
            # Bucket parameter specifies which S3 bucket to retrieve from
            # Key parameter is the filename/path in the S3 bucket
            response = self.s3.get_object(Bucket=self.bucket, Key=filename)
            # Return the 'Body' field which contains the file content/data
            # This is a streaming object that can be read by the caller
            return response['Body']
        # Catch AWS-specific errors (file not found, permission denied, etc.)
        except ClientError as e:
            # Log the error details for debugging
            print(f"Error retrieving file: {e}")
            # Return None to indicate the retrieval failed
            return None

