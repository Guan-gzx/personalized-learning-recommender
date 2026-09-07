"""Leakage-safe, chronological offline evaluation for the recommendation service."""
from datetime import datetime
from math import log2
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recommender.db import Repository
from recommender.service import LearningService


class SnapshotRepository:
    """Read-only repository view used to prevent future events leaking into ranking."""
    def __init__(self, source, history):
        self.source = source
        self.history = history

    def knowledge_points(self):
        return self.source.knowledge_points()

    def edges(self):
        return self.source.edges()

    def questions(self):
        return self.source.questions()

    def interactions(self, student_id):
        return self.history if student_id == "demo_student" else []

root = Path(__file__).resolve().parents[1]
repo = Repository(root / "data" / "learning.db")
repo.initialize(force_seed=True)
events = repo.interactions("demo_student")
holdout = events[-12:]
history = events[:-12]
pre_time = datetime.fromisoformat(holdout[0]["answered_at"])
post_time = datetime.fromisoformat(holdout[-1]["answered_at"])
service = LearningService(SnapshotRepository(repo, history), use_checkpoint=False)
weak_targets = {event["knowledge_id"] for event in holdout if not event["correct"]}
ranking = service.recommend("demo_student", limit=5, now=pre_time)
recommended = [item["knowledge_id"] for item in ranking]
hits = [item in weak_targets for item in recommended]
precision = sum(hits) / len(recommended)
recall = len(set(recommended) & weak_targets) / max(len(weak_targets), 1)
dcg = sum((1 if hit else 0) / log2(index + 2) for index, hit in enumerate(hits))
# A result is relevant at the exercise level, so multiple exercises for one weak
# knowledge point remain distinct relevant documents in the ranked list.
relevant_available = sum(item["knowledge_id"] in weak_targets for item in repo.questions())
ideal = sum(1 / log2(index + 2) for index in range(min(relevant_available, len(recommended))))
ndcg = dcg / ideal if ideal else 0.0
pre_mastery = service.mastery("demo_student", now=pre_time)[0]
post_service = LearningService(SnapshotRepository(repo, events), use_checkpoint=False)
post_mastery = post_service.mastery("demo_student", now=post_time)[0]
knowledge_gain = sum(post_mastery[item] - pre_mastery[item] for item in weak_targets) / max(len(weak_targets), 1)

# For every weak concept, count hold-out attempts until model mastery first reaches 0.75.
efficiency_counts = []
for knowledge_id in weak_targets:
    sequence = list(history)
    attempts = 0
    reached = False
    for event in holdout:
        sequence.append(event)
        if event["knowledge_id"] == knowledge_id:
            attempts += 1
            timestamp = datetime.fromisoformat(event["answered_at"])
            snapshot = LearningService(SnapshotRepository(repo, sequence), use_checkpoint=False).mastery("demo_student", now=timestamp)[0]
            if snapshot[knowledge_id] >= 0.75:
                reached = True
                efficiency_counts.append(attempts)
                break
    if not reached:
        continue
efficiency = sum(efficiency_counts) / len(efficiency_counts) if efficiency_counts else None
print("Evaluation protocol: deterministic demo log; chronological 60-event history / 12-event hold-out; no future events in ranking.")
print(f"Precision@5: {precision:.3f}")
print(f"Recall@5: {recall:.3f}")
print(f"NDCG@5: {ndcg:.3f}")
print(f"Model-estimated Knowledge Gain (post - pre mastery): {knowledge_gain:.3f}")
if efficiency is None:
    print("Learning Efficiency: not achieved in this hold-out (no weak concept crossed 0.75 mastery).")
else:
    print(f"Learning Efficiency (recommended attempts / newly mastered concept): {efficiency:.3f}")
