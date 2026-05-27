terraform {
  backend "s3" {

    bucket = "dev-cog-generic-terraform-state-file"

    key = "gitlab/lambda/terraform.tfstate"

    region = "us-west-2"
  }
}