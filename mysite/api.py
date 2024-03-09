from django.http import JsonResponse
import boto3
import uuid
import pika

from mysite.mysite.utils import execute_database_query


def send_song(request):
    if request.method == 'POST':
        request_id = str(uuid.uuid4())

        email = request.POST.get('email')
        song = request.FILES['song']

        # Initialize the S3 client
        s3_client = boto3.client('s3',
                                 aws_access_key_id="0l7RJElo0SbDoyaTFCuj",
                                 aws_secret_access_key="Zyr2T3rM71YvsbAOzHbBLvtQC7N6Po4xilmiDu1g",
                                 endpoint_url="https://m5j6.fra.idrivee2-40.com",
                                 )

        # Specify the S3 bucket name and file key (path) within the bucket
        bucket_name = 'songs'
        message = "Unknown"

        # Upload the song file to the S3 bucket
        try:
            s3_client.upload_fileobj(song, bucket_name, request_id)
            message = "Song uploaded successfully to S3 bucket"
        except Exception as e:
            message = f"Error uploading song to S3 bucket, previous step: {message}, error: {e}"

        # recording request in the DB
        message = execute_database_query(
            """INSERT INTO songsrequests (ID, email, status, songID) VALUES (%s, %s, %s, %s)""",
            (request_id, email, 'pending', "Unknown"))

        # adding the request ID to rabbitMQ
        try:
            # Connect to RabbitMQ server
            message = "trying to create connection"
            connection = pika.BlockingConnection(pika.URLParameters(
                url='amqps://pbememzq:kza9uJTLxwR1stEpuig6LvOOYwhP6R3t@octopus.rmq3.cloudamqp.com/pbememzq'))
            message = "trying to get the channel"

            channel = connection.channel()

            message = "connection and channel set up"
            # Declare a queue named 'song_requests'
            channel.queue_declare(queue='song_requests')

            message = "queue declared"
            # Publish the message to the queue
            channel.basic_publish(exchange='', routing_key='song_requests', body=request_id.encode('utf-8'))

            # Close the connection
            connection.close()
            message = f"request ID added to rabbitMQ, request_id: {request_id}"
        except Exception as e:
            message = f"failed to add ID to rabbitMQ, previous step: {message}, error: {e}"

        return JsonResponse({"message": message}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
