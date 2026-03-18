const board = document.querySelector("#board");

const BOARD_SIZE = 42;
const BOARD_COLS = 6;
const BOARD_ROWS = Math.ceil(BOARD_SIZE / BOARD_COLS);
document.documentElement.style.setProperty("--cols", String(BOARD_COLS));
document.documentElement.style.setProperty("--rows", String(BOARD_ROWS));
document.body.classList.add("boardImage");

const questionBank = Array.isArray(window.QUESTION_BANK)
  ? window.QUESTION_BANK
  : [];
let unusedQuestionIndexes = [];
let questionsUsedCount = 0;

const shuffleInPlace = (arr) => {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
  }
  return arr;
};

const refillQuestionPool = () => {
  unusedQuestionIndexes = [];
  for (let i = 0; i < questionBank.length; i++) unusedQuestionIndexes.push(i);
  shuffleInPlace(unusedQuestionIndexes);
};

const pickNextQuestion = () => {
  if (questionBank.length === 0) return null;
  if (unusedQuestionIndexes.length === 0) refillQuestionPool();
  const idx = unusedQuestionIndexes.pop();
  return questionBank[idx] || null;
};

const quizModal = document.querySelector("#quizModal");
const quizPlayerName = document.querySelector("#quizPlayerName");
const quizTimer = document.querySelector("#quizTimer");
const quizDiceValue = document.querySelector("#quizDiceValue");
const quizQuestion = document.querySelector("#quizQuestion");
const quizChoices = document.querySelector("#quizChoices");
const quizAnswer = document.querySelector("#quizAnswer");
const quizTimerVideo = document.querySelector("#quizTimerVideo");
const revealAnswerBtn = document.querySelector("#revealAnswerBtn");
const markCorrectBtn = document.querySelector("#markCorrectBtn");
const markWrongBtn = document.querySelector("#markWrongBtn");

let quizCountdownInterval = null;
let pendingRoll = null;

const clearQuizCountdown = () => {
  if (quizCountdownInterval) {
    clearInterval(quizCountdownInterval);
    quizCountdownInterval = null;
  }
};

const closeQuizModal = () => {
  clearQuizCountdown();
  if (quizTimerVideo) {
    quizTimerVideo.pause();
    quizTimerVideo.currentTime = 0;
  }
  if (quizModal) quizModal.className = "modal hide";
};

const openQuizModalForPlayer = (playerNo, diceDisplay) => {
  if (!quizModal) return;

  const q = pickNextQuestion();
  const player = players[playerNo - 1];

  if (q) {
    questionsUsedCount += 1;
    console.log(
      `[Quiz] Player ${playerNo} | Dice ${diceDisplay} | Used ${questionsUsedCount}/${questionBank.length}`
    );
  }

  quizPlayerName.textContent = player ? player.name : `Player ${playerNo}`;
  quizDiceValue.textContent = String(diceDisplay);

  if (!q) {
    quizQuestion.textContent =
      "Chưa có dữ liệu câu hỏi. Hãy kiểm tra questions.js / questions.json.";
    quizChoices.innerHTML = "";
    quizAnswer.textContent = "";
    quizAnswer.className = "quizAnswer hide";
    revealAnswerBtn.disabled = true;
  } else {
    quizQuestion.textContent = q.prompt || "";
    quizChoices.innerHTML = (q.choices || [])
      .map(
        (c) =>
          `<div class="quizChoice"><span class="quizChoiceKey">${c.key}.</span>${c.text}</div>`
      )
      .join("");
    quizAnswer.textContent = "";
    quizAnswer.className = "quizAnswer hide";
    revealAnswerBtn.disabled = false;
    revealAnswerBtn.onclick = () => {
      const correctKey = (q.answer || "").toUpperCase();
      const correctChoice = (q.choices || []).find(
        (c) => (c.key || "").toUpperCase() === correctKey
      );
      const answerText = correctChoice ? correctChoice.text : "";
      quizAnswer.textContent = answerText
        ? `Đáp án: ${correctKey}. ${answerText}`
        : `Đáp án: ${correctKey}`;
      quizAnswer.className = "quizAnswer";
    };
  }

  // Timer: 15s thinking time
  clearQuizCountdown();
  let secondsLeft = 15;
  quizTimer.textContent = `${secondsLeft}s`;
  quizCountdownInterval = setInterval(() => {
    secondsLeft--;
    if (secondsLeft <= 0) {
      quizTimer.textContent = "0s (hết giờ)";
      clearQuizCountdown();
      return;
    }
    quizTimer.textContent = `${secondsLeft}s`;
  }, 1000);

  // Resolve handlers
  markCorrectBtn.disabled = false;
  markWrongBtn.disabled = false;
  markCorrectBtn.onclick = () => {
    if (pendingRoll) pendingRoll.resolve(true);
  };
  markWrongBtn.onclick = () => {
    if (pendingRoll) pendingRoll.resolve(false);
  };

  if (quizTimerVideo) {
    quizTimerVideo.currentTime = 0;
    quizTimerVideo.play().catch(() => {});
  }

  quizModal.className = "modal";
};

