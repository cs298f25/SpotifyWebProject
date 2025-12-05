![System Architecture](Screenshot%202025-12-05%20at%203.16.29%20PM.png)

# SpotifyWebProject
### By Louis Spann, Jack Wagenheim, & Mohammad Alzoubi

This a simple web application that make a copy of a version the of [Spotle](https://spotle.io/). Spotle is a Spotify-artist version of Wordle. You guess a Spotify artist, and it will tell you the correctness of your guesses until you guess the correct one or run out of guesses. Players will search for a Spotify artist’s name and be returned with that artist’s name and characteristics. 
Using attributes such as an artist’s gender, country, genre, and popularity, players will attempt to identify the correct artist. 
Each guess reveals how closely the guessed artist’s characteristics match those of the correct artist, helping players narrow down the answer.

### Game Logic
Green= match 
Black= no match 
Blue= popularity is higher
Orange= popularity is lower

There is a limit of 7 total guesses before a player loses the game and the correct artist is revealed 

# External APIs
This web application uses the music Musicbrainz and Spotify APIs to collect information about public artist's data. For further information about the external or interal APIs used for this web application, reference the API markdown file in this repository 

# Scripts 
**localdeploy.sh shell script** 
Local deploy script 
- Starts virtual environment
- Starts redis in the background 
- Once redis is up and running, uses systemd to start the application

**awsPrepare.sh shell script**
Prepare script 
- Uploaded to EC2 instance when created 
- It installs git and redis before
- Git cloning the project into the instance
- Finishes by activates virtual environment
- Now you have to make your .env

**awsDeploy.sh shell script**
- Starts flask and redis on systemd

# Application Setup

## Musicbrainz
1. Must have a email created and can be used with web application 

## Spotify
1. Must create a spotify account 
    - This account is only needed in order to create a developer account. For the purposes of this web application, no user information will be accessed 

2. Go to [Spotify Developer](https://developer.spotify.com/) and sign in using your spotify account credentials 
    - You will be prompted to authenticate and must enter a verification code 

3. Go to the developer dashboard in the website 

4. You must then create a create app
    - Create a name and description for your app.
    - For the Redirect URI use 
    ```
    http://127.0.0.1:3000**
    ```
    - Choose Web API for the API/SDK you want to use for the app
    - Agree to Spotify's terms and conditions 
    - Click save to create the app 

# .env Instructions
Create a file `.env` within the directory that contains the following information:

## Redis
Change values as is necessary, but these default values will work automatically.

```
REDIS_HOST=localhost
REDIS_PORT=6379
```
## Spotify
Get your Spotify client id and secret from an app from your [Spotify developer dashboard](https://developer.spotify.com/).

```
SPOTIFY_CLIENT_ID=<client_id>
SPOTIFY_CLIENT_SECRET=<client_secret>
```
## Musicbrainz
2. Add an email for Musicbrainz to use to authenticate.

```
USER_EMAIL=<email>
```

# Local Deploy

1. Begin by following the .env instructions to create your environment variables. 
2. Run `./localdeploy.sh` to run the Flask server locally.

# AWS Deploy

## Creating a EC2 Instance 
1. Open AWS Managment Console
2. In the search box to the top right of AWS Managment Console, search for and choose EC2 to open the AWS EC2 console
3. Choose Launch Instance
   
   **Instance Name:** ec2EventsManager
   
   **Amazon Machine Image:** Keep Amazon Linux
   
   **Instance Type:** Keep t2.mirco
   
   **Key pair:** select the dropdown and choose vockey
   
   **Security Group:** Select to allow Inbound connections from port 80 (HTTP)

   **Under "Advanced details" upload `awsPrepare.sh` to the "User data" property**
   
   **Keep the rest of the default settings and choose Launch Instance**

1. From there, get the public IP from the instance, and ssh into it.

2. At this point in the process, you must follow the .env instructions.

3. To finalize deployment, run `sudo ./awsDeploy.sh`, which will finish launching the server.
