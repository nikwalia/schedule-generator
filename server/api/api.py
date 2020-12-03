import os
import ast
import json
import time
import ast

import pandas as pd
from flask import Flask, request, send_from_directory, jsonify, redirect, url_for, json
from flask_cors import CORS

from db.mysql_engine import * 
from db.neo4j_engine import *
from server.api.data_util import * 
from server.api.calculation_util import *
from model.train import direct_predict
from model.utils import load_checkpoint, setup_model

FIELD_NAME = 'field_name'
INTEREST = 'interest'
CREDIT_HOURS = 'credit_hours'
NET_ID = 'net_id'
MODELS_DIR = '../../saved_models'
CS_BS = 'Computer Science, BS'

app = Flask(__name__)
CORS(app)
engine = loadEngine()
neo4j_engine = loadNeo4JEngine()

def setup_models():
    models = {}
    for filename in os.listdir(MODELS_DIR):
        if filename.endswith('.pth'):
            # get model name from filename (remove last two portions)
            model_name = '-'.join(filename.split('-')[:len(filename.split('-')) - 2])
            models[model_name] = load_checkpoint(MODELS_DIR + '/' + filename)

    return models

models = setup_models() # UNCOMMENT

all_course_data = engine.wrapped_query('SELECT * FROM student_info.courses').to_dict()
# TODO: run this nightly?
all_enrollments_data = engine.wrapped_query('SELECT * FROM student_info.enrollments').to_dict()


'''===============
USER INFORMATION
==============='''

@app.route('/submit', methods=['GET', 'POST'])
def submit_form(): 
    """ Submits survey data to SQL database. """
    if request.method == "POST":
        data = request.data
        if data:
            data = json.loads(data.decode("utf-8").replace("'",'"'))
            student, enrollments, tracks = processSurveyData(data)

            insert = 'INSERT INTO student_info.student (net_id, student_name, pass_word, start_semester, current_semester,' \
                     'expected_graduation, total_semesters) VALUES("%s", "%s", "%s", "%s", "%s", "%s", %i)' % (student)
            insert += 'ON DUPLICATE KEY UPDATE student_name="%s", pass_word="%s", start_semester="%s", current_semester="%s", ' \
                      'expected_graduation="%s", total_semesters=%i' % tuple(student[1:])
            engine.raw_operation(insert)
            
            for e in enrollments:
                insert = 'INSERT INTO student_info.enrollments VALUES("%s", "%s", "%s", "%s", %i)' % tuple(e)
                insert += 'ON DUPLICATE KEY UPDATE semester="%s", semester_taken="%s", rating=%i' % tuple(e[2:])
                engine.raw_operation(insert)

            for t in tracks:
                insert = 'INSERT INTO student_info.track VALUES("%s", "%s", %i, "%s")' % tuple(t)
                insert += 'ON DUPLICATE KEY UPDATE interest = "{}", credit_hours={}'.format(t[1], t[2])
                engine.raw_operation(insert)

            if 'DeletedMajor' in data or 'DeletedMinor' in data:
                tracks_to_delete = data['DeletedMajor'] + data['DeletedMinor']
                for track in tracks_to_delete:
                    engine.drop_rows('DELETE FROM student_info.track WHERE \
                                track.net_id = "%s" AND track.field_name = "%s"' % (student[0], track))
                

            return 'Successful submission'
        return "Invalid input"


@app.route('/get-profile', methods=['GET'])
def get_profile():
    """
    Retrieves user profile from student table.
    usage: /get-profile?netid=<netid>
    """
    if request.method == "GET":
        netid = request.args['netid']
        if netid:
            student_data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid).to_dict()
            track_data = engine.wrapped_query('SELECT * FROM student_info.track WHERE net_id = "%s"' % netid).to_dict()

            minors = {FIELD_NAME: {}, INTEREST: {}, CREDIT_HOURS: {}, NET_ID: {}}
            majors = {FIELD_NAME: {}, INTEREST: {}, CREDIT_HOURS: {}, NET_ID: {}}
            minors_key = 0
            majors_key = 0

            # Iterate through entries in track_data (i.e. tracks)
            for i in range(len(track_data[FIELD_NAME])):
                # TODO: have this read from concentrations.json?
                if 'minor' in track_data[FIELD_NAME][i].lower() or ', b' not in track_data[FIELD_NAME][i].lower():
                    for key in track_data:
                        minors[key][minors_key] = track_data[key][i]
                    minors_key += 1
                else:
                    for key in track_data:
                        majors[key][majors_key] = track_data[key][i]
                    majors_key += 1

            

            response = jsonify({'student': student_data, 'majors': majors, 'minors': minors, 'tracks': track_data})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid"


