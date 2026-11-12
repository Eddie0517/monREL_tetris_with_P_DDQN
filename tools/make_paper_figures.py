"""
Tạo hình (PDF) cho paper từ kết quả Kaggle trong result/.
  python tools/make_paper_figures.py
Ghi vào: paper write/LaTeX2e+Proceedings+Template+ZIP (1)/figures/
"""
import json
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "result")
OUT = os.path.join(ROOT, "paper write", "LaTeX2e+Proceedings+Template+ZIP (1)", "figures")
os.makedirs(OUT, exist_ok=True)

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#dddcd8"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "legend.fontsize": 7,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "lines.linewidth": 1.4,
})
CM = 1 / 2.54
TEXTWIDTH = 12.2 * CM  # LNCS


def load(group):
    d = os.path.join(RES, f"results_{group}", f"results_{group}")
    rows = json.load(open(os.path.join(d, "reports", "sweep_results.json"), encoding="utf-8"))
    for r in rows:
        r["dir"] = os.path.join(d, "checkpoints", f"{r['config']}_s{r['seed']}")
    return rows


def curve(run_dir):
    pts = []
    for line in open(os.path.join(run_dir, "train.log"), encoding="utf-8", errors="ignore"):
        m = re.match(r"Ep\s+(\d+)/\d+.*Avg50:\s*([\d.]+)", line)
        if m:
            pts.append((int(m[1]), float(m[2])))
    return np.array(pts)


LABELS = {
    "baseline": "baseline (SARSA)", "lines_x2": "lines ×2", "lines_half": "lines ×0.5",
    "holes_x2": "holes ×2", "holes_half": "holes ×0.5", "bump_x2": "bump ×2", "bump_0": "bump = 0",
    "height_x2": "height ×2", "height_0": "height = 0", "alive_0": "alive = 0",
    "gameover_50": "game-over 50", "lines_only": "lines only",
    "gamma_095": "γ = 0.95", "lr_5e-4": "lr = 5e-4", "target_5": "sync 5 ep", "target_25": "sync 25 ep",
    "eps_decay_600": "ε-decay 600", "hidden_128": "hidden 128", "batch_256": "batch 256",
    "qlearning": "Q-learning", "double_q": "Double Q", "expected_sarsa": "Expected SARSA",
    "sarsa_1050": "SARSA", "qlearning_1050": "Q-learning", "double_q_1050": "Double Q",
    "expected_sarsa_1050": "Expected SARSA",
}


def per_config(rows, configs):
    out = {}
    for c in configs:
        rs = sorted([r for r in rows if r["config"] == c], key=lambda r: r["seed"])
        out[c] = {w: np.array([r["eval"][w]["mean_lines"] for r in rs]) for w in ("best", "latest")}
    return out


