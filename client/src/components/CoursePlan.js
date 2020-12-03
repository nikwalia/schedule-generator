import React, { useState, useEffect } from "react";
import { Header, List } from "semantic-ui-react";
import CourseTile from "./CourseTile.js";
import "bootstrap/dist/css/bootstrap.min.css";
import "./CoursePlan.css";
import Container from "react-bootstrap/Container";
import CourseModal from "./CourseModal.js";
import AddCourseModal from "./AddCourseModal.js";

var concentrations = require('../static/concentrations.json');
var userData = require('../static/sampleUserData.json')

 

export default function CoursePlan(props) {

    const [showModal, setShowModal] = useState(false); 
    const [showAddModal, setShowAddModal] = useState(false);

    const [currentCourse, setCurrentCourse] = useState("");
    const [removedCourses, setRemovedCourses] = useState([]);
    const [addedCourses, setAddedCourses] = useState({});

    const [currentSem, setCurrentSem] = useState("");

    const [refresh, setRefresh] = useState(false);
    const [coursework, setCoursework] = useState([]);
    const [courseInfo, setCourseInfo] = useState("");

    const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');

    const serverURL = process.env.REACT_APP_PROXY

 

    useEffect(() => {


        const requestOptions = {

                method: 'GET',

                headers: {

                  "Access-Control-Allow-Origin": "*"

                }

              };

              setNetid(localStorage.getItem('currentUser'));

              const response = fetch(serverURL + '/get-survey?netid=' + netid, requestOptions)

                .then(response => response.json())

                .then(data => {

                  if (data) {

                    createCoursesArray(data.enrollment); 

                  }

                })

                .catch(error => console.error('Error:', error));      

    }, []);

 

 

    async function getCourseInfo(courses) {

        const res = await fetch(serverURL + '/get-courses?courseid=' + courses,

        {

            method: 'GET',

            headers: {

                "Access-Control-Allow-Origin": "*"

            }

        })

          const json = await res.json();

          return json

      }

 

    function getCourseIds(enrollmentData) {

        var ids = []

 

        Object.keys(enrollmentData.course_id).forEach(function(idx) {

            ids.push(enrollmentData.course_id[idx])

        })

 

        return ids

    }

 

    function createCoursesArray(enrollmentData) {

        var coursework = []

        var ids = getCourseIds(enrollmentData)

        const courseInfo = getCourseInfo(ids)

        courseInfo.then((data) => {

            Object.keys(enrollmentData.course_id).forEach(function(idx) {

                var course;

                var courseData;

                var courseid = enrollmentData.course_id[idx]

                var semester = enrollmentData.semester[idx]

 

                for (var i = 0; i < data.length; i++) {

                    if (data[i]["n.courseId"] == courseid) {

                        course = {"id": courseid, "avgGpa": data[i]["n.GPA"], "rating": enrollmentData.rating[idx], "desc": data[i]["n.description"]}

                    }

                }
                var semExists = false

 

                coursework.forEach(function(entry) {

                    if (entry["sem"] == semester) {

                        entry["courses"].push(course)

                        semExists = true

                   }

                });

 

                if (!semExists) {

                    coursework.push({sem:semester, courses:[course]})

                }
            })

            setCoursework(coursework)
        });

        return [];

    }

 

  return (

    <div>

        <Container>           

            <Header as='h2' textAlign='center'>Coursework</Header>

            <List>

                {coursework.map(semester => {

                return (

                    <List.Item  key={semester.sem}>

                        <List.Content>

                            <h3>{semester.sem}</h3>

                            <List>

                                <Container id="grid-container">

                                {semester.courses.map(course => {

                                    return (

                                        <Container id="grid-box">

                                            <List.Item key={course.id}>

                                                <List.Content>

                                                    <CourseTile

                                                        sem={semester.sem}

                                                        course={course}

                                                        setShowModal={setShowModal}

                                                        setCurrentCourse={setCurrentCourse}

                                                        removedCourses={removedCourses}

                                                        setRemovedCourses={setRemovedCourses}

                                                        setRefresh={setRefresh}

                                                        refresh={refresh}

                                                    />

                                                </List.Content>

                                            </List.Item>

                                        </Container>

                                    );

                                })}

 

                                <Container id="grid-box"  onClick={() => {setCurrentSem(semester.sem); setShowAddModal(true)}}>

                                    <List.Item key={"ADD_A_COURSE"}>

                                        <List.Content>

                                            <CourseTile course={"ADD_A_COURSE"}/>

                                        </List.Content>

                                    </List.Item>

                                </Container>

                                </Container>

                            </List>

                        </List.Content>

                        <br></br>

                    </List.Item>                   

                );

                })}

            </List> 

            <button type="button" onClick={async () => {

              // get stored data

              const requestOptions = {

                method: 'GET',

                headers: {

                  "Access-Control-Allow-Origin": "*"

                }

              };

              setNetid(localStorage.getItem('currentUser'));

              const response = await fetch(serverURL + '/get-survey?netid=' + netid, requestOptions)

                .then(response => response.json())

                .then(data => {

                  if (data) {

                    createCoursesArray(data.enrollment); 

                  }

                })

                .catch(error => console.error('Error:', error));             

            }}>

            Save Changes

            </button>   

        </Container>

        { (showModal == true) &&

            <CourseModal setShowModal={setShowModal} course={currentCourse}/>

        }

        { (showAddModal == true) &&

            <AddCourseModal setRefresh={setRefresh} refresh={refresh} setShowAddModal={setShowAddModal} sem={currentSem}/>

        }

 

    </div>

  );

}