// For the movement of pots
const colorsPots = [
  "redPot",
  "bluePot",
  "greenPot",
  "yellowPot",
  "purplePot",
  "orangePot",
];

// For Audio
const drop = document.querySelector("#drop");
const ladder = document.querySelector("#ladder");
const snake = document.querySelector("#snake");
const diceAudio = document.querySelector("#diceAudio");
const success = document.querySelector("#success");

// For showing the winner message
const modal = document.querySelector("#modal");
const wname = document.querySelector("#wname");
const wimg = document.querySelector("#wimg");

// Path of ladders
let ladders = [
  [2, 15],
  [7, 28],
  [14, 27],
  [19, 32],
  [25, 38],
];
// Path for snakes
let snakes = [
  [41, 24],
  [35, 21],
  [30, 9],
  [13, 3],
  [10, 6],
];

// Dice probabilities array
const diceArray = [1, 2, 3, 4, 5, 6];
// Used for looping players chances
const playerNumbers = [1, 2, 3, 4, 5, 6];
// Dice icon according to random dice value
const diceIcons = [
  "fa-dice-one",
  "fa-dice-two",
  "fa-dice-three",
  "fa-dice-four",
  "fa-dice-five",
  "fa-dice-six",
];
// Array of object for tracking user
const players = [
  {
    name: "Player 1",
    image: 1,
    lastDice: 0,
    score: 0,
    lastMovement: 0,
  },
  {
    name: "Player 2",
    image: 0,
    lastDice: 0,
    score: 0,
    lastMovement: 0,
  },
  {
    name: "Player 3",
    image: 3,
    lastDice: 0,
    score: 0,
    lastMovement: 0,
  },
  {
    name: "Player 4",
    image: 4,
    lastDice: 0,
    score: 0,
    lastMovement: 0,
  },
  {
    name: "Player 5",
    image: 5,
    lastDice: 0,
    score: 0,
    lastMovement: 0,
  },
  {
    name: "Player 6",
    image: 6,
    lastDice: 0,
    score: 0,
    lastMovement: 0,
  },
];
// Multiple screens on the page
const screen1 = document.querySelector("#screen1");
const screen2 = document.querySelector("#screen2");
const screen3 = document.querySelector("#screen3");

// Tracking the current player
let currentPlayer = 1;
const winners = [];
const finishedPlayers = new Set();

const maxWinners = () => {
  if (playersCount > 4) return 2;
  return 1;
};

const getNextActivePlayer = (fromPlayer) => {
  let next = fromPlayer;
  for (let i = 0; i < playersCount; i++) {
    next = playerNumbers[next % playersCount];
    if (!finishedPlayers.has(next)) return next;
  }
  return fromPlayer;
};

// Create a board where pots are placed
const drawBoard = () => {
  let content = "";
  for (let renderRow = 0; renderRow < BOARD_ROWS; renderRow++) {
    // Map top-to-bottom render rows to bottom-to-top logical rows.
    const logicalRow = BOARD_ROWS - 1 - renderRow;
    const rowStart = logicalRow * BOARD_COLS + 1;
    const leftToRight = logicalRow % 2 === 0;

    if (leftToRight) {
      for (let step = 0; step < BOARD_COLS; step++) {
        const n = rowStart + step;
        content += `<div class="box" id="potBox${n}" data-num="${n}"></div>`;
      }
    } else {
      for (let step = BOARD_COLS - 1; step >= 0; step--) {
        const n = rowStart + step;
        content += `<div class="box" id="potBox${n}" data-num="${n}"></div>`;
      }
    }
  }
  board.innerHTML = content;
};

