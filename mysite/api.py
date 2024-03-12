import requests
from django.http import JsonResponse
import boto3
import uuid
import pika
import logging

from mysite.utils import execute_database_query, read_from_object_storage, call_shazam_api, call_spotify_search_api, \
    call_spotify_recommendation_api


def send_recommended_songs_email(user_email):
    logger = logging.getLogger(__name__)

    # getting songID with ready status
    response, message = execute_database_query("""SELECT songID FROM songsrequests WHERE status = 'ready'""")
    # spotify_id = response['songID']
    spotify_id = '0c6xIDDpzE81m2q797ordA'
    # request_id = response['ID']
    request_id = 'test_id'

    logger.critical(f'ready records response received, message: {message}, response: {response}')
    # getting recommended songs
    response, message = call_spotify_recommendation_api(spotify_id)

    logger.critical(f'recommended songs, message: {message}, response: {response}')
    # sending user email
    response = requests.post(
            "https://app.mailgun.com/app/sending/domains/sandboxa24d58344eb74bd9b73f39aedc34c3ff.mailgun.org",
            auth=("api", "ab5b6638da085196bca42114b98dcbd8-b02bcf9f-0c9fd7c4"),
            data={"from": "Excited User <mailgun@sandboxa24d58344eb74bd9b73f39aedc34c3ff.mailgun.org>",
                  "to": [user_email],
                  "subject": "recommended songs",
                  "text": "Testing some Mailgun awesomeness!"})

    logger.critical(f'email send, response: {response}')
    # changing status to done
    _, message = execute_database_query("""UPDATE songsrequests SET status = %s WHERE ID = %s""",
                                        ("done", request_id))

    logger.critical(f'song id and status updated in the database, message: {message}')


def consume_rabbitmq(email):
    logger = logging.getLogger(__name__)
    try:
        connection = pika.BlockingConnection(pika.URLParameters(
            url='amqps://pbememzq:kza9uJTLxwR1stEpuig6LvOOYwhP6R3t@octopus.rmq3.cloudamqp.com/pbememzq'))
        channel = connection.channel()
        channel.queue_declare(queue='song_requests')

        def callback(ch, method, properties, body):
            request_id = body.decode('utf-8')

            logger.critical(f'callback parameters, body: {request_id}')
            # get the song from amazon s3
            read_object, message = read_from_object_storage(request_id)

            logger.critical(f'object has been read from the storage, message: {message}')

            if read_object is None:
                return
            # get the song name with shazam api
            song_name, message = call_shazam_api(read_object)

            logger.critical(f'song name has obtained with shazam, message: {message}, song name: {song_name}')

            if song_name is None:
                song_name = "Darde Moshtarak 1 "
                # return
            # get the song spotify ID with the song name
            spotify_id, message = call_spotify_search_api(song_name)

            logger.critical(f'song spotify id: {spotify_id}, message: {message}')
            if spotify_id is None:
                return
            # update the song ID and status in the requests table
            _, message = execute_database_query("""UPDATE songsrequests SET status = %s, songID = %s WHERE ID = %s""",
                                                ("ready", spotify_id, request_id))

            logger.critical(f'song id and status updated in the database, message: {message}')
            # This function is not async, so just print here

        logger.critical('calling consume on channel')
        channel.basic_consume(queue='song_requests', on_message_callback=callback, auto_ack=True)

        channel.start_consuming()
        send_recommended_songs_email(email)
    except Exception as e:
        logger.critical(f'consuming rabbitMQ faced error, error: {e}')


def send_song(request):
    logger = logging.getLogger(__name__)
    logger.critical('processing the send_song api')

    if request.method == 'POST':
        request_id = str(uuid.uuid4())

        email = request.POST.get('email')
        song = request.FILES['song']

        logger.critical(f'email and song received, song: {song}')

        # Initialize the S3 client
        s3_client = boto3.client('s3',
                                 aws_access_key_id="0l7RJElo0SbDoyaTFCuj",
                                 aws_secret_access_key="Zyr2T3rM71YvsbAOzHbBLvtQC7N6Po4xilmiDu1g",
                                 endpoint_url="https://m5j6.fra.idrivee2-40.com",
                                 )

        # Specify the S3 bucket name and file key (path) within the bucket
        bucket_name = 'songs'

        # Upload the song file to the S3 bucket
        try:
            s3_client.upload_fileobj(song, bucket_name, request_id)
            logger.critical("Song uploaded successfully to S3 bucket")
        except Exception as e:
            logger.critical(f"Error uploading song to S3 bucket, error: {e}")

        # recording request in the DB
        _, message = execute_database_query(
            """INSERT INTO songsrequests (ID, email, status, songID) VALUES (%s, %s, %s, %s)""",
            (request_id, email, 'pending', "Unknown"))
        logger.critical(message)

        # adding the request ID to rabbitMQ
        try:
            # Connect to RabbitMQ server
            connection = pika.BlockingConnection(pika.URLParameters(
                url='amqps://pbememzq:kza9uJTLxwR1stEpuig6LvOOYwhP6R3t@octopus.rmq3.cloudamqp.com/pbememzq'))
            channel = connection.channel()

            # Declare a queue named 'song_requests'
            channel.queue_declare(queue='song_requests')

            # Publish the message to the queue
            channel.basic_publish(exchange='', routing_key='song_requests', body=request_id.encode('utf-8'))

            # Close the connection
            connection.close()
            logger.critical(f"request ID added to rabbitMQ, request_id: {request_id}")
        except Exception as e:
            logger.critical(f"failed to add ID to rabbitMQ, error: {e}")

        consume_rabbitmq(email)
        return JsonResponse({"message": "every thing is ok"}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
