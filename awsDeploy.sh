# Install python and dependencies
sudo yum install python3 -y
sudo pip3 install -r requirements.txt

# Clone the repository
git clone https://github.com/cs298f25/SpotifyWebProject.git /home/ec2-user/SpotifyWebProject
cd /home/ec2-user/SpotifyWebProject

# Run the Flask application
python3 app.py