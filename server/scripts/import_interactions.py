"""Import a normalized ASSISTments/EdNet-compatible interaction CSV."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recommender.db import Repository

REQUIRED = {"student_id", "knowledge_id", "question_id", "correct", "answered_at"}
root = Path(__file__).resolve().parents[1]
repo = Repository(root / "data" / "learning.db")
repo.initialize()

if len(sys.argv) != 2:
    raise SystemExit("Usage: python scripts/import_interactions.py interactions.csv")
with Path(sys.argv[1]).open(encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle)
    if not REQUIRED.issubset(reader.fieldnames or []):
        raise SystemExit(f"CSV must include: {', '.join(sorted(REQUIRED))}")
    count = 0
    with repo.connect() as conn:
        for row in reader:
            conn.execute(
                "INSERT INTO interactions (student_id, knowledge_id, question_id, correct, duration_sec, answered_at) VALUES (?, ?, ?, ?, ?, ?)",
                (row["student_id"], row["knowledge_id"], row["question_id"], int(row["correct"]), float(row.get("duration_sec", 0) or 0), row["answered_at"]),
            )
            count += 1
print(f"Imported {count} interactions.")
