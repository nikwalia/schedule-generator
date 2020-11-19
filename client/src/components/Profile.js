import React, { useState, useEffect } from 'react';
import { Redirect } from 'react-router-dom';

const serverURL = process.env.REACT_APP_PROXY

function Profile(props) {
  const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');
  const [responseData, setResponseData] = useState('');
  const [buttonState, setButtonState] = useState(0);

  useEffect(() => {
    //   alert(JSON.stringify(netid)); 
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
        .then(data => setResponseData(data));
    }
  }, []);

  if(!netid) {
    return <Redirect to='/login' />
  }

  const handleSubmit = event => {

    if (buttonState === 2) {
      // Delete account
      // Fetch account details
      event.preventDefault();
      fetch(serverURL + '/delete-profile?netid=' + netid,
        {
            method: 'GET',
            headers: {
              "Access-Control-Allow-Origin": "*"
            }
        })
        .then(response => response.json())
        .then(data => setResponseData(data));
    } else if (buttonState === 1) {
      props.logoutFunc();
      localStorage.clear();
    }
    
    }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>            
            {responseData.student_name && netid && <div>
              <p>NetID: {netid}</p> 
              <p>Student Name: {JSON.stringify(responseData.student_name["0"])}</p>    
              <p>Start Semester: {JSON.stringify(responseData.start_semester["0"])}</p>
              <p>Current Semester: {JSON.stringify(responseData.current_semester["0"])}</p>
              <p>Expected Graduation: {JSON.stringify(responseData.expected_graduation["0"])}</p>
            </div>}

            <input type="submit" value="Logout" onClick={() => (setButtonState(1))}/>
            <input type="submit" value="Delete Account" onClick={() => (setButtonState(2))}/>
        </label>
        </form>
    </div>
  );
}

export default Profile