// Initial state at the beginning of the game
const initialState = () => {
  drawBoard();
  screen2.style.display = "none";
  screen3.style.display = "none";

  const questionCountEl = document.querySelector("#questionCount");
  if (questionCountEl) {
    questionCountEl.textContent = `Question bank: ${questionBank.length} questions loaded`;
  }

  refillQuestionPool();
};

initialState();

// Select players for game
let playersCount = 1;
const selectBox = document.getElementsByClassName("selectBox");
const selectPlayers = (value) => {
  selectBox[playersCount - 1].className = "selectBox";
  selectBox[value - 1].className = "selectBox selected";
  playersCount = value;
};

// To start the game
const start = () => {
  screen1.style.display = "none";
  screen2.style.display = "block";
  hideUnwantedPlayers();
};

// To back user to previous screen
const back = () => {
  screen2.style.display = "none";
  screen1.style.display = "block";
  resetPlayersCount();
};

// Next the user from screen 2 to screen 3
const next = () => {
  screen2.style.display = "none";
  screen3.style.display = "block";
  hideFinalPlayers();
  displayNames();
  disableDices();
};

// Reset the number of players in the add profile screen
const resetPlayersCount = () => {
  for (let i = 2; i < 7; i++) {
    let x = "card" + i;
    document.getElementById(x).style.display = "flex";
  }
};
// Hide unwanted Players according to the player count
const hideUnwantedPlayers = () => {
  for (let i = playersCount + 1; i < 7; i++) {
    let x = "card" + i;
    document.getElementById(x).style.display = "none";
  }
};
// Hide the final screen 3 players
const hideFinalPlayers = () => {
  for (let i = playersCount + 1; i < 7; i++) {
    let x = "playerCard" + i;
    document.getElementById(x).style.display = "none";
  }
};
// Display the name and profile icon for the users
const displayNames = () => {
  for (let i = 1; i < playersCount + 1; i++) {
    const baseURL = "images/avatars/";
    let x = "displayName" + i;
    let y = "avatar" + i;
    document.getElementById(x).innerHTML = players[i - 1].name;
    document.getElementById(y).src = baseURL + players[i - 1].image + ".png";
  }
};
// Update the name and profile icon for the users
const updateUserProfile = (playerNo, value) => {
  // Change profile to next profile in order
  const baseURL = "images/avatars/";
  if (value === 1) {
    players[playerNo - 1].image = (players[playerNo - 1].image + 1) % 8;
  } else {
    if (players[playerNo - 1].image === 0) {
      players[playerNo - 1].image = 7;
    } else {
      players[playerNo - 1].image = Math.abs(
        (players[playerNo - 1].image - 1) % 8
      );
    }
  }
  let x = "profile" + playerNo;
  document.getElementById(x).src =
    baseURL + players[playerNo - 1].image + ".png";
};
// Change the name of the player from input box
const changeName = (playerNo) => {
  let x = "name" + playerNo;
  let value = document.getElementById(x).value;
  if (value.length > 0) {
    players[playerNo - 1].name = value;
  } else {
    players[playerNo - 1].name = "Player" + playerNo;
  }
};

// Called by name input `onblur` in the HTML
const updateValue = (playerNo) => {
  changeName(playerNo);
};
// Clean the board with no pots
const resetBoard = () => {
  for (let i = 1; i < BOARD_SIZE + 1; i++) {
    document.getElementById("potBox" + i).innerHTML = "";
  }
};
// Refresh the board after every dice roll
const updateBoard = () => {
  resetBoard();
  for (let i = 0; i < playersCount; i++) {
    if (players[i].score != 0) {
      let x = "potBox" + players[i].score;
      document.getElementById(
        x
      ).innerHTML += `<div class="pot ${colorsPots[i]} slot${i}"></div>`;
    }
  }
};

