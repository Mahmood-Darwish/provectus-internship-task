from util import *
from minio import Minio
import os


def append_to_csv(minio_client: Minio, input_bucket: str, object_name: str, user_id: (bool, int), output_bucket: str) -> bool:
    """
    Given the path to the .csv file and the user id, create the data needed and then
    append it to output_file/output.csv.
    :param output_file: path to where the output file should be.
    :param user_id: user id to be added to the output file.
    :param path_to_csv: path to the .csv file.
    :param user_png: is there a photo for this .csv file.
    :return: true if the output.csv was changed, false if not.
    """
    lines = get_csv(minio_client, output_bucket, "output.csv", 5)
    if user_id[0]:
        jpg_path = input_bucket + "/" + object_name[:-4]
        jpg_path += ".png"
    else:
        jpg_path = "None"
    temp = get_csv(minio_client, input_bucket, object_name, 3)
    line_to_write = [str(user_id[1]), *temp[1], jpg_path]
    for i in range(len(lines)):
        if lines[i][0] == line_to_write[0]:
            if lines[i] == line_to_write:
                return False
            else:
                lines[i] = line_to_write
            break
    else:
        lines.append(line_to_write)
    put_csv("temp_output.csv", lines)
    minio_client.remove_object(output_bucket, "output.csv")
    minio_client.fput_object(output_bucket, "output.csv", "temp_output.csv")
    os.remove("temp_output.csv")
    return True


def find_png_and_id(minio_client: Minio, input_bucket: str, obj_name: str) -> (bool, int):
    """
    Takes a path to a .csv file and checks if there's a .png file with the same name in the same directory.
    if the file exists then returns the name of the file (since this is also the user id), if it doesn't exist
    return -1.
    :param input_path: path to the .csv file.
    :return: user id if the file exists or -1 otherwise.
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


def process(minio_client: Minio, input_bucket: str, output_bucket: str) -> (int, list):
    """
    Reads all files in input_path (absolute path). looks for a .png and a .csv files that have the same name and
    combines them. Stores output in output_path/output.csv.
    Returns the number of files found and their names.
    :param minio_client: path used for finding the input.
    :param input_bucket: path used for finding the input.
    :param output_bucket: path used for finding the output file.
    :return: number of files found and their names.
    """
    count = 0
    filenames = []
    for obj in minio_client.list_objects(input_bucket):
        if obj.object_name.endswith('.csv'):
            user_id = find_png_and_id(minio_client, input_bucket, obj.object_name)
            if user_id[1] == -1:
                continue
            if append_to_csv(minio_client, input_bucket, obj.object_name, user_id, output_bucket):
                count += 1
                filenames.append(obj.object_name)
    filenames.sort()
    return count, filenames
