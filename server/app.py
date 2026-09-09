from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

from recommender.db import Repository
from recommender.dataloader import DataLoader
from recommender.service import LearningService

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
repo = Repository(ROOT / "data" / "learning.db")
service = LearningService(repo)
loader = DataLoader(repo, ROOT / "data" / "uploads")


@app.before_request
def ensure_database():
    repo.initialize()


@app.get("/")
def dashboard():
    student_id = request.args.get("student", "demo_student")
    snapshot = service.dashboard(student_id)
    return render_template("dashboard.html", **snapshot)


@app.get("/study/<question_id>")
def study(question_id):
    student_id = request.args.get("student", "demo_student")
    question = repo.get_question(question_id)
    if question is None:
        abort(404)
    session_total = max(1, min(request.args.get("session_total", 1, type=int), 20))
    session_step = max(1, min(request.args.get("session_step", 1, type=int), session_total))
    return render_template(
        "study.html", question=question, student_id=student_id,
        favorite=question_id in repo.favorites(student_id), session_total=session_total,
        session_step=session_step, knowledge=request.args.get("knowledge", ""),
    )


@app.get("/practice")
def practice():
    student_id = request.args.get("student", "demo_student")
    question = service.practice_question(student_id, request.args.get("knowledge"))
    if question is None:
        return redirect(url_for("library", student=student_id))
    session_total = max(1, min(request.args.get("total", 5, type=int), 20))
    session_step = max(1, min(request.args.get("step", 1, type=int), session_total))
    return redirect(url_for(
        "study", question_id=question["id"], student=student_id,
        session_total=session_total, session_step=session_step, knowledge=request.args.get("knowledge") or "",
    ))


@app.get("/library")
def library():
    student_id = request.args.get("student", "demo_student")
    knowledge_id = request.args.get("knowledge") or None
    level = request.args.get("level") or None
    keyword = request.args.get("q", "").strip()
    favorites_only = request.args.get("favorites") == "1"
    questions = service.question_catalog(student_id, knowledge_id, level, keyword, favorites_only)
    return render_template("library.html", student_id=student_id, questions=questions, points=repo.knowledge_points(), selected_knowledge=knowledge_id, selected_level=level, keyword=keyword, favorites_only=favorites_only)


@app.get("/history")
def history():
    student_id = request.args.get("student", "demo_student")
    return render_template("history.html", student_id=student_id, events=service.learning_history(student_id))


@app.get("/mistakes")
def mistakes():
    student_id = request.args.get("student", "demo_student") or "demo_student"
    # 同一题只保留最近一次答错记录（按时间序遍历，后者覆盖前者）
    latest_wrong = {}
    for event in service.learning_history(student_id, only_wrong=True):
        latest_wrong[event["question"]["id"]] = event
    return render_template("mistakes.html", student_id=student_id, events=list(latest_wrong.values()))


@app.get("/knowledge/<knowledge_id>")
def knowledge_detail(knowledge_id):
    student_id = request.args.get("student", "demo_student")
    detail = service.knowledge_detail(student_id, knowledge_id)
    if detail is None:
        abort(404)
    return render_template("knowledge.html", student_id=student_id, **detail)


@app.post("/favorite/<question_id>")
def favorite(question_id):
    student_id = request.form.get("student_id", "demo_student")
    if repo.get_question(question_id) is None:
        abort(404)
    repo.toggle_favorite(student_id, question_id)
    return redirect(request.referrer or url_for("library", student=student_id))


@app.post("/settings/daily-goal")
def set_daily_goal():
    student_id = request.form.get("student_id", "demo_student")
    try:
        repo.set_daily_goal(student_id, request.form.get("daily_goal", 5))
    except (TypeError, ValueError):
        abort(400)
    return redirect(request.referrer or url_for("dashboard", student=student_id))


@app.post("/study/<question_id>")
def submit_answer(question_id):
    student_id = request.form.get("student_id", "demo_student")
    selected = request.form.get("answer", "")
    question = repo.get_question(question_id)
    if question is None:
        abort(404)
    correct = selected == question["answer"]
    try:
        duration_sec = max(0.0, min(float(request.form.get("duration_sec", 0)), 7200.0))
    except ValueError:
        duration_sec = 0.0
    service.record_answer(student_id, question_id, correct, duration_sec)
    return redirect(url_for(
        "result", question_id=question_id, student=student_id, correct=int(correct),
        session_total=max(1, min(request.form.get("session_total", 1, type=int), 20)),
        session_step=max(1, request.form.get("session_step", 1, type=int)),
        knowledge=request.form.get("knowledge", ""),
    ))


