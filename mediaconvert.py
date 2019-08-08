import boto3
from boto3.dynamodb.conditions import Key
import json
import uuid
import os
import time
from misc import get_table, get_mediaconvert_role
from config import get_config

def convert_video(event, context):

    table = get_table()

    sourceS3Bucket = event['Records'][0]['s3']['bucket']['name']
    sourceS3Key = event['Records'][0]['s3']['object']['key']

    destinationS3 = 's3://' + get_config("videos", "outputBucket") + '/' + sourceS3Key + '/'

    mediaConvertRole = get_mediaconvert_role()
    region = get_config("deployment", "region")

    statusCode = 200
    body = {}

    try:

        response = table.get_item(
            Key={
                'id': sourceS3Key,
            }
        )
        item = response['Item']
        item['status'] = "Transcoding"

        # Use MediaConvert SDK UserMetadata to tag jobs with the assetID
        # Events from MediaConvert will have the assetID in UserMedata
        jobMetadata = {'assetID': sourceS3Key}

        # get the account-specific mediaconvert endpoint for this region
        mc_client = boto3.client('mediaconvert', region_name=region)
        endpoints = mc_client.describe_endpoints()

        # add the account-specific endpoint to the client session
        client = boto3.client('mediaconvert', region_name=region, endpoint_url=endpoints['Endpoints'][0]['Url'], verify=False)

        # Job settings are in the lambda zip file in the current working directory
        with open('job.json') as json_data:
            jobSettings = json.load(json_data)

        # Update the job settings with the source video from the S3 event and destination
        # paths for converted videos
        jobSettings['Inputs'][0]['FileInput'] = 's3://'+ sourceS3Bucket + '/' + sourceS3Key
        jobSettings['OutputGroups'][0]['OutputGroupSettings']['FileGroupSettings']['Destination'] = destinationS3
        jobSettings['OutputGroups'][1]['OutputGroupSettings']['HlsGroupSettings']['Destination'] = destinationS3 + 'hls1/master'
        jobSettings['OutputGroups'][2]['OutputGroupSettings']['FileGroupSettings']['Destination'] = destinationS3 + 'thumbnails/'

        print('jobSettings:')
        print(json.dumps(jobSettings))

        # Convert the video using AWS Elemental MediaConvert
        job = client.create_job(Role=mediaConvertRole, UserMetadata=jobMetadata, Settings=jobSettings)
        print (json.dumps(job, default=str))

        item['job_id'] = job['Job']['Id']
        item['last_update'] = int(time.time())
        result = table.put_item(Item=item)

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

def update_video_status(event, context):
    table = get_table()

    job_id = event['detail']['jobId']
    job_status = event['detail']['status']

    statusCode = 200
    body = {}

    try:

        response = table.scan(
            FilterExpression=Key('job_id').eq(job_id)
        )

        for item in response['Items']:
            if job_status == "COMPLETE":
                item['status'] = "Ready"
            elif job_status == "ERROR":
                item['status'] = "Error while transcoding"
            item['last_update'] = int(time.time())
        result = table.put_item(Item=item)

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
