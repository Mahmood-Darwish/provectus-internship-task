import config
from util import *
from minio import Minio
import os
import io
import db_handler


def append_to_csv(minio_client: Minio, input_bucket: str, object_name: str, user_id: (bool, int), output_bucket: str) -> None:
    """
    Given the info about a certain .csv file, create the necessary info and add it to output_bucket/output.csv.
    :param minio_client: The minio client connected to.
    :param input_bucket: The bucket where to find the csv file to append.
    :param object_name:  The name of the .csv file.
    :param user_id: A tuple that explains if there is a .png for that .csv and the user id for that .csv.
    :param output_bucket: Where to save the output.csv.
    """
    lines = get_csv(minio_client, output_bucket, "output.csv", 5)
    if user_id[0]:
        png_path = input_bucket + "/" + object_name[:-4]
        png_path += ".png"
    else:
        png_path = "None"
    temp = get_csv(minio_client, input_bucket, object_name, 3)
    line_to_write = [str(user_id[1]), *temp[1], png_path]
    lines.append(line_to_write)
    put_csv("temp_output.csv", lines)
    minio_client.remove_object(output_bucket, "output.csv")
    minio_client.fput_object(output_bucket, "output.csv", "temp_output.csv")
    os.remove("temp_output.csv")
    db_handler.handle_row(config.table_name, line_to_write)


def find_png_and_id(minio_client: Minio, input_bucket: str, obj_name: str) -> (bool, int):
    """
    Checks if the .csv input_bucket/obj_name has a proper id and if it does then checks if there is a .png file
    with the same id.
    :param minio_client: The minio client connected to.
    :param input_bucket: The bucket where to find the inputs.
    :param obj_name: The name of the .csv file.
    :return: A tuple, first value is a true or false if a .png exists or not. The second value is a non-negative int
    if the user_id is correct or -1 if not.
    """
    try:
        user_id = int(obj_name[:-4])
    except ValueError:
        return False, -1
    png_name = obj_name[:-4]
    png_name += ".png"
    try:
        minio_client.stat_object(input_bucket, png_name)
        return True, user_id
    except:
        return False, user_id


def process(minio_client: Minio, input_bucket: str, output_bucket: str) -> None:
    """
    Reads all files in input_bucket in a minio client. looks for a .png and a .csv files
    that have the same name and combines them. Creates a new file output_bucket/output.csv
    with results and deletes the old one, replacing it.
    :param minio_client: The minio client connected to.
    :param input_bucket: The bucket where to find the inputs.
    :param output_bucket: The bucket where to store the outputs.
    """
    minio_client.remove_object(output_bucket, "output.csv")
    minio_client.put_object(
        output_bucket, "output.csv", io.BytesIO(b"user_id,first_name,last_name,birthts,img_path"), 45,
    )
    for obj in minio_client.list_objects(input_bucket):
        if obj.object_name.endswith('.csv'):
            user_id = find_png_and_id(minio_client, input_bucket, obj.object_name)
            if user_id[1] == -1:
                continue
            append_to_csv(minio_client, input_bucket, obj.object_name, user_id, output_bucket)
