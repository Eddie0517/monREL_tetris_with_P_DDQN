import random
from collections import deque
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from src.models.dqn_model import DQN


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
    ):
        self.state_dim = state_dim
        self.gamma = gamma
        self.memory = deque(maxlen=memory_size)

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

    def remember(self, state, reward, next_state, done):
        """Stores transition in replay buffer."""
        self.memory.append((state, reward, next_state, done))

    def train_step(self, batch_size=512):
        """
        Samples a mini-batch from replay buffer and updates online network weights.
        Returns:
            loss (float) or None if insufficient samples
        """
        if len(self.memory) < batch_size:
            return None

        batch = random.sample(self.memory, batch_size)
        states, rewards, next_states, dones = zip(*batch)

        states_t = torch.tensor(np.array(states), dtype=torch.float32, device=self.device)
        rewards_t = torch.tensor(np.array(rewards), dtype=torch.float32, device=self.device).unsqueeze(1)
        next_states_t = torch.tensor(np.array(next_states), dtype=torch.float32, device=self.device)
        dones_t = torch.tensor(np.array(dones), dtype=torch.float32, device=self.device).unsqueeze(1)

        # Target Q calculation with Double DQN / Target Network
        with torch.no_grad():
            next_q = self.target_net(next_states_t)
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
