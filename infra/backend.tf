terraform {
  backend "s3" {
    bucket = "terraform-tstate-file"
    key    = "lambda/terraform.tfstate"
    region = "us-west-2"
  }
}
