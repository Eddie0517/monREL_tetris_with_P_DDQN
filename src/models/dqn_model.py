import torch
import torch.nn as nn


class DQN(nn.Module):
    """
    Multi-Layer Perceptron (MLP) for predicting Q-values of candidate Tetris states.
    Input: 4-dimensional geometric feature vector [AggHeight, Holes, Bumpiness, Lines]
    Output: Scalar Q-value estimate
    """

    def __init__(self, input_dim=4, hidden_dim=64):
        super(DQN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0.0)

    def forward(self, x):
        """
        Forward pass.
        Args:
            x: Tensor of shape (batch_size, 4)
        Returns:
            Tensor of shape (batch_size, 1)
        """
        return self.net(x)
