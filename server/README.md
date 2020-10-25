# Backend information and guide

## Python dependencies:
The `conda` Python package manager has been used to install all software maintained on the Anaconda cloud. Pip is used for the rest. An `environment.yml` will soon be available.

After installing Anaconda, all dependencies can be installed with the following commands:

`conda install numpy pandas sqlalchemy -y`

`pip install neo4j`

Note the above is handled through the server setup script.

## Flask setup:
 - Create directory (e.g. "api") containing your Flask application.
    - Configure your API with all necessary endpoints.
 - Create ".flaskenv" file with corresponding environment variables.
    - The two lines you should insert are `FLASK_APP=<file_name>.py` and `FLASK_ENV=development`.
 - You can run your Flask application by navigating into your directory and running `flask run`.
 - You should be able to open up your application on your browser (default "127.0.0.1:5000").

## Server initialization on Amazon EC2 Console:
- Follow the instructions for creating an RDS instance in `db/README.md`
- Go to the EC2 page and select "Launch Instance"
- Choose Amazon Linux Image as the Amazon Machine Image 2 (AMI)
- Select t2.micro (free tier eligible) as the instance type
- Skip to Step 6: Configure Security Group. Choose "select an existing security group" and choose the one corresponding to the RDS console.
- Review and then click "Launch". Make sure to save the .pem file for enabling access.

## Connecting to the EC2 instance
- To SSH into the site, use the following command: `ssh -i /path/to/your/.pem username@public_ipv4_address`. The default username is `ec2-user` and the public IPv4 address can be obtained on the EC2 instance monitoring dashboard.

## First-Time Setup on EC2
- SSH into the server. Make sure Git is installed (`sudo yum install git -y`).
- Clone this repository.
- Run the setup script in `server/setup.sh`.

## Configuring sqlalchemy connections through Python:
Strings should be configured as `mysql://user_name:password@endpoint`. Refer to `demo_connect_db.py` for an example.

## Files and directories:
- `demo_connect_db.py`- a demo script for connecting to RDS.
