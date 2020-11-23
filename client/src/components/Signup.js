import React from "react";

import { Formik } from "formik";
import "./LoginStyle.css"
import { Link } from "react-router-dom";

const Signup = () => (
  <Formik
    onSubmit={(values, { setSubmitting }) => {
      setTimeout(() => {
        setSubmitting(false);
      }, 500);
    }}
  >
    {props => {
      const {
        isSubmitting,
        handleSubmit
      } = props;

      return (
        <div>
        <hr  style={{
            color: '#808080',
            backgroundColor: '#808080',
            height: .3,
            width: '70%',
            borderColor : '#808080'
        }}/>
        <h2 style={{textAlign: "center"}}>Don't have an account?</h2>

        <form onSubmit={handleSubmit}>
        
        <Link to='/survey'>
        <button type="submit" disabled={isSubmitting}>Fill out the survey</button>
        </Link>

        </form>
        </div>
      );
    }}
  </Formik>
);

export default Signup;
