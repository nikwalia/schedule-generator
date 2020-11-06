import React, { useState, useEffect } from "react";
import Row from 'react-bootstrap/Row'; 
import { Formik, Field, Form, FieldArray } from 'formik';
import * as Yup from 'yup';
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
import "./SurveyStyle.css"

const SurveySchema = Yup.object().shape({
  Name: Yup.string()
      .required('Required'),
  NetID: Yup.string()
      .required('Required'),
  CurrentSem: Yup.string()
      .required('Required'),
  StartingSem: Yup.string()
      .required('Required'), 
  EndingSem: Yup.string() 
      .required('Required'),
  /*Course: Yup.string()
      .required('Required'), // TODO: add this constraint? 
  Sem: Yup.number(), 
      .required('Required'),
  Rating: Yup.number() 
      .integer() 
      .min(1)
      .max(10)
      .required('Required'), // is rating required? 
  */ 

});

var concentrations = require('../static/concentrations.json');

// TODO: constants.js for url
// TODO: more customized validation 

export default function Survey(props) {
  function createCoursesArray(enrollmentData) {
    var courses = [] 
    Object.keys(enrollmentData.course_id).forEach(function(idx) {
      courses.push([enrollmentData.course_id[idx], enrollmentData.semester[idx], enrollmentData.rating[idx]]);
    });
    return courses; 
  }

  function getMajors(majorData) {
    var majors = [] 
    Object.keys(majorData['field_name']).forEach(function(idx) {
      majors.push(majorData['field_name'][idx]);
    });
    return majors; 
  }

  return (
    <div id="form-container">
      <h1>Survey</h1>
      <Formik
        initialValues={{
            Name: '',
            NetID: '',
            CurrentSem: '', 
            StartingSem: '',
            EndingSem: '', 
            Majors: [], 
            Minors: []
        }}
        validationSchema={SurveySchema}
        onSubmit={async (values) => {
            const requestOptions = {
              method: 'POST',
              // headers: {
              //   'Access-Control-Allow-Origin': '*',
              //   'Referrer-Policy': 'origin-when-cross-origin'
              // },
              mode: 'no-cors',
              body: JSON.stringify(values)
            };

            const response = await fetch('http://localhost:5000/submit', requestOptions)
                .then(response => console.log(response))
                .catch(error => console.error('Error:', error));
            
        }}
      > 
      {({ errors, touched, values, setFieldValue }) => (
        <Form>
            <label htmlFor="NetID">NetID: </label>
            <Field id="NetID" name="NetID" placeholder="jdoe8" /> 
            {errors.NetID && touched.NetID ? (<div>{errors.NetID}</div>) : null}

            <button type="button" onClick={async () => {
              // get stored data
              const requestOptions = {
                method: 'GET',
                headers: {
                  "Access-Control-Allow-Origin": "*"
                }
              };
              const response = await fetch('http://localhost:5000/get-survey?netid=' + values.NetID, requestOptions)
                .then(response => response.json())
                .then(data => {
                  if (data) {
                    setFieldValue("Name", data.student.student_name[0]); 
                    setFieldValue("CurrentSem", data.student.current_semester[0]); 
                    setFieldValue("StartingSem", data.student.start_semester[0]); 
                    setFieldValue("Majors", getMajors(data.majors)); 
                    setFieldValue("Minors", getMajors(data.minors)); 
                    setFieldValue("EndingSem", data.student.expected_graduation[0]); 

                    var courses = createCoursesArray(data.enrollment);  
                    setFieldValue("classes", courses); 
                  }
                })
                .catch(error => console.error('Error:', error));              
            }}>
              Fetch info
            </button>
            <p>Your information will be auto-filled by fetching your data based on NetID.</p>
            <br />
            <br />

            <label htmlFor="Name">Name (First and Last): </label>
            <Field id="Name" name="Name" placeholder="Jane Doe"/> 
            {errors.Name && touched.Name ? (<div>{errors.Name}</div>) : null}
            <br />            

            <label htmlFor="CurrentSem">Current Semester: </label>
            <Field id="CurrentSem" name="CurrentSem" placeholder="e.g. SP20"/> 
            {errors.CurrentSem && touched.CurrentSem ? (<div>{errors.CurrentSem}</div>) : null}
            <br />

            <label htmlFor="StartingSem">Starting Semester: </label>
            <Field id="StartingSem" name="StartingSem" placeholder="e.g. FA19"/> 
            {errors.StartingSem && touched.StartingSem ? (<div>{errors.StartingSem}</div>) : null}
            <br />

            <label htmlFor="Majors">Majors: </label>
            <Field
              component="select"
              name="Majors"
              // TODO: this has to be required
              onChange={evt =>
                setFieldValue(
                  "Majors",
                  [].slice
                    .call(evt.target.selectedOptions)
                    .map(option => option.value)
                )
              }
              multiple={true}
            >
              {concentrations.majors.map(s => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Field>
            <br />
            <br />

            <label htmlFor="Minors">Minors: </label>
            <Field
              component="select"
              name="Minors"
              // You need to set the new field value
              onChange={evt =>
                setFieldValue(
                  "Minors",
                  [].slice
                    .call(evt.target.selectedOptions)
                    .map(option => option.value)
                )
              }
              multiple={true}
            >
              {concentrations.minors.map(s => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Field>
            <br /> 
            <br />

            <label htmlFor="EndingSem">Ending Semester: </label>
            <Field id="EndingSem" name="EndingSem" placeholder="e.g. SP23"/> 
            {errors.EndingSem && touched.EndingSem ? (<div>{errors.EndingSem}</div>) : null}
            <br />

            <p>Please enter your classes below. For each class, you can indicate the course ID (e.g. CS411), 
               semester you took it in (e.g. 1), and rating 1-10 (1 being the worst).</p>

            <FieldArray
             name="classes"
             render={arrayHelpers => (
               <div>
                 {values.classes && values.classes.length > 0 ? (
                    values.classes.map((friend, index) => (
                     <div key={index}>
                       <Row> {/*TODO: make the three text fields be in 1 row*/}
                       <Field name={`classes.${index}.${0}`} placeholder="CourseID (e.g. CS411)" id="Course"/>
                       {/*errors.Course && touched.Course ? (<div>{errors.Course}</div>) : null*/}

                       <Field name={`classes.${index}.${1}`} placeholder="Semester (e.g. FA20)" id="Sem"/>
                       <Field name={`classes.${index}.${2}`} placeholder="Rating (e.g. 10)" id="Rating"/>
                       
                       <button
                         type="button"
                         onClick={() => arrayHelpers.remove(index)} 
                       > - </button>
                       <button
                         type="button"
                         onClick={() => {arrayHelpers.insert(index, '')}} 
                       > + </button>
                      </Row>
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
