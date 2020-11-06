import numpy as np
import pandas as pd
import pathlib
from tqdm import tqdm


def parse_data(file_path: str):
    """
    Reads through all downloaded CSV files to find the latest course information and definitions.

    :param file_path: the directory where to find the CSV files
    :return: A pandas DataFrame object containing the relevant parsed information
    """
    print('\nLoading class data from CSVs...')
    df = pd.DataFrame(columns=['courseId', 'courseTitle', 'creditHours', 'description', 'prereqs'])
    if file_path is None:
        raise ValueError('Must provide not-None filepath')

    pbar = tqdm(total = len(sorted(pathlib.Path(file_path).glob('*.csv'), reverse=True)) - 1)
    for csv_filepath in sorted(pathlib.Path(file_path).glob('*.csv'), reverse=True):
        if csv_filepath is None:
            raise ValueError('Must provide legal filepath')
        
        if 'gpa-data.csv' in str(csv_filepath):
            continue
        new = pd.read_csv(str(csv_filepath))
        diff = new.loc[~new['courseId'].isin(df['courseId'])]
        df = pd.concat([df, diff], axis=0)
        pbar.update(1)
        
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

    print('\nFinished reading in class CSV data')
    return df


def extract_gpa_data(file_path: str):
    """
    Reads through the GPA CSV (Obtained from prof. Wade's datasets) and extracts GPA per class

    :param file_path: the directory where to find the gpa-data.csv file
    :return: A pandas DataFrame object containing the relevant GPA information
    """
    print('\nReading in class GPA data from CSV...')
    df = pd.read_csv(file_path + '/gpa-data.csv')
    df = df[['YearTerm', 'Subject', 'Number', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D', 'F']]
    df['Students'] = np.sum(df.to_numpy()[:, 3:], axis=1)
    df['scores'] = np.sum(df.to_numpy()[:, 3:-1] * [4., 4., 3.67, 3.33, 3, 2.67, 2.33, 2, 1.67, 1.33, 1., 0.67, 0], axis=1)
    df['courseId'] = df['Subject'] + " " + df['Number'].astype(str)
    df = df.drop(labels=['Subject', 'Number'], axis=1)
    rows = []

    pbar = tqdm(total=len(set(df['courseId'])))
    for courseId in set(df['courseId']):
        summed_row = np.sum(df[['Students', 'scores']].loc[df['courseId'] == courseId], axis=0)
        rows.append(list(summed_row) + [courseId])
        pbar.update(1)

    out_df = pd.DataFrame(rows, columns=['Students', 'scores', 'courseId'])
    out_df['GPA'] = out_df['scores'] / out_df['Students']
    
    print('\nFinished calculating GPA data for each class')
    return out_df


def merge_gpa_data(main_df: pd.DataFrame, gpa_df: pd.DataFrame):
    """
    Merges in the GPA data with the main DF based on classes where GPA data is found.
    For classes where GPA data is unknown, a default "filler value" of 3.33 (B average) is used.

    :param main_df: dataframe into which data will be merged
    :param gpa_df: dataframe containing GPA data
    :return: modified main_df
    """
    main_df['GPA'] = [3.33] * len(main_df)

    _, main_ind, gpa_ind = np.intersect1d(main_df['courseId'], gpa_df['courseId'], return_indices=True)
    main_df['GPA'].iloc[main_ind] = gpa_df['GPA'].iloc[gpa_ind].to_numpy()

    return main_df
