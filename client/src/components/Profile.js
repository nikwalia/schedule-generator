import React, { useState, useEffect } from "react";
import Row from 'react-bootstrap/Row'; 

import { Formik, Field, Form, FieldArray } from 'formik';
import * as Yup from 'yup';

import Button from "react-bootstrap/Button";
import { Typeahead } from 'react-bootstrap-typeahead';

import "bootstrap/dist/css/bootstrap.min.css";
import 'react-bootstrap-typeahead/css/Typeahead.css';
import "./ProfileStyle.css"


const serverURL = process.env.REACT_APP_PROXY
const sampleInterests = require('../static/sampleTracks.json')

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
      Interest_Name: Yup.string(), 
      Credit_Hours: Yup.number('Credit hours must be an integer')
    })
  )
});

var concentrations = require('../static/concentrations.json');

export default function Profile(props) {
  // TODO: update pwd function
  const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');
  // For all majors
  const [majors, setMajors] = useState(concentrations['majors']);
  const [minors, setMinors] = useState(concentrations['minors']);

  // User selected Majors
  const [selectedMajors, setSelectedMajors] = useState([]);
  const [selectedMinors, setSelectedMinors] = useState([]);

  // Majors being removed
  const [removedMajors, setRemovedMajors] = useState([]);
  const [removedMinors, setRemovedMinors] = useState([]);

  const [responseData, setResponseData] = useState('');

  const [selectedInterests, setSelectedInterests] = useState([]); 

  function logout() {
    localStorage.clear();
    window.location.reload();
  }

  function getMajors(majorData) {
    // Converts response data to list of majors/minors
    var majors = [] ;
    Object.keys(majorData['field_name']).forEach(function(idx) {
      majors.push(majorData['field_name'][idx]);
    });
    return majors; 
  }

  function getCoursesError(errorArray) {
    var errorStr = "Please fix the following errors "; 

    if (errorArray["Interest_Name"]) {
      errorStr += "Interest_Name: " + errorArray["InterestName"] + ", "; 
    }
    if (errorArray["Credit_Hours"]) {
      errorStr += " Credit Hours: " + errorArray["Credit_Hours"] + ", "; 
    }

    return errorStr; 
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

  function generateEmptyInterests(tracks) {
    // for each field, add (field_name, interest, credit_hrs) to an array
    var interests = []; 

    Object.keys(tracks.credit_hours).forEach(function(idx) {
      let row = {'field_name': tracks.field_name[idx], 'interest': tracks.interest[idx], 'credit_hrs': tracks.credit_hours[idx]}
      interests.push(row)
    }); 

    return interests; 
  }

  function getInterestError(errorArray) {
    var errorStr = "Please fix the following errors "; 

    if (errorArray["Interest_Name"]) {
      errorStr += "Interest: " + errorArray["Interest_Name"] + ", "; 
    }
    if (errorArray["Credit_Hours"]) {
      errorStr += " Credit Hours: " + errorArray["Credit_Hours"] + ", "; 
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
    setNetid(localStorage.getItem('currentUser'));
    if (netid) {
      fetch(serverURL + '/get-profile?netid=' + netid,
        {
            method: 'GET',
            headers: {
              "Access-Control-Allow-Origin": "*"
            }
        })
        .then(response => response.json())
        .then(data => {setResponseData(data); 
          setSelectedMajors(getMajors(data.majors));
          setSelectedMinors(getMajors(data.minors));
        });
    }    
  }, []);

  return (
    <div id="form-container">
      <h1>Profile</h1>
      <Formik
        initialValues={{
            Name: responseData ? responseData.student.student_name["0"] : '',
            Password: responseData ? responseData.student.pass_word["0"] : '',
            NetID: netid,
            CurrentSem: responseData ?  responseData.student.current_semester["0"] : '', 
            StartingSem: responseData ? responseData.student.start_semester["0"] : '',
            EndingSem: responseData ? responseData.student.expected_graduation["0"] : '', 
            Majors: responseData ? getMajors(responseData.majors) : '', 
            Minors: responseData ? getMajors(responseData.minors) : '', 
            interests: responseData ? generateEmptyInterests(responseData.tracks) : '',
        }} // generateEmptyInterests(netid, getMajors(responseData.majors), getMajors(responseData.minors))
        enableReinitialize={true}
        validationSchema={SurveySchema}
        onSubmit={async (values) => {
            values['DeletedMajor'] = removedMajors;
            values['DeletedMinor'] = removedMinors;

            values.Majors.forEach(element => element.trim());
            values.Minors.forEach(element => element.trim());

            console.log(values);

            if (netid !== SUBMITTED) {
              const requestOptions = {
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify(values)
              };

              await fetch(serverURL + '/submit', requestOptions)
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

            <label htmlFor="Password">Password: </label>
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
                  if (selected.length < selectedMajors.length) {
                    var temp = [...removedMajors, ...selectedMajors.filter(x => selected.indexOf(x) === -1)];
                    setRemovedMajors(temp);
                  }
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
                  if (selected.length < selectedMinors.length) {
                    var temp = [...removedMinors, ...selectedMinors.filter(x => selected.indexOf(x) === -1)];
                    setRemovedMinors(temp);
                  }
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

            <p>Add any interests below.</p>

            <FieldArray
             name="interests"
             render={arrayHelpers => (
               <div>
                 {values.interests && values.interests.length > 0 ? (
                    values.interests.map((friend, index) => (
                     <div key={index}>
                     <br />
                       <Row lg={3}>
                        <p>{values.interests[index].field_name}</p>
                        <Typeahead
                          multiple={false}
                          name={`interests.${index}.Interest_Name`}
                          filterBy={filterBy}
                          id="Interest_Name"
                          options={sampleInterests[values.interests[index].field_name] ? sampleInterests[values.interests[index].field_name] : ['General']}
                          defaultSelected={[values.interests[index].interest]}
                          onChange={(selected) => {
                            var currentOptions = sampleInterests[values.interests[index].field_name] ? sampleInterests[values.interests[index].field_name] : ['General']
                            var stringSelected = JSON.stringify(selected)
                            stringSelected = stringSelected.slice(2, stringSelected.length - 2);
                            if(currentOptions.includes(stringSelected)) {
                                values.interests[index].interest = stringSelected; 
                            }
                            // setFieldValue("Interests", selected)
                            // setSelectedInterests(selected);
                          }}
                          placeholder="Select your interest...">
                        </Typeahead>
                          
                        <Field name={`interests.${index}.credit_hrs`} placeholder={"Credit Hours (e.g. 3)"} />

                      </Row>
                      {/*<div style={{color: "red"}}>{errors && errors.interests && errors.interests[index] && getInterestError(errors.interests[index])}</div>*/}
                      <div style={{color: "red"}}>{errors && errors.interests && errors.interests[index] && getInterestError(errors.interests[index])}</div>
                     </div>

                   ))
                 ) : (
                   <p>No tracks were entered. To add interests, you have to select majors/minors.</p>
                 )}
                 
               </div>
             )}
           />
            <br />
            <div>
              <Button type="submit">Save Changes</Button>
              <Button onClick={logout}>Logout</Button>
            </div>
        </Form>
      )}
      </Formik>
    </div>
  );
}


