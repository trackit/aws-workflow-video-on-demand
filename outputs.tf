output "lambda_role_name" {
    value = aws_iam_role.lambda_job.name
}

output "mediaconvert_role_name" {
    value = aws_iam_role.mediaconvert_job.name
}