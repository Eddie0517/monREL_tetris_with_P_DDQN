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
import json
import random
import time
import numpy as np
import matplotlib.pyplot as plt

from src.env.tetris_env import TetrisEnv
from src.agents.heuristic_agent import HeuristicAgent, NaiveGreedyAgent
from src.agents.dqn_agent import DQNAgent


class RandomAgent:
    """Agent that selects random valid placements."""
    def act(self, next_states):
        if not next_states:
            return None
        return random.choice(list(next_states.keys()))


def run_single_game(env, agent, is_dqn=False, max_steps=10000):
    env.reset()
    steps = 0
    while not env.game_over and steps < max_steps:
        next_states = env.get_next_states()
        if not next_states:
            break

        if is_dqn:
            action, _ = agent.act(next_states, epsilon=0.0)
        else:
            action = agent.act(next_states)

        if action is None:
            break

        env.step(action)
        steps += 1

    return {
        "lines": env.cleared_lines,
        "score": env.score,
        "steps": steps,
        "pieces": env.pieces_count,
    }


def evaluate(args):
    os.makedirs(args.output_dir, exist_ok=True)
    env = TetrisEnv()

    agents = {}
    if not args.skip_random:
        agents["Random Baseline (Demaine 2002)"] = (RandomAgent(), False)

    agents["Naive Greedy (Fahey 2003)"] = (NaiveGreedyAgent(), False)

    if os.path.exists(args.model_path):
        dqn_agent = DQNAgent(state_dim=4, device=args.device)
        dqn_agent.load(args.model_path)
        agents["Proposed DDQN Agent"] = (dqn_agent, True)
    else:
        print(f"Warning: Model file '{args.model_path}' not found. Skipping DDQN Agent evaluation.")

    if not args.skip_heuristic:
        agents["Expert Heuristic (Dellacherie 2003)"] = (HeuristicAgent(), False)

    results = {}

    print("=" * 65, flush=True)
    print(f"STARTING BENCHMARK EVALUATION ({args.games} games per agent)", flush=True)
    print("=" * 65, flush=True)

    for agent_name, (agent, is_dqn) in agents.items():
        print(f"\nEvaluating: {agent_name}...", flush=True)
        game_stats = []
        t0 = time.time()

        for g in range(1, args.games + 1):
            stats = run_single_game(env, agent, is_dqn=is_dqn, max_steps=args.max_steps)
            game_stats.append(stats)
            print(
                f"  Game {g:2d}/{args.games}: Lines={stats['lines']:4d} | Score={stats['score']:6d} | Steps={stats['steps']:4d}",
                flush=True,
            )

        elapsed = time.time() - t0
        lines_arr = [s["lines"] for s in game_stats]
        scores_arr = [s["score"] for s in game_stats]
        steps_arr = [s["steps"] for s in game_stats]

        results[agent_name] = {
            "games": args.games,
            "mean_lines": float(np.mean(lines_arr)),
            "std_lines": float(np.std(lines_arr)),
            "max_lines": int(np.max(lines_arr)),
            "min_lines": int(np.min(lines_arr)),
            "median_lines": float(np.median(lines_arr)),
            "mean_score": float(np.mean(scores_arr)),
            "std_score": float(np.std(scores_arr)),
            "max_score": int(np.max(scores_arr)),
            "mean_steps": float(np.mean(steps_arr)),
            "raw_lines": lines_arr,
            "raw_scores": scores_arr,
            "time_elapsed": elapsed,
        }

    # Print Summary Table
    print("\n" + "=" * 70, flush=True)
    print("FINAL BENCHMARK COMPARISON TABLE", flush=True)
    print("=" * 70, flush=True)
    print(f"{'Agent':<25} | {'Mean Lines (±Std)':<18} | {'Max Lines':<10} | {'Mean Score':<12}", flush=True)
    print("-" * 70, flush=True)
    for name, r in results.items():
        mean_std_str = f"{r['mean_lines']:.1f} ± {r['std_lines']:.1f}"
        print(f"{name:<25} | {mean_std_str:<18} | {r['max_lines']:<10} | {r['mean_score']:<12.1f}", flush=True)
    print("=" * 70, flush=True)

    # Save JSON results
    json_path = os.path.join(args.output_dir, "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        # Don't serialize non-json types
        json.dump(results, f, indent=2)
    print(f"\nResults successfully saved to: {json_path}", flush=True)

    # Generate Graphs
    plot_path = os.path.join(args.output_dir, "benchmark_comparison.png")
    generate_charts(results, plot_path)
    print(f"Comparison chart saved to: {plot_path}", flush=True)


def generate_charts(results, output_file):
    names = list(results.keys())
    if not names:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = ["#94a3b8", "#f59e0b", "#38bdf8", "#a855f7"]

    # 1. Bar Chart: Mean Cleared Lines
    mean_lines = [results[n]["mean_lines"] for n in names]
    std_lines = [results[n]["std_lines"] for n in names]

    axes[0].bar(names, mean_lines, yerr=std_lines, capsize=5, color=colors[: len(names)], alpha=0.85)
    axes[0].set_title("Average Cleared Lines per Game (Higher is better)", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Cleared Lines")
    axes[0].tick_params(axis='x', labelrotation=15)
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)

    for i, v in enumerate(mean_lines):
        axes[0].text(i, v + (std_lines[i] if std_lines[i] > 0 else 1) * 0.1, f"{v:.1f}", ha="center", fontweight="bold")

    # 2. Boxplot: Distribution of Cleared Lines
    data_to_plot = [results[n]["raw_lines"] for n in names]
    axes[1].boxplot(data_to_plot, tick_labels=names, patch_artist=True)
    axes[1].set_title("Cleared Lines Distribution (Boxplot)", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Cleared Lines")
    axes[1].tick_params(axis='x', labelrotation=15)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=200)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate and Benchmark Tetris Agents")
    parser.add_argument("--games", type=int, default=5, help="Number of games to evaluate per agent")
    parser.add_argument("--max-steps", type=int, default=500, help="Max steps per game to avoid infinite loops")
    parser.add_argument("--model-path", type=str, default="checkpoints/best_model.pth", help="Trained model path")
    parser.add_argument("--output-dir", type=str, default="reports/figures", help="Directory for reports and plots")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or cuda)")
    parser.add_argument("--skip-random", action="store_true", help="Skip random agent")
    parser.add_argument("--skip-heuristic", action="store_true", help="Skip heuristic agent")

    args = parser.parse_args()
    evaluate(args)
