import boto3
from boto3.dynamodb.conditions import Key
import json
import uuid
import os

import json

# Read environment variables

def convert_video(event, context):

    sourceS3Bucket = event['Records'][0]['s3']['bucket']['name']
    sourceS3Key = event['Records'][0]['s3']['object']['key']

    destinationPath = "/".join(sourceS3Key.split('/')[:-1])
    destinationS3 = 's3://' + os.environ["OUTPUT_BUCKET"] + '/$fn$/'

    mediaConvertRole = os.environ["MEDIACONVERT_ROLE_ARN"]
    mediaConvertEndpoint = os.environ["MEDIACONVERT_ENDPOINT"]
    region = os.environ["REGION"]

    statusCode = 200
    body = {}

    try:
        # Use MediaConvert SDK UserMetadata to tag jobs with the assetID
        # Events from MediaConvert will have the assetID in UserMedata
        jobMetadata = {'assetID': sourceS3Key}

        # add the account-specific endpoint to the client session
        client = boto3.client('mediaconvert', region_name=region, endpoint_url=mediaConvertEndpoint, verify=False)

        # Job settings are in the lambda zip file in the current working directory
        with open('job.json') as json_data:
            jobSettings = json.load(json_data)

        # Update the job settings with the source video from the S3 event and destination
        # paths for converted videos
        jobSettings['Inputs'][0]['FileInput'] = 's3://'+ sourceS3Bucket + '/' + sourceS3Key
        jobSettings['OutputGroups'][0]['OutputGroupSettings']['HlsGroupSettings']['Destination'] = destinationS3 + "/hls/"
        jobSettings['OutputGroups'][1]['OutputGroupSettings']['FileGroupSettings']['Destination'] = destinationS3 + "/mp4/"
        print('jobSettings:')
        print(json.dumps(jobSettings))

        # Convert the video using AWS Elemental MediaConvert
        job = client.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=jobSettings)
        print (json.dumps(job, default=str))

        body = {'success': True}

    except Exception as ex:
        print(ex)
        statusCode = 500
        body = {'error': str(ex)}
        raise

    finally:
        return {
            'statusCode': statusCode,
            'body': json.dumps(body),
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
        }
