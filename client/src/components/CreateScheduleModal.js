import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button"; 
import { Typeahead } from 'react-bootstrap-typeahead';
import 'react-bootstrap-typeahead/css/Typeahead.css';
import { Formik, Field, Form, FieldArray } from 'formik';
import * as Yup from 'yup';

const ScheduleSchema = Yup.object().shape({
    classes: Yup.string()
          .required('Required'),
  });

export default function CreateScheduleModal(props) {
    const [selectedCourses, setSelectedCourses] = useState([]); 
    const [courseList, setCourseList] = useState(localStorage.getItem('courseList') || []);
    const serverURL = process.env.REACT_APP_PROXY; 

    useEffect(() => {
      console.log(courseList);
      // If nothing in cached courseList, retrieve list of courses
      if (courseList.length === 0) {
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
      } else if (courseList.length !== 0 && typeof courseList === 'string') {
        setCourseList(courseList.split(','));
      }
    }, []);

    function filterBy(option, courseId) {
      // Applies filter for removing options
      if (courseId.selected.length) {
        return true;
      }
      return option.toLowerCase().indexOf(courseId.text.toLowerCase()) > -1;
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

  return (
    <Modal show={true} onHide={() => {props.setCreateScheduleModal(false)}} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create a schedule</Modal.Title>
        </Modal.Header>
        <Modal.Body>
        <Formik
        initialValues={{
            NetID: props.netid, 
            ScheduleID: props.numSchedules,
            semester: 'SP21', // TODO: change to next sem
            classes: []
        }}
        enableReinitialize={true}
        validationSchema={ScheduleSchema}
        onSubmit={async (values) => {
            // try to save schedule 
            const requestOptions = {
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify(values)
              };

              await fetch(serverURL + '/add-schedule', requestOptions)
                  .then(response => {
                      props.setNumSchedules(props.numSchedules + 1)
                      props.setCreateScheduleModal(false)
                      props.getAllSchedules()
                      // if response is ok, setNumSchedules(numScheudles + 1)
                  })
                  .catch(error => console.error('Error:', error));
        }}
      > 
      {({ errors, touched, values, setFieldValue }) => (
        <Form>
            {/*<label htmlFor="semester">Semester: </label>
            <Field id="semester" name="Semester" placeholder="e.g. SP20"/> 
            {errors.CurrentSem && touched.CurrentSem ? (<div style={{color: "red"}}>{errors.CurrentSem}</div>) : null}
            <br />*/}

            <label htmlFor="classes">Courses: </label>
            <Typeahead
                multiple={true}
                filterBy={filterBy}
                id="class-lookup"
                options={courseList}
                selected={selectedCourses}
                onChange={(selected) => {
                  setSelectedCourses(selected);
                  setFieldValue("classes", selected)
                }}
                placeholder="Select courses to add...">
                  {({ isMenuShown, toggleMenu }) => (
                <ToggleButton isOpen={isMenuShown} onClick={e => toggleMenu()} />
                )}
            </Typeahead>
            {errors.classes && touched.classes ? (<div style={{color: "red"}}>{errors.classes}</div>) : null}
            <br />
            <Button type="submit">Save Schedule</Button>
        </Form>
        )}
        </Formik>    
        </Modal.Body>
      </Modal>
  ); 
}
