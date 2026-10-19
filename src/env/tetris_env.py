import random
import numpy as np

# 7 standard tetrominoes with unique rotations (all uint8 for fast bitwise ops)
PIECES = {
    'I': [
        np.array([[1, 1, 1, 1]], dtype=np.uint8),
        np.array([[1], [1], [1], [1]], dtype=np.uint8)
    ],
    'O': [
        np.array([[1, 1], [1, 1]], dtype=np.uint8)
    ],
    'T': [
        np.array([[1, 1, 1], [0, 1, 0]], dtype=np.uint8),
        np.array([[0, 1], [1, 1], [0, 1]], dtype=np.uint8),
        np.array([[0, 1, 0], [1, 1, 1]], dtype=np.uint8),
        np.array([[1, 0], [1, 1], [1, 0]], dtype=np.uint8)
    ],
    'S': [
        np.array([[0, 1, 1], [1, 1, 0]], dtype=np.uint8),
        np.array([[1, 0], [1, 1], [0, 1]], dtype=np.uint8)
    ],
    'Z': [
        np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8),
        np.array([[0, 1], [1, 1], [1, 0]], dtype=np.uint8)
    ],
    'J': [
        np.array([[1, 0, 0], [1, 1, 1]], dtype=np.uint8),
        np.array([[1, 1], [1, 0], [1, 0]], dtype=np.uint8),
        np.array([[1, 1, 1], [0, 0, 1]], dtype=np.uint8),
        np.array([[0, 1], [0, 1], [1, 1]], dtype=np.uint8)
    ],
    'L': [
        np.array([[0, 0, 1], [1, 1, 1]], dtype=np.uint8),
        np.array([[1, 0], [1, 0], [1, 1]], dtype=np.uint8),
        np.array([[1, 1, 1], [1, 0, 0]], dtype=np.uint8),
        np.array([[1, 1], [0, 1], [0, 1]], dtype=np.uint8)
    ]
}

PIECE_NAMES = list(PIECES.keys())


