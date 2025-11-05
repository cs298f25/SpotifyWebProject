# Local Deploy

Run `./localdeploy.sh` to run the Flask server locally on 

# AWS Deploy

Create a new EC2 instance. Allow inbound connections from port 80 (HTTP) and, under "Advanced details", upload `awsDeploy.sh` to the "User data" property. When the server has finished launching, Flask will have deployed itself.