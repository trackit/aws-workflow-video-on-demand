# AWS Workflow VOD Terraform module

AWS Elemental MediaConvert is a file-based video transcoding service that allows you to easily create video-on-demand (VOD) content for broadcast and multiscreen delivery at scale without having to worry about the complexity of building and operating your own video processing infrastructure.
This terraform module is used to set an automated workflow in order to transcode videos with your configuration.

![Infrastructure schema](./.documentation/infrastructure.png)

## Terraform versions

Terraform 0.12 and newer.

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 0.12 |
| aws | >= 2.11 |

## Providers

AWS

## Prerequisites

 * You must retrieve your **AWS Elemental MediaConvert API endpoint** (account specific). For that use aws-cli and keep the given endpoint:
```sh
$ aws mediaconvert describe-endpoints

{
    "Endpoints": [
        {
            "Url": "https://abcd1234.mediaconvert.us-west-2.amazonaws.com"
        }
    ]
}
```

* You also must have an **input S3 bucket** and an **output S3 bucket** _**(those S3 buckets must be in the same AWS Region that region you'll set to terraform module)**_.

## Usage

Clone our repository where you plan to use this module.

Before using the module, change directory to **mediaconvert_lambda**.
```bash
$ cd mediaconvert_lambda && ls
job.json    mediaconvert.py
```

**job.json** is a MediaConvert Job configuration example, you may want to modify **job.json** file in order to change MediaConvert Job settings. Some values are populated from Lambda function, ( *"[Populated by Lambda function]"* values ).

#### Default outputs :
**Apple HLS :**
| Resolution | Bitrate (bits/s) |
|:------------:|:---------:|
| 1280x720 | 192000 |
| 1920x1080 | 192000 |

**MP4 :**
| Resolution | Bitrate (bits/s) |
|:------------:|:---------:|
| 1920x1080 | 192000 |


Once your MediaConvert Job configuration is done, zip mediaconvert_lambda's content :
```bash
mediaconvert_lambda$ zip -r ../mediaconvert_lambda.zip .
```

You're now ready to use this module.

## Usage Example

```hcl
module "workflow_vod" {
  source = "./aws-workflow-video-on-demand"

  region                = "us-west-2"
  input_bucket_name     = "my_input_bucket_name"
  output_bucket_name    = "my_output_bucket_name"
  lambda_zip_path       = "./aws-workflow-video-on-demand/mediaconvert_lambda.zip"
  project_base_name     = "my_workflow_vod_name"
  bucket_event_prefix   = "input/"
  bucket_event_suffix   = ".mov"
  mediaconvert_endpoint = "https://abcd1234.mediaconvert.us-west-2.amazonaws.com"
}
```

What does it do ?
* I upload a file _my_video_***.mov*** to the ***input/*** folder in ***my_input_bucket_name*** bucket.
* The video file match with **bucket_event_prefix** and **bucket_event_suffix**.
* The lambda function is triggered and start MediaConvert job.
* Output video(s) are generated in the ***my_output_bucket_name*** bucket.

### Alternative example using vars.tf
```hcl
# vars.tf
/*
// module configuration variables
//  - By changing default values and using module
*/

variable "region" {
    description = "AWS region"
    default = "us-west-2"
}

variable "input_bucket_name" {
    description = "Input bucket name which contains videos to be transcoded."
    default = "my_input_bucket_name"
    type = string
}

variable "output_bucket_name" {
    description = "Output bucket name which contains videos after transcoding."
    default = "my_output_bucket_name"
    type = string
}

variable "bucket_event_prefix" {
    description = "Element prefix to trigger lambda function."
    default = "input/"
}

variable "bucket_event_suffix" {
    description = "Element suffix to trigger lambda function."
    default = ".mov"
}

variable "project_base_name" {
    description = "Project name."
    default = "my_workflow_vod_name"
}

variable "lambda_zip_path" {
    description = "Path to lambda function and configuration zip."
    default = "./aws-workflow-video-on-demand/mediaconvert_lambda.zip"
}

variable "speke_server_url" {
    description = "For future versions."
    default = ""
}

variable "speke_system_id" {
    description = "For future versions."
    default = ""
}

variable "mediaconvert_endpoint" {
    description = "AWS Element MediaConvert API endpoint."
    default = "https://abcd1234.mediaconvert.us-west-2.amazonaws.com"
}
```

```hcl
# in file using module
module "workflow_vod" {
  source = "./aws-workflow-video-on-demand"
}
```