@app.route('/get-survey', methods=['GET'])
def get_survey():
    """
    Retrieves user survey data via netid.
    usage: /get-survey?netid=<netid>
    """
    if request.method == "GET":
        netid = request.args['netid']
        if netid:
            # Retrieve all relevant data via netid
            student_data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid).to_dict()
            enrollments_data = engine.wrapped_query('SELECT * FROM student_info.enrollments WHERE net_id = "%s"' % netid).to_dict()
            track_data = engine.wrapped_query('SELECT * FROM student_info.track WHERE net_id = "%s"' % netid).to_dict()
            
            # Initialize empty structures for splitting track_data
            # TODO: make this thing a helper method
            minors = {FIELD_NAME: {}, INTEREST: {}, CREDIT_HOURS: {}, NET_ID: {}}
            majors = {FIELD_NAME: {}, INTEREST: {}, CREDIT_HOURS: {}, NET_ID: {}}
            minors_key = 0
            majors_key = 0

            # Iterate through entries in track_data (i.e. tracks)
            for i in range(len(track_data[FIELD_NAME])):
                # TODO: have this read from concentrations.json?
                if 'minor' in track_data[FIELD_NAME][i].lower() or ', b' not in track_data[FIELD_NAME][i].lower():
                    for key in track_data:
                        minors[key][minors_key] = track_data[key][i]
                    minors_key += 1
                else:
                    for key in track_data:
                        majors[key][majors_key] = track_data[key][i]
                    majors_key += 1
            
            # Recreate response data JSON
            response = jsonify({'student': student_data, 'enrollment': enrollments_data, 'majors': majors, 'minors': minors})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid"

