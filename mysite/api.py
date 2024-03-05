from django.http import JsonResponse
import boto3
import uuid
import psycopg2
import pika


def send_song(request):
    if request.method == 'POST':
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
        file_key = song.name
        message = "Unknown"

        # Upload the song file to the S3 bucket
        try:
            # s3_client.upload_fileobj(song, bucket_name, file_key)
            message = "Song uploaded successfully to S3 bucket"
        except Exception as e:
            message = f"Error uploading song to S3 bucket, previous step: {message}, error: {e}"

        # recording request in the DB
        request_id = "not yet defined"
        try:
            # message = "trying to create conn"
            #
            # # Connect to the PostgreSQL database
            # conn = psycopg2.connect(
            #     dbname="postgres",
            #     user="root",
            #     password="e8l0D0YC8xhfY4wI1col4FMv",
            #     host="monte-rosa.liara.cloud",
            #     port="32270")
            # message = "conn created"
            #
            # # Create a cursor object to execute SQL statements
            # cur = conn.cursor()
            #
            # # Insert a record into the table
            # insert_query = """INSERT INTO songsrequests (ID, email, status, songID) VALUES (%s, %s, %s, %s)"""

            request_id = str(uuid.uuid4())
            # # Example data to insert into the table
            # data = (request_id, email, 'pending', "Unknown")
            #
            # # Execute the SQL query to insert data into the table
            # # cur.execute(insert_query, data)
            #
            # message = "query executed"
            #
            # # Commit the transaction to apply the changes
            # conn.commit()
            #
            # message = "query committed"
            #
            # # Close the cursor and connection
            # cur.close()
            # conn.close()
            #
            # message = f"request recorded in the database successfully, ID: {request_id}"
        except Exception as e:
            message = f"failed, previous step: {message}, request_id: {request_id}, error: {e}"

        # adding the request ID to rabbitMQ
        try:
            # Connect to RabbitMQ server
            message = "trying to create connection"
            connection = pika.BlockingConnection(pika.ConnectionParameters('amqps://pbememzq:kza9uJTLxwR1stEpuig6LvOOYwhP6R3t@octopus.rmq3.cloudamqp.com/pbememzq'))
            channel = connection.channel()

            message = "connection and channel set up"
            # Declare a queue named 'song_requests'
            channel.queue_declare(queue='song_requests')

            message = "queue declared"
            # Publish the message to the queue
            channel.basic_publish(exchange='', routing_key='song_requests', body=request_id.encode('utf-8'))

            # Close the connection
            connection.close()
            message = "request ID added to rabbitMQ"
        except Exception as e:
            message = f"failed to add ID to rabbitMQ, previous step: {message}"

        return JsonResponse({"message": message}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
