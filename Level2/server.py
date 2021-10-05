from flask import Flask, request, jsonify
from Level1.image_path_finder import process
import csv
import os

input_path = "/home/mahmood/git_workspace/provectus task/provectus-internship-task/src-data"
output_path = "/home/mahmood/git_workspace/provectus task/provectus-internship-task/processed_data"

app = Flask(__name__)


@app.route('/data', methods=['POST'])
def process_data():
    process(input_path, output_path)
    return "OK", 200


def millisecond_to_years(x):
    return x / 31556952000


def check_image(row, image_filter):
    if image_filter is None:
        return True
    if image_filter:
        if row[-1] != "":
            return True
    if not image_filter:
        if row[-1] == "":
            return True
    return False


def check_min_age(row, min_age_filter):
    if min_age_filter == -1:
        return True
    if millisecond_to_years(int(row[-2])) >= min_age_filter:
        return True
    return False


def check_max_age(row, max_age_filter):
    if max_age_filter == -1:
        return True
    if millisecond_to_years(int(row[-2])) <= max_age_filter:
        return True
    return False


def get_data(image_filter, min_age_filter, max_age_filter):
    if not os.path.isfile(output_path + "/output.csv"):
        f = open(output_path + "/output.csv", "w+")
        f.close()
    r = csv.reader(open(output_path + "/output.csv", "r+"))
    lines = list(r)[1:]
    ans = []
    for i in range(len(lines)):
        if not check_image(lines[i], image_filter):
            continue
        if not check_min_age(lines[i], min_age_filter):
            continue
        if not check_max_age(lines[i], max_age_filter):
            continue
        ans.append(lines[i])
    return ans


@app.route('/data', methods=['GET'])
def process_request():
    image_filter = request.args.get('is_image_exists', default="None", type=str)
    min_age_filter = request.args.get('min_age', default=-1.0, type=float)
    max_age_filter = request.args.get('max_age', default=-1.0, type=float)
    if min_age_filter > max_age_filter != -1:
        return "min age is bigger than max age", 400
    if image_filter.lower() == "true":
        image_filter = True
    elif image_filter.lower() == "false":
        image_filter = False
    else:
        image_filter = None
    return jsonify({'result': get_data(image_filter, min_age_filter, max_age_filter)})


if __name__ == "__main__":
    app.run(debug=True)
