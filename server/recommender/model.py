from datetime import datetime, timezone

import numpy as np
import torch
from torch import nn


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


class TemporalMasteryModel:
    """A compact, inspectable LSTM cell with a time-aware forgetting gate.

    The gate parameters are intentionally explicit so students can inspect and tune
    the model before replacing them with weights trained on ASSISTments/EdNet.
    """

    def __init__(self):
        self.w_forget = np.array([-0.6, -0.35, -0.28, 0.12])
        self.w_input = np.array([1.25, -0.7, -0.12, 0.18])
        self.w_output = np.array([0.85, -0.20, -0.08, 0.15])
        self.w_candidate = np.array([1.10, -0.55, -0.10, 0.20])

    def score(self, events, difficulty=0.5, now=None):
        now = now or datetime.now(timezone.utc)
        cell, hidden, previous = 0.0, 0.0, None
        trace = []
        for event in events:
            timestamp = datetime.fromisoformat(event["answered_at"])
            interval_days = 0.0 if previous is None else max(0.0, (timestamp - previous).total_seconds() / 86400)
            previous = timestamp
            features = np.array([2 * int(event["correct"]) - 1, difficulty, min(interval_days / 7, 3), hidden])
            forget = sigmoid(float(np.dot(self.w_forget, features) + 1.3))
            input_gate = sigmoid(float(np.dot(self.w_input, features)))
            output_gate = sigmoid(float(np.dot(self.w_output, features)))
            candidate = np.tanh(float(np.dot(self.w_candidate, features)))
            cell = forget * cell + input_gate * candidate
            hidden = output_gate * np.tanh(cell)
            trace.append({
                "forget_gate": round(float(forget), 3),
                "input_gate": round(float(input_gate), 3),
                "output_gate": round(float(output_gate), 3),
                "interval_days": round(interval_days, 2),
            })
        if previous is not None:
            days_since = max(0.0, (now - previous).total_seconds() / 86400)
            # Explicit post-session decay makes an overdue review observable in the UI.
            retention = float(np.exp(-days_since * (0.055 + difficulty * 0.025)))
            hidden *= retention
        else:
            days_since, retention = 0.0, 1.0
        mastery = float(np.clip(0.5 + hidden * 0.5, 0.02, 0.98))
        diagnostic = trace[-1] if trace else {"forget_gate": 0.0, "input_gate": 0.0, "output_gate": 0.0, "interval_days": 0.0}
        return mastery, {**diagnostic, "retention": round(retention, 3), "days_since": round(days_since, 2), "event_count": len(events)}


class KnowledgeGraphEncoder(nn.Module):
    """Direction-aware GraphSAGE-style encoder for the knowledge graph.

    Prerequisite edges have asymmetric meanings: a predecessor contributes
    differently to a target concept than a target contributes back to its
    prerequisite. Keeping the two aggregation channels separate avoids the
    feature collapse caused by treating every relation as an undirected edge.
    """

    def __init__(self, input_dim=10, hidden_dim=16, output_dim=8, seed=7):
        super().__init__()
        torch.manual_seed(seed)
        self.self_layer = nn.Linear(input_dim, hidden_dim)
        self.predecessor_layer = nn.Linear(input_dim, hidden_dim)
        self.successor_layer = nn.Linear(input_dim, hidden_dim)
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        for layer in (self.self_layer, self.predecessor_layer, self.successor_layer, self.output_layer):
            nn.init.xavier_uniform_(layer.weight, gain=0.7)
            nn.init.zeros_(layer.bias)
        self.eval()

    @torch.no_grad()
    def encode(self, features, edge_index):
        x = torch.as_tensor(features, dtype=torch.float32)
        n = x.shape[0]
        predecessor = torch.zeros((n, n), dtype=torch.float32)
        successor = torch.zeros((n, n), dtype=torch.float32)
        if edge_index:
            for source, target in edge_index:
                predecessor[target, source] = 1.0
                successor[source, target] = 1.0
        predecessor_mean = predecessor @ x / predecessor.sum(dim=1, keepdim=True).clamp_min(1.0)
        successor_mean = successor @ x / successor.sum(dim=1, keepdim=True).clamp_min(1.0)
        hidden = torch.relu(
            self.self_layer(x)
            + self.predecessor_layer(predecessor_mean)
            + self.successor_layer(successor_mean)
        )
        return torch.nn.functional.normalize(self.output_layer(hidden), dim=1).numpy()


class TemporalMasteryNet(nn.Module):
    """Time-aware LSTM knowledge tracer with one probability per knowledge point.

    At every observed interaction the network updates a memory cell with the
    answer, item difficulty, response duration and elapsed time. The readout
    is a vector of current mastery probabilities for *all* knowledge points,
    rather than one generic next-answer score.
    """

    def __init__(self, knowledge_count, hidden_dim=32):
        super().__init__()
        self.knowledge_count = knowledge_count
        self.knowledge_embedding = nn.Embedding(knowledge_count, 12)
        self.input_proj = nn.Linear(12 + 4, hidden_dim)
        self.gates = nn.Linear(hidden_dim + hidden_dim, hidden_dim * 4)
        self.mastery_readout = nn.Linear(hidden_dim, knowledge_count)
        self.decay_rate = nn.Parameter(torch.tensor(0.06))

    def forward(self, knowledge_ids, correct, difficulty, duration_sec, delta_days):
        batch_size, sequence_length = knowledge_ids.shape
        hidden_dim = self.mastery_readout.in_features
        hidden = torch.zeros(batch_size, hidden_dim, device=knowledge_ids.device)
        cell = torch.zeros_like(hidden)
        predictions, forget_trace = [], []
        for step in range(sequence_length):
            embedding = self.knowledge_embedding(knowledge_ids[:, step])
            features = torch.stack([correct[:, step].float(), difficulty[:, step].float(), torch.log1p(duration_sec[:, step].float()) / 6.0, torch.clamp(delta_days[:, step].float() / 7.0, 0, 3)], dim=1)
            x = torch.tanh(self.input_proj(torch.cat([embedding, features], dim=1)))
            input_gate, forget_gate, output_gate, candidate = self.gates(torch.cat([x, hidden], dim=1)).chunk(4, dim=1)
            input_gate, forget_gate, output_gate = torch.sigmoid(input_gate), torch.sigmoid(forget_gate), torch.sigmoid(output_gate)
            candidate = torch.tanh(candidate)
            retention = torch.exp(-torch.relu(self.decay_rate) * torch.clamp(delta_days[:, step], 0, 30)).unsqueeze(1)
            cell = retention * forget_gate * cell + input_gate * candidate
            hidden = output_gate * torch.tanh(cell)
            predictions.append(torch.sigmoid(self.mastery_readout(hidden)))
            forget_trace.append(forget_gate.mean(dim=1))
        return torch.stack(predictions, dim=1), torch.stack(forget_trace, dim=1)
