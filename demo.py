import os
import json
import time
import boto3
import psycopg2
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# 1. Load the custom configurations provisioned dynamically by install.sh
if not os.path.exists(".env"):
    print("\033[0;31m Error: .env file not found! Please run ./install.sh first to provision resources.\033[0m")
    exit(1)

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
LAMBDA_NAME = os.getenv("LAMBDA_FUNCTION_NAME")

# LocalStack serves all simulated AWS services on port 4566
LOCALSTACK_ENDPOINT = "http://localhost:4566"


def wait_for_lambda_ready(lambda_client, function_name, timeout_seconds=60, interval_seconds=2):
    print(f"    Waiting for Lambda function '{function_name}' to become available...")
    deadline = time.time() + timeout_seconds
    last_error = None

    while time.time() < deadline:
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"    Lambda function '{function_name}' is ready.")
            return
        except ClientError as exc:
            last_error = exc
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in {"ResourceNotFoundException", "FunctionNotFoundException", "NotFoundException"}:
                time.sleep(interval_seconds)
                continue
            raise
        except Exception as exc:
            last_error = exc
            time.sleep(interval_seconds)

    raise RuntimeError(
        f"Lambda function '{function_name}' did not become ready within {timeout_seconds} seconds: {last_error}"
    )


print("======================================================================")
print(" <--- STARTING APPLICATION DEVELOPER WORKFLOW VALIDATION --->")
print("======================================================================")


# ---  USE CASE 1: Using the Pre-Provisioned S3 Bucket ---
print(f" [S3 Action] Initializing client connection toward: {LOCALSTACK_ENDPOINT}")
s3_client = boto3.client('s3', endpoint_url=LOCALSTACK_ENDPOINT)

# Create a local dummy mock file to mimic a real binary image upload
local_filename = 'sample_image.jpg'


print(f"    Uploading '{local_filename}' to pre-existing bucket '{BUCKET_NAME}'...")
s3_client.upload_file(local_filename, BUCKET_NAME, local_filename)


# ---  USE CASE 2: Using the Pre-Provisioned Database ---
print(f"\n [DB Action] Connecting to PostgreSQL on localhost:5432 (DB: {DB_NAME})...")
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
cur = conn.cursor()

print("Create and Insert sample developer records into a sammple table named 'my_table'...")
cur.execute("CREATE TABLE IF NOT EXISTS my_table (id SERIAL PRIMARY KEY, name VARCHAR(100), age INT);")
cur.execute("INSERT INTO my_table (name, age) VALUES ('A', 30), ('B', 25), ('C', 35);")
conn.commit()


# ---  USE CASE 3: Synchronously Invoking the Cloud Lambda Function ---
print(f"\n[Lambda Action] Connecting to Lambda service engine...")
lambda_client = boto3.client('lambda', endpoint_url=LOCALSTACK_ENDPOINT, region_name='us-east-1')

# Build a payload dictionary containing test parameters to forward to the function
mock_event_payload = {
    "action": "TEST_PING",
    "user": DB_USER
}

wait_for_lambda_ready(lambda_client, LAMBDA_NAME)

print(f"    Invoking function '{LAMBDA_NAME}' and waiting for response...")
for attempt in range(1, 6):
    try:
        lambda_response = lambda_client.invoke(
            FunctionName=LAMBDA_NAME,
            InvocationType='RequestResponse',  # Synchronous request-response execution
            Payload=json.dumps(mock_event_payload)
        )
        break
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code in {"ResourceNotFoundException", "FunctionNotFoundException", "NotFoundException"} and attempt < 5:
            print(f"    Lambda function was not ready yet; retrying ({attempt}/5)...")
            time.sleep(2)
            continue
        raise

# Extract and decode the raw binary byte stream stream payload body response 
raw_payload_bytes = lambda_response['Payload'].read()
decoded_response_string = raw_payload_bytes.decode('utf-8')
lambda_result = json.loads(decoded_response_string)


# ---  CLEANUP WORKSPACE ---
cur.close()
conn.close()


# ======================================================================
#  FINAL RESULTS REPORT PIPELINE OUTPUTS
# ======================================================================
print("\n" + "="*70)
print("\033[0;32m ALL LOCAL CLOUD COMPONENT TASKS TESTED!\033[0m")
print("="*70)
print("\033[0;32m[S3 Status]:  File successfully pushed to the local bucket storage system.\033[0m")
print("\033[0;32m[DB Status]:  Row entries committed safely into the relational tables.\033[0m")
print("\033[0;32m[Lambda Status]: Execution triggered smoothly.\033[0m")
print("")

# Parse out and show the inner structural verification report compiled by the background Lambda
lambda_body_data = json.loads(lambda_result.get('body', '{}'))
print(f" \033[1;34m--- Real-time Response From Inside the Lambda Container ---\033[0m")
print(f"  Database Scan Result:  {lambda_body_data.get('database_check')}")
print(f"  S3 Bucket Scan Result:  {lambda_body_data.get('s3_check')}")
print(f"  Passed Event Action:   {lambda_body_data.get('triggered_by_event_action')}")
print(f"\033[1;34m-----------------------------------------------------------\033[0m")
print("")
print("\033[0;32m------------------- You can manually Verify by navigating as mentioned below ! -------------------\033[0m")
print(f" S3 metadata url: http://localhost:4566/{BUCKET_NAME}/{local_filename}")
print(f" DB query check:  docker exec -it mock_rds_postgres psql -U {DB_USER} -d {DB_NAME} -c \"SELECT * FROM my_table;\"")
print(f" Lambda invoke:   docker exec -it localstack_main awslocal lambda invoke --function-name payload-processor-lambda     --payload '{{\"action\": \"MANUAL_TERMINAL_PING\"}}'     raw_result.json")
print("======================================================================")
