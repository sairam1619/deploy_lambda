resource "aws_glue_job" "glue_job" {

  name = var.glue_job_name

  role_arn = aws_iam_role.glue_role.arn

  command {

    script_location = "s3://${var.s3_bucket}/glue/glue_job.py"

    python_version = "3"

    name = "glueetl"
  }

  glue_version = "4.0"

  max_capacity = 2
}
