import os
import ast
import json
import time

import pandas as pd
from flask import Flask, request, send_from_directory, jsonify, redirect, url_for
from flask_cors import CORS
from db.mysql_engine import * 
from server.api.data_util import * 

FIELD_NAME = 'field_name'
INTEREST = 'interest'
CREDIT_HOURS = 'credit_hours'
NET_ID = 'net_id'

app = Flask(__name__)
CORS(app)
engine = loadEngine()

@app.route('/submit', methods=['GET', 'POST'])
def submit_form(): 
    """ Submits survey data to SQL database. """
    if request.method == "POST":
        data = request.data
        if data:
            data = json.loads(data.decode("utf-8").replace("'",'"'))
            
            student, enrollments, tracks = processSurveyData(data)
            insert = 'INSERT INTO student_info.student (net_id, student_name, start_semester, current_semester,' \
                     'expected_graduation, total_semesters) VALUES("%s", "%s", "%s", "%s", "%s", %i)' % (student)
            insert += 'ON DUPLICATE KEY UPDATE student_name="%s", start_semester="%s", current_semester="%s", ' \
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

            return data
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
            data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid, 'student').to_dict()
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
            student_data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid, 'student').to_dict()
            enrollments_data = engine.wrapped_query('SELECT * FROM student_info.enrollments WHERE net_id = "%s"' % netid, 'enrollments').to_dict()
            track_data = engine.wrapped_query('SELECT * FROM student_info.track WHERE net_id = "%s"' % netid, 'track').to_dict()
            
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

@app.route('/login-request')
def login():
    """
    Validates login request.
    usage: /login-request?netid=<netid>
    """
    if request.method == "GET":
        netid = request.args['netid']
        if netid:
            data = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid, 'student').to_dict()
            response = jsonify({'userFound': len(data['net_id'])})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
    return 'Invalid Netid'

@app.route('/signup-request', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        data = request.data
        if data:
            data = json.loads(data.decode("utf-8").replace("'",'"'))
            # TODO: process data into student and insert into SQL database
            # note that we will have to retrieve semester info on signup
             
            curr_user_req = engine.wrapped_query('SELECT * FROM student_info.student WHERE net_id = "%s"' % netid, 'student').to_dict()

            if len(curr_user_req['net_id']):
                return "User exists already!"
            
            insert = 'INSERT INTO student_info.student (net_id, start_semester, current_semester, ' \
                     'total_semesters) VALUES("%s", "%s", "%s", %i)' % (student)
            engine.raw_operation(insert)

            return data
        return "Invalid input"