class TetrisEnv:
    """
    Fast Tetris environment optimized for Reinforcement Learning.
    Operates on a 20x10 binary grid using placement-based actions (rotation, column).
    """

    def __init__(self, rows=20, cols=10):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((self.rows, self.cols), dtype=np.uint8)
        self.bag = []
        self.current_piece = None
        self.next_piece = None

        # Game statistics
        self.score = 0
        self.cleared_lines = 0
        self.pieces_count = 0
        self.game_over = False

        # Previous state features for delta reward computation
        self.prev_agg_height = 0
        self.prev_holes = 0
        self.prev_bumpiness = 0

        self.reset()

    def _refill_bag(self):
        new_bag = PIECE_NAMES.copy()
        random.shuffle(new_bag)
        self.bag.extend(new_bag)

    def _get_next_piece_from_bag(self):
        if len(self.bag) <= 3:
            self._refill_bag()
        return self.bag.pop(0)

    def reset(self):
        """Resets the environment and returns the initial state."""
        self.board = np.zeros((self.rows, self.cols), dtype=np.uint8)
        self.bag = []
        self._refill_bag()
        self.current_piece = self._get_next_piece_from_bag()
        self.next_piece = self._get_next_piece_from_bag()

        self.score = 0
        self.cleared_lines = 0
        self.pieces_count = 0
        self.game_over = False

        self.prev_agg_height = 0
        self.prev_holes = 0
        self.prev_bumpiness = 0

        return self.get_board_features(self.board, 0)

    @staticmethod
    def get_board_features(board, lines_cleared=0):
        """
        Extracts 4 geometric features from board:
        [AggHeight, Holes, Bumpiness, Lines]
        """
        rows, cols = board.shape
        col_heights = np.zeros(cols, dtype=np.int32)

        for c in range(cols):
            col = board[:, c]
            filled = np.where(col > 0)[0]
            if len(filled) > 0:
                col_heights[c] = rows - filled[0]
            else:
                col_heights[c] = 0

        agg_height = int(np.sum(col_heights))

        # Holes: empty cells below highest filled block in each column
        holes = 0
        for c in range(cols):
            h = col_heights[c]
            if h > 0:
                holes += int(np.sum(board[rows - h :, c] == 0))

        # Bumpiness: sum of adjacent height differences
        bumpiness = int(np.sum(np.abs(np.diff(col_heights))))

        return np.array([agg_height, holes, bumpiness, lines_cleared], dtype=np.float32)

    def _drop_piece(self, board, piece, col):
        """
        Drops a piece shape into the board at column `col`.
        Returns (new_board, lines_cleared, is_overflow)
        """
        p_h, p_w = piece.shape
        if col < 0 or col + p_w > self.cols:
            return None, 0, True

        # Find maximum row r where piece fits without collision
        landing_r = -1
        for r in range(self.rows - p_h + 1):
            region = board[r : r + p_h, col : col + p_w]
            if np.any((region > 0) & (piece > 0)):
                break
            landing_r = r

        if landing_r == -1:
            return None, 0, True

        new_board = board.copy()
        new_board[landing_r : landing_r + p_h, col : col + p_w] |= piece

        # Check line clears
        full_rows = np.all(new_board > 0, axis=1)
        lines_cleared = int(np.sum(full_rows))

        if lines_cleared > 0:
            remaining_rows = new_board[~full_rows]
            empty_top = np.zeros((lines_cleared, self.cols), dtype=np.uint8)
            new_board = np.vstack([empty_top, remaining_rows])

        return new_board, lines_cleared, False

    def get_next_states(self, piece_name=None):
        """
        Returns a dictionary of all legal next states for the given piece:
        { (rotation_idx, col): (feature_vector, next_board) }
        """
        if piece_name is None:
            piece_name = self.current_piece

        rotations = PIECES[piece_name]
        next_states = {}

        for rot_idx, piece in enumerate(rotations):
            p_h, p_w = piece.shape
            for col in range(self.cols - p_w + 1):
                board_after, lines_cleared, overflow = self._drop_piece(self.board, piece, col)
                if not overflow and board_after is not None:
                    features = self.get_board_features(board_after, lines_cleared)
                    next_states[(rot_idx, col)] = (features, board_after)

        return next_states

    def step(self, action):
        """
        Executes action (rot_idx, col).
        Returns:
            features: 4-dim feature vector of the resulting board
            reward: scalar reward
            done: boolean flag
            info: dict with metadata
        """
        if self.game_over:
            raise RuntimeError("Game is over. Call reset() to play again.")

        rot_idx, col = action
        rotations = PIECES[self.current_piece]
        piece = rotations[rot_idx]

        new_board, lines_cleared, overflow = self._drop_piece(self.board, piece, col)

        if overflow or new_board is None:
            self.game_over = True
            reward = -10.0  # Terminal penalty
            features = self.get_board_features(self.board, 0)
            info = {
                "score": self.score,
                "cleared_lines": self.cleared_lines,
                "pieces_count": self.pieces_count,
            }
            return features, reward, True, info

        # Update board
        self.board = new_board
        self.pieces_count += 1
        self.cleared_lines += lines_cleared

        # Score matching standard rules
        line_scores = [0, 40, 100, 300, 1200]
        self.score += line_scores[min(lines_cleared, 4)]

        # Features of new board
        features = self.get_board_features(self.board, lines_cleared)
        agg_height, holes, bumpiness, _ = features

        # Reward according to PROPOSAL.md:
        # R = w1 * Lines^2 - w2 * delta(Holes) - w3 * delta(Bumpiness) - w4 * delta(AggHeight) + r_alive
        delta_holes = holes - self.prev_holes
        delta_bumpiness = bumpiness - self.prev_bumpiness
        delta_height = agg_height - self.prev_agg_height

        reward = 1.0 + (lines_cleared ** 2) * 10.0 - 1.5 * delta_holes - 0.5 * delta_bumpiness - 0.5 * delta_height

        # Update tracking
        self.prev_agg_height = agg_height
        self.prev_holes = holes
        self.prev_bumpiness = bumpiness

        # Advance pieces
        self.current_piece = self.next_piece
        self.next_piece = self._get_next_piece_from_bag()

        # Check if new piece can be placed at all
        next_legal_states = self.get_next_states()
        if len(next_legal_states) == 0:
            self.game_over = True
            reward -= 10.0

        info = {
            "score": self.score,
            "cleared_lines": self.cleared_lines,
            "pieces_count": self.pieces_count,
            "lines_cleared_this_step": lines_cleared,
        }

        return features, reward, self.game_over, info
