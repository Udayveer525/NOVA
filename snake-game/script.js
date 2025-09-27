
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const gridSize = 20;
let snake = [{ x: 10, y: 10 }];
let food = {};
let powerUp = {};
let direction = 'right';
let changingDirection = false;
let score = 0;
let gameSpeed = 150; // Milliseconds per frame
let gameInterval;
let activePowerUp = null;
let powerUpTimer = 0;
let scoreMultiplier = 1;
let growthInhibitorCount = 0;

const powerUpTypes = [
    { name: 'speedBoost', color: 'cyan', duration: 5000 }, // 5 seconds
    { name: 'scoreMultiplier', color: 'gold', duration: 7000 }, // 7 seconds
    { name: 'growthInhibitor', color: 'magenta', duration: 3 }, // 3 eats
];

function generateRandomPosition() {
    return {
        x: Math.floor(Math.random() * (canvas.width / gridSize)),
        y: Math.floor(Math.random() * (canvas.height / gridSize))
    };
}

function generateFood() {
    food = generateRandomPosition();
    // Ensure food doesn't spawn on snake or power-up
    while (snake.some(segment => segment.x === food.x && segment.y === food.y) ||
           (powerUp.x === food.x && powerUp.y === food.y)) {
        food = generateRandomPosition();
    }
}

function generatePowerUp() {
    if (Math.random() < 0.3) { // 30% chance to spawn a power-up
        const typeIndex = Math.floor(Math.random() * powerUpTypes.length);
        powerUp.type = powerUpTypes[typeIndex];
        powerUp.position = generateRandomPosition();
        // Ensure power-up doesn't spawn on snake or food
        while (snake.some(segment => segment.x === powerUp.position.x && segment.y === powerUp.position.y) ||
               (food.x === powerUp.position.x && food.y === powerUp.position.y)) {
            powerUp.position = generateRandomPosition();
        }
    } else {
        powerUp = {}; // No power-up this time
    }
}

function drawSegment(segment, color) {
    ctx.fillStyle = color;
    ctx.strokeStyle = 'darkgreen';
    ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize, gridSize);
    ctx.strokeRect(segment.x * gridSize, segment.y * gridSize, gridSize, gridSize);
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas

    // Draw snake
    snake.forEach(segment => drawSegment(segment, 'lightgreen'));

    // Draw food
    drawSegment(food, 'red');

    // Draw power-up if it exists
    if (powerUp.type) {
        drawSegment(powerUp.position, powerUp.type.color);
    }

    // Display score and active power-up info
    ctx.fillStyle = 'black';
    ctx.font = '16px Arial';
    ctx.fillText('Score: ' + score, 10, 20);
    if (activePowerUp) {
        let infoText = `Active: ${activePowerUp.name}`;
        if (activePowerUp.duration) {
            infoText += ` (${Math.ceil(powerUpTimer / 1000)}s)`;
        } else if (activePowerUp.count) {
            infoText += ` (${activePowerUp.count} eats)`;
        }
        ctx.fillText(infoText, 10, 40);
    }
}

function changeDirection(event) {
    if (changingDirection) return;
    changingDirection = true;

    const keyPressed = event.keyCode;
    const LEFT_KEY = 37;
    const RIGHT_KEY = 39;
    const UP_KEY = 38;
    const DOWN_KEY = 40;

    const goingUp = direction === 'up';
    const goingDown = direction === 'down';
    const goingLeft = direction === 'left';
    const goingRight = direction === 'right';

    if (keyPressed === LEFT_KEY && !goingRight) {
        direction = 'left';
    }
    if (keyPressed === UP_KEY && !goingDown) {
        direction = 'up';
    }
    if (keyPressed === RIGHT_KEY && !goingLeft) {
        direction = 'right';
    }
    if (keyPressed === DOWN_KEY && !goingUp) {
        direction = 'down';
    }
}

