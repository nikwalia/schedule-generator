# Needs to be run with root permissions. Guaranteed to work only on an Amazon Linux Image.

# install Apache2 HTTP server
sudo yum update && sudo yum upgrade -y
sudo yum install httpd tmux -y
sudo chkconfig httpd on

# install Anaconda in silent mode
wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh -O ~/anaconda.sh
sh ~/anaconda.sh -b -p /home/ec2-user/anaconda
rm ~/anaconda.sh
echo 'export PATH=/home/ec2-user/anaconda/bin:$PATH' >> ~/.bashrc

source ~/.bashrc
conda install numpy pandas pymysql sqlalchemy flask flask-cors -y
pip install neo4j python-dotenv

# set up Neo4J through Docker
sudo amazon-linux-extras install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# download apoc library necessary for data structure predicates
mkdir -p /home/ec2-user/neo4j/plugins
cd /home/ec2-user/neo4j/plugins && wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/4.1.0.0/apoc-4.1.0.0-core.jar 

sudo docker run \
    -p7474:7474 -p7687:7687 \
    -d \
    --rm \
    -v /home/ec2-user/neo4j/data:/data \
    -v /home/ec2-user/neo4j/logs:/logs \
    -v /home/ec2-user/neo4j/import:/var/lib/neo4j/import \
    -v /home/ec2-user/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/test \
    --name prerequisites \
    neo4j:latest

# install Node.JS and corresponding required dependencies
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install node
cd /home/ec2-user/schedule-generator/client
npm install

# setting up website
npm run build
sudo cp build/* /var/www/html
sudo cp -r build/static/ /var/www/html/
cd /home/ec2-user/schedule-generator/server
sudo cp ./httpd.conf /etc/httpd/conf/httpd.conf

# setting up flask
cd api
tmux new-session -d -s backend 'flask run --host 0.0.0.0 --port 5000'

# run website
sudo service httpd start
