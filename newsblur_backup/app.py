import os
import io
import requests
import boto3

ssm = boto3.client('ssm')
s3 = boto3.client('s3')

USERNAME = ssm.get_parameter(Name='/newsblur-backup/username', WithDecryption=True)
PASSWORD = ssm.get_parameter(Name='/newsblur-backup/password', WithDecryption=True)
BUCKET_NAME = os.environ.get('BUCKET_NAME')
loginParams = {"username": USERNAME["Parameter"]["Value"], "password": PASSWORD["Parameter"]["Value"]}


def login():
    session = requests.Session()
    response = session.post("https://www.newsblur.com/api/login", data=loginParams)
    if response.json()["authenticated"] is False and response.status_code == 200:
        raise Exception(response.json())
    return session


def backup_starred_stories(session):
    starred_stories = session.get("https://www.newsblur.com/reader/starred_stories")
    print("Starred stories downloaded in " + str(starred_stories.elapsed))
    #todo: put this in S3
    with io.BytesIO() as f:
        f.write(str(starred_stories.json()).encode('utf-8'))
        f.seek(0)
        s3.upload_fileobj(f, BUCKET_NAME, 'starred_stories.json')



def backup_opml(session):
    opml = session.get("https://www.newsblur.com/import/opml_export")
    print("OPML downloaded in " + str(opml.elapsed))
    with io.BytesIO() as f:
        f.write(str(opml.text).encode('utf-8'))
        f.seek(0)
        s3.upload_fileobj(f, BUCKET_NAME, 'opml.xml')



def lambda_handler(event, context):

    with login() as s:
        backup_starred_stories(s)
        backup_opml(s)
        s.close()
