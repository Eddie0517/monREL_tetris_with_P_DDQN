"""
Đo tốc độ vòng train (bước/giây) của 1 process: env -> act -> remember -> train_step.
Notebook Kaggle chạy song song nhiều bản để chọn cấu hình nhanh nhất (CPU hay GPU, bao nhiêu job).

  python tools/bench_throughput.py --device cuda --seconds 30
In ra 1 dòng JSON: {"device": ..., "steps": ..., "seconds": ..., "steps_per_sec": ...}
"""
import argparse
import json
import os
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import torch

from src.env.tetris_env import TetrisEnv
from src.agents.dqn_agent import DQNAgent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cpu")
    p.add_argument("--seconds", type=float, default=30)
    p.add_argument("--batch-size", type=int, default=512)
    p.add_argument("--target-mode", default="sarsa")
    args = p.parse_args()

    np.random.seed(0)
    torch.manual_seed(0)
    env = TetrisEnv()
    agent = DQNAgent(state_dim=4, device=args.device, target_mode=args.target_mode)
    # Buffer đầy sẵn để train_step chạy đúng kích thước batch như lúc train thật
    for _ in range(agent.memory.capacity):
        s = np.random.rand(4).astype(np.float32) * 50
        agent.remember(s, 1.0, s, False, np.repeat(s[None], 20, axis=0) if agent.needs_candidates else None)

    def run(seconds):
        steps, t0 = 0, time.time()
        env.reset()
        action, state = agent.act(env.get_next_states(), epsilon=0.0)
        while time.time() - t0 < seconds:
            _, reward, done, _ = env.step(action)
            ns = env.get_next_states() if not done else None
            if not ns:
                env.reset()
                ns = env.get_next_states()
            action, nxt = agent.act(ns, epsilon=0.0)
            if agent.needs_candidates:
                agent.remember(state, reward, nxt, False, np.stack([f for f, _ in ns.values()]),
                               list(ns).index(action))
            else:
                agent.remember(state, reward, nxt, False)
            agent.train_step(args.batch_size, epsilon=0.1)
            state = nxt
            steps += 1
        return steps, time.time() - t0

    run(min(3.0, args.seconds / 5))  # khởi động (CUDA context, cache)
    steps, secs = run(args.seconds)
    print(json.dumps({"device": args.device, "target_mode": args.target_mode, "steps": steps, "seconds": secs,
                      "steps_per_sec": steps / secs}), flush=True)


if __name__ == "__main__":
    main()
