"""
Tạo 2 notebook Kaggle (tự chứa mã nguồn, không cần upload dataset / bật Internet):

  notebooks/kaggle_group1_reward.ipynb   – ablation reward: 12 cấu hình × 3 seed = 36 run
  notebooks/kaggle_group2_hparam.ipynb   – siêu tham số:   7 cấu hình × 3 seed = 21 run (+ baseline)
  notebooks/kaggle_group3_target.ipynb   – target TD: SARSA / Q-learning / Double Q / Expected SARSA × {2000, 1050} ep

Mã nguồn (src/, tools/reward_sweep.py, tools/bench_throughput.py) được nhúng vào notebook dạng zip base64.
Sửa code xong thì chạy lại:  python tools/build_kaggle_notebooks.py
"""
import base64
import io
import os
import sys
import zipfile

import nbformat as nbf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE_FILES = [
    "src/__init__.py",
    "src/env/__init__.py", "src/env/tetris_env.py",
    "src/agents/__init__.py", "src/agents/heuristic_agent.py", "src/agents/dqn_agent.py",
    "src/models/__init__.py", "src/models/dqn_model.py",
    "src/train.py", "src/evaluate.py",  # train.py có --target-mode (Nhóm 3)
    "tools/reward_sweep.py", "tools/bench_throughput.py",
]


def code_zip_b64():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in CODE_FILES:
            z.write(os.path.join(ROOT, rel), rel)
    return base64.b64encode(buf.getvalue()).decode()


GROUPS = {
    "reward": {
        "file": "kaggle_group1_reward.ipynb",
        "title": "Nhóm 1 – Ablation reward (12 cấu hình × 3 seed = 36 run)",
        "only": None,
        "intro": (
            "Mỗi cấu hình chỉ đổi **một** trọng số so với `baseline` (reward gốc của report):\n\n"
            "$$r = 1 + 10\\cdot L^2 - 1.5\\,\\Delta\\text{Holes} - 0.5\\,\\Delta\\text{Bump} - 0.5\\,\\Delta\\text{Height}"
            "\\quad(-10 \\text{ khi thua})$$"
        ),
    },
    "hparam": {
        "file": "kaggle_group2_hparam.ipynb",
        "title": "Nhóm 2 – Siêu tham số (7 cấu hình × 3 seed = 21 run, + baseline)",
        "only": ["baseline", "gamma_095", "lr_5e-4", "target_5", "target_25",
                 "eps_decay_600", "hidden_128", "batch_256"],
        "intro": (
            "Reward giữ nguyên như `baseline`, mỗi cấu hình chỉ đổi **một** siêu tham số train.\n\n"
            "`baseline` được kèm vào để tính Δ. **Nếu gắn output của notebook Nhóm 1 làm Input** "
            "thì 3 run baseline được dùng lại (không train lại) → chỉ còn 21 run."
        ),
    },
    "target": {
        "file": "kaggle_group3_target.ipynb",
        "title": "Nhóm 3 – Cách tính target TD: SARSA vs Q-learning vs Double Q vs Expected SARSA",
        "only": ["baseline", "qlearning", "double_q", "expected_sarsa",
                 "sarsa_1050", "qlearning_1050", "double_q_1050", "expected_sarsa_1050"],
        "bench_mode": "qlearning",
        "intro": r"""Áp dụng `doc/2.8 Q-learning` và `doc/2.9 Expected Sarsa` vào P-DDQN (học giá trị afterstate $U$).
Reward và mọi siêu tham số giữ như `baseline`; **chỉ đổi giá trị bootstrap** của trạng thái kế tiếp
($A'$ = mọi vị trí đặt của khối kế tiếp, $U^-$ = mạng target):

| Config | Target cho $U(as_t)$ | Ý nghĩa |
|---|---|---|
| `baseline` (= SARSA, cách gốc) | $r + \gamma\, U^-(as'_{\text{chọn bằng ε-greedy}})$ | on-policy |
| `qlearning` | $r + \gamma \max_{a'} U^-(as'_{a'})$ | off-policy, học thẳng giá trị tối ưu (slide 2.8) |
| `double_q` | $r + \gamma\, U^-(as'_{a^*}),\ a^*=\arg\max_{a'} U_{online}(as'_{a'})$ | Double DQN đúng nghĩa |
| `expected_sarsa` | $r + \gamma[(1-\varepsilon)\max_{a'} U^- + \varepsilon\,\mathrm{mean}_{a'} U^-]$ | kỳ vọng theo π ε-greedy (slide 2.9) |

Mỗi cách chạy **2000 episode** và **1050 episode** (như report, decay 1200) → kiểm tra giả thuyết:
off-policy học được ngay khi ε còn lớn nên cần ít episode hơn. 8 cấu hình × 3 seed = **24 run**
(gắn output Nhóm 1 làm Input thì 3 run `baseline` được dùng lại → 21 run).

Q-learning / Double Q / Expected SARSA tính mạng trên **512×34 afterstate mỗi bước train** →
nặng hơn SARSA ~4–5 lần trên CPU, **đây là chỗ 2×T4 phát huy tác dụng** (benchmark đo bằng mode `qlearning`).""",
    },
}


