const board = ['', '', '', '', '', '', '', '', ''];
const humanPlayer = 'X';
const aiPlayer = 'O';
let currentPlayer = humanPlayer;
let gameActive = true;
let difficulty = 'hard'; // Default difficulty

const gameBoard = document.getElementById('game-board');
const gameMessage = document.getElementById('game-message');
const resetButton = document.getElementById('reset-button');
const difficultySelect = document.getElementById('difficulty');

const winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
];

function initializeGame() {
    gameBoard.innerHTML = '';
    board.fill('');
    currentPlayer = humanPlayer;
    gameActive = true;
    gameMessage.textContent = `It's ${currentPlayer}'s turn`;
    difficulty = difficultySelect.value; // Set difficulty from dropdown

    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.classList.add('cell');
        cell.dataset.index = i;
        cell.addEventListener('click', handleCellClick);
        gameBoard.appendChild(cell);
    }
}

function handleCellClick(event) {
    const clickedCell = event.target;
    const clickedCellIndex = parseInt(clickedCell.dataset.index);

    if (board[clickedCellIndex] !== '' || !gameActive || currentPlayer === aiPlayer) {
        return;
    }

    handlePlayerMove(clickedCell, clickedCellIndex);
    checkGameStatus();

    if (gameActive && currentPlayer === aiPlayer) {
        setTimeout(handleAIMove, 500);
    }
}

function handlePlayerMove(cell, index) {
    board[index] = currentPlayer;
    cell.textContent = currentPlayer;
    cell.classList.add(currentPlayer.toLowerCase());
}

function changePlayer() {
    currentPlayer = currentPlayer === humanPlayer ? aiPlayer : humanPlayer;
    gameMessage.textContent = `It's ${currentPlayer}'s turn`;
}

function checkGameStatus() {
    let roundWon = false;
    for (let i = 0; i < winningConditions.length; i++) {
        const winCondition = winningConditions[i];
        let a = board[winCondition[0]];
        let b = board[winCondition[1]];
        let c = board[winCondition[2]];

        if (a === '' || b === '' || c === '') {
            continue;
        }
        if (a === b && b === c) {
            roundWon = true;
            break;
        }
    }

    if (roundWon) {
        gameMessage.textContent = `${currentPlayer} has won!`;
        gameActive = false;
        return;
    }

    let roundDraw = !board.includes('');
    if (roundDraw) {
        gameMessage.textContent = `Game ended in a draw!`;
        gameActive = false;
        return;
    }

    changePlayer();
}

// Minimax Algorithm
function minimax(newBoard, player) {
    const availableSpots = newBoard.map((s, i) => (s === '' ? i : null)).filter(s => s !== null);

    if (checkWin(newBoard, humanPlayer)) {
        return { score: -10 };
    } else if (checkWin(newBoard, aiPlayer)) {
        return { score: 10 };
    } else if (availableSpots.length === 0) {
        return { score: 0 };
    }

    const moves = [];
    for (let i = 0; i < availableSpots.length; i++) {
        const move = {};
        move.index = availableSpots[i];
        newBoard[availableSpots[i]] = player;

        if (player === aiPlayer) {
            const result = minimax(newBoard, humanPlayer);
            move.score = result.score;
        } else {
            const result = minimax(newBoard, aiPlayer);
            move.score = result.score;
        }

        newBoard[availableSpots[i]] = ''; // Reset the spot
        moves.push(move);
    }

    let bestMove;
    if (player === aiPlayer) {
        let bestScore = -Infinity;
        for (let i = 0; i < moves.length; i++) {
            if (moves[i].score > bestScore) {
                bestScore = moves[i].score;
                bestMove = i;
            }
        }
    } else {
        let bestScore = Infinity;
        for (let i = 0; i < moves.length; i++) {
            if (moves[i].score < bestScore) {
                bestScore = moves[i].score;
                bestMove = i;
            }
        }
    }

    return moves[bestMove];
}

function checkWin(currentBoard, player) {
    return winningConditions.some(condition => {
        return condition.every(index => {
            return currentBoard[index] === player;
        });
    });
}

function getAvailableSpots(currentBoard) {
    return currentBoard.map((s, i) => (s === '' ? i : null)).filter(s => s !== null);
}

function handleAIMove() {
    let bestSpot;
    const availableSpots = getAvailableSpots(board);

    if (difficulty === 'easy') {
        bestSpot = availableSpots[Math.floor(Math.random() * availableSpots.length)];
    } else if (difficulty === 'medium') {
        // Try to win
        for (let i = 0; i < availableSpots.length; i++) {
            const tempBoard = [...board];
            tempBoard[availableSpots[i]] = aiPlayer;
            if (checkWin(tempBoard, aiPlayer)) {
                bestSpot = availableSpots[i];
                break;
            }
        }
        // Block human player
        if (bestSpot === undefined) {
            for (let i = 0; i < availableSpots.length; i++) {
                const tempBoard = [...board];
                tempBoard[availableSpots[i]] = humanPlayer;
                if (checkWin(tempBoard, humanPlayer)) {
                    bestSpot = availableSpots[i];
                    break;
                }
            }
        }
        // Otherwise, random move
        if (bestSpot === undefined) {
            bestSpot = availableSpots[Math.floor(Math.random() * availableSpots.length)];
        }
    } else { // 'hard' difficulty
        bestSpot = minimax(board, aiPlayer).index;
    }

    const cell = document.querySelector(`[data-index="${bestSpot}"]`);
    handlePlayerMove(cell, bestSpot);
    checkGameStatus();
}

resetButton.addEventListener('click', initializeGame);
difficultySelect.addEventListener('change', initializeGame);

initializeGame();
