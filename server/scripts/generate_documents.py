"""Generate the editable paper DOCX and defense PPTX from verified project facts."""
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt as PptPt
from pptx.dml.color import RGBColor as PptColor

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

INK = PptColor(27, 36, 48)
CYAN = PptColor(8, 126, 139)
AMBER = PptColor(220, 138, 22)
RED = PptColor(207, 78, 78)
PAPER = PptColor(247, 249, 252)
MUTED = PptColor(100, 116, 139)


def text_box(slide, x, y, w, h, text, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    paragraph = tf.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    run = paragraph.runs[0]
    run.font.name = "Microsoft YaHei"
    run.font.size = PptPt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def rectangle(slide, x, y, w, h, color, radius=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def title(slide, number, heading, subtitle=""):
    rectangle(slide, 0, 0, 13.333, 0.16, CYAN)
    text_box(slide, 0.6, 0.42, 10.8, 0.55, heading, 26, INK, True)
    text_box(slide, 0.62, 0.98, 10.5, 0.32, subtitle, 11, MUTED)
    text_box(slide, 12.1, 7.1, 0.6, 0.22, f"{number:02d}", 10, MUTED, False, PP_ALIGN.RIGHT)


def bullet(slide, x, y, label, detail, accent=CYAN):
    rectangle(slide, x, y + 0.08, 0.12, 0.42, accent)
    text_box(slide, x + 0.26, y, 2.4, 0.35, label, 16, INK, True)
    text_box(slide, x + 0.26, y + 0.38, 3.1, 0.62, detail, 12, MUTED)


def generate_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    slide = prs.slides.add_slide(blank)
    rectangle(slide, 0, 0, 13.333, 7.5, PAPER)
    rectangle(slide, 0, 0, 13.333, 0.2, CYAN)
    text_box(slide, 0.8, 1.35, 9.8, 0.55, "基于知识图谱与遗忘曲线的", 28, INK, True)
    text_box(slide, 0.8, 2.03, 9.8, 0.6, "个性化习题推荐系统", 32, CYAN, True)
    text_box(slide, 0.82, 3.0, 7.9, 0.7, "综合实训项目答辩", 17, MUTED)
    rectangle(slide, 9.75, 1.2, 2.4, 4.5, CYAN, True)
    for i, name in enumerate(["答题事件", "知识图谱", "遗忘门控", "推荐结果"]):
        rectangle(slide, 9.98, 1.55 + i * 0.95, 1.94, 0.58, PAPER, True)
        text_box(slide, 10.08, 1.68 + i * 0.95, 1.72, 0.25, name, 12, CYAN, True, PP_ALIGN.CENTER)
    text_box(slide, 0.82, 5.72, 5.7, 0.3, "Python · SQLite · 知识图谱 · 时序门控模型 · Web", 12, MUTED)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 2, "任务目标与问题界定", "把实训要求拆分为可验证的工程模块")
    bullet(slide, 0.8, 1.7, "学习问题", "固定题单忽略学生基础差异和遗忘节奏。")
    bullet(slide, 4.65, 1.7, "系统目标", "为每名学生推荐下一道最有价值的练习。", AMBER)
    bullet(slide, 8.5, 1.7, "验收要点", "图谱、数据库、时序模型、指标与 Web 展示。", RED)
    rectangle(slide, 0.8, 4.15, 11.7, 1.45, PptColor(230, 242, 244), True)
    text_box(slide, 1.15, 4.48, 11.0, 0.56, "核心原则：推荐结论必须可解释；演示数据与真实数据结论必须严格区分。", 19, INK, True, PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 3, "总体架构", "一次答题如何变成下一题推荐")
    steps = [("Web 答题", 0.75, CYAN), ("SQLite 事件", 3.1, AMBER), ("图谱 + 门控", 5.45, CYAN), ("排序服务", 7.8, AMBER), ("仪表盘", 10.15, CYAN)]
    for label, x, color in steps:
        rectangle(slide, x, 2.6, 1.65, 0.8, color, True); text_box(slide, x + 0.08, 2.86, 1.49, 0.22, label, 14, PAPER, True, PP_ALIGN.CENTER)
    for x in [2.45, 4.8, 7.15, 9.5]:
        text_box(slide, x, 2.83, 0.35, 0.25, "→", 20, MUTED, True, PP_ALIGN.CENTER)
    text_box(slide, 1.3, 4.5, 10.7, 0.65, "模块边界清晰：数据层保存事实，模型层估计状态，服务层排序，界面层解释与交互。", 19, INK, False, PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 4, "知识图谱与数据设计", "前置关系约束学习路径，交互日志提供时序证据")
    nodes = [("整数运算", 1.0, 2.5, CYAN), ("分数运算", 3.2, 2.5, AMBER), ("一元一次方程", 5.55, 2.5, RED), ("一次函数", 8.3, 2.5, CYAN), ("三角形面积", 3.2, 4.45, AMBER)]
    for label, x, y, color in nodes:
        rectangle(slide, x, y, 1.55, 0.65, color, True); text_box(slide, x + 0.04, y + 0.22, 1.47, 0.18, label, 11, PAPER, True, PP_ALIGN.CENTER)
    for x, y in [(2.63,2.68),(4.99,2.68),(7.72,2.68)]: text_box(slide,x,y,0.3,0.2,"→",18,MUTED,True)
    text_box(slide, 8.7, 4.48, 3.1, 0.55, "4 张核心表\n知识点 / 关系 / 习题 / 交互事件", 16, INK, True, PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 5, "时间感知的遗忘门控模型", "输入门、遗忘门、输出门共同更新知识掌握状态")
    rectangle(slide, 0.8, 1.8, 2.3, 2.8, PptColor(230,242,244), True); text_box(slide, 1.02, 2.25, 1.85, 0.28, "事件特征", 18, INK, True, PP_ALIGN.CENTER); text_box(slide, 1.05, 2.83, 1.8, 1.1, "答题正误\n题目难度\n间隔时间\n历史状态", 15, MUTED, False, PP_ALIGN.CENTER)
    text_box(slide, 3.26, 2.9, 0.55, 0.3, "→", 28, MUTED, True)
    rectangle(slide, 3.85, 1.8, 3.0, 2.8, CYAN, True); text_box(slide, 4.15, 2.22, 2.4, 0.3, "LSTM 风格门控单元", 18, PAPER, True, PP_ALIGN.CENTER); text_box(slide, 4.22, 2.92, 2.25, 0.95, "fₜ = σ(Wf·xₜ + b)\ncₜ = fₜcₜ₋₁ + iₜgₜ\nhₜ = oₜtanh(cₜ)", 16, PAPER, False, PP_ALIGN.CENTER)
    text_box(slide, 7.05, 2.9, 0.55, 0.3, "→", 28, MUTED, True)
    rectangle(slide, 7.65, 1.8, 4.4, 2.8, PptColor(254,242,222), True); text_box(slide, 7.98, 2.23, 3.75, 0.3, "掌握度 + 解释信息", 18, INK, True, PP_ALIGN.CENTER); text_box(slide, 8.03, 3.0, 3.65, 0.72, "掌握度：0.02–0.98\n遗忘门值、最近练习间隔\n作为推荐理由的证据", 15, MUTED, False, PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 6, "推荐排序与可解释性", "不只给出题目，也说明“为什么是这道题”")
    text_box(slide, 0.85, 1.65, 5.5, 0.33, "score = 0.56 × 薄弱 + 0.20 × 前置缺口 + 0.12 × 难度 + 0.12 × 图谱匹配", 15, CYAN, True)
    for i, (a,b,c) in enumerate([( "掌握度偏低", "优先巩固当前知识点", RED),("前置知识缺口", "先补基础再进入后继内容", AMBER),("遗忘复习窗口", "间隔较久时主动提醒", CYAN)]):
        y=2.45+i*1.13; rectangle(slide,0.88,y,3.0,0.75,c,True); text_box(slide,1.03,y+0.25,2.7,0.2,a,15,PAPER,True,PP_ALIGN.CENTER); text_box(slide,4.35,y+0.17,5.7,0.4,b,16,INK)
    rectangle(slide, 9.5, 2.1, 2.2, 3.2, PptColor(230,242,244), True); text_box(slide, 9.77,2.45,1.66,0.3,"推荐卡",18,INK,True,PP_ALIGN.CENTER); text_box(slide,9.8,3.1,1.6,1.55,"分数运算\n掌握概率 40%\n弱项邻域匹配 69%\n前置基础待复习\n[开始练习]",13,MUTED,False,PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 7, "Web 系统与数据库落地", "答题、存储、状态更新和展示形成闭环")
    for i,(label,desc,color) in enumerate([( "学习面板", "推荐卡、知识状态图谱", CYAN),("答题页", "单选交互与即时反馈", AMBER),("数据接口", "JSON 仪表盘数据", CYAN),("SQLite", "可追溯事件记录", AMBER)]):
        x=0.85+(i%2)*5.9; y=1.75+(i//2)*2.15; rectangle(slide,x,y,5.1,1.45,PptColor(255,255,255),True); rectangle(slide,x,y,0.14,1.45,color); text_box(slide,x+0.35,y+0.29,2.0,0.25,label,18,INK,True); text_box(slide,x+0.35,y+0.75,3.9,0.22,desc,14,MUTED)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 8, "演示数据上的离线评估", "按时间留出最后 12 条记录；此页不是真实教学效果声明")
    cards=[("Precision@5","0.400",CYAN),("Recall@5","1.000",AMBER),("NDCG@5","0.553",CYAN),("Model Gain","0.029",AMBER)]
    for i,(label,value,color) in enumerate(cards):
        x=0.75+i*3.08; rectangle(slide,x,2.0,2.55,1.6,PptColor(255,255,255),True); rectangle(slide,x,2.0,2.55,0.11,color); text_box(slide,x+0.2,2.43,2.15,0.42,value,26,color,True,PP_ALIGN.CENTER); text_box(slide,x+0.18,3.02,2.2,0.22,label,11,MUTED,False,PP_ALIGN.CENTER)
    rectangle(slide,0.8,4.55,11.65,0.86,PptColor(254,242,222),True); text_box(slide,1.1,4.83,11.0,0.25,"真实实验必须导入经授权 ASSISTments/EdNet 数据，按学生和时间切分后重新训练、对比与报告。",14,INK,True,PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 9, "验收演示流程", "三分钟完成一次可见、可追溯的推荐闭环")
    flow=[("1", "初始化", "生成数据库与演示数据"),("2", "打开面板", "查看推荐与知识状态"),("3", "完成答题", "提交一道推荐练习"),("4", "回到面板", "观察状态和推荐更新")]
    for i,(n,h,d) in enumerate(flow):
        x=0.83+i*3.05; rectangle(slide,x,2.0,2.45,2.45,PptColor(255,255,255),True); text_box(slide,x+0.2,2.26,0.4,0.38,n,25,CYAN,True); text_box(slide,x+0.2,2.95,2.0,0.3,h,18,INK,True); text_box(slide,x+0.2,3.53,2.0,0.45,d,13,MUTED)
        if i<3: text_box(slide,x+2.58,3.03,0.3,0.2,"→",18,MUTED,True)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 10, "四周计划与后续实验", "从可运行原型走向真实数据验证")
    weeks=[("第 1 周","需求、数据调研、图谱设计"),("第 2 周","数据库、模型与原型"),("第 3 周","系统集成、真实数据复现"),("第 4 周","对比实验、论文和答辩")]
    for i,(w,d) in enumerate(weeks):
        x=0.8+i*3.07; rectangle(slide,x,2.2,2.4,1.75,CYAN if i%2==0 else AMBER,True); text_box(slide,x+0.2,2.58,2.0,0.3,w,17,PAPER,True,PP_ALIGN.CENTER); text_box(slide,x+0.22,3.13,1.96,0.4,d,13,PAPER,False,PP_ALIGN.CENTER)
    text_box(slide,0.95,5.1,11.4,0.48,"真实实验补充：训练门控参数、设置随机/正确率/无图谱基线、报告均值与方差、分析误判。",16,INK,False,PP_ALIGN.CENTER)

    slide = prs.slides.add_slide(blank); rectangle(slide, 0, 0, 13.333, 7.5, PAPER); title(slide, 11, "总结", "完成可运行、可解释、可复现实验链路")
    for i, label in enumerate(["知识图谱约束路径", "时间门控估计掌握", "SQLite 保存学习证据", "Web 形成交互闭环"]):
        x=0.95+(i%2)*5.9; y=1.9+(i//2)*1.45; rectangle(slide,x,y,5.2,0.95,PptColor(230,242,244),True); text_box(slide,x+0.28,y+0.31,4.65,0.25,label,17,INK,True,PP_ALIGN.CENTER)
    text_box(slide,1.15,5.35,11.0,0.35,"限制：随附的是透明演示数据。真实教育结论须基于经授权数据和独立实验。",15,RED,True,PP_ALIGN.CENTER)
    text_box(slide,1.15,6.08,11.0,0.3,"谢谢",21,CYAN,True,PP_ALIGN.CENTER)
    prs.save(DOCS / "defense_presentation.pptx")


def add_body(document, text):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.first_line_indent = Cm(0.74)
    paragraph.paragraph_format.line_spacing = 1.5
    run = paragraph.add_run(text)
    run.font.name = "Microsoft YaHei"
    run.font.size = Pt(10.5)


def generate_docx():
    document = Document()
    section = document.sections[0]
    section.top_margin = Cm(2.2); section.bottom_margin = Cm(2.2); section.left_margin = Cm(2.5); section.right_margin = Cm(2.5)
    styles = document.styles
    styles["Normal"].font.name = "Microsoft YaHei"; styles["Normal"].font.size = Pt(10.5)
    p = document.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("综合实训论文"); r.font.name = "Microsoft YaHei"; r.font.size = Pt(22); r.bold = True
    p = document.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("基于知识图谱与遗忘曲线的个性化习题推荐系统"); r.font.name = "Microsoft YaHei"; r.font.size = Pt(18); r.bold = True
    for line in ["专业：通信工程", "课程：专业综合实训", "日期：2026 年 9 月"]:
        p = document.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run(line)
    document.add_page_break()
    sections = [
        ("摘要", "针对统一题单难以适应学生基础差异、复习时机固定的问题，本文设计并实现了一个基于知识图谱与遗忘曲线的个性化习题推荐系统。系统以知识点、前置关系、习题和学习交互事件为核心数据对象，通过 SQLite 建立持久化存储；以知识图谱约束学习路径；使用包含输入门、遗忘门和输出门的时间感知状态更新单元估计学生的知识掌握度；再综合薄弱程度、前置知识缺口和题目难度对候选题排序。系统提供学习仪表盘、答题页、即时反馈和 JSON 数据接口。项目内置确定性演示数据，用于验证完整数据流和离线评估流程。在按时间留出的演示记录上，脚本输出 Precision@5、Recall@5、NDCG@5 等指标。本文明确指出，该数值仅用于功能验证，真实教学效果仍须在经授权的 ASSISTments 或 EdNet 数据上重新训练与检验。"),
        ("关键词", "知识图谱；遗忘曲线；个性化推荐；LSTM；学习分析；Web 系统"),
        ("1 绪论", "在线学习平台通常拥有大量习题，却常以章节顺序或静态难度向所有学生推送同一批题目。这种方式无法反映学习者的前置知识是否扎实，也不能识别刚刚掌握但已长期未复习的内容。遗忘规律表明，学习效果会随着时间间隔衰减；知识图谱则能够表达概念间的依赖关系。因此，将两者用于题目推荐，既能让推荐服务于当前薄弱点，也能够避免学生在基础未掌握时直接进入后继内容。"),
        ("2 需求分析与总体设计", "根据实训要求，系统需要包含知识图谱、数据库、时序记忆增强网络、推荐评价指标和 Web 界面。总体架构分为四层：数据层存储知识点、关系、题目与交互日志；模型层把有序交互转为知识状态；服务层生成可解释推荐；界面层完成展示和答题。这样的划分避免将页面逻辑、数据逻辑与模型逻辑混在一起，便于后续将演示数据替换为真实数据集。"),
        ("3 数据库与知识图谱设计", "系统建立 knowledge_points、edges、questions 和 interactions 四张核心表。knowledge_points 保存概念名称、描述和学习顺序；edges 使用 prerequisite 和 related 两种关系；questions 保存题干、选项、标准答案、解析和难度；interactions 保存学生、题目、所属知识点、正误、答题用时与带时区的作答时间。演示课程包含整数运算、分数运算、一元一次方程、一次函数和三角形面积等知识点，并用前置边形成学习路径。图结构通过纯 PyTorch 实现的 GraphSAGE 风格编码器进行邻域聚合，输出每个知识点的低维嵌入，用于相似性与推荐排序。真实部署时可以由课程大纲或教师标注构建初始图谱，再根据共现关系扩展。"),
        ("4 时间感知掌握度模型", "系统按时间顺序读取学生事件，特征包含答题正误、题目难度、答题用时和时间间隔。TemporalMasteryNet 使用 LSTM 的输入门、遗忘门、输出门更新隐藏状态，并输出全部知识点的掌握概率；时间保留项 exp(-δ·Δt) 对间隔过长的记忆进行衰减。网页同时保留可解释的显式门控回退模型，展示遗忘门、保留率和神经预测概率。"),
        ("5 推荐算法与系统实现", "推荐模块首先排除最近刚完成的题目，再计算候选题分数：0.56 乘知识点薄弱程度，0.20 乘前置知识缺口，0.12 乘题目难度，0.12 乘弱项邻域图谱匹配。图谱匹配由方向感知 GraphSAGE 嵌入与学生弱项上下文余弦相似度、相邻知识点缺口共同得到，因此不是把某一个嵌入维度直接当作关联度。若前置知识缺口较大，页面提示学生先补基础；若距离上次练习较久，则提示进入遗忘复习窗口。Flask 后端提供仪表盘、答题提交、答题结果和 JSON 接口。每次提交均写入 SQLite，重新计算状态并更新下一题，使系统形成闭环。"),
        ("6 实验设计与结果说明", "项目将 demo_student 的 60 条历史交互和最后 12 条交互按时间切分，排序过程只读取此前历史，避免未来信息泄漏。当前脚本输出 Precision@5=0.400、Recall@5=1.000、NDCG@5=0.553、模型估计 Knowledge Gain=0.029；Learning Efficiency 在本留出期没有知识点达到 0.75 阈值，因此报告为未达成。Knowledge Gain 按后测掌握度减前测掌握度计算；这些数字只证明演示数据上的流程可复现，不能替代真实教学因果结论。"),
        ("7 局限性与改进方向", "本项目未随附真实学习日志，因此没有报告真实群体的泛化性能，也未实施统计显著性检验。后续工作包括：取得经授权的 ASSISTments 或 EdNet 数据并脱敏；按学生与时间完成训练、验证和测试切分；以随机推荐、仅按正确率推荐、无图谱推荐作为基线；训练门控网络并比较 Precision、Recall、NDCG、知识掌握度提升率和学习效率；增加教师端图谱维护与学生历史查询。"),
        ("8 结论", "本文完成了一个可运行的个性化习题推荐原型。它用知识图谱表达先修关系，用时间感知门控模型估计掌握度，用可解释排序生成推荐，并用 Web 与数据库把整个过程串联起来。项目将演示结果和真实实验结论明确分开，为后续在真实数据上开展严谨评价保留了可替换、可扩展的实现基础。"),
        ("参考文献", "[1] Corbett A T, Anderson J R. Knowledge tracing: Modeling the acquisition of procedural knowledge. User Modeling and User-Adapted Interaction, 1994.\n[2] Piech C, et al. Deep Knowledge Tracing. NeurIPS, 2015.\n[3] Zhang J, et al. A Survey on Knowledge Graphs: Representation, Acquisition, and Applications. IEEE TNNLS, 2022.\n[4] ASSISTments. https://sites.google.com/site/assistmentsdata/ （访问日期：2026-09-03）\n[5] Choi Y, et al. EdNet: A Large-Scale Hierarchical Dataset in Education. AIED, 2020.")
    ]
    for heading, body in sections:
        h = document.add_heading(heading, level=1)
        for run in h.runs: run.font.name = "Microsoft YaHei"
        for paragraph in body.split("\n"):
            add_body(document, paragraph)
    document.save(DOCS / "training_paper.docx")


if __name__ == "__main__":
    DOCS.mkdir(exist_ok=True)
    generate_docx()
    generate_pptx()
    print("Generated training_paper.docx and defense_presentation.pptx")
