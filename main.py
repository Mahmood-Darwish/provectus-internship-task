from minio import Minio
import config
import os
import io
import app
from minio.select import SelectRequest, CSVInputSerialization, CSVOutputSerialization
import db_handler


def get_minio_client(access: str, secret: str) -> Minio:
    """
    Creates a connection to a minio client.
    :param access: Access key to minio.
    :param secret: Secret key to minio.
    :return: minio connection.
    """
    return Minio(
        config.minio_host + ":9000",
        access_key=access,
        secret_key=secret,
        secure=False
    )


if __name__ == "__main__":
    minio_client = get_minio_client(config.access_key, config.secret_key)
    db_handler.create_table_users(config.table_name)
    if not minio_client.bucket_exists(config.input_bucket):
        minio_client.make_bucket(config.input_bucket)
    if not minio_client.bucket_exists(config.output_bucket):
        minio_client.make_bucket(config.output_bucket)

    try:
        minio_client.select_object_content(
                config.output_bucket,
                "output.csv",
                SelectRequest(
                    "select * from S3Object",
                    CSVInputSerialization(),
                    CSVOutputSerialization(),
                    request_progress=True,
                ),
        )
    except:
        minio_client.put_object(
            config.output_bucket, "output.csv", io.BytesIO(b"user_id,first_name,last_name,birthts,img_path"), 45,
        )

    app.minio_client = minio_client
    port = int(os.environ.get('PORT', 5000))
    app.app.run(host='0.0.0.0', port=port)
