# Personalized Learning Recommender

This is the complete runnable deliverable for Task 16, "Personalized exercise recommendation based on a knowledge graph and forgetting curve".

## What is included

- `app.py`: local Web application.
- `recommender/`: SQLite repository, knowledge graph, pure-PyTorch GraphSAGE-style encoder, temporal LSTM-style forgetting model, recommendation and evaluation services.
- `data/`: compact reproducible demo course and interaction seed data.
- `scripts/`: database initialization, evaluation, ASSISTments-compatible CSV importer, and document generator.
- `scripts/train_models.py`: train and save the temporal LSTM + forgetting-gate checkpoint on the current log.
- `docs/`: training paper, defense deck, slide notes, weekly plan, and data/claim statement.

## Run

Use Python 3.10+ in a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\init_db.py
python app.py
```

Open `http://127.0.0.1:5000`. The seeded learner is `demo_student`.

## Key workflow

1. The learner opens the dashboard and receives ranked exercises.
2. Candidate exercises are selected from weak, overdue, or prerequisite knowledge points.
3. `KnowledgeGraphEncoder` performs learnable neighborhood aggregation to produce a compact embedding for each knowledge point. `TemporalMasteryModel` encodes ordered learning events with input, output, and forget gates. The forget gate depends on elapsed time and task difficulty.
4. An answer is saved to SQLite and the next recommendation is recalculated.
5. `scripts/evaluate.py` reports Precision@K, Recall@K, NDCG@K, Knowledge Gain, and Learning Efficiency on a held-out slice of the included deterministic demo log.

## Learning features

- Smart practice starts the next graph-aware recommendation and supports knowledge-point-specific practice.
- The dashboard includes a persisted daily goal and a 3/5/8-question continuous-practice flow with visible session progress.
- Question library contains 100 local exercises with keyword, knowledge point, level, and favorites filters.
- Library search and difficulty/status ordering update immediately in the browser; the form filters remain available without JavaScript.
- Favorites, mistake review, learning history, and knowledge-point profiles are persisted through SQLite.
- The knowledge star map is clickable: select a node to inspect its mastery, prerequisite/related path, and dedicated question set.

The dashboard's “知识星空图” is generated from the same graph service: node brightness encodes mastery, relation lines encode prerequisite/related edges, and a halo marks knowledge points represented in the current recommendation set.

## Real dataset import

The bundled records are transparent synthetic demonstration data, not ASSISTments results. To reproduce a class-scale experiment, download an authorized ASSISTments/EdNet export and normalize it to a CSV with `student_id,knowledge_id,question_id,correct,answered_at`; optionally add `duration_sec` for answer time. Then run:

```powershell
python scripts\import_interactions.py path\to\interactions.csv
python scripts\evaluate.py
```

To exercise the trainable path on the local log:

```powershell
python scripts\train_models.py
```

This writes `data/temporal_mastery.pt`. The fixed, inspectable scorer remains the default Web fallback so the demo is deterministic; the checkpoint is the reproducible training artifact for the real-data experiment phase.

See `docs/data_and_claims.md` before reporting metrics in a paper or defense.
