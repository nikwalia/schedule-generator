import React, { useState, useEffect } from 'react';

function Profile(props) {
  const [netid, setNetid] = useState('');
  const [responseData, setResponseData] = useState('');
  const [buttonState, setButtonState] = useState(0);

  useEffect(() => {
    //   alert(JSON.stringify(netid)); 
    
    if (props.userData) {
      fetch('http://localhost:5000/get-profile?netid=' + props.userData,
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

  const handleChangeNetid = e => {
    setNetid(e.target.value)
  }

  const handleSubmit = event => {

    if (buttonState === 1) {
      // Fetch account details
      event.preventDefault();
      fetch('http://localhost:5000/get-profile?netid=' + netid,
        {
            method: 'GET',
            headers: {
              "Access-Control-Allow-Origin": "*"
            }
        })
        .then(response => response.json())
        .then(data => setResponseData(data));
    } else if (buttonState === 2) {
      // Delete account
      // Fetch account details
      event.preventDefault();
      fetch('http://localhost:5000/delete-profile?netid=' + netid,
        {
            method: 'GET',
            headers: {
              "Access-Control-Allow-Origin": "*"
            }
        })
        .then(response => response.json())
        .then(data => setResponseData(data));
    }
    
    // console.log(response);
    }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
            Netid: 
            <input
                type="username"
                value={netid}
                onChange={handleChangeNetid}
            />
            <input type="submit" value="Get Account" onClick={() => (setButtonState(1))}/>
            <input type="submit" value="Delete Account" onClick={() => (setButtonState(2))}/>
            {netid && buttonState === 1 && <div>
              <p>Student Name: {JSON.stringify(responseData.student_name["0"])}</p>    
              <p>Start Semester: {JSON.stringify(responseData.start_semester["0"])}</p>
              <p>Current Semester: {JSON.stringify(responseData.current_semester["0"])}</p>
              <p>Expected Graduation: {JSON.stringify(responseData.expected_graduation["0"])}</p>
            </div>}
        </label>
        </form>
    </div>
  );
}

export default Profile
