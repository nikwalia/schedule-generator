import React, { useState, useEffect } from 'react';
import './App.css';

import Survey from './components/Survey'; 
import Login from './components/Login'
import Signup from './components/Signup';
import Profile from './components/Profile';
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
  const [user, setUser] = useState('temp');

  function updateUser(newUser) {
    setUser(newUser);
  };

  useEffect(() => {
    console.log("Reloaded page " + currentTab)
  }, []);

  return (
    <Router>
      <div>
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
          <a class="navbar-brand">Schedule Generator</a>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
              <li class={(currentTab === "home") ? "nav-item active" : "nav-item"}>
                <a class="nav-link" href="/home" onClick={() => {setCurrentTab("home")}}>Home</a>
              </li>
              <li class={(currentTab === "survey") ? "nav-item active" : "nav-item"}>
                <a class="nav-link" href="/survey" onClick={() => {setCurrentTab("survey")}}>Survey</a>
              </li>
              
            </ul>
          </div>
          <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav ml-auto">
              <li class={(currentTab === "login") ? "nav-item active" : "nav-item"}>
                {!user && <a class="nav-link" href="/login" onClick={() => {setCurrentTab("login")}}>Login/Register</a>}
              </li>
              <li class={(currentTab === "profile") ? "nav-item active" : "nav-item"}>
                {user && <a class="nav-link" href="/profile" onClick={() => {setCurrentTab("profile")}}>My Profile</a>}
              </li>
            </ul>
          </div>

        </nav>

        <Switch>
          <Route path="/home">
            <Home />
          </Route>
          <Route path="/survey">
            <Survey userData={user}/>
          </Route>
          <Route path="/login">
            <Login userData={user}/>
            <Signup />
          </Route>
          <Route path="/profile">
            <Profile userData={user}/>
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;

// https://reactrouter.com/web/guides/quick-start
// https://ant.design/docs/react/introduce
