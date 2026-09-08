"""DataLoader：Web 界面数据加载器。

支持从上传的 JSON / CSV 文件解析、校验并导入题目（questions）与
答题记录（interactions）两张表。流程：parse → validate → preview → commit。
"""

import csv
import io
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

CHOICE_SEPARATORS = ("|", "｜", ";", "；")
TRUE_TOKENS = {"1", "true", "yes", "对", "正确", "是"}
FALSE_TOKENS = {"0", "false", "no", "错", "错误", "否"}


class DataLoader:
    def __init__(self, repo, staging_dir: Path):
        self.repo = repo
        self.staging_dir = staging_dir
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    # ---------- 解析 ----------

    def parse(self, raw: bytes, filename: str, target: str):
        """解析上传文件为原始字典列表，不校验业务规则。"""
        target = target if target in ("questions", "interactions") else "questions"
        text = self._decode(raw)
        rows = []
        errors = []
        if filename.lower().endswith(".json") or text.lstrip()[:1] in "[{":
            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                return [], [f"JSON 解析失败：第 {exc.lineno} 行第 {exc.colno} 列 — {exc.msg}"]
            if isinstance(data, dict) and target in data:
                data = data[target]
            if isinstance(data, dict):
                data = [data]
            if not isinstance(data, list):
                return [], ["JSON 顶层必须是数组，或形如 {\"questions\": [...]} 的对象"]
            rows = [item for item in data if isinstance(item, dict)]
            if len(rows) != len(data):
                errors.append(f"忽略 {len(data) - len(rows)} 个非对象元素")
        else:
            try:
                reader = csv.DictReader(io.StringIO(text))
                rows = [self._clean_row(r) for r in reader]
            except csv.Error as exc:
                return [], [f"CSV 解析失败：{exc}"]
        return rows, errors

    @staticmethod
    def _decode(raw: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "gbk"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")

    @staticmethod
    def _clean_row(row):
        cleaned = {}
        for key, value in row.items():
            if key is None:
                continue
            key = key.strip().lower()
            cleaned[key] = (value or "").strip() if isinstance(value, str) else value
        return cleaned

    # ---------- 校验 ----------

    def validate(self, rows, target):
        """逐行校验，返回 (valid_records, errors)。"""
        if target == "questions":
            return self._validate_questions(rows)
        return self._validate_interactions(rows)

    def _validate_questions(self, rows):
        knowledge_ids = {p["id"] for p in self.repo.knowledge_points()}
        existing = {q["id"] for q in self.repo.questions()}
        max_num = 0
        for qid in existing:
            match = re.fullmatch(r"q(\d+)", qid)
            if match:
                max_num = max(max_num, int(match.group(1)))
        used_ids = set()
        valid, errors = [], []
        for index, row in enumerate(rows, start=1):
            problems = []
            knowledge_id = str(row.get("knowledge_id", "")).strip()
            if not knowledge_id:
                problems.append("缺少 knowledge_id")
            elif knowledge_id not in knowledge_ids:
                problems.append(f"知识点不存在：{knowledge_id}（可选：{'、'.join(sorted(knowledge_ids))}）")
            title = str(row.get("title", "")).strip()
            prompt = str(row.get("prompt", "")).strip()
            if not title:
                problems.append("缺少 title（标题）")
            if not prompt:
                problems.append("缺少 prompt（题干）")
            choices = self._parse_choices(row.get("choices"))
            if len(choices) < 2:
                problems.append("choices 至少需要 2 个选项（JSON 数组或用 | 分隔）")
            answer = str(row.get("answer", "")).strip()
            if not answer:
                problems.append("缺少 answer（正确答案）")
            elif choices and answer not in choices:
                problems.append(f"答案 “{answer}” 不在选项中")
            explanation = str(row.get("explanation", "")).strip()
            if not explanation:
                problems.append("缺少 explanation（解析）")
            try:
                difficulty = float(row.get("difficulty", 0.5))
                if not 0 <= difficulty <= 1:
                    problems.append(f"difficulty 需在 0–1 之间（当前 {difficulty}）")
            except (TypeError, ValueError):
                difficulty = 0.5
                problems.append("difficulty 不是数字，已按 0.5 处理")
            question_id = str(row.get("id", "")).strip()
            if question_id:
                if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*", question_id):
                    problems.append(f"id 格式非法：{question_id}（字母开头，仅字母数字下划线）")
                elif question_id in existing:
                    problems.append(f"id 已存在：{question_id}（可选择覆盖或跳过）")
                elif question_id in used_ids:
                    problems.append(f"文件内 id 重复：{question_id}")
                else:
                    used_ids.add(question_id)
            else:
                max_num += 1
                question_id = f"q{max_num:03d}"
                while question_id in existing or question_id in used_ids:
                    max_num += 1
                    question_id = f"q{max_num:03d}"
                used_ids.add(question_id)
            if problems:
                errors.append({"row": index, "title": title or question_id, "problems": problems})
            else:
                valid.append({
                    "id": question_id, "knowledge_id": knowledge_id, "title": title,
                    "prompt": prompt, "choices": choices, "answer": answer,
                    "explanation": explanation, "difficulty": difficulty,
                })
        return valid, errors

    @staticmethod
    def _parse_choices(raw):
        if raw is None:
            return []
        if isinstance(raw, (list, tuple)):
            return [str(c).strip() for c in raw if str(c).strip()]
        text = str(raw).strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(c).strip() for c in parsed if str(c).strip()]
            except json.JSONDecodeError:
                pass
        for sep in CHOICE_SEPARATORS:
            if sep in text:
                return [c.strip() for c in text.split(sep) if c.strip()]
        return [text]

    def _validate_interactions(self, rows):
        questions = {q["id"]: q for q in self.repo.questions()}
        valid, errors = [], []
        for index, row in enumerate(rows, start=1):
            problems = []
            question_id = str(row.get("question_id", "")).strip()
            question = questions.get(question_id)
            if not question:
                problems.append(f"question_id 不存在：{question_id or '（空）'}")
            student_id = str(row.get("student_id", "")).strip() or "demo_student"
            correct_raw = str(row.get("correct", "")).strip().lower()
            if correct_raw in TRUE_TOKENS:
                correct = 1
            elif correct_raw in FALSE_TOKENS:
                correct = 0
            else:
                correct = None
                problems.append(f"correct 无法识别：{correct_raw or '（空）'}（可用：1/0、true/false、对/错）")
            try:
                duration_sec = max(0.0, min(float(row.get("duration_sec", 0) or 0), 7200.0))
            except (TypeError, ValueError):
                duration_sec = 0.0
                problems.append("duration_sec 不是数字，已按 0 处理")
            answered_at = str(row.get("answered_at", "")).strip()
            if answered_at:
                try:
                    datetime.fromisoformat(answered_at.replace("Z", "+00:00"))
                except ValueError:
                    problems.append(f"answered_at 不是 ISO 时间（当前 {answered_at}，可留空=现在）")
            else:
                answered_at = datetime.now(timezone.utc).isoformat()
            if problems:
                errors.append({"row": index, "title": question_id or "—", "problems": problems})
            else:
                valid.append({
                    "student_id": student_id, "question_id": question_id,
                    "knowledge_id": question["knowledge_id"] if question else "",
                    "correct": correct, "duration_sec": duration_sec,
                    "answered_at": answered_at,
                })
        return valid, errors

    # ---------- 暂存与提交 ----------

    def stage(self, records, target):
        token = uuid.uuid4().hex[:12]
        payload = {"target": target, "records": records, "created_at": datetime.now(timezone.utc).isoformat()}
        (self.staging_dir / f"{token}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return token

    def load_staged(self, token):
        path = self.staging_dir / f"{token}.json"
        if not re.fullmatch(r"[0-9a-f]{12}", token or "") or not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def commit(self, token, duplicate_mode="skip"):
        staged = self.load_staged(token)
        if staged is None:
            return None
        target, records = staged["target"], staged["records"]
        result = self._commit_questions(records, duplicate_mode) if target == "questions" \
            else self._commit_interactions(records)
        # 提交后清除该暂存文件
        try:
            (self.staging_dir / f"{token}.json").unlink()
        except OSError:
            pass
        return result

    def _commit_questions(self, records, duplicate_mode):
        inserted = updated = skipped = 0
        with self.repo.connect() as conn:
            for record in records:
                exists = conn.execute("SELECT 1 FROM questions WHERE id = ?", (record["id"],)).fetchone()
                if exists and duplicate_mode == "skip":
                    skipped += 1
                    continue
                conn.execute(
                    """INSERT INTO questions (id, knowledge_id, title, prompt, choices, answer, explanation, difficulty)
                       VALUES (:id, :knowledge_id, :title, :prompt, :choices, :answer, :explanation, :difficulty)
                       ON CONFLICT(id) DO UPDATE SET knowledge_id=:knowledge_id, title=:title, prompt=:prompt,
                       choices=:choices, answer=:answer, explanation=:explanation, difficulty=:difficulty""",
                    {**record, "choices": json.dumps(record["choices"], ensure_ascii=False)},
                )
                if exists:
                    updated += 1
                else:
                    inserted += 1
        return {"inserted": inserted, "updated": updated, "skipped": skipped, "total": len(records)}

    def _commit_interactions(self, records):
        with self.repo.connect() as conn:
            conn.executemany(
                """INSERT INTO interactions (student_id, knowledge_id, question_id, correct, duration_sec, answered_at)
                   VALUES (:student_id, :knowledge_id, :question_id, :correct, :duration_sec, :answered_at)""",
                records,
            )
        return {"inserted": len(records), "updated": 0, "skipped": 0, "total": len(records)}
