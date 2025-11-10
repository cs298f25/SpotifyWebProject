#!/bin/bash

# Install python
sudo yum update -y
sudo yum install python3 python3-pip git redis -y
sudo amazon-linux-extras install redis6 -y
sudo /home/ec2-user/SpotifyWebProject/.venv/bin/python3 -m pip install --upgrade pip

# Clone the repository
git clone https://github.com/cs298f25/SpotifyWebProject.git /home/ec2-user/SpotifyWebProject
cd /home/ec2-user/SpotifyWebProject

# Source the virtual environment script (activates venv)
source ./virtualEnvironment.sh

# Run Flask and Redis
sudo cp flask.service /etc/systemd/system
sudo cp redis.service /etc/systemd/system

sudo systemctl daemon-reload

sudo systemctl enable flask
sudo systemctl start flask

sudo systemctl enable redis
sudo systemctl start redis