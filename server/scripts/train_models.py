"""Train a compact temporal mastery model on the local or imported interaction log."""
from datetime import datetime
from pathlib import Path
import sys
import torch
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recommender.db import Repository
from recommender.model import TemporalMasteryNet

root = Path(__file__).resolve().parents[1]
repo = Repository(root / "data" / "learning.db")
repo.initialize()
points = repo.knowledge_points(); index = {p["id"]: i for i, p in enumerate(points)}
questions = {q["id"]: q for q in repo.questions()}; events = repo.interactions("demo_student")
if len(events) < 4: raise SystemExit("Need at least four interactions to train.")
ids = torch.tensor([[index[e["knowledge_id"]] for e in events]], dtype=torch.long)
correct = torch.tensor([[e["correct"] for e in events]], dtype=torch.float32)
difficulty = torch.tensor([[questions[e["question_id"]]["difficulty"] for e in events]], dtype=torch.float32)
duration = torch.tensor([[e.get("duration_sec", 0.0) for e in events]], dtype=torch.float32)
deltas, previous = [], None
for event in events:
    timestamp = datetime.fromisoformat(event["answered_at"])
    deltas.append(0.0 if previous is None else max(0.0, (timestamp - previous).total_seconds() / 86400)); previous = timestamp
delta_days = torch.tensor([deltas], dtype=torch.float32)
model = TemporalMasteryNet(len(points), hidden_dim=32); optimizer = torch.optim.AdamW(model.parameters(), lr=0.01, weight_decay=1e-4); model.train()
for epoch in range(80):
    optimizer.zero_grad(); prediction, _ = model(ids, correct, difficulty, duration, delta_days)
    # Supervise the probability of the knowledge point answered at the next step.
    # The network still emits a mastery vector for every concept at each timestep.
    next_prediction = prediction[:, :-1].gather(-1, ids[:, 1:].unsqueeze(-1)).squeeze(-1)
    loss = F.binary_cross_entropy(next_prediction, correct[:, 1:]); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); optimizer.step()
output = root / "data" / "temporal_mastery.pt"
torch.save({"model": model.state_dict(), "knowledge_ids": index, "hidden_dim": 32, "epochs": 80}, output)
print(f"Saved {output.name}; final next-event loss={loss.item():.4f}; epochs=80")
