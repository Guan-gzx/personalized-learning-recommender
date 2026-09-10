"""个性化学习推荐系统 Flask 应用入口。

注意：在 Spyder / PyQtWebEngine 等 GUI 环境中直接 import torch 会触发 c10.dll 初始化失败
（WinError 1114）。原因：PyQt5 自带不同版本的 msvcp140.dll / vcruntime140.dll，
被 Spyder 主进程先加载，与 torch 自带的版本冲突。必须：
1. 通过 ctypes.RTLD_GLOBAL 强制把 torch 自带的 VC 运行时先加载进进程；
2. 把 torch.lib 加入 DLL 搜索路径首位；
3. 允许 OpenMP 重复库（兼容 PyQt5 自带的 libiomp5md）。"""
import os
import sys
import ctypes
from functools import wraps
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "True")
os.environ.setdefault("OMP_NUM_THREADS", "1")

# 计算 torch.lib 路径并前置到 PATH / os.add_dll_directory
_VENV = Path(__file__).resolve().parent / ".venv"
_TORCH_LIB = _VENV / "Lib" / "site-packages" / "torch" / "lib"
if _TORCH_LIB.exists():
    s = str(_TORCH_LIB)
    if s not in os.environ.get("PATH", ""):
        os.environ["PATH"] = s + os.pathsep + os.environ["PATH"]
    try:
        # Python 3.8+ on Windows：明确把目录加入 DLL 搜索路径
        os.add_dll_directory(s)
    except (AttributeError, OSError):
        pass
    # 强制预加载 torch 自带的 VC 运行时（c10.dll 依赖），用 RTLD_GLOBAL 让后续所有模块共享
    for _dll in ("vcruntime140_1.dll", "vcruntime140.dll", "msvcp140.dll"):
        _p = _TORCH_LIB / _dll
        if _p.exists():
            try:
                ctypes.CDLL(str(_p), mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass  # 已被其他模块加载过同名 DLL 时忽略，不影响后续 torch 行为

from flask import Flask, Response, abort, jsonify, redirect, render_template, request, session, url_for

from recommender.db import Repository
from recommender.dataloader import DataLoader
from recommender.service import LearningService

ROOT = Path(__file__).resolve().parent
app = Flask(__name__)
app.secret_key = "plr-demo-secret-key-change-in-production"  # noqa: S105

# ---------- 账号与角色 ----------
# 演示用：管理员需密码，普通用户也设了密码以避免登录页留空。
USERS = {
    "admin":    {"password": "admin123",   "role": "admin", "display_name": "管理员 Admin",   "tagline": "查看全量后台 · 调度数据"},
    "alice":    {"password": "alice123",   "role": "user",  "display_name": "Alice 林小敏",  "tagline": "七年级 · 偏弱项:方程"},
    "bob":      {"password": "bob123",     "role": "user",  "display_name": "Bob 王大力",    "tagline": "八年级 · 偏弱项:几何"},
    "charlie":  {"password": "charlie123", "role": "user",  "display_name": "Charlie 周晓",  "tagline": "九年级 · 偏弱项:函数"},
}


def current_user():
    """从 session 解析当前登录用户；未登录或账号失效返回 None。"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    record = USERS.get(user_id)
    if record is None:
        return None
    return {"id": user_id, **record}


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def _student_id():
    """解析 student_id：URL 参数优先，其次用当前登录账号。"""
    override = request.values.get("student")
    if override:
        return override
    return session.get("user_id") or "demo_student"


@app.context_processor
def inject_user():
    """把 current_user / is_admin 注入到所有模板的渲染上下文。"""
    user = current_user()
    return {
        "current_user": user,
        "is_admin": bool(user and user["role"] == "admin"),
    }


@app.errorhandler(403)
def forbidden(error):
    """管理员专属功能被普通用户访问时的友好提示页。"""
    html = """<!doctype html><meta charset="utf-8"><title>403 · 权限不足</title>
<style>
        body{font:15px/1.6 "Microsoft YaHei",Arial,sans-serif;background:#f4f7fb;color:#17213b;
             display:grid;place-items:center;min-height:100vh;margin:0}
        .card{background:#fff;padding:36px 42px;border-radius:14px;
              box-shadow:0 16px 40px rgba(33,63,112,.07);max-width:480px;text-align:center}
        h1{margin:0 0 10px;color:#e86571;font-size:24px}
        p{color:#71809d;margin:0 0 18px;font-size:14px}
        .btns a{text-decoration:none;color:#fff;padding:10px 22px;border-radius:10px;font-weight:700;margin:0 4px}
        .b1{background:#3d82f6}.b2{background:#71809d}
    </style>
<div class="card">
    <h1>403 · 权限不足</h1>
    <p>该功能仅对<b>管理员</b>开放。请使用管理员账号登录后再试，<br>或返回个人学习空间继续练习。</p>
    <div class="btns">
        <a class="b1" href="/login">切换账号</a>
        <a class="b2" href="/">返回首页</a>
    </div>
</div>"""
    return Response(html, mimetype="text/html", status=403)


repo = Repository(ROOT / "data" / "learning.db")
service = LearningService(repo)
loader = DataLoader(repo, ROOT / "data" / "uploads")


@app.before_request
def ensure_database():
    """首次访问时初始化数据库；静态文件跳过。"""
    if request.endpoint == "static":
        return
    repo.initialize()


# ---------- 登录 / 登出 ----------
@app.get("/login")
def login():
    if current_user():
        return redirect(request.args.get("next") or url_for("dashboard"))
    return render_template(
        "login.html",
        users=USERS,
        error=request.args.get("error"),
        next_url=request.args.get("next") or url_for("dashboard"),
    )


@app.post("/login")
def login_submit():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    next_url = request.form.get("next") or url_for("dashboard")
    record = USERS.get(username)
    if record is None:
        return redirect(url_for("login", error="账号不存在", next=next_url))
    expected = record["password"]
    if expected and password != expected:
        return redirect(url_for("login", error="密码错误", next=next_url))
    session["user_id"] = username
    session["role"] = record["role"]
    session["display_name"] = record["display_name"]
    return redirect(next_url)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@login_required
def dashboard():
    student_id = _student_id()
    snapshot = service.dashboard(student_id)
    return render_template("dashboard.html", **snapshot)


@app.get("/study/<question_id>")
@login_required
def study(question_id):
    student_id = _student_id()
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
@login_required
def practice():
    student_id = _student_id()
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
@login_required
def library():
    student_id = _student_id()
    knowledge_id = request.args.get("knowledge") or None
    level = request.args.get("level") or None
    keyword = request.args.get("q", "").strip()
    favorites_only = request.args.get("favorites") == "1"
    questions = service.question_catalog(student_id, knowledge_id, level, keyword, favorites_only)
    return render_template("library.html", student_id=student_id, questions=questions, points=repo.knowledge_points(), selected_knowledge=knowledge_id, selected_level=level, keyword=keyword, favorites_only=favorites_only)


@app.get("/history")
@login_required
def history():
    student_id = _student_id()
    return render_template("history.html", student_id=student_id, events=service.learning_history(student_id))


@app.get("/mistakes")
@login_required
def mistakes():
    student_id = _student_id() or "demo_student"
    # 同一题只保留最近一次答错记录（按时间序遍历，后者覆盖前者）
    latest_wrong = {}
    for event in service.learning_history(student_id, only_wrong=True):
        latest_wrong[event["question"]["id"]] = event
    return render_template("mistakes.html", student_id=student_id, events=list(latest_wrong.values()))


@app.get("/knowledge/<knowledge_id>")
@login_required
def knowledge_detail(knowledge_id):
    student_id = _student_id()
    detail = service.knowledge_detail(student_id, knowledge_id)
    if detail is None:
        abort(404)
    return render_template("knowledge.html", student_id=student_id, **detail)


@app.post("/favorite/<question_id>")
@login_required
def favorite(question_id):
    student_id = _student_id()
    if repo.get_question(question_id) is None:
        abort(404)
    repo.toggle_favorite(student_id, question_id)
    return redirect(request.referrer or url_for("library", student=student_id))


@app.post("/settings/daily-goal")
@login_required
def set_daily_goal():
    student_id = _student_id()
    try:
        repo.set_daily_goal(student_id, request.form.get("daily_goal", 5))
    except (TypeError, ValueError):
        abort(400)
    return redirect(request.referrer or url_for("dashboard", student=student_id))


@app.post("/study/<question_id>")
@login_required
def submit_answer(question_id):
    student_id = _student_id()
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
@login_required
def result(question_id):
    question = repo.get_question(question_id)
    if question is None:
        abort(404)
    session_total = max(1, min(request.args.get("session_total", 1, type=int), 20))
    session_step = max(1, min(request.args.get("session_step", 1, type=int), session_total))
    knowledge = request.args.get("knowledge") or None
    next_student = _student_id()
    next_question = None if session_step >= session_total else service.practice_question(next_student, knowledge)
    return render_template(
        "result.html",
        question=question,
        student_id=next_student,
        correct=request.args.get("correct") == "1",
        next_question=next_question,
        session_total=session_total,
        session_step=session_step,
        knowledge=knowledge,
    )


@app.get("/api/dashboard/<student_id>")
@login_required
def api_dashboard(student_id):
    return jsonify(service.dashboard(student_id))


# ---------- 路由（仅管理员可见：数据中心、DataLoader、数据库 API） ----------

@app.get("/data")
@app.get("/dataloader")
@admin_required
def data_page():
    return render_template("data.html", points=repo.knowledge_points(), tab=request.args.get("tab", "loader"))


# 常见手动输入别名：自动跳转到正确页面，避免 404
_ALIAS = {
    "data.html": "data_page", "dataloader.html": "data_page", "database": "data_page",
    "database.html": "data_page", "db": "data_page",
    "index": "dashboard", "index.html": "dashboard", "home": "dashboard",
    "lib": "library", "questions": "library",
    "wrong": "mistakes", "wrongbook": "mistakes",
}

# 这些别名等价于数据中心入口，需要管理员权限
_ADMIN_ALIASES = {"data.html", "dataloader.html", "database", "database.html", "db"}


@app.get("/<alias>")
def alias_redirect(alias):
    key = alias.lower().strip("/")
    target = _ALIAS.get(key)
    if target is None:
        abort(404)
    # 数据中心类别名需要管理员权限
    if key in _ADMIN_ALIASES:
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "admin":
            abort(403)
    return redirect(url_for(target, **request.args))


@app.get("/api/db")
@admin_required
def api_db():
    """数据库浏览器数据源：全部业务表实时快照。"""
    tables = {}
    with repo.connect() as conn:
        for name in ("questions", "interactions", "knowledge_points", "edges", "favorites", "learner_settings"):
            cols = [row[1] for row in conn.execute(f"PRAGMA table_info({name})")]
            rows_data = [dict(row) for row in conn.execute(f"SELECT * FROM {name}")]
            tables[name] = {"columns": cols, "rows": rows_data}
    return jsonify({"tables": tables})


@app.post("/dataloader/preview")
@admin_required
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
@admin_required
def dataloader_commit():
    token = request.form.get("token", "")
    duplicate_mode = request.form.get("duplicate_mode", "skip")
    result = loader.commit(token, duplicate_mode)
    if result is None:
        return render_template("data.html", points=repo.knowledge_points(), tab="loader",
                               error="加载会话已过期，请重新上传文件")
    return render_template("data.html", points=repo.knowledge_points(), tab="loader", result=result)


@app.get("/dataloader/template/<target>")
@admin_required
def dataloader_template(target):
    if target == "questions":
        csv_text = "id,knowledge_id,title,prompt,choices,answer,explanation,difficulty\n" \
            ",integer,示例题,2 + 3 = ?,5|6|1|0,5,先算加法。,0.30\n"
    elif target == "interactions":
        csv_text = "student_id,question_id,correct,duration_sec,answered_at\n" \
            "demo_student,q01,1,30,\n"
    else:
        abort(404)
    return Response("\ufeff" + csv_text, mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={target}_template.csv"})


if __name__ == "__main__":
    repo.initialize(force_seed=False)
    app.run(host="127.0.0.1", port=5000, debug=False)
