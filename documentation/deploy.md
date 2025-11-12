
# .env Instructions
Create a file `.env` that contains the following information:

## Redis
Change values as is necessary, but these default values will work automatically.

```
REDIS_HOST=localhost
REDIS_PORT=6379
```

# Local Deploy

Begin by following the .env instructions to create your environment variables. Then, run `./localdeploy.sh` to run the Flask server locally.

# AWS Deploy

Create a new EC2 instance. Allow inbound connections from port 80 (HTTP) and upload `awsPrepare.sh` to the "User data" property under "Advanced details".

At this point in the process, you must follow the .env instructions.

To finalize deployment, run `awsDeploy.sh`, which will finish launching the server.

**WE NEED INFO ABOUT SPOTIFY CLIENT**