from neo4j_engine import Neo4JEngine
from os import path
import pandas as pd
import numpy as np
import pathlib


# not official courses, but need to be taken into account
special_prereqs = ['THREE YEARS OF HIGH SCHOOL MATHEMATICS', 'ONE YEAR OF HIGH SCHOOL CHEMISTRY']

# used to insert a class node
insert_command = 'CREATE (c: Class {courseId: "%s", courseTitle: "%s", creditHours: %d, description: "%s"})'

# used to create the OR and AND nodes, as well as the relevant relationships
and_insert_command = 'MATCH (c: Class {courseId: "%s"}) CREATE (c)<-[r: HAS]-(a: AND {courseId: "%s"})'
or_insert_command = 'MATCH (a: AND {courseId: "%s"}) CREATE (a)<-[r:HAS]-(o: OR {courseId: "%s", prereqId: %d})'
prereq_rel_command = 'MATCH (o: OR {courseId: "%s", prereqId: %d}), (c: Class {courseId: "%s"}) CREATE (o)<-[r:PREREQ]-(c)'


def extract_prereqs(prerequisite):
    """
    Extracts rough prerequisites based on tokenization, then converts into JSON format.
    Each key-value pair represents an OR combination.

    :param prerequisite: A raw string
    :return: A JSON-ized dictionary of lists.

    """
    # Replacement mapping for prereq strings
    PREREQ_REPLACE_MAPPING = {
        ': ': '',
        ' OR': ',',
        ' AND': ';',
        'ONE OF': '',
    }
    
    if type(prerequisite) == pd.core.series.Series:
        prerequisite = str(prerequisite.to_numpy())

    prereq_dict = {}
    prerequisite = prerequisite.strip().upper()
    if 'PREREQUISITE' not in prerequisite:
        return {'req1': []}
    
    if 'PREREQUISITES' in prerequisite:
        prerequisite = prerequisite[prerequisite.find('PREREQUISITES') + 14:]
    else:
        prerequisite = prerequisite[prerequisite.find('PREREQUISITE') + 13:]
    prerequisite = prerequisite.strip()

    for key, value in PREREQ_REPLACE_MAPPING.items():
        prerequisite = prerequisite.replace(key, value).split(".")[0]

    # Splitting AND values based on semicolons and OR values after that based on commas
    # Also removes empty values
    split_values = [list(filter(lambda x: x != '', map(lambda x: x.strip(),
                                                       string.split(","))))
                    for string in prerequisite.split(";")]

    #Adding each requisite to the JSON dictionary
    for i, value in enumerate(split_values):
        prereq_dict['req' + str(i + 1)] = value

    return prereq_dict


def clean_entries(data):
    """
    Guarantees that each prerequisite set has at least 1 by validating class list. Ignores "no prereq" classes.

    :param data: a Pandas dataframe
    :return: a cleaned pandas dataframe.
    """
    valid_rows = np.array([True] * len(data))
    i = 0
    for _, row in data.iterrows():
        prereqs = row['calculated_prereqs']
        if len(prereqs) == 1 and len(prereqs['req1']) == 0:
            continue
        for or_req in prereqs:
            i = 0
            while i < len(prereqs[or_req]):
                match = data['courseId'].loc[[substring in prereqs[or_req][i] for substring in data['courseId']]]
                if len(match) > 0:
                    prereqs[or_req][i] = str(match.to_numpy()[0])
                    i += 1
                elif prereqs[or_req][i] in special_prereqs:
                    i += 1
                else:
                    del prereqs[or_req][i]
            
            if len(prereqs[or_req]) == 0:
                valid_rows[i] = False
                break
        i += 1
    out_data = data.loc[valid_rows]
    def remove_quotes(desc):
        return desc.replace('"', '').replace("'", '')
    out_data['description'] = out_data['description'].apply(remove_quotes)
    return out_data


