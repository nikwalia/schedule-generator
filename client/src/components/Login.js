import React from "react";

import { Formik } from "formik";
import * as Yup from "yup";
import "./LoginStyle.css"

const Login = (props) => (
  <Formik
    initialValues={{ netid: "", password: "" }}
    onSubmit={(values, { setSubmitting }) => {
      setTimeout(() => {
        console.log(props.userData);
        console.log("Logging in", values);
        setSubmitting(false);
      }, 500);
    }}
    validationSchema={Yup.object().shape({
        netid: Yup.string()
          .required("Required"),
        password: Yup.string()
          .required("No password provided.")
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
        {errors.password && touched.password && (
            <div className="input-feedback">{errors.password}</div>
        )}

        <button type="submit" disabled={isSubmitting}>Login</button>

        </form>
      );
    }}
  </Formik>
);

export default Login;