def fig_ablation():
    panels = [
        ("(a) Reward weights (CPU)", load("reward"), None),
        ("(b) Training hyper-parameters (CPU)", load("hparam"), None),
        ("(c) TD target, 2000 episodes (GPU)", load("target"),
         ["baseline", "qlearning", "double_q", "expected_sarsa"]),
    ]
    sizes = []
    for _, rows, only in panels:
        cfgs = only or list(dict.fromkeys(r["config"] for r in rows))
        sizes.append(len(cfgs))
    fig, axes = plt.subplots(3, 1, figsize=(TEXTWIDTH, 13.0 * CM), sharex=True,
                             gridspec_kw={"height_ratios": [s + 1.2 for s in sizes]})
    for ax, (title, rows, only) in zip(axes, panels):
        cfgs = only or list(dict.fromkeys(r["config"] for r in rows))
        data = per_config(rows, cfgs)
        cfgs = sorted(cfgs, key=lambda c: data[c]["best"].mean())
        for i, c in enumerate(cfgs):
            b, l = data[c]["best"], data[c]["latest"]
            ax.plot([0, 400], [i, i], color=GRID, lw=0.6, zorder=0)
            ax.scatter(l, np.full(3, i - 0.15), s=18, facecolors="white", edgecolors=ORANGE, linewidths=1.1,
                       zorder=3, label="latest checkpoint (per seed)" if i == 0 else None)
            ax.scatter(b, np.full(3, i + 0.15), s=18, color=BLUE, edgecolors="white", linewidths=0.6,
                       zorder=4, label="best checkpoint (per seed)" if i == 0 else None)
            ax.plot([b.mean()] * 2, [i + 0.02, i + 0.38], color=BLUE, lw=1.6, zorder=5)
            ax.plot([l.mean()] * 2, [i - 0.38, i - 0.02], color=ORANGE, lw=1.6, zorder=5)
        ax.set_yticks(range(len(cfgs)))
        ax.set_yticklabels([LABELS[c] for c in cfgs])
        for t, c in zip(ax.get_yticklabels(), cfgs):
            if c == "baseline":
                t.set_fontweight("bold")
        ax.set_ylim(-0.7, len(cfgs) - 0.3)
        ax.set_title(title, loc="left", color=INK)
        ax.axvline(400, color=INK2, lw=0.6, ls=":")
        ax.tick_params(axis="y", length=0)
    axes[0].legend(loc="lower left", frameon=False, ncol=2, bbox_to_anchor=(0, 1.08), handletextpad=0.3)
    axes[-1].set_xlabel("Mean lines cleared per game (100 games, 1000-placement cap; dotted line = cap ≈ 400)")
    axes[-1].set_xlim(-8, 410)
    fig.tight_layout(h_pad=0.6)
    fig.savefig(os.path.join(OUT, "fig_ablation.pdf"))
    plt.close(fig)


def fig_1050():
    rows = load("target")
    cfgs = ["sarsa_1050", "qlearning_1050", "double_q_1050", "expected_sarsa_1050"]
    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 5.0 * CM))
    for i, c in enumerate(cfgs):
        rs = sorted([r for r in rows if r["config"] == c], key=lambda r: r["seed"])
        ev = np.array([r["eval"]["latest"]["mean_lines"] for r in rs])
        tr = np.array([curve(r["dir"])[-1, 1] for r in rs])
        offs = np.array([-0.18, 0, 0.18])
        ax.scatter(i + offs, ev, s=26, color=BLUE, edgecolors="white", linewidths=0.6, zorder=3,
                   label="greedy evaluation, ε = 0 (per seed)" if i == 0 else None)
        ax.scatter(i + offs, tr, s=22, facecolors="white", edgecolors=ORANGE, linewidths=1.1, zorder=3,
                   marker="s", label="training Avg50 at episode 1050, ε ≈ 0.13" if i == 0 else None)
        ok = int((ev >= 250).sum())
        ax.text(i, 430, f"{ok}/3 seeds learn", ha="center", va="bottom", color=INK, fontsize=7)
    ax.set_xticks(range(len(cfgs)))
    ax.set_xticklabels([LABELS[c] for c in cfgs])
    ax.set_ylabel("Mean lines per game")
    ax.set_ylim(-15, 470)
    ax.set_xlim(-0.6, len(cfgs) - 0.4)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", frameon=False, ncol=2, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_1050.pdf"))
    plt.close(fig)