// Used for moving pot from one place to another (legacy, no longer used)
// Used for moving pot from one place to another
const movePot = (value, playerNumber) => {
  const player = players[playerNumber - 1];
  const start = player.score;
  let end = start + value;

  if (end > BOARD_SIZE) end = BOARD_SIZE;
  if (end <= start) return;

  const steps = end - start;
  let moved = 0;

  const t = setInterval(() => {
    player.score += 1;
    drop.currentTime = 0;
    drop.play();
    updateBoard();
    moved += 1;

    if (moved >= steps) {
      clearInterval(t);

      if (end === BOARD_SIZE) {
        if (!finishedPlayers.has(playerNumber)) {
          finishedPlayers.add(playerNumber);
          winners.push(player.name);
          alert(`${player.name} da ve dich!`);
        }

        if (winners.length >= maxWinners()) {
          modal.className = "modal";
          success.play();
          const baseURL = "images/avatars/";
          wimg.src = baseURL + player.image + ".png";
          wname.innerHTML = winners.slice(0, maxWinners()).join(" & ");
        }
      } else {
        checkLadder(player.score, playerNumber);
        checkSnake(player.score, playerNumber);
      }
    }
  }, 400);
};

// For random dice value
const rollDice = (playerNo) => {
  if (playerNo === currentPlayer) {
    diceAudio.play();
    const diceNumber = diceArray[Math.floor(Math.random() * diceArray.length)];
    const isBonusTurnRoll = diceNumber === 1 || diceNumber === 6;
    const diceDisplay = `${diceNumber}`;
    let x = "dice" + playerNo;

    document.getElementById(x).innerHTML = `<i class="diceImg fas ${
      diceIcons[diceNumber - 1]
    }"></i>`;

    const tempCurrentPlayer = currentPlayer;
    currentPlayer = 0;
    disableDices();

    // Show dice first for a few seconds, then ask question before moving
    setTimeout(() => {
      const decision = new Promise((resolve) => {
        pendingRoll = { resolve };
        openQuizModalForPlayer(tempCurrentPlayer, diceDisplay);
      }).then((isCorrect) => {
        pendingRoll = null;
        closeQuizModal();
        return Boolean(isCorrect);
      });

      decision.then((isCorrect) => {
        if (isCorrect) {
          // Move the current players pot
          setTimeout(() => {
            movePot(diceNumber, tempCurrentPlayer);
          }, 300);
          setTimeout(() => {
            if (finishedPlayers.has(tempCurrentPlayer)) {
              currentPlayer = getNextActivePlayer(tempCurrentPlayer);
            } else if (isBonusTurnRoll) {
              currentPlayer = tempCurrentPlayer;
            } else {
              currentPlayer = getNextActivePlayer(tempCurrentPlayer);
            }
            document.getElementById("dice" + currentPlayer).style.color = "";
            disableDices();
          }, 1000 + diceNumber * 400);
        } else {
          // Wrong answer: stay still, next player immediately
          setTimeout(() => {
            currentPlayer = getNextActivePlayer(tempCurrentPlayer);
            document.getElementById("dice" + currentPlayer).style.color = "";
            disableDices();
          }, 300);
        }
      });
    }, 4000);
  }
};
// Disable Other player's dice that are not current player
const disableDices = () => {
  for (let i = 1; i < playersCount + 1; i++) {
    if (currentPlayer != i) {
      let x = "dice" + i;
      document.getElementById(x).style.color = "grey";
      continue;
    }
    if (finishedPlayers.has(i)) {
      let x = "dice" + i;
      document.getElementById(x).style.color = "grey";
    }
  }
};

// Check the current player is on ladder or not
const checkLadder = (value, playerNumber) => {
  for (let i = 0; i < ladders.length; i++) {
    if (ladders[i][0] === value) {
      specialMove(i, playerNumber);
    }
  }
};
// Check the current player is on snake or not
const checkSnake = (value, playerNumber) => {
  for (let i = 0; i < snakes.length; i++) {
    if (snakes[i][0] === value) {
      specialMoveSnake(i, playerNumber);
    }
  }
};
// Move the pot on the ladder
const specialMove = (value, playerNumber) => {
  let i = 0;
  var t = setInterval(() => {
    players[playerNumber - 1].score = ladders[value][i];
    ladder.play();
    updateBoard();
    i++;
    if (i === ladders[value].length) {
      clearInterval(t);
    }
  }, 400);
};
// Move the pot according to snake
const specialMoveSnake = (value, playerNumber) => {
  let i = 0;
  snake.play();
  var t = setInterval(() => {
    players[playerNumber - 1].score = snakes[value][i];
    updateBoard();
    i++;
    if (i === snakes[value].length) {
      clearInterval(t);
    }
  }, 400);
};
