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

resource "aws_iam_role_policy_attachment" "AWSLambda_Read" {
  role       = aws_iam_role.lambda_role_all.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

data "archive_file" "resource_discovery_package" {
  type = "zip"
  source_file = "${path.module}/../list_vlab_resources.py"
  output_path = "resource_discovery.zip"
}

resource "aws_lambda_function" "resource_discovery_lambdas" {
  for_each = toset([
    "list",
    "detail",
  ])
  function_name = "vlab_resource_discovery_${each.key}"
  filename      = "resource_discovery.zip"
  source_code_hash = data.archive_file.resource_discovery_package.output_base64sha256
  role          = aws_iam_role.lambda_role_all.arn
  runtime       = "python3.9"
  handler       = "list_vlab_resources.${each.key}_handler"
  timeout       = 10
}

# HTTP API
resource "aws_apigatewayv2_api" "resource_discovery_api" {
  name          = "api-resource_discovery"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "resource_discover_api_v1" {
  api_id      = aws_apigatewayv2_api.resource_discovery_api.id
  name        = "v1"
  auto_deploy = true
  default_route_settings {
    throttling_burst_limit = 50
    throttling_rate_limit  = 100
  }
}

resource "aws_apigatewayv2_integration" "discovery_api_integrations" {
  for_each               = aws_lambda_function.resource_discovery_lambdas

  api_id                 = aws_apigatewayv2_api.resource_discovery_api.id
  integration_type       = "AWS_PROXY"
  connection_type        = "INTERNET"
  description            = "resource_discovery service"
  integration_uri        = each.value.invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 10000
}

resource "aws_apigatewayv2_route" "discoverlist_api_route" {
  for_each  = aws_apigatewayv2_integration.discovery_api_integrations

  api_id    = aws_apigatewayv2_api.resource_discovery_api.id
  route_key = "GET /vlab_resource_discovery_${each.key}"
  target    = "integrations/${each.value.id}"
}

resource "aws_lambda_permission" "allow_api" {
  for_each            = aws_lambda_function.resource_discovery_lambdas

  action              = "lambda:InvokeFunction"
  function_name       =  each.value.arn
  principal           = "apigateway.amazonaws.com"
  source_arn          = "${aws_apigatewayv2_api.resource_discovery_api.execution_arn}/**"
}
