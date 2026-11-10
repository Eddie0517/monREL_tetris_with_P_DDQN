import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from src.models.dqn_model import DQN


class ReplayBuffer:
    """
    Replay buffer dạng mảng numpy vòng (thay cho deque + random.sample, nhanh hơn ~10 lần).
    Ngữ nghĩa giữ nguyên: dung lượng cố định, bỏ mẫu cũ nhất khi đầy,
    lấy mẫu đều KHÔNG lặp lại trong một batch.
    """

    def __init__(self, capacity, state_dim, max_candidates=0):
        self.capacity = capacity
        self.max_candidates = max_candidates
        self.states = np.zeros((capacity, state_dim), dtype=np.float32)
        self.next_states = np.zeros((capacity, state_dim), dtype=np.float32)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.dones = np.zeros(capacity, dtype=np.float32)
        if max_candidates:
            # Mọi afterstate của khối kế tiếp (đệm tới max_candidates) cho Q-learning / Expected SARSA
            self.next_cands = np.zeros((capacity, max_candidates, state_dim), dtype=np.float32)
            self.next_mask = np.zeros((capacity, max_candidates), dtype=bool)
            self.chosen = np.zeros(capacity, dtype=np.int64)
        self.pos = 0
        self.size = 0
        # Seed lấy từ np.random (train.py đã seed) -> chạy lại cùng seed cho cùng kết quả
        self.rng = np.random.default_rng(np.random.randint(0, 2**31 - 1))

    def append(self, transition, next_candidates=None, chosen_idx=0):
        state, reward, next_state, done = transition
        i = self.pos
        if self.max_candidates:
            n = 0 if next_candidates is None else len(next_candidates)
            self.next_mask[i] = False
            if n:
                self.next_cands[i, :n] = next_candidates
                self.next_mask[i, :n] = True
            self.chosen[i] = chosen_idx
        self.states[i] = state
        self.rewards[i] = reward
        self.next_states[i] = next_state
        self.dones[i] = float(done)
        self.pos = (i + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def __len__(self):
        return self.size

    def sample(self, batch_size):
        idx = self.rng.choice(self.size, batch_size, replace=False, shuffle=False)
        batch = (self.states[idx], self.rewards[idx], self.next_states[idx], self.dones[idx])
        if self.max_candidates:
            batch += (self.next_cands[idx], self.next_mask[idx], self.chosen[idx])
        return batch


# Cách tính giá trị bootstrap của trạng thái kế tiếp (xem doc/2.8 Q-learning, doc/2.9 Expected Sarsa):
#   sarsa          : U⁻(afterstate kế tiếp ĐÃ CHỌN bằng ε-greedy)          -> on-policy (cách gốc của project)
#   qlearning      : max_a' U⁻(afterstate a')                              -> off-policy, học thẳng giá trị tối ưu
#   double_q       : U⁻(afterstate argmax_a' U_online)                     -> Double DQN đúng nghĩa
#   expected_sarsa : (1-ε)·max_a' U⁻ + ε·mean_a' U⁻                        -> kỳ vọng theo chính sách ε-greedy
TARGET_MODES = ("sarsa", "qlearning", "double_q", "expected_sarsa")
MAX_CANDIDATES = 34  # T/J/L: 4 hướng xoay -> 8+9+8+9 = 34 vị trí đặt


class DQNAgent:
    """
    Double Deep Q-Network (DDQN) Agent for Placement-based Tetris.
    Includes Experience Replay Memory, Target Network, and Huber Loss.
    """

    def __init__(
        self,
        state_dim=4,
        hidden_dim=64,
        lr=1e-3,
        gamma=0.99,
        memory_size=30000,
        device=None,
        target_mode="sarsa",
    ):
        if target_mode not in TARGET_MODES:
            raise ValueError(f"target_mode phải thuộc {TARGET_MODES}")
        self.state_dim = state_dim
        self.gamma = gamma
        self.target_mode = target_mode
        self.needs_candidates = target_mode != "sarsa"
        self.memory = ReplayBuffer(memory_size, state_dim,
                                   max_candidates=MAX_CANDIDATES if self.needs_candidates else 0)

        # For small 4-feature MLP, CPU is often significantly faster due to zero GPU launch overhead
        if device is None:
            self.device = torch.device("cpu")
        else:
            self.device = torch.device(device)

        # Online Network (policy) and Target Network (evaluation stability)
        self.online_net = DQN(input_dim=state_dim, hidden_dim=hidden_dim).to(self.device)
        self.target_net = DQN(input_dim=state_dim, hidden_dim=hidden_dim).to(self.device)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.online_net.parameters(), lr=lr)
        self.criterion = nn.SmoothL1Loss()  # Huber Loss for stable gradients

    def act(self, next_states, epsilon=0.0):
        """
        Chooses the best action given candidate next states {action: (features, board)}.
        Exploration via epsilon-greedy.
        Returns:
            (best_action, best_features)
        """
        if not next_states:
            return None, None

        actions = list(next_states.keys())
        features_list = [next_states[a][0] for a in actions]

        # Exploration: pick uniform random candidate
        if random.random() < epsilon:
            idx = random.randrange(len(actions))
            return actions[idx], features_list[idx]

        # Exploitation: evaluate Q(s') for all candidate placements
        features_tensor = torch.tensor(
            np.array(features_list), dtype=torch.float32, device=self.device
        )
        self.online_net.eval()
        with torch.no_grad():
            q_values = self.online_net(features_tensor)[:, 0]
            best_idx = torch.argmax(q_values).item()

        return actions[best_idx], features_list[best_idx]

    def remember(self, state, reward, next_state, done, next_candidates=None, chosen_idx=0):
        """Stores transition in replay buffer.
        next_candidates: mảng (n, 4) mọi afterstate của khối kế tiếp (chỉ cần khi target_mode != sarsa)."""
        self.memory.append((state, reward, next_state, done), next_candidates, chosen_idx)

    def train_step(self, batch_size=512, epsilon=0.0):
        """
        Samples a mini-batch from replay buffer and updates online network weights.
        Returns:
            loss (float) or None if insufficient samples
        """
        if len(self.memory) < batch_size:
            return None

        batch = self.memory.sample(batch_size)
        states, rewards, next_states, dones = batch[:4]

        states_t = torch.from_numpy(states).to(self.device)
        rewards_t = torch.from_numpy(rewards).to(self.device).unsqueeze(1)
        next_states_t = torch.from_numpy(next_states).to(self.device)
        dones_t = torch.from_numpy(dones).to(self.device).unsqueeze(1)

        # Target Q calculation with Double DQN / Target Network
        with torch.no_grad():
            if self.target_mode == "sarsa":
                next_q = self.target_net(next_states_t)
            else:
                next_q = self._bootstrap(batch[4], batch[5], epsilon)
            target_q = rewards_t + (1.0 - dones_t) * self.gamma * next_q

        # Current Q predictions
        self.online_net.train()
        pred_q = self.online_net(states_t)

        loss = self.criterion(pred_q, target_q)

        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping to prevent instability
        nn.utils.clip_grad_norm_(self.online_net.parameters(), max_norm=1.0)
        self.optimizer.step()

        return loss.item()

    def _bootstrap(self, cands, mask, epsilon):
        """Giá trị bootstrap từ MỌI afterstate kế tiếp (Q-learning / Double Q / Expected SARSA)."""
        b, k, d = cands.shape
        cands_t = torch.from_numpy(cands).to(self.device).view(b * k, d)
        mask_t = torch.from_numpy(mask).to(self.device)
        has_next = mask_t.any(dim=1, keepdim=True)  # transition kết thúc ván không có afterstate kế tiếp
        neg_inf = torch.tensor(float("-inf"), device=self.device)

        u_target = self.target_net(cands_t).view(b, k)
        u_target_masked = torch.where(mask_t, u_target, neg_inf)

        if self.target_mode == "qlearning":
            boot = u_target_masked.max(dim=1, keepdim=True).values
        elif self.target_mode == "double_q":
            u_online = torch.where(mask_t, self.online_net(cands_t).view(b, k), neg_inf)
            a_star = u_online.argmax(dim=1, keepdim=True)
            boot = u_target.gather(1, a_star)
        else:  # expected_sarsa
            u_max = u_target_masked.max(dim=1, keepdim=True).values
            n = mask_t.sum(dim=1, keepdim=True).clamp(min=1)
            u_mean = (u_target * mask_t).sum(dim=1, keepdim=True) / n
            boot = (1.0 - epsilon) * u_max + epsilon * u_mean
        return torch.where(has_next, boot, torch.zeros_like(boot))

    def update_target_network(self):
        """Copies weights from online network to target network."""
        self.target_net.load_state_dict(self.online_net.state_dict())

    def save(self, filepath):
        """Saves agent weights and metadata."""
        torch.save(
            {
                "online_net_state_dict": self.online_net.state_dict(),
                "target_net_state_dict": self.target_net.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
            },
            filepath,
        )

    def load(self, filepath):
        """Loads agent weights from checkpoint."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.online_net.load_state_dict(checkpoint["online_net_state_dict"])
        self.target_net.load_state_dict(checkpoint.get("target_net_state_dict", checkpoint["online_net_state_dict"]))
        if "optimizer_state_dict" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
