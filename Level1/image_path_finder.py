import os
import pathlib
import csv


def append_to_csv(output_file, user_id: int, path_to_csv: str) -> bool:
    """

    :param output_file:
    :param user_id:
    :param path_to_csv:
    :return:
    """
    r = csv.reader(open(output_file + "/output.csv", "r"))
    lines = list(r)
    if not len(lines):
        lines.append(["user_id", "first_name", "last_name", "birthts", "img_path"])
    jpg_path = path_to_csv[:-4]
    jpg_path += ".png"
    line_to_write = [str(user_id), *list(csv.reader(open(path_to_csv, "r+")))[1], jpg_path]
    for i in range(len(lines)):
        if lines[i][0] == line_to_write[0]:
            if lines[i] == line_to_write:
                return False
            else:
                lines[i] = line_to_write
            break
    else:
        lines.append(line_to_write)
    w = csv.writer(open(output_file + "/output_temp.csv", "w+"))
    w.writerows(lines)
    os.remove(output_file + "/output.csv")
    os.rename(output_file + "/output_temp.csv", output_file + "/output.csv")
    return True


def find_png(input_path: str) -> int:
    """
    TODO
    :param input_path:
    :return:
    """
    user_id = int(pathlib.Path(input_path).stem)
    input_path = input_path[:-4]
    input_path += ".png"
    if os.path.isfile(input_path):
        return user_id
    return -1


def process(input_path: str, output_path: str) -> (int, list):
    """
    TODO
    :param input_path:
    :param output_path:
    :return:
    """
    if not os.path.exists(os.path.dirname(input_path)):
        raise ValueError("This directory doesn't exist")
    count = 0
    filenames = []
    for filename in os.listdir(input_path):
        if filename.endswith('.csv'):
            user_id = find_png(input_path + "/" + filename)
            if user_id == -1:
                continue
            if append_to_csv(output_path, user_id, input_path + "/" + filename):
                count += 1
                filenames.append(pathlib.Path(filename).stem)
    return count, filenames


print(process("/home/mahmood/git_workspace/provectus task/provectus-internship-task/Level1/demo-data", "/home/mahmood/git_workspace/provectus task/provectus-internship-task/Level1/demo-output"))
