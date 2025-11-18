# API Documentation

This document describes how the application uses the Spotify API and MusicBrainz API.

## Environment Variables

The following environment variables must be set in your `.env` file:

**Spotify API:**
- `SPOTIFY_CLIENT_ID` (required): Your Spotify app's client ID
- `SPOTIFY_CLIENT_SECRET` (required): Your Spotify app's client secret

**MusicBrainz API:**
- `USER_EMAIL` (required): Your email address for MusicBrainz user agent identification

**Other:**
- `REDIS_HOST` (required): Redis server hostname (default: `localhost`)
- `REDIS_PORT` (required): Redis server port (default: `6379`)
- `SECRET_KEY` (optional): Flask secret key (auto-generated if not provided)

---

# Spotify Web API

## Overview
The Spotify API connects to Spotify and can deliver information about artists, playlists, tracks, albums, etc. Developer must make a Spotify developer account and must create an app from the dashboard to generate the client id and client secret. 

## Base URL
https://api.spotify.com/v1

## Authentication
The spotify api has four different way to authenticate; Authentication code, Authentication code with PKCE extension, client credentials. Purposes of this web project since we are only get general public information about artists, songs, etc. We will be using client credentials that allows us to do just that. When a spotify app is created from the dashboard in the spotify developer account, a client id and client secret will be generated with that app. A post request must then be made with the client id and client secret in order to get the bearer token or access token. Each token is only available for a hour.

## Spotify API Usage in This Application

The application uses Spotify API through helper functions in `src/spotify.py`. These functions are not exposed as Flask endpoints but are used internally by other parts of the application.

### Helper Functions

#### `_request_access_token()`

Internal function that authenticates with Spotify API using Client Credentials flow.

**What it does:**
- Retrieves `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` from environment variables
- Creates a Base64-encoded authorization header
- Makes a POST request to `https://accounts.spotify.com/api/token` with a 10-second timeout built in from the request library calls. (client safe guard)
- Returns the access token data

**Request Headers:**
- `Authorization: Basic {base64_encoded_credentials}`
- `Content-Type: application/x-www-form-urlencoded`

**Request Body:**
- `grant_type: client_credentials`

**Returns:**
```json
{
  "access_token": "BQD...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Note:** Tokens expire after 1 hour (3600 seconds). A new token is requested each time `get_artist_popularity()` is called.

#### `get_artist_popularity(query)`

Gets the popularity score of an artist by searching for them on Spotify.

**Parameters:**
- `query` (string, required): Artist name to search for (e.g., "Pitbull", "Taylor Swift")

**What it does:**
1. Calls `_request_access_token()` to get a bearer token
2. Searches Spotify API: `GET https://api.spotify.com/v1/search?q={query}&type=artist&limit=1` with a 10-second timeout
3. Extracts the popularity score from the first search result

**Request Headers:**
- `Authorization: Bearer {access_token}`

**Behavior:**
- Returns the popularity of the first matching artist
- If no artist is found, raises an `IndexError` (not handled internally)
- Popularity is calculated by Spotify based on total plays and how recent they are

**Returns:**
- `int`: Popularity score (0-100), where 100 is the most popular

**Example:**
```python
popularity = get_artist_popularity("Pitbull")
# Returns: 85
```

**Spotify API Endpoint Used:**
- `GET https://api.spotify.com/v1/search`
  - Query parameter: `q` - Search query string
  - Query parameter: `type=artist` - Search only for artists
  - Query parameter: `limit=1` - Return only the first result

## Integration in Application

The Spotify functionality is integrated into the following application endpoint (which also uses MusicBrainz data):

### `GET /musicbrain/search?q={artist_name}`

Returns combined MusicBrainz and Spotify data. Includes `spotify_popularity` field in the response.

**Query Parameters:**
- `q` (string, required): Artist name to search for

**HTTP Status Codes:**
- `200 OK`: Successful request
- `500 Internal Server Error`: Artist not found, API error, or missing environment variables

**Example Response:**
```json
{
  "name": "Pitbull",
  "type": "Person",
  "gender": "male",
  "life-span": {
    "begin": "1981-01-15",
    "ended": "false"
  },
  "area": {
    "name": "United States"
  },
  "spotify popularity": 85,
  "tag": "dance-pop"
}
```

