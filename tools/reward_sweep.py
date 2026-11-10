"""
Sweep so sánh các cấu hình reward / siêu tham số cho P-DDQN.

Mỗi cấu hình:
  1. Train bằng src/train.py (cùng số episode, cùng seed) -> checkpoints/sweep/<run>/
  2. Đánh giá best_model.pth và latest_model.pth theo đúng metric Table 1 của report
     (100 games, trần 1000 bước, seed cố định -> mọi cấu hình gặp cùng chuỗi khối gạch)
  3. Gộp kết quả -> reports/sweep/sweep_results.json + sweep_table.md

Ví dụ:
  python tools/reward_sweep.py --list
  python tools/reward_sweep.py                              # chạy toàn bộ
  python tools/reward_sweep.py --only baseline holes_x2     # chạy vài cấu hình
  python tools/reward_sweep.py --group reward --seeds 0 1 2 # 3 seed mỗi cấu hình
  python tools/reward_sweep.py --skip-train                 # chỉ đánh giá lại + xuất bảng
  python tools/reward_sweep.py --group reward --seeds 0 1 2 --jobs 4 --device cuda --gpus 2 --stop-at <unix time>
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.agents.dqn_agent import DQNAgent
from src.evaluate import evaluate_agent

# ---------------------------------------------------------------------------
# DANH SÁCH CẤU HÌNH (one-factor-at-a-time: mỗi run chỉ đổi 1 thứ so với baseline)
# Baseline = đúng cấu hình trong report (slide 6):
#   r = 1 + 10·f4² − 0.5·Δf1 − 1.5·Δf2 − 0.5·Δf3, thua −10
# Key trong "args" là tham số CLI của src/train.py (bỏ dấu "--").
# ---------------------------------------------------------------------------
CONFIGS = {
    # ----- Nhóm 1: trọng số reward -----
    "baseline":       ("reward", "Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10", {}),
    "lines_x2":       ("reward", "Thưởng dọn hàng ×2 (lines=20)",              {"r-lines": 20}),
    "lines_half":     ("reward", "Thưởng dọn hàng ×0.5 (lines=5)",             {"r-lines": 5}),
    "holes_x2":       ("reward", "Phạt lỗ ×2 (holes=3.0)",                     {"r-holes": 3.0}),
    "holes_half":     ("reward", "Phạt lỗ ×0.5 (holes=0.75)",                  {"r-holes": 0.75}),
    "bump_x2":        ("reward", "Phạt gồ ghề ×2 (bump=1.0)",                  {"r-bumpiness": 1.0}),
    "bump_0":         ("reward", "Bỏ phạt gồ ghề (bump=0)",                    {"r-bumpiness": 0}),
    "height_x2":      ("reward", "Phạt chiều cao ×2 (height=1.0)",             {"r-height": 1.0}),
    "height_0":       ("reward", "Bỏ phạt chiều cao (height=0)",               {"r-height": 0}),
    "alive_0":        ("reward", "Bỏ thưởng sống sót (alive=0)",               {"r-alive": 0}),
    "gameover_50":    ("reward", "Phạt thua nặng (game_over=50)",              {"r-game-over": 50}),
    "lines_only":     ("reward", "Chỉ thưởng dọn hàng + sống (bỏ hết shaping)",
                       {"r-holes": 0, "r-bumpiness": 0, "r-height": 0}),
    # ----- Nhóm 2: siêu tham số huấn luyện -----
    "gamma_095":      ("hparam", "Discount gamma=0.95 (mặc định 0.99)",        {"gamma": 0.95}),
    "lr_5e-4":        ("hparam", "Learning rate 5e-4 (mặc định 1e-3)",         {"lr": 5e-4}),
    "target_5":       ("hparam", "Đồng bộ target net mỗi 5 ep (mặc định 10)",  {"target-update-freq": 5}),
    "target_25":      ("hparam", "Đồng bộ target net mỗi 25 ep",               {"target-update-freq": 25}),
    "eps_decay_600":  ("hparam", "Epsilon giảm trong 600 ep (mặc định 1200)",  {"decay-episodes": 600}),
    "hidden_128":     ("hparam", "MLP 128 neuron/lớp (mặc định 64)",           {"hidden-dim": 128}),
    "batch_256":      ("hparam", "Batch 256 (mặc định 512)",                   {"batch-size": 256}),
    # ----- Nhóm 3: cách tính target TD (doc/2.8 Q-learning, doc/2.9 Expected Sarsa) -----
    # "baseline" chính là sarsa 2000 ep (cách gốc của project)
    "qlearning":      ("target", "Q-learning: max_a' U⁻(s'_a')",               {"target-mode": "qlearning"}),
    "double_q":       ("target", "Double Q: U⁻(argmax_a' U_online)",           {"target-mode": "double_q"}),
    "expected_sarsa": ("target", "Expected SARSA: (1-ε)·max + ε·mean",         {"target-mode": "expected_sarsa"}),
    # Cùng 4 cách nhưng chỉ 1050 episode (như report, decay 1200): off-policy có học nhanh hơn không?
    "sarsa_1050":          ("target", "SARSA (gốc), 1050 ep",          {"episodes": 1050}),
    "qlearning_1050":      ("target", "Q-learning, 1050 ep",           {"target-mode": "qlearning", "episodes": 1050}),
    "double_q_1050":       ("target", "Double Q, 1050 ep",             {"target-mode": "double_q", "episodes": 1050}),
    "expected_sarsa_1050": ("target", "Expected SARSA, 1050 ep",       {"target-mode": "expected_sarsa", "episodes": 1050}),
}


class DeadlineReached(Exception):
    """Hết thời gian cho phép (--stop-at): run bị bỏ dở, lần chạy sau sẽ làm lại."""


# Mỗi job đang train giữ 1 "slot"; slot quyết định GPU nào (round-robin khi có nhiều GPU)
SLOTS = queue.Queue()


def run_cmd(cmd, args, log=None, extra_env=None):
    """Chạy process con; nếu tới --stop-at thì kill và báo DeadlineReached."""
    env = worker_env()
    env.update(extra_env or {})
    proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT, env=env,
                            stdout=log, stderr=subprocess.STDOUT if log else None)
    while True:
        try:
            ret = proc.wait(timeout=5)
            break
        except subprocess.TimeoutExpired:
            if args.stop_at and time.time() > args.stop_at:
                proc.kill()
                proc.wait()
                raise DeadlineReached()
    if ret != 0:
        raise subprocess.CalledProcessError(ret, cmd)


def run_name(cfg, seed):
    return f"{cfg}_s{seed}"


def train_one(cfg, seed, args, slot=0):
    _, _, overrides = CONFIGS[cfg]
    cmd = [
        sys.executable, os.path.join(PROJECT_ROOT, "src", "train.py"),
        "--episodes", str(args.episodes),
        "--decay-episodes", str(args.decay_episodes),
        "--seed", str(seed),
        "--run-name", run_name(cfg, seed),
        "--checkpoint-dir", args.checkpoint_dir,
        "--log-dir", args.log_dir,
        "--log-freq", "10",  # đủ dày để vẽ đường cong học
        "--save-freq", str(args.episodes + 1),  # không lưu checkpoint trung gian
        "--max-episode-steps", str(args.max_episode_steps),
        "--device", args.device,
    ]
    for k, v in overrides.items():
        if k in ("decay-episodes", "episodes"):
            cmd[cmd.index(f"--{k}") + 1] = str(v)
        else:
            cmd += [f"--{k}", str(v)]
    run_dir = os.path.join(args.checkpoint_dir, run_name(cfg, seed))
    # Xóa run dở dang (nếu có): train.py đặt best_lines=17 khi đã có best_model.pth cũ
    if os.path.isdir(run_dir):
        shutil.rmtree(run_dir)
    os.makedirs(run_dir, exist_ok=True)
    log_path = os.path.join(run_dir, "train.log")
    print(f">>> TRAIN start {run_name(cfg, seed)} (log: {log_path})", flush=True)
    t0 = time.time()
    extra = {}
    if args.device == "cuda" and args.gpus > 0:
        extra["CUDA_VISIBLE_DEVICES"] = str(slot % args.gpus)
    with open(log_path, "w", encoding="utf-8") as log:
        run_cmd(cmd, args, log=log, extra_env=extra)
    secs = time.time() - t0
    with open(os.path.join(run_dir, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"train_seconds": secs, "finished": True}, f)
    print(f">>> TRAIN done  {run_name(cfg, seed)} in {secs / 60:.1f} min", flush=True)
    return secs


def worker_env():
    """Mỗi job dùng 1 luồng CPU để chạy song song nhiều job không tranh nhau."""
    env = dict(os.environ)
    env.update({"OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "PYTHONIOENCODING": "utf-8"})
    return env


def eval_subprocess(cfg, seed, args):
    """Chạy eval trong process riêng (để song song thật, không bị GIL)."""
    cmd = [
        sys.executable, os.path.abspath(__file__), "--worker-eval", cfg, str(seed),
        "--games", str(args.games), "--max-steps", str(args.max_steps),
        "--eval-seed", str(args.eval_seed), "--checkpoint-dir", args.checkpoint_dir,
    ]
    run_cmd(cmd, args, extra_env={"CUDA_VISIBLE_DEVICES": ""})  # eval chạy CPU
    with open(os.path.join(args.checkpoint_dir, run_name(cfg, seed), "eval.json"), encoding="utf-8") as f:
        return json.load(f)


def run_job(cfg, seed, args):
    secs = None
    run_dir = os.path.join(args.checkpoint_dir, run_name(cfg, seed))
    meta_path = os.path.join(run_dir, "run_meta.json")
    eval_path = os.path.join(run_dir, "eval.json")
    # Resume: run đã train + eval xong thì dùng lại kết quả
    if not args.force and os.path.exists(meta_path) and os.path.exists(eval_path):
        with open(meta_path, encoding="utf-8") as f:
            secs = json.load(f).get("train_seconds")
        with open(eval_path, encoding="utf-8") as f:
            ev = json.load(f)
        print(f"=== RESUME {run_name(cfg, seed)}: đã xong, dùng lại kết quả", flush=True)
        return {
            "config": cfg, "seed": seed, "group": CONFIGS[cfg][0],
            "overrides": CONFIGS[cfg][2], "train_seconds": secs, "eval": ev,
        }
    # Train xong nhưng chưa eval -> chỉ eval
    if not args.force and os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            secs = json.load(f).get("train_seconds")
        print(f"=== RESUME {run_name(cfg, seed)}: đã train, chỉ eval", flush=True)
        ev = eval_subprocess(cfg, seed, args)
        return {
            "config": cfg, "seed": seed, "group": CONFIGS[cfg][0],
            "overrides": CONFIGS[cfg][2], "train_seconds": secs, "eval": ev,
        }
    if args.skip_train:
        if not os.path.exists(os.path.join(args.checkpoint_dir, run_name(cfg, seed), "run_config.json")):
            print(f"skip {run_name(cfg, seed)}: chưa train", flush=True)
            return None
    else:
        # Không bắt đầu run mới nếu không đủ thời gian để xong trước --stop-at
        if args.stop_at and time.time() + args.min_start_minutes * 60 > args.stop_at:
            raise DeadlineReached()
        slot = SLOTS.get()
        try:
            secs = train_one(cfg, seed, args, slot)
        finally:
            SLOTS.put(slot)
    ev = eval_subprocess(cfg, seed, args)
    return {
        "config": cfg, "seed": seed, "group": CONFIGS[cfg][0],
        "overrides": CONFIGS[cfg][2], "train_seconds": secs, "eval": ev,
    }


def eval_one(cfg, seed, args):
    run_dir = os.path.join(args.checkpoint_dir, run_name(cfg, seed))
    with open(os.path.join(run_dir, "run_config.json"), encoding="utf-8") as f:
        hidden = json.load(f)["args"]["hidden_dim"]
    out = {}
    for ckpt in ("best_model.pth", "latest_model.pth"):
        path = os.path.join(run_dir, ckpt)
        if not os.path.exists(path):
            continue
        agent = DQNAgent(state_dim=4, hidden_dim=hidden, device="cpu")
        agent.load(path)
        r = evaluate_agent(agent, True, args.games, args.max_steps, args.eval_seed)
        out[ckpt.replace("_model.pth", "")] = r
        print(f"    eval {run_name(cfg, seed)} {ckpt:<17} lines {r['mean_lines']:.1f}±{r['std_lines']:.1f} | "
              f"score {r['mean_score']:.0f} | pts/line {r['points_per_line']:.1f} | "
              f"cap {r['cap_hits']}/{r['games']}", flush=True)
    with open(os.path.join(run_dir, "eval.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out


def aggregate(rows, which):
    """Gộp nhiều seed của cùng một cấu hình: trung bình các metric chính."""
    keys = ["mean_lines", "std_lines", "median_lines", "max_lines", "mean_score",
            "mean_placements", "points_per_line", "cap_hits"]
    vals = [r["eval"][which] for r in rows if which in r["eval"]]
    if not vals:
        return None
    agg = {k: float(np.mean([v[k] for v in vals])) for k in keys}
    agg["seed_std_mean_lines"] = float(np.std([v["mean_lines"] for v in vals]))
    agg["n_seeds"] = len(vals)
    agg["games"] = vals[0]["games"]
    return agg


def write_report(all_rows, args):
    os.makedirs(args.output_dir, exist_ok=True)
    with open(os.path.join(args.output_dir, "sweep_results.json"), "w", encoding="utf-8") as f:
        json.dump(all_rows, f, indent=2, ensure_ascii=False)

    by_cfg = {}
    for r in all_rows:
        by_cfg.setdefault(r["config"], []).append(r)

    md = [
        "# Reward / Hyper-parameter Sweep – P-DDQN",
        "",
        f"Train: {args.episodes} episodes/run (trần {args.max_episode_steps} khối/episode). Eval: {args.games} games, trần {args.max_steps} bước, "
        f"eval seed {args.eval_seed} (mọi cấu hình gặp cùng chuỗi khối gạch).",
        "Metric theo Table 1 của report. Δ Lines tính so với `baseline`.",
        "",
    ]
    for which in ("best", "latest"):
        base = aggregate(by_cfg.get("baseline", []), which)
        md += [
            f"## Checkpoint `{which}_model.pth`",
            "",
            "| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |",
            "|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|",
        ]
        for cfg in CONFIGS:
            if cfg not in by_cfg:
                continue
            a = aggregate(by_cfg[cfg], which)
            if a is None:
                continue
            group, desc, _ = CONFIGS[cfg]
            seed_note = f" (±{a['seed_std_mean_lines']:.1f} giữa seed)" if a["n_seeds"] > 1 else ""
            delta = f"{a['mean_lines'] - base['mean_lines']:+.1f}" if base and cfg != "baseline" else "—"
            mins = np.mean([r["train_seconds"] for r in by_cfg[cfg] if r.get("train_seconds")] or [0]) / 60
            md.append(
                f"| `{cfg}` | {group} | {desc} | {a['n_seeds']} | {a['mean_lines']:.1f} ± {a['std_lines']:.1f}{seed_note} | "
                f"{a['median_lines']:.1f} | {a['max_lines']:.0f} | {a['mean_score']:.1f} | {a['mean_placements']:.1f} | "
                f"{a['points_per_line']:.1f} | {a['cap_hits']:.1f}/{a['games']} | {delta} | {mins:.1f} |"
            )
        md.append("")
    path = os.path.join(args.output_dir, "sweep_table.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"\nSaved: {path}", flush=True)


def main():
    p = argparse.ArgumentParser(description="Sweep reward weights / hyper-params for P-DDQN")
    p.add_argument("--list", action="store_true", help="In danh sách cấu hình rồi thoát")
    p.add_argument("--only", nargs="+", default=None, help="Chỉ chạy các cấu hình này")
    p.add_argument("--group", choices=["reward", "hparam", "target"], default=None, help="Chỉ chạy 1 nhóm")
    p.add_argument("--seeds", nargs="+", type=int, default=[0], help="Seed train (nhiều seed = tin cậy hơn)")
    # Pilot 03/11/2026: 1050 ep (như report) không đủ để baseline học; 2000 ep / decay 1200 thì học ổn định.
    p.add_argument("--episodes", type=int, default=2000, help="Số episode train")
    p.add_argument("--max-episode-steps", type=int, default=1500,
                   help="Trần số khối mỗi episode khi train (giới hạn thời gian khi agent đã giỏi)")
    p.add_argument("--decay-episodes", type=int, default=1200, help="Epsilon decay (mặc định train.py)")
    p.add_argument("--games", type=int, default=100)
    p.add_argument("--max-steps", type=int, default=1000)
    p.add_argument("--eval-seed", type=int, default=12345, help="Seed eval, khác seed train")
    p.add_argument("--skip-train", action="store_true", help="Không train, chỉ eval checkpoint có sẵn")
    p.add_argument("--checkpoint-dir", default="checkpoints/sweep")
    p.add_argument("--log-dir", default="logs/sweep")
    p.add_argument("--output-dir", default="reports/sweep")
    p.add_argument("--jobs", type=int, default=1, help="Số job chạy song song (mỗi job 1 nhân CPU)")
    p.add_argument("--force", action="store_true", help="Train/eval lại cả các run đã xong")
    p.add_argument("--device", default="cpu", help="Thiết bị train: cpu | cuda")
    p.add_argument("--gpus", type=int, default=1, help="Số GPU để chia job (round-robin)")
    p.add_argument("--stop-at", type=float, default=None,
                   help="Unix time: kill các run đang chạy và không bắt đầu run mới sau mốc này")
    p.add_argument("--min-start-minutes", type=float, default=0,
                   help="Không bắt đầu run mới nếu còn ít hơn N phút tới --stop-at")
    p.add_argument("--worker-eval", nargs=2, metavar=("CONFIG", "SEED"), help=argparse.SUPPRESS)
    args = p.parse_args()

    if args.worker_eval:
        eval_one(args.worker_eval[0], int(args.worker_eval[1]), args)
        return

    if args.list:
        for name, (group, desc, ov) in CONFIGS.items():
            print(f"{name:<15} [{group}] {desc}  {ov or ''}")
        return

    cfgs = [c for c in CONFIGS
            if (args.only is None or c in args.only) and (args.group is None or CONFIGS[c][0] == args.group)]
    unknown = set(args.only or []) - set(CONFIGS)
    if unknown:
        sys.exit(f"Unknown config(s): {sorted(unknown)}. Dùng --list để xem.")

    # Giữ lại kết quả cũ của các cấu hình không chạy lần này
    results_path = os.path.join(args.output_dir, "sweep_results.json")
    all_rows = []
    if os.path.exists(results_path):
        with open(results_path, encoding="utf-8") as f:
            all_rows = json.load(f)
    done_now = {(c, s) for c in cfgs for s in args.seeds}
    all_rows = [r for r in all_rows if (r["config"], r["seed"]) not in done_now]

    # Thứ tự seed trước: nếu hết giờ giữa chừng, mọi cấu hình vẫn có ít nhất seed đầu tiên
    jobs = [(c, s) for s in args.seeds for c in cfgs]
    for i in range(args.jobs):
        SLOTS.put(i)
    print(f"Sweep: {len(jobs)} run(s), {args.jobs} song song, device={args.device}", flush=True)
    failed, unfinished = [], []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_job, c, s, args): (c, s) for c, s in jobs}
        for fut in as_completed(futures):
            c, s = futures[fut]
            try:
                row = fut.result()
            except DeadlineReached:
                unfinished.append(run_name(c, s))
                continue
            except Exception as e:
                print(f"!!! FAILED {run_name(c, s)}: {e}", flush=True)
                failed.append(run_name(c, s))
                continue
            if row is not None:
                all_rows.append(row)
                write_report(all_rows, args)  # ghi sau mỗi run để không mất kết quả nếu dừng giữa chừng
    write_report(all_rows, args)
    ok = len(jobs) - len(failed) - len(unfinished)
    print(f"\nSWEEP FINISHED. {ok}/{len(jobs)} ok" + (f", failed: {failed}" if failed else ""), flush=True)
    if unfinished:
        print(f"HẾT GIỜ: {len(unfinished)} run chưa xong (chạy lại để tiếp tục): {unfinished}", flush=True)


if __name__ == "__main__":
    main()
