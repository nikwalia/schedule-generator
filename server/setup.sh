# Needs to be run with root permissions. Guaranteed to work only on an Amazon Linux Image.

# say yes to all installation
sudo -i
sudo echo "assumeyes=1" >> /etc/yum.conf
exit

# install Apache2 HTTP server
sudo yum update && sudo yum upgrade -y
sudo yum install httpd -y
sudo service httpd start
sudo chkconfig httpd on

# install Anaconda in silent mode
wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh -O ~/anaconda.sh
sh ~/anaconda.sh -b -p $HOME/anaconda
rm anaconda.sh
EXPORT PATH=$PATH:$HOME/anaconda/bin

conda install numpy pandas sqlalchemy -y
pip install neo4j

# set up Neo4J through Docker
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

sudo docker run \
    -p7474:7474 -p7687:7687 \
    -d \
    --rm \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/test \
    --name prerequisites \
    neo4j:latest

# track all keystrokes
mkdir logs
script logs/log.txt