@app.get("/result/<question_id>")
def result(question_id):
    question = repo.get_question(question_id)
    if question is None:
        abort(404)
    session_total = max(1, min(request.args.get("session_total", 1, type=int), 20))
    session_step = max(1, min(request.args.get("session_step", 1, type=int), session_total))
    knowledge = request.args.get("knowledge") or None
    next_question = None if session_step >= session_total else service.practice_question(request.args.get("student", "demo_student"), knowledge)
    return render_template(
        "result.html",
        question=question,
        student_id=request.args.get("student", "demo_student"),
        correct=request.args.get("correct") == "1",
        next_question=next_question,
        session_total=session_total,
        session_step=session_step,
        knowledge=knowledge,
    )


@app.get("/api/dashboard/<student_id>")
def api_dashboard(student_id):
    return jsonify(service.dashboard(student_id))


# ---------- 数据中心：DataLoader + 数据库浏览器（合并页） ----------

@app.get("/data")
@app.get("/dataloader")
def data_page():
    return render_template("data.html", points=repo.knowledge_points(), tab=request.args.get("tab", "loader"))


@app.get("/api/db")
def api_db():
    """数据库浏览器数据源：全部业务表实时快照。"""
    tables = {}
    with repo.connect() as conn:
        for name in ("questions", "interactions", "knowledge_points", "edges", "favorites", "learner_settings"):
            cols = [row[1] for row in conn.execute(f"PRAGMA table_info({name})")]
            rows = [dict(row) for row in conn.execute(f"SELECT * FROM {name}")]
            tables[name] = {"columns": cols, "rows": rows}
    return jsonify({"tables": tables})


@app.post("/dataloader/preview")
def dataloader_preview():
    upload = request.files.get("file")
    target = request.form.get("target", "questions")
    if target not in ("questions", "interactions"):
        abort(400)
    if upload is None or not upload.filename:
        return render_template("data.html", points=repo.knowledge_points(), tab="loader",
                               error="请先选择要上传的文件")
    raw = upload.read()
    if not raw:
        return render_template("data.html", points=repo.knowledge_points(), tab="loader",
                               error="上传的文件为空")
    rows, parse_errors = loader.parse(raw, upload.filename, target)
    if not rows:
        return render_template("data.html", points=repo.knowledge_points(), tab="loader",
                               error="未能从文件中解析出任何数据行", errors=parse_errors)
    valid, row_errors = loader.validate(rows, target)
    parse_errors = [f"第 {e['row']} 行（{e['title']}）：{'；'.join(e['problems'])}" for e in row_errors] + parse_errors
    token = loader.stage(valid, target) if valid else ""
    preview = valid[:20]
    return render_template(
        "data.html", points=repo.knowledge_points(), tab="loader", target=target,
        filename=upload.filename, total=len(rows), valid_count=len(valid),
        error_count=len(parse_errors), errors=parse_errors[:30],
        preview=preview, token=token, staged_total=len(valid),
    )


@app.post("/dataloader/commit")
def dataloader_commit():
    token = request.form.get("token", "")
    duplicate_mode = request.form.get("duplicate_mode", "skip")
    result = loader.commit(token, duplicate_mode)
    if result is None:
        return render_template("data.html", points=repo.knowledge_points(), tab="loader",
                               error="加载会话已过期，请重新上传文件")
    return render_template("data.html", points=repo.knowledge_points(), tab="loader", result=result)


@app.get("/dataloader/template/<target>")
def dataloader_template(target):
    if target == "questions":
        csv_text = "id,knowledge_id,title,prompt,choices,answer,explanation,difficulty\n" \
            ",integer,示例题,2 + 3 = ?,5|6|1|0,5,先算加法。,0.30\n"
    elif target == "interactions":
        csv_text = "student_id,question_id,correct,duration_sec,answered_at\n" \
            "demo_student,q01,1,30,\n"
    else:
        abort(404)
    from flask import Response
    return Response("\ufeff" + csv_text, mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={target}_template.csv"})


if __name__ == "__main__":
    repo.initialize(force_seed=True)
    app.run(host="127.0.0.1", port=5000, debug=False)
