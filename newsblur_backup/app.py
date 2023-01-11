import os
import io
import requests
import boto3

ssm = boto3.client('ssm')
s3 = boto3.client('s3')

USERNAME = ssm.get_parameter(Name='/newsblur-backup/username', WithDecryption=True)
PASSWORD = ssm.get_parameter(Name='/newsblur-backup/password', WithDecryption=True)
BUCKET_NAME = os.environ.get('BUCKET_NAME')

loginParams = {
    "username": USERNAME["Parameter"]["Value"],
    "password": PASSWORD["Parameter"]["Value"]
    }


def create_session():
    """
    Creates a request.Session and returns it if the newsblur API login is valid.
    """
    session = requests.Session()
    response = session.post("https://www.newsblur.com/api/login", data=loginParams)
    if response.json()["authenticated"] is False and response.status_code == 200:
        raise Exception(response.json())
    return session


def backup_starred_stories(session):
    """
    Backup starred stories from the configured newsblur account.
    """
    starred_stories = session.get("https://www.newsblur.com/reader/starred_stories")
    print("Starred stories downloaded in " + str(starred_stories.elapsed))
    with io.BytesIO() as file_object:
        file_object.write(str(starred_stories.json()).encode('utf-8'))
        file_object.seek(0)
        s3.upload_fileobj(file_object, BUCKET_NAME, 'starred_stories.json')



def backup_opml(session):
    """
    Backs up subscribed feeds from the configured newsblur account.
    """
    opml = session.get("https://www.newsblur.com/import/opml_export")
    print("OPML downloaded in " + str(opml.elapsed))
    with io.BytesIO() as file_object:
        file_object.write(str(opml.text).encode('utf-8'))
        file_object.seek(0)
        s3.upload_fileobj(file_object, BUCKET_NAME, 'opml.xml')



def lambda_handler(event, context):
    """
    Handles incoming lambda events.
    """
    with create_session() as session:
        backup_starred_stories(session)
        backup_opml(session)
        session.close()
