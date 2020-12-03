import React, { useState, useEffect } from "react";

import "bootstrap/dist/css/bootstrap.min.css";

import Modal from "react-bootstrap/Modal";

import Button from "react-bootstrap/Button";

import { Typeahead } from 'react-bootstrap-typeahead';

import 'react-bootstrap-typeahead/css/Typeahead.css';

 

const courseList = ['CS361', 'CS498VR']; // temp

 

export default function AddCourseModal(props) {

    const [selectedCourses, setSelectedCourses] = useState([]);

 

    const [course, setCourse] = useState('');

    const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');

    const [courseList, setCourseList] = useState(localStorage.getItem('courseList') || []);

    const serverURL = process.env.REACT_APP_PROXY

    const [rating, setRating] = useState('')

 

    useEffect(() => {

 

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

 

  return (

    <Modal show={true} onHide={() => {props.setShowAddModal(false)}} centered>

        <Modal.Header closeButton>

          <Modal.Title>Add class to {props.sem}</Modal.Title>

        </Modal.Header>

        <Modal.Body>

            <Typeahead

                multiple={false}

                filterBy={filterBy}

                id="class-lookup"

                options={courseList}

                selected={selectedCourses}

                onChange={(selected) => {

                  setSelectedCourses(selected);

                }}

                placeholder="Select courses to add...">

            </Typeahead>

            <input type="text" name="name" placeholder="rating" onChange={event => setRating(event.target.value)}/>

        </Modal.Body>

        <Button onClick={async () => {
              setNetid(localStorage.getItem('currentUser'));

              const requestOptions = {

                method: 'POST',

                body: JSON.stringify(netid + "," + props.sem + "," + rating + "," + selectedCourses),

                headers: {

                  "Access-Control-Allow-Origin": "*"

                }

              };

              await fetch(serverURL + '/add-classes', requestOptions)

                  .then(response => {

                    console.log(response);
                    props.setShowAddModal(false)
                   

                  })

                  .catch(error => console.error('Error:', error));

 

              alert('Submitted!')    

            }

          }>Add class</Button>

      </Modal>

  );

}