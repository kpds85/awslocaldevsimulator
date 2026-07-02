#!/bin/bash
set -euo pipefail
clear

# Terminal Styling Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "======================================================================"
echo " <--- AWS LOCAL DEV SIMULATOR SETUP  ---> " 
echo "======================================================================"
echo -e "${GREEN}INFO : You need to provide sudo password to remove the cached build files when prompted during installation !!.${NC}"
echo "======================================================================"
echo -e "Checking for Docker and Docker Compose installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is installed but the daemon is not running. Please start Docker and try again.${NC}"
    exit 1
fi

if ! docker compose version > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker Compose is not available. Please install Docker Compose and try again.${NC}"
    exit 1
fi

# 1. Capture user customization configurations
read -p "Enter S3 Bucket Name [my-local-bucket]: " BUCKET_NAME
BUCKET_NAME=${BUCKET_NAME:-my-local-bucket}

read -p "Enter Database Name [mydb]: " DB_NAME
DB_NAME=${DB_NAME:-mydb}

read -p "Enter Database Master Username [myuser]: " DB_USER
DB_USER=${DB_USER:-myuser}

read -sp "Enter Database Master Password [mypassword]: " DB_PASS
DB_PASS=${DB_PASS:-mypassword}
echo ""

read -p "Enter Lambda Function Name [payload-processor-lambda]: " LAMBDA_NAME
LAMBDA_NAME=${LAMBDA_NAME:-payload-processor-lambda}

# Export environmental bindings so docker-compose picks them up cleanly
export MOCK_DB_NAME=$DB_NAME
export MOCK_DB_USER=$DB_USER
export MOCK_DB_PASS=$DB_PASS

# 2. Spin up core container architectures
echo -e "${GREEN}\n Starting Infrastructure Containers (LocalStack & PostgreSQL)...${NC}"
docker compose -f infrastructure/docker-compose.yml up -d

# 3. Rest and wait for basic engines readiness healthchecks
echo -e "${YELLOW} Provisioning PostgreSQL Database instance and Database engine...${NC}"
until docker exec mock_rds_postgres pg_isready -U "$DB_USER" -d "$DB_NAME" > /dev/null 2>&1; do
  sleep 1
done

echo -e "${YELLOW} Waiting for LocalStack cloud framework...${NC}"
until docker exec localstack_main awslocal s3 ls > /dev/null 2>&1; do
  sleep 1
done

# 4. Execute Infrastructure Layer Provisioning
echo -e "${GREEN}\n Provisioning Cloud Resources via Mock IaC...${NC}"

echo -e "${YELLOW} Provisioning S3 Bucket...${NC}"
docker exec localstack_main awslocal s3 mb "s3://$BUCKET_NAME" > /dev/null

echo -e "${YELLOW} Provisioning Lambda Function...${NC}"

# 5. Build and Package the Lambda Function Bundle
echo -e "${YELLOW} Packaging cloud dependencies archive from requirements.txt...${NC}"
BUILD_DIR=".build_staging"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Download Linux-native compilation binaries directly into the staging partition
docker run --rm \
    --entrypoint /bin/bash \
    -v "$(pwd)/$BUILD_DIR:/var/task" \
    -v "$(pwd)/requirements.txt:/var/task/requirements.txt" \
    public.ecr.aws/lambda/python:3.10 \
    -c "pip install -r /var/task/requirements.txt --target /var/task --quiet"

# Copy the developer's clean index.py code file directly into the staging package environment root
if [ -f src/lambdas/payload_processor/index.py ]; then
    cp src/lambdas/payload_processor/index.py "$BUILD_DIR/index.py"
else
    echo -e "${RED} Error: src/lambdas/payload_processor/index.py not found!${NC}"
    sudo rm -rf "$BUILD_DIR"
    exit 1
fi

# Compress the entire staging layout workspace into a standard deployment target zip file
(cd "$BUILD_DIR" && zip -q -r ../lambda_deployment.zip .)

sudo rm -rf "$BUILD_DIR"


# 6. Create the Lambda Function by passing the packaged binary data stream over stdin [1]
if ! docker exec -i localstack_main awslocal lambda create-function \
    --function-name "$LAMBDA_NAME" \
    --runtime python3.10 \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --handler index.lambda_handler \
    --zip-file fileb:///dev/stdin \
    --environment "Variables={DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASS=$DB_PASS,S3_BUCKET_NAME=$BUCKET_NAME}" \
    < lambda_deployment.zip > /dev/null 2>&1; then
    
    echo -e "${RED} Failed to provision Lambda, check logs of container localstack_main.${NC}"
    sudo rm -f lambda_deployment.zip
    exit 1
fi

# Wipe out deployment asset cleanly
sudo rm -f lambda_deployment.zip

# 7. Create runtime config parameters file sheet for the app developer workspace
cat << EOF > .env
S3_BUCKET_NAME=$BUCKET_NAME
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS
LAMBDA_FUNCTION_NAME=$LAMBDA_NAME
EOF

echo "======================================================================"
echo -e "${GREEN} ENVIRONMENT IS PROVISIONED AND READY FOR USE!${NC}"
echo "======================================================================"
echo -e "${YELLOW}To test the environment, run:${NC}"
echo -e "  ${BLUE}python3 demo.py${NC}"
echo ""
echo " Manual Verification Command Verification Traces:"
echo -e "   DB: ${BLUE}docker exec -it mock_rds_postgres psql -U $DB_USER -d $DB_NAME -c 'SELECT * FROM my_table;'${NC}"
echo -e "   S3: ${BLUE}docker exec -it localstack_main awslocal s3 ls s3://$BUCKET_NAME/${NC}"
echo -e "   Lambda: ${BLUE}docker exec -it localstack_main awslocal lambda invoke --function-name $LAMBDA_NAME --payload '{\"action\": \"MANUAL_TERMINAL_PING\"}' raw_result.json${NC}"
echo "======================================================================"
