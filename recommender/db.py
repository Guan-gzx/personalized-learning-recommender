import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Repository:
    def __init__(self, path: Path):
        self.path = path

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self, force_seed=False):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS knowledge_points (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, ordinal INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS edges (
                    source_id TEXT NOT NULL, target_id TEXT NOT NULL, relation TEXT NOT NULL,
                    PRIMARY KEY (source_id, target_id, relation)
                );
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY, knowledge_id TEXT NOT NULL, title TEXT NOT NULL, prompt TEXT NOT NULL,
                    choices TEXT NOT NULL, answer TEXT NOT NULL, explanation TEXT NOT NULL, difficulty REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL, knowledge_id TEXT NOT NULL,
                    question_id TEXT NOT NULL, correct INTEGER NOT NULL, duration_sec REAL NOT NULL DEFAULT 0, answered_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS favorites (
                    student_id TEXT NOT NULL, question_id TEXT NOT NULL, created_at TEXT NOT NULL,
                    PRIMARY KEY (student_id, question_id)
                );
                CREATE TABLE IF NOT EXISTS learner_settings (
                    student_id TEXT PRIMARY KEY, daily_goal INTEGER NOT NULL DEFAULT 5,
                    updated_at TEXT NOT NULL
                );
                """
            )
            exists = conn.execute("SELECT COUNT(*) FROM knowledge_points").fetchone()[0]
            columns = {row[1] for row in conn.execute("PRAGMA table_info(interactions)").fetchall()}
            if "duration_sec" not in columns:
                conn.execute("ALTER TABLE interactions ADD COLUMN duration_sec REAL NOT NULL DEFAULT 0")
            if not exists or force_seed:
                if force_seed:
                    conn.execute("DELETE FROM interactions")
                    conn.execute("DELETE FROM questions")
                    conn.execute("DELETE FROM edges")
                    conn.execute("DELETE FROM knowledge_points")
                    conn.execute("DELETE FROM favorites")
                self._seed(conn)

    def _seed(self, conn):
        seed_path = self.path.parent / "demo_course.json"
        data = json.loads(seed_path.read_text(encoding="utf-8"))
        conn.executemany(
            "INSERT INTO knowledge_points VALUES (:id, :name, :description, :ordinal)", data["knowledge_points"]
        )
        conn.executemany("INSERT INTO edges VALUES (:source_id, :target_id, :relation)", data["edges"])
        data["questions"] = self._expand_questions(data["questions"])
        for question in data["questions"]:
            question["choices"] = json.dumps(question["choices"], ensure_ascii=False)
        conn.executemany(
            """INSERT INTO questions VALUES (:id, :knowledge_id, :title, :prompt, :choices,
               :answer, :explanation, :difficulty)""", data["questions"]
        )
        # Anchor the demo log relative to seeding time so the final event sits
        # two days in the past; every seeded timestamp then stays earlier than
        # any new learner answer recorded at "now".
        now = datetime.now(timezone.utc)
        base = now - timedelta(hours=9 * 71) - timedelta(days=2)
        events = []
        for index in range(72):
            question = data["questions"][index % len(data["questions"])]
            # The deterministic pattern creates both learned and weak concepts for demonstration.
            correct = int((index * 7 + question["difficulty"] * 10) % 5 != 0)
            if question["knowledge_id"] in {"fractions", "equations"} and index % 4 == 0:
                correct = 0
            duration_sec = 22 + ((index * 13) % 75)
            events.append(("demo_student", question["knowledge_id"], question["id"], correct, duration_sec,
                           (base + timedelta(hours=index * 9)).isoformat()))
        conn.executemany(
            "INSERT INTO interactions (student_id, knowledge_id, question_id, correct, duration_sec, answered_at) VALUES (?, ?, ?, ?, ?, ?)",
            events,
        )

    @staticmethod
    def _expand_questions(base):
        """Provide a substantial, varied local question bank for continuous practice."""
        extra = [
            ("integer", "整数减法", "15 - 23 的结果是？", ["-8", "8", "-38", "38"], "-8", "减去更大的数，结果为负数。", .28),
            ("integer", "绝对值", "|-9| + |4| 的结果是？", ["-5", "5", "13", "-13"], "13", "绝对值表示到零点的距离。", .32),
            ("integer", "混合运算", "-3 + 5 × 2 的结果是？", ["4", "7", "-4", "-13"], "7", "先乘除后加减，5×2=10。", .43),
            ("integer", "整数除法", "(-36) ÷ 9 的结果是？", ["-4", "4", "-27", "27"], "-4", "异号相除为负。", .35),
            ("integer", "相反数", "-12 的相反数是？", ["-12", "12", "0", "1/12"], "12", "只有符号相反的两个数互为相反数。", .22),
            ("integer", "数轴比较", "下列数中最小的是？", ["-5", "-2", "0", "3"], "-5", "数轴上越靠左的数越小。", .30),
            ("integer", "括号运算", "8 - (-6) 的结果是？", ["2", "-2", "14", "-14"], "14", "减去一个负数等于加上它的相反数。", .40),
            ("integer", "整数平方", "(-5)² 的结果是？", ["-25", "25", "-10", "10"], "25", "负数的平方为正数。", .34),
            ("fractions", "分数约分", "12/18 化成最简分数是？", ["2/3", "3/2", "6/9", "4/6"], "2/3", "分子分母同时除以最大公因数 6。", .38),
            ("fractions", "分数减法", "7/10 - 3/10 的结果是？", ["4/20", "4/10", "3/10", "1"], "4/10", "同分母分数相减，分母不变。", .36),
            ("fractions", "分数乘法", "2/3 × 3/5 的结果是？", ["6/15", "2/5", "5/2", "1"], "2/5", "分子乘分子、分母乘分母后约分。", .50),
            ("fractions", "分数除法", "3/4 ÷ 1/2 的结果是？", ["3/8", "3/2", "2/3", "1/2"], "3/2", "除以一个分数等于乘它的倒数。", .62),
            ("fractions", "通分", "1/4 和 1/6 的最小公分母是？", ["10", "12", "24", "2"], "12", "4 和 6 的最小公倍数是 12。", .42),
            ("fractions", "带分数", "1 又 1/2 化成假分数是？", ["2/3", "3/2", "1/2", "5/2"], "3/2", "整数部分乘分母再加分子。", .45),
            ("fractions", "实际应用", "一根绳子长 3/4 米，用去 1/4 米，还剩？", ["1/2 米", "2/4 米", "1/4 米", "1 米"], "1/2 米", "3/4-1/4=2/4=1/2。", .48),
            ("fractions", "分数比较", "下列分数中最大的是？", ["1/2", "2/3", "3/5", "5/8"], "2/3", "可通分或化为小数比较。", .52),
            ("equations", "移项求解", "解方程 5x - 7 = 18，x = ?", ["3", "5", "7", "25"], "5", "两边加 7 后再除以 5。", .42),
            ("equations", "系数为负", "解方程 -2x = 14，x = ?", ["7", "-7", "12", "-12"], "-7", "两边同时除以 -2。", .40),
            ("equations", "分配律", "解方程 3(x + 2)=21，x = ?", ["5", "7", "9", "1"], "5", "先除以 3，再减 2。", .56),
            ("equations", "含分数方程", "x/4 = 3，x = ?", ["3/4", "7", "12", "1"], "12", "两边同乘 4。", .39),
            ("equations", "实际问题", "某数的 3 倍减 4 等于 20，这个数是？", ["8", "6", "24", "16"], "8", "列式 3x-4=20。", .55),
            ("equations", "两边含未知数", "解方程 4x + 3 = 2x + 13，x = ?", ["5", "8", "10", "-5"], "5", "移项得 2x=10。", .66),
            ("equations", "去括号", "解方程 2(x+1)-3=7，x = ?", ["3", "4", "5", "6"], "4", "去括号并合并同类项。", .70),
            ("equations", "等式性质", "方程两边同时乘同一个非零数，解集会？", ["不变", "扩大", "缩小", "消失"], "不变", "等式两边进行同样的非零运算，解不变。", .35),
            ("functions", "一次函数图像", "函数 y=3x-2 的纵截距是？", ["3", "-2", "2", "0"], "-2", "y=kx+b 中 b 为纵截距。", .43),
            ("functions", "函数代入", "y=-x+5，当 x=-2 时 y = ?", ["-7", "3", "5", "7"], "7", "代入得 -(-2)+5=7。", .40),
            ("functions", "点在直线", "点 (2,5) 是否在 y=2x+1 上？", ["是", "否", "无法判断", "只在 x>0 时是"], "是", "x=2 时 y=5。", .45),
            ("functions", "变化率", "y=-4x+6 中，x 每增加 1，y 如何变化？", ["增加 4", "减少 4", "增加 6", "不变"], "减少 4", "斜率为 -4。", .52),
            ("functions", "零点", "y=2x-8 的零点横坐标是？", ["-4", "4", "8", "-8"], "4", "令 y=0，解 2x-8=0。", .56),
            ("functions", "平行关系", "与 y=3x+1 平行的直线斜率可能是？", ["3", "1", "-3", "0"], "3", "平行直线斜率相同。", .50),
            ("functions", "比例判断", "下列哪一个是一次函数？", ["y=2x-1", "y=x²", "y=1/x", "y=2"], "y=2x-1", "一次函数形式为 y=kx+b。", .44),
            ("functions", "交点求解", "y=x+1 与 y=5 的交点横坐标是？", ["1", "4", "5", "6"], "4", "令 x+1=5。", .60),
            ("geometry", "面积单位", "三角形底 10 cm、高 4 cm，面积是？", ["14 cm²", "20 cm²", "40 cm²", "80 cm²"], "20 cm²", "面积=10×4÷2。", .30),
            ("geometry", "等底等高", "两个三角形底和高都相等，它们的面积？", ["相等", "不一定", "相差一倍", "无法比较"], "相等", "面积由底和高唯一决定。", .28),
            ("geometry", "面积反求底", "三角形面积 30 cm²、高 5 cm，底是？", ["6 cm", "12 cm", "15 cm", "25 cm"], "12 cm", "底=2×面积÷高。", .50),
            ("geometry", "直角三角形", "直角三角形两直角边为 6 cm、8 cm，面积是？", ["14 cm²", "24 cm²", "48 cm²", "28 cm²"], "24 cm²", "任选一条直角边作底，另一条作高。", .43),
            ("geometry", "面积变化", "三角形底不变，高变为原来的 2 倍，面积？", ["不变", "变为 2 倍", "变为 4 倍", "变为 1/2"], "变为 2 倍", "面积与高成正比。", .46),
            ("geometry", "图形拼接", "两个面积分别为 12 cm²、15 cm² 且不重叠的三角形拼成图形，面积是？", ["3 cm²", "12 cm²", "15 cm²", "27 cm²"], "27 cm²", "不重叠图形面积相加。", .34),
            ("geometry", "面积应用", "一块三角形花坛底 9 m、高 6 m，面积是？", ["15 m²", "27 m²", "54 m²", "108 m²"], "27 m²", "9×6÷2=27。", .37),
            ("geometry", "同底面积", "两个三角形底相同，面积比为 2:3，则高比为？", ["2:3", "3:2", "4:9", "1:1"], "2:3", "底相同时，面积比等于高比。", .63),
        ]
        extra_more = [
            ("integer", "负数相加", "两个负数相加，结果一定是？", ["负数", "正数", "0", "无法确定"], "负数", "同号相加取相同符号，绝对值相加。", .30),
            ("integer", "负数除法", "(-18) ÷ (-3) 的结果是？", ["6", "-6", "15", "-15"], "6", "同号相除得正。", .34),
            ("integer", "乘方符号", "-2³ 的结果是？", ["8", "-8", "6", "-6"], "-8", "先算乘方 2³=8，再取相反数。", .48),
            ("integer", "先除后加", "12 ÷ (-4) + 3 的结果是？", ["0", "-6", "6", "-1"], "0", "先除后加：12÷(-4)=-3，-3+3=0。", .44),
            ("integer", "绝对值方程", "若 |x| = 7，则 x 的值有？", ["只有 7", "只有 -7", "7 和 -7 两个", "无解"], "7 和 -7 两个", "绝对值为 7 的数有两个。", .40),
            ("integer", "温度变化", "气温从 -5℃ 上升 8℃ 后是？", ["3℃", "-3℃", "13℃", "-13℃"], "3℃", "-5+8=3。", .30),
            ("integer", "数轴距离", "数轴上 -7 与 2 之间的距离是？", ["5", "9", "-9", "7"], "9", "距离 = |-7-2| = 9。", .38),
            ("integer", "多重符号", "-[-(-3)] 的结果是？", ["3", "-3", "0", "无法确定"], "-3", "从里向外逐层取相反数。", .50),
            ("integer", "负分数比较", "比较 -3/4 与 -2/3 的大小？", ["-3/4 大", "-2/3 大", "相等", "无法比较"], "-2/3 大", "两个负数，绝对值小的反而大；3/4 > 2/3。", .55),
            ("integer", "连续整数", "三个连续整数之和为 18，则其中最小的数是？", ["5", "6", "4", "7"], "5", "设中间数为 x，则 3x=18，x=6，最小为 5。", .58),
            ("fractions", "分数单位", "3/8 的分数单位是？", ["1/8", "3/8", "1/3", "8/3"], "1/8", "分数单位由分母决定。", .25),
            ("fractions", "假分数化带分数", "17/5 化成带分数是？", ["3 又 2/5", "2 又 3/5", "3 又 3/5", "5 又 2/3"], "3 又 2/5", "17÷5=3 余 2。", .40),
            ("fractions", "异分母加法", "1/3 + 1/4 的结果是？", ["2/7", "7/12", "1/7", "2/12"], "7/12", "通分为 4/12 + 3/12 = 7/12。", .46),
            ("fractions", "异分母减法", "5/6 - 1/4 的结果是？", ["4/2", "7/12", "1/3", "3/2"], "7/12", "通分为 10/12 - 3/12 = 7/12。", .48),
            ("fractions", "分数乘整数", "3/8 × 4 的结果是？", ["3/2", "12/32", "3/32", "3/4"], "3/2", "4 与分母 8 约分，得 3/2。", .42),
            ("fractions", "求倒数", "5/7 的倒数是？", ["7/5", "5/7", "-5/7", "1/7"], "7/5", "分子分母交换位置。", .30),
            ("fractions", "除以整数", "2/5 ÷ 4 的结果是？", ["8/5", "1/10", "4/5", "2/9"], "1/10", "除以整数等于乘它的倒数：2/5×1/4=1/10。", .44),
            ("fractions", "小数化分数", "把 0.375 化成最简分数是？", ["3/8", "5/8", "3/5", "7/8"], "3/8", "0.375 = 375/1000，约分得 3/8。", .35),
            ("fractions", "整体求部分", "12 米的 3/4 是多少米？", ["9 米", "16 米", "8 米", "3 米"], "9 米", "12×3/4=9。", .32),
            ("fractions", "部分求整体", "一个数的 2/5 是 14，这个数是？", ["28", "35", "21", "7"], "35", "14÷2/5=35。", .54),
            ("equations", "简单移项", "解方程 x + 12 = 30，x = ?", ["18", "42", "12", "-18"], "18", "两边减 12。", .25),
            ("equations", "系数化一", "解方程 6x = 42，x = ?", ["7", "36", "48", "252"], "7", "两边除以 6。", .28),
            ("equations", "负系数方程", "解方程 -3x + 5 = 20，x = ?", ["5", "-5", "10", "-10"], "-5", "移项得 -3x=15，两边除以 -3 得 x=-5。", .48),
            ("equations", "合并同类项", "解方程 7x - 2x = 25，x = ?", ["5", "7", "3", "10"], "5", "合并得 5x=25，x=5。", .35),
            ("equations", "去分母", "解方程 x/2 - 1 = 4，x = ?", ["9", "10", "8", "5"], "10", "两边加 1 得 x/2=5，再两边乘 2。", .42),
            ("equations", "分数系数", "解方程 2x/3 = 8，x = ?", ["12", "16/3", "6", "24"], "12", "两边乘 3 得 2x=24，再除以 2。", .46),
            ("equations", "括号与移项", "解方程 5(x - 2) = 3x + 4，x = ?", ["7", "3", "14", "5"], "7", "去括号得 5x-10=3x+4，移项合并得 x=7。", .58),
            ("equations", "列方程", "小明今年 x 岁，爸爸 40 岁，爸爸年龄比小明的 3 倍多 4 岁，可列方程？", ["3x+4=40", "3x-4=40", "x/3+4=40", "3(x+4)=40"], "3x+4=40", "按“3 倍多 4”直接列式。", .50),
            ("equations", "检验方程的解", "x = 3 是下列哪个方程的解？", ["2x-1=5", "x+3=7", "2x=8", "x-3=1"], "2x-1=5", "把 x=3 代入逐一检验，只有 2×3-1=5 成立。", .38),
            ("equations", "利润率", "某商品进价 80 元，售价 104 元，利润率是？", ["30%", "24%", "26%", "130%"], "30%", "利润率 = 利润÷进价 = 24÷80 = 30%。", .60),
            ("functions", "反求自变量", "函数 y = 4x - 3，当 y = 5 时 x = ?", ["2", "8", "2.5", "-2"], "2", "解方程 4x-3=5，得 x=2。", .42),
            ("functions", "斜率与常数", "函数 y = -2x + 7 的斜率是？", ["-2", "7", "2", "-7"], "-2", "y=kx+b 中 k 为斜率。", .30),
            ("functions", "识别一次函数", "下列关系中，y 是 x 的一次函数的是？", ["y = -3x", "y = 5/x", "y = x² + 1", "y² = x"], "y = -3x", "一次函数形如 y=kx+b（k≠0）。", .36),
            ("functions", "增减性", "一次函数 y = 2x + 1，y 随 x 增大而？", ["增大", "减小", "不变", "先增后减"], "增大", "k=2>0，y 随 x 增大而增大。", .34),
            ("functions", "图象过象限", "一次函数 y = -x + 2 的图象不经过哪个象限？", ["第一象限", "第二象限", "第三象限", "第四象限"], "第三象限", "k<0、b>0，图象经过一、二、四象限。", .62),
            ("functions", "待定系数法", "一次函数图象过点 (0,3) 和 (1,5)，其解析式是？", ["y=2x+3", "y=3x+2", "y=5x+3", "y=2x+5"], "y=2x+3", "b=3，k=(5-3)÷1=2。", .55),
            ("functions", "函数值代入", "y = x/2 + 4，当 x = 6 时 y = ?", ["7", "5", "10", "3.5"], "7", "代入得 6/2+4=7。", .32),
            ("functions", "正比例函数", "正比例函数 y = kx 的图象过点 (2, 10)，k = ?", ["5", "10", "2", "20"], "5", "k = 10÷2 = 5。", .38),
            ("functions", "图象平移", "直线 y = 2x 向上平移 3 个单位后的解析式是？", ["y=2x+3", "y=5x", "y=2x-3", "y=2(x+3)"], "y=2x+3", "向上平移在原解析式上加 3。", .50),
            ("functions", "行程计费", "出租车起步价 8 元（含 3 公里），之后每公里 2 元，行驶 x（x>3）公里的费用 y = ?", ["y=2x+2", "y=2x+8", "y=8x+2", "y=2x-2"], "y=2x+2", "8 + 2(x-3) = 2x+2。", .64),
            ("geometry", "面积公式", "三角形的面积公式是？", ["底×高÷2", "底×高", "底+高", "底×高×2"], "底×高÷2", "三角形面积等于底与高乘积的一半。", .22),
            ("geometry", "面积单位换算", "0.5 m² 等于多少 cm²？", ["500 cm²", "50 cm²", "5000 cm²", "0.005 cm²"], "5000 cm²", "1 m² = 10000 cm²。", .48),
            ("geometry", "等面积求高", "三角形面积 24 cm²、底 8 cm，对应的高是？", ["6 cm", "3 cm", "12 cm", "4 cm"], "6 cm", "高 = 2×24÷8 = 6。", .42),
            ("geometry", "中线平分面积", "三角形的一条中线把原三角形分成的两个小三角形面积？", ["相等", "一个大一个小", "无法确定", "相差一半"], "相等", "等底等高的两个三角形面积相等。", .52),
            ("geometry", "正方形对角线", "正方形被一条对角线分成两个三角形，每个三角形的面积是正方形的？", ["一半", "四分之一", "三分之一", "两倍"], "一半", "对角线把正方形面积等分。", .30),
            ("geometry", "平行四边形面积", "平行四边形底 12 cm、高 5 cm，面积是？", ["60 cm²", "30 cm²", "17 cm²", "24 cm²"], "60 cm²", "平行四边形面积 = 底×高。", .35),
            ("geometry", "同底等高", "一个三角形与一个平行四边形同底等高，三角形面积是平行四边形的？", ["一半", "相等", "两倍", "四分之一"], "一半", "同底等高时，三角形面积是平行四边形的一半。", .46),
            ("geometry", "勾股定理", "直角三角形两直角边分别为 3 cm 和 4 cm，斜边长是？", ["5 cm", "7 cm", "6 cm", "3.5 cm"], "5 cm", "由勾股定理，斜边²=3²+4²=25，斜边=5。", .55),
            ("geometry", "面积缩放", "三角形的底和高都扩大为原来的 3 倍，面积变为原来的？", ["9 倍", "3 倍", "6 倍", "不变"], "9 倍", "面积与底、高的乘积成正比，3×3=9。", .60),
            ("geometry", "土地测量", "一块三角形土地底 20 m、高 15 m，面积是？", ["150 m²", "300 m²", "35 m²", "75 m²"], "150 m²", "20×15÷2=150。", .28),
        ]
        expanded = list(base)
        for offset, item in enumerate(extra + extra_more, start=11):
            knowledge_id, title, prompt, choices, answer, explanation, difficulty = item
            expanded.append({"id": f"q{offset:02d}", "knowledge_id": knowledge_id, "title": title, "prompt": prompt, "choices": choices, "answer": answer, "explanation": explanation, "difficulty": difficulty})
        return expanded

    def knowledge_points(self):
        with self.connect() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM knowledge_points ORDER BY ordinal")]

    def edges(self):
        with self.connect() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM edges")]

    def questions(self):
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM questions ORDER BY id").fetchall()
        return [self._question(row) for row in rows]

    def favorites(self, student_id):
        with self.connect() as conn:
            rows = conn.execute("SELECT question_id FROM favorites WHERE student_id = ?", (student_id,)).fetchall()
        return {row["question_id"] for row in rows}

    def toggle_favorite(self, student_id, question_id):
        with self.connect() as conn:
            exists = conn.execute("SELECT 1 FROM favorites WHERE student_id = ? AND question_id = ?", (student_id, question_id)).fetchone()
            if exists:
                conn.execute("DELETE FROM favorites WHERE student_id = ? AND question_id = ?", (student_id, question_id))
                return False
            conn.execute("INSERT INTO favorites (student_id, question_id, created_at) VALUES (?, ?, ?)", (student_id, question_id, datetime.now(timezone.utc).isoformat()))
            return True

    def get_question(self, question_id):
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM questions WHERE id = ?", (question_id,)).fetchone()
        return self._question(row) if row else None

    @staticmethod
    def _question(row):
        item = dict(row)
        item["choices"] = json.loads(item["choices"])
        return item

    def interactions(self, student_id):
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM interactions WHERE student_id = ? ORDER BY answered_at, id", (student_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def add_interaction(self, student_id, question, correct, duration_sec=0):
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO interactions (student_id, knowledge_id, question_id, correct, duration_sec, answered_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (student_id, question["knowledge_id"], question["id"], int(correct), float(duration_sec), now),
            )

    def daily_goal(self, student_id):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT daily_goal FROM learner_settings WHERE student_id = ?", (student_id,)
            ).fetchone()
        return int(row["daily_goal"]) if row else 5

    def set_daily_goal(self, student_id, goal):
        goal = max(1, min(int(goal), 20))
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO learner_settings (student_id, daily_goal, updated_at) VALUES (?, ?, ?)
                   ON CONFLICT(student_id) DO UPDATE SET daily_goal = excluded.daily_goal,
                   updated_at = excluded.updated_at""",
                (student_id, goal, datetime.now(timezone.utc).isoformat()),
            )
        return goal
