variable "aws_region" {
  default = "us-west-2"
}

variable "lambda_function_name" {
  default = "gitlab-lambda"
}

variable "glue_job_name" {
  default = "gitlab-glue-job"
}

variable "s3_bucket" {
  default = "your-glue-script-bucket"
}
