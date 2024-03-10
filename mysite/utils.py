import boto3
import psycopg2
import requests


def execute_database_query(query, data):
    message = None
    try:
        message = "trying to create conn"
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="postgres",
            user="root",
            password="e8l0D0YC8xhfY4wI1col4FMv",
            host="monte-rosa.liara.cloud",
            port="32270")
        message = "conn created"

        # Create a cursor object to execute SQL statements
        cur = conn.cursor()
        message = "cursor attained"

        # Execute the SQL query to insert data into the table
        cur.execute(query, data)

        message = "query executed"

        # Commit the transaction to apply the changes
        conn.commit()

        message = "query committed"

        # Close the cursor and connection
        cur.close()
        conn.close()

        message = f"request recorded in the database successfully"
    except Exception as e:
        message = f"failed, previous step: {message}, error: {e}"

    return message


def read_from_object_storage(object_key):
    read_object = None
    # Initialize the S3 client
    message = "getting the boto3 client"
    s3_client = boto3.client('s3',
                             aws_access_key_id="0l7RJElo0SbDoyaTFCuj",
                             aws_secret_access_key="Zyr2T3rM71YvsbAOzHbBLvtQC7N6Po4xilmiDu1g",
                             endpoint_url="https://m5j6.fra.idrivee2-40.com",
                             )

    # Specify the S3 bucket name and file key (path) within the bucket
    bucket_name = 'songs'

    # Upload the song file to the S3 bucket
    try:
        message = "trying to read from the object storage"
        read_object = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        message = f"trying to read the response body, response: {read_object}"
        read_object = read_object['Body'].read()

        message = "Song received successfully from S3 bucket"
    except Exception as e:
        message = f"Error receiving song from S3 bucket, previous step: {message}, error: {e}"

    return read_object, message


def call_shazam_api(song_file):
    message = "setting headers"
    headers = {
        'x-rapidapi-key': "7396f26c74mshc3ce21c7685d8b5p147355jsn002e8b49aab1",
        'x-rapidapi-host': "shazam-api-free.p.rapidapi.com"
    }
    files = {'upload_file': song_file}

    try:
        message = 'trying to send post request'
        response = requests.post("https://shazam-api-free.p.rapidapi.com/shazam/recognize/",
                                 headers=headers, files=files)
        data = response.json()
        message = f'accessing response attributes, response data: {data}'
        song_name = data['track']['title']
        return song_name, message
    except Exception as e:
        message = f"Error getting song, previous step: {message}, error: {e}"
        return None, message


def call_spotify_search_api(song_name):
    spotify_id = None
    message = "setting headers"
    headers = {
        'x-rapidapi-key': "7396f26c74mshc3ce21c7685d8b5p147355jsn002e8b49aab1",
        'x-rapidapi-host': "spotify23.p.rapidapi.com"
    }
    files = {'q': song_name}

    try:
        message = 'trying to send get request'
        response = requests.get("https://spotify23.p.rapidapi.com/search/", headers=headers, files=files)
        data = response.json()
        message = f'accessing response attributes, respose: {response}'
        spotify_id = data['tracks']['items'][0]['data']['id']
        return spotify_id, message
    except Exception as e:
        message = f"Error getting song, previous step: {message}, error: {e}"
        return spotify_id, message
