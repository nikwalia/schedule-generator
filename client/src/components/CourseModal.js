import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import Modal from "react-bootstrap/Modal";


export default function CourseModal(props) {
  return (
    <Modal show={true} onHide={() => {props.setShowModal(false)}} centered>
        <Modal.Header closeButton>
          <Modal.Title>{props.course.id}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
            <p><b>Average GPA : </b> {props.course.avgGpa}</p>
            <p><b>Course Rating : </b>{props.course.rating}</p>
            <p><b>Description : </b>{props.course.desc}</p>
        </Modal.Body>
      </Modal>
  ); 
}
