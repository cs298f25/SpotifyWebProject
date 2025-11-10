# SpotifyWebProject

Spotify Web Project.


* Create a file `.env` that contains the hostname and port number for Redis.  To Run Redis, we be using (`localhost`) and using the standard Redis port (6379). 

  ```
  REDIS_HOST=localhost
  REDIS_PORT=6379
  ```

## Redis Setup

* (If needed) Install [Homebrew](https://brew.sh/)

    ```
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
* Install Redis on your system

    ```
    brew install redis
    ```


## Running index.html file locally

We will need launch the system in two terminal windows 

* Terminal #1 (in the project root) Launch redis: 

  ```
  redis-server
  ```
* Terminal #2 (in the project root) Launch the server: 


  ```
  source .venv/bin/activate
  python app.py
  ```

## Members 
- Louis Spann
- Jack Wagenheim
- Mohammad Alzoubi
