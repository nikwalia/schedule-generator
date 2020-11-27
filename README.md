# Schedule Generator by OurSQL

### Directory guide:
- `db` contains necessary instructions for MySQL server initialization and connection on Amazon RDS, as well as other SQL scripts
- `server` contains Flask server backend instructions, Amazon EC2 server setup instructions, and code for fetching/transferring data
- `client` contains JS user-facing code
- `model` contains the neural network that powers schedule generation and recommendation

### Local dependencies:
- A local SSH client is necessary to connect to AWS
- Installation of Neo4J Engine is recommended
- Python3 (conda distribution preferred):
    - `conda install numpy pandas pathlib tqdm neo4j sqlalchemy flask flask-cors -y`
    - `pip install neo4j python-dotenv`

### Setup Script
To install the module run `python setup.py install`. 
To clean the module from the directory run `bash clean_install.sh`

### Advanced Function 1
The advanced function is used to generate an optimal schedule. Scores are calculated based off of this formula:

![Equation for AF1](https://latex.codecogs.com/svg.latex?\Large&space;score=\\frac{(AVG\\_GPA+AVG\\_User\\_Rating+AVG\\_NN\\_Score)\\cdot\\;num\\_interest\\_courses}{|num\\_CH-num\\_CH\\_desired|\\cdot\\;num\\_courses})

There are multiple factors that go into this:
- `AVG_GPA` is the average GPA of all the classes in a candidate schedule
- `AVG_User_Rating` is the average of average ratings across all user-provided ratings for the classes in the schedule
- `AVG_NN_Score` is the average NN rating. This rating takes into account temporal trends
- `num_interest_courses` and `num_courses` correspond to how many courses align with a student's stream and the number of courses in the schedule
- `num_CH` and `num_CH_desired` correspond to the total credit-hours of the schedule, and the amount the user wants to limit to.
