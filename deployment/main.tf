# Install our simple lambdas
# No runtime required, only boto3

resource "aws_iam_role" "lambda_role_all" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "AWSLambda_FullAccess" {
  role       = aws_iam_role.lambda_role_all.name
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
}

resource "aws_iam_role_policy_attachment" "AWSLambda_Ec2Read" {
  role       = aws_iam_role.lambda_role_all.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

data "archive_file" "resource_discovery_package" {
    type = "zip"
    source_file = "${path.module}/../list_vlab_resources.py"
    output_path = "resource_discovery.zip"
}

resource "aws_lambda_function" "resource_discovery_lambda" {
    function_name = "vlab_resource_discovery"
    filename      = "resource_discovery.zip"
    source_code_hash = data.archive_file.resource_discovery_package.output_base64sha256
    role          = aws_iam_role.lambda_role_all.arn
    runtime       = "python3.9"
    handler       = "list_vlab_resources.list_handler"
    timeout       = 10
}

resource "aws_lambda_function" "resource_discovery_lambda_detail" {
    function_name = "vlab_resource_discovery_detail"
    filename      = "resource_discovery.zip"
    source_code_hash = data.archive_file.resource_discovery_package.output_base64sha256
    role          = aws_iam_role.lambda_role_all.arn
    runtime       = "python3.9"
    handler       = "list_vlab_resources.detail_handler"
    timeout       = 10
}
