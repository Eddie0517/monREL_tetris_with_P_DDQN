import numpy as np


class HeuristicAgent:
    """
    Baseline agent using Pierre Dellacherie's classic Tetris heuristic weights:
    Score = -0.51 * Height + 0.76 * Lines - 0.36 * Holes - 0.18 * Bumpiness
    """

    def __init__(self, weight_height=-0.51, weight_lines=0.76, weight_holes=-0.36, weight_bumpiness=-0.18):
        self.weights = np.array([weight_height, weight_holes, weight_bumpiness, weight_lines], dtype=np.float32)

    def evaluate_features(self, features):
        """Calculates heuristic value for a 4D feature vector [Height, Holes, Bumpiness, Lines]."""
        return np.dot(features, self.weights)

    def act(self, next_states):
        """
        Given dict of next_states { action: (features, board) },
        returns the best action maximizing the heuristic score.
        """
        if not next_states:
            return None

        best_score = -float('inf')
        best_action = None

        for action, (features, _) in next_states.items():
            score = self.evaluate_features(features)
            if score > best_score:
                best_score = score
                best_action = action

        return best_action


class NaiveGreedyAgent(HeuristicAgent):
    """
    Lower-performing baseline (Fahey 2003 / Stevens 2016 baseline):
    Only greedily minimizes aggregate height and maximizes cleared lines,
    completely ignoring holes and bumpiness. This causes fatal trapped holes.
    """
    def __init__(self):
        super().__init__(weight_height=-1.0, weight_holes=0.0, weight_bumpiness=0.0, weight_lines=1.0)