### Rate Limiting
Spotify API enforces rate limits to prevent abuse. The rate limit is based on the number of calls your application makes within a rolling 30-second window. The exact limits may vary:
- Rate limits are applied per client ID
- Requests exceeding the limit will return `429 Too Many Requests` with a `Retry-After` header
- The application does not implement rate limiting or retry logic
- **Note**: For exact rate limit values, refer to the [official Spotify Web API documentation](https://developer.spotify.com/documentation/web-api)

### Errors

**Common Issues:**
- Developer could've not made a Spotify developer account
- Developer forgotten to enter both client id and client secret into a `.env` file
- Network or connectivity issues with the Spotify API that delays or prevents calls
- Artist not found in search results (raises `IndexError`)
- Invalid credentials (returns `401 Unauthorized`)
- Rate limit exceeded (returns `429 Too Many Requests`)

**Error Handling:**
- The application uses `response.raise_for_status()` which raises exceptions for HTTP errors
- No automatic retry logic is implemented
- Timeout is set to 10 seconds for all requests


## Versioning
The Spotify Web API currently supports only a single version (`v1`). 
All endpoints use the /v1/ prefix, and no alternative versions exist. 
Spotify manages updates internally and aims to maintain backward compatibility.

---

# MusicBrainz API

## Overview
MusicBrainz is an open music encyclopedia that collects music metadata. The application uses the `musicbrainzngs` Python library to interact with the MusicBrainz API.

## Base URL
https://musicbrainz.org/ws/2

## Authentication
MusicBrainz requires setting a user agent to identify your application. The user agent includes:
- Application name: "ArtistGuesser"
- Version: "2.0"
- Contact email: Set via `USER_EMAIL` environment variable (note developer must provide a email to establish a connection to the music brainz api)


## MusicBrainz API Usage in This Application

The application uses MusicBrainz API through functions in `src/musicbrain.py`. The main endpoint is exposed as a Flask route.

### Helper Functions

#### `_initialize_musicbrainz()`

Initializes the MusicBrainz client with a user agent.

**What it does:**
- Sets the user agent using `musicbrainzngs.set_useragent()`
- Uses `USER_EMAIL` from environment variables

#### `_get_full_artist_by_query(query)`

Searches for an artist and retrieves their full details.

**Parameters:**
- `query` (string, required): Artist name to search for

**What it does:**
1. Initializes MusicBrainz client
2. Searches for artists: `musicbrainzngs.search_artists(query=query, limit=1)`
3. Gets full artist details by MBID: `musicbrainzngs.get_artist_by_id(artist["id"], includes=["tags"])`

**Returns:**
- Full artist object with tags included

**Behavior:**
- Returns the first matching artist from search results
- If no artist is found, accessing `result["artist-list"][0]` will raise an `IndexError`
- Always requests tags in the includes parameter

#### `_filter_to_highest_tag(artist_data)`

Filters the tag list to only include the tag with the highest count.

**Parameters:**
- `artist_data` (dict): Artist data from MusicBrainz

**What it does:**
- Finds the tag with the highest `count` value
- Replaces the `tag-list` with only that tag

**Returns:**
- Modified artist data with filtered tag list

#### `get_artist_highest_tag(query)`

Gets the highest count tag for an artist.

**Parameters:**
- `query` (string, required): Artist name to search for

**Returns:**
- Tag object with highest count, or `None` if no tags found

**Example:**
```python
tag = get_artist_highest_tag("Pitbull")
# Returns: {"count": "7", "name": "dance-pop"}
```

### Flask Endpoints

#### `GET /musicbrain/search?q={artist_name}`

Searches for an artist and returns filtered data including Spotify popularity.

**Query Parameters:**
- `q` (string, required): Artist name to search for

**Response:**
```json
{
  "name": "Pitbull",
  "type": "Person",
  "gender": "male",
  "life-span": {
    "begin": "1981-01-15",
    "ended": "false"
  },
  "area": {
    "name": "United States"
  },
  "spotify popularity": 85,
  "tag": "dance-pop"
}
```

**MusicBrainz API Endpoints Used:**
- `musicbrainzngs.search_artists()` - Searches for artists
- `musicbrainzngs.get_artist_by_id()` - Gets full artist details with tags

### Rate Limiting
MusicBrainz API has rate limits:
- **Default**: 1 request per second per IP address
- Requests exceeding the limit will be throttled
- The application does not implement rate limiting or retry logic
- The `musicbrainzngs` library may handle some rate limiting automatically

### Errors
- Missing `USER_EMAIL` environment variable (may cause issues with user agent)
- No artists found for search query (raises `IndexError` when accessing `artist-list[0]`)
- Network or connectivity issues with MusicBrainz API
- Empty tag list (no tags available for artist) - returns `None` for tag field
- Invalid MBID format (if manually calling `get_artist_by_id()`)
- Rate limit exceeded (requests may be throttled or blocked)

**Error Handling:**
- The application does not catch or handle exceptions from MusicBrainz API calls
- Errors will propagate to Flask and return `500 Internal Server Error`
- Missing tags are handled gracefully (returns `None` instead of raising an error)
