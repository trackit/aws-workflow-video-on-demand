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