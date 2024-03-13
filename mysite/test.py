import boto3
import requests

if __name__ == '__main__':
    object_key = '03a100d5-c85a-4be5-9d8d-059e2f265af7.mp3'

    s3_client = boto3.client('s3',
                             aws_access_key_id="0l7RJElo0SbDoyaTFCuj",
                             aws_secret_access_key="Zyr2T3rM71YvsbAOzHbBLvtQC7N6Po4xilmiDu1g",
                             endpoint_url="https://m5j6.fra.idrivee2-40.com", )

    # Specify the S3 bucket name and file key (path) within the bucket
    bucket_name = 'songs'

    message = "trying to download from the object storage"
    s3_client.download_file(bucket_name, object_key, object_key)

