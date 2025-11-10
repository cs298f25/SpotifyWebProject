#!/bin/bash

# Install python & Redis
sudo yum update -y
sudo yum install -y python3 python3-pip git
sudo amazon-linux-extras install -y redis6
sudo /home/ec2-user/SpotifyWebProject/.venv/bin/python3 -m pip install --upgrade pip

# Clone the repository
git clone https://github.com/cs298f25/SpotifyWebProject.git /home/ec2-user/SpotifyWebProject
cd /home/ec2-user/SpotifyWebProject

# Activate venv
source ./virtualEnvironment.sh

# Install and start services
sudo cp flask.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now redis
sudo systemctl enable --now flask