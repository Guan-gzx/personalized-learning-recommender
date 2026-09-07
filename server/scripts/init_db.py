from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recommender.db import Repository

root = Path(__file__).resolve().parents[1]
Repository(root / "data" / "learning.db").initialize(force_seed=True)
print("Database initialized with deterministic demonstration data.")
