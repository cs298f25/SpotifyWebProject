let startButton, game, textbox;

//HELPERS FOR BUTTON LOADING
function showLoading(button, text = "Loading...") {
    if (!button) return;
    button.dataset.original = button.innerText;
    button.innerText = text;
    button.disabled = true;
}

function hideLoading(button) {
    if (!button || !button.dataset.original) return;
    button.innerText = button.dataset.original;
    button.disabled = false;
}


window.onload = () => {
    console.log("Loaded page & connecting buttons...");
    connectStart();
    connectTextbox();
    connectGuessButton();
};


function connectStart() {
    game = document.getElementById("game");
    startButton = document.getElementById("start");
    startButton.onclick = startGame;
}

async function startGame() {
    console.log("Starting new game...");

    showLoading(startButton, "Loading...");

    const response = await fetch("/new-game");
    hideLoading(startButton);

    if (!response.ok) {
        alert("Error starting a new game.");
        return;
    }

    startButton.classList.add("hidden");
    const preGameMessage = document.getElementById("pre-game-message");
    if (preGameMessage) {
        preGameMessage.classList.add("hidden");
    }
    game.classList.remove("hidden");

    // Clear old guesses & any old Game Over card
    document.getElementById("guesses").innerHTML = "";

    // Re-enable textbox + Guess button
    textbox.disabled = false;
    const guessButton = document.getElementById("guessButton");
    guessButton.disabled = false;
}


function connectGuessButton() {
    const guessButton = document.getElementById("guessButton");
    guessButton.onclick = async () => {
        showLoading(guessButton, "Checking...");
        await textboxSubmit();
        hideLoading(guessButton);
    };
}

function connectTextbox() {
    textbox = document.getElementById("textbox");
    textbox.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
            const guessButton = document.getElementById("guessButton");
            showLoading(guessButton, "Checking...");
            await textboxSubmit();
            hideLoading(guessButton);
        }
    });
}

async function textboxSubmit() {
    const submission = textbox.value.trim();
    if (!submission) return;

    const response = await fetch("/guess", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ guess: submission }),
    });

    let data;
    try {
        data = await response.json();
    } catch (e) {
        console.error("Failed to parse guess response:", e);
        alert("Server error while processing guess.");
        return;
    }

    if (!response.ok || data.error) {
        alert(data.message || "Error making guess.");
        return;
    }

    // Render the guess card
    renderGuessCard(data.comparison, data.guess_number, data.max_guesses);
    textbox.value = "";

    // Handle game status
    if (data.status === "WON") {
        renderGameOverCard(data.answer, true);
        disableGuessing();
    } else if (data.status === "LOST") {
        renderGameOverCard(data.answer, false);
        disableGuessing();
    }
}

function disableGuessing() {
    textbox.disabled = true;
    const guessButton = document.getElementById("guessButton");
    guessButton.disabled = true;
}



// RENDER GUESS CARD
function renderGuessCard(comparison, guessNumber, maxGuesses) {
    const container = document.getElementById("guesses");

    const card = document.createElement("div");
    card.classList.add("guess-card");

    const artist = comparison.guess_artist;
    const fields = comparison.fields;

    card.innerHTML = `
        <div class="guess-header">
            <span class="guess-title">🎤 ${artist.name}</span>
            <span class="guess-count">Guess ${guessNumber} of ${maxGuesses}</span>
        </div>
        <div class="divider"></div>

        <div class="guess-field-row">
            <span class="field-label">Gender</span>
            <span class="field-badge ${fields.gender}">
                ${artist.gender ?? "Unknown"}
            </span>
        </div>

        <div class="guess-field-row">
            <span class="field-label">Genre</span>
            <span class="field-badge ${fields.genre}">
                ${artist.tag ?? "Unknown"}
            </span>
        </div>

        <div class="guess-field-row">
            <span class="field-label">Country</span>
            <span class="field-badge ${fields.area}">
                ${artist.area?.name ?? "Unknown"}
            </span>
        </div>

        <div class="guess-field-row">
            <span class="field-label">Popularity</span>
            <span class="field-badge ${fields.popularity}">
                ${artist["spotify popularity"]}
            </span>
        </div>
    `;

    container.prepend(card);
}

// RENDER GAME OVER CARD
function renderGameOverCard(answer, didWin = false) {
    const container = document.getElementById("guesses");

    // Remove existing game-over if any
    const old = document.querySelector(".game-over-card");
    if (old) old.remove();

    const card = document.createElement("div");
    card.classList.add("game-over-card");

    const icon = didWin ? "✅" : "❌";
    const title = didWin ? "You Got It!" : "Game Over";
    const message = didWin ? "Nice job, you guessed the artist!" : "No guesses left.";

    const capitalizeGenre = (genre) => {
        if (!genre || genre === "Unknown") return genre;
        return genre.split(' ').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');
    };

    card.innerHTML = `
        <div class="go-title">${icon} ${title}</div>
        <div class="go-text">${message}</div>

        <div class="go-answer-header">Correct Artist:</div>
        <div class="go-answer">
            <strong>${answer.name}</strong><br>
            Gender: ${answer.gender ?? "Unknown"}<br>
            Genre: ${capitalizeGenre(answer.genre)}<br>
            Country: ${answer.area ?? "Unknown"}<br>
            Popularity: ${answer.popularity ?? "?"}
        </div>
    `;

    container.prepend(card);
}

