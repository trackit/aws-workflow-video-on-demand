# API Documentation

API will be managed by API Gateway.
Each endpoint will be a dedicated Lambda function.

## Authentication

Cognito is used to secure API endpoints.
Two Cognito users pools are used:
- `vod-workflow-user-pool-users`: For every endpoints
- `vod-workflow-user-pool-admins`: For POST and DELETE requests

A token needs to be generated and added in requests headers (`Authorization: $token`)

Note: You will need to enable authentication in AWS Console: Cognito -> User Pool -> Your User Pool --> App Clients and click on `Show details` and click on `Enable username password auth for admin APIs for authentication (ALLOW_ADMIN_USER_PASSWORD_AUTH)` and Save app client changes.

You can generate a token using AWS CLI tool:

````sh
$> cat auth.json
{
   "UserPoolId": "$user_pool_id",
   "ClientId": "$client_id",
   "AuthFlow": "ADMIN_NO_SRP_AUTH",
   "AuthParameters": {
       "USERNAME": "$username",
       "PASSWORD": "$password"
   }
}
$> aws cognito-idp admin-initiate-auth --cli-input-json file://auth.json
````

Note: You will need to use `IdToken`, not `AccessToken` or `RefreshToken`.

## Endpoints

### GET /videos

Return list of available videos

Example: (`GET /videos`)
````json
[{
	"status": "Ready",
	"job_id": "1234567890123-vod123",
	"id": "f8b49d03354b410bcc20518787bfc64b",
	"name": "vod_workflow_introduction.mpg",
	"last_update": 1234567890
},{
	"status": "Transcoding",
	"job_id": "4567890123456-vod456",
	"id": "205b410bcc64bf8b49d018787bfc3354",
	"name": "vod_workflow_demo.mpg",
	"last_update": 1234567890
}]
````

### GET /videos/:id

Return details for requested video

Example: (`GET /videos/f8b49d03354b410bcc20518787bfc64b`)
````json
{
	"status": "Ready",
	"job_id": "1234567890123-vod123",
	"last_update": 1234567890,
	"content": {
		"mp4": "$CLOUDFRONT_PRESIGNED_URL",
		"hls": {
			"master_low.m3u8": "$CLOUDFRONT_PRESIGNED_URL",
			"master_high.m3u8": "$CLOUDFRONT_PRESIGNED_URL",
			"master_med.m3u8": "$CLOUDFRONT_PRESIGNED_URL"
		},
		"thumbnails": [
			"$CLOUDFRONT_PRESIGNED_URL",
			"$CLOUDFRONT_PRESIGNED_URL"
		]
	},
	"id": "f8b49d03354b410bcc20518787bfc64b",
	"name": "vod_workflow_introduction.mpg"
}
````

### POST /videos

Return a signed URL to upload a file into S3 bucket

Body:
````json
{
	"name": "$FILE_NAME",
	"data": "$DATA"
}
````

N.B. : Only `name` field is required, you can add other fields and they will be stored into DynamoDB.

Example: (`POST /videos` with previous body)
````json
{
	"upload_url": "$UPLOAD_URL"
}
````

You can now post your video on AWS Mediaconvert with the following request:

`curl -v --upload-file your_video.mp4 "$UPLOAD_URL"`

### POST /videos/:id

Update data for a specific video

Body:
````json
{
	"data": "$DATA",
	"tags": {
		"key": "value"
	}
}
````

N.B. :
- `id` and `name` fields cannot be changed.
- `status` field can be omitted, latest value will be stored if not provided.
- `last_update` field is handled by API and will be overridden if provided.
- If a field is previously set and not provided again, it will be deleted during the update.

Example: (`POST /videos/f8b49d03354b410bcc20518787bfc64b` with previous body)
````json
{
	"id": "f8b49d03354b410bcc20518787bfc64b",
	"name": "vod_workflow_introduction.mpg",
	"status": "Ready",
	"job_id": "1234567890123-vod123",
	"last_update": 1234567890,
	"data": "$DATA",
	"tags": {
		"key": "value"
	},
	"content": {
		"mp4": "$CLOUDFRONT_PRESIGNED_URL",
		"hls": {
			"master_low.m3u8": "$CLOUDFRONT_PRESIGNED_URL",
			"master_high.m3u8": "$CLOUDFRONT_PRESIGNED_URL",
			"master_med.m3u8": "$CLOUDFRONT_PRESIGNED_URL"
		},
		"thumbnails": [
			"$CLOUDFRONT_PRESIGNED_URL",
			"$CLOUDFRONT_PRESIGNED_URL"
		]
	}
}
````

### DELETE /videos/:id

Delete a specific video

Example: (`DELETE /videos/f8b49d03354b410bcc20518787bfc64b`)
````json
{
	"status": "Removed",
	"job_id": "1234567890123-vod123",
	"last_update": 1234567890,
	"id": "f8b49d03354b410bcc20518787bfc64b",
	"name": "vod_workflow_introduction.mpg"
}
````
