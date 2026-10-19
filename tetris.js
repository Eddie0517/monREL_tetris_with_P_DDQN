// CYBER TETRIS - Complete Game Logic
(function () {
  'use strict';

  // Constants & Dimensions
  const COLS = 10;
  const ROWS = 20;
  const BLOCK_SIZE = 30; // 300px width / 10 cols

  // Tetromino definitions (matrices and neon color themes)
  const SHAPES = {
    I: {
      matrix: [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
      ],
      color: '#00f0ff',
      glow: 'rgba(0, 240, 255, 0.7)',
      light: '#e0ffff'
    },
    J: {
      matrix: [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
      ],
      color: '#3b82f6',
      glow: 'rgba(59, 130, 246, 0.7)',
      light: '#93c5fd'
    },
    L: {
      matrix: [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]
      ],
      color: '#f97316',
      glow: 'rgba(249, 115, 22, 0.7)',
      light: '#fdba74'
    },
    O: {
      matrix: [
        [1, 1],
        [1, 1]
      ],
      color: '#eab308',
      glow: 'rgba(234, 179, 8, 0.7)',
      light: '#fef08a'
    },
    S: {
      matrix: [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
      ],
      color: '#22c55e',
      glow: 'rgba(34, 197, 94, 0.7)',
      light: '#86efac'
    },
    T: {
      matrix: [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
      ],
      color: '#a855f7',
      glow: 'rgba(168, 85, 247, 0.7)',
      light: '#d8b4fe'
    },
    Z: {
      matrix: [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
      ],
      color: '#ef4444',
      glow: 'rgba(239, 68, 68, 0.7)',
      light: '#fca5a5'
    }
  };

  const PIECE_TYPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z'];

  // DOM Elements
  const canvas = document.getElementById('tetris-canvas');
  const ctx = canvas.getContext('2d');
  const fxCanvas = document.getElementById('effects-canvas');
  const fxCtx = fxCanvas.getContext('2d');

  const holdCanvas = document.getElementById('hold-canvas');
  const holdCtx = holdCanvas.getContext('2d');
  const next1Canvas = document.getElementById('next-1-canvas');
  const next1Ctx = next1Canvas.getContext('2d');
  const next2Canvas = document.getElementById('next-2-canvas');
  const next2Ctx = next2Canvas.getContext('2d');
  const next3Canvas = document.getElementById('next-3-canvas');
  const next3Ctx = next3Canvas.getContext('2d');

  const scoreEl = document.getElementById('score-display');
  const linesEl = document.getElementById('lines-display');
  const levelEl = document.getElementById('level-display');
  const highscoreEl = document.getElementById('highscore-display');
  const statusTextEl = document.getElementById('game-status-text');

  // Overlay Elements
  const overlay = document.getElementById('game-overlay');
  const overlayTitle = document.getElementById('overlay-title');
  const overlayDesc = document.getElementById('overlay-desc');
  const overlayStats = document.getElementById('overlay-stats');
  const finalScoreEl = document.getElementById('final-score');
  const finalLinesEl = document.getElementById('final-lines');
  const finalLevelEl = document.getElementById('final-level');
  const btnOverlayAction = document.getElementById('btn-overlay-action');
  const btnOverlayRestart = document.getElementById('btn-overlay-restart');

  const btnPause = document.getElementById('btn-pause');
  const btnRestart = document.getElementById('btn-restart');
  const btnAiPlay = document.getElementById('btn-ai-play');
  const btnSound = document.getElementById('btn-sound');
  const iconSoundOn = document.getElementById('icon-sound-on');
  const iconSoundOff = document.getElementById('icon-sound-off');
  const btnMusic = document.getElementById('btn-music');
  const btnHelp = document.getElementById('btn-help');
  const helpModal = document.getElementById('help-modal');
  const btnCloseHelp = document.getElementById('btn-close-help');

  // Game State
  let board = createMatrix(ROWS, COLS);
  let score = 0;
  let lines = 0;
  let level = 1;
  let combo = -1;
  let highScore = parseInt(localStorage.getItem('cyber_tetris_highscore') || '0', 10);

  let currentPiece = null;
  let holdPiece = null;
  let canHold = true;
  let bag = [];
  let nextQueue = [];

  let dropCounter = 0;
  let dropInterval = 800; // ms
  let lastTime = 0;
  let isGameOver = false;
  let isPaused = false;
  let isStarted = false;
  let isAiMode = false;
  let aiActionTimer = null;

  // Particle System & Floating texts
  let particles = [];
  let floatingTexts = [];

  function createMatrix(rows, cols) {
    const matrix = [];
    for (let r = 0; r < rows; r++) {
      matrix.push(new Array(cols).fill(0));
    }
    return matrix;
  }

  // 7-Bag Randomizer
  function refillBag() {
    const pieces = [...PIECE_TYPES];
    // Fisher-Yates shuffle
    for (let i = pieces.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pieces[i], pieces[j]] = [pieces[j], pieces[i]];
    }
    bag.push(...pieces);
  }

  function getNextPieceType() {
    if (bag.length <= 4) {
      refillBag();
    }
    return bag.shift();
  }

  function createPiece(type) {
    const def = SHAPES[type];
    return {
      type: type,
      matrix: def.matrix.map(row => [...row]),
      color: def.color,
      glow: def.glow,
      light: def.light,
      x: Math.floor(COLS / 2) - Math.ceil(def.matrix[0].length / 2),
      y: 0
    };
  }

  // Collision detection
  function collide(board, piece, offsetX = 0, offsetY = 0) {
    const m = piece.matrix;
    for (let y = 0; y < m.length; y++) {
      for (let x = 0; x < m[y].length; x++) {
        if (m[y][x] !== 0) {
          const newX = piece.x + x + offsetX;
          const newY = piece.y + y + offsetY;
          if (newX < 0 || newX >= COLS || newY >= ROWS) {
            return true;
          }
          if (newY >= 0 && board[newY][newX] !== 0) {
            return true;
          }
        }
      }
    }
    return false;
  }

  // Merge piece into board
  function merge(board, piece) {
    piece.matrix.forEach((row, y) => {
      row.forEach((value, x) => {
        if (value !== 0) {
          const boardY = piece.y + y;
          const boardX = piece.x + x;
          if (boardY >= 0 && boardY < ROWS && boardX >= 0 && boardX < COLS) {
            board[boardY][boardX] = {
              color: piece.color,
              glow: piece.glow,
              light: piece.light
            };
          }
        }
      });
    });
  }

  // Rotate matrix
  function rotate(matrix, dir) {
    const result = [];
    const size = matrix.length;
    for (let i = 0; i < size; i++) {
      result.push(new Array(size).fill(0));
    }

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        if (dir > 0) {
          // Clockwise
          result[x][size - 1 - y] = matrix[y][x];
        } else {
          // Counter-Clockwise
          result[size - 1 - x][y] = matrix[y][x];
        }
      }
    }
    return result;
  }

  // Piece Rotation with Wall Kick offsets
  function playerRotate(dir) {
    if (!currentPiece || isPaused || isGameOver) return;
    const oldMatrix = currentPiece.matrix;
    currentPiece.matrix = rotate(currentPiece.matrix, dir);

    // Wall kick offsets to test: (0,0), (-1,0), (1,0), (0,-1), (-2,0), (2,0)
    const kicks = [0, -1, 1, -2, 2];
    let kicked = false;

    for (const offset of kicks) {
      if (!collide(board, currentPiece, offset, 0)) {
        currentPiece.x += offset;
        kicked = true;
        break;
      }
    }

    if (!kicked) {
      // Revert rotation if failed
      currentPiece.matrix = oldMatrix;
    } else {
      if (window.soundEngine) window.soundEngine.playRotate();
    }
  }

  // Player Movements
  function playerMove(dir) {
    if (!currentPiece || isPaused || isGameOver) return;
    if (!collide(board, currentPiece, dir, 0)) {
      currentPiece.x += dir;
      if (window.soundEngine) window.soundEngine.playMove();
    }
  }

  // Soft Drop
  function playerDrop() {
    if (!currentPiece || isPaused || isGameOver) return;
    if (!collide(board, currentPiece, 0, 1)) {
      currentPiece.y++;
      dropCounter = 0;
      score += 1;
      updateStats();
    } else {
      lockPiece();
    }
  }

  // Hard Drop
  function playerHardDrop() {
    if (!currentPiece || isPaused || isGameOver) return;
    let dropDistance = 0;
    while (!collide(board, currentPiece, 0, 1)) {
      currentPiece.y++;
      dropDistance++;
    }
    score += dropDistance * 2;
    updateStats();

    if (window.soundEngine) window.soundEngine.playHardDrop();
    triggerScreenShake();
    createDropParticles(currentPiece);
    lockPiece();
  }

  // Hold piece feature
  function playerHold() {
    if (!canHold || isPaused || isGameOver) return;

    if (window.soundEngine) window.soundEngine.playHold();

    if (!holdPiece) {
      holdPiece = currentPiece.type;
      spawnNewPiece();
    } else {
      const temp = holdPiece;
      holdPiece = currentPiece.type;
      currentPiece = createPiece(temp);
    }
    canHold = false;
    drawHoldPreview();
  }

  // Calculate Ghost Piece position (where it will land)
  function getGhostPosition() {
    if (!currentPiece) return null;
    let ghostY = currentPiece.y;
    while (!collide(board, currentPiece, 0, ghostY - currentPiece.y + 1)) {
      ghostY++;
    }
    return {
      x: currentPiece.x,
      y: ghostY,
      matrix: currentPiece.matrix,
      color: currentPiece.color
    };
  }

  // Lock piece down & process cleared lines
  function lockPiece() {
    merge(board, currentPiece);
    if (window.soundEngine) window.soundEngine.playDrop();

    clearLines();
    canHold = true;
    spawnNewPiece();
  }

  // Check & clear full rows
  function clearLines() {
    let linesCleared = 0;
    const clearedIndices = [];

    outer: for (let y = ROWS - 1; y >= 0; y--) {
      for (let x = 0; x < COLS; x++) {
        if (board[y][x] === 0) {
          continue outer;
        }
      }
      clearedIndices.push(y);
    }

    if (clearedIndices.length > 0) {
      linesCleared = clearedIndices.length;
      lines += linesCleared;
      combo++;

      // Remove lines from board
      clearedIndices.forEach(rowY => {
        // Create particle explosions across the row
        for (let col = 0; col < COLS; col++) {
          const cellColor = board[rowY][col] ? board[rowY][col].color : '#00f0ff';
          createLineParticles(col * BLOCK_SIZE + BLOCK_SIZE / 2, rowY * BLOCK_SIZE + BLOCK_SIZE / 2, cellColor);
        }
        board.splice(rowY, 1);
        board.unshift(new Array(COLS).fill(0));
      });

      // Score calculation
      const lineScores = [0, 100, 300, 500, 800];
      let gained = (lineScores[linesCleared] || 100) * level;
      if (combo > 0) {
        gained += combo * 50 * level;
      }
      score += gained;

      // Floating text
      const midY = clearedIndices[0] * BLOCK_SIZE;
      if (linesCleared === 4) {
        addFloatingText(`TETRIS! +${gained}`, 150, midY, '#00f0ff');
      } else if (combo > 1) {
        addFloatingText(`COMBO x${combo}! +${gained}`, 150, midY, '#ffb800');
      } else {
        addFloatingText(`+${gained}`, 150, midY, '#a855f7');
      }

      // Sound
      if (window.soundEngine) window.soundEngine.playLineClear(linesCleared);

      // Level Progression: Level up every 10 lines
      const newLevel = Math.floor(lines / 10) + 1;
      if (newLevel > level) {
        level = newLevel;
        dropInterval = Math.max(120, 800 - (level - 1) * 65);
        if (window.soundEngine) window.soundEngine.playLevelUp();
        addFloatingText(`LEVEL UP! CẤP ${level}`, 150, 300, '#00ff88');
      }

      updateStats();
    } else {
      combo = -1; // Reset combo if no line cleared
    }
  }

  // Spawn Next Piece
  function spawnNewPiece() {
    while (nextQueue.length < 3) {
      nextQueue.push(getNextPieceType());
    }
    const nextType = nextQueue.shift();
    nextQueue.push(getNextPieceType());

    currentPiece = createPiece(nextType);

    // Game Over check
    if (collide(board, currentPiece)) {
      handleGameOver();
    }

    drawNextPreviews();

    // Trigger AI move if autoplay is active
    if (isAiMode && !isGameOver && !isPaused) {
      if (aiActionTimer) clearTimeout(aiActionTimer);
      aiActionTimer = setTimeout(triggerAiStep, 90);
    }
  }

  // --- AI DECISION ENGINE (Pierre Dellacherie / RL Heuristic) ---
  function evaluateSimulatedBoard(simBoard) {
    const heights = new Array(COLS).fill(0);
    for (let c = 0; c < COLS; c++) {
      for (let r = 0; r < ROWS; r++) {
        if (simBoard[r][c] !== 0) {
          heights[c] = ROWS - r;
          break;
        }
      }
    }

    let aggHeight = 0;
    for (let c = 0; c < COLS; c++) aggHeight += heights[c];

    let holes = 0;
    for (let c = 0; c < COLS; c++) {
      const h = heights[c];
      if (h > 0) {
        for (let r = ROWS - h; r < ROWS; r++) {
          if (simBoard[r][c] === 0) holes++;
        }
      }
    }

    let bumpiness = 0;
    for (let c = 0; c < COLS - 1; c++) {
      bumpiness += Math.abs(heights[c] - heights[c + 1]);
    }

    return { aggHeight, holes, bumpiness };
  }

  function findBestAiMove() {
    if (!currentPiece) return null;
    let bestScore = -Infinity;
    let bestMove = null;

    let testMatrix = currentPiece.matrix;
    for (let rot = 0; rot < 4; rot++) {
      for (let testX = -3; testX < COLS + 3; testX++) {
        const dummyPiece = {
          x: testX,
          y: 0,
          matrix: testMatrix
        };

        if (collide(board, dummyPiece, 0, 0)) continue;

        let dropY = 0;
        while (!collide(board, dummyPiece, 0, dropY + 1)) {
          dropY++;
        }
        dummyPiece.y = dropY;

        // Build temporary board
        const simBoard = [];
        for (let r = 0; r < ROWS; r++) {
          simBoard.push(board[r].map(cell => (cell ? 1 : 0)));
        }

        for (let py = 0; py < testMatrix.length; py++) {
          for (let px = 0; px < testMatrix[py].length; px++) {
            if (testMatrix[py][px] !== 0) {
              const by = dummyPiece.y + py;
              const bx = dummyPiece.x + px;
              if (by >= 0 && by < ROWS && bx >= 0 && bx < COLS) {
                simBoard[by][bx] = 1;
              }
            }
          }
        }

        // Count cleared lines
        let linesCleared = 0;
        for (let r = ROWS - 1; r >= 0; r--) {
          if (simBoard[r].every(cell => cell !== 0)) {
            linesCleared++;
            simBoard.splice(r, 1);
            simBoard.unshift(new Array(COLS).fill(0));
            r++;
          }
        }

        const { aggHeight, holes, bumpiness } = evaluateSimulatedBoard(simBoard);

        // Pierre Dellacherie Heuristic:
        // Score = -0.51 * Height + 0.76 * Lines - 0.36 * Holes - 0.18 * Bumpiness
        const score = -0.51 * aggHeight + 0.76 * linesCleared - 0.36 * holes - 0.18 * bumpiness;

        if (score > bestScore) {
          bestScore = score;
          bestMove = { rot, x: testX, matrix: testMatrix };
        }
      }

      testMatrix = rotate(testMatrix, 1);
    }

    return bestMove;
  }

  function triggerAiStep() {
    if (!isAiMode || isPaused || isGameOver || !currentPiece) return;

    const move = findBestAiMove();
    if (move) {
      currentPiece.matrix = move.matrix;
      currentPiece.x = move.x;
      // Slight smooth delay so hard drop animation looks natural
      setTimeout(() => {
        if (isAiMode && !isPaused && !isGameOver && currentPiece) {
          playerHardDrop();
        }
      }, 70);
    }
  }

  function handleGameOver() {
    isGameOver = true;
    if (window.soundEngine) window.soundEngine.playGameOver();

    if (score > highScore) {
      highScore = score;
      localStorage.setItem('cyber_tetris_highscore', highScore.toString());
      highscoreEl.textContent = highScore.toLocaleString();
    }

    statusTextEl.textContent = 'KẾT THÚC';
    overlayTitle.textContent = 'GAME OVER';
    overlayDesc.textContent = 'Khối gạch đã chạm đỉnh!';
    finalScoreEl.textContent = score.toLocaleString();
    finalLinesEl.textContent = lines.toString();
    finalLevelEl.textContent = level.toString();
    overlayStats.classList.remove('hidden');
    btnOverlayAction.textContent = 'CHƠI LẠI';
    btnOverlayRestart.classList.add('hidden');
    overlay.classList.remove('hidden');
  }

  function triggerScreenShake() {
    const container = document.querySelector('.board-wrapper');
    container.classList.remove('screen-shake');
    void container.offsetWidth; // trigger reflow
    container.classList.add('screen-shake');
    setTimeout(() => {
      container.classList.remove('screen-shake');
    }, 250);
  }

  // Particle Effects
  function createLineParticles(x, y, color) {
    for (let i = 0; i < 14; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 5 + 2;
      particles.push({
        x: x,
        y: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: Math.random() * 4 + 2,
        color: color,
        life: 1.0,
        decay: Math.random() * 0.03 + 0.02
      });
    }
  }

  function createDropParticles(piece) {
    const m = piece.matrix;
    m.forEach((row, y) => {
      row.forEach((v, x) => {
        if (v !== 0) {
          const px = (piece.x + x) * BLOCK_SIZE + BLOCK_SIZE / 2;
          const py = (piece.y + y + 1) * BLOCK_SIZE;
          for (let i = 0; i < 5; i++) {
            particles.push({
              x: px,
              y: py,
              vx: (Math.random() - 0.5) * 4,
              vy: -(Math.random() * 3 + 1),
              size: Math.random() * 3 + 1,
              color: piece.color,
              life: 0.8,
              decay: 0.04
            });
          }
        }
      });
    });
  }

  function addFloatingText(text, x, y, color) {
    floatingTexts.push({
      text: text,
      x: x,
      y: y,
      color: color,
      alpha: 1.0,
      vy: -1.2
    });
  }

  function updateParticles() {
    fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);

    // Update & draw glowing particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;

      if (p.life <= 0) {
        particles.splice(i, 1);
        continue;
      }

      fxCtx.save();
      fxCtx.globalAlpha = p.life;
      fxCtx.shadowColor = p.color;
      fxCtx.shadowBlur = 10;
      fxCtx.fillStyle = p.color;
      fxCtx.beginPath();
      fxCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      fxCtx.fill();
      fxCtx.restore();
    }

    // Update & draw floating texts
    for (let i = floatingTexts.length - 1; i >= 0; i--) {
      const ft = floatingTexts[i];
      ft.y += ft.vy;
      ft.alpha -= 0.018;

      if (ft.alpha <= 0) {
        floatingTexts.splice(i, 1);
        continue;
      }

      fxCtx.save();
      fxCtx.font = "bold 16px 'Orbitron', sans-serif";
      fxCtx.textAlign = 'center';
      fxCtx.fillStyle = ft.color;
      fxCtx.shadowColor = ft.color;
      fxCtx.shadowBlur = 12;
      fxCtx.globalAlpha = Math.max(0, ft.alpha);
      fxCtx.fillText(ft.text, ft.x, ft.y);
      fxCtx.restore();
    }
  }

  // Block Rendering with 3D neon beveled arcade look
  function drawBlock(targetCtx, x, y, color, glow, light, size = BLOCK_SIZE, alpha = 1.0) {
    const px = x * size;
    const py = y * size;

    targetCtx.save();
    targetCtx.globalAlpha = alpha;

    // Outer glow
    targetCtx.shadowColor = glow || color;
    targetCtx.shadowBlur = 8;

    // Fill block
    targetCtx.fillStyle = color;
    targetCtx.fillRect(px + 1, py + 1, size - 2, size - 2);

    // Top & left bevel highlight
    targetCtx.shadowBlur = 0;
    targetCtx.fillStyle = light || '#ffffff';
    targetCtx.globalAlpha = alpha * 0.45;
    targetCtx.beginPath();
    targetCtx.moveTo(px + 1, py + 1);
    targetCtx.lineTo(px + size - 1, py + 1);
    targetCtx.lineTo(px + size - 4, py + 4);
    targetCtx.lineTo(px + 4, py + 4);
    targetCtx.lineTo(px + 4, py + size - 4);
    targetCtx.lineTo(px + 1, py + size - 1);
    targetCtx.closePath();
    targetCtx.fill();

    // Bottom & right bevel shadow
    targetCtx.fillStyle = '#000000';
    targetCtx.globalAlpha = alpha * 0.35;
    targetCtx.beginPath();
    targetCtx.moveTo(px + size - 1, py + 1);
    targetCtx.lineTo(px + size - 1, py + size - 1);
    targetCtx.lineTo(px + 1, py + size - 1);
    targetCtx.lineTo(px + 4, py + size - 4);
    targetCtx.lineTo(px + size - 4, py + size - 4);
    targetCtx.lineTo(px + size - 4, py + 4);
    targetCtx.closePath();
    targetCtx.fill();

    // Center subtle inner core
    targetCtx.fillStyle = '#ffffff';
    targetCtx.globalAlpha = alpha * 0.2;
    targetCtx.fillRect(px + 6, py + 6, size - 12, size - 12);

    targetCtx.restore();
  }

  // Draw Ghost Piece
  function drawGhostPiece(ghost) {
    if (!ghost) return;
    ghost.matrix.forEach((row, y) => {
      row.forEach((value, x) => {
        if (value !== 0) {
          const px = (ghost.x + x) * BLOCK_SIZE;
          const py = (ghost.y + y) * BLOCK_SIZE;

          ctx.save();
          ctx.strokeStyle = ghost.color;
          ctx.lineWidth = 1.5;
          ctx.shadowColor = ghost.color;
          ctx.shadowBlur = 6;
          ctx.strokeRect(px + 2, py + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4);

          ctx.fillStyle = ghost.color;
          ctx.globalAlpha = 0.12;
          ctx.fillRect(px + 3, py + 3, BLOCK_SIZE - 6, BLOCK_SIZE - 6);
          ctx.restore();
        }
      });
    });
  }

  // Draw subtle grid lines on the board
  function drawGrid() {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
    ctx.lineWidth = 1;

    for (let c = 0; c <= COLS; c++) {
      ctx.beginPath();
      ctx.moveTo(c * BLOCK_SIZE, 0);
      ctx.lineTo(c * BLOCK_SIZE, ROWS * BLOCK_SIZE);
      ctx.stroke();
    }

    for (let r = 0; r <= ROWS; r++) {
      ctx.beginPath();
      ctx.moveTo(0, r * BLOCK_SIZE);
      ctx.lineTo(COLS * BLOCK_SIZE, r * BLOCK_SIZE);
      ctx.stroke();
    }
  }

  // Main Render Loop
  function draw() {
    // Clear canvas with dark gradient
    ctx.fillStyle = '#0a0d18';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawGrid();

    // Draw fixed board blocks
    for (let y = 0; y < ROWS; y++) {
      for (let x = 0; x < COLS; x++) {
        const cell = board[y][x];
        if (cell !== 0) {
          drawBlock(ctx, x, y, cell.color, cell.glow, cell.light);
        }
      }
    }

    // Draw ghost piece preview
    if (currentPiece && !isPaused && !isGameOver) {
      const ghost = getGhostPosition();
      drawGhostPiece(ghost);
    }

    // Draw active falling piece
    if (currentPiece && !isPaused && !isGameOver) {
      currentPiece.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
          if (value !== 0) {
            drawBlock(
              ctx,
              currentPiece.x + x,
              currentPiece.y + y,
              currentPiece.color,
              currentPiece.glow,
              currentPiece.light
            );
          }
        });
      });
    }

    updateParticles();
  }

  // Preview Render Helper (Hold and Next)
  function renderMiniPiece(targetCtx, targetCanvas, type, cellSize = 20) {
    targetCtx.clearRect(0, 0, targetCanvas.width, targetCanvas.height);
    if (!type) return;

    const def = SHAPES[type];
    const matrix = def.matrix;
    const pieceWidth = matrix[0].length * cellSize;
    const pieceHeight = matrix.length * cellSize;

    const startX = (targetCanvas.width - pieceWidth) / 2 / cellSize;
    const startY = (targetCanvas.height - pieceHeight) / 2 / cellSize;

    matrix.forEach((row, y) => {
      row.forEach((value, x) => {
        if (value !== 0) {
          drawBlock(
            targetCtx,
            startX + x,
            startY + y,
            def.color,
            def.glow,
            def.light,
            cellSize
          );
        }
      });
    });
  }

  function drawHoldPreview() {
    renderMiniPiece(holdCtx, holdCanvas, holdPiece, 22);
  }

  function drawNextPreviews() {
    renderMiniPiece(next1Ctx, next1Canvas, nextQueue[0], 20);
    renderMiniPiece(next2Ctx, next2Canvas, nextQueue[1], 16);
    renderMiniPiece(next3Ctx, next3Canvas, nextQueue[2], 16);
  }

  function updateStats() {
    scoreEl.textContent = score.toLocaleString();
    linesEl.textContent = lines.toString();
    levelEl.textContent = level.toString();
    highscoreEl.textContent = Math.max(score, highScore).toLocaleString();
  }

  // Game Loop
  function update(time = 0) {
    const deltaTime = time - lastTime;
    lastTime = time;

    if (isStarted && !isPaused && !isGameOver) {
      dropCounter += deltaTime;
      if (dropCounter > dropInterval) {
        playerDrop();
      }
    }

    draw();
    requestAnimationFrame(update);
  }

  // Game Control Functions
  function startGame() {
    board = createMatrix(ROWS, COLS);
    score = 0;
    lines = 0;
    level = 1;
    combo = -1;
    dropInterval = 800;
    dropCounter = 0;
    isGameOver = false;
    isPaused = false;
    isStarted = true;
    holdPiece = null;
    canHold = true;
    bag = [];
    nextQueue = [];

    particles = [];
    floatingTexts = [];

    refillBag();
    refillBag();
    while (nextQueue.length < 3) {
      nextQueue.push(getNextPieceType());
    }

    statusTextEl.textContent = 'ĐANG CHƠI';
    btnPause.textContent = 'TẠM DỪNG (P)';
    overlay.classList.add('hidden');
    overlayStats.classList.add('hidden');

    spawnNewPiece();
    drawHoldPreview();
    updateStats();
  }

  function togglePause() {
    if (!isStarted || isGameOver) return;
    isPaused = !isPaused;

    if (isPaused) {
      statusTextEl.textContent = 'TẠM DỪNG';
      overlayTitle.textContent = 'TẠM DỪNG';
      overlayDesc.textContent = 'Trò chơi đang dừng lại.';
      overlayStats.classList.add('hidden');
      btnOverlayAction.textContent = 'TIẾP TỤC';
      btnOverlayRestart.classList.remove('hidden');
      overlay.classList.remove('hidden');
      btnPause.textContent = 'TIẾP TỤC (P)';
    } else {
      statusTextEl.textContent = 'ĐANG CHƠI';
      overlay.classList.add('hidden');
      btnPause.textContent = 'TẠM DỪNG (P)';
    }
  }

  // Event Listeners (Keyboard)
  window.addEventListener('keydown', e => {
    // Prevent default scrolling for arrows and space
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
      e.preventDefault();
    }

    if (!isStarted) {
      if (e.key === ' ' || e.key === 'Enter') {
        startGame();
      }
      return;
    }

    if (e.key === 'p' || e.key === 'P' || e.key === 'Escape') {
      togglePause();
      return;
    }

    if (e.key === 'r' || e.key === 'R') {
      startGame();
      return;
    }

    if (isPaused || isGameOver) return;

    switch (e.key) {
      case 'ArrowLeft':
      case 'a':
      case 'A':
        playerMove(-1);
        break;
      case 'ArrowRight':
      case 'd':
      case 'D':
        playerMove(1);
        break;
      case 'ArrowDown':
      case 's':
      case 'S':
        playerDrop();
        break;
      case 'ArrowUp':
      case 'w':
      case 'W':
      case 'x':
      case 'X':
        playerRotate(1); // Clockwise
        break;
      case 'z':
      case 'Z':
      case 'Control':
        playerRotate(-1); // Counter-Clockwise
        break;
      case ' ':
        playerHardDrop();
        break;
      case 'c':
      case 'C':
      case 'Shift':
        playerHold();
        break;
    }
  });

  // UI Button Bindings
  btnPause.addEventListener('click', togglePause);
  btnRestart.addEventListener('click', startGame);

  if (btnAiPlay) {
    btnAiPlay.addEventListener('click', () => {
      isAiMode = !isAiMode;
      btnAiPlay.classList.toggle('active', isAiMode);
      btnAiPlay.textContent = isAiMode ? '⚡ AI ĐANG CHƠI (TẮT)' : '🤖 BẬT AI AUTOPLAY';
      statusTextEl.textContent = isAiMode ? 'AI AUTOPLAY' : (isPaused ? 'TẠM DỪNG' : 'ĐANG CHƠI');
      if (isAiMode) {
        if (!isStarted || isGameOver) {
          startGame();
        }
        triggerAiStep();
      }
    });
  }

  btnOverlayAction.addEventListener('click', () => {
    if (!isStarted || isGameOver) {
      startGame();
    } else if (isPaused) {
      togglePause();
    }
  });

  btnOverlayRestart.addEventListener('click', startGame);

  // Audio Toggles
  btnSound.addEventListener('click', () => {
    if (window.soundEngine) {
      const active = window.soundEngine.toggleSound();
      iconSoundOn.classList.toggle('hidden', !active);
      iconSoundOff.classList.toggle('hidden', active);
    }
  });

  btnMusic.addEventListener('click', () => {
    if (window.soundEngine) {
      const musicActive = window.soundEngine.toggleMusic();
      btnMusic.style.borderColor = musicActive ? 'var(--neon-cyan)' : '';
      btnMusic.style.color = musicActive ? 'var(--neon-cyan)' : '';
    }
  });

  // Help Modal
  btnHelp.addEventListener('click', () => {
    helpModal.classList.remove('hidden');
  });

  btnCloseHelp.addEventListener('click', () => {
    helpModal.classList.add('hidden');
  });

  helpModal.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop')) {
      helpModal.classList.add('hidden');
    }
  });

  // Mobile Touch Controls
  const bindTouch = (id, action) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('touchstart', (e) => {
      e.preventDefault();
      if (!isStarted) startGame();
      action();
    });
    el.addEventListener('click', (e) => {
      e.preventDefault();
      if (!isStarted) startGame();
      action();
    });
  };

  bindTouch('ctrl-left', () => playerMove(-1));
  bindTouch('ctrl-right', () => playerMove(1));
  bindTouch('ctrl-down', () => playerDrop());
  bindTouch('ctrl-rotate-cw', () => playerRotate(1));
  bindTouch('ctrl-rotate-ccw', () => playerRotate(-1));
  bindTouch('ctrl-hard-drop', () => playerHardDrop());
  bindTouch('ctrl-hold', () => playerHold());

  // Initial State Setup
  highscoreEl.textContent = highScore.toLocaleString();
  overlayTitle.textContent = 'CYBER TETRIS';
  overlayDesc.textContent = 'Trải nghiệm xếp gạch phong cách arcade cyberpunk.';
  btnOverlayAction.textContent = 'BẮT ĐẦU CHƠI';
  btnOverlayRestart.classList.add('hidden');
  overlay.classList.remove('hidden');

  // Start animation loop
  requestAnimationFrame(update);
})();
