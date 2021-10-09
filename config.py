import os
access_key = "minio-access-key"
secret_key = "minio-secret-key"
db_name = "internship"
user = "postgres"
password = "postgres"
db_host = "db" if os.getenv("IS_DOCKER", False) else "localhost"
minio_host = "minio" if os.getenv("IS_DOCKER", False) else "localhost"
schedule_time = 900
table_name = "users"
input_bucket = "src"
output_bucket = "res"