def build(group):
    g = GROUPS[group]
    nb = nbf.v4.new_notebook()
    C = []
    md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip("\n")))
    code = lambda s: C.append(nbf.v4.new_code_cell(s.strip("\n")))

    md(f"""
# P-DDQN Tetris – {g['title']}

{g['intro']}

### Cách chạy trên Kaggle
1. **File → Import Notebook** → chọn file `.ipynb` này.
2. Panel bên phải **Settings → Accelerator = `GPU T4 x2`** (Internet không cần).
3. Bấm **Save Version → Save & Run All (Commit)** → chạy nền tối đa 12 giờ, có thể tắt trình duyệt.
4. Xong: vào trang version → tab **Output** → tải **`results_{group}.zip`**.

### Nếu chưa xong trong 12 giờ
Notebook tự dừng trước hạn (`TIME_BUDGET_HOURS` = 11.3 giờ), lưu các run đã xong và vẫn zip kết quả.
Để chạy tiếp: **Edit** notebook → **Add Input → Your Work → Notebooks** → chọn chính notebook này (output của version trước)
→ **Save & Run All** lần nữa. Các run đã xong được khôi phục và bỏ qua, chỉ chạy phần còn thiếu.

### Tận dụng phần cứng
* Code đã tối ưu (env tính mọi điểm đặt khối cùng lúc + cache, replay buffer numpy): **~2.5× nhanh hơn** bản gốc,
  kết quả env giống hệt bản gốc (đã kiểm tra 150 ván / 66k bước).
* Mạng chỉ 4→64→64→1 nên GPU không chắc nhanh hơn CPU → cell **Benchmark** đo thật trên máy Kaggle
  (CPU vs 2×T4, 4 hay 6 job song song) rồi tự chọn cấu hình nhanh nhất. Job được chia đều cho 2 GPU.
* Thứ tự chạy: **seed 0 của mọi cấu hình trước**, rồi seed 1, seed 2 → nếu hết giờ vẫn so sánh được mọi cấu hình.
""")

    md("## 1. Cấu hình")
    code(f"""
import time
T_START = time.time()          # Kaggle tính 12h từ lúc session bắt đầu

GROUP   = "{group}"
ONLY    = {g['only']!r}   # None = mọi cấu hình của GROUP
SEEDS   = [0, 1, 2]

EPISODES          = 2000   # pilot: 1050 ep (như report) chưa đủ để học; 2000 ep thì ổn định
DECAY_EPISODES    = 1200   # epsilon 1.0 -> 0.001 tuyến tính
MAX_EPISODE_STEPS = 1500   # trần số khối / episode khi TRAIN

GAMES     = 100            # eval theo Table 1: 100 ván
MAX_STEPS = 1000           # trần 1000 khối / ván
EVAL_SEED = 12345          # mọi cấu hình gặp cùng chuỗi khối gạch khi eval

DEVICE = "auto"            # "auto" (benchmark rồi chọn) | "cpu" | "cuda"
JOBS   = "auto"            # "auto" | số nguyên

TIME_BUDGET_HOURS = 11.3   # dừng train trước mốc này (giới hạn Kaggle 12h, chừa thời gian zip)
MIN_START_MINUTES = 30     # không bắt đầu run mới nếu còn ít hơn N phút
BENCH_MODE = "{g.get('bench_mode', 'sarsa')}"   # target mode dùng khi benchmark chọn CPU/GPU
""")

    md("## 2. Giải nén mã nguồn + chuẩn bị thư mục")
    code(f"""
import os, sys, io, json, base64, zipfile, shutil, subprocess, glob
from pathlib import Path

ON_KAGGLE = Path("/kaggle/working").is_dir()
WORK = Path("/kaggle/working") if ON_KAGGLE else Path.cwd() / "kaggle_out"
CODE = Path("/tmp/p_ddqn_code") if ON_KAGGLE else WORK / "_code"
RES  = WORK / f"results_{{GROUP}}"            # mọi kết quả nằm ở đây -> zip lại cuối cùng
CKPT, LOGS, REPORT = RES / "checkpoints", RES / "logs", RES / "reports"
for d in (CODE, CKPT, LOGS, REPORT):
    d.mkdir(parents=True, exist_ok=True)

CODE_ZIP_B64 = "{code_zip_b64()}"
with zipfile.ZipFile(io.BytesIO(base64.b64decode(CODE_ZIP_B64))) as z:
    z.extractall(CODE)
# Lưu kèm bản code vào kết quả để tái lập được
shutil.copytree(CODE, RES / "code_snapshot", dirs_exist_ok=True)

sys.path[:0] = [str(CODE), str(CODE / "tools")]
os.chdir(CODE)
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import reward_sweep as rs

CONFIGS = list(ONLY) if ONLY else [c for c in rs.CONFIGS if rs.CONFIGS[c][0] == GROUP]
RUNS = [rs.run_name(c, s) for s in SEEDS for c in CONFIGS]
print(f"{{len(CONFIGS)}} cấu hình × {{len(SEEDS)}} seed = {{len(RUNS)}} run")
print("Kết quả:", RES)
""")

    md("## 3. Phần cứng")
    code("""
import torch
N_CPU = os.cpu_count()
N_GPU = torch.cuda.device_count()
print(f"CPU: {N_CPU} lõi logic | GPU: {N_GPU}", [torch.cuda.get_device_name(i) for i in range(N_GPU)])
try:
    import psutil; vm = psutil.virtual_memory()
    print(f"RAM: {vm.available/2**30:.1f} / {vm.total/2**30:.1f} GB trống")
except ImportError:
    pass
print("torch", torch.__version__, "| numpy", np.__version__)
""")

    md("""
## 4. Khôi phục kết quả từ lần chạy trước (nếu có Input)

Tìm trong `/kaggle/input` các run đã xong (thư mục run có `run_meta.json`), kể cả trong file `results_*.zip`,
rồi chép vào thư mục kết quả → sweep sẽ bỏ qua các run này.
""")
    code("""
INPUT_ROOT = Path("/kaggle/input")

import tempfile

def expected_args(run):
    # Tham số train mà run này PHẢI có (theo cấu hình hiện tại + override của config)
    cfg = run.rsplit("_s", 1)[0]
    exp = {"episodes": EPISODES, "decay_episodes": DECAY_EPISODES, "max_episode_steps": MAX_EPISODE_STEPS}
    exp.update({k.replace("-", "_"): v for k, v in rs.CONFIGS[cfg][2].items()})
    return exp

def matches_settings(run_dir):
    # Chỉ dùng lại run cũ nếu cùng episode / decay / override và cùng số ván eval
    try:
        args = json.loads((run_dir / "run_config.json").read_text(encoding="utf-8"))["args"]
        bad = {k: (args.get(k), v) for k, v in expected_args(run_dir.name).items()
               if str(args.get(k)) != str(v) and not (isinstance(v, (int, float)) and args.get(k) == v)}
        ev = run_dir / "eval.json"
        if ev.exists():
            games = {r.get("games") for r in json.loads(ev.read_text(encoding="utf-8")).values()}
            if games != {GAMES}:
                bad["games"] = (games, GAMES)
        if bad:
            print(f"  bỏ qua {run_dir.name}: khác cấu hình {bad}")
        return not bad
    except Exception as e:
        print(f"  bỏ qua {run_dir.name}: {e}")
        return False

def restore_previous():
    roots = [INPUT_ROOT]
    tmp = Path(tempfile.mkdtemp(prefix="prev_results_")); restored = []
    for root in roots:
        if not root.exists():
            continue
        for i, zp in enumerate(root.rglob("results_*.zip")):   # output cũ dạng zip
            with zipfile.ZipFile(zp) as z:
                z.extractall(tmp / f"{i}_{zp.stem}")
        for base in (root, tmp):
            for meta in base.rglob("run_meta.json"):
                run_dir = meta.parent
                if run_dir.name not in RUNS or (CKPT / run_dir.name / "run_meta.json").exists():
                    continue
                if not matches_settings(run_dir):
                    continue
                shutil.copytree(run_dir, CKPT / run_dir.name, dirs_exist_ok=True)
                restored.append(run_dir.name)
    return sorted(set(restored))

restored = restore_previous()
print(f"Khôi phục {len(restored)} run:", restored)

def progress():
    rows = []
    for r in RUNS:
        d = CKPT / r
        st = ("✅ xong" if (d / "eval.json").exists() else
              "train xong, chờ eval" if (d / "run_meta.json").exists() else
              "dở (sẽ train lại)" if d.exists() else "chưa chạy")
        rows.append({"run": r, "trạng thái": st})
    df = pd.DataFrame(rows).set_index("run")
    print(df["trạng thái"].value_counts().to_string())
    return df

progress_df = progress()
REMAINING = int((progress_df["trạng thái"] != "✅ xong").sum())
""")

    md("""
## 5. Benchmark: chọn CPU hay GPU, bao nhiêu job song song

Chạy đồng thời K process đo tốc độ vòng train thật (env → chọn khối → train_step batch 512) trong ~25 giây,
cộng tổng số bước/giây của cả máy. Chọn phương án nhanh nhất.
""")
    code("""
def bench(device, jobs, seconds=25):
    env = dict(os.environ, OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    procs = []
    for i in range(jobs):
        e = dict(env, CUDA_VISIBLE_DEVICES=str(i % max(N_GPU, 1)) if device == "cuda" else "")
        procs.append(subprocess.Popen([sys.executable, "tools/bench_throughput.py", "--device", device,
                                       "--seconds", str(seconds), "--target-mode", BENCH_MODE], stdout=subprocess.PIPE, text=True, env=e))
    total = 0.0
    for p in procs:
        out, _ = p.communicate()
        try:
            total += json.loads(out.strip().splitlines()[-1])["steps_per_sec"]
        except Exception:
            print("bench lỗi:", out[-300:])
    return total

if DEVICE == "auto" or JOBS == "auto":
    cands = [("cpu", N_CPU)]
    if N_GPU:
        cands += [("cuda", N_CPU), ("cuda", N_CPU + 2)]
    if DEVICE != "auto":
        cands = [c for c in cands if c[0] == DEVICE] or [(DEVICE, N_CPU)]
    if JOBS != "auto":
        cands = sorted({(d, int(JOBS)) for d, _ in cands})
    bench_res = []
    for d, j in cands:
        sps = bench(d, j)
        bench_res.append({"device": d, "jobs": j, "tổng bước/giây": round(sps), "bước/giây/job": round(sps / j)})
        print(bench_res[-1], flush=True)
    best = max(bench_res, key=lambda r: r["tổng bước/giây"])
    DEVICE_USED, JOBS_USED, THROUGHPUT = best["device"], best["jobs"], best["tổng bước/giây"]
    display(pd.DataFrame(bench_res))
else:
    DEVICE_USED, JOBS_USED = DEVICE, int(JOBS)
    THROUGHPUT = bench(DEVICE_USED, JOBS_USED)

# Ước tính: 1 run ≈ 650k bước train (đa số ở cuối khi agent sống tới trần 1500 khối) + eval
STEPS_PER_RUN = 650_000
est_h = REMAINING * STEPS_PER_RUN / THROUGHPUT / 3600 * 1.1
left_h = TIME_BUDGET_HOURS - (time.time() - T_START) / 3600
print(f"\\n➡ Chọn device={DEVICE_USED}, jobs={JOBS_USED} | {REMAINING} run còn lại | ước tính ~{est_h:.1f} giờ "
      f"(còn {left_h:.1f} giờ trong ngân sách)")
if est_h > left_h:
    print("⚠ Có thể không xong trong 1 session: notebook sẽ dừng an toàn, zip kết quả; "
          "chạy thêm 1 version (gắn output cũ làm Input) để hoàn tất.")
""")

    md("""
## 6. Chạy sweep

Mỗi run: train (`src/train.py`) → eval `best_model.pth` + `latest_model.pth` (100 ván, trần 1000 khối).
Log từng run ở `results_*/checkpoints/<run>/train.log`. Cell luôn kết thúc bình thường (kể cả khi lỗi / hết giờ)
để các cell sau vẫn xuất bảng và zip.
""")
    code("""
stop_at = T_START + TIME_BUDGET_HOURS * 3600
cmd = [sys.executable, "-u", "tools/reward_sweep.py",
       "--seeds", *map(str, SEEDS), "--jobs", str(JOBS_USED),
       "--device", DEVICE_USED, "--gpus", str(max(N_GPU, 1)),
       "--episodes", str(EPISODES), "--decay-episodes", str(DECAY_EPISODES),
       "--max-episode-steps", str(MAX_EPISODE_STEPS),
       "--games", str(GAMES), "--max-steps", str(MAX_STEPS), "--eval-seed", str(EVAL_SEED),
       "--checkpoint-dir", str(CKPT), "--log-dir", str(LOGS), "--output-dir", str(REPORT),
       "--stop-at", str(stop_at), "--min-start-minutes", str(MIN_START_MINUTES)]
cmd += ["--only", *ONLY] if ONLY else ["--group", GROUP]
print(" ".join(cmd), "\\n", flush=True)

t0 = time.time()
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                        env=dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8"),
                        start_new_session=True)
try:
    for line in proc.stdout:
        print(time.strftime("[%H:%M:%S] "), line, end="", flush=True)
    proc.wait()
except KeyboardInterrupt:
    print("\\n⛔ Dừng sweep (các run đã xong vẫn được giữ)...")
    try:
        import signal; os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        proc.kill()
except Exception as e:
    print("Lỗi khi chạy sweep:", e)
print(f"\\nExit code: {proc.returncode} | {(time.time() - t0) / 3600:.2f} giờ")
progress_df = progress()
""")

    md("## 7. Bảng kết quả (metric Table 1, trung bình qua các seed)")
    code("""
CHECKPOINT = "latest"   # "latest" (model cuối) hoặc "best" (episode train nhiều hàng nhất)

results = []
p = REPORT / "sweep_results.json"
if p.exists():
    results = [r for r in json.loads(p.read_text(encoding="utf-8")) if r["config"] in CONFIGS]

def summary_table(results, which):
    by_cfg = {}
    for r in results:
        by_cfg.setdefault(r["config"], []).append(r)
    base = rs.aggregate(by_cfg.get("baseline", []), which)
    rows = []
    for c in CONFIGS:
        a = rs.aggregate(by_cfg.get(c, []), which) if c in by_cfg else None
        if a is None:
            continue
        secs = [r["train_seconds"] for r in by_cfg[c] if r.get("train_seconds")]
        rows.append({
            "config": c, "thay đổi": rs.CONFIGS[c][1], "seeds": a["n_seeds"],
            "Lines mean": round(a["mean_lines"], 1), "±std (ván)": round(a["std_lines"], 1),
            "±seed": round(a["seed_std_mean_lines"], 1),
            "Median": round(a["median_lines"], 1), "Max": int(a["max_lines"]),
            "Mean Score": round(a["mean_score"], 1), "Placements": round(a["mean_placements"], 1),
            "Pts/Line": round(a["points_per_line"], 1), "Cap hits": f"{a['cap_hits']:.1f}/{a['games']}",
            "Δ Lines vs baseline": (round(a["mean_lines"] - base["mean_lines"], 1)
                                    if base and c != "baseline" else None),
            "Train (phút)": round(np.mean(secs) / 60, 1) if secs else None,
        })
    return pd.DataFrame(rows).set_index("config") if rows else pd.DataFrame()

tables = {w: summary_table(results, w) for w in ("latest", "best")}
table = tables[CHECKPOINT]
print(f"{len(results)} run có kết quả | checkpoint: {CHECKPOINT}_model.pth")
if not table.empty:
    display(table.sort_values("Lines mean", ascending=False)
                 .style.background_gradient(subset=["Lines mean", "Mean Score", "Pts/Line"], cmap="Greens")
                 .format(precision=1, na_rep="—"))
""")
    code("""
# Kết quả từng seed (Mean Lines) – để thấy độ dao động giữa các lần train
per_seed = pd.DataFrame([
    {"config": r["config"], "seed": r["seed"],
     **{k: r["eval"][CHECKPOINT][k] for k in ("mean_lines", "mean_score", "points_per_line", "cap_hits")}}
    for r in results if CHECKPOINT in r["eval"]
])
if not per_seed.empty:
    display(per_seed.pivot_table(index="config", columns="seed", values="mean_lines").round(1))
""")

    md("## 8. Biểu đồ")
    code("""
if not table.empty:
    t = table.sort_values("Lines mean")
    colors = ["#94a3b8" if c == "baseline" else "#0ea5e9" for c in t.index]
    fig, axes = plt.subplots(1, 3, figsize=(18, max(4, 0.45 * len(t) + 1.5)))
    axes[0].barh(t.index, t["Lines mean"], xerr=t["±seed"], color=colors, capsize=3)
    if "baseline" in t.index:
        axes[0].axvline(t.loc["baseline", "Lines mean"], ls="--", c="#64748b", lw=1, label="baseline")
        axes[0].legend(loc="lower right")
    axes[0].set_title("Mean Lines (thanh lỗi = độ lệch giữa seed)")
    axes[1].barh(t.index, t["Mean Score"], color=colors); axes[1].set_title("Mean Score")
    axes[2].barh(t.index, t["Pts/Line"], color=colors); axes[2].set_title("Points / Line (combo)")
    for ax in axes:
        ax.grid(axis="x", ls=":", alpha=0.6)
    plt.suptitle(f"{GROUP} – checkpoint {CHECKPOINT}")
    plt.tight_layout()
    plt.savefig(REPORT / f"comparison_{CHECKPOINT}.png", dpi=150)
    plt.show()

if not per_seed.empty:
    order = table.sort_values("Lines mean").index.tolist()
    data = [per_seed.loc[per_seed.config == c, "mean_lines"].values for c in order]
    fig, ax = plt.subplots(figsize=(10, max(4, 0.45 * len(order) + 1.5)))
    try:
        ax.boxplot(data, vert=False, tick_labels=order)
    except TypeError:                       # matplotlib < 3.9
        ax.boxplot(data, vert=False, labels=order)
    for i, d in enumerate(data, start=1):
        ax.scatter(d, [i] * len(d), c="#0ea5e9", zorder=3, s=18)
    ax.set_title("Mean Lines của từng seed (mỗi chấm = 1 lần train)")
    ax.grid(axis="x", ls=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(REPORT / f"per_seed_{CHECKPOINT}.png", dpi=150)
    plt.show()
""")

    if group == "target":
        md("""
## 8b. Tốc độ học: đường cong Avg50 và episode đầu tiên đạt Avg50 ≥ 100

Đọc `train.log` của từng run (log mỗi 10 episode). Giả thuyết cần kiểm tra: Q-learning / Double Q / Expected SARSA
đạt ngưỡng **sớm hơn** SARSA vì giá trị bootstrap không bị kéo xuống bởi các nước đi ngẫu nhiên khi ε còn lớn.
""")
        code(r"""
import re
THRESH = 100

def read_curve(run):
    f = CKPT / run / "train.log"
    pts = []
    if f.exists():
        for l in open(f, encoding="utf-8", errors="ignore"):
            m = re.match(r"Ep\s+(\d+)/\d+.*Avg50:\s*([\d.]+)", l)
            if m:
                pts.append((int(m[1]), float(m[2])))
    return pts

curves, speed_rows = {}, []
for c in CONFIGS:
    for s in SEEDS:
        r = rs.run_name(c, s)
        pts = read_curve(r)
        if not pts or not (CKPT / r / "run_meta.json").exists():
            continue
        curves.setdefault(c, []).append(dict(pts))
        first = next((ep for ep, v in pts if v >= THRESH), None)
        speed_rows.append({"config": c, "seed": s, f"ep đầu tiên Avg50≥{THRESH}": first,
                           "Avg50 cuối": pts[-1][1], "max Avg50": max(v for _, v in pts)})
speed_df = pd.DataFrame(speed_rows)
if not speed_df.empty:
    col = f"ep đầu tiên Avg50≥{THRESH}"
    agg = speed_df.groupby("config").agg(
        **{"seed đạt ngưỡng": (col, lambda x: f"{x.notna().sum()}/{len(x)}"),
           col + " (mean)": (col, "mean"),
           "Avg50 cuối (mean)": ("Avg50 cuối", "mean"),
           "max Avg50 (mean)": ("max Avg50", "mean")}).reindex([c for c in CONFIGS if c in curves])
    display(agg.round(1))
    display(speed_df.pivot_table(index="config", columns="seed", values=col))

if curves:
    fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)
    for c, runs in curves.items():
        ax = axes[1] if c.endswith("_1050") else axes[0]
        eps_ = sorted(set().union(*runs))
        mean = [np.mean([r[e] for r in runs if e in r]) for e in eps_]
        ax.plot(eps_, mean, label=f"{c} ({len(runs)} seed)", lw=2 if c in ("baseline", "sarsa_1050") else 1.5,
                ls="--" if c in ("baseline", "sarsa_1050") else "-")
    for ax, t in zip(axes, ("2000 episode", "1050 episode (như report)")):
        ax.axhline(THRESH, c="#94a3b8", lw=1, ls=":")
        ax.set_title(f"Avg50 lines khi train – {t} (trung bình các seed)")
        ax.set_xlabel("episode"); ax.grid(ls=":", alpha=0.6)
        if ax.get_lines():
            ax.legend()
    axes[0].set_ylabel("Avg50 lines")
    plt.tight_layout()
    plt.savefig(REPORT / "learning_curves.png", dpi=150)
    plt.show()
""")

    md("## 9. Xuất bảng + zip toàn bộ kết quả")
    code("""
for which, tb in tables.items():
    if tb.empty:
        continue
    tb.to_csv(REPORT / f"summary_{which}.csv", encoding="utf-8-sig")      # mở bằng Excel không lỗi font
    try:
        (REPORT / f"summary_{which}.md").write_text(tb.to_markdown(), encoding="utf-8")
    except ImportError:
        pass
if not per_seed.empty:
    per_seed.to_csv(REPORT / f"per_seed_{CHECKPOINT}.csv", index=False, encoding="utf-8-sig")
progress_df.to_csv(REPORT / "progress.csv", encoding="utf-8-sig")
if "speed_df" in globals() and not speed_df.empty:
    speed_df.to_csv(REPORT / "learning_speed_per_seed.csv", index=False, encoding="utf-8-sig")
(REPORT / "session_info.json").write_text(json.dumps({
    "group": GROUP, "configs": CONFIGS, "seeds": SEEDS, "episodes": EPISODES,
    "decay_episodes": DECAY_EPISODES, "max_episode_steps": MAX_EPISODE_STEPS,
    "games": GAMES, "max_steps": MAX_STEPS, "eval_seed": EVAL_SEED,
    "device": DEVICE_USED, "jobs": JOBS_USED, "restored_runs": restored,
    "session_hours": (time.time() - T_START) / 3600,
}, indent=2, ensure_ascii=False), encoding="utf-8")

zip_base = WORK / f"results_{GROUP}"
zip_path = shutil.make_archive(str(zip_base), "zip", root_dir=WORK, base_dir=RES.name)
print(f"✅ Đã zip: {zip_path} ({os.path.getsize(zip_path) / 2**20:.1f} MB)")
print(progress_df["trạng thái"].value_counts().to_string())
if ON_KAGGLE:
    from IPython.display import FileLink
    os.chdir(WORK)
    display(FileLink(Path(zip_path).name))
""")

    nb.cells = C
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    out = os.path.join(ROOT, "notebooks", g["file"])
    nbf.write(nb, out)
    print("written", out, f"({os.path.getsize(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    for grp in (sys.argv[1:] or GROUPS):
        build(grp)
