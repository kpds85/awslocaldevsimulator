# AWS Local Dev Simulator

This project provides a local development environment for testing AWS-like services without connecting to real cloud infrastructure. It uses Docker Compose to run LocalStack for S3 and Lambda simulation, and PostgreSQL for a local relational database.

## What this project includes

- LocalStack to simulate AWS S3 and Lambda services
- A PostgreSQL container for local database testing
- A sample Lambda function that checks database and S3 connectivity
- A demo script that exercises S3, PostgreSQL, and Lambda together

## Project structure

```text
awslocaldevsimulator/
├── demo.py
├── install.sh
├── uninstall.sh
├── requirements.txt
├── infrastructure/
│   └── docker-compose.yml
└── src/
    └── lambdas/
        └── payload_processor/
            └── index.py
```

## Key files

- infrastructure/docker-compose.yml
  Defines the LocalStack and PostgreSQL containers used by the environment.

- src/lambdas/payload_processor/index.py
  The sample Lambda handler that connects to PostgreSQL and verifies an object in the S3 bucket.

- install.sh
  Provisions the local environment, creates the S3 bucket, prepares PostgreSQL, packages the Lambda code, deploys it to LocalStack, and generates a .env file.

- uninstall.sh
  Stops and removes the Docker Compose services created during setup.

## Prerequisites

Make sure the following are installed on your machine:

- Docker
- Docker Compose
- Python 3
- zip

Ensure that Docker is running and you have permissions to execute Docker commands.
Ensure that you have sudo permissions to remove directories and files created during the installation process, it will be asked during the install.sh execution.

## Quick start

1. Clone the repository and change into the project folder:

```bash
cd awslocaldevsimulator
```

2. Make the setup scripts executable:

```bash
chmod +x ./install.sh ./uninstall.sh
```

3. Run the installer:

```bash
./install.sh
```

The installer will prompt for:

- S3 bucket name
- PostgreSQL database name
- PostgreSQL username
- PostgreSQL password
- Lambda function name

It will then start the containers, provision the resources, deploy the Lambda, and create a .env file for the demo script.

4. Run the demo workflow:

```bash
python3 demo.py
```

This script uploads a sample image to S3, inserts rows into PostgreSQL, and invokes the Lambda function.

5. When you are finished, remove the environment:

```bash
./uninstall.sh
```

## Useful verification commands

After installation, you can verify the environment manually with:

```bash
docker exec -it mock_rds_postgres psql -U <db_user> -d <db_name> -c "SELECT * FROM my_table;"
docker exec -it localstack_main awslocal s3 ls s3://<bucket_name>
docker exec -it localstack_main awslocal lambda invoke --function-name <lambda_name> --payload '{"action":"MANUAL_TERMINAL_PING"}' raw_result.json
```

## Notes

- The generated .env file stores runtime configuration values for the demo script.
- The sample Lambda uses the LocalStack endpoint and the PostgreSQL container to validate local integrations.
