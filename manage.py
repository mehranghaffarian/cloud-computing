#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import sys
import asyncio
import pika

from mysite.utils import read_from_object_storage, call_shazam_api, call_spotify_search_api, \
    execute_database_query


async def listen_to_rabbitmq():
    logger.critical('calling consume')
    await asyncio.gather(consume())


async def consume():
    try:
        logger.critical('creating the pika client')
        connection = pika.BlockingConnection(pika.URLParameters(
            url='amqps://pbememzq:kza9uJTLxwR1stEpuig6LvOOYwhP6R3t@octopus.rmq3.cloudamqp.com/pbememzq'))
        channel = connection.channel()
        channel.queue_declare(queue='song_requests')

        def callback(ch, method, properties, body):
            request_id = body

            logger.critical(f'callback has gotten the request_id: {request_id}')
            # get the song from amazon s3
            read_object, message = read_from_object_storage(request_id)

            logger.critical('object has been read from the storage')
            # get the song name with shazam api
            song_name, message = call_shazam_api(read_object)

            logger.critical(f'song name has obtained with shazam, song name: {song_name}')
            # get the song spotify ID with the song name
            spotify_id, message = call_spotify_search_api(song_name)

            logger.critical(f'song spotify id: {spotify_id}')
            # update the song ID and status in the requests table
            message = execute_database_query("""UPDATE your_table_name SET status = %s, songID = %s WHERE ID = %s""",
                                             ("ready", spotify_id, request_id))

            logger.critical('song id and status updated in the database')
            # This function is not async, so just print here

        logger.critical('calling consume on channel')
        channel.basic_consume(queue='song_requests', on_message_callback=callback, auto_ack=True)

        channel.start_consuming()
    except Exception as e:
        pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    logger.critical('running listening to rabbitMQ')
    asyncio.run(listen_to_rabbitmq())


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    main()
