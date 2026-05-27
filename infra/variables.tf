variable "aws_region" {
  default = "us-west-2"
}

variable "lambda_function_name" {
  default = "gitlab-lambda"
}

variable "lambda_role_arn" {

  description = "Lambda IAM Role ARN"

  type = string
}


