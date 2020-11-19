import React, { useState, useEffect }  from "react";

import { Formik } from "formik";
import { Redirect } from 'react-router-dom';
import * as Yup from "yup";
import "./LoginStyle.css"

const serverURL = process.env.REACT_APP_PROXY

const Login = (props) => (
  <Formik
    initialValues={{ netid: "", password: "" }}
    onSubmit={(values, { setSubmitting }) => {
      setTimeout(() => {

        fetch(serverURL + '/login-request?netid=' + values.netid + '&password=' + values.password,
        {
            method: 'GET',
            headers: {
              "Access-Control-Allow-Origin": "*"
            }
        })
        .then(response => response.json())
        .then((data) => {
          if (data.userFound) {
            props.loginFunc(values);
          } else {
            values.password = "inv";
          }
        });

        setSubmitting(false);
      }, 500);
    }}
    validationSchema={Yup.object().shape({
        netid: Yup.string()
          .required("Required"),
        password: Yup.string()
          .required("No password provided.")
          .min(6, "Password should be 6 characters minimum."),
      })}
  >
    {props => {
      const {
        values,
        touched,
        errors,
        isSubmitting,
        handleChange,
        handleBlur,
        handleSubmit
      } = props;
      
      return (
        <div>
        {localStorage.getItem('currentUser') && <Redirect to='/profile' />}
        <form onSubmit={handleSubmit}>

        <label htmlFor="netid">netID</label>
        <input
            id="netid"
            name="netid"
            type="text"
            placeholder="Enter your netid"
            value={values.netid}
            onChange={handleChange}
            onBlur={handleBlur}
            className={errors.netid && touched.netid && "error"}
        />
        {errors.netid && touched.netid && (
            <div className="input-feedback">{errors.netid}</div>
        )}

        <label htmlFor="password">Password</label>
        <input
            id="password"
            name="password"
            type="password"
            placeholder="Enter your password"
            value={values.password}
            onChange={handleChange}
            onBlur={handleBlur}
            className={errors.password && touched.password && "error"}
        />
        {(errors.password && touched.password) || (values.password == "inv") && (
            <div className="input-feedback">{errors.password}</div>
        )}

        <button type="submit" disabled={isSubmitting}>Login</button>

        </form>
        </div>
      );
    }}
  </Formik>
);

export default Login;
