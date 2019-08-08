import boto3
import json
import uuid
import time
from config import get_config
from misc import get_table, format_tags, DecimalEncoder, generate_s3_presigned_url, generate_cf_presigned_url

# GET /videos
def get_videos(event, context):
    table = get_table()

    try:
        response = table.scan()
        result = {
            "statusCode": 200,
            "body": json.dumps(response['Items'], indent=4, cls=DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    except Exception as ex:
        print(ex)
        result = {
            'statusCode': 501,
            'body': {"Exception": str(ex)},
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return result

# GET /video/{id}
def get_video(event, context):
    table = get_table()
    vid = event['pathParameters']['id']
    s3 = boto3.client('s3')

    try:
        response = table.get_item(
            Key={
                'id': vid,
            }
        )
        item = response['Item']

        if item['status'] == "Ready":
            content = {}
            content['mp4'] = generate_cf_presigned_url(vid + '/' + vid + '.mp4')
            content['thumbnails'] = []
            response = s3.list_objects(
                Bucket=get_config("videos", "outputBucket"),
                Prefix=vid + '/thumbnails'
            )
            for object in response['Contents']:
                content['thumbnails'].append(generate_cf_presigned_url(object['Key']))
            content['hls'] = {}
            response = s3.list_objects(
                Bucket=get_config("videos", "outputBucket"),
                Prefix=vid + '/hls1'
            )
            for object in response['Contents']:
                if object['Key'].endswith(".m3u8"):
                    filename = object['Key'].split('/')[-1]
                    if filename.startswith("master_"):
                        content['hls'][filename] = generate_cf_presigned_url(object['Key'])
            item['content'] = content

        result = {
            "statusCode": 200,
            "body": json.dumps(item, indent=4, cls=DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    except Exception as ex:
        print(ex)
        result = {
            'statusCode': 501,
            'body': {"Exception": str(ex)},
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return result

# POST /videos
def upload_video(event, context):
    table = get_table()
    s3 = boto3.client('s3')

    try:
        upload_key = uuid.uuid4().hex

        metadata = json.loads(event['body'])
        if not 'name' in metadata:
            raise Exception("Missing name value")
        metadata['id'] = upload_key
        metadata['status'] = "Uploading"
        metadata['last_update'] = int(time.time())

        res = table.put_item(Item=metadata)

        presigned_url = generate_s3_presigned_url('put_object',
                                                get_config("videos", "inputBucket"),
                                                upload_key)

        body = {"upload_url": presigned_url}
        return {
            "statusCode": 200,
            "body": json.dumps(body, indent=4),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    except Exception as ex:
        print(ex)
        return {
            "statusCode": 500,
            'body': json.dumps({"Exception": str(ex)}, indent=4),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

# POST /videos/{id}
def edit_video(event, context):
    table = get_table()
    vid = event['pathParameters']['id']
    s3 = boto3.client('s3')

    try:
        response = table.get_item(
            Key={
                'id': vid,
            }
        )

        old_metadata = response['Item']
        metadata = json.loads(event['body'])

        locked_keys = ['id', 'name']
        for key in locked_keys:
            metadata[key] = old_metadata[key]

        if not 'status' in metadata:
            metadata['status'] = old_metadata['status']

        metadata['last_update'] = int(time.time())

        tags = []
        if 'tags' in metadata:
            tags = format_tags(metadata['tags'])

        s3.put_object_tagging(
            Bucket=get_config("videos", "inputBucket"),
            Key=metadata['id'],
            Tagging={
                "TagSet": tags
            }
        )
        response = s3.list_objects(
            Bucket=get_config("videos", "outputBucket"),
            Prefix=metadata['id']
        )
        for object in response['Contents']:
            response = s3.put_object_tagging(
                Bucket=get_config("videos", "outputBucket"),
                Key=object['Key'],
                Tagging={
                    "TagSet": tags
                }
            )

        res = table.put_item(Item=metadata)

        result = {
            "statusCode": 200,
            "body": json.dumps(metadata, indent=4, cls=DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    except Exception as ex:
        print(ex)
        result = {
            'statusCode': 501,
            'body': json.dumps({"Exception": str(ex)}, indent=4),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return result

# DELETE /videos/{id}
def delete_video(event, context):
    table = get_table()
    s3 = boto3.client('s3')
    vid = event['pathParameters']['id']

    try:
        response = table.get_item(
            Key={
                'id': vid,
            }
        )

        metadata = response['Item']

        if metadata['status'] != "Uploading":
            response = s3.delete_object(
                Bucket=get_config("videos", "inputBucket"),
                Key=metadata['id']
            )
            response = s3.list_objects(
                Bucket=get_config("videos", "outputBucket"),
                Prefix=metadata['id']
            )
            for object in response['Contents']:
                response = s3.delete_object(
                    Bucket=get_config("videos", "outputBucket"),
                    Key=object['Key']
                )

        response = table.delete_item(
            Key={
                'id': vid,
            }
        )

        metadata['status'] = "Removed"

        result = {
            "statusCode": 200,
            "body": json.dumps(metadata, indent=4, cls=DecimalEncoder),
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    except Exception as ex:
        print(ex)
        result = {
            'statusCode': 501,
            'body': {"Exception": str(ex)},
            "headers": {
                "Access-Control-Allow-Origin": "*",
            }
        }

    return result
