import psycopg2
import boto3

# Create an S3 bucket using localstack and upload a sample image file

s3 = boto3.client('s3', endpoint_url='http://localhost:4566')
bucket_name = 'my-local-bucket'
# Create the bucket
s3.create_bucket(Bucket=bucket_name)
# Upload a sample image file to the bucket
s3.upload_file('sample_image.jpg', bucket_name, 'sample_image.jpg')

# Create a PostgreSQL table using dockerized PostgreSQL and psycopg2
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='mydb',
    user='myuser',
    password='mypassword'
)
cur = conn.cursor()
# Create a sample table
cur.execute('''
    CREATE TABLE IF NOT EXISTS my_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        age INT
    )
''')
# Insert sample data into the table
cur.execute('''
    INSERT INTO my_table (name, age) VALUES
    ('Alice', 30),
    ('Bob', 25),
    ('Charlie', 35)
''')
# Commit the changes and close the connection
conn.commit()
cur.close()
conn.close()
print("-----------------------------Outputs-----------------------------------")
print("\033[0;32mS3 sample bucket created and sample image uploaded.\033[0m")
print("\033[0;32mPostgreSQL sample table created and sample data inserted.\033[0m")
print("")
print("\033[0;32m----------------------S3 Check---------------------------------------------------\033[0m")
print("\033[0;32mOpen in browser 'http://localhost:4566/my-local-bucket/sample_image.jpg' to verify the uploaded image.\033[0m")
print("")
print("\033[0;32m----------------------DB Check---------------------------------------------------\033[0m")
print("\033[0;32mRun '  docker exec -it mock_rds_postgres psql -U myuser -d mydb -c 'SELECT * FROM my_table;'  ' to verify the inserted data.\033[0m")
