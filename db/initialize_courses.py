from utils import parse_data, extract_gpa_data, merge_gpa_data
from mysql_engine import loadEngine, MySQLEngine
import pathlib
import numpy as np
import json
from tqdm import tqdm


def upload_courses(file_path: str, engine: MySQLEngine):
    """
    Uploads all the courses to the MySQL database.

    :param self:
    :param file_path: the directory where to search the CSV files
    :param engine: a MySQLEngine where the data needs to be uploaded
    """
    df = parse_data(file_path)
    df = df[['courseId', 'creditHours']]

    # default value of Interest- will need to be hardcoded.
    df['Interest'] = ['["None"]'] * len(df)

    gpa_df = extract_gpa_data(file_path)
    df = merge_gpa_data(df, gpa_df)

    engine.insert_df(df, 'courses')


def tag_courses(file_path: str, engine: MySQLEngine):
    """
    Adds all tags to courses

    :param file_path (string): where to find the JSON document with course info
    :param engine (MySQLEngine): used to connect to RDMS
    """
    f = open(file_path, 'r')
    course_tags = json.load(f)
    f.close()

    engine.raw_operation('SET SQL_SAFE_UPDATES = 0')
    engine.raw_operation('UPDATE student_info.courses SET courses.interest = JSON_ARRAY()')
    engine.raw_operation('SET SQL_SAFE_UPDATES = 1')

    exec_command = "UPDATE student_info.courses " \
                    "SET interest = JSON_ARRAY_APPEND(`interest`, '$', '{}') " \
                    "WHERE course_id = '{}'"

    for tag in course_tags:
        tag_classes = course_tags[tag]
        pbar = tqdm(total=len(tag_classes))
        pbar.set_description("Processing {}".format(tag))
        for tag_class in tag_classes:
            engine.raw_operation(exec_command.format(tag, tag_class))
            pbar.update(1)
        del pbar


if __name__ == '__main__':
    e = loadEngine()
    upload_courses('data', e)
    tag_courses('db/static/track_data.json', e)
    del e
