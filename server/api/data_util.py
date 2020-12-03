from db.mysql_engine import *
import pandas as pd
import numpy as np

SPRING_SEM = "SP"

def convertSem(s: str):
    """
    Converts a string (e.g. "FA20") to a representative number

    :param s: string representing semester/year
    :return: integer representing semester/year
    """
    return int(s[len(SPRING_SEM):]) * 2 if s[:len(SPRING_SEM)] == SPRING_SEM else 1 + int(s[len(SPRING_SEM):]) * 2

def processSurveyData(data: dict):
    """
    Creates tuples to insert to the students and enrollments table from post request

    :param data: JSON of data from request
    :return: tuples representing students, enrollments, and tracks
    """
    startS, endS, currS, netID, name, password = data["StartingSem"], data["EndingSem"], data["CurrentSem"], data["NetID"], data["Name"], data["Password"]
    totalSem = convertSem(endS) - convertSem(startS) + 1
    student = (netID, name, password, startS, currS, endS, totalSem)

    tracks_to_insert = list(data["Majors"]) + list(data["Minors"])
    tracks = []
    if "interests" in data: # if interests is being submitted
        interests = list(data["interests"])
        for i, track in enumerate(tracks_to_insert):
            if i >= len(interests):
                tracks.append([track, "General", 0, netID])
            else:
                idx = [i for i, entry in enumerate(data['interests']) if track in entry['field_name']][0]
                tracks.append([track, interests[idx]['interest'], int(interests[idx]['credit_hrs']), netID])

    else: # create interests from scratch
        for m in (tracks_to_insert):
            tracks.append([m, "General", 0, netID])

    enrollments = []
    if "classes" in data:
        for c in data["classes"]:
            enrollments.append([netID, c['Course'], c['Sem'], c['Sem'], int(c['Rating'])])

    return student, enrollments, tracks

def get_schedule_statistics(net_id: str, semester: str, schedule_id: int, engine: MySQLEngine):
    """
    Gets the average GPA, average rating, total credits, number of interest classes, number of classes,
    and desired credits for a specified schedule.

    :param net_id: ...
    :param semester: Of format "FA20"
    :param schedule_id: ID of a unique schedule (as there can be multiple)
    :param engine: MYSQLEngine, used to retrieve information

    :return: average GPA, average rating, total credits, desired credits, number of interest classes, number of classes
    """
    match_rows_command = 'SELECT rowid\n' \
                            'FROM student_info.schedules\n' \
                            'WHERE schedules.net_id = "{}"\n' \
                            'AND schedules.semester = "{}"\n' \
                            'AND schedules.schedule_id = {}'.format(net_id, semester, schedule_id)

    res_rows = engine.wrapped_query(match_rows_command)
    res_data = []

    AVG_RATING = 'Average Rating'
    AVG_GPA = 'Average GPA'
    TOTAL_CREDITS = 'Total Credits'
    DESIRED_CREDITS = 'Desired Credits'
    NUM_CLASSES = 'Number of Classes'
    NUM_INTEREST_CLASSES = 'Number of classes of interest'
    
    for _, row in res_rows.iterrows():
        res_data.append(engine.stored_proc("schedule_statistics", list(row), 6)[0])

    res_df = pd.DataFrame(res_data, columns=[AVG_RATING, AVG_GPA, TOTAL_CREDITS, DESIRED_CREDITS, NUM_CLASSES, NUM_INTEREST_CLASSES])

    TOTAL_RATING = 'Total Rating'
    TOTAL_GPA = 'Total GPA'

    res_df[TOTAL_RATING] = res_df[AVG_RATING] * res_df[NUM_CLASSES]
    res_df[TOTAL_GPA] = res_df[AVG_GPA] * res_df[NUM_CLASSES]
    combined_weights = res_df.sum(axis=0)

    overall_avg_rating = combined_weights[TOTAL_RATING] / combined_weights[NUM_CLASSES]
    overall_avg_gpa = combined_weights[TOTAL_GPA] / combined_weights[NUM_CLASSES]
    overall_total_credits = combined_weights[TOTAL_CREDITS]
    overall_desired_credits = combined_weights[DESIRED_CREDITS]
    overall_num_classes = combined_weights[NUM_CLASSES]
    overall_num_interest_classes = combined_weights[NUM_INTEREST_CLASSES]

    return overall_avg_rating, overall_avg_gpa, overall_total_credits, \
            overall_desired_credits, overall_num_classes, overall_num_interest_classes
