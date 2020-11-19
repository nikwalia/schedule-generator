import React from "react";

import { Formik } from "formik";
import * as Yup from "yup";
import "./LoginStyle.css"
import { Link } from "react-router-dom";

const Signup = () => (
  <Formik
    initialValues={{ netid: "", password: "" }}
    onSubmit={(values, { setSubmitting }) => {
      setTimeout(() => {
        console.log("Registering user", values);
        setSubmitting(false);
      }, 500);
    }}
    validationSchema={Yup.object().shape({
        netid: Yup.string()
          .required("Required"),
        password: Yup.string()
          .required("No password provided.")
          .min(6, "Password should be 6 characters minimum."),
        passwordConfirm: Yup.string()
          .oneOf([Yup.ref('password'), null], 'Passwords must match'),
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
        <hr  style={{
            color: '#808080',
            backgroundColor: '#808080',
            height: .3,
            width: '70%',
            borderColor : '#808080'
        }}/>
        <h2 style={{textAlign: "center"}}>Don't have an account?</h2>

        <form onSubmit={handleSubmit}>

        {/* <label htmlFor="netid">netID</label>
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

        <label htmlFor="password">Confirm Password</label>
        <input
            id="passwordConfirm"
            name="passwordConfirm"
            type="password"
            placeholder="Retype your password"
            value={values.passwordConfirm}
            onChange={handleChange}
            onBlur={handleBlur}
            className={errors.passwordConfirm && touched.passwordConfirm && "error"}
        />
        {errors.passwordConfirm && touched.passwordConfirm && (
            <div className="input-feedback">{errors.passwordConfirm}</div>
        )} */}
        
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
