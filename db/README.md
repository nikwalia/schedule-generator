# Database information and guide

## Setting up MySQL Server on AWS

### Database Initialization on Amazon RDS Console
- Create an account on AWS as a "root user": https://www.aws.amazon.com/console
- Follow the instructions for creation of an RDS free-tier database: https://aws.amazon.com/getting-started/hands-on/create-mysql-db/
    - Select MySQL workbench under "Engine options"
    - Select "Free tier" under "Templates"
    - Enter root access credentials and make sure to save them.
    - Select "db.t2.micro" under "Burstable classes" in "DB instance size"
    - All other configurations remain the same

### Enabling global connections on Amazon RDS Console (NOT SECURE!)
- In AWS Console, head to RDS and select the initialized database
- Under "Connectivity & security", in the "Security" section, click on the URL for the VPC security group that you have selected
- Click on the "security group ID" that corresponds to the VPC used by the RDS instance
- Under "Inbound rules", click on "Edit inbound rules"
- Click on "Add rule" and set the rules to be as below:
![Access setup](inbound-rule-setup.png)

### Connecting to RDS through MySQL Workbench:
- Follow the instructions at https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToInstance.html for MySQL Workbench.

### Connecting to RDS through Python code:
- Refer to `server/README.md` for instructions on this.

## Files and directories:
- `schema_setup.sql`- creates all tables for the database. Should be executed before everything else.

## Setting up Neo4J Server on AWS

### Database initialization
Since hosting a Neo4J RDS instance on AWS is paid, we will instead use a Docker container on our EC2 instance. This setup is already handled
for the prerequisites database through use of the `setup.sh` script- make sure you run this first! Since we are using the community edition of Neo4J,
multiple graph databases are not allowed for a single instance- so we will simply work around this by spinning up multiple Docker instances
and querying them individually.

### Connecting to Neo4J using Neo4J Desktopp:
- Download Neo4J Desktop.
- Create a new project that will contain all of the graph database connections.
- Select "Add a new database" and choose "Connect to Remore DBMS".
- Set the name of the database. Make sure these are distinct and descriptive, as the graph within each database will be `neo4j-default` and cannot
be renamed.
- Replace `localhost` with the IP address of the instance. Make sure to change the port to match the exposed Bolt port for the DB instance. The
corresponding port for the prerequisites DB is 7687- the default option.
- Enter "neo4j" as the username and "test" as the password, then connect and open.
- You should see a screen similar to this:
![Neo4j Setup](neo4j-connection.png)

### Spinning up a new Docker-Neo4J instance
- SSH into the EC2 instance. Check out the instructions at `server/README.md`.
- Run `docker ps` to find all the running instances of Docker images.
- There, you will see all the different ports that have been occcupied. For example, the default port connection 