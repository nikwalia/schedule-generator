from os import path
import pandas as pd
from mysql_engine import MySQLEngine
import pathlib


def upload_courses(file_path: str, engine: MySQLEngine):
    """
    Uploads all the courses to the MySQL database.

    :param self:
    :param file_path: the directory where to search the CSV files
    :param engine: a MySQLEngine where the data needs to be uploaded
    """
    # finds all CSVs, loads them into dataframes, and remove duplicates
    df = pd.DataFrame(columns=['courseId', 'creditHours'])
    if file_path is None:
        raise ValueError('Must provide not-None filepath')
    for csv_filepath in pathlib.Path(file_path).glob('*.csv'):
        if csv_filepath is None:
            raise ValueError('Must provide legal filepath')
        
        new = pd.read_csv(str(csv_filepath))
        diff = new.loc[~new['courseId'].isin(df['courseId'])][['courseId', 'creditHours']]
        df = pd.concat([df, diff], axis=0)

    # function for storing credit-hours. If there are multiple possible values, take the average
    def extract_hours(hrs_str):
        t = hrs_str.split()
        if 'TO' in t:
            return (int(t[0]) + int(t[2])) // 2
        elif 'OR' in t:
            return (int(t[0])) + int(t[2]) // 2
        else:
            return int(t[0])

    df['creditHours'] = df['creditHours'].apply(extract_hours)

    # default value of Interest- will need to be hardcoded
    df['Interest'] = ['None'] * len(df)
    # upload
    e.insert_df(df, 'courses')


if __name__ == '__main__':
    with open("../server_info", "r") as f:
        e = MySQLEngine(url = f.readline())
        upload_courses('../data', e)
        del e