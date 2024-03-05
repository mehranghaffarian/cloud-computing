from django.http import JsonResponse
import boto3
import uuid
import psycopg2
from botocore.config import Config


def send_song(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        song = request.FILES['song']


        # Initialize the S3 client
        s3_client = boto3.client('s3',
                                 aws_access_key_id="0l7RJElo0SbDoyaTFCuj",
                                 aws_secret_access_key="Zyr2T3rM71YvsbAOzHbBLvtQC7N6Po4xilmiDu1g",
                                 endpoint_url="https://m5j6.fra.idrivee2-40.com",
                                 config=Config(proxies={
                                    # 'http': 'http://s20.mydnets.top:8080',
                                    # 'https': 'https://s20.mydnets.top:8080'
                                     })
                                     )

        # Specify the S3 bucket name and file key (path) within the bucket
        bucket_name = 'songs'
        file_key = song.name
        message = "Unknown"

        # Upload the song file to the S3 bucket
        try:
            s3_client.upload_fileobj(song, bucket_name, file_key)
            message = "Song uploaded successfully to S3 bucket"
        except Exception as e:
            message = f"Error uploading song to S3 bucket, error: {e}"

        # recording request in the DB
        # try:
            # Connect to the PostgreSQL database
            # conn = psycopg2.connect(
            #     dbname="requests",
            #     user="root",
            #     password="e8l0D0YC8xhfY4wI1col4FMv",
            #     host="monte-rosa.liara.cloud",
            #     port="32270"
            # )

            # Create a cursor object to execute SQL statements
            # cur = conn.cursor()

        #     # Insert a record into the table
        #     insert_query = """INSERT INTO SongsRequests (ID, email, status, songID) VALUES (%s, %s, %s, %s)"""

        #     requestID = unique_id = uuid.uuid4()
        #     # Example data to insert into the table
        #     data = (requestID, email, 'pending', "Unknown")

        #     # Execute the SQL query to insert data into the table
        #     cur.execute(insert_query, data)

        #     # Commit the transaction to apply the changes
        #     conn.commit()

        #     # Close the cursor and connection
        #     cur.close()
        #     conn.close()

        #     message = f"request recorded in the database successfully, ID: {requestID}"
        # except Exception as e:
        #     message = f"failed to record request in the database, error: {e}"

        # adding the request ID to rabbitMQ
        # try:
        #     message = "request ID added to rabbitMQ"
        # except Exception as e:
        #     message = "failed to add ID to rabbitMQ"

        return JsonResponse({"message": message}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
