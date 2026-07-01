import json
import os
import boto3
import psycopg2

def lambda_handler(event, context):
    # 1. Fetch values injected by install.sh
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    
    # 2. Fetch the dynamic local cloud host provided by LocalStack
    # Fallback to host.docker.internal if running in a generic container
    LOCAL_CLOUD_HOST = os.environ.get("LOCALSTACK_HOSTNAME", "host.docker.internal")
    
    #  Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            host="host.docker.internal", 
            port=5432, 
            database=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS
        )
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM my_table;")
        row_count = cur.fetchone()
        cur.close()
        conn.close()
        db_status = f"Success! Found {row_count[0]} rows inside 'my_table'."
    except Exception as e:
        db_status = f"Database tracking connection failed: {str(e)}"

    #  Connect to S3 using LocalStack's internal endpoint routing
    try:
        # Construct endpoint cleanly: http://<localstack_internal_ip>:4566
        s3_endpoint = f"http://{LOCAL_CLOUD_HOST}:4566"
        
        s3 = boto3.client('s3', endpoint_url=s3_endpoint)
        s3.head_object(Bucket=BUCKET_NAME, Key="sample_image.jpg")
        s3_status = f"Success! Found 'sample_image.jpg' inside bucket '{BUCKET_NAME}'."
    except Exception as e:
        s3_status = f"S3 object scanning verification failed: {str(e)}"

    return {
        'statusCode': 200,
        'body': json.dumps({
            'database_check': db_status,
            's3_check': s3_status,
            'triggered_by_event_action': event.get("action", "UNKNOWN")
        })
    }
