#!/bin/bash

# Install python
sudo yum install python3 python3-pip git -y

# Clone the repository
git clone https://github.com/cs298f25/SpotifyWebProject.git /home/ec2-user/SpotifyWebProject
cd /home/ec2-user/SpotifyWebProject

# Install dependencies
sudo pip install -r requirements.txt

# Run the Flask application
python3 app.py