# Needs to be run with root permissions. Guaranteed to work only on an Amazon Linux Image.

# install Apache2 HTTP server
sudo yum update && sudo yum upgrade -y
sudo yum install httpd -y
sudo service httpd start
sudo chkconfig httpd on

# install Anaconda in silent mode
wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh -O ~/anaconda.sh
sh ~/anaconda.sh -b -p $HOME/anaconda

# track all keystrokes
mkdir logs
script logs/log.txt
