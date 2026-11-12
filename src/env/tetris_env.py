import random
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

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


def _piece_geometry(piece):
    """Thông tin hình học dùng cho tính điểm rơi nhanh (mọi tetromino có ô liên tục theo cột)."""
    rows_idx, cols_idx = np.nonzero(piece)
    p_w = piece.shape[1]
    top = np.array([rows_idx[cols_idx == j].min() for j in range(p_w)])
    bottom = np.array([rows_idx[cols_idx == j].max() for j in range(p_w)])
    return {"cells_r": rows_idx, "cells_c": cols_idx, "top": top, "bottom": bottom}


PIECE_GEOMETRY = {name: [_piece_geometry(p) for p in rots] for name, rots in PIECES.items()}


# Default reward weights (giá trị gốc của dự án).
# R = alive + lines * L^2 - holes * dHoles - bumpiness * dBumpiness - height * dAggHeight
# Khi thua: game_over_penalty được trừ vào reward.
DEFAULT_REWARD_WEIGHTS = {
    "alive": 1.0,
    "lines": 10.0,
    "holes": 1.5,
    "bumpiness": 0.5,
    "height": 0.5,
    "game_over_penalty": 10.0,
}


class TetrisEnv:
    """
    Fast Tetris environment optimized for Reinforcement Learning.
    Operates on a 20x10 binary grid using placement-based actions (rotation, column).

    reward_weights: dict ghi đè một phần hoặc toàn bộ DEFAULT_REWARD_WEIGHTS.
    """

    def __init__(self, rows=20, cols=10, reward_weights=None):
        unknown = set(reward_weights or {}) - set(DEFAULT_REWARD_WEIGHTS)
        if unknown:
            raise ValueError(f"Unknown reward weight keys: {sorted(unknown)}")
        self.reward_weights = {**DEFAULT_REWARD_WEIGHTS, **(reward_weights or {})}

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
        self._next_states_cache = None

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
        self._next_states_cache = None

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
        rows = board.shape[0]
        filled = board > 0
        # Chiều cao cột = rows - chỉ số hàng có ô đầy đầu tiên tính từ trên (0 nếu cột trống)
        col_heights = np.where(filled.any(axis=0), rows - filled.argmax(axis=0), 0)

        agg_height = int(col_heights.sum())

        # Holes: ô trống nằm dưới ô đầy cao nhất của mỗi cột.
        # Mọi ô đầy đều nằm trong vùng chiều cao cột => holes = tổng chiều cao - tổng số ô đầy.
        holes = agg_height - int(filled.sum())

        # Bumpiness: sum of adjacent height differences
        bumpiness = int(np.abs(np.diff(col_heights)).sum())

        return np.array([agg_height, holes, bumpiness, lines_cleared], dtype=np.float32)

    def _drop_piece(self, board, piece, col):
        """
        Drops a piece shape into the board at column `col`.
        Returns (new_board, lines_cleared, is_overflow)
        """
        p_h, p_w = piece.shape
        if col < 0 or col + p_w > self.cols:
            return None, 0, True

        # Find maximum row r where piece fits without collision.
        # Kiểm tra va chạm ở mọi vị trí r cùng lúc (sliding window) thay vì lặp từng hàng;
        # landing_r = vị trí ngay trước va chạm đầu tiên (giống hệt vòng lặp cũ).
        windows = sliding_window_view(board[:, col : col + p_w], (p_h, p_w))[:, 0]
        collide = (windows & piece).any(axis=(1, 2))
        if collide.any():
            landing_r = int(collide.argmax()) - 1
        else:
            landing_r = self.rows - p_h

        if landing_r < 0:
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

        Kết quả cho khối hiện tại được cache cho tới khi bàn cờ đổi (step/reset),
        vì step() đã phải tính nó để kiểm tra thua -> vòng train không phải tính lại.
        Không được sửa tại chỗ dict/mảng trả về.
        """
        if piece_name is None:
            piece_name = self.current_piece
        cache = self._next_states_cache
        if cache is not None and cache[0] == piece_name:
            return cache[1]
        next_states = self._compute_next_states(piece_name)
        self._next_states_cache = (piece_name, next_states)
        return next_states

    def _compute_next_states(self, piece_name):
        """
        Tính mọi điểm đặt cùng lúc (vector hóa). Kết quả giống hệt việc gọi
        _drop_piece + get_board_features cho từng (rot, col) theo thứ tự cũ.
        """
        board = self.board
        rows, cols = self.rows, self.cols
        filled = board > 0
        col_has = filled.any(axis=0)
        col_top = np.where(col_has, filled.argmax(axis=0), rows)  # hàng ô đầy cao nhất (rows nếu trống)

        keys, landings, cell_r, cell_c = [], [], [], []
        fallback = {}
        for rot_idx, (piece, geo) in enumerate(zip(PIECES[piece_name], PIECE_GEOMETRY[piece_name])):
            p_h, p_w = piece.shape
            for col in range(cols - p_w + 1):
                tops = col_top[col : col + p_w]
                if (tops < geo["top"]).any():
                    # Chồng gạch chạm sát đỉnh: dùng cách tính gốc cho chắc chắn đúng
                    board_after, lines_cleared, overflow = self._drop_piece(board, piece, col)
                    keys.append((rot_idx, col))
                    landings.append(-1)
                    cell_r.append(geo["cells_r"])
                    cell_c.append(geo["cells_c"] + col)
                    if not overflow and board_after is not None:
                        fallback[len(keys) - 1] = (board_after, lines_cleared)
                    continue
                # Va chạm đầu tiên khi rơi từ trên xuống: ô thấp nhất của khối chạm ô đầy cao nhất của cột
                hit = np.where(col_has[col : col + p_w], np.maximum(tops - geo["bottom"], 0), rows + 1)
                first_hit = int(hit.min())
                landing = rows - p_h if first_hit > rows else min(first_hit - 1, rows - p_h)
                keys.append((rot_idx, col))
                landings.append(landing)
                cell_r.append(geo["cells_r"] + landing)
                cell_c.append(geo["cells_c"] + col)

        landings = np.array(landings)
        ok = (landings >= 0)
        for i in fallback:
            ok[i] = True
        idx = np.nonzero(ok)[0]
        if len(idx) == 0:
            return {}

        n = len(idx)
        boards = np.repeat(board[None], n, axis=0)
        fast = np.array([i not in fallback for i in idx])
        fast_rows = np.nonzero(fast)[0]
        if len(fast_rows):
            rr = np.stack([cell_r[idx[k]] for k in fast_rows])
            cc = np.stack([cell_c[idx[k]] for k in fast_rows])
            boards[fast_rows[:, None], rr, cc] = 1

        full = (boards > 0).all(axis=2)
        lines = full.sum(axis=1)
        board_list = list(boards)
        for k in range(n):
            if not fast[k]:
                board_list[k], lines[k] = fallback[idx[k]]
                boards[k] = board_list[k]
            elif lines[k] > 0:
                remaining = boards[k][~full[k]]
                cleared = np.vstack([np.zeros((lines[k], cols), dtype=np.uint8), remaining])
                boards[k] = cleared
                board_list[k] = cleared

        f = boards > 0
        heights = np.where(f.any(axis=1), rows - f.argmax(axis=1), 0)
        agg = heights.sum(axis=1)
        holes = agg - f.sum(axis=(1, 2))
        bump = np.abs(np.diff(heights, axis=1)).sum(axis=1)
        feats = np.stack([agg, holes, bump, lines], axis=1).astype(np.float32)

        return {keys[idx[k]]: (feats[k], board_list[k]) for k in range(n)}

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

        # Dùng lại kết quả đã tính trong get_next_states() nếu có (giống hệt _drop_piece)
        cache = self._next_states_cache
        if cache is not None and cache[0] == self.current_piece and action in cache[1]:
            cached_features, new_board = cache[1][action]
            lines_cleared, overflow = int(cached_features[3]), False
        else:
            new_board, lines_cleared, overflow = self._drop_piece(self.board, piece, col)

        if overflow or new_board is None:
            self.game_over = True
            reward = -self.reward_weights["game_over_penalty"]  # Terminal penalty
            features = self.get_board_features(self.board, 0)
            info = {
                "score": self.score,
                "cleared_lines": self.cleared_lines,
                "pieces_count": self.pieces_count,
            }
            return features, reward, True, info

        # Update board
        self.board = new_board
        self._next_states_cache = None
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

        w = self.reward_weights
        reward = (
            w["alive"]
            + w["lines"] * (lines_cleared ** 2)
            - w["holes"] * delta_holes
            - w["bumpiness"] * delta_bumpiness
            - w["height"] * delta_height
        )
        reward = float(reward)

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
            reward -= self.reward_weights["game_over_penalty"]

        info = {
            "score": self.score,
            "cleared_lines": self.cleared_lines,
            "pieces_count": self.pieces_count,
            "lines_cleared_this_step": lines_cleared,
        }

        return features, reward, self.game_over, info