def fig_curves():
    rows = load("target")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(TEXTWIDTH, 6.6 * CM), sharey=True)
    colors = {"baseline": BLUE, "qlearning": ORANGE, "double_q": AQUA, "expected_sarsa": YELLOW}
    for c, col in colors.items():
        cs = [curve(r["dir"]) for r in rows if r["config"] == c]
        grid = np.arange(10, 2001, 10)
        ys = np.array([np.interp(grid, cv[:, 0], cv[:, 1]) for cv in cs])
        a1.plot(grid, ys.mean(0), color=col, label=LABELS[c], lw=1.4)
    a1.axvline(1200, color=INK2, lw=0.6, ls=":")
    a1.text(1170, 130, "ε reaches 0.001", ha="right", va="bottom", fontsize=6.5, color=INK2)
    a1.set_title("(a) Mean training curve over 3 seeds", loc="left")
    a1.set_xlabel("Episode")
    a1.set_ylabel("Avg50 lines (training, ε-greedy)")
    a1.legend(frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.62))

    collapsed = [("target", "expected_sarsa", 0, YELLOW, "Expected SARSA, seed 0"),
                 ("target", "qlearning", 2, ORANGE, "Q-learning, seed 2"),
                 ("target", "baseline", 0, BLUE, "SARSA, seed 0"),
                 ("hparam", "gamma_095", 1, INK2, "γ = 0.95, seed 1")]
    cache = {"target": rows}
    for g, c, s, col, lab in collapsed:
        rr = cache.setdefault(g, load(g))
        r = next(r for r in rr if r["config"] == c and r["seed"] == s)
        cv = curve(r["dir"])
        a2.plot(cv[:, 0], cv[:, 1], color=col, lw=1.1, label=lab)
    a2.set_xlim(1000, 2010)
    a2.set_title("(b) Late-training collapse (single runs)", loc="left")
    a2.set_xlabel("Episode")
    a2.legend(frameon=False, loc="upper center", fontsize=6.5, ncol=2, bbox_to_anchor=(0.5, -0.27), columnspacing=0.8)
    for ax in (a1, a2):
        ax.grid(color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.set_ylim(-10, 620)
    fig.tight_layout(w_pad=0.8)
    fig.savefig(os.path.join(OUT, "fig_curves.pdf"))
    plt.close(fig)


def fig_tradeoff():
    """Survival vs. combo: mean lines vs. points per line (best checkpoint, seed means)."""
    groups = [("reward", "Reward weights (CPU)", BLUE, "o"),
              ("hparam", "Hyper-parameters (CPU)", ORANGE, "s"),
              ("target", "TD target, 2000 ep (GPU)", AQUA, "D")]
    label_these = {
        ("reward", "baseline"): ("baseline", (-6, -9)),
        ("reward", "lines_half"): ("lines ×0.5", (5, 2)),
        ("reward", "lines_only"): ("lines only", (5, -6)),
        ("reward", "bump_x2"): ("bump ×2", (8, -7)),
        ("hparam", "gamma_095"): ("γ = 0.95", (-40, 1)),
        ("hparam", "hidden_128"): ("hidden 128", (6, -4)),
        ("hparam", "batch_256"): ("batch 256", (5, 2)),
        ("hparam", "lr_5e-4"): ("lr 5e-4", (5, 2)),
        ("target", "expected_sarsa"): ("Expected SARSA", (-38, -12)),
        ("target", "double_q"): ("Double Q", (5, 2)),
        ("target", "qlearning"): ("Q-learning", (-48, -3)),
        ("target", "baseline"): ("SARSA (GPU)", (-22, 7)),
    }
    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 6.4 * CM))
    xs = np.linspace(100, 410, 200)
    for sc in (15000, 20000, 25000, 30000):
        ax.plot(xs, sc / xs, color=GRID, lw=0.8, zorder=0)
        ax.text(sc / 104, 104, f"{sc // 1000}k pts", fontsize=6, color=INK2, va="top", ha="left")
    for g, name, col, mk in groups:
        rows = load(g)
        cfgs = list(dict.fromkeys(r["config"] for r in rows if not r["config"].endswith("_1050")))
        for c in cfgs:
            rs = [r for r in rows if r["config"] == c]
            x = np.mean([r["eval"]["best"]["mean_lines"] for r in rs])
            y = np.mean([r["eval"]["best"]["points_per_line"] for r in rs])
            if g == "hparam" and c == "baseline":
                continue  # identical to the reward-group baseline (deterministic CPU)
            ax.scatter(x, y, s=30, marker=mk, color=col, edgecolors="white", linewidths=0.6, zorder=3,
                       label=name if c == cfgs[0] or (g == "hparam" and c == cfgs[1] and cfgs[0] == "baseline") else None)
            if (g, c) in label_these:
                lab, off = label_these[(g, c)]
                ax.annotate(lab, (x, y), xytext=off, textcoords="offset points", fontsize=6.5, color=INK)
    ax.set_xlabel("Mean lines per game (best checkpoint, mean of 3 seeds)")
    ax.set_ylabel("Points per line")
    ax.set_xlim(100, 410)
    ax.set_ylim(40, 105)
    ax.grid(color=GRID, lw=0.4, ls=":")
    ax.set_axisbelow(True)
    handles, labels = ax.get_legend_handles_labels()
    seen = {}
    for h, l in zip(handles, labels):
        seen.setdefault(l, h)
    ax.legend(seen.values(), seen.keys(), frameon=False, loc="lower left", fontsize=6.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_tradeoff.pdf"))
    plt.close(fig)


def fig_pipeline():
    """Acting loop (top) and learning loop (bottom) of the agent."""
    from matplotlib.patches import FancyBboxPatch

    fig, ax = plt.subplots(figsize=(TEXTWIDTH, 5.0 * CM))
    ax.set_xlim(-0.15, 10.45)
    ax.set_ylim(0.15, 4.15)
    ax.axis("off")
    W, H = 1.7, 0.8
    xs = [0.85, 3.0, 5.15, 7.3, 9.45]
    y1, y2 = 3.0, 0.8
    boxes = {
        "env": (xs[0], y1, "Tetris\nenvironment", "#e8eefb"),
        "enum": (xs[1], y1, "Placement\nenumeration", "white"),
        "feat": (xs[2], y1, "Afterstate\nfeatures", "white"),
        "mlp": (xs[3], y1, "Online\nnetwork", "#fdeedd"),
        "pol": (xs[4], y1, "ε-greedy\npolicy", "white"),
        "buf": (xs[0], y2, "Replay\nbuffer", "#e5f6ec"),
        "tnet": (xs[1], y2, "Target\nnetwork", "white"),
        "tgt": (xs[2], y2, "TD target", "#fdf7d9"),
        "loss": (xs[4], y2, "Loss and\nupdate", "white"),
    }
    for _, (x, y, txt, col) in boxes.items():
        ax.add_patch(FancyBboxPatch((x - W / 2, y - H / 2), W, H, boxstyle="round,pad=0.0,rounding_size=0.08",
                                    fc=col, ec="#555555", lw=0.8))
        ax.text(x, y, txt, ha="center", va="center", fontsize=8, color=INK, linespacing=1.15)

    def arrow(p, q, ls="-"):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color="#333333", lw=0.8,
                                                         linestyle=ls, shrinkA=0, shrinkB=0, mutation_scale=8))

    # acting loop (top row)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow((a + W / 2, y1), (b - W / 2, y1))
    top = y1 + H / 2
    ax.plot([xs[4], xs[4], xs[0]], [top, 3.85, 3.85], color="#333333", lw=0.8)
    arrow((xs[0], 3.85), (xs[0], top))
    ax.text((xs[0] + xs[4]) / 2, 3.9, "action", ha="center", va="bottom", fontsize=7.5, color=INK)

    # learning loop (bottom row)
    arrow((xs[0], y1 - H / 2), (xs[0], y2 + H / 2))
    ax.text(xs[0] + 0.08, (y1 + y2) / 2, "transitions", ha="left", va="center", fontsize=7.5, color=INK)
    arrow((xs[0] + W / 2, y2), (xs[1] - W / 2, y2))
    arrow((xs[1] + W / 2, y2), (xs[2] - W / 2, y2))
    arrow((xs[2] + W / 2, y2), (xs[4] - W / 2, y2))
    # periodic copy: online network -> target network (dashed)
    ymid = 1.85
    ax.plot([xs[3], xs[3], xs[1]], [y1 - H / 2, ymid, ymid], color="#333333", lw=0.8, ls=(0, (3, 2)))
    arrow((xs[1], ymid), (xs[1], y2 + H / 2), ls=(0, (3, 2)))
    ax.text((xs[1] + xs[3]) / 2, ymid + 0.07, "periodic copy", ha="center", va="bottom", fontsize=7.5, color=INK)
    # gradient update: loss -> online network
    arrow((xs[4], y2 + H / 2), (xs[3] + W / 2 - 0.15, y1 - H / 2))
    ax.text(xs[4] - 0.05, (y1 + y2) / 2 + 0.05, "update", ha="left", va="center", fontsize=7.5, color=INK)
    fig.tight_layout(pad=0.1)
    fig.savefig(os.path.join(OUT, "fig_pipeline.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    fig_pipeline()
    fig_ablation()
    fig_1050()
    fig_curves()
    fig_tradeoff()
    print("figures ->", OUT, os.listdir(OUT))
