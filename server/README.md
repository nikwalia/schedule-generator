# Backend information and guide

## Python dependencies:
The `conda` Python package manager has been used to install all software. An `environment.yml` will soon be available.

After installing Anaconda, all dependencies can be installed with the following command:
`conda install numpy pandas sqlalchemy flask python-dotenv`

## Flask setup:
 - Create directory (e.g. "api") containing your Flask application.
    - Configure your API with all necessary endpoints.
 - Create ".flaskenv" file with corresponding environment variables.
    - The two lines you should insert are `FLASK_APP=<file_name>.py` and `FLASK_ENV=development`.
 - You can run your Flask application by navigating into your directory and running `flask run`.
 - You should be able to open up your application on your browser (default "127.0.0.1:5000").

## Server initialization on Amazon EC2 Console:
__TODO__: instructions for EC2 setup

## Configuring sqlalchemy connections through Python:
Strings should be configured as `mysql://user_name:password@endpoint`. Refer to `demo_connect_db.py` for an example.

## Files and directories:
- `demo_connect_db.py`- a demo script for connecting to RDS.
