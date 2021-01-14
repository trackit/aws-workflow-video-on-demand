data "aws_iam_policy_document" "lambda_job_trust" {
    statement {
        actions = ["sts:AssumeRole"]

        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
    }
}

data "aws_iam_policy_document" "mediaconvert_job_trust" {
    statement {
        actions = ["sts:AssumeRole"]

        principals {
        type        = "Service"
        identifiers = ["mediaconvert.amazonaws.com"]
        }
    }
}

resource "aws_iam_role" "lambda_job" {
  name               = "${local.lambda_job_name_base}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_job_trust.json
}

resource "aws_iam_role_policy" "lambda_job" {
    name = "${local.lambda_job_name_base}-policy"
    role = aws_iam_role.lambda_job.id

    policy = data.aws_iam_policy_document.lambda_job_policy.json
}

resource "aws_iam_role_policy_attachment" "basic_execution" {
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    role = aws_iam_role.lambda_job.name
}

resource "aws_iam_role" "mediaconvert_job" {
    name = "${local.mediaconvert_job_name_base}-role"
    assume_role_policy = data.aws_iam_policy_document.mediaconvert_job_trust.json
}

resource "aws_iam_role_policy" "mediaconvert_job" {
    name = "${local.mediaconvert_job_name_base}-policy"
    role = aws_iam_role.mediaconvert_job.id

    policy = data.aws_iam_policy_document.mediaconvert_job_policy.json
}

data "aws_iam_policy_document" "lambda_job_policy" {
    statement {
        effect = "Allow"
        actions = [
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "mediaconvert:*"
        ]
        resources = ["*"]
    }

    statement {
        effect = "Allow"
        actions = [
            "s3:PutObject",
            "s3:GetObject"
        ]
        resources = [
            "arn:aws:s3:::${var.input_bucket_name}/*",
            "arn:aws:s3:::${var.output_bucket_name}/*",
        ]
    }

    statement {
        effect = "Allow"
        actions = [
            "iam:PassRole"
        ]
        resources = [
            aws_iam_role.mediaconvert_job.arn
        ]
    }

    statement {
        effect = "Allow"
        actions = [
            "s3:GetBucketNotification"
        ]

        resources = [
            "arn:aws:s3:::${var.input_bucket_name}"
        ]
    }

    statement {
        effect = "Allow"
        actions = [
            "s3:PutBucketNotification"
        ]

        resources = [
            "arn:aws:s3:::${var.output_bucket_name}"
        ]
    }
}

data "aws_iam_policy_document" "mediaconvert_job_policy" {
    statement {
        effect = "Allow"
        actions = [
            "mediaconvert:*"
        ]
        resources = ["*"]
    }

    statement {
        effect = "Allow"
        actions = [
            "s3:GetObject"
        ]
        resources = [
            "arn:aws:s3:::${var.input_bucket_name}",
            "arn:aws:s3:::${var.input_bucket_name}/*"
        ]
    }

    statement {
        effect = "Allow"
        actions = [
            "s3:PutObject"
        ]
        resources = [
            "arn:aws:s3:::${var.output_bucket_name}",
            "arn:aws:s3:::${var.output_bucket_name}/*"
        ]
    }
}