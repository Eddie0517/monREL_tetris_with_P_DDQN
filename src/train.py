import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Suppress TF and oneDNN warning noise
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Reconfigure UTF-8 for Windows console
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import json
import time
import numpy as np
import torch

from src.env.tetris_env import TetrisEnv, DEFAULT_REWARD_WEIGHTS
from src.agents.dqn_agent import DQNAgent


def build_reward_weights(args):
    """Gom các trọng số reward từ CLI thành dict truyền vào TetrisEnv."""
    return {
        "alive": args.r_alive,
        "lines": args.r_lines,
        "holes": args.r_holes,
        "bumpiness": args.r_bumpiness,
        "height": args.r_height,
        "game_over_penalty": args.r_game_over,
    }


def train(args):
    # Mỗi run có thư mục checkpoint/log riêng để dễ so sánh các cấu hình reward
    if args.run_name:
        args.checkpoint_dir = os.path.join(args.checkpoint_dir, args.run_name)
        args.log_dir = os.path.join(args.log_dir, args.run_name)

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    if args.seed is not None:
        import random
        random.seed(args.seed)
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)

    # Lazy-load SummaryWriter to avoid startup delay if not needed
    writer = None
    if not args.no_tensorboard:
        try:
            from torch.utils.tensorboard import SummaryWriter
            writer = SummaryWriter(log_dir=args.log_dir)
            print(f"TensorBoard logging enabled: {args.log_dir}", flush=True)
        except Exception as e:
            print(f"TensorBoard could not be initialized ({e}), continuing without it.", flush=True)

    reward_weights = build_reward_weights(args)
    env = TetrisEnv(reward_weights=reward_weights)

    # Lưu lại cấu hình của run để đối chiếu sau này
    config_path = os.path.join(args.checkpoint_dir, "run_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"reward_weights": reward_weights, "args": vars(args)}, f, indent=2, ensure_ascii=False)

    agent = DQNAgent(
        state_dim=4,
        hidden_dim=args.hidden_dim,
        lr=args.lr,
        gamma=args.gamma,
        memory_size=args.memory_size,
        device=args.device,
        target_mode=args.target_mode,
    )

    start_episode = 1
    best_lines = 17 if os.path.exists(os.path.join(args.checkpoint_dir, "best_model.pth")) else 0

    if args.resume and os.path.exists(args.resume):
        print(f"Loading checkpoint from {args.resume}...", flush=True)
        agent.load(args.resume)
        print("Checkpoint loaded successfully!", flush=True)

    print("=" * 65, flush=True)
    print(">>> STARTING TETRIS DEEP Q-NETWORK TRAINING", flush=True)
    print(f"Device: {agent.device} | Total Episodes: {args.episodes}", flush=True)
    print(f"Batch Size: {args.batch_size} | LR: {args.lr} | Gamma: {args.gamma} | Target: {args.target_mode}", flush=True)
    print(f"Checkpoints: {args.checkpoint_dir} | Logs: {args.log_dir}", flush=True)
    print(f"Reward weights: {reward_weights}", flush=True)
    print("=" * 65, flush=True)

    if writer is not None:
        writer.add_text("Config/Reward_Weights", json.dumps(reward_weights), 0)

    recent_lines = []
    recent_rewards = []
    recent_scores = []
    start_time = time.time()

    for episode in range(start_episode, args.episodes + 1):
        env.reset()
        episode_reward = 0.0
        episode_losses = []
        steps = 0

        # Epsilon decay
        epsilon = max(
            args.min_epsilon,
            args.initial_epsilon - (episode / args.decay_episodes) * (args.initial_epsilon - args.min_epsilon),
        )

        # Get initial candidate placements
        next_states = env.get_next_states()
        if not next_states:
            continue

        action, current_state = agent.act(next_states, epsilon=epsilon)

        while not env.game_over:
            _, reward, done, info = env.step(action)
            episode_reward += reward
            steps += 1

            if not done:
                next_states = env.get_next_states()
                if next_states:
                    next_action, next_state = agent.act(next_states, epsilon=epsilon)
                    if agent.needs_candidates:
                        # Q-learning / Double Q / Expected SARSA cần MỌI afterstate của khối kế tiếp
                        cands = np.stack([f for f, _ in next_states.values()])
                        chosen = list(next_states).index(next_action)
                        agent.remember(current_state, reward, next_state, False, cands, chosen)
                    else:
                        agent.remember(current_state, reward, next_state, False)
                    action = next_action
                    current_state = next_state
                else:
                    agent.remember(current_state, reward, np.zeros(4, dtype=np.float32), True)
                    break
            else:
                agent.remember(current_state, reward, np.zeros(4, dtype=np.float32), True)
                break

            # Mini-batch gradient step
            loss = agent.train_step(batch_size=args.batch_size, epsilon=epsilon)
            if loss is not None:
                episode_losses.append(loss)

            # Cắt episode quá dài (truncation, không phải thua -> không lưu transition terminal)
            if args.max_episode_steps and steps >= args.max_episode_steps:
                break

        # Periodic target network sync
        if episode % args.target_update_freq == 0:
            agent.update_target_network()

        # Track history
        recent_lines.append(env.cleared_lines)
        recent_rewards.append(episode_reward)
        recent_scores.append(env.score)
        if len(recent_lines) > 50:
            recent_lines.pop(0)
            recent_rewards.pop(0)
            recent_scores.pop(0)

        avg_lines = float(np.mean(recent_lines))
        avg_reward = float(np.mean(recent_rewards))
        avg_loss = float(np.mean(episode_losses)) if episode_losses else 0.0

        # TensorBoard Logging
        if writer is not None:
            writer.add_scalar("Train/Episode_Reward", episode_reward, episode)
            writer.add_scalar("Train/Cleared_Lines", env.cleared_lines, episode)
            writer.add_scalar("Train/Score", env.score, episode)
            writer.add_scalar("Train/Steps", steps, episode)
            writer.add_scalar("Train/Epsilon", epsilon, episode)
            writer.add_scalar("Train/Loss", avg_loss, episode)
            writer.add_scalar("Stats/Avg50_Lines", avg_lines, episode)
            writer.add_scalar("Stats/Avg50_Reward", avg_reward, episode)

        # Save Best Model
        if env.cleared_lines > best_lines:
            best_lines = env.cleared_lines
            best_path = os.path.join(args.checkpoint_dir, "best_model.pth")
            agent.save(best_path)
            print(f">>> [NEW RECORD] Episode {episode}: Cleared {best_lines} lines! Saved to {best_path}", flush=True)

        # Regular logging
        if episode % args.log_freq == 0 or episode == 1:
            elapsed = time.time() - start_time
            print(
                f"Ep {episode:4d}/{args.episodes} | "
                f"Lines: {env.cleared_lines:4d} (Avg50: {avg_lines:5.1f}) | "
                f"Score: {env.score:6d} | "
                f"Steps: {steps:4d} | "
                f"Reward: {episode_reward:7.1f} | "
                f"Loss: {avg_loss:.4f} | "
                f"Eps: {epsilon:.3f} | "
                f"Time: {elapsed:5.1f}s",
                flush=True,
            )

        # Periodic checkpoint
        if episode % args.save_freq == 0:
            ckpt_path = os.path.join(args.checkpoint_dir, f"dqn_ep{episode}.pth")
            agent.save(ckpt_path)

        # Always save latest
        agent.save(os.path.join(args.checkpoint_dir, "latest_model.pth"))

    if writer is not None:
        writer.close()

    print("=" * 65, flush=True)
    print("SUCCESS: TRAINING FINISHED!", flush=True)
    print(f"Best Lines Achieved: {best_lines}", flush=True)
    print(f"Latest checkpoint saved at: {os.path.join(args.checkpoint_dir, 'latest_model.pth')}", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Double DQN on Cyber Tetris")
    parser.add_argument("--episodes", type=int, default=2000, help="Total number of episodes")
    parser.add_argument("--batch-size", type=int, default=512, help="Mini-batch size")
    parser.add_argument("--hidden-dim", type=int, default=64, help="Hidden dimension for MLP")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    parser.add_argument("--memory-size", type=int, default=30000, help="Replay buffer capacity")
    parser.add_argument("--initial-epsilon", type=float, default=1.0, help="Starting epsilon")
    parser.add_argument("--min-epsilon", type=float, default=0.001, help="Minimum epsilon")
    parser.add_argument("--decay-episodes", type=int, default=1200, help="Episodes to decay epsilon")
    parser.add_argument("--target-update-freq", type=int, default=10, help="Target net update frequency in episodes")
    parser.add_argument("--log-freq", type=int, default=10, help="Console log frequency")
    parser.add_argument("--save-freq", type=int, default=200, help="Checkpoint save frequency")
    parser.add_argument("--checkpoint-dir", type=str, default="checkpoints", help="Path to save models")
    parser.add_argument("--log-dir", type=str, default="logs", help="Path for TensorBoard logs")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda or cpu)")
    parser.add_argument("--target-mode", default="sarsa",
                        choices=["sarsa", "qlearning", "double_q", "expected_sarsa"],
                        help="Cách tính target TD: sarsa (gốc) | qlearning | double_q | expected_sarsa")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint to resume")
    parser.add_argument("--no-tensorboard", action="store_true", help="Disable TensorBoard logging")
    parser.add_argument("--seed", type=int, default=None, help="Seed cho random/numpy/torch (để so sánh công bằng)")
    parser.add_argument("--max-episode-steps", type=int, default=None,
                        help="Giới hạn số khối mỗi episode khi train (mặc định: không giới hạn)")
    parser.add_argument("--run-name", type=str, default=None,
                        help="Tên run; checkpoint/log sẽ lưu vào <checkpoint-dir>/<run-name> và <log-dir>/<run-name>")

    # Reward weights: R = alive + lines*L^2 - holes*dHoles - bumpiness*dBump - height*dHeight
    rw = parser.add_argument_group("Reward weights")
    rw.add_argument("--r-alive", type=float, default=DEFAULT_REWARD_WEIGHTS["alive"], help="Thưởng sống sót mỗi bước")
    rw.add_argument("--r-lines", type=float, default=DEFAULT_REWARD_WEIGHTS["lines"], help="Hệ số thưởng cho Lines^2")
    rw.add_argument("--r-holes", type=float, default=DEFAULT_REWARD_WEIGHTS["holes"], help="Hệ số phạt delta Holes")
    rw.add_argument("--r-bumpiness", type=float, default=DEFAULT_REWARD_WEIGHTS["bumpiness"], help="Hệ số phạt delta Bumpiness")
    rw.add_argument("--r-height", type=float, default=DEFAULT_REWARD_WEIGHTS["height"], help="Hệ số phạt delta AggHeight")
    rw.add_argument("--r-game-over", type=float, default=DEFAULT_REWARD_WEIGHTS["game_over_penalty"], help="Mức phạt khi thua")

    args = parser.parse_args()
    train(args)
