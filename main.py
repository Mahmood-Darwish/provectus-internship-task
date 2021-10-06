from minio import Minio
import config
import os, io
import glob
import server
from minio.select import SelectRequest, CSVInputSerialization, CSVOutputSerialization


def get_minio_client(access, secret):
    return Minio(
        'localhost:9000',
        access_key=access,
        secret_key=secret,
        secure=False
    )


def upload_local_directory_to_minio(local_path, bucket_name):
    assert os.path.isdir(local_path)

    for local_file in glob.glob(local_path + '/**'):
        local_file = local_file.replace(os.sep, "/")  # Replace \ with / on Windows
        if not os.path.isfile(local_file):
            upload_local_directory_to_minio(
                local_file, bucket_name)
        else:
            remote_path = os.path.join(
                local_file[1 + len(local_path):])
            remote_path = remote_path.replace(
                os.sep, "/")  # Replace \ with / on Windows
            minio_client.fput_object(bucket_name, remote_path, local_file)


if __name__ == "__main__":
    minio_client = get_minio_client(config.access_key, config.secret_key)
    if not minio_client.bucket_exists("src"):
        minio_client.make_bucket("src")
    if not minio_client.bucket_exists("res"):
        minio_client.make_bucket("res")

    try:
        minio_client.select_object_content(
                "res",
                "output.csv",
                SelectRequest(
                    "select * from S3Object",
                    CSVInputSerialization(),
                    CSVOutputSerialization(),
                    request_progress=True,
                ),
        )
    except:
        result = minio_client.put_object(
            "res", "output.csv", io.BytesIO(b"user_id,first_name,last_name,birthts,img_path"), 45,
        )

    server.minio_client = minio_client
    server.input_bucket = "src"
    server.output_bucket = "res"
    server.app.run()
