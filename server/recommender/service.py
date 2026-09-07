from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

from .model import KnowledgeGraphEncoder, TemporalMasteryModel, TemporalMasteryNet


class LearningService:
    def __init__(self, repo, use_checkpoint=True):
        self.repo = repo
        self.model = TemporalMasteryModel()
        self.graph_encoder = KnowledgeGraphEncoder()
        self.temporal_net = None
        self.temporal_index = {}
        repo_path = getattr(self.repo, "path", None)
        checkpoint = repo_path.parent / "temporal_mastery.pt" if repo_path else None
        if use_checkpoint and checkpoint and checkpoint.exists():
            try:
                payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
                self.temporal_index = payload.get("knowledge_ids", {})
                network = TemporalMasteryNet(len(self.repo.knowledge_points()), hidden_dim=int(payload.get("hidden_dim", 32)))
                network.load_state_dict(payload["model"])
                network.eval()
                self.temporal_net = network
            except (OSError, KeyError, RuntimeError, ValueError, TypeError):
                # Keep the inspectable NumPy LSTM fallback usable with an older checkpoint.
                self.temporal_net = None

    def graph_embeddings(self, mastery=None):
        points = self.repo.knowledge_points()
        index = {point["id"]: i for i, point in enumerate(points)}
        mastery = mastery or {point["id"]: 0.5 for point in points}
        incoming = {point["id"]: 0 for point in points}
        outgoing = {point["id"]: 0 for point in points}
        for edge in self.repo.edges():
            outgoing[edge["source_id"]] += 1
            incoming[edge["target_id"]] += 1
        features = []
        for point in points:
            features.append([
                point["ordinal"] / max(len(points), 1),
                mastery[point["id"]],
                1.0 if mastery[point["id"]] < 0.55 else 0.0,
                incoming[point["id"]] / max(len(points) - 1, 1),
                outgoing[point["id"]] / max(len(points) - 1, 1),
                *[1.0 if point["id"] == item["id"] else 0.0 for item in points],
            ])
        edge_index = [(index[e["source_id"]], index[e["target_id"]]) for e in self.repo.edges()]
        return {point["id"]: embedding for point, embedding in zip(points, self.graph_encoder.encode(features, edge_index))}

    def graph_affinity(self, mastery, embeddings):
        """Return a 0..1 match to the student's weak knowledge neighborhood."""
        points = self.repo.knowledge_points()
        ids = [point["id"] for point in points]
        matrix = np.asarray([embeddings[item] for item in ids], dtype=float)
        weights = np.asarray([max(0.0, 1.0 - mastery[item]) for item in ids], dtype=float)
        context = (matrix * weights[:, None]).sum(axis=0)
        context_norm = np.linalg.norm(context)
        if context_norm < 1e-9:
            context = matrix.mean(axis=0)
            context_norm = np.linalg.norm(context)
        affinity = {}
        for i, point_id in enumerate(ids):
            vector = matrix[i]
            cosine = float(np.dot(vector, context) / max(np.linalg.norm(vector) * context_norm, 1e-9))
            cosine_score = (cosine + 1.0) / 2.0
            adjacent_weakness = 0.0
            for edge in self.repo.edges():
                if edge["source_id"] == point_id:
                    adjacent_weakness = max(adjacent_weakness, 1.0 - mastery[edge["target_id"]])
                elif edge["target_id"] == point_id:
                    adjacent_weakness = max(adjacent_weakness, 1.0 - mastery[edge["source_id"]])
            affinity[point_id] = round(float(np.clip(0.65 * cosine_score + 0.35 * adjacent_weakness, 0.0, 1.0)), 3)
        return affinity

    def _neural_mastery(self, student_id, now):
        if self.temporal_net is None:
            return None
        events = self.repo.interactions(student_id)
        if not events:
            return {point["id"]: 0.5 for point in self.repo.knowledge_points()}
        questions = {question["id"]: question for question in self.repo.questions()}
        points = self.repo.knowledge_points()
        index = self.temporal_index or {point["id"]: i for i, point in enumerate(points)}
        valid = [event for event in events if event["knowledge_id"] in index and event["question_id"] in questions]
        if not valid:
            return None
        ids = torch.tensor([[index[event["knowledge_id"]] for event in valid]], dtype=torch.long)
        correct = torch.tensor([[event["correct"] for event in valid]], dtype=torch.float32)
        difficulty = torch.tensor([[questions[event["question_id"]]["difficulty"] for event in valid]], dtype=torch.float32)
        duration = torch.tensor([[event.get("duration_sec", 0.0) for event in valid]], dtype=torch.float32)
        deltas, previous = [], None
        for event in valid:
            timestamp = datetime.fromisoformat(event["answered_at"])
            deltas.append(0.0 if previous is None else max(0.0, (timestamp - previous).total_seconds() / 86400))
            previous = timestamp
        with torch.no_grad():
            prediction, _ = self.temporal_net(ids, correct, difficulty, duration, torch.tensor([deltas], dtype=torch.float32))
        probabilities = prediction[0, -1].numpy()
        elapsed = max(0.0, (now - previous).total_seconds() / 86400) if previous else 0.0
        decay = float(torch.relu(self.temporal_net.decay_rate).item())
        probabilities = 0.5 + (probabilities - 0.5) * np.exp(-decay * min(elapsed, 30.0))
        return {point["id"]: round(float(np.clip(probabilities[index[point["id"]]], 0.02, 0.98)), 4) for point in points if point["id"] in index}

    def mastery(self, student_id, now=None):
        now = now or datetime.now(timezone.utc)
        questions = {q["id"]: q for q in self.repo.questions()}
        grouped = defaultdict(list)
        for event in self.repo.interactions(student_id):
            grouped[event["knowledge_id"]].append(event)
        values = {}
        diagnostics = {}
        for point in self.repo.knowledge_points():
            events = grouped[point["id"]]
            difficulty = self._point_difficulty(point["id"], questions)
            values[point["id"]], diagnostics[point["id"]] = self.model.score(events, difficulty, now=now)
        neural = self._neural_mastery(student_id, now)
        if neural:
            for point_id in values:
                handcrafted = values[point_id]
                values[point_id] = round(float(np.clip(0.35 * handcrafted + 0.65 * neural.get(point_id, handcrafted), 0.02, 0.98)), 4)
                diagnostics[point_id]["neural_probability"] = neural.get(point_id, handcrafted)
                diagnostics[point_id]["model"] = "LSTM + 时间遗忘门控"
        else:
            for diagnostic in diagnostics.values():
                diagnostic["neural_probability"] = None
                diagnostic["model"] = "可解释 LSTM 回退"
        return values, diagnostics

    def recommend(self, student_id, limit=5, now=None):
        mastery, diagnostics = self.mastery(student_id, now=now)
        embeddings = self.graph_embeddings(mastery)
        affinity = self.graph_affinity(mastery, embeddings)
        points = {p["id"]: p for p in self.repo.knowledge_points()}
        prerequisites = defaultdict(list)
        for edge in self.repo.edges():
            if edge["relation"] == "prerequisite":
                prerequisites[edge["target_id"]].append(edge["source_id"])
        candidates = []
        # Exclude the most recently *submitted* answers by insertion order, so a
        # question just answered is never served again within the same session,
        # even if older seeded logs carry later timestamps.
        recent = sorted(self.repo.interactions(student_id), key=lambda item: item["id"])[-8:]
        seen = {event["question_id"] for event in recent}
        for question in self.repo.questions():
            if question["id"] in seen:
                continue
            knowledge_id = question["knowledge_id"]
            weak = 1 - mastery[knowledge_id]
            prerequisite_gap = max((1 - mastery[item] for item in prerequisites[knowledge_id]), default=0)
            # Graph affinity rewards exercises connected to the student's weak neighborhood.
            graph_affinity = affinity[knowledge_id]
            score = 0.56 * weak + 0.20 * prerequisite_gap + 0.12 * question["difficulty"] + 0.12 * graph_affinity
            reason = "掌握度偏低，需要巩固"
            prerequisite_names = [points[item]["name"] for item in prerequisites[knowledge_id]]
            path = " → ".join(prerequisite_names + [points[knowledge_id]["name"]]) if prerequisite_names else points[knowledge_id]["name"]
            if prerequisite_gap > 0.45:
                reason = "前置知识存在缺口，建议先复习基础"
            if diagnostics[knowledge_id]["interval_days"] > 5:
                reason = "距上次练习较久，进入遗忘复习窗口"
            candidates.append({
                **question,
                "score": round(score, 3),
                "reason": reason,
                "mastery": round(mastery[knowledge_id], 3),
                "knowledge_name": points[knowledge_id]["name"],
                "graph_signal": graph_affinity,
                "knowledge_path": path,
                "explanation": f"{path} · 弱项邻域匹配 {graph_affinity:.2f}",
            })
        ranked = sorted(candidates, key=lambda item: (item["score"], item["difficulty"]), reverse=True)
        # Keep dashboard recommendations diverse: select one strongest item per
        # knowledge point before filling remaining slots with the next best items.
        diverse = []
        used_knowledge = set()
        for item in ranked:
            if item["knowledge_id"] in used_knowledge:
                continue
            diverse.append(item)
            used_knowledge.add(item["knowledge_id"])
            if len(diverse) >= limit:
                return diverse
        for item in ranked:
            if item in diverse:
                continue
            diverse.append(item)
            if len(diverse) >= limit:
                break
        return diverse

    def dashboard(self, student_id):
        mastery, diagnostics = self.mastery(student_id)
        embeddings = self.graph_embeddings(mastery)
        points = self.repo.knowledge_points()
        positions = {"integer": (18, 52), "fractions": (39, 25), "equations": (61, 52), "functions": (82, 25), "geometry": (39, 78)}
        recommended_ids = {item["knowledge_id"] for item in self.recommend(student_id)}
        graph_nodes = []
        for point in points:
            value = mastery[point["id"]]
            x, y = positions.get(point["id"], (50, 50))
            graph_nodes.append({
                "id": point["id"], "name": point["name"], "mastery": round(value * 100),
                "state": "薄弱" if value < 0.55 else "待复习" if value < 0.75 else "已掌握",
                "x": x, "y": y, "highlight": point["id"] in recommended_ids,
                "embedding": [round(float(v), 3) for v in embeddings[point["id"]]],
            })
        node_lookup = {node["id"]: node for node in graph_nodes}
        graph_edges = []
        for edge in self.repo.edges():
            source = node_lookup[edge["source_id"]]; target = node_lookup[edge["target_id"]]
            graph_edges.append({**edge, "x1": source["x"], "y1": source["y"], "x2": target["x"], "y2": target["y"]})
        events = self.repo.interactions(student_id)
        daily_goal = self.repo.daily_goal(student_id)
        today = datetime.now(timezone.utc).date().isoformat()
        today_events = [event for event in events if event["answered_at"][:10] == today]
        completed_today = len(today_events)
        recent_days = {event["answered_at"][:10] for event in events}
        streak = 0
        day = datetime.now(timezone.utc).date()
        while day.isoformat() in recent_days:
            streak += 1
            day = day.fromordinal(day.toordinal() - 1)
        return {
            "student_id": student_id,
            "recommendations": self.recommend(student_id),
            "nodes": graph_nodes,
            "edges": self.repo.edges(),
            "graph_edges": graph_edges,
            "activity_count": len(events),
            "daily_goal": daily_goal,
            "completed_today": completed_today,
            "daily_progress": min(100, round(completed_today / daily_goal * 100)),
            "streak": streak,
            "average_mastery": round(sum(mastery.values()) / max(len(mastery), 1) * 100),
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "diagnostics": {key: {**item, "display_probability": round((item["neural_probability"] if item["neural_probability"] is not None else item["forget_gate"]) * 100)} for key, item in diagnostics.items()},
            "signal_items": self._unique_knowledge_items(self.recommend(student_id, limit=50), len(points)),
        }

    @staticmethod
    def _unique_knowledge_items(items, limit):
        unique = []
        seen = set()
        for item in items:
            if item["knowledge_id"] in seen:
                continue
            seen.add(item["knowledge_id"])
            unique.append(item)
            if len(unique) >= limit:
                break
        return unique

    def question_catalog(self, student_id, knowledge_id=None, level=None, keyword=None, favorites_only=False):
        answered = {event["question_id"]: event for event in self.repo.interactions(student_id)}
        favorites = self.repo.favorites(student_id)
        points = {point["id"]: point for point in self.repo.knowledge_points()}
        result = []
        for question in self.repo.questions():
            if knowledge_id and question["knowledge_id"] != knowledge_id:
                continue
            if level == "basic" and question["difficulty"] > 0.42:
                continue
            if level == "advanced" and question["difficulty"] < 0.52:
                continue
            if keyword and keyword.lower() not in (question["title"] + question["prompt"]).lower():
                continue
            if favorites_only and question["id"] not in favorites:
                continue
            event = answered.get(question["id"])
            result.append({**question, "knowledge_name": points[question["knowledge_id"]]["name"], "favorite": question["id"] in favorites, "answered": bool(event), "last_correct": None if not event else bool(event["correct"])})
        return result

    def learning_history(self, student_id, only_wrong=False):
        questions = {question["id"]: question for question in self.repo.questions()}
        points = {point["id"]: point for point in self.repo.knowledge_points()}
        history = []
        for event in reversed(self.repo.interactions(student_id)):
            if only_wrong and event["correct"]:
                continue
            question = questions.get(event["question_id"])
            if question:
                history.append({**event, "question": question, "knowledge_name": points[event["knowledge_id"]]["name"]})
        return history

    def knowledge_detail(self, student_id, knowledge_id):
        points = {point["id"]: point for point in self.repo.knowledge_points()}
        point = points.get(knowledge_id)
        if point is None:
            return None
        mastery, diagnostics = self.mastery(student_id)
        history = [item for item in self.learning_history(student_id) if item["knowledge_id"] == knowledge_id]
        related = []
        for edge in self.repo.edges():
            if edge["source_id"] == knowledge_id or edge["target_id"] == knowledge_id:
                other = edge["target_id"] if edge["source_id"] == knowledge_id else edge["source_id"]
                related.append({"name": points[other]["name"], "relation": "前置知识" if edge["relation"] == "prerequisite" else "关联知识"})
        return {"point": point, "mastery": round(mastery[knowledge_id] * 100), "diagnostic": diagnostics[knowledge_id], "history": history[:8], "related": related, "questions": self.question_catalog(student_id, knowledge_id=knowledge_id)}

    def practice_question(self, student_id, knowledge_id=None):
        candidates = self.recommend(student_id, limit=50)
        if knowledge_id:
            candidates = [item for item in candidates if item["knowledge_id"] == knowledge_id]
        if candidates:
            return candidates[0]
        catalog = self.question_catalog(student_id, knowledge_id=knowledge_id)
        return catalog[0] if catalog else None

    def record_answer(self, student_id, question_id, correct, duration_sec=0):
        question = self.repo.get_question(question_id)
        self.repo.add_interaction(student_id, question, correct, duration_sec)

    @staticmethod
    def _point_difficulty(knowledge_id, questions):
        matching = [item["difficulty"] for item in questions.values() if item["knowledge_id"] == knowledge_id]
        return sum(matching) / len(matching)
