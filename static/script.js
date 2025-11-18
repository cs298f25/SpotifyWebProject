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

function connectMusicbrainSearch() {
    const searchButton = document.getElementById("musicbrainSearchButton");
    const searchInput = document.getElementById("musicbrainSearchInput");
    
    // if the user clicks the search button, perform the artist search
    searchButton.onclick = async () => {
        await performMusicbrainSearch();
    };
    
    // if the user presses enter, perform the artist search
    searchInput.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
            await performMusicbrainSearch();
        }
    });
}

async function performMusicbrainSearch() {
    const searchInput = document.getElementById("musicbrainSearchInput");
    const resultElement = document.getElementById("musicbrainSearchResult");
    
    const query = searchInput.value.trim();
    
    const response = await fetch(`/musicbrain/search?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    resultElement.textContent = JSON.stringify(data, null, 2);
}

document.addEventListener("DOMContentLoaded", function() {
    connectStart();
    connectTextbox();
    connectMusicbrainSearch();
})


