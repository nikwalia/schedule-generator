import React, { useState, useEffect } from "react";
import { Table, Column, HeaderCell, Cell } from 'rsuite-table';
import "rsuite-table/dist/css/rsuite-table.css";
import "./HomeStyle.css"

const currCourse = [{id: 'No course selected', avgGpa: '', rating: '', desc: ''}];

const topCourses = [
  { id: 'CS233', avgGpa: 3.10, rating: 1},
  { id: 'CS126', avgGpa: 3.20, rating: 2},
  { id: 'CS411', avgGpa: 3.30, rating: 3}
];

const scheduleData = [
  { id: 'CS233', avgGpa: 3.10, rating: 1, desc: "Fundamentals of computer architecture: digital logic design, working up from the logic gate level to understand the function of a simple computer; machine-level programming to understand implementation of high-level languages; performance models of modern computer architectures to enable performance optimization of software; hardware primitives for parallelism and security. Course Information: Prerequisite: CS 125 and CS 173; credit or concurrent enrollment in CS 225."},
  { id: 'CS126', avgGpa: 3.20, rating: 2, desc: "Fundamental principles and techniques of software development. Design, documentation, testing, and debugging software, with a significant emphasis on code review. Course Information: Credit is not given for both CS 242 and CS 126. Prerequisite: CS 125. For majors only."},
  { id: 'CS411', avgGpa: 3.30, rating: 3, desc: "Examination of the logical organization of databases: the entity-relationship model; the hierarchical, network, and relational data models and their languages. Functional dependencies and normal forms. Design, implementation, and optimization of query languages; security and integrity; concurrency control, and distributed database systems. Course Information: 3 undergraduate hours. 3 or 4 graduate hours. Prerequisite: CS 225."},
  { id: 'CS225', avgGpa: 3.40, rating: 4, desc: "Data abstractions: elementary data structures (lists, stacks, queues, and trees) and their implementation using an object-oriented programming language. Solutions to a variety of computational problems such as search on graphs and trees. Elementary analysis of algorithms. Course Information: Prerequisite: CS 125 or ECE 220; One of CS 173, MATH 213, MATH 347, MATH 412 or MATH 413. Class Schedule Information: Students must register for one lecture-discussion and one lecture section."}
];

const topSchedules = [
  { id: 'Schedule 1', score: 10},
  { id: 'Schedule 2', score: 9},
  { id: 'Schedule 3', score: 7}
];

export default function Home() {
  return (
  	<div>
  		<div id="scheduleBox">
			{
			  scheduleData.map((course) => {
			    return (
			      <div className="schedule" id={course.id}>
				    <div onClick={() => this.changeSidebar(course)}>
				        <h4>{course.id}</h4>
				        <p><b>Average GPA : </b> {course.avgGpa}</p>
				        <p><b>Course Rating : </b>{course.rating}</p>
				     </div>
				     <button onClick={() => this.removeCourse(course.id)}>Remove</button>
			      </div>
			    );
			  })
			} 
			<br/>
			<button onClick={() => this.addCourse()}>add</button>
		</div>

  		<div id="sidebar">
  			<h5>Course Preview</h5>
			{
			  this.state.currCourse.map((course) => {
			    return (
			      <div id="preview">
			        <h4>{course.id}</h4>
			        <p><b>Average GPA : </b>{course.avgGpa}</p>
			        <p><b>Course Rating : </b>{course.rating}</p>
			        <p><b>Description : </b>{course.desc}</p>
			      </div>
			    );
			  })
			} 

			<h5>Courses For You</h5>
		    <Table data={topCourses}>
			    <Column width={100}>
			      <HeaderCell>Course ID</HeaderCell>
			      <Cell dataKey="id" />
			    </Column>

			    <Column width={100}>
			      <HeaderCell>GPA</HeaderCell>
			      <Cell dataKey="avgGpa" />
			    </Column>

			    <Column width={100}>
			      <HeaderCell>Rating</HeaderCell>
			      <Cell dataKey="rating" />
			    </Column>
		  </Table>

		  <h5>Schedules For You</h5>
		  <Table data = {topSchedules}>
		  		<Column width={100}>
					<HeaderCell>Schedule</HeaderCell>
					<Cell dataKey="id" />
				</Column>

				<Column width={100}>
					<HeaderCell>Score</HeaderCell>
					<Cell dataKey="score" />
				</Column>
		  </Table>
		</div>

  </div>
  );
}
