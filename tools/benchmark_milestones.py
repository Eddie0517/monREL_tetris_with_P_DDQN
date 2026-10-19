import os
import sys

# Ensure project root in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import time
import numpy as np
import torch

from src.env.tetris_env import TetrisEnv
from src.agents.dqn_agent import DQNAgent

def test_checkpoint(model_path, games=5, max_steps=1000):
    if not os.path.exists(model_path):
        return None
    
    env = TetrisEnv()
    agent = DQNAgent(state_dim=4, device="cpu")
    agent.load(model_path)
    
    lines_list = []
    scores_list = []
    steps_list = []
    
    for g in range(games):
        env.reset()
        step_count = 0
        while not env.game_over and step_count < max_steps:
            next_states = env.get_next_states()
            if not next_states:
                break
            action, _ = agent.act(next_states, epsilon=0.0)
            if action is None:
                break
            env.step(action)
            step_count += 1
            
        lines_list.append(env.cleared_lines)
        scores_list.append(env.score)
        steps_list.append(step_count)
        
    return {
        "mean_lines": float(np.mean(lines_list)),
        "std_lines": float(np.std(lines_list)),
        "max_lines": int(np.max(lines_list)),
        "mean_score": float(np.mean(scores_list)),
        "mean_steps": float(np.mean(steps_list)),
    }

def main():
    parser = argparse.ArgumentParser(description="Benchmark Checkpoint Milestones")
    parser.add_argument("--games", type=int, default=5, help="Number of games per checkpoint")
    parser.add_argument("--max-steps", type=int, default=1000, help="Step cap per game")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints", help="Path to checkpoints folder")
    args = parser.parse_args()

    milestones = [
        ("Ep 100", os.path.join(args.checkpoint_dir, "dqn_ep100.pth")),
        ("Ep 200", os.path.join(args.checkpoint_dir, "dqn_ep200.pth")),
        ("Ep 300", os.path.join(args.checkpoint_dir, "dqn_ep300.pth")),
        ("Ep 400", os.path.join(args.checkpoint_dir, "dqn_ep400.pth")),
        ("Ep 500", os.path.join(args.checkpoint_dir, "dqn_ep500.pth")),
        ("Ep 600", os.path.join(args.checkpoint_dir, "dqn_ep600.pth")),
        ("Ep 700", os.path.join(args.checkpoint_dir, "dqn_ep700.pth")),
        ("Ep 800", os.path.join(args.checkpoint_dir, "dqn_ep800.pth")),
        ("Ep 900", os.path.join(args.checkpoint_dir, "dqn_ep900.pth")),
        ("Ep 1000", os.path.join(args.checkpoint_dir, "dqn_ep1000.pth")),
        ("Best Model", os.path.join(args.checkpoint_dir, "best_model.pth")),
        ("Latest (Ep 1066)", os.path.join(args.checkpoint_dir, "latest_model.pth")),
    ]

    print("=" * 75)
    print(f"BENCHMARK TIẾN HÓA CÁC MỐC CHECKPOINTS ({args.games} ván / mốc, trần {args.max_steps} bước)")
    print("=" * 75)
    print(f"{'Mốc Checkpoint':<18} | {'Hàng TB (±Std)':<18} | {'Kỷ lục Hàng':<14} | {'Điểm TB':<12}")
    print("-" * 75)

    for label, path in milestones:
        if not os.path.exists(path):
            continue
        res = test_checkpoint(path, games=args.games, max_steps=args.max_steps)
        if res:
            mean_std = f"{res['mean_lines']:.1f} ± {res['std_lines']:.1f}"
            print(f"{label:<18} | {mean_std:<18} | {res['max_lines']:<14} | {res['mean_score']:<12.1f}", flush=True)

    print("=" * 75)

if __name__ == "__main__":
    main()
