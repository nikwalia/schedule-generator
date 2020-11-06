# Schedule Generator by OurSQL

### Directory guide:
- `db` contains necessary instructions for MySQL server initialization and connection on Amazon RDS, as well as other SQL scripts
- `server` contains Flask server backend instructions, Amazon EC2 server setup instructions, and code for fetching/transferring data
- `client` contains JS user-facing code

### Local dependencies:
- A local SSH client is necessary to connect to AWS
- Installation of Neo4J Engine is recommended
- Python3 (conda distribution preferred):
    - `conda install numpy, pandas, pathlib, tqdm, neo4j, sqlalchemy -y`
