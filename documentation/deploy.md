# Local Deploy

Run `./localdeploy.sh` to run the Flask server locally on 

# AWS Deploy

Create a new EC2 instance. Allow inbound connections from port 80 (HTTP) and upload `awsPrepare.sh` to the "User data" property under "Advanced details".

For Redis, we will default to using `localhost` and port 6379, the default Redis port. If you want to use a different host and port, create a file `.env` that contains the following information:

```
REDIS_HOST=<host>
REDIS_PORT=<port-number>
```

To finalize deployment, run `awsDeploy.sh`, which will finish launching the server.

**WE NEED INFO ABOUT SPOTIFY CLIENT**