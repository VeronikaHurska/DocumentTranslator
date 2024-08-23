from typing import Union
import boto3
import uuid
import os
from pathlib import Path
from botocore.exceptions import ClientError
from api.settings import settings
from api.logger import logger

def create_local_folder(local_folder_path: Union[str, Path]) -> Path:
    local_storage_path = Path(local_folder_path)
    local_storage_path.mkdir(parents=True, exist_ok=True)
    return local_storage_path

def remove_local_folder(local_folder_path: Union[str, Path]) -> None:
    local_storage_path = Path(local_folder_path)
    if local_storage_path.exists():
        local_storage_path.rmdir()

class ManagerS3():
    def __init__(self, bucket_name: str, user_id: str = None):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource("s3")
        self.user_id = user_id  # Correct assignment of user_id

    def create_folder(self, folder_path: str) -> bool:
        try:
            project_folder_path = f"{self.user_id}/{folder_path}/"
            objects = list(self.s3.Bucket(self.bucket_name).objects.filter(Prefix=project_folder_path))
            if objects:
                logger.warning(f"Folder '{project_folder_path}' already exists in S3.")
                return True
            self.s3.Object(self.bucket_name, project_folder_path).put(Body="")
            logger.info(f"Folder created successfully in S3: {project_folder_path}")
            return True
        except Exception as e:
            logger.exception(f"An error occurred while creating folders in S3: {e}")
            return False
        
    def download_file_from_s3(self, file_name: str, file_folder: str) -> Path:
        s3_client = boto3.client("s3")
        local_dir_path = settings.get_project_local_storage_path(self.user_id) / file_folder
        local_file_path = local_dir_path / file_name

        try:
            create_local_folder(local_dir_path)  # Ensure the local directory exists, including the specific subdirectory
            s3_client.download_file(self.bucket_name, f"{self.user_id}/{file_folder}/{file_name}", str(local_file_path))
            logger.info(f"Downloaded {file_name} from {self.bucket_name}/{self.user_id}/{file_folder}/ to {local_file_path}")
            return local_file_path
        except ClientError as e:
            logger.error(f"Error downloading {file_name} from S3: {e}")
            raise e
        
    def upload_file(self, file_data, file_name):
        """
        Uploads a file to S3 in a user-specific folder and returns the S3 file URL and S3 key.
        """
        # Create a unique file name to avoid collisions
        unique_file_name = f"{uuid.uuid4()}_{file_name}"
        
        # Define the S3 key with the user ID folder
        s3_key = f"{self.user_id}/{unique_file_name}"
        
        # Upload the file to S3
        self.s3.Bucket(self.bucket_name).put_object(Key=s3_key, Body=file_data)
        
        # Return the full S3 URL for the file and the S3 key
        file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        return file_url, s3_key

    
    def get_file_size(self, file_data):
        """
        Returns the size of the file in bytes.
        """
        file_data.seek(0, os.SEEK_END)
        file_size = file_data.tell()
        file_data.seek(0)  # Reset file pointer to the beginning for future reads
        return file_size
