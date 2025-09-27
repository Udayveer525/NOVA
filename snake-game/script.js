const gameCanvas = document.getElementById('gameCanvas');
const ctx = gameCanvas.getContext('2d');
const startButton = document.getElementById('startButton');

const gridSize = 20;
let snake;
let food;
let score;
let direction;
let gameInterval;
let gameSpeed = 150; // milliseconds

function initializeGame() {
    snake = [
        { x: 10 * gridSize, y: 10 * gridSize }
    ];
    food = generateFood();
    score = 0;
    direction = 'right';
    gameSpeed = 150; // Reset speed
    if (gameInterval) {
        clearInterval(gameInterval);
    }
    draw();
}

function generateFood() {
    let newFood;
    while (true) {
        newFood = {
            x: Math.floor(Math.random() * (gameCanvas.width / gridSize)) * gridSize,
            y: Math.floor(Math.random() * (gameCanvas.height / gridSize)) * gridSize
        };
        let collisionWithSnake = false;
        for (let i = 0; i < snake.length; i++) {
            if (snake[i].x === newFood.x && snake[i].y === newFood.y) {
                collisionWithSnake = true;
                break;
            }
        }
        if (!collisionWithSnake) {
            return newFood;
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);

    // Draw snake
    for (let i = 0; i < snake.length; i++) {
        ctx.fillStyle = (i === 0) ? 'green' : 'lime';
        ctx.fillRect(snake[i].x, snake[i].y, gridSize, gridSize);
        ctx.strokeStyle = 'darkgreen';
        ctx.strokeRect(snake[i].x, snake[i].y, gridSize, gridSize);
    }

    // Draw food
    ctx.fillStyle = 'red';
    ctx.strokeStyle = 'darkred';
    ctx.fillRect(food.x, food.y, gridSize, gridSize);
    ctx.strokeRect(food.x, food.y, gridSize, gridSize);

    // Display score (optional, can add a dedicated score element later)
    ctx.fillStyle = 'white';
    ctx.font = '15px Arial';
    ctx.fillText('Score: ' + score, 10, 20);
}

function update() {
    const head = { x: snake[0].x, y: snake[0].y };

    switch (direction) {
        case 'up':
            head.y -= gridSize;
            break;
        case 'down':
            head.y += gridSize;
            break;
        case 'left':
            head.x -= gridSize;
            break;
        case 'right':
            head.x += gridSize;
            break;
    }

    // Check for collision with walls
    if (head.x < 0 || head.x >= gameCanvas.width ||
        head.y < 0 || head.y >= gameCanvas.height) {
        gameOver();
        return;
    }

    // Check for collision with self
    for (let i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            gameOver();
            return;
        }
    }

    snake.unshift(head);

    // Check for food eaten
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        food = generateFood();
        // Optionally increase speed
        if (gameSpeed > 50) {
            gameSpeed -= 5; // Make it faster
            clearInterval(gameInterval);
            gameInterval = setInterval(update, gameSpeed);
        }
    } else {
        snake.pop();
    }

    draw();
}

function gameOver() {
    clearInterval(gameInterval);
    alert('Game Over! Your score: ' + score);
    startButton.textContent = 'Play Again';
    startButton.disabled = false;
}

document.addEventListener('keydown', e => {
    const keyPressed = e.key;
    const goingUp = direction === 'up';
    const goingDown = direction === 'down';
    const goingLeft = direction === 'left';
    const goingRight = direction === 'right';

    if (keyPressed === 'ArrowLeft' && !goingRight) {
        direction = 'left';
    } else if (keyPressed === 'ArrowUp' && !goingDown) {
        direction = 'up';
    } else if (keyPressed === 'ArrowRight' && !goingLeft) {
        direction = 'right';
    } else if (keyPressed === 'ArrowDown' && !goingUp) {
        direction = 'down';
    }
});

startButton.addEventListener('click', () => {
    startButton.textContent = 'Game Running...';
    startButton.disabled = true;
    initializeGame();
    gameInterval = setInterval(update, gameSpeed);
});

// Initial draw when page loads
initializeGame();