import React, { useState, useEffect } from 'react';
import './App.css';

import Survey from './components/Survey'; 
import Login from './components/Login'
import Signup from './components/Signup';
import Profile from './components/Profile';
import Lookup from './components/Lookup';
import Home from './components/Home'; 

import "bootstrap/dist/css/bootstrap.min.css";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";


// TODO: display the currentTab as active

function App() {
  const [currentTab, setCurrentTab] = useState(""); 
  const [user, setUser] = useState(
    localStorage.getItem('currentUser') || ''
  );

  function loginUser(vals) {
    localStorage.setItem('currentUser', vals.netid);
    setUser(localStorage.getItem('currentUser'));
  };

  function logoutUser() {
    localStorage.setItem('currentUser', null);
    setUser(localStorage.getItem('currentUser'));
  };

  return (
    <Router>
      <div>
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
          <a class="navbar-brand">Schedule Generator</a>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
              {/* <li class={(currentTab === "home") ? "nav-item active" : "nav-item"}>
                <a class="nav-link" href="/home" onClick={() => {setCurrentTab("home")}}>Home</a>
              </li>
              <li class={(currentTab === "lookup") ? "nav-item active" : "nav-item"}>
                <a class="nav-link" href="/lookup" onClick={() => {setCurrentTab("lookup")}}>Course Lookup</a>
              </li> */}
              <li class={(currentTab === "survey") ? "nav-item active" : "nav-item"}>
                <a class="nav-link" href="/survey" onClick={() => {setCurrentTab("survey")}}>Survey</a>
              </li>
              
            </ul>
          </div>
          {/* <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav ml-auto">
              <li class={(currentTab === "login") ? "nav-item active" : "nav-item"}>
                {!user && <a class="nav-link" href="/login" onClick={() => {setCurrentTab("login")}}>Login/Register</a>}
              </li>
              <li class={(currentTab === "profile") ? "nav-item active" : "nav-item"}>
                {user && <a class="nav-link" href="/profile" onClick={() => {setCurrentTab("profile")}}>My Profile</a>}
              </li>
            </ul>
          </div> */}

        </nav>

        <Switch>
          <Route path="/home">
            <Home />
          </Route>
          <Route path="/survey">
            <Survey userData={user}/>
          </Route>
          <Route path="/lookup">
            <Lookup />
          </Route>
          <Route path="/login">
            <Login userData={user} loginFunc={loginUser}/>
            <Signup />
          </Route>
          <Route path="/profile">
            <Profile userData={user} logoutFunc={logoutUser}/>
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;

// https://reactrouter.com/web/guides/quick-start
// https://ant.design/docs/react/introduce
