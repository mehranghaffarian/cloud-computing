import psycopg2
import requests
import boto3


def execute_database_query(query, data=None):
    message = None
    response = None
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
        if data is None:
            response = cur.execute(query)
        else:
            response = cur.execute(query, data)

        # Commit the transaction to apply the changes
        conn.commit()
        message = "query committed"

        response = cur.fetchall()
        message = f"all rows fetched, response: {response}"

        # Close the cursor and connection
        cur.close()
        conn.close()

        message = f"query executed successfully"
    except Exception as e:
        message = f"query failed, previous step: {message}, error: {e}"

    return response, message


def read_from_object_storage(object_key):
    read_object = None
    # Initialize the S3 client
    message = "getting the boto3 client"
    s3_client = boto3.client('s3',
                             aws_access_key_id="0l7RJElo0SbDoyaTFCuj",
                             aws_secret_access_key="Zyr2T3rM71YvsbAOzHbBLvtQC7N6Po4xilmiDu1g",
                             endpoint_url="https://m5j6.fra.idrivee2-40.com",)

    # Specify the S3 bucket name and file key (path) within the bucket
    bucket_name = 'songs'

    try:
        message = "trying to download from the object storage"
        read_object = s3_client.download_file(bucket_name, object_key+'.mp3', object_key+'.mp3')

        message = f"Song received successfully from S3 bucket, "
    except Exception as e:
        message = f"Error receiving song from S3 bucket, previous step: {message}, error: {e}"

    return read_object, message


def call_shazam_api(song_file_path):
    message = "setting headers"
    headers = {
        'x-rapidapi-key': "7396f26c74mshc3ce21c7685d8b5p147355jsn002e8b49aab1",
        'x-rapidapi-host': "shazam-api-free.p.rapidapi.com"
    }
    try:
        files = {'upload_file': open(song_file_path, 'rb')}

        message = 'trying to send post request in shazam'
        response = requests.post("https://shazam-api-free.p.rapidapi.com/shazam/recognize/",
                                 headers=headers, files=files)
        data = response.json()
        message = f'accessing shazam response attributes, files: {files}, response jason: {data}'
        song_name = data['track']['title']
        return song_name, message
    except Exception as e:
        message = f"Error getting song, previous step: {message}, error: {e}"
        return None, message


def call_spotify_search_api(song_name):
    spotify_id = None
    message = "setting headers"
    headers = {
        'q': song_name,
        'x-rapidapi-key': "7396f26c74mshc3ce21c7685d8b5p147355jsn002e8b49aab1",
        'x-rapidapi-host': "spotify23.p.rapidapi.com"
    }
    params = {'q': song_name}

    try:
        message = 'trying to send get request'
        response = requests.get("https://spotify23.p.rapidapi.com/search/", headers=headers, params=params)
        data = response.json()
        message = f'accessing spotify search response attributes'
        spotify_id = data['tracks']['items'][0]['data']['id']
        return spotify_id, message
    except Exception as e:
        message = f"Error getting song, previous step: {message}, error: {e}"
        return spotify_id, message


def call_spotify_recommendation_api(song_id):
    message = "setting headers"
    headers = {
        'x-rapidapi-key': "7396f26c74mshc3ce21c7685d8b5p147355jsn002e8b49aab1",
        'x-rapidapi-host': "spotify23.p.rapidapi.com"
    }
    params = {'seed_tracks': song_id}

    try:
        message = 'trying to send get request'
        response = requests.get("https://spotify23.p.rapidapi.com/recommendations/", headers=headers, params=params)
        data = response.json()['tracks']

        recommended_songs = []
        for track in data:
            recommended_songs.append((track['name'], track['id']))

        message = f'accessing spotify recommendation response attributes'

        return recommended_songs, message
    except Exception as e:
        message = f"Error getting song, previous step: {message}, error: {e}"
        return None, message