def insert_to_database(file_path: str, engine: Neo4JEngine):
    """
    Inserts all class data into  Neo4J database. Takes the latest class definition to generate prereqs.

    :param file_path: directory containing CSVs scraped from UIUC's courses site.
    :param engine: a Neo4J engine used to insert data
    """
    df = pd.DataFrame(columns=['courseId', 'courseTitle', 'creditHours', 'description', 'prereqs'])
    if file_path is None:
        raise ValueError('Must provide not-None filepath')
    for csv_filepath in sorted(pathlib.Path(file_path).glob('*.csv'), reverse=True):
        if csv_filepath is None:
            raise ValueError('Must provide legal filepath')
        
        if 'gpa_data.csv' in csv_filepath:
            continue
        new = pd.read_csv(str(csv_filepath))
        diff = new.loc[~new['courseId'].isin(df['courseId'])]
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

    # replaces NaNs with empty strings for classes w/o prereqs
    df['prereqs'].loc[[type(val) == float for val in df['prereqs']]] = ''

    df['calculated_prereqs'] = df['prereqs'].apply(extract_prereqs)

    # keeps only the rows that aren't identical to another class.
    df = df.loc[~((df['calculated_prereqs'] == {'req1': []}) & (df['prereqs'].str.contains('Same as')))]

    df = clean_entries(df)

    # inserts all the class nodes
    for row in df.to_numpy():
        exec_command = insert_command % tuple(row[:-2])
        try:
            engine.raw_operation(exec_command)
        except Exception as e:
            print(exec_command)
            print('\n\n')
            print(e)
            break

    # create special nodes
    engine.raw_operation('CREATE (c: Class {courseId: "NOPREREQS"})')
    for val in special_prereqs:
        engine.raw_operation('CREATE (c: Class {courseId: "%s"})' % val)

    # insert all relationship nodes
    for _, row in df.iterrows():
        calculated_prereqs = row['calculated_prereqs']
        and_exec_command = and_insert_command % (row['courseId'], row['courseId'])
        engine.raw_operation(and_exec_command)
        
        if len(calculated_prereqs) == 1 and len(calculated_prereqs['req1']) == 0:
            or_exec_command = or_insert_command % (row['courseId'], row['courseId'], 0)
            prereq_exec_command = prereq_rel_command % (row['courseId'], 0, "NOPREREQS")
            engine.raw_operation(or_exec_command)
            engine.raw_operation(prereq_exec_command)
        
        else:
            for i, or_prereq in enumerate(calculated_prereqs):
                or_exec_command = or_insert_command % (row['courseId'], row['courseId'], i)
                engine.raw_operation(or_exec_command)
                for prereq in calculated_prereqs[or_prereq]:
                    prereq_exec_command = prereq_rel_command % (row['courseId'], i, prereq)
                    engine.raw_operation(prereq_exec_command)


def insert_gpa_data(file_path: str, engine: Neo4JEngine):
    df = pd.read_csv(file_path)
    df = df[['YearTerm', 'Subject', 'Number', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D', 'F']]
    df['Students'] = np.sum(df.to_numpy()[:, 3:], axis=1)
    df['scores'] = np.sum(df.to_numpy()[:, 3:-1] * [4., 4., 3.67, 3.33, 3, 2.67, 2.33, 2, 1.67, 1.33, 1., 0.67, 0], axis=1)
    df['courseId'] = df['Subject'] + " " + df['Number'].astype(str)
    df = df.drop(labels=['Subject', 'Number'], axis=1)
    rows = []

    for i, courseId in enumerate(set(df['courseId'])):
        summed_row = np.sum(df[['Students', 'scores']].loc[df['courseId'] == courseId], axis=0)
        rows.append(list(summed_row) + [courseId])

    out_df = pd.DataFrame(rows, columns=['Students', 'scores', 'courseId'])
    
    gpa_exec_command = 'MATCH (c: Class {courseId: "%s"})  SET c.GPA = %f'
    for i, row in out_df.iterrows():
        exec_command = gpa_exec_command % (row['courseId'], row['GPA'])
        e.raw_operation(exec_command)


if __name__ == '__main__':
    file_path = '../data'
    uri = "bolt://%s:7687" % input()
    username = input()
    password = input()
    e = Neo4JEngine(uri, username, password)
    insert_to_database(file_path, e)
    insert_to_database(file_path + 'gpa-data.csv', e)
    del e
