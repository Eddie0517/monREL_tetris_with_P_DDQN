import os
import sys
import glob
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from tensorboard.backend.event_processing import event_accumulator

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Load TensorBoard data
log_files = glob.glob(os.path.join(PROJECT_ROOT, "logs", "events.out.tfevents.*"))
if not log_files:
    print("No TensorBoard log files found!")
    sys.exit(1)

ea = event_accumulator.EventAccumulator(log_files[0])
ea.Reload()

lines_ev = ea.Scalars("Train/Cleared_Lines")
score_ev = ea.Scalars("Train/Score")
steps_ev = ea.Scalars("Train/Steps")
loss_ev = ea.Scalars("Train/Loss")
eps_ev = ea.Scalars("Train/Epsilon")
avg50_ev = ea.Scalars("Stats/Avg50_Lines")

t_start = lines_ev[0].wall_time
episodes = [e.step for e in lines_ev]
cleared_lines = [e.value for e in lines_ev]
scores = [e.value for e in score_ev]
steps = [e.value for e in steps_ev]
losses = [e.value for e in loss_ev]
epsilons = [e.value for e in eps_ev]
avg50_lines = [e.value for e in avg50_ev]
cum_times_min = [(e.wall_time - t_start) / 60.0 for e in lines_ev]

print(f"Loaded {len(episodes)} episodes. Total time: {cum_times_min[-1]:.2f} min.")

# Set clean academic styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "Arial, DejaVu Sans, Helvetica"
plt.rcParams["axes.edgecolor"] = "#cbd5e1"
plt.rcParams["axes.linewidth"] = 0.8

# ==============================================================================
# FIGURE 1: 4-PANEL TRAINING PROGRESSION CURVE
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)

# (a) Cleared Lines & 50-ep Moving Average
axes[0, 0].plot(episodes, cleared_lines, color="#94a3b8", alpha=0.35, label="Raw Lines per Episode", linewidth=0.8)
axes[0, 0].plot(episodes, avg50_lines, color="#0284c7", linewidth=2.2, label="50-Episode Moving Average")
axes[0, 0].axvline(x=1000, color="#ef4444", linestyle="--", linewidth=1.2, label="Epsilon Decay Complete (Ep 1000)")
axes[0, 0].set_title("(a) Cleared Lines Evolution & Moving Average", fontsize=12, fontweight="bold", pad=8)
axes[0, 0].set_xlabel("Training Episodes", fontsize=10)
axes[0, 0].set_ylabel("Cleared Lines", fontsize=10)
axes[0, 0].legend(loc="upper left", frameon=True, fontsize=9)
axes[0, 0].grid(True, linestyle="--", alpha=0.5)

# (b) Cumulative Training Time
axes[0, 1].plot(episodes, cum_times_min, color="#10b981", linewidth=2.2, label="Cumulative Wall-Clock Time (Min)")
axes[0, 1].axvline(x=1000, color="#ef4444", linestyle="--", linewidth=1.2, label="Ep 1000 (8.9 min)")
axes[0, 1].scatter([1000, episodes[-1]], [cum_times_min[999], cum_times_min[-1]], color="#ef4444", zorder=5)
axes[0, 1].annotate("Ep 1000: 8.9 min", xy=(1000, cum_times_min[999]), xytext=(720, 12),
                    arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.2), fontsize=9, fontweight="bold")
axes[0, 1].annotate(f"Final Ep {episodes[-1]}: {cum_times_min[-1]:.1f} min", xy=(episodes[-1], cum_times_min[-1]), xytext=(650, 17),
                    arrowprops=dict(arrowstyle="->", color="#10b981", lw=1.2), fontsize=9, fontweight="bold")
axes[0, 1].set_title("(b) Training Duration Across Episodes", fontsize=12, fontweight="bold", pad=8)
axes[0, 1].set_xlabel("Training Episodes", fontsize=10)
axes[0, 1].set_ylabel("Cumulative Time (Minutes)", fontsize=10)
axes[0, 1].legend(loc="upper left", frameon=True, fontsize=9)
axes[0, 1].grid(True, linestyle="--", alpha=0.5)

# (c) Score Progression & Epsilon Decay
ax_c = axes[1, 0]
ax_c2 = ax_c.twinx()
ax_c.plot(episodes, scores, color="#8b5cf6", alpha=0.5, linewidth=0.8, label="Episode Score")
ax_c2.plot(episodes, epsilons, color="#f59e0b", linestyle="-.", linewidth=1.8, label="Epsilon (Exploration Rate)")
ax_c.set_title("(c) Score Growth & Epsilon Exploration Decay", fontsize=12, fontweight="bold", pad=8)
ax_c.set_xlabel("Training Episodes", fontsize=10)
ax_c.set_ylabel("Game Score", color="#6d28d9", fontsize=10)
ax_c2.set_ylabel("Epsilon Rate", color="#d97706", fontsize=10)
ax_c.grid(True, linestyle="--", alpha=0.5)

lines_c1, labels_c1 = ax_c.get_legend_handles_labels()
lines_c2, labels_c2 = ax_c2.get_legend_handles_labels()
ax_c.legend(lines_c1 + lines_c2, labels_c1 + labels_c2, loc="upper left", frameon=True, fontsize=9)

