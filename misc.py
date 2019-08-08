import boto3
import json
import decimal
from config import get_config

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def get_table():
    table_name = get_config("videos", "dynamodbTable")
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(table_name)

def validate_tags(tags):
    if not type(tags) is dict:
        raise Exception("Tags must be a dictionary")
    for key in tags:
        if not type(tags[key]) in [str, unicode]:
            raise Exception("Value of " + key + " should be a string")
    return True

def format_tags(tags):
    if validate_tags(tags):
        formatted = []
        for key in tags:
            formatted.append({'Key': key, 'Value': tags[key]})
        return formatted
    return []

def get_mediaconvert_role():
    try:
        client = boto3.client('iam')
        roleName = get_config("videos", "roles", "mediaConvertRole")
        roles = client.list_roles()
        for role in roles['Roles']:
            if roleName in role['Arn']:
                return role['Arn']
        return None
    except Exception as ex:
        print(ex)
        return None

def generate_s3_presigned_url(method, bucket, key):
    s3 = boto3.client('s3')
    print(key)
    return s3.generate_presigned_url(
            ClientMethod=method,
            Params={
                'Bucket': bucket,
                'Key': key
            }
        )

def generate_cf_presigned_url(file):
    lambdas = boto3.client('lambda')
    functions = lambdas.list_functions()
    cfFunction = None
    for func in functions['Functions']:
        if "generate_cloudfront_presigned_urls" in func['FunctionName']:
            cfFunction = func['FunctionName']
    if cfFunction:
        payload = {"file": file}
        response = lambdas.invoke(FunctionName=cfFunction, InvocationType='RequestResponse', Payload=json.dumps(payload))
        payload = response['Payload'].read()
        payloadParsed = json.loads(payload)
        body = json.loads(payloadParsed['body'])
        return body['signedUrl']
    return None
