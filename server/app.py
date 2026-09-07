from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

from recommender.db import Repository
from recommender.service import LearningService

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
repo = Repository(ROOT / "data" / "learning.db")
service = LearningService(repo)


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
    student_id = request.args.get("student", "demo_student")
    return render_template("mistakes.html", student_id=student_id, events=service.learning_history(student_id, only_wrong=True))


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


if __name__ == "__main__":
    repo.initialize(force_seed=True)
    app.run(host="127.0.0.1", port=5000, debug=False)
