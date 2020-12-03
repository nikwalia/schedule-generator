import React, { useState, useEffect } from "react";

import "bootstrap/dist/css/bootstrap.min.css";

import "./CourseTileStyle.css";

import Button from "react-bootstrap/Button";

import Row from "react-bootstrap/Row";

import Col from "react-bootstrap/Col";

 

var concentrations = require('../static/concentrations.json');

var userData = require('../static/sampleUserData.json')

 

export default function CoursePlan(props) {

    const [showAddModal, setShowAddModal] = useState(false);

    const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');

    const serverURL = process.env.REACT_APP_PROXY

 

    async function removeCourse(course) {

      setNetid(localStorage.getItem('currentUser'));

      const requestOptions = {

        method: 'POST',

        body: JSON.stringify(netid + "," + course),

        headers: {

          "Access-Control-Allow-Origin": "*"

        }

      };

     

      await fetch(serverURL + '/remove-class', requestOptions)

          .then(response => console.log(response))

          .catch(error => console.error('Error:', error));

 

      alert('Submitted!')  

      }

 

    function isAlreadyRemoved(sem, course, removedCourses) {

        var currentSemCourses = removedCourses[sem];

        if (typeof currentSemCourses === "undefined") {

            return false;

        }

        return currentSemCourses.includes(course.id);

    }

   

    if (props.course === "ADD_A_COURSE") {

        return (

            <div class="course-box" id={props.course.id}>

                <div>

                    <h5>Add a class</h5>

                </div>

            </div>          

        )

    } else {

        return (

            <div class="course-box" id={props.course.id}>

                <div>

                    <h4>{props.course.id}</h4>

                    <p><b>Average GPA : </b> {props.course.avgGpa}</p>

                    <p><b>Course Rating : </b>{props.course.rating}</p>

                </div>

 

                <Row cols={2}>

                    <Col><Button onClick={() => {props.setShowModal(true); props.setCurrentCourse(props.course)}}>See Details</Button></Col>

                    <Col>

                        { isAlreadyRemoved(props.sem, props.course, props.removedCourses) &&

                            <Button disabled variant="warning">

                                Already removed

                            </Button>

                        }

 

                        { !isAlreadyRemoved(props.sem, props.course, props.removedCourses) &&

                            <Button onClick={() => {

                                removeCourse(props.course.id)

                                var newRemovedList = props.removedCourses[props.sem]; //.concat(props.course.id);

                                if (typeof newRemovedList === "undefined") {

                                    props.removedCourses[props.sem] = [props.course.id];

                                } else {

                                    newRemovedList = newRemovedList.concat(props.course.id);

                                    props.removedCourses[props.sem] = newRemovedList;

                                }

                                props.setRefresh(!props.refresh);

                            }}

                            variant="danger">

                                Remove

                            </Button>

                        }

                    </Col>

                </Row>               

            </div>

        )

    }

}