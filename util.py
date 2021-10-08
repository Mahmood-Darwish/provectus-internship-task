import csv
import time
import datetime
from minio import Minio
from minio.select import SelectRequest, CSVInputSerialization, CSVOutputSerialization
from typing import Union


def timestamp_to_years(x: int) -> float:
    """
    Turns x timestamp to age in years.
    :param x: Timestamp.
    :return: the equivalent age.
    """
    temp = time.gmtime(x / 1000)
    temp1 = datetime.date(temp.tm_year, temp.tm_mon, temp.tm_mday)
    temp2 = datetime.date.today()
    return (temp2 - temp1).days / 365


def check_image(row: list, image_filter: Union[None, bool]) -> bool:
    """
    Checks if a certain row in the output.csv file correctly passes the filter.
    :param row: an entry in the .csv file.
    :param image_filter: True, False, or None.
    :return: if it passes or not.
    """
    if image_filter is None:
        return True
    if image_filter:
        if row[-1] != "None":
            return True
    if not image_filter:
        if row[-1] == "None":
            return True
    return False


def check_min_age(row: list, min_age_filter: float) -> bool:
    """
    Checks if a certain row in the output.csv file correctly passes the filter.
    :param row: an entry in the .csv file.
    :param min_age_filter: minimum age in years.
    :return: if it passes or not.
    """
    if min_age_filter == -1:
        return True
    if timestamp_to_years(int(row[-2])) >= min_age_filter:
        return True
    return False


def check_max_age(row: list, max_age_filter: float) -> bool:
    """
    Checks if a certain row in the output.csv file correctly passes the filter.
    :param row: an entry in the .csv file.
    :param max_age_filter: maximum age in years.
    :return: if it passes or not.
    """
    if max_age_filter == -1:
        return True
    if timestamp_to_years(int(row[-2])) <= max_age_filter:
        return True
    return False


def get_csv(minio_client: Minio, bucket: str, obj: str, num_col: int) -> list:
    """
    Given a minio client with a bucket name and an object name, returns the csv file named obj in the bucket.
    To parse the CSV file it needs the number of columns.
    :param minio_client: Minio client where the data is put.
    :param bucket: Name of the bucket.
    :param obj: Name of the CSV file.
    :param num_col: Number of rows in the CSV file.
    :return: A list of lists where each inner list is a row in the CSV file.
    """
    with minio_client.select_object_content(
            bucket,
            obj,
            SelectRequest(
                "select * from S3Object",
                CSVInputSerialization(),
                CSVOutputSerialization(),
                request_progress=True,
            ),
    ) as result:
        for data in result.stream():
            x = data.decode().replace("\n", ",").split(",")
            for i in range(len(x)):
                x[i] = x[i].strip('"').strip(" ")
    y = [i for i in x if i != ""]
    ans = []
    k = 0
    temp = []
    for i in y:
        if not k:
            ans.append(temp.copy())
            temp.clear()
        temp.append(i)
        k += 1
        k %= num_col
    ans.append(temp.copy())
    ans = ans[1:]
    return ans


def put_csv(path: str, lines: list) -> None:
    """
    Takes a path and a list of lists. Creates a CSV file out of that list in that path.
    :param path: The path to where to save the file.
    :param lines: A list of lists. Each list is a row in the CSV file.
    """
    w = csv.writer(open(path, "w+"))
    w.writerows(lines)