# (d) TD Loss Convergence
axes[1, 1].plot(episodes, losses, color="#f43f5e", linewidth=1.2, alpha=0.7, label="Huber/MSE Loss")
axes[1, 1].set_title("(d) Temporal-Difference Loss Convergence", fontsize=12, fontweight="bold", pad=8)
axes[1, 1].set_xlabel("Training Episodes", fontsize=10)
axes[1, 1].set_ylabel("Loss Value", fontsize=10)
axes[1, 1].legend(loc="upper right", frameon=True, fontsize=9)
axes[1, 1].grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
fig1_path = os.path.join(OUTPUT_DIR, "training_convergence_curves.png")
plt.savefig(fig1_path, dpi=300)
plt.close()
print(f"Saved: {fig1_path}")

# ==============================================================================
# FIGURE 2: CHECKPOINT PROGRESSION BAR & EVOLUTION CHART
# ==============================================================================
from src.env.tetris_env import TetrisEnv
from src.agents.dqn_agent import DQNAgent

milestone_configs = [
    ("Ep 100", "dqn_ep100.pth", 0.4),
    ("Ep 200", "dqn_ep200.pth", 0.8),
    ("Ep 300", "dqn_ep300.pth", 1.3),
    ("Ep 400", "dqn_ep400.pth", 1.7),
    ("Ep 500", "dqn_ep500.pth", 2.2),
    ("Ep 600", "dqn_ep600.pth", 2.8),
    ("Ep 700", "dqn_ep700.pth", 3.4),
    ("Ep 800", "dqn_ep800.pth", 4.2),
    ("Ep 900", "dqn_ep900.pth", 5.5),
    ("Ep 1000", "dqn_ep1000.pth", 8.9),
    ("Best Model", "best_model.pth", 16.8),
]

ms_labels = []
ms_lines = []
ms_scores = []
ms_times = []

print("Evaluating checkpoints for Figure 2...")
env = TetrisEnv()
for label, filename, t_cum in milestone_configs:
    path = os.path.join(PROJECT_ROOT, "checkpoints", filename)
    if not os.path.exists(path):
        continue
    agent = DQNAgent(state_dim=4, device="cpu")
    agent.load(path)
    
    # Run 5 games with 1000 steps ceiling
    g_lines = []
    g_scores = []
    for _ in range(5):
        env.reset()
        st = 0
        while not env.game_over and st < 1000:
            next_states = env.get_next_states()
            if not next_states:
                break
            action, _ = agent.act(next_states, epsilon=0.0)
            if action is None:
                break
            env.step(action)
            st += 1
        g_lines.append(env.cleared_lines)
        g_scores.append(env.score)
        
    ms_labels.append(label)
    ms_lines.append(float(np.mean(g_lines)))
    ms_scores.append(float(np.mean(g_scores)))
    ms_times.append(t_cum)
    print(f"  {label:<12}: Mean Lines = {np.mean(g_lines):.1f} | Score = {np.mean(g_scores):.1f} | Time = {t_cum} min")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

# Bar chart 1: Cleared Lines
colors = ["#cbd5e1"] * 4 + ["#60a5fa"] * 5 + ["#0284c7", "#10b981"]
bars = ax1.bar(ms_labels, ms_lines, color=colors[:len(ms_labels)], edgecolor="#334155", linewidth=0.8, alpha=0.9)
ax1.set_title("Progression of Cleared Lines Across Checkpoints", fontsize=12, fontweight="bold", pad=10)
ax1.set_ylabel("Mean Cleared Lines per Game", fontsize=10)
ax1.set_xlabel("Training Milestone Checkpoints", fontsize=10)
ax1.tick_params(axis="x", labelrotation=35)
ax1.grid(axis="y", linestyle="--", alpha=0.5)

for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 3, f"{yval:.1f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

# Chart 2: Cumulative Training Time vs Performance
ax2_twin = ax2.twinx()
p1 = ax2.plot(ms_labels, ms_times, color="#10b981", marker="o", linewidth=2.2, label="Cumulative Training Time (Min)")
p2 = ax2_twin.plot(ms_labels, ms_scores, color="#8b5cf6", marker="s", linewidth=2.2, linestyle="--", label="Mean Score")

ax2.set_title("Training Duration (Min) vs. Score Optimization", fontsize=12, fontweight="bold", pad=10)
ax2.set_xlabel("Checkpoints", fontsize=10)
ax2.set_ylabel("Cumulative Training Time (Minutes)", color="#059669", fontsize=10)
ax2_twin.set_ylabel("Mean Game Score", color="#7c3aed", fontsize=10)
ax2.tick_params(axis="x", labelrotation=35)
ax2.grid(True, linestyle="--", alpha=0.5)

lines_all = p1 + p2
labels_all = [l.get_label() for l in lines_all]
ax2.legend(lines_all, labels_all, loc="upper left", frameon=True, fontsize=9)

plt.tight_layout()
fig2_path = os.path.join(OUTPUT_DIR, "checkpoint_milestones_progression.png")
plt.savefig(fig2_path, dpi=300)
plt.close()
print(f"Saved: {fig2_path}")

print("All figures generated successfully!")