@app.route('/get-schedules', methods=['GET'])
def get_schedule():
    if request.method == "GET":
        # print(request.args)
        netid = request.args['netid']

        if netid:
            semester = engine.wrapped_query('SELECT student.current_semester\n' \
                                                    'FROM student_info.student\n' \
                                                    'WHERE student.net_id = "{}"'.format(netid)).to_numpy().flatten()[0]
            
            schedule_ids = engine.wrapped_query("SELECT DISTINCT schedule_id\n" \
                                                    "FROM student_info.schedules\n" \
                                                    "WHERE schedules.net_id = '{}'\n" \
                                                    "AND schedules.semester = '{}'".format(netid, semester)).to_numpy().flatten()
            all_schedules = {}

            for schedule_id in schedule_ids:
                sub_schedules = engine.wrapped_query("SELECT schedule\n" \
                                                        "FROM student_info.schedules\n" \
                                                        "WHERE schedules.net_id = '{}'\n" \
                                                        "AND schedules.semester = '{}'\n" \
                                                        "AND schedules.schedule_id = {}".format(netid, semester, schedule_id))

                combined_schedule = []
                for schedule in sub_schedules.to_numpy().flatten():
                    combined_schedule.extend(ast.literal_eval(schedule)) 
            
                combined_schedule = list(set(combined_schedule))
                all_schedules[int(schedule_id)] = combined_schedule

            response = app.response_class(
                response = json.dumps(all_schedules),
                status=200,
                mimetype='application/json'
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid and/or schedule_id"


@app.route('/delete-profile', methods=['GET'])
def delete_profile():
    """
    Deletes user profile via netid.
    usage: /delete-profile?netid=<netid>
    """
    if request.method == "GET":
        netid = request.args['netid']
        if netid:
            for t in ["student", "track", "enrollments"]:
                engine.raw_operation('DELETE FROM student_info.%s WHERE net_id = "%s"' % (t, netid))
            response = jsonify({'deleted':'yes'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid"


@app.route('/login-request', methods=['GET'])
def login():
    """
    Validates login request.
    usage: /login-request?netid=<netid>&password=<password>
    """
    if request.method == "GET":
        netid = request.args['netid']
        password = request.args['password']
        if netid:
            data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s" AND pass_word = "%s"' % (netid, password)).to_dict()
            response = jsonify({'userFound': len(data['net_id'])})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return 'Invalid Netid'

'''===============
SCHEDULE INFORMATION
==============='''

def generate_ideal_schedule(courses_taken: list, track_data: list):
    '''
    Generates and returns the ideal schedule based on taken courses
    and field/interest/credit hour combinations.

    :param courses_taken: list of courses previously taken
    :param track_data: list of tuples of field/interest/credit_hours
    :returns: a list respresenting an ideal schedule
    '''
    # validate schedule with neo4j
    # note that we assume a person won't want to retake a class
    potential_courses = neo4j_engine.get_potential_classes(courses_taken)

    ideal_schedule = []
    for field, interest, credit_hours in track_data:
        # generate schedule distribution
        # TODO: change back to field/interest when more models/data are available
        # taken = schedule_to_interest_vector(courses_taken, engine, field, interest)
        taken, possible = schedule_to_interest_vector(courses_taken, engine, CS_BS)
        if not taken:
            continue
    
        distribution = direct_predict(models[CS_BS+'-General'], taken)
        class_data = [{"course_id": possible[i], "score": float(distribution[i])} 
                        for i in range(len(possible)) if possible[i] in potential_courses]
        class_data = json.dumps(class_data)

        # call stored proc
        # TODO: fill in with actual values
        # results = engine.stored_proc('score_classes', [class_data, credit_hours, interest], 2)
        schedule, score = engine.stored_proc('score_classes', [class_data, 15, CS_BS+'-General'], 2)[0]
        ideal_schedule += schedule.split(',')

    return ideal_schedule, score


def score_schedule(netid, semester, schedule_id):
    '''
    Returns a heuristic score of a schedule.

    :param netid: student netid
    :param semester: semester of schedule
    :param schedule_id: schedule id
    :returns: score of schedule
    '''
    # retrieve all previous semester's for a student
    student_data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid).to_dict()
    enrollments_data = engine.wrapped_query('SELECT * FROM student_info.enrollments WHERE net_id = "%s"' % netid).to_dict()
    track_data = engine.wrapped_query('SELECT * FROM student_info.track WHERE net_id = "%s"' % netid).to_dict()
    schedule_data = engine.wrapped_query('SELECT * FROM student_info.schedules WHERE net_id = "%s" AND semester = "%s" AND schedule_id = "%s"' % (netid, semester, schedule_id)).to_dict()

    # TODO: convert schedule_data into schedule
    schedule_df = pd.DataFrame(schedule_data)
    schedule = [inner for outer in list(schedule_df['schedule']) for inner in outer]

    # get interest field combinations from track table
    interests = [entry for entry in track_data['interest'].values()]
    fields = [entry for entry in track_data['field_name'].values()]
    credit_hours = [entry for entry in track_data['credit_hours'].values()]
    track_list = [(fields[i], interests[i], credit_hours[i]) for i in range(len(interests))]

    # get list of taken courses and all possible courses
    taken_courses = [entry for entry in enrollments_data['course_id'].values()]
    all_courses = [entry for entry in all_course_data['course_id'].values()]

    # generate ideal schedule and calculate nn score
    ideal_schedule, ideal_schedule_score = generate_ideal_schedule(taken_courses, track_list)
    ideal_schedule_vector = schedule_to_vector(ideal_schedule, all_courses)
    current_schedule_vector = schedule_to_vector(schedule, all_courses)

    # calculate variables for score formula
    nn_score = calculate_schedule_difference(ideal_schedule_vector, current_schedule_vector)

    avg_user_rating, avg_gpa, num_credit_hours, \
            num_credit_hours_desired, num_courses, num_interest_courses = get_schedule_statistics(netid, semester, schedule_id, engine)

    numerator = (avg_gpa + avg_user_rating + nn_score) * num_interest_courses
    denominator = abs(num_credit_hours - num_credit_hours_desired) * num_courses

    # normalize score
    return (numerator / denominator) / ideal_schedule_score


@app.route('/review-schedule', methods=['GET', 'POST'])
def review_schedule(): 
    """
    Reviews a schedule for a student.
    usage: /review-schedule
    """
    if request.method == "GET":
        netid = request.args['NetID']
        schedule_id = request.args['ScheduleID']
        semester = engine.wrapped_query(
                                        'SELECT student.current_semester\n' \
                                        'FROM student_info.student\n' \
                                        'WHERE student.net_id = "{}"'.format(netid)).to_numpy().flatten()[0]
        if netid and schedule_id and semester:
            # semester = engine.wrapped_query('SELECT student.current_semester\n' \
            #             'FROM student_info.student\n' \
            #             'WHERE student.net_id = "{}"'.format(netid)).to_numpy().flatten()[0]
            # data = json.loads(data.decode("utf-8").replace("'",'"'))
            # netid, semester, schedule_id = data['NetID'], data['Semester'], data['ScheduleID']
            # score schedule
            score = score_schedule(netid, semester, schedule_id)
            print(score)
            response = app.response_class(
                response=json.dumps({'score': score}),
                status=200,
                mimetype='application/json'
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid input"


@app.route('/get-ideal-schedule', methods=['GET'])
def get_ideal_schedule(): 
    """
    Retrieves ideal schedule for a student.
    usage: /get-ideal-schedule?netid=<netid>
    """
    if request.method == "GET":
        netid = request.args['netid']
        if netid:
            # get current student data
            enrollments_data = engine.wrapped_query('SELECT * FROM student_info.enrollments WHERE net_id = "%s"' % netid).to_dict()
            track_data = engine.wrapped_query('SELECT * FROM student_info.track WHERE net_id = "%s"' % netid).to_dict()

            taken_courses = [entry for entry in enrollments_data['course_id'].values()]
            interests = [entry for entry in track_data['interest'].values()]
            fields = [entry for entry in track_data['field_name'].values()]
            credit_hours = [entry for entry in track_data['credit_hours'].values()]
            track_list = [(fields[i], interests[i], credit_hours[i]) for i in range(len(interests))]
            
            # return ideal schedule
            ideal_schedule, _ = generate_ideal_schedule(taken_courses, track_list)
            response = app.response_class(
                response=json.dumps({'schedule': ideal_schedule}),
                status=200,
                mimetype='application/json'
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid"

@app.route('/add-schedule', methods=['GET', 'POST'])
def add_schedule():
    """
    Adds a schedule to the database, splitting it up into its different streams
    """
    if request.method == 'POST':
        data = request.data
        if data:            
            data = json.loads(data.decode("utf-8").replace("'",'"'))
            net_id = data['NetID']
            schedule_id = int(data['ScheduleID'])

            user_track_info = engine.wrapped_query(
                                        'SELECT CONCAT(track.field_name, "-", track.interest) AS tag\n' \
                                        'FROM student_info.track\n' \
                                        'WHERE track.net_id = "{}"'.format(net_id))

            semester = engine.wrapped_query(
                                        'SELECT student.current_semester\n' \
                                        'FROM student_info.student\n' \
                                        'WHERE student.net_id = "{}"'.format(net_id)).to_numpy().flatten()[0]

            with open('../../db/static/track_data.json', 'r') as f:
                all_track_info = json.load(f)

            schedule_res = []
            classes = set(data['classes'])
            for _, track in user_track_info.iterrows():
                track_string = track.to_numpy().flatten()[0]
                match_classes = classes & set(all_track_info[track_string])
                schedule_res.append((0, net_id, semester, track_string.split('-')[0], track_string.split('-')[-1], schedule_id, str(list(match_classes)).replace("'", '"')))
                classes = classes - match_classes

                if len(classes) == 0:
                    break
            
            df = pd.DataFrame(schedule_res, columns=['rowid', 'net_id', 'semester', 'field_name', 'interest', 'schedule_id', 'schedule'])
            engine.insert_df(df, "schedules")
            
            return 'Successful submission'
        return "Invalid input"

'''===============
COURSE INFORMATION
==============='''

@app.route('/get-valid-courses', methods=['GET'])
def get_valid_courses():
    """
    Retrieves valid course for a student.
    usage: /get-valid-courses?netid=<netid>
    """
    if request.method == "GET":
        netid = request.args['netid']
        if netid:
            # Get class node from cypher query
            enrollments_data = engine.wrapped_query('SELECT * FROM student_info.enrollments WHERE net_id = "%s"' % netid).to_dict()
            courses_taken = [entry for entry in enrollments_data['course_id'].values()]
            data = neo4j_engine.get_potential_classes(courses_taken)

            data = data.extend(courses_taken)
            
            response = app.response_class(
                response=json.dumps({'valid_classes': data}),
                status=200,
                mimetype='application/json'
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid"


@app.route('/get-subsequent-courses', methods=['GET'])
def get_subsequent_courses():
    """
    Retrieves valid course for a student.
    usage: /get-subsequent-coursess?course=<course>
    """
    if request.method == "GET":
        course = request.args['courseid']
        if course:
            # Get class node from cypher query
            data = neo4j_engine.get_subsequent_classes(course)
            data = [item[0] for item in data]
            # data = [item for sublist in data for item in sublist]
            
            response = app.response_class(
                response=json.dumps({'subsequent_classes': data}),
                status=200,
                mimetype='application/json'
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid course"


@app.route('/get-course', methods=['GET'])
def get_course():
    """
    Retrieves course and details based on input.
    usage: /get-course?courseid=<courseid>
    """
    if request.method == "GET":
        courseid = request.args['courseid']
        if courseid:
            # Get class node from cypher query
            try:
                data = neo4j_engine.wrapped_query('MATCH (p: Class {courseId: "%s"}) RETURN p' % courseid)[0]['p']
                course_dict = {key : data[key] for key in data.keys()}
                
                subsequent = neo4j_engine.get_subsequent_classes(courseid)
                subsequent = [item[0] for item in subsequent]
                course_dict['subsequent_classes'] = subsequent 

                response = app.response_class(
                    response=json.dumps({'course': course_dict}['course']),
                    status=200,
                    mimetype='application/json'
                )
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            except IndexError:
                return 'Invalid course'
        return "Invalid netid"


@app.route('/get-all-courses', methods=['GET'])
def get_all_courses():
    """
    Retrieves an array of courses
    usage: /get-all-courses
    """
    if request.method == "GET":
        data = [entry for entry in all_course_data['course_id'].values()]
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/get-courses', methods=['GET'])

def get_courses():

    """

    Retrieves courses and details based on input.

    usage: /get-courses?courseid=<courseids>

    """

    if request.method == "GET":

        courseids = request.args['courseid'].split(",")

        if courseids:

            # Get class nodes from cypher query

            courseidString = '","'.join(courseids)

            q = 'MATCH (n) WHERE n.courseId IN ["%s"] RETURN n.courseId, n.GPA, n.description' % courseidString

            data = neo4j_engine.wrapped_query(q)[:len(courseids)]

           

            response = app.response_class(

                response=json.dumps(data),

                status=200,

                mimetype='application/json'

            )

            response.headers.add('Access-Control-Allow-Origin', '*')

            return response

        return "Invalid netid"

 

@app.route('/add-classes', methods=['GET', 'POST'])

def add_classes():

    """ Submits added course (from course plan) to SQL database. """

    if request.method == "POST":

        data = request.data

        if data:

            data = json.loads(data.decode("utf-8").replace("'",'"')).split(",")

            netid, sem, rating, classes = data[0], data[1], int(data[2]), data[3:]

            for c in classes:

                #get rating and sem taken

                insert = 'INSERT INTO student_info.enrollments VALUES("%s", "%s", "%s", "%s", %i)' % (netid, c, sem, sem, rating)

                insert += 'ON DUPLICATE KEY UPDATE semester="%s", rating=%i' % (sem, 0)

                engine.raw_operation(insert)

        return "Invalid input"

 

@app.route('/remove-class', methods=['GET', 'POST'])

def remove_class():

    """ Removes course (from course plan) to SQL database. """

    if request.method == "POST":

        data = request.data

        if data:

            data = json.loads(data.decode("utf-8").replace("'",'"')).split(",")

            netid, course = data[0], data[1]

            engine.raw_operation('DELETE FROM student_info.enrollments WHERE net_id = "%s" AND course_id = "%s"' % (netid, course))

        return "Invalid input"

@app.route('/remove-schedule', methods=['GET', 'POST'])

def remove_schedule():

    """ Removes schedule from user-generated schedules. """

    if request.method == "POST":

        data = request.data

        if data:

            data = json.loads(data.decode("utf-8").replace("'",'"')).split(",")

            netid, scheduleid = data[0], data[1]

            engine.raw_operation('DELETE FROM student_info.schedules WHERE net_id = "%s" AND schedule_id = "%s"' % (netid, scheduleid))

        return "Invalid input"