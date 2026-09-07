# 个性化学习推荐系统 · Personalized Learning Recommender

基于**知识图谱**与**遗忘曲线**的个性化练习推荐系统（Task 16 交付项目）。

> 🌐 **在线演示（GitHub Pages）**：纯前端版本，含 100 道分层练习、智能推荐、知识星空图、错题本，学习数据保存在浏览器 localStorage 中。

## 功能特性

- **智能推荐**：排序分数 = `0.56×薄弱程度 + 0.20×前置知识缺口 + 0.12×题目难度 + 0.12×图谱关联度`，自动排除最近做过的题目，保证练习多样性
- **遗忘曲线建模**：每个知识点的掌握度随答题结果更新，并按艾宾浩斯遗忘曲线 `exp(-0.06·天数)` 随时间衰减，久未练习会进入"遗忘复习窗口"
- **知识星空图**：可交互的知识图谱可视化，节点亮度编码掌握度，光环标记当前推荐知识点，点击进入专项详情
- **100 道分层题库**：5 个知识点（整数运算 / 分数运算 / 一元一次方程 / 一次函数 / 三角形面积）各 20 题，支持关键词、难度、收藏筛选
- **完整学习闭环**：连续练习（3/5/8 题）、每日目标与连续学习天数、学习记录、错题本、知识点画像
- **图谱感知**：4 条前置/关联边驱动"前置知识缺口"检测——先修概念薄弱时优先推荐基础题

## 仓库结构

```
├── index.html          # 在线演示（纯前端 SPA，GitHub Pages 托管）
├── assets/             # 演示站样式、逻辑与题库数据
├── server/             # 完整后端源码（Flask + SQLite + PyTorch）
│   ├── app.py          #   Web 应用入口
│   ├── recommender/    #   仓储层、GraphSAGE 式图谱编码器、LSTM 遗忘门控模型
│   ├── scripts/        #   初始化、评估、导入、训练脚本
│   ├── templates/      #   Jinja2 模板
│   └── data/           #   确定性演示课程数据
└── docs/               # 训练论文、答辩 PPT、验证记录等文档
```

## 运行完整后端（可选）

演示站为纯前端版本；如需体验可训练的深度模型（GraphSAGE 式图谱编码 + LSTM 时间遗忘门控），运行完整 Flask 后端：

```bash
cd server
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
python app.py                    # http://127.0.0.1:5000
```

离线评估（严格按时间切分，无未来信息泄漏）：

```bash
python scripts/evaluate.py       # Precision@5 / Recall@5 / NDCG@5 / Knowledge Gain
python scripts/train_models.py   # 训练 LSTM 检查点（CPU 即可）
```

## 数据与结论边界

随代码提供的演示数据为确定性种子数据，用于验证数据流与功能闭环，不能表述为真实班级或 ASSISTments/EdNet 数据集的实验结果。详见 [`docs/data_and_claims.md`](docs/data_and_claims.md)。

## 技术栈

| 层 | 技术 |
|---|---|
| 在线演示 | 原生 HTML / CSS / JavaScript（零依赖，localStorage 持久化） |
| 后端 | Flask + SQLite |
| 模型 | PyTorch（GraphSAGE 式方向感知图谱编码器、时间感知 LSTM 知识追踪） |
| 评估 | Precision@K / Recall@K / NDCG@K / Knowledge Gain / Learning Efficiency |
