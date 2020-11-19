# Frontend information and guide

## Dependencies:
We use React as our main framework to support our front-end. As such you must have Node.js installed on your local machine. You must also run `npm install` to get all required libraries that we use (e.g. Formik, Yup, etc).

## React setup:
- Create react app via `npx create-react-app client`
- Configure proxy in `package.json` to target the Flask webaddress by adding `"proxy": "http://localhost:5000",`
    - It is also worth defining a script to help start up the backend for local development.
- You can run the React application by navigating into `client` and running `npm start`.
- The browser should automatically open up the webpage; however, your console will have a link to it as well.

## Files and directories:
- `public`
    - `manifest.json`-
- `src`
    - `components`
        - `Home.js`- Home page
        - `Login.js`- Login component
        - `LoginStyle.css`- Login component styles
        - `Lookup.js` - Lookup component
        - `LookupStyles.css` - Lookup styles component
        - `Profile.js`- Profile page 
        - `Signup.js`- Signup component
        - `Survey.js`- Survey page
        - `SurveyStyle.css`- Survey page styles
    - `static`
        - `concentrations.json`- static data of all majors and minors offered by UIUC
    - `App.js`- Main routing page
    - `App.css`- Styles for app
    - `index.js`- stores ReactDOM
    - `index.css`- stores styles for index.js
    - `serviceWorker.js`-
    - `setupTests.js`-
- `package-lock.json`- packages necessary to run 
- `package.json`- configuration of webapp
- `yarn.lock`-
- `.env.development` - Config for development environment
- `.env.production` - Config for production environment