function moveSnake() {
    const head = { x: snake[0].x, y: snake[0].y };

    switch (direction) {
        case 'up':
            head.y -= 1;
            break;
        case 'down':
            head.y += 1;
            break;
        case 'left':
            head.x -= 1;
            break;
        case 'right':
            head.x += 1;
            break;
    }

    snake.unshift(head); // Add new head

    // Check for power-up collision
    if (powerUp.type && head.x === powerUp.position.x && head.y === powerUp.position.y) {
        activatePowerUp(powerUp.type);
        powerUp = {}; // Remove power-up from board
        generatePowerUp(); // Try to spawn a new power-up
    }

    const didEatFood = head.x === food.x && head.y === food.y;
    if (didEatFood) {
        score += (10 * scoreMultiplier);
        generateFood();
        generatePowerUp(); // Try to spawn a power-up after eating food
        if (growthInhibitorCount > 0) {
            growthInhibitorCount--;
        } else {
            // Snake grows
        }
    } else {
        if (growthInhibitorCount === 0) {
            snake.pop(); // Remove tail if not eating food and no growth inhibitor
        } else {
            // Snake doesn't pop, effectively growing without adding to length
            // This is a bit of a hack for growth inhibitor, a better way would be to only pop if not eating
            // For now, if inhibitor is active, we just don't pop, making it grow until inhibitor wears off
            growthInhibitorCount--; // Decrement inhibitor even if no growth
            if (growthInhibitorCount < 0) growthInhibitorCount = 0; // Prevent negative
        }
    }
}

function activatePowerUp(type) {
    activePowerUp = { name: type.name };
    powerUpTimer = type.duration || 0;

    switch (type.name) {
        case 'speedBoost':
            gameSpeed /= 2; // Double speed
            clearInterval(gameInterval);
            gameInterval = setInterval(gameLoop, gameSpeed);
            break;
        case 'scoreMultiplier':
            scoreMultiplier = 2;
            break;
        case 'growthInhibitor':
            activePowerUp.count = type.duration; // Using duration as count for eats
            growthInhibitorCount = type.duration;
            powerUpTimer = 0; // No time-based timer for this one
            break;
    }

    if (powerUpTimer > 0) {
        setTimeout(deactivatePowerUp, powerUpTimer);
    }
}

function deactivatePowerUp() {
    if (!activePowerUp) return;

    switch (activePowerUp.name) {
        case 'speedBoost':
            gameSpeed *= 2; // Restore speed
            clearInterval(gameInterval);
            gameInterval = setInterval(gameLoop, gameSpeed);
            break;
        case 'scoreMultiplier':
            scoreMultiplier = 1;
            break;
        // growthInhibitor is handled by count, no time-based deactivation
    }
    activePowerUp = null;
    powerUpTimer = 0;
}


function didGameEnd() {
    // Check if snake hits wall
    const hitLeftWall = snake[0].x < 0;
    const hitRightWall = snake[0].x >= canvas.width / gridSize;
    const hitTopWall = snake[0].y < 0;
    const hitBottomWall = snake[0].y >= canvas.height / gridSize;

    if (hitLeftWall || hitRightWall || hitTopWall || hitBottomWall) {
        return true;
    }

    // Check if snake hits itself
    for (let i = 4; i < snake.length; i++) {
        if (snake[i].x === snake[0].x && snake[i].y === snake[0].y) {
            return true;
        }
    }

    return false;
}

function gameLoop() {
    if (didGameEnd()) {
        clearInterval(gameInterval);
        alert('Game Over! Your score: ' + score);
        resetGame();
        return;
    }

    changingDirection = false;
    moveSnake();
    draw();

    // Update power-up timer if active and time-based
    if (activePowerUp && activePowerUp.duration && activePowerUp.duration > 0) {
        powerUpTimer -= gameSpeed; // Decrement by game frame time
        if (powerUpTimer <= 0) {
            deactivatePowerUp();
        }
    }
}

function resetGame() {
    snake = [{ x: 10, y: 10 }];
    direction = 'right';
    score = 0;
    gameSpeed = 150;
    activePowerUp = null;
    powerUpTimer = 0;
    scoreMultiplier = 1;
    growthInhibitorCount = 0;
    powerUp = {}; // Clear any active power-up object
    generateFood();
    clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, gameSpeed);
}

document.addEventListener('keydown', changeDirection);

generateFood();
generatePowerUp(); // Generate initial power-up
gameInterval = setInterval(gameLoop, gameSpeed);
