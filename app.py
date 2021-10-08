from flask import Flask, request, jsonify
import config
from image_path_finder import process
from util import *
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from typing import Union
import db_handler


minio_client = None
input_bucket = config.input_bucket
output_bucket = config.output_bucket


def sched_process():
    """
    Function for the scheduler to make automatic updates to entries.
    """
    print("Running automated update...")
    process(minio_client, input_bucket, output_bucket)
    print("Finished...")


sched = BackgroundScheduler()
sched.add_job(sched_process, 'interval', seconds=config.schedule_time)
sched.start()
atexit.register(lambda: sched.shutdown())

app = Flask(__name__)


@app.route('/data', methods=['POST'])
def process_data():
    """
    Forces a data update.
    """
    process(minio_client, input_bucket, output_bucket)
    return jsonify({"Result": "Done"})


def get_data(image_filter: Union[None, bool], min_age_filter: float, max_age_filter: float) -> list:
    """
    Gets the data from the database and removes the rows that don't pass the filters.
    :param image_filter: True, False, or None. Returns entries with photo path if true. Returns entries without
    photo path if false. Ignores if None.
    :param min_age_filter: Either -1 or a positive float. If -1 ignore, else entries' age must be higher
    than min_age_filter.
    :param max_age_filter: Either -1 or a positive float. If -1 ignore, else entries' age must be lower
    than min_age_filter.
    :return: list with filtered rows.
    """
    lines = db_handler.get_users_data(config.table_name)
    ans = []
    for i in range(len(lines)):
        if not check_image(lines[i], image_filter) or not check_min_age(lines[i], min_age_filter) or \
                not check_max_age(lines[i], max_age_filter):
            continue
        ans.append(lines[i])
    return ans


@app.route('/data', methods=['GET'])
def process_request():
    """
    Takes parameters from the query string in the URL as specified in the readme file.
    Queries the database and returns all of the rows.
    :return: a JSON file of all the rows that pass the filtering.
    """
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
