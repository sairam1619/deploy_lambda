resource "aws_lambda_function" "lambda_function" {

  function_name = var.lambda_function_name

  role = aws_iam_role.lambda_role.arn

  handler = "app.lambda_handler"

  runtime = "python3.14"

  filename = "../src/lambda_code/lambda.zip"

  source_code_hash = filebase64sha256("../src/lambda_code/lambda.zip")
}
