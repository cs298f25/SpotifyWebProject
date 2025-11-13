let startButton, game, textbox;
let artistResult;

function connectStart() {
    game = document.getElementById("game")
    startButton = document.getElementById("start")
    startButton.onclick = startGame
}

async function startGame() {
    console.log("test")
    await fetch("/new-game"); // this is a get, so i don't need to do anything with json
    
    startButton.classList.add("hidden")
    game.classList.remove("hidden")
}

function connectTextbox() {
    textbox = document.getElementById("textbox");
    textbox.addEventListener("keydown", async (event) => {
        if (event.key !== "Enter") { return; }
        await textboxSubmit();
    })
}

async function textboxSubmit() {
    submission = textbox.value;

    const response = await fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "guess": submission })
    });

    const data = await response.json();
    alert(data.result);

    textbox.value = "";
}

async function loadArtist() {
    artistResult = document.getElementById("artistResult");
    if (!artistResult) { return; }

    const response = await fetch('/artist');
    const data = await response.json();
    artistResult.textContent = JSON.stringify(data, null, 2);
}

document.addEventListener("DOMContentLoaded", function() {
    connectStart();
    connectTextbox();
    loadArtist();
})


/*
require('dotenv').config(); // Load environment variables from .env file

const express = require('express');
const SpotifyWebApi = require('spotify-web-api-node');

const app = express();

const spotifyApi = new SpotifyWebApi({
    clientId: process.env.CLIENT_ID,
    clientSecret: process.env.CLIENT_SECRET,
    redirectUri: process.env.REDIRECT_URI, // TODO: Change to actual redirect URI
});
*/

