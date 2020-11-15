from utils import parse_data, extract_gpa_data, merge_gpa_data
from mysql_engine import loadEngine, MySQLEngine
import pathlib
import numpy as np


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

    e.insert_df(df, 'courses')


if __name__ == '__main__':
    e = loadEngine()
    upload_courses('data', e)
    del e
