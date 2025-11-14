# Spotify Web API

## Overview
The Spotify api connects to spotify and can deliver information about artists, playlist, tracks, albums, etc. Developer must make a spotify developer account and must create a app from the dashboard to generate the client id and client secret 

## Base URL
https://api.spotify.com/v1

## Authentication
The spotify api has four different way to authenticate; Authentication code, Authentication code with PKCE extension, client credentials. Purposes of this web project since we are only get general public information about artists, songs, etc. We will be using client credentials that allows us to do just that. When a spotify app is created from the dashboard in the spotify developer account, a client id and client secret will be generated with that app. A post request must then be made with the client id and client secret in order to get the bearer token or access token. Each token is only available for a hour.

## Endpoints


### GET /artist/{id}
Endpoint gets details about a artist using their artist id given by Spotify

#### Path Parameters
- id (string): The ID of the user. (Literally just the id of Pitbull right now )


#### Response Example
{
  "external_urls": {
    "spotify": "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg"
  },
  "followers": {
    "href": null,
    "total": 11984460
  },
  "genres": [],
  "href": "https://api.spotify.com/v1/artists/0TnOYISbd1XYRBk9myaseg?locale=en-US%2Cen%3Bq%3D0.9",
  "id": "0TnOYISbd1XYRBk9myaseg",
  "images": [
    {
      "url": "https://i.scdn.co/image/ab6761610000e5eb8d8ac7290d0fe2d12fb6e4d9",
      "height": 640,
      "width": 640
    },
    {
      "url": "https://i.scdn.co/image/ab676161000051748d8ac7290d0fe2d12fb6e4d9",
      "height": 320,
      "width": 320
    },
    {
      "url": "https://i.scdn.co/image/ab6761610000f1788d8ac7290d0fe2d12fb6e4d9",
      "height": 160,
      "width": 160
    }
  ],
  "name": "Pitbull",
  "popularity": 84,
  "type": "artist",
  "uri": "spotify:artist:0TnOYISbd1XYRBk9myaseg"
}

### Errors
- Developer could've not made a spotify developer account 
- Developer forgotten to enter in both client id and client secret ito a .env file
- There could be network or connectivity issues with the spotify api that delays or prevents calls


## Versioning
The Spotify Web API currently supports only a single version (`v1`). 
All endpoints use the /v1/ prefix, and no alternative versions exist. 
Spotify manages updates internally and aims to maintain backward compatibility.
