import React, { useState, useEffect } from 'react';
import { Typeahead } from 'react-bootstrap-typeahead';

import 'react-bootstrap-typeahead/css/Typeahead.css';
import './LookupStyle.css';

// Lookahead Documentation
// https://www.npmjs.com/package/react-bootstrap-typeahead
// https://codesandbox.io/s/rbt-combobox-example-kkmyd?file=/src/index.js:244-250
//

const serverURL = process.env.REACT_APP_PROXY

function Lookup() {
  const [course, setCourse] = useState('');
  const [courseList, setCourseList] = useState(localStorage.getItem('courseList') || []);

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

  function handleSelect(selected) {
    // event.preventDefault();
    fetch(serverURL + '/get-course?courseid=' + selected,
    {
        method: 'GET',
        headers: {
            "Access-Control-Allow-Origin": "*"
        }
    })
    .then(response => response.json())
    .then(data => setCourse(data));
    
  }

  function filterBy(option, courseId) {
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
    <div>
      <Typeahead
          filterBy={filterBy}
          id="course-lookup"
          options={courseList}
          onChange={(selected) => {
            handleSelect(selected);
          }}
          placeholder="Choose a course...">
          {({ isMenuShown, toggleMenu }) => (
          <ToggleButton isOpen={isMenuShown} onClick={e => toggleMenu()} />
          )}
      </Typeahead>
      {course && <div>
              <h2>{course.courseId}: {course.courseTitle}</h2>  
              <p>Credit Hours: {course.creditHours}</p>
              <p>GPA: {course.GPA}</p>    
              <p>Course Description: {course.description}</p>  
            </div>}

    </div>
  );
}

export default Lookup
