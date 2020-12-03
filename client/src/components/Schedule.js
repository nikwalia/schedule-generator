import React, { useState, useEffect } from "react";
import { Header, List } from "semantic-ui-react";
import CourseTile from "./CourseTile.js"; 
import "bootstrap/dist/css/bootstrap.min.css";
import "./CoursePlan.css";
import Container from "react-bootstrap/Container";
import CourseModal from "./CourseModal.js";
import AddCourseModal from "./AddCourseModal.js";
import Button from "react-bootstrap/Button"; 
import Row from "react-bootstrap/Row"; 
import Col from "react-bootstrap/Col"; 
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';

var userData = require('../static/sampleGeneratedSchedules.json')

const useStyles = makeStyles({
    table: {
        minWidth: '100%',
    },
});

export default function Schedule(props) {
    const classes = useStyles();
    // const rows = createRows(props.classes); 
  function convertToArray(obj) { 
      var list = []; 
      Object.keys(obj).forEach(function(idx) {
        if (!list.includes(obj[idx])) {
          list.push(obj[idx]);
        }
      });
      return list; 
  }
  return (
    <TableContainer component={Paper} style={{minWidth: '100%'}}>
      <Table className={classes.table} aria-label="simple table" style={{minWidth: '100%'}}>
        <TableHead>
          <TableRow>
            <TableCell> </TableCell>
            <TableCell align="center">CourseID</TableCell> {/*TODO: on click, bring up course modal*/}
          </TableRow>
        </TableHead>
        <TableBody>
          {convertToArray(props.classes).map((index, courseID) => (
            <TableRow key={index}>
              <TableCell>{courseID}</TableCell>
              <TableCell align="center">
                {index}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
