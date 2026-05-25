# AWS Lambda + Glue CI/CD Pipeline Using GitLab and Terraform

This project demonstrates a production-style CI/CD pipeline for deploying:

- AWS Lambda functions
- AWS Glue jobs

using:

- GitLab CI/CD
- Terraform
- Pytest
- AWS S3

---

# Project Architecture

```text
Developer Pushes Code
        ↓
GitLab Pipeline Starts
        ↓
Terraform Format Check
        ↓
Terraform Validate
        ↓
Pytest Execution
        ↓
Glue Script Upload to S3
        ↓
Terraform Deploy
        ↓
AWS Resources Updated
```

---

# Project Structure

```text
project/
│
├── infra/
│   ├── provider.tf
│   ├── variables.tf
│   ├── lambda.tf
│   ├── glue.tf
│   ├── outputs.tf
│   └── main.tf
│
├── src/
│   ├── lambda_code/
│   │   └── app.py
│   │
│   └── glue/
│       └── glue_job.py
│
├── tests/
│   ├── lambda/
│   │   └── test_lambda.py
│   │
│   └── glue/
│       └── test_glue.py
│
├── scripts/
│   └── upload_glue.sh
│
├── requirements.txt
├── .gitlab-ci.yml
├── README.md
└── .gitignore
```

---

# Technologies Used

- Terraform
- GitLab CI/CD
- AWS Lambda
- AWS Glue
- AWS S3
- Pytest
- Python

---

# Features

- Deploy Lambda only
- Deploy Glue only
- Deploy both simultaneously
- Terraform validation
- Terraform formatting checks
- Automated Glue script upload to S3
- Automated Lambda packaging using Terraform archive provider
- Pytest integration
- Manual destroy stage
- Runtime IAM role input support

---

# Prerequisites

Install the following tools locally:

## Terraform

https://developer.hashicorp.com/terraform/downloads

---

## AWS CLI

https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

---

## Git

https://git-scm.com/downloads

---

# AWS Requirements

The following resources must already exist:

- S3 bucket for Glue scripts
- Lambda IAM Role
- Glue IAM Role

Example:

```text
arn:aws:iam::123456789012:role/dev-lambda-role

arn:aws:iam::123456789012:role/dev-glue-role
```

---

# Configure AWS Credentials

Run:

```bash
aws configure
```

Provide:

```text
AWS Access Key ID
AWS Secret Access Key
AWS Region
```

---

# Clone Repository

```bash
git clone <repo-url>

cd <repo-name>
```

---

# Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# Lambda Code

Location:

```text
src/lambda_code/app.py
```

Example:

```python
def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "body": "Lambda deployment successful"
    }
```

---

# Glue Job Code

Location:

```text
src/glue/glue_job.py
```

Example:

```python
def main():

    print("Glue Job Started")

if __name__ == "__main__":
    main()
```

---

# Running Tests Locally

```bash
pytest tests/ -v
```

---

# Terraform Commands

## Initialize Terraform

```bash
cd infra

terraform init
```

---

## Validate Terraform

```bash
terraform validate
```

---

## Format Terraform Files

```bash
terraform fmt -recursive
```

---

# GitLab CI/CD Pipeline

Pipeline stages:

```text
format
validate
test
deploy
destroy
```

---

# GitLab Variables

When running the pipeline manually, provide:

| Variable | Description |
|---|---|
| TF_VAR_lambda_role_arn | Existing Lambda IAM Role ARN |
| TF_VAR_glue_role_arn | Existing Glue IAM Role ARN |

Example:

```text
TF_VAR_lambda_role_arn=arn:aws:iam::123456789012:role/dev-lambda-role

TF_VAR_glue_role_arn=arn:aws:iam::123456789012:role/dev-glue-role
```

---

# Deploying Lambda

Go to:

```text
GitLab → Build → Pipelines → Run Pipeline
```

Run:

```text
deploy_lambda
```

Provide:

```text
TF_VAR_lambda_role_arn
```

---

# Deploying Glue

Run:

```text
deploy_glue
```

Provide:

```text
TF_VAR_glue_role_arn
```

---

# Deploying Both

Run:

```text
deploy_both
```

Provide:

```text
TF_VAR_lambda_role_arn

TF_VAR_glue_role_arn
```

---

# Glue Script Upload

The pipeline automatically uploads:

```text
src/glue/glue_job.py
```

to:

```text
s3://dev-cog-generic-glue-scripts/new/
```

No manual S3 upload is required.

---

# Lambda Packaging

Terraform automatically packages Lambda code using:

```hcl
archive_file
```

No manual ZIP creation is required.

---

# Destroy Infrastructure

The pipeline includes a manual destroy stage.

To destroy resources:

```text
Run → terraform_destroy
```

This action is manual for safety purposes.

---

# Important Notes

- IAM roles are NOT created by Terraform
- Existing IAM role ARNs are provided during pipeline execution
- Glue scripts are automatically uploaded to S3
- Lambda packaging is fully automated

---

# Best Practices

- Use remote Terraform backend
- Use separate environments (dev/qa/prod)
- Store secrets securely
- Avoid hardcoding ARNs
- Use least privilege IAM policies

---

# Future Improvements

- Terraform remote state
- Security scanning
- Multi-environment deployment
- Approval stages
- Dockerized testing
- Blue/Green deployments

---

# Troubleshooting

## Terraform Validation Error

Run:

```bash
terraform fmt -recursive
```

---

## Pytest Import Error

Ensure:

```text
PYTHONPATH = $CI_PROJECT_DIR
```

is configured in `.gitlab-ci.yml`.

---

## Glue Deployment Fails

Verify:

- S3 bucket exists
- Glue role has S3 permissions

---

# Useful Commands

## Push Changes

```bash
git add .

git commit -m "Updated pipeline"

git push
```

---

# License

This project is for learning and DevOps automation purposes.