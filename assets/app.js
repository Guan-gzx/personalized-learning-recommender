/* 个性化学习推荐系统 · 纯前端演示
 * 知识图谱 + 遗忘曲线（艾宾浩斯衰减）+ 分层推荐排序，全部在浏览器本地计算。
 * 学习记录保存在 localStorage，可通过侧栏「重置学习数据」清空。
 */
(() => {
  "use strict";

  const POINTS = COURSE_DATA.knowledge_points;
  const EDGES = COURSE_DATA.edges;
  const QUESTIONS = COURSE_DATA.questions;
  const POINT_BY_ID = Object.fromEntries(POINTS.map(p => [p.id, p]));
  const Q_BY_ID = Object.fromEntries(QUESTIONS.map(q => [q.id, q]));
  const POSITIONS = { integer: [18, 52], fractions: [39, 25], equations: [61, 52], functions: [82, 25], geometry: [39, 78] };
  const STORE_KEY = "plr_demo_state_v1";
  const DAY = 86400000;

  /* ---------------- 本地状态 ---------------- */
  const defaultState = () => ({ answers: [], favorites: [], dailyGoal: 5 });
  let state = loadState();
  function loadState() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORE_KEY));
      if (raw && Array.isArray(raw.answers)) return Object.assign(defaultState(), raw);
    } catch (e) { /* 损坏则重置 */ }
    return defaultState();
  }
  function saveState() { localStorage.setItem(STORE_KEY, JSON.stringify(state)); }

  /* ---------------- 掌握度模型（遗忘曲线） ----------------
   * 每个知识点从 0.5 出发；答对按难度加权提升、答错衰减，
   * 再按距最近一次练习的天数做指数遗忘衰减 exp(-0.06·days)。 */
  function masteryMap(now = Date.now()) {
    const byPoint = {};
    for (const p of POINTS) byPoint[p.id] = { value: 0.5, last: null, total: 0, correct: 0 };
    const ordered = [...state.answers].sort((a, b) => a.at - b.at);
    for (const ans of ordered) {
      const m = byPoint[ans.knowledgeId];
      if (!m) continue;
      const q = Q_BY_ID[ans.qid];
      const diff = q ? q.difficulty : 0.5;
      if (ans.correct) m.value += (0.98 - m.value) * 0.22 * (1.25 - diff);
      else m.value -= (m.value - 0.02) * 0.30 * (0.70 + diff);
      m.last = ans.at; m.total += 1; if (ans.correct) m.correct += 1;
    }
    for (const m of Object.values(byPoint)) {
      if (m.last != null) {
        const days = Math.max(0, (now - m.last) / DAY);
        const retention = Math.exp(-days * 0.06);
        m.value = 0.5 + (m.value - 0.5) * retention;
        m.daysSince = days;
      } else m.daysSince = null;
    }
    return byPoint;
  }
  const stateOf = v => (v < 0.55 ? "weak" : v < 0.75 ? "reviewing" : "mastered");
  const stateLabel = v => (v < 0.55 ? "薄弱" : v < 0.75 ? "待复习" : "已掌握");

  /* ---------------- 推荐排序 ---------------- */
  function prerequisitesOf(kpId) {
    return EDGES.filter(e => e.relation === "prerequisite" && e.target_id === kpId).map(e => e.source_id);
  }
  function neighborsOf(kpId) {
    return EDGES.filter(e => e.source_id === kpId || e.target_id === kpId)
      .map(e => (e.source_id === kpId ? e.target_id : e.source_id));
  }
  function recommend(limit = 5, kpId = null, mastery = null) {
    mastery = mastery || masteryMap();
    const recent = [...state.answers].sort((a, b) => b.at - a.at).slice(0, 8).map(a => a.qid);
    const seen = new Set(recent);
    const answered = new Set(state.answers.map(a => a.qid));
    const attemptCounts = {};
    for (const a of state.answers) attemptCounts[a.qid] = (attemptCounts[a.qid] || 0) + 1;
    const scored = [];
    for (const q of QUESTIONS) {
      if (seen.has(q.id)) continue;
      if (kpId && q.knowledge_id !== kpId) continue;
      const m = mastery[q.knowledge_id];
      const weak = 1 - m.value;
      const prereqGap = Math.max(0, ...prerequisitesOf(q.knowledge_id).map(p => 1 - mastery[p].value), 0);
      const affinity = Math.max(0, ...neighborsOf(q.knowledge_id).map(p => 1 - mastery[p].value), 0);
      const novelty = 1 / (1 + (attemptCounts[q.id] || 0));
      const score = 0.46 * weak + 0.16 * prereqGap + 0.10 * q.difficulty + 0.10 * affinity + 0.18 * novelty;
      let reason = "掌握度偏低，需要巩固";
      if (!attemptCounts[q.id]) reason = "新题拓展：尚未练习过，优先尝鲜";
      else if (prereqGap > 0.45) reason = "前置知识存在缺口，建议先复习基础";
      else if (m.daysSince != null && m.daysSince > 5) reason = "距上次练习较久，进入遗忘复习窗口";
      scored.push({ q, score, reason, mastery: m.value, isReview: answered.has(q.id) });
    }
    scored.sort((a, b) => b.score - a.score);
    const diverse = []; const used = new Set();
    for (const item of scored) {
      if (used.has(item.q.knowledge_id)) continue;
      diverse.push(item); used.add(item.q.knowledge_id);
      if (diverse.length >= limit) return diverse;
    }
    for (const item of scored) {
      if (diverse.includes(item)) continue;
      diverse.push(item);
      if (diverse.length >= limit) break;
    }
    return diverse;
  }
  function practiceQuestion(kpId = null) {
    const ranked = recommend(50, kpId);
    return ranked.length ? ranked[0] : null;
  }

  /* ---------------- 每日统计 ---------------- */
  function dailyStats(now = new Date()) {
    const today = now.toISOString().slice(0, 10);
    const days = new Set(state.answers.map(a => new Date(a.at).toISOString().slice(0, 10)));
    let completed = 0;
    for (const a of state.answers) if (new Date(a.at).toISOString().slice(0, 10) === today) completed++;
    let streak = 0; const d = new Date(now);
    while (days.has(d.toISOString().slice(0, 10))) { streak++; d.setDate(d.getDate() - 1); }
    return { completed, streak };
  }

  /* ---------------- 视图工具 ---------------- */
  const view = document.getElementById("view");
  const crumb = document.getElementById("crumb");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fmtTime = ts => {
    const d = new Date(ts);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  };
  function setNav(name) {
    document.querySelectorAll("#side-nav a").forEach(a => a.classList.toggle("active", a.dataset.nav === name));
  }
  const diffDot = d => `<span class="difficulty-dot${d >= 0.52 ? " hard" : ""}">难度 ${Math.round(d * 100)}%</span>`;

  /* ---------------- 仪表盘 ---------------- */
  function renderDashboard() {
    setNav("dashboard"); crumb.textContent = "学习面板";
    const mastery = masteryMap();
    const recos = recommend(5);
    const { completed, streak } = dailyStats();
    const goal = state.dailyGoal;
    const progress = Math.min(100, Math.round(completed / goal * 100));
    const avg = Math.round(Object.values(mastery).reduce((s, m) => s + m.value, 0) / POINTS.length * 100);
    const answeredCount = new Set(state.answers.map(a => a.qid)).size;
    const wrongCount = state.answers.filter(a => !a.correct).length;

    const recoCards = recos.map((r, i) => `
      <a class="reco-item" href="#/study/${r.q.id}?total=5&step=1&kp=${encodeURIComponent(r.kp || "")}">
        <span class="reco-rank">${i + 1}</span>
        <div><h3>${esc(r.q.title)} · ${esc(POINT_BY_ID[r.q.knowledge_id].name)}</h3>
        <div class="why">${esc(r.reason)} <b>弱项匹配 ${(r.score * 100).toFixed(0)}%</b>${r.isReview ? " · 复练" : ""}</div></div>
        <div class="reco-meta"><strong>${Math.round(r.mastery * 100)}%</strong>当前掌握</div>
      </a>`).join("");

    const nodesSvg = POINTS.map(p => {
      const m = mastery[p.id];
      const [x, y] = POSITIONS[p.id] || [50, 50];
      const st = stateOf(m.value);
      const hl = recos.some(r => r.q.knowledge_id === p.id);
      return `<g class="star-node ${st}${hl ? " highlight" : ""}" data-kp="${p.id}" tabindex="0" role="link" aria-label="${esc(p.name)}">
        <circle class="halo" cx="${x}" cy="${y}" r="6.4"></circle>
        <circle class="core" cx="${x}" cy="${y}" r="3.1"></circle>
        <text x="${x}" y="${y + 6.8}">${esc(p.name)}</text>
        <text class="star-value" x="${x}" y="${y + 9.6}">${Math.round(m.value * 100)}% · ${stateLabel(m.value)}</text>
      </g>`;
    }).join("");
    const linksSvg = EDGES.map(e => {
      const a = POSITIONS[e.source_id], b = POSITIONS[e.target_id];
      return `<line class="star-link${e.relation === "related" ? " related" : ""}" x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"></line>`;
    }).join("");

    const signalBars = POINTS.map(p => {
      const m = mastery[p.id];
      return `<div class="signal-item"><span>${esc(p.name)}</span><i><b style="width:${Math.round(m.value * 100)}%"></b></i><strong>${Math.round(m.value * 100)}%</strong></div>`;
    }).join("");

    view.innerHTML = `
      <section class="daily-plan">
        <div class="daily-plan-copy"><span class="daily-icon">◎</span>
          <div><p class="eyebrow">TODAY'S FOCUS</p>
          <h2>完成 ${goal} 道题，保持学习节奏</h2>
          <p class="sub">${completed} / ${goal} 已完成 · ${streak ? `已连续学习 ${streak} 天` : "从第一题开始积累连续学习"}</p></div>
        </div>
        <div class="daily-progress"><div class="daily-ring" style="--progress:${progress}"><strong>${progress}%</strong></div>
          <form class="goal-form"><label for="daily-goal">目标</label>
          <select id="daily-goal">${[3, 5, 8, 10].map(g => `<option value="${g}" ${g === goal ? "selected" : ""}>${g} 道</option>`).join("")}</select></form>
        </div>
        <form class="session-launch" id="session-launch">
          <label>连续练习<select id="session-total"><option value="3">3 题</option><option value="5" selected>5 题</option><option value="8">8 题</option></select></label>
          <button class="button primary" type="submit">开始计划 <span>→</span></button>
        </form>
      </section>
      <section class="summary-strip">
        <a href="#/practice"><span class="summary-icon cyan">✦</span><div><small>今日建议</small><strong>${recos.length} 道练习</strong></div></a>
        <a href="#/library"><span class="summary-icon violet">▤</span><div><small>已练题目</small><strong>${answeredCount} / ${QUESTIONS.length} 题</strong></div></a>
        <a href="#/mistakes"><span class="summary-icon amber">↺</span><div><small>待巩固错题</small><strong>${wrongCount} 次</strong></div></a>
        <div class="card"><span class="summary-icon green">◉</span><div><small>平均掌握度</small><strong>${avg}%</strong></div></div>
      </section>
      <div class="dash-grid">
        <div class="panel"><h2>智能推荐 · 为你而选</h2>
          <p class="sub">排序 = 0.56×薄弱程度 + 0.20×前置缺口 + 0.12×题目难度 + 0.12×图谱关联（图谱邻域 + 遗忘窗口实时计算）</p>
          <div class="reco-list">${recoCards}</div>
          <div class="model-explainer">
            <div><h2>推荐引擎如何工作</h2>
            <p>每个知识点的掌握度随答题结果更新，并按艾宾浩斯遗忘曲线随时间衰减（exp(-0.06·天数)）。推荐分数综合薄弱程度、前置知识缺口、图谱邻域关联与题目难度，且自动排除最近 8 道做过的题。</p></div>
            <div class="model-facts">
              <span><b>${QUESTIONS.length}</b>分层题库</span>
              <span><b>${POINTS.length}</b>知识图谱节点</span>
              <span><b>${EDGES.length}</b>前置/关联边</span>
              <span><b>0.06</b>遗忘衰减系数</span>
            </div>
          </div>
        </div>
        <div class="panel"><h2>知识星空图</h2>
          <p class="sub">节点亮度 = 掌握度 · 光环 = 当前推荐 · 点击节点查看详情</p>
          <div class="star-map">
            <svg viewBox="0 0 100 100" role="img" aria-label="知识图谱星空图">${linksSvg}${nodesSvg}</svg>
            <div class="star-legend">
              <span><i class="legend-dot weak"></i>薄弱(&lt;55%)</span>
              <span><i class="legend-dot reviewing"></i>待复习(&lt;75%)</span>
              <span><i class="legend-dot mastered"></i>已掌握(≥75%)</span>
            </div>
          </div>
          <div class="signal-bars">${signalBars}</div>
        </div>
      </div>`;

    document.getElementById("daily-goal").addEventListener("change", e => {
      state.dailyGoal = parseInt(e.target.value, 10); saveState(); renderDashboard();
    });
    document.getElementById("session-launch").addEventListener("submit", e => {
      e.preventDefault();
      const total = document.getElementById("session-total").value;
      location.hash = `#/practice?total=${total}`;
    });
    view.querySelectorAll(".star-node").forEach(n => {
      const go = () => { location.hash = `#/knowledge/${n.dataset.kp}`; };
      n.addEventListener("click", go);
      n.addEventListener("keydown", ev => { if (ev.key === "Enter") go(); });
    });
  }

  /* ---------------- 练习会话 ---------------- */
  let session = null; // { total, step, kp }
  function renderPractice(query) {
    setNav("practice"); crumb.textContent = "智能练习";
    const total = clampInt(query.total, 5, 1, 20);
    const step = clampInt(query.step, 1, 1, total);
    const kp = query.kp || null;
    session = { total, step, kp };
    const pick = practiceQuestion(kp);
    if (!pick) { view.innerHTML = emptyBox("暂无可推荐题目", "当前筛选条件下没有更多题目，去题库逛逛吧。", "#/library"); return; }
    location.hash = `#/study/${pick.q.id}?total=${total}&step=${step}&kp=${encodeURIComponent(kp || "")}`;
  }
  function clampInt(v, d, min, max) { const n = parseInt(v, 10); return isNaN(n) ? d : Math.max(min, Math.min(max, n)); }

  function renderStudy(qid, query) {
    setNav("practice"); crumb.textContent = "连续练习";
    const q = Q_BY_ID[qid];
    if (!q) { render404(); return; }
    const total = clampInt(query.total, 1, 1, 20);
    const step = clampInt(query.step, 1, 1, total);
    const kp = query.kp || "";
    const fav = state.favorites.includes(q.id);
    const choices = q.choices.map((c, i) => `
      <label class="choice"><input required type="radio" name="answer" value="${esc(c)}">
      <span class="choice-key">${"ABCD"[i]}</span><span>${esc(c)}</span></label>`).join("");
    view.innerHTML = `
      <div class="study-shell"><a class="back-link" href="#/">← 返回学习面板</a>
      ${total > 1 ? `<div class="session-status"><span>连续练习</span><strong>第 ${step} / ${total} 题</strong>
        <div class="session-track"><i style="width:${Math.round((step - 1) / total * 100)}%"></i></div></div>` : ""}
      <section class="study">
        <div class="study-top">
          <a class="tag" href="#/knowledge/${q.knowledge_id}">${esc(POINT_BY_ID[q.knowledge_id].name)}</a>
          <div style="display:flex;gap:9px;align-items:center">
            <span class="difficulty">难度 ${Math.round(q.difficulty * 100)}%</span>
            <button class="favorite-btn" id="fav-btn" aria-label="收藏题目">${fav ? "★" : "☆"}</button>
          </div>
        </div>
        <h1>${esc(q.title)}</h1><p class="prompt">${esc(q.prompt)}</p>
        <form id="answer-form">${choices}
          <button class="button primary submit-btn" type="submit">提交答案 <span>→</span></button>
        </form>
      </section></div>`;
    document.getElementById("fav-btn").addEventListener("click", () => toggleFavorite(q.id, () => renderStudy(qid, query)));
    const startedAt = Date.now();
    document.getElementById("answer-form").addEventListener("submit", e => {
      e.preventDefault();
      const answer = new FormData(e.target).get("answer");
      if (!answer) return;
      const durationSec = Math.round((Date.now() - startedAt) / 100) / 10;
      const correct = answer === q.answer;
      state.answers.push({ qid: q.id, correct, knowledgeId: q.knowledge_id, at: Date.now(), durationSec });
      saveState();
      location.hash = `#/result/${q.id}?correct=${correct ? 1 : 0}&total=${total}&step=${step}&kp=${encodeURIComponent(kp)}`;
    });
  }

  function renderResult(qid, query) {
    setNav("practice"); crumb.textContent = "答题回顾";
    const q = Q_BY_ID[qid];
    if (!q) { render404(); return; }
    const total = clampInt(query.total, 1, 1, 20);
    const step = clampInt(query.step, 1, 1, total);
    const kp = query.kp || "";
    const correct = query.correct === "1";
    const finished = step >= total;
    const next = finished ? null : practiceQuestion(kp || null);
    view.innerHTML = `
      <div class="study-shell">
      <section class="study result-card ${correct ? "success" : "retry"}">
        <div class="result-icon">${correct ? "✓" : "!"}</div>
        <p class="eyebrow">ANSWER REVIEW${total > 1 ? ` · ${step}/${total}` : ""}</p>
        <h1>${finished && total > 1 ? "本轮练习完成" : correct ? "回答正确" : "再想一想"}</h1>
        <p class="prompt"><b>正确答案：${esc(q.answer)}</b><br>${esc(q.explanation)}</p>
        <p class="muted">本次学习记录已写入本地，掌握度与下一题推荐已重新计算。</p>
        <div class="result-actions">
          ${next ? `<a class="button primary" href="#/study/${next.q.id}?total=${total}&step=${step + 1}&kp=${encodeURIComponent(kp)}">继续第 ${step + 1} 题 →</a>` : ""}
          ${finished && total > 1 ? `<a class="button primary" href="#/">查看今日进度 →</a>` : ""}
          ${!finished && !next ? `<a class="button primary" href="#/library">去题库自选 →</a>` : ""}
          <a class="button ghost" href="#/">返回面板</a>
        </div>
      </section></div>`;
  }

  /* ---------------- 题库 ---------------- */
  function renderLibrary(query) {
    setNav("library"); crumb.textContent = "题库";
    const kp = query.kp || "";
    const level = query.level || "";
    const kw = (query.q || "").trim().toLowerCase();
    const favOnly = query.favorites === "1";
    const answered = new Map(state.answers.map(a => [a.qid, a]));
    const list = QUESTIONS.filter(q => {
      if (kp && q.knowledge_id !== kp) return false;
      if (level === "basic" && q.difficulty > 0.42) return false;
      if (level === "advanced" && q.difficulty < 0.52) return false;
      if (kw && !(q.title + q.prompt).toLowerCase().includes(kw)) return false;
      if (favOnly && !state.favorites.includes(q.id)) return false;
      return true;
    });
    const cards = list.map(q => {
      const ev = answered.get(q.id);
      const status = !ev ? `<span class="status-label">未作答</span>`
        : ev.correct ? `<span class="status-label done">✓ 正确</span>` : `<span class="status-label wrong">✗ 出错</span>`;
      return `<article class="question-card">
        <div class="card-top"><a class="tag" href="#/knowledge/${q.knowledge_id}">${esc(POINT_BY_ID[q.knowledge_id].name)}</a>${diffDot(q.difficulty)}</div>
        <h3>${esc(q.title)}</h3><p>${esc(q.prompt)}</p>
        <div class="card-footer">
          <button class="favorite-btn" data-fav="${q.id}">${state.favorites.includes(q.id) ? "★" : "☆"}</button>
          ${status}
          <div class="card-actions"><a class="button ghost" style="padding:8px 13px;font-size:12px" href="#/study/${q.id}">去作答 →</a></div>
        </div></article>`;
    }).join("");
    view.innerHTML = `
      <div class="page-title"><div><h1>题库</h1>
        <p>共 ${QUESTIONS.length} 道分层练习 · ${POINTS.length} 个知识点 · 每个知识点 20 题</p></div>
        <a class="button" href="#/practice">开始智能练习</a></div>
      <form class="filterbar" id="lib-filter">
        <input class="search-input" name="q" placeholder="搜索题目关键词…" value="${esc(query.q || "")}">
        <select name="kp"><option value="">全部知识点</option>
          ${POINTS.map(p => `<option value="${p.id}" ${kp === p.id ? "selected" : ""}>${esc(p.name)}</option>`).join("")}</select>
        <select name="level"><option value="">全部难度</option>
          <option value="basic" ${level === "basic" ? "selected" : ""}>基础</option>
          <option value="advanced" ${level === "advanced" ? "selected" : ""}>进阶</option></select>
        <label class="check-filter"><input type="checkbox" name="favorites" value="1" ${favOnly ? "checked" : ""}>只看收藏</label>
        <button class="button ghost" type="submit">筛选</button>
      </form>
      <div class="library-grid">${cards || emptyBox("没有匹配的题目", "换个关键词或放宽筛选条件试试。")}</div>`;
    document.getElementById("lib-filter").addEventListener("submit", e => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const params = new URLSearchParams();
      for (const [k, v] of fd.entries()) if (v) params.set(k, v);
      location.hash = `#/library?${params.toString()}`;
    });
    view.querySelectorAll("[data-fav]").forEach(btn =>
      btn.addEventListener("click", () => toggleFavorite(btn.dataset.fav, () => renderLibrary(query))));
  }
  const emptyBox = (title, sub, link) => `
    <div class="empty-state"><strong>${esc(title)}</strong>${esc(sub)}${link ? `<br><br><a class="button" href="${link}">去看看</a>` : ""}</div>`;

  function toggleFavorite(qid, rerender) {
    const i = state.favorites.indexOf(qid);
    if (i >= 0) state.favorites.splice(i, 1); else state.favorites.push(qid);
    saveState(); if (rerender) rerender();
  }

  /* ---------------- 学习记录 / 错题本 ---------------- */
  function renderHistory() {
    setNav("history"); crumb.textContent = "学习记录";
    const rows = [...state.answers].sort((a, b) => b.at - a.at).map(a => {
      const q = Q_BY_ID[a.qid];
      return `<div class="history-row">
        <span class="history-badge ${a.correct ? "ok" : "no"}">${a.correct ? "✓" : "✗"}</span>
        <div><h3>${esc(q ? q.title : a.qid)} · ${esc(POINT_BY_ID[a.knowledgeId]?.name || "")}</h3>
        <small>${fmtTime(a.at)} · 用时 ${a.durationSec || 0}s</small></div>
        <a class="history-result" href="#/study/${a.qid}">再练一次 →</a></div>`;
    }).join("");
    view.innerHTML = `<div class="page-title"><div><h1>学习记录</h1>
      <p>共 ${state.answers.length} 次作答 · 答对 ${state.answers.filter(a => a.correct).length} 次</p></div></div>
      <div class="timeline">${rows || emptyBox("还没有学习记录", "从智能练习开始你的第一题吧。", "#/practice")}</div>`;
  }

  function renderMistakes() {
    setNav("mistakes"); crumb.textContent = "错题本";
    const wrong = new Map();
    for (const a of [...state.answers].sort((a, b) => a.at - b.at)) if (!a.correct) wrong.set(a.qid, a);
    const cards = [...wrong.values()].map(a => {
      const q = Q_BY_ID[a.qid];
      return `<article class="mistake-card">
        <div class="card-top"><a class="tag" href="#/knowledge/${a.knowledgeId}">${esc(POINT_BY_ID[a.knowledgeId]?.name || "")}</a>${diffDot(q.difficulty)}</div>
        <h3>${esc(q.title)}</h3><p>${esc(q.prompt)}</p>
        <div class="fix"><b>正确答案：${esc(q.answer)}</b><br>${esc(q.explanation)}</div>
        <div class="card-footer"><small class="muted">${fmtTime(a.at)}</small>
        <a class="button ghost" style="padding:8px 13px;font-size:12px" href="#/study/${a.qid}">再练一次 →</a></div>
      </article>`;
    }).join("");
    view.innerHTML = `<div class="page-title"><div><h1>错题本</h1>
      <p>共 ${wrong.size} 道待巩固 · 答错后掌握度自动下调，推荐引擎会优先安排复练</p></div></div>
      <div class="mistake-grid">${cards || emptyBox("太棒了，暂无错题！", "继续保持，或去题库挑战进阶难度。", "#/library")}</div>`;
  }

  /* ---------------- 知识点详情 ---------------- */
  function renderKnowledge(kpId) {
    const p = POINT_BY_ID[kpId];
    if (!p) { render404(); return; }
    setNav("library"); crumb.textContent = `知识点 · ${p.name}`;
    const mastery = masteryMap();
    const m = mastery[kpId];
    const related = EDGES.filter(e => e.source_id === kpId || e.target_id === kpId)
      .map(e => ({ other: e.source_id === kpId ? e.target_id : e.source_id, relation: e.relation === "prerequisite" ? (e.target_id === kpId ? "前置知识" : "后继知识") : "关联知识" }));
    const answeredIds = new Set(state.answers.filter(a => a.knowledgeId === kpId).map(a => a.qid));
    const qs = QUESTIONS.filter(q => q.knowledge_id === kpId);
    const miniCards = qs.map(q => `<a class="mini-q" href="#/study/${q.id}">
      <h4>${esc(q.title)}</h4>
      <small>${answeredIds.has(q.id) ? "已练" : "未练"} · 难度 ${Math.round(q.difficulty * 100)}%</small></a>`).join("");
    view.innerHTML = `
      <a class="back-link" href="#/">← 返回学习面板</a>
      <div class="detail-head">
        <div class="knowledge-score" style="--p:${Math.round(m.value * 100)}"><strong>${Math.round(m.value * 100)}%</strong></div>
        <div style="flex:1;min-width:220px"><h1>${esc(p.name)}</h1><p class="sub">${esc(p.description)} · 当前状态：${stateLabel(m.value)}</p>
          <div class="detail-stats">
            <div><small>已练题数</small><b>${answeredIds.size} / ${qs.length}</b></div>
            <div><small>作答次数</small><b>${m.total}</b></div>
            <div><small>正确率</small><b>${m.total ? Math.round(m.correct / m.total * 100) + "%" : "—"}</b></div>
            <div><small>距上次练习</small><b>${m.daysSince == null ? "—" : m.daysSince < 1 ? Math.round(m.daysSince * 24) + " 小时" : Math.round(m.daysSince) + " 天"}</b></div>
          </div>
          <div class="related-chips">${related.map(r => `<a class="tag" href="#/knowledge/${r.other}">${esc(POINT_BY_ID[r.other].name)} · ${r.relation}</a>`).join("") || '<span class="tag">图谱叶子节点</span>'}</div>
        </div>
        <a class="button" href="#/practice?total=5&kp=${kpId}">专项练习 →</a>
      </div>
      <div class="detail-grid">${miniCards}</div>`;
  }

  function render404() {
    view.innerHTML = emptyBox("页面不存在", "链接可能已过期，回面板重新出发。", "#/");
  }

  /* ---------------- 路由 ---------------- */
  function parseHash() {
    const raw = location.hash.replace(/^#\/?/, "");
    const [path, qs] = raw.split("?");
    const query = {};
    new URLSearchParams(qs || "").forEach((v, k) => { query[k] = v; });
    return { segs: path.split("/").filter(Boolean), query };
  }
  function router() {
    const { segs, query } = parseHash();
    const [root, arg] = segs;
    window.scrollTo(0, 0);
    if (!root) return renderDashboard();
    if (root === "library") return renderLibrary(query);
    if (root === "history") return renderHistory();
    if (root === "mistakes") return renderMistakes();
    if (root === "practice") return renderPractice(query);
    if (root === "study" && arg) return renderStudy(arg, query);
    if (root === "result" && arg) return renderResult(arg, query);
    if (root === "knowledge" && arg) return renderKnowledge(arg);
    render404();
  }
  window.addEventListener("hashchange", router);

  document.getElementById("reset-btn").addEventListener("click", () => {
    if (confirm("确定清空本地学习记录？掌握度、收藏和练习历史将全部重置。")) {
      state = defaultState(); saveState(); location.hash = "#/"; router();
    }
  });
  router();
})();
