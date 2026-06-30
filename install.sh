#!/bin/bash
clear

NC='\033[0m'        # Reset
GREEN='\033[0;32m'  # Green
YELLOW='\033[1;33m' # Yellow
RED='\033[0;31m'
echo "======================================================================"
echo -e "${GREEN}INITIALIZING LOCAL DEVELOPMENT ENVIRONMENT${NC}"
echo "======================================================================"
echo -e "${YELLOW}Check for Docker runtime and Docker Compose installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker and try again.${NC}"
    exit 1
fi
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose and try again.${NC}"
    exit 1
fi
if ! command -v pip &> /dev/null; then
    echo -e "${RED}pip is not installed. Please install pip and try again.${NC}"
    exit 1
fi
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 is not installed. Please install Python3 and try again.${NC}"
    exit 1
fi

echo -e "${YELLOW}Booting Docker containers in the background......${NC}"
echo ""

# Start the environment
docker compose up -d

echo -e "${YELLOW}Waiting for initialization of simulated AWS and Mock RDS...${NC}"
sleep 4
echo -e "${GREEN}Done! Simulated Environment with containers $(docker ps --format '{{.Names}}' | grep -E 'rds|localstack' | paste -sd ', ' -) is running.${NC}"
sleep 4
echo "======================================================================"
echo -e "${GREEN}MOCK DB AND S3 CONFIG DETAILS FOR APPLICATION ENGINEERS${NC}"
echo "======================================================================"
echo -e "${YELLOW}APPLICATION DATABASE SERVICE CONNECTION DETAILS :${NC}"
echo "   DB_HOST     : mock_rds_postgres"
echo "   DB_PORT     : 5432"
echo "   DB_USER     : myuser"
echo "   DB_PASSWORD : mypassword"
echo "   DB_NAME     : mydb"
echo ""
echo -e "${YELLOW} AWS S3 SERVICE CONNECTION URL Usage : ${NC}"
echo "   s3_client = boto3.client('s3', endpoint_url='http://localstack_main:4566', aws_access_key_id=test, aws_secret_access_key=test)"
echo ""
echo -e "${YELLOW}DEVELOPER TODO : PRODUCTION AWS CLOUD MIGRATION :${NC}"
echo "   1. Update DB_HOST config to your live AWS RDS endpoint URL."
echo "   2. CLEAN UP S3 INITIALIZATION FOR PRODUCTION:"
echo "      Change to: s3_client = boto3.client('s3')"
echo "      REMOVE: 'endpoint_url', 'aws_access_key_id', and 'aws_secret_access_key' parameters."
echo "======================================================================"
echo -e "${GREEN}SAMPLE PYTHON CODE FOR APPLICATION ENGINEERS${NC}"
echo "======================================================================"
echo -e "${YELLOW}Read demo.py in the repository and to test it Run 'python3 -m pip install boto3 psycopg2-binary && python3 demo.py' to see the following in action:${NC}"
echo "
        - create a sample S3 bucket using simulated AWS S3 service 
        - create a sample table in the mock RDS database."    