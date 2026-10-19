import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Reconfigure UTF-8 for Windows console
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import time
import pygame
import numpy as np

from src.env.tetris_env import TetrisEnv, PIECES
from src.agents.heuristic_agent import HeuristicAgent
from src.agents.dqn_agent import DQNAgent

# Cyberpunk Neon Color Palette
COLORS = {
    "background": (10, 14, 26),
    "grid_bg": (15, 23, 42),
    "grid_line": (30, 41, 59),
    "panel_bg": (19, 29, 54),
    "panel_border": (56, 189, 248),
    "text": (248, 250, 252),
    "text_muted": (148, 163, 184),
    "accent_cyan": (0, 240, 255),
    "accent_purple": (168, 85, 247),
    "accent_green": (34, 197, 94),
    "accent_orange": (249, 115, 22),
    "piece_colors": {
        "I": (0, 240, 255),
        "J": (59, 130, 246),
        "L": (249, 115, 22),
        "O": (234, 179, 8),
        "S": (34, 197, 94),
        "T": (168, 85, 247),
        "Z": (239, 68, 68),
        "filled": (120, 140, 180),
    },
}

BLOCK_SIZE = 30
BOARD_COLS = 10
BOARD_ROWS = 20
BOARD_WIDTH = BOARD_COLS * BLOCK_SIZE
BOARD_HEIGHT = BOARD_ROWS * BLOCK_SIZE
SIDE_PANEL_WIDTH = 260
WINDOW_WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH + 60
WINDOW_HEIGHT = BOARD_HEIGHT + 60


def draw_block(surface, x, y, color, size=BLOCK_SIZE, is_ghost=False):
    rect = pygame.Rect(x, y, size, size)
    if is_ghost:
        pygame.draw.rect(surface, color, rect, width=2, border_radius=4)
    else:
        # Main body
        pygame.draw.rect(surface, color, rect, border_radius=4)
        # Highlight top-left border for 3D bevel effect
        highlight_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
        pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + size - 2, y + 2), 2)
        pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + 2, y + size - 2), 2)
        # Dark bottom-right border
        shadow_color = (max(color[0] - 50, 0), max(color[1] - 50, 0), max(color[2] - 50, 0))
        pygame.draw.line(surface, shadow_color, (x + 2, y + size - 2), (x + size - 2, y + size - 2), 2)
        pygame.draw.line(surface, shadow_color, (x + size - 2, y + 2), (x + size - 2, y + size - 2), 2)


def main():
    parser = argparse.ArgumentParser(description="Cyber Tetris AI Real-Time Visualizer")
    parser.add_argument("--agent", type=str, default="heuristic", choices=["heuristic", "dqn", "random"], help="AI agent to run")
    parser.add_argument("--model-path", type=str, default="checkpoints/best_model.pth", help="Path to DQN checkpoint")
    parser.add_argument("--fps", type=int, default=15, help="Simulation speed / frames per second")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or cuda)")
    args = parser.parse_args()

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("CYBER TETRIS AI - Real-time Visualizer")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("Segoe UI, Arial", 22, bold=True)
    font_body = pygame.font.SysFont("Segoe UI, Arial", 16)
    font_small = pygame.font.SysFont("Segoe UI, Arial", 13)

    # Initialize environment
    env = TetrisEnv()
    heuristic_agent = HeuristicAgent()
    dqn_agent = None
    if os.path.exists(args.model_path):
        try:
            dqn_agent = DQNAgent(state_dim=4, device=args.device)
            dqn_agent.load(args.model_path)
        except Exception as e:
            print(f"Warning loading DQN: {e}")

    current_agent_type = args.agent
    paused = False
    fps = args.fps

    board_x = 30
    board_y = 30
    panel_x = board_x + BOARD_WIDTH + 20
    panel_y = board_y

    last_features = [0, 0, 0, 0]
    running = True

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    env.reset()
                elif event.key == pygame.K_UP:
                    fps = min(fps + 5, 120)
                elif event.key == pygame.K_DOWN:
                    fps = max(fps - 5, 1)
                elif event.key == pygame.K_h:
                    current_agent_type = "heuristic"
                elif event.key == pygame.K_d:
                    if dqn_agent is not None:
                        current_agent_type = "dqn"

        # Game Step if not paused and not game over
        if not paused and not env.game_over:
            next_states = env.get_next_states()
            if next_states:
                if current_agent_type == "heuristic":
                    action = heuristic_agent.act(next_states)
                    last_features, _ = next_states[action]
                elif current_agent_type == "dqn" and dqn_agent is not None:
                    action, last_features = dqn_agent.act(next_states, epsilon=0.0)
                else:
                    action = np.random.choice(list(next_states.keys()))
                    last_features, _ = next_states[action]

                if action:
                    env.step(action)
            else:
                env.game_over = True

        # Render Frame
        screen.fill(COLORS["background"])

        # Draw Board Grid Background
        grid_rect = pygame.Rect(board_x, board_y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(screen, COLORS["grid_bg"], grid_rect, border_radius=6)
        pygame.draw.rect(screen, COLORS["panel_border"], grid_rect, width=2, border_radius=6)

        # Draw Grid Lines
        for c in range(1, BOARD_COLS):
            x = board_x + c * BLOCK_SIZE
            pygame.draw.line(screen, COLORS["grid_line"], (x, board_y), (x, board_y + BOARD_HEIGHT), 1)
        for r in range(1, BOARD_ROWS):
            y = board_y + r * BLOCK_SIZE
            pygame.draw.line(screen, COLORS["grid_line"], (board_x, y), (board_x + BOARD_WIDTH, y), 1)

        # Draw Placed Blocks on Board
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if env.board[r, c] > 0:
                    bx = board_x + c * BLOCK_SIZE
                    by = board_y + r * BLOCK_SIZE
                    draw_block(screen, bx, by, COLORS["piece_colors"]["filled"])

        # Side Panel Background
        panel_rect = pygame.Rect(panel_x, panel_y, SIDE_PANEL_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(screen, COLORS["panel_bg"], panel_rect, border_radius=6)
        pygame.draw.rect(screen, (51, 65, 85), panel_rect, width=2, border_radius=6)

        # Render Stats in Side Panel
        py_offset = panel_y + 15

        def render_text(txt, color=COLORS["text"], font=font_body):
            nonlocal py_offset
            surf = font.render(txt, True, color)
            screen.blit(surf, (panel_x + 15, py_offset))
            py_offset += surf.get_height() + 8

        render_text("CYBER TETRIS AI", COLORS["accent_cyan"], font_title)
        render_text(f"Agent: {current_agent_type.upper()}", COLORS["accent_purple"])
        render_text(f"Speed: {fps} FPS [↑/↓]")
        py_offset += 10

        pygame.draw.line(screen, (51, 65, 85), (panel_x + 15, py_offset), (panel_x + SIDE_PANEL_WIDTH - 15, py_offset), 1)
        py_offset += 12

        render_text(f"Score: {env.score:,}", COLORS["accent_orange"], font_title)
        render_text(f"Cleared Lines: {env.cleared_lines:,}", COLORS["accent_green"], font_title)
        render_text(f"Pieces Dropped: {env.pieces_count:,}")
        py_offset += 10

        pygame.draw.line(screen, (51, 65, 85), (panel_x + 15, py_offset), (panel_x + SIDE_PANEL_WIDTH - 15, py_offset), 1)
        py_offset += 12

        render_text("Next Piece:", COLORS["text_muted"])
        if env.next_piece and env.next_piece in PIECES:
            next_shape = PIECES[env.next_piece][0]
            n_h, n_w = next_shape.shape
            p_color = COLORS["piece_colors"].get(env.next_piece, COLORS["accent_cyan"])
            start_nx = panel_x + 30
            start_ny = py_offset
            for nr in range(n_h):
                for nc in range(n_w):
                    if next_shape[nr, nc] > 0:
                        draw_block(screen, start_nx + nc * 22, start_ny + nr * 22, p_color, size=20)
            py_offset += n_h * 22 + 15

        pygame.draw.line(screen, (51, 65, 85), (panel_x + 15, py_offset), (panel_x + SIDE_PANEL_WIDTH - 15, py_offset), 1)
        py_offset += 12

        render_text("Evaluation Features:", COLORS["text_muted"])
        render_text(f"• Height: {int(last_features[0])}", font=font_small)
        render_text(f"• Holes: {int(last_features[1])}", font=font_small)
        render_text(f"• Bumpiness: {int(last_features[2])}", font=font_small)
        render_text(f"• Lines Cleared: {int(last_features[3])}", font=font_small)

        py_offset = panel_y + BOARD_HEIGHT - 65
        render_text("[Space] Pause | [R] Restart", COLORS["text_muted"], font_small)
        render_text("[H] Heuristic | [D] DQN", COLORS["text_muted"], font_small)

        # Game Over Banner
        if env.game_over:
            overlay = pygame.Surface((BOARD_WIDTH, 90), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (board_x, board_y + BOARD_HEIGHT // 2 - 45))
            go_text = font_title.render("GAME OVER", True, (239, 68, 68))
            sub_text = font_body.render("Press [R] to Restart", True, COLORS["text"])
            screen.blit(go_text, (board_x + (BOARD_WIDTH - go_text.get_width()) // 2, board_y + BOARD_HEIGHT // 2 - 35))
            screen.blit(sub_text, (board_x + (BOARD_WIDTH - sub_text.get_width()) // 2, board_y + BOARD_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
