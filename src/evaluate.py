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
        "hit_cap": (not env.game_over) and steps >= max_steps,
    }


def set_seed(seed):
    """Cố định seed để các agent/cấu hình được đánh giá trên cùng chuỗi khối gạch."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def summarize(game_stats, max_steps):
    """Tính các metric theo Table 1 của report."""
    lines_arr = [s["lines"] for s in game_stats]
    scores_arr = [s["score"] for s in game_stats]
    pieces_arr = [s["pieces"] for s in game_stats]
    total_lines = int(np.sum(lines_arr))
    return {
        "games": len(game_stats),
        "max_steps": max_steps,
        "mean_lines": float(np.mean(lines_arr)),
        "std_lines": float(np.std(lines_arr)),
        "median_lines": float(np.median(lines_arr)),
        "max_lines": int(np.max(lines_arr)),
        "min_lines": int(np.min(lines_arr)),
        "mean_score": float(np.mean(scores_arr)),
        "std_score": float(np.std(scores_arr)),
        "max_score": int(np.max(scores_arr)),
        # Survival Placements = số khối đặt được trung bình mỗi ván
        "mean_placements": float(np.mean(pieces_arr)),
        "mean_steps": float(np.mean(pieces_arr)),  # giữ key cũ cho các tool khác
        # Points / Line = tổng điểm / tổng số hàng (cao = hay ăn combo 3-4 hàng)
        "points_per_line": float(np.sum(scores_arr) / total_lines) if total_lines > 0 else 0.0,
        # Số ván sống tới trần max_steps (không thua)
        "cap_hits": int(sum(s["hit_cap"] for s in game_stats)),
        "raw_lines": lines_arr,
        "raw_scores": scores_arr,
        "raw_placements": pieces_arr,
    }


def evaluate_agent(agent, is_dqn, games, max_steps, seed, verbose=False):
    """Chạy `games` ván với seed cố định; ván thứ g dùng seed + g."""
    env = TetrisEnv()
    game_stats = []
    t0 = time.time()
    for g in range(games):
        set_seed(seed + g)
        stats = run_single_game(env, agent, is_dqn=is_dqn, max_steps=max_steps)
        game_stats.append(stats)
        if verbose:
            print(
                f"  Game {g + 1:3d}/{games}: Lines={stats['lines']:4d} | Score={stats['score']:6d} | "
                f"Placements={stats['pieces']:4d}{' (cap)' if stats['hit_cap'] else ''}",
                flush=True,
            )
    result = summarize(game_stats, max_steps)
    result["time_elapsed"] = time.time() - t0
    return result


def print_table1(results):
    """In bảng theo đúng format Table 1 của report."""
    header = (
        f"{'Agent':<36} | {'Lines (Mean ± Std)':<18} | {'Median':>7} | {'Max':>5} | "
        f"{'Mean Score':>10} | {'Placements':>10} | {'Pts/Line':>8} | {'Cap':>7}"
    )
    print("\n" + "=" * len(header), flush=True)
    print("TABLE 1 – BENCHMARK", flush=True)
    print("=" * len(header), flush=True)
    print(header, flush=True)
    print("-" * len(header), flush=True)
    for name, r in results.items():
        ms = f"{r['mean_lines']:.1f} ± {r['std_lines']:.1f}"
        print(
            f"{name:<36} | {ms:<18} | {r['median_lines']:>7.1f} | {r['max_lines']:>5} | "
            f"{r['mean_score']:>10.1f} | {r['mean_placements']:>10.1f} | {r['points_per_line']:>8.1f} | "
            f"{r['cap_hits']:>3}/{r['games']:<3}",
            flush=True,
        )
    print("=" * len(header), flush=True)


def evaluate(args):
    os.makedirs(args.output_dir, exist_ok=True)

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
    print(
        f"STARTING BENCHMARK EVALUATION ({args.games} games/agent, max {args.max_steps} placements, seed {args.seed})",
        flush=True,
    )
    print("=" * 65, flush=True)

    for agent_name, (agent, is_dqn) in agents.items():
        print(f"\nEvaluating: {agent_name}...", flush=True)
        results[agent_name] = evaluate_agent(
            agent, is_dqn, args.games, args.max_steps, args.seed, verbose=not args.quiet
        )

    print_table1(results)

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
    # Mặc định khớp Table 1 của report: 100 games, trần 1000 bước
    parser.add_argument("--games", type=int, default=100, help="Number of games to evaluate per agent")
    parser.add_argument("--max-steps", type=int, default=1000, help="Max placements per game (step cap)")
    parser.add_argument("--seed", type=int, default=0, help="Base seed (game g uses seed+g)")
    parser.add_argument("--quiet", action="store_true", help="Không in kết quả từng ván")
    parser.add_argument("--model-path", type=str, default="checkpoints/best_model.pth", help="Trained model path")
    parser.add_argument("--output-dir", type=str, default="reports/figures", help="Directory for reports and plots")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or cuda)")
    parser.add_argument("--skip-random", action="store_true", help="Skip random agent")
    parser.add_argument("--skip-heuristic", action="store_true", help="Skip heuristic agent")

    args = parser.parse_args()
    evaluate(args)
