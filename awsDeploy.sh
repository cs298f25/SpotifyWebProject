#!/bin/bash

# Install python
sudo yum update -y
sudo yum install python3 python3-pip git -y
sudo /home/ec2-user/SpotifyWebProject/.venv/bin/python3 -m pip install --upgrade pip

# Clone the repository
git clone https://github.com/cs298f25/SpotifyWebProject.git /home/ec2-user/SpotifyWebProject
cd /home/ec2-user/SpotifyWebProject

# Source the virtual environment script (activates venv)
source ./virtualEnvironment.sh

# Run the Flask application
sudo cp flask.service /etc/systemd/system
sudo systemctl enable flask
sudo systemctl start flask
