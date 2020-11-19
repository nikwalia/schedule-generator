import React, { useState, useEffect } from "react";
import Row from 'react-bootstrap/Row'; 

import { Formik, Field, Form, FieldArray } from 'formik';
import * as Yup from 'yup';

import Button from "react-bootstrap/Button";
import { Typeahead } from 'react-bootstrap-typeahead';

import "bootstrap/dist/css/bootstrap.min.css";
import 'react-bootstrap-typeahead/css/Typeahead.css';
import "./SurveyStyle.css"

const SPRING_SEM = "SP";
const SUBMITTED = "submitted";

function convertSem(sem) {
  if (sem.slice(0,SPRING_SEM.length) === SPRING_SEM) {
    return sem.slice(SPRING_SEM.length) * 2;
  } else {
    return sem.slice(SPRING_SEM.length) * 2 + 1;
  }
}

function semGreaterThan(sem1, sem2) {
  return convertSem(sem1) >= convertSem(sem2);
}

const SurveySchema = Yup.object().shape({
  Name: Yup.string()
      .min(2, "Too Short!")
      .max(40, "Too Long!")
      .matches(/^[\w'\-,.][^0-9_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$/, 'Invalid characters entered')
      .required('Required'),
  Password: Yup.string()
      .min(10, "Password should be 10 characters minimum.")
      .max(30, "Password is too long!")
      .nullable(),
  NetID: Yup.string()
      .required('Required')
      .min(2, "NetID is too short!")
      .max(8, "NetID is too long!")
      .matches(/^[\w'\-,.][^_!¡?÷?¿/\\+=@#$%ˆ&*(){}|~<>;:[\]]{2,}$/, 'Invalid characters entered'),
  CurrentSem: Yup.string()
      .required('Required')
      .max(4, "Current semester is not in the correct format!")
      .matches(/(?:FA|SP)(?:1[0-9]|2[0-2])/ , 'Current semester is not in the correct format!')
      .test('test-compare semesters', 'Current semester not between start and end semesters',
        function(value) {
          
          if (!this.resolve(Yup.ref("EndingSem")) || !this.resolve(Yup.ref("StartingSem")) || !this.resolve(Yup.ref("EndingSem"))) return true;
          return semGreaterThan(this.resolve(Yup.ref("CurrentSem")), this.resolve(Yup.ref("StartingSem"))) &&
          semGreaterThan(this.resolve(Yup.ref("EndingSem")), this.resolve(Yup.ref("CurrentSem")));
        }),
  StartingSem: Yup.string()
      .required('Required')
      .max(4, "Current semester is not in the correct format!")
      .matches(/(?:FA|SP)(?:1[0-9]|2[0-2])/ , 'Start semester is not in the correct format!'),
  EndingSem: Yup.string() 
      .required('Required')
      .max(4, "Current semester is not in the correct format!")
      .matches(/(?:FA|SP)(?:1[0-9]|2[0-9])/ , 'End semester is not in the correct format!')
      .test('test-compare semesters', 'Start semester not before ending semester',
        function(value) {
          
          if (!this.resolve(Yup.ref("EndingSem")) || !this.resolve(Yup.ref("StartingSem"))) return true;
          return semGreaterThan(this.resolve(Yup.ref("EndingSem")), this.resolve(Yup.ref("StartingSem")));
        }),
  Majors: Yup.string()
        .required('Required'),
  classes: Yup.array().of(
    Yup.object().shape({
      Course: Yup.string()
          .required('Required')
          .matches(/[A-Z]{2,5}\s\d{3}/, "Invalid course format.")
          .test('valid course', 'Invalid course title', 
            function(value) {
              return localStorage.getItem('courseList').includes(value); 
            }),
      Sem: Yup.string()
          .required('Required')
          .matches(/(?:FA|SP)(?:1[0-9]|2[0-2])/ , 'Semester is not in the correct format')
          .test('test-compare semesters', 'Semester not between start and end semesters',
            function(value) {
              if (!this.resolve(Yup.ref("EndingSem")) || !this.resolve(Yup.ref("StartingSem"))) return true;
              return semGreaterThan(this.resolve(Yup.ref("CurrentSem")), this.resolve(Yup.ref("StartingSem"))) &&
              semGreaterThan(this.resolve(Yup.ref("EndingSem")), this.resolve(Yup.ref("CurrentSem")));
            }),
      Rating: Yup.number() 
          .required('Required')
          .integer('Rating must be an integer from 1-10') 
          .min(1, "Rating not in range")
          .max(10, "Rating not in range"),
    })
  )
  
});

var concentrations = require('../static/concentrations.json');
const serverURL = process.env.REACT_APP_PROXY

export default function Survey(props) {
  const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');
  const [majors, setMajors] = useState(concentrations['majors']);
  const [minors, setMinors] = useState(concentrations['minors']);

  const [classArr, setClassArr] = useState([]);
  const [selectedMajors, setSelectedMajors] = useState([]);
  const [selectedMinors, setSelectedMinors] = useState([]);

  const [courseList, setCourseList] = useState(localStorage.getItem('courseList') || []);
  const [responseData, setResponseData] = useState('');

  function getMajors(majorData) {
    // Converts response data to list of majors/minors
    var majors = [] ;
    Object.keys(majorData['field_name']).forEach(function(idx) {
      majors.push(majorData['field_name'][idx]);
    });
    return majors; 
  }

  function getClassArr(enrollmentData) {
    // Converts response data to list of disctionaries for Formik
    var classesArr = [];
    Object.keys(enrollmentData['course_id']).forEach(function(idx) {
      let courseItem = {'Course': enrollmentData['course_id'][idx], 'Sem': enrollmentData['semester'][idx], 'Rating': enrollmentData['rating'][idx]};
      classesArr.push(courseItem);
    });
    return classesArr;
  }

  function filterBy(option, courseId) {
    // Applies filter for removing options
    if (courseId.selected.length) {
      return true;
    }
    return option.toLowerCase().indexOf(courseId.text.toLowerCase()) > -1;
  }

  function getCoursesError(errorArray) {
    var errorStr = "*Please fix the following errors* "; 

    if (errorArray["Course"]) {
      errorStr += "Course: " + errorArray["Course"] + ", "; 
    }
    if (errorArray["Sem"]) {
      errorStr += " Semester: " + errorArray["Sem"] + ", "; 
    }
    if (errorArray["Rating"]) {
      errorStr += " Rating: " + errorArray["Rating"] + ", "; 
    }

    return errorStr; 
  }

  const ToggleButton = ({ isOpen, onClick }) => (
    <button
      className="toggle-button"
      onClick={onClick}
      onMouseDown={e => {
        // Prevent input from losing focus.
        e.preventDefault();
      }}>
      {isOpen ? '▲' : '▼'}
    </button>
  );

  useEffect(() => {
  
    // If nothing in cached courseList, retrieve list of courses
    if (courseList.length == 0) {
      fetch(serverURL + '/get-all-courses',
      {
          method: 'GET',
          headers: {
              "Access-Control-Allow-Origin": "*"
          }
      })
      .then(response => response.json())
      .then(data => {
        setCourseList(data);
        localStorage.setItem('courseList', data);
      });
    }
    
    // Prevent resubmission if a form has already been submitted
    setNetid(localStorage.getItem('currentUser'));
    if (netid == SUBMITTED) {
      alert("You've already submitted a form. You won't be able to submit again!");
    } else if (netid) {
      // Autofill in survey entries based on cached netid
      const requestOptions = {
        method: 'GET',
        headers: {
          "Access-Control-Allow-Origin": "*"
        }
      };
      fetch(serverURL + '/get-survey?netid=' + netid, requestOptions)
        .then(response => response.json())
        .then(data => {
          setResponseData(data);
          setSelectedMajors(getMajors(data.majors));
          setSelectedMinors(getMajors(data.minors));
          setClassArr(getClassArr(data.enrollment));
          console.log(data)
        })
        .catch(error => console.error('Error:', error));
    }
    
  }, []);

  return (
    <div id="form-container">
      <h1>Survey</h1>
      <Formik
        initialValues={{
            Name: responseData ? responseData.student.student_name[0] : '',
            Password: null,
            NetID: netid,
            CurrentSem: responseData ?  responseData.student.current_semester[0] : '', 
            StartingSem: responseData ? responseData.student.start_semester[0] : '',
            EndingSem: responseData ? responseData.student.expected_graduation[0] : '', 
            Majors: responseData ? getMajors(responseData.majors) : '', 
            Minors: responseData ? getMajors(responseData.minors) : '',
            classes: responseData ? classArr : '',
        }}
        enableReinitialize={true}
        validationSchema={SurveySchema}
        onSubmit={async (values) => {
            console.log('Submitting survey.');

            if (netid != SUBMITTED) {
              const requestOptions = {
                method: 'POST',
                // headers: {
                //   'Access-Control-Allow-Origin': '*',
                //   'Referrer-Policy': 'origin-when-cross-origin'
                // },
                mode: 'no-cors',
                body: JSON.stringify(values)
              };

              const response = await fetch(serverURL + '/submit', requestOptions)
                  .then(response => console.log(response))
                  .catch(error => console.error('Error:', error));

              alert('Submitted!')
            }
            
            if (values.Password) {
              localStorage.setItem('currentUser', values.NetID);
            } else if (!localStorage.getItem('currentUser')) {
              localStorage.setItem('currentUser', SUBMITTED);
            }
        }}
      > 
      {({ errors, touched, values, setFieldValue }) => (
        <Form>
            <label htmlFor="NetID">NetID: </label>
            <Field id="NetID" name="NetID" placeholder="jdoe8" /> 
            {errors.NetID && touched.NetID ? (<div style={{color: "red"}}>{errors.NetID}</div>) : null}
            <br />

            <label htmlFor="Password">Password (Optional): </label>
            <Field id="Password" type="password" name="Password"/> 
            {errors.Password && touched.Password ? (<div style={{color: "red"}}>{errors.Password}</div>) : null}
            <br />

            <label htmlFor="Name">Name (First and Last): </label>
            <Field id="Name" name="Name" placeholder="Jane Doe"/> 
            {errors.Name && touched.Name ? (<div style={{color: "red"}}>{errors.Name}</div>) : null}
            <br />            

            <label htmlFor="CurrentSem">Current Semester: </label>
            <Field id="CurrentSem" name="CurrentSem" placeholder="e.g. SP20"/> 
            {errors.CurrentSem && touched.CurrentSem ? (<div style={{color: "red"}}>{errors.CurrentSem}</div>) : null}
            <br />

            <label htmlFor="StartingSem">Starting Semester: </label>
            <Field id="StartingSem" name="StartingSem" placeholder="e.g. FA19"/> 
            {errors.StartingSem && touched.StartingSem ? (<div style={{color: "red"}}>{errors.StartingSem}</div>) : null}
            <br />

            <label htmlFor="Majors">Majors: </label>
            <Typeahead
                multiple={true}
                filterBy={filterBy}
                id="major-lookup"
                options={majors}
                selected={selectedMajors}
                onChange={(selected) => {
                  setFieldValue("Majors", selected)
                  setSelectedMajors(selected);
                }}
                placeholder="Select your majors...">
                {({ isMenuShown, toggleMenu }) => (
                <ToggleButton isOpen={isMenuShown} onClick={e => toggleMenu()} />
                )}
            </Typeahead>
            {errors.Majors && touched.Majors ? (<div style={{color: "red"}}>{errors.Majors}</div>) : null}

            <br />
            <br />

            <label htmlFor="Minors">Minors: </label>
            <Typeahead
                multiple={true}
                filterBy={filterBy}
                id="minor-lookup"
                options={minors}
                selected={selectedMinors}
                onChange={(selected) => {
                  setFieldValue("Minors", selected);
                  setSelectedMinors(selected);
                }}
                placeholder="Select your minors...">
                {({ isMenuShown, toggleMenu }) => (
                <ToggleButton isOpen={isMenuShown} onClick={e => toggleMenu()} />
                )}
            </Typeahead>
            <br /> 
            <br />

            <label htmlFor="EndingSem">Ending Semester: </label>
            <Field id="EndingSem" name="EndingSem" placeholder="e.g. SP23"/> 
            {errors.EndingSem && touched.EndingSem ? (<div style={{color: "red"}}>{errors.EndingSem}</div>) : null}
            <br />

            <p>Please enter your classes below. For each class, you can indicate the course ID (e.g. CS 411), 
               semester you took it in (e.g. "FA20"), and rating 1-10 (1 being the worst).</p>

            <FieldArray
             name="classes"
             render={arrayHelpers => (
               <div>
                 {values.classes && values.classes.length > 0 ? (
                    values.classes.map((friend, index) => (
                     <div key={index}>
                     <br />
                       <Row lg={3}>
                       <Field name={`classes.${index}.Course`} placeholder="CourseID (e.g. CS 411)" id="Course"/> 
                       <Field name={`classes.${index}.Sem`} placeholder="Semester (e.g. FA20)" id="Sem"/>
                       <Field name={`classes.${index}.Rating`} placeholder="Rating (e.g. 10)" id="Rating"/>

                       {index == values.classes.length-1 ? (
                         <div>
                          <button
                            type="button"
                            onClick={() => arrayHelpers.remove(index)}
                          > - </button>
                          <button
                            type="button"
                            onClick={() => {arrayHelpers.insert(index+1, '')}}
                          > + </button>
                        </div>
                       ) : (<div></div>)}       

                      </Row>
                      <div style={{color: "red"}}>{errors && errors.classes && errors.classes[index] && getCoursesError(errors.classes[index])}</div>
                     </div>
                   ))
                 ) : (
                   <button type="button" onClick={() => arrayHelpers.push('')}>
                     Add a class
                   </button>
                   
                 )}
                 
               </div>
             )}
           />
            <br />
            <Button type="submit">Submit</Button>
        </Form>
      )}
      </Formik>
    </div>
  );
}
