import os
import ast
import json
import time

import pandas as pd
from flask import Flask, request, send_from_directory, jsonify, redirect, url_for, json
from flask_cors import CORS
from db.mysql_engine import * 
from db.neo4j_engine import *
from server.api.data_util import * 

FIELD_NAME = 'field_name'
INTEREST = 'interest'
CREDIT_HOURS = 'credit_hours'
NET_ID = 'net_id'

app = Flask(__name__)
CORS(app)
engine = loadEngine()
neo4j_engine = loadNeo4JEngine()

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
                insert += 'ON DUPLICATE KEY UPDATE credit_hours=%i' % t[2]
                engine.raw_operation(insert)

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
            data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid).to_dict()
            response = jsonify(data)
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
            data = neo4j_engine.wrapped_query('MATCH (p: Class {courseId: "%s"}) RETURN p' % courseid)[0]['p']
            course_dict = {key : data[key] for key in data.keys()}
            
            response = app.response_class(
                response=json.dumps({'course': course_dict}['course']),
                status=200,
                mimetype='application/json'
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        return "Invalid netid"

@app.route('/get-all-courses', methods=['GET'])
def get_all_courses():
    """
    Retrieves an array of courses
    usage: /get-all-courses
    """
    if request.method == "GET":
        data = engine.wrapped_query('SELECT * FROM student_info.courses').to_dict()
        data = [entry for entry in data['course_id'].values()]
        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

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
            schedule_id = data['ScheduleID']

            user_track_info = engine.wrapped_query(
                                        "SELECT CONCAT(track.field_name, track.interest) AS tag\n" \
                                        "FROM student_info.track\n" \
                                        "WHERE track.net_id = {}".format(net_id))

            semester = engine.wrapped_query(
                                        "SELECT student.current_semester\n" \
                                        "FROM student_info.student\n" \
                                        "WHERE student.net_id = {}".format(net_id))

            with open('../../db/static/track_data.json', 'r') as f:
                all_track_info = json.load(f)

            schedule_res = []
            classes = set(data['classes'])
            for track in user_track_info:
                match_classes = classes & set(all_track_info[track])
                schedule_res.append((net_id, semester, track.split('-')[0], track.split('-')[-1], schedule_id, str(list(match_classes))))
                classes = classes - match_classes

                if len(classes) == 0:
                    break
            
            df = pd.DataFrame(columns=['net_id', 'semester', 'field_name', 'interest', 'schedule_id', 'schedule'], schedule_res)
            engine.insert_df(df)
            
            return 'Successful submission'
        return "Invalid input"
