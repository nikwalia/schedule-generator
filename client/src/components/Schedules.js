import React, { useState, useEffect } from "react";
import { Header, List } from "semantic-ui-react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./CoursePlan.css";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button"; 
import Row from "react-bootstrap/Row"; 
import Col from "react-bootstrap/Col"; 
import Schedule from "./Schedule.js";
import CreateScheduleModal from "./CreateScheduleModal.js"; 
import Tooltip from '@material-ui/core/Tooltip';

var generatedSchedules = require('../static/sampleGeneratedSchedules.json')
var schedulesArr = [];
    Object.keys(generatedSchedules).forEach(function(key) {
        schedulesArr.push(generatedSchedules[key]);
});
const serverURL = process.env.REACT_APP_PROXY

export default function Schedules(props) {   
  const [netid, setNetid] = useState(localStorage.getItem('currentUser') || '');
  const [optimalSchedule, setOptimalSchedule] = useState(''); 
  const [scheduleGenerated, setScheduleGenerated] = useState(false); 
  const [createScheduleModal, setCreateScheduleModal] = useState(false);
  const [storedSchedules, setStoredSchedules] = useState(false); 
  const [numSchedules, setNumSchedules] = useState(0);  
  const [scheduleScores, setScheduleScores] = useState([]); 
  const [unprocessedSchedules, setUnprocessedSchedules] = useState([]); 

  function getOptimalSchedule() {
    const requestOptions = {
        method: 'GET',
        headers: {
          "Access-Control-Allow-Origin": "*"
        }
      };
      fetch(serverURL + '/get-ideal-schedule?netid=' + netid, requestOptions)
        .then(response => response.json())
        .then(data => {
          setOptimalSchedule(data["schedule"]); 
        })
        .catch(error => console.error('Error:', error));   
  }

  function convertToArray(obj) { 
    var list = []; 
    Object.keys(obj).forEach(function(idx) {
        list.push(obj[idx]);
    });
    return list; 
  }

  function getScheduleScore(index, id) {
    const requestOptions = {
        method: 'GET',
        headers: {
            "Access-Control-Allow-Origin": "*"
            },
        };
        fetch(serverURL + '/review-schedule?NetID='+netid+"&ScheduleID="+id, requestOptions)
            .then(response => response.json())
            .then(data => {
                scheduleScores[index] = data["score"]
            })
            .catch(error => console.error('Error:', error));   
        // return 1
  }

  function getEachScore() {
    var scores = []
    Object.keys(unprocessedSchedules).forEach(async function(idx) {
        var score = await getScheduleScore(idx); 
        // alert(score) 
        //scores.push(score) 
    })
    setScheduleScores(scores); 
  }

  function removeSchedule(id) {
      // remove schedule with post request 
      const requestOptions = {
        method: 'POST',
        mode: 'no-cors',
        body: JSON.stringify(netid + "," + id)
      };

      fetch(serverURL + '/remove-schedule', requestOptions)
          .then(response => console.log(response))
          .catch(error => console.error('Error:', error));
      alert("Removed!")
      getAllSchedules(); 
      // dont worry about adjusting ids, they build off of the greatest # 
  }

  function getAllSchedules() {
    const requestOptions = {
        method: 'GET',
        headers: {
            "Access-Control-Allow-Origin": "*"
        }
        };
        fetch(serverURL + '/get-schedules?netid=' + netid, requestOptions)
        .then(response => response.json())
        .then(data => {
            alert("Fetching and displaying schedules...")
            setUnprocessedSchedules(data); 
            var scheduleArr = []
            var scoreArr = [] 
            Object.keys(data).forEach(function(idx) {
                scheduleArr.push([idx, data[idx]])
                scoreArr.push("empty")
            }); 

            Object.keys(data).forEach(function(idx, index) {
                if(index == scheduleArr.length - 1) {
                    setNumSchedules(idx + 1); 
                }
            }); 
            
            setStoredSchedules(scheduleArr);  
            setScheduleScores(scoreArr); 
        })
        .catch(error => console.error('Error:', error));        
  }

  useEffect(() => {
    setNetid(localStorage.getItem('currentUser'));
    if (netid) {
        // getOptimalSchedule(); 
        getAllSchedules(); 
    }       
  }, []);

  return (
    <div>
        <Container> 
            <Header as='h2' textAlign='center'>Recommended Schedule
            {!scheduleGenerated && 
                <Button variant="link" onClick={() => {getOptimalSchedule(); setScheduleGenerated(true)}}>View</Button>
            } 
            </Header>    

            

            {scheduleGenerated && 
                <Schedule classes={optimalSchedule}/>
            }
            
            <br />
            <br />
            <br />
            <Header as='h2' textAlign='center'>Plan Ahead
                <Button variant="link" onClick={() => {setCreateScheduleModal(true)}}>Add a schedule</Button>
            </Header>  
            <List style={{minWidth: '100%'}}>
                {convertToArray(storedSchedules).map((schedule, index) => {
                return (
                    <div>
                    <Row lg={2} onClick={() => {
                        if (scheduleScores[index] === "empty") { // not scored yet
                            getScheduleScore(index, schedule[0]); 
                            alert("Fetching score...")
                        } else {
                            alert("Score: "+scheduleScores[index])
                        }                        
                    }}>
                    <Tooltip title={"Click to view schedule score"} arrow>           
                    <List.Item  key={schedule[0]}>
                        <List.Content>
                            <Schedule classes={schedule[1]}/>                         
                        </List.Content>
                        <br></br>
                    </List.Item>    
                    </Tooltip>
                    </Row>   
                    
                    <Button variant="dark" onClick={() => {removeSchedule(schedule[0])}}>Remove schedule</Button> 
                      
                    <br /> <br /><br /> <br /><br /> 
                    </div>          
                );
                })}
            </List> 
            
        </Container>

        {createScheduleModal &&
        <CreateScheduleModal getAllSchedules={getAllSchedules} setCreateScheduleModal={setCreateScheduleModal} netid={netid} numSchedules={numSchedules} setNumSchedules={setNumSchedules}/>}
        
    </div>
  );
}
