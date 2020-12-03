import numpy as np

GENERAL = '-General'

def calculate_avg_gpa(schedule: list, course_information: dict):
    '''
    Calculates average GPA of a schedule based on historic GPA data

    :param schedule: list of courses being taken
    :param course_information: all course information from catalog
    :returns: average gpa for courses in schedule
    '''
    courses = [entry for entry in course_information['course_id'].values()]

    gpa = 0
    for course in schedule:
        idx = courses.index(course)
        gpa += course_information['gpa'][idx]

    return gpa / len(schedule) if len(schedule) else 0


def calculate_avg_user_rating(schedule: list, enrollments_data: dict):
    '''
    Calculates average rating of courses in schedule based on feedback from students

    :param schedule: list of courses being taken
    :param enrollments_data: all enrollments data
    :returns: average user rating for courses in schedule
    '''
    enrollments = [entry for entry in enrollments_data['course_id'].values()]
    
    rating = 0
    for course in schedule:
        indices = [i for i, x in enumerate(enrollments) if course in x]
        course_rating = 0

        for idx in indices:
            course_rating += enrollments['rating'][idx]
        rating += course_rating / len(indices)

    return rating / len(schedule) if len(schedule) else 0


def calculate_credit_hours(schedule: list, course_information: dict):
    '''
    Calculates number of credit hours in a schedule

    :param schedule: list of courses being taken
    :param course_information: all course information from catalog
    :returns: credit hours in schedule
    '''
    courses = [entry for entry in course_information['course_id'].values()]
    
    credit_hours = 0
    for course in schedule:
        idx = courses.index(course)
        credit_hours += course_information['credits'][idx]

    return credit_hours


def get_number_interesting_courses(schedule: list, engine, fields_interest: list):
    
    num_interesting = 0
    interesting_potential_classes = []
    for field, interest in fields_interest:
        classes = engine.wrapped_query(
            "SELECT course_id " \
            "FROM student_info.courses " \
            "WHERE interest LIKE '%%{}%%'".format(field + interest))
        classes = [c[0] for c in classes if c not in interesting_potential_classes]
        interesting_potential_classes.extend(classes)
    
    for course in schedule:
        if course in interesting_potential_classes:
            num_interesting += 1
    
    return num_interesting


def schedule_to_interest_vector(schedule: list, engine, field_name: str, interest: str = None):
    '''
    Converts a schedule to a vectorized format based on an interest.

    :param schedule: list of courses being taken
    :param engine: SQL engine
    :param field_name: name of major/minor in question
    :param interest: interest in question
    :returns: vectorized schedule based on interest/field and list of courses possible
    '''
    classes = []
    if interest:
        classes = engine.wrapped_query(
            "SELECT course_id " \
            "FROM student_info.courses " \
            "WHERE interest LIKE '%%{}%%'".format(field_name + interest))
        classes = classes['course_id'].unique()
    else:
        classes = engine.wrapped_query(
            "SELECT course_id " \
            "FROM student_info.courses " \
            "WHERE interest LIKE '%%{}%%'".format(field_name + GENERAL))
        classes = classes['course_id'].unique()

    # generate model inputs
    return schedule_to_vector(schedule, classes), classes


def schedule_to_vector(schedule: list, possible_courses: list):
    '''
    Converts a schedule to a vectorized format.

    :param schedule: list of courses being taken
    :param possible_courses: list of courses to vectorize based on
    :returns: vectorized schedule based on interest/field
    '''
    # generate model inputs
    taken_classes = [0] * len(possible_courses)
    for i, c in enumerate(possible_courses):
        if c in schedule:
            taken_classes[i] = 1

    return taken_classes


def calculate_schedule_difference(schedule1: list, schedule2: list):
    '''
    Calculates distance between schedules (currently uses Euclidian distance)

    :param schedule1: vector of courses in schedule 1
    :param schedule2: vector of courses in schedule 2
    :returns: Euclidian distance between schedules
    '''
    return np.linalg.norm(np.array(schedule1) - np.array(schedule2))
