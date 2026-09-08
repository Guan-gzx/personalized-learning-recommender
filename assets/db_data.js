const DB = {
 "tables": {
  "questions": {
   "columns": [
    "id",
    "knowledge_id",
    "title",
    "prompt",
    "choices",
    "answer",
    "explanation",
    "difficulty"
   ],
   "rows": [
    {
     "id": "q01",
     "knowledge_id": "integer",
     "title": "整数加法",
     "prompt": "-7 + 12 的结果是？",
     "choices": "[\"-19\", \"-5\", \"5\", \"19\"]",
     "answer": "5",
     "explanation": "异号相加，绝对值相减，符号取绝对值较大的数。",
     "difficulty": 0.25
    },
    {
     "id": "q02",
     "knowledge_id": "integer",
     "title": "整数乘法",
     "prompt": "(-4) × (-6) 的结果是？",
     "choices": "[\"-24\", \"-10\", \"10\", \"24\"]",
     "answer": "24",
     "explanation": "负数乘负数为正数。",
     "difficulty": 0.35
    },
    {
     "id": "q03",
     "knowledge_id": "fractions",
     "title": "同分母分数",
     "prompt": "3/8 + 2/8 的结果是？",
     "choices": "[\"5/16\", \"5/8\", \"1/8\", \"6/8\"]",
     "answer": "5/8",
     "explanation": "同分母分数相加，分母不变、分子相加。",
     "difficulty": 0.4
    },
    {
     "id": "q04",
     "knowledge_id": "fractions",
     "title": "异分母分数",
     "prompt": "1/3 + 1/6 的结果是？",
     "choices": "[\"1/9\", \"1/2\", \"2/9\", \"2/6\"]",
     "answer": "1/2",
     "explanation": "通分为 2/6 + 1/6 = 3/6 = 1/2。",
     "difficulty": 0.62
    },
    {
     "id": "q05",
     "knowledge_id": "equations",
     "title": "基础方程",
     "prompt": "解方程 3x + 2 = 14，x = ?",
     "choices": "[\"3\", \"4\", \"5\", \"6\"]",
     "answer": "4",
     "explanation": "两边减 2 后除以 3。",
     "difficulty": 0.45
    },
    {
     "id": "q06",
     "knowledge_id": "equations",
     "title": "含括号方程",
     "prompt": "解方程 2(x - 3) = 10，x = ?",
     "choices": "[\"2\", \"5\", \"8\", \"13\"]",
     "answer": "8",
     "explanation": "两边先除以 2，再加 3。",
     "difficulty": 0.68
    },
    {
     "id": "q07",
     "knowledge_id": "functions",
     "title": "函数值",
     "prompt": "y = 2x + 1，当 x = 3 时 y = ?",
     "choices": "[\"5\", \"6\", \"7\", \"9\"]",
     "answer": "7",
     "explanation": "代入 x=3，y=2×3+1=7。",
     "difficulty": 0.48
    },
    {
     "id": "q08",
     "knowledge_id": "functions",
     "title": "斜率识别",
     "prompt": "直线 y = -3x + 2 的斜率是？",
     "choices": "[\"-3\", \"2\", \"3\", \"-2\"]",
     "answer": "-3",
     "explanation": "一次函数 y=kx+b 中 k 为斜率。",
     "difficulty": 0.55
    },
    {
     "id": "q09",
     "knowledge_id": "geometry",
     "title": "面积计算",
     "prompt": "三角形底为 8 cm、高为 5 cm，面积是？",
     "choices": "[\"13\", \"20\", \"40\", \"80\"]",
     "answer": "20",
     "explanation": "三角形面积 = 底×高÷2 = 20。",
     "difficulty": 0.36
    },
    {
     "id": "q10",
     "knowledge_id": "geometry",
     "title": "反求高",
     "prompt": "面积为 24 cm²、底为 6 cm 的三角形，高是？",
     "choices": "[\"4\", \"6\", \"8\", \"12\"]",
     "answer": "8",
     "explanation": "高 = 2×面积÷底 = 8。",
     "difficulty": 0.58
    },
    {
     "id": "q11",
     "knowledge_id": "integer",
     "title": "整数减法",
     "prompt": "15 - 23 的结果是？",
     "choices": "[\"-8\", \"8\", \"-38\", \"38\"]",
     "answer": "-8",
     "explanation": "减去更大的数，结果为负数。",
     "difficulty": 0.28
    },
    {
     "id": "q12",
     "knowledge_id": "integer",
     "title": "绝对值",
     "prompt": "|-9| + |4| 的结果是？",
     "choices": "[\"-5\", \"5\", \"13\", \"-13\"]",
     "answer": "13",
     "explanation": "绝对值表示到零点的距离。",
     "difficulty": 0.32
    },
    {
     "id": "q13",
     "knowledge_id": "integer",
     "title": "混合运算",
     "prompt": "-3 + 5 × 2 的结果是？",
     "choices": "[\"4\", \"7\", \"-4\", \"-13\"]",
     "answer": "7",
     "explanation": "先乘除后加减，5×2=10。",
     "difficulty": 0.43
    },
    {
     "id": "q14",
     "knowledge_id": "integer",
     "title": "整数除法",
     "prompt": "(-36) ÷ 9 的结果是？",
     "choices": "[\"-4\", \"4\", \"-27\", \"27\"]",
     "answer": "-4",
     "explanation": "异号相除为负。",
     "difficulty": 0.35
    },
    {
     "id": "q15",
     "knowledge_id": "integer",
     "title": "相反数",
     "prompt": "-12 的相反数是？",
     "choices": "[\"-12\", \"12\", \"0\", \"1/12\"]",
     "answer": "12",
     "explanation": "只有符号相反的两个数互为相反数。",
     "difficulty": 0.22
    },
    {
     "id": "q16",
     "knowledge_id": "integer",
     "title": "数轴比较",
     "prompt": "下列数中最小的是？",
     "choices": "[\"-5\", \"-2\", \"0\", \"3\"]",
     "answer": "-5",
     "explanation": "数轴上越靠左的数越小。",
     "difficulty": 0.3
    },
    {
     "id": "q17",
     "knowledge_id": "integer",
     "title": "括号运算",
     "prompt": "8 - (-6) 的结果是？",
     "choices": "[\"2\", \"-2\", \"14\", \"-14\"]",
     "answer": "14",
     "explanation": "减去一个负数等于加上它的相反数。",
     "difficulty": 0.4
    },
    {
     "id": "q18",
     "knowledge_id": "integer",
     "title": "整数平方",
     "prompt": "(-5)² 的结果是？",
     "choices": "[\"-25\", \"25\", \"-10\", \"10\"]",
     "answer": "25",
     "explanation": "负数的平方为正数。",
     "difficulty": 0.34
    },
    {
     "id": "q19",
     "knowledge_id": "fractions",
     "title": "分数约分",
     "prompt": "12/18 化成最简分数是？",
     "choices": "[\"2/3\", \"3/2\", \"6/9\", \"4/6\"]",
     "answer": "2/3",
     "explanation": "分子分母同时除以最大公因数 6。",
     "difficulty": 0.38
    },
    {
     "id": "q20",
     "knowledge_id": "fractions",
     "title": "分数减法",
     "prompt": "7/10 - 3/10 的结果是？",
     "choices": "[\"4/20\", \"4/10\", \"3/10\", \"1\"]",
     "answer": "4/10",
     "explanation": "同分母分数相减，分母不变。",
     "difficulty": 0.36
    },
    {
     "id": "q21",
     "knowledge_id": "fractions",
     "title": "分数乘法",
     "prompt": "2/3 × 3/5 的结果是？",
     "choices": "[\"6/15\", \"2/5\", \"5/2\", \"1\"]",
     "answer": "2/5",
     "explanation": "分子乘分子、分母乘分母后约分。",
     "difficulty": 0.5
    },
    {
     "id": "q22",
     "knowledge_id": "fractions",
     "title": "分数除法",
     "prompt": "3/4 ÷ 1/2 的结果是？",
     "choices": "[\"3/8\", \"3/2\", \"2/3\", \"1/2\"]",
     "answer": "3/2",
     "explanation": "除以一个分数等于乘它的倒数。",
     "difficulty": 0.62
    },
    {
     "id": "q23",
     "knowledge_id": "fractions",
     "title": "通分",
     "prompt": "1/4 和 1/6 的最小公分母是？",
     "choices": "[\"10\", \"12\", \"24\", \"2\"]",
     "answer": "12",
     "explanation": "4 和 6 的最小公倍数是 12。",
     "difficulty": 0.42
    },
    {
     "id": "q24",
     "knowledge_id": "fractions",
     "title": "带分数",
     "prompt": "1 又 1/2 化成假分数是？",
     "choices": "[\"2/3\", \"3/2\", \"1/2\", \"5/2\"]",
     "answer": "3/2",
     "explanation": "整数部分乘分母再加分子。",
     "difficulty": 0.45
    },
    {
     "id": "q25",
     "knowledge_id": "fractions",
     "title": "实际应用",
     "prompt": "一根绳子长 3/4 米，用去 1/4 米，还剩？",
     "choices": "[\"1/2 米\", \"2/4 米\", \"1/4 米\", \"1 米\"]",
     "answer": "1/2 米",
     "explanation": "3/4-1/4=2/4=1/2。",
     "difficulty": 0.48
    },
    {
     "id": "q26",
     "knowledge_id": "fractions",
     "title": "分数比较",
     "prompt": "下列分数中最大的是？",
     "choices": "[\"1/2\", \"2/3\", \"3/5\", \"5/8\"]",
     "answer": "2/3",
     "explanation": "可通分或化为小数比较。",
     "difficulty": 0.52
    },
    {
     "id": "q27",
     "knowledge_id": "equations",
     "title": "移项求解",
     "prompt": "解方程 5x - 7 = 18，x = ?",
     "choices": "[\"3\", \"5\", \"7\", \"25\"]",
     "answer": "5",
     "explanation": "两边加 7 后再除以 5。",
     "difficulty": 0.42
    },
    {
     "id": "q28",
     "knowledge_id": "equations",
     "title": "系数为负",
     "prompt": "解方程 -2x = 14，x = ?",
     "choices": "[\"7\", \"-7\", \"12\", \"-12\"]",
     "answer": "-7",
     "explanation": "两边同时除以 -2。",
     "difficulty": 0.4
    },
    {
     "id": "q29",
     "knowledge_id": "equations",
     "title": "分配律",
     "prompt": "解方程 3(x + 2)=21，x = ?",
     "choices": "[\"5\", \"7\", \"9\", \"1\"]",
     "answer": "5",
     "explanation": "先除以 3，再减 2。",
     "difficulty": 0.56
    },
    {
     "id": "q30",
     "knowledge_id": "equations",
     "title": "含分数方程",
     "prompt": "x/4 = 3，x = ?",
     "choices": "[\"3/4\", \"7\", \"12\", \"1\"]",
     "answer": "12",
     "explanation": "两边同乘 4。",
     "difficulty": 0.39
    },
    {
     "id": "q31",
     "knowledge_id": "equations",
     "title": "实际问题",
     "prompt": "某数的 3 倍减 4 等于 20，这个数是？",
     "choices": "[\"8\", \"6\", \"24\", \"16\"]",
     "answer": "8",
     "explanation": "列式 3x-4=20。",
     "difficulty": 0.55
    },
    {
     "id": "q32",
     "knowledge_id": "equations",
     "title": "两边含未知数",
     "prompt": "解方程 4x + 3 = 2x + 13，x = ?",
     "choices": "[\"5\", \"8\", \"10\", \"-5\"]",
     "answer": "5",
     "explanation": "移项得 2x=10。",
     "difficulty": 0.66
    },
    {
     "id": "q33",
     "knowledge_id": "equations",
     "title": "去括号",
     "prompt": "解方程 2(x+1)-3=7，x = ?",
     "choices": "[\"3\", \"4\", \"5\", \"6\"]",
     "answer": "4",
     "explanation": "去括号并合并同类项。",
     "difficulty": 0.7
    },
    {
     "id": "q34",
     "knowledge_id": "equations",
     "title": "等式性质",
     "prompt": "方程两边同时乘同一个非零数，解集会？",
     "choices": "[\"不变\", \"扩大\", \"缩小\", \"消失\"]",
     "answer": "不变",
     "explanation": "等式两边进行同样的非零运算，解不变。",
     "difficulty": 0.35
    },
    {
     "id": "q35",
     "knowledge_id": "functions",
     "title": "一次函数图像",
     "prompt": "函数 y=3x-2 的纵截距是？",
     "choices": "[\"3\", \"-2\", \"2\", \"0\"]",
     "answer": "-2",
     "explanation": "y=kx+b 中 b 为纵截距。",
     "difficulty": 0.43
    },
    {
     "id": "q36",
     "knowledge_id": "functions",
     "title": "函数代入",
     "prompt": "y=-x+5，当 x=-2 时 y = ?",
     "choices": "[\"-7\", \"3\", \"5\", \"7\"]",
     "answer": "7",
     "explanation": "代入得 -(-2)+5=7。",
     "difficulty": 0.4
    },
    {
     "id": "q37",
     "knowledge_id": "functions",
     "title": "点在直线",
     "prompt": "点 (2,5) 是否在 y=2x+1 上？",
     "choices": "[\"是\", \"否\", \"无法判断\", \"只在 x>0 时是\"]",
     "answer": "是",
     "explanation": "x=2 时 y=5。",
     "difficulty": 0.45
    },
    {
     "id": "q38",
     "knowledge_id": "functions",
     "title": "变化率",
     "prompt": "y=-4x+6 中，x 每增加 1，y 如何变化？",
     "choices": "[\"增加 4\", \"减少 4\", \"增加 6\", \"不变\"]",
     "answer": "减少 4",
     "explanation": "斜率为 -4。",
     "difficulty": 0.52
    },
    {
     "id": "q39",
     "knowledge_id": "functions",
     "title": "零点",
     "prompt": "y=2x-8 的零点横坐标是？",
     "choices": "[\"-4\", \"4\", \"8\", \"-8\"]",
     "answer": "4",
     "explanation": "令 y=0，解 2x-8=0。",
     "difficulty": 0.56
    },
    {
     "id": "q40",
     "knowledge_id": "functions",
     "title": "平行关系",
     "prompt": "与 y=3x+1 平行的直线斜率可能是？",
     "choices": "[\"3\", \"1\", \"-3\", \"0\"]",
     "answer": "3",
     "explanation": "平行直线斜率相同。",
     "difficulty": 0.5
    },
    {
     "id": "q41",
     "knowledge_id": "functions",
     "title": "比例判断",
     "prompt": "下列哪一个是一次函数？",
     "choices": "[\"y=2x-1\", \"y=x²\", \"y=1/x\", \"y=2\"]",
     "answer": "y=2x-1",
     "explanation": "一次函数形式为 y=kx+b。",
     "difficulty": 0.44
    },
    {
     "id": "q42",
     "knowledge_id": "functions",
     "title": "交点求解",
     "prompt": "y=x+1 与 y=5 的交点横坐标是？",
     "choices": "[\"1\", \"4\", \"5\", \"6\"]",
     "answer": "4",
     "explanation": "令 x+1=5。",
     "difficulty": 0.6
    },
    {
     "id": "q43",
     "knowledge_id": "geometry",
     "title": "面积单位",
     "prompt": "三角形底 10 cm、高 4 cm，面积是？",
     "choices": "[\"14 cm²\", \"20 cm²\", \"40 cm²\", \"80 cm²\"]",
     "answer": "20 cm²",
     "explanation": "面积=10×4÷2。",
     "difficulty": 0.3
    },
    {
     "id": "q44",
     "knowledge_id": "geometry",
     "title": "等底等高",
     "prompt": "两个三角形底和高都相等，它们的面积？",
     "choices": "[\"相等\", \"不一定\", \"相差一倍\", \"无法比较\"]",
     "answer": "相等",
     "explanation": "面积由底和高唯一决定。",
     "difficulty": 0.28
    },
    {
     "id": "q45",
     "knowledge_id": "geometry",
     "title": "面积反求底",
     "prompt": "三角形面积 30 cm²、高 5 cm，底是？",
     "choices": "[\"6 cm\", \"12 cm\", \"15 cm\", \"25 cm\"]",
     "answer": "12 cm",
     "explanation": "底=2×面积÷高。",
     "difficulty": 0.5
    },
    {
     "id": "q46",
     "knowledge_id": "geometry",
     "title": "直角三角形",
     "prompt": "直角三角形两直角边为 6 cm、8 cm，面积是？",
     "choices": "[\"14 cm²\", \"24 cm²\", \"48 cm²\", \"28 cm²\"]",
     "answer": "24 cm²",
     "explanation": "任选一条直角边作底，另一条作高。",
     "difficulty": 0.43
    },
    {
     "id": "q47",
     "knowledge_id": "geometry",
     "title": "面积变化",
     "prompt": "三角形底不变，高变为原来的 2 倍，面积？",
     "choices": "[\"不变\", \"变为 2 倍\", \"变为 4 倍\", \"变为 1/2\"]",
     "answer": "变为 2 倍",
     "explanation": "面积与高成正比。",
     "difficulty": 0.46
    },
    {
     "id": "q48",
     "knowledge_id": "geometry",
     "title": "图形拼接",
     "prompt": "两个面积分别为 12 cm²、15 cm² 且不重叠的三角形拼成图形，面积是？",
     "choices": "[\"3 cm²\", \"12 cm²\", \"15 cm²\", \"27 cm²\"]",
     "answer": "27 cm²",
     "explanation": "不重叠图形面积相加。",
     "difficulty": 0.34
    },
    {
     "id": "q49",
     "knowledge_id": "geometry",
     "title": "面积应用",
     "prompt": "一块三角形花坛底 9 m、高 6 m，面积是？",
     "choices": "[\"15 m²\", \"27 m²\", \"54 m²\", \"108 m²\"]",
     "answer": "27 m²",
     "explanation": "9×6÷2=27。",
     "difficulty": 0.37
    },
    {
     "id": "q50",
     "knowledge_id": "geometry",
     "title": "同底面积",
     "prompt": "两个三角形底相同，面积比为 2:3，则高比为？",
     "choices": "[\"2:3\", \"3:2\", \"4:9\", \"1:1\"]",
     "answer": "2:3",
     "explanation": "底相同时，面积比等于高比。",
     "difficulty": 0.63
    },
    {
     "id": "q51",
     "knowledge_id": "integer",
     "title": "负数相加",
     "prompt": "两个负数相加，结果一定是？",
     "choices": "[\"负数\", \"正数\", \"0\", \"无法确定\"]",
     "answer": "负数",
     "explanation": "同号相加取相同符号，绝对值相加。",
     "difficulty": 0.3
    },
    {
     "id": "q52",
     "knowledge_id": "integer",
     "title": "负数除法",
     "prompt": "(-18) ÷ (-3) 的结果是？",
     "choices": "[\"6\", \"-6\", \"15\", \"-15\"]",
     "answer": "6",
     "explanation": "同号相除得正。",
     "difficulty": 0.34
    },
    {
     "id": "q53",
     "knowledge_id": "integer",
     "title": "乘方符号",
     "prompt": "-2³ 的结果是？",
     "choices": "[\"8\", \"-8\", \"6\", \"-6\"]",
     "answer": "-8",
     "explanation": "先算乘方 2³=8，再取相反数。",
     "difficulty": 0.48
    },
    {
     "id": "q54",
     "knowledge_id": "integer",
     "title": "先除后加",
     "prompt": "12 ÷ (-4) + 3 的结果是？",
     "choices": "[\"0\", \"-6\", \"6\", \"-1\"]",
     "answer": "0",
     "explanation": "先除后加：12÷(-4)=-3，-3+3=0。",
     "difficulty": 0.44
    },
    {
     "id": "q55",
     "knowledge_id": "integer",
     "title": "绝对值方程",
     "prompt": "若 |x| = 7，则 x 的值有？",
     "choices": "[\"只有 7\", \"只有 -7\", \"7 和 -7 两个\", \"无解\"]",
     "answer": "7 和 -7 两个",
     "explanation": "绝对值为 7 的数有两个。",
     "difficulty": 0.4
    },
    {
     "id": "q56",
     "knowledge_id": "integer",
     "title": "温度变化",
     "prompt": "气温从 -5℃ 上升 8℃ 后是？",
     "choices": "[\"3℃\", \"-3℃\", \"13℃\", \"-13℃\"]",
     "answer": "3℃",
     "explanation": "-5+8=3。",
     "difficulty": 0.3
    },
    {
     "id": "q57",
     "knowledge_id": "integer",
     "title": "数轴距离",
     "prompt": "数轴上 -7 与 2 之间的距离是？",
     "choices": "[\"5\", \"9\", \"-9\", \"7\"]",
     "answer": "9",
     "explanation": "距离 = |-7-2| = 9。",
     "difficulty": 0.38
    },
    {
     "id": "q58",
     "knowledge_id": "integer",
     "title": "多重符号",
     "prompt": "-[-(-3)] 的结果是？",
     "choices": "[\"3\", \"-3\", \"0\", \"无法确定\"]",
     "answer": "-3",
     "explanation": "从里向外逐层取相反数。",
     "difficulty": 0.5
    },
    {
     "id": "q59",
     "knowledge_id": "integer",
     "title": "负分数比较",
     "prompt": "比较 -3/4 与 -2/3 的大小？",
     "choices": "[\"-3/4 大\", \"-2/3 大\", \"相等\", \"无法比较\"]",
     "answer": "-2/3 大",
     "explanation": "两个负数，绝对值小的反而大；3/4 > 2/3。",
     "difficulty": 0.55
    },
    {
     "id": "q60",
     "knowledge_id": "integer",
     "title": "连续整数",
     "prompt": "三个连续整数之和为 18，则其中最小的数是？",
     "choices": "[\"5\", \"6\", \"4\", \"7\"]",
     "answer": "5",
     "explanation": "设中间数为 x，则 3x=18，x=6，最小为 5。",
     "difficulty": 0.58
    },
    {
     "id": "q61",
     "knowledge_id": "fractions",
     "title": "分数单位",
     "prompt": "3/8 的分数单位是？",
     "choices": "[\"1/8\", \"3/8\", \"1/3\", \"8/3\"]",
     "answer": "1/8",
     "explanation": "分数单位由分母决定。",
     "difficulty": 0.25
    },
    {
     "id": "q62",
     "knowledge_id": "fractions",
     "title": "假分数化带分数",
     "prompt": "17/5 化成带分数是？",
     "choices": "[\"3 又 2/5\", \"2 又 3/5\", \"3 又 3/5\", \"5 又 2/3\"]",
     "answer": "3 又 2/5",
     "explanation": "17÷5=3 余 2。",
     "difficulty": 0.4
    },
    {
     "id": "q63",
     "knowledge_id": "fractions",
     "title": "异分母加法",
     "prompt": "1/3 + 1/4 的结果是？",
     "choices": "[\"2/7\", \"7/12\", \"1/7\", \"2/12\"]",
     "answer": "7/12",
     "explanation": "通分为 4/12 + 3/12 = 7/12。",
     "difficulty": 0.46
    },
    {
     "id": "q64",
     "knowledge_id": "fractions",
     "title": "异分母减法",
     "prompt": "5/6 - 1/4 的结果是？",
     "choices": "[\"4/2\", \"7/12\", \"1/3\", \"3/2\"]",
     "answer": "7/12",
     "explanation": "通分为 10/12 - 3/12 = 7/12。",
     "difficulty": 0.48
    },
    {
     "id": "q65",
     "knowledge_id": "fractions",
     "title": "分数乘整数",
     "prompt": "3/8 × 4 的结果是？",
     "choices": "[\"3/2\", \"12/32\", \"3/32\", \"3/4\"]",
     "answer": "3/2",
     "explanation": "4 与分母 8 约分，得 3/2。",
     "difficulty": 0.42
    },
    {
     "id": "q66",
     "knowledge_id": "fractions",
     "title": "求倒数",
     "prompt": "5/7 的倒数是？",
     "choices": "[\"7/5\", \"5/7\", \"-5/7\", \"1/7\"]",
     "answer": "7/5",
     "explanation": "分子分母交换位置。",
     "difficulty": 0.3
    },
    {
     "id": "q67",
     "knowledge_id": "fractions",
     "title": "除以整数",
     "prompt": "2/5 ÷ 4 的结果是？",
     "choices": "[\"8/5\", \"1/10\", \"4/5\", \"2/9\"]",
     "answer": "1/10",
     "explanation": "除以整数等于乘它的倒数：2/5×1/4=1/10。",
     "difficulty": 0.44
    },
    {
     "id": "q68",
     "knowledge_id": "fractions",
     "title": "小数化分数",
     "prompt": "把 0.375 化成最简分数是？",
     "choices": "[\"3/8\", \"5/8\", \"3/5\", \"7/8\"]",
     "answer": "3/8",
     "explanation": "0.375 = 375/1000，约分得 3/8。",
     "difficulty": 0.35
    },
    {
     "id": "q69",
     "knowledge_id": "fractions",
     "title": "整体求部分",
     "prompt": "12 米的 3/4 是多少米？",
     "choices": "[\"9 米\", \"16 米\", \"8 米\", \"3 米\"]",
     "answer": "9 米",
     "explanation": "12×3/4=9。",
     "difficulty": 0.32
    },
    {
     "id": "q70",
     "knowledge_id": "fractions",
     "title": "部分求整体",
     "prompt": "一个数的 2/5 是 14，这个数是？",
     "choices": "[\"28\", \"35\", \"21\", \"7\"]",
     "answer": "35",
     "explanation": "14÷2/5=35。",
     "difficulty": 0.54
    },
    {
     "id": "q71",
     "knowledge_id": "equations",
     "title": "简单移项",
     "prompt": "解方程 x + 12 = 30，x = ?",
     "choices": "[\"18\", \"42\", \"12\", \"-18\"]",
     "answer": "18",
     "explanation": "两边减 12。",
     "difficulty": 0.25
    },
    {
     "id": "q72",
     "knowledge_id": "equations",
     "title": "系数化一",
     "prompt": "解方程 6x = 42，x = ?",
     "choices": "[\"7\", \"36\", \"48\", \"252\"]",
     "answer": "7",
     "explanation": "两边除以 6。",
     "difficulty": 0.28
    },
    {
     "id": "q73",
     "knowledge_id": "equations",
     "title": "负系数方程",
     "prompt": "解方程 -3x + 5 = 20，x = ?",
     "choices": "[\"5\", \"-5\", \"10\", \"-10\"]",
     "answer": "-5",
     "explanation": "移项得 -3x=15，两边除以 -3 得 x=-5。",
     "difficulty": 0.48
    },
    {
     "id": "q74",
     "knowledge_id": "equations",
     "title": "合并同类项",
     "prompt": "解方程 7x - 2x = 25，x = ?",
     "choices": "[\"5\", \"7\", \"3\", \"10\"]",
     "answer": "5",
     "explanation": "合并得 5x=25，x=5。",
     "difficulty": 0.35
    },
    {
     "id": "q75",
     "knowledge_id": "equations",
     "title": "去分母",
     "prompt": "解方程 x/2 - 1 = 4，x = ?",
     "choices": "[\"9\", \"10\", \"8\", \"5\"]",
     "answer": "10",
     "explanation": "两边加 1 得 x/2=5，再两边乘 2。",
     "difficulty": 0.42
    },
    {
     "id": "q76",
     "knowledge_id": "equations",
     "title": "分数系数",
     "prompt": "解方程 2x/3 = 8，x = ?",
     "choices": "[\"12\", \"16/3\", \"6\", \"24\"]",
     "answer": "12",
     "explanation": "两边乘 3 得 2x=24，再除以 2。",
     "difficulty": 0.46
    },
    {
     "id": "q77",
     "knowledge_id": "equations",
     "title": "括号与移项",
     "prompt": "解方程 5(x - 2) = 3x + 4，x = ?",
     "choices": "[\"7\", \"3\", \"14\", \"5\"]",
     "answer": "7",
     "explanation": "去括号得 5x-10=3x+4，移项合并得 x=7。",
     "difficulty": 0.58
    },
    {
     "id": "q78",
     "knowledge_id": "equations",
     "title": "列方程",
     "prompt": "小明今年 x 岁，爸爸 40 岁，爸爸年龄比小明的 3 倍多 4 岁，可列方程？",
     "choices": "[\"3x+4=40\", \"3x-4=40\", \"x/3+4=40\", \"3(x+4)=40\"]",
     "answer": "3x+4=40",
     "explanation": "按“3 倍多 4”直接列式。",
     "difficulty": 0.5
    },
    {
     "id": "q79",
     "knowledge_id": "equations",
     "title": "检验方程的解",
     "prompt": "x = 3 是下列哪个方程的解？",
     "choices": "[\"2x-1=5\", \"x+3=7\", \"2x=8\", \"x-3=1\"]",
     "answer": "2x-1=5",
     "explanation": "把 x=3 代入逐一检验，只有 2×3-1=5 成立。",
     "difficulty": 0.38
    },
    {
     "id": "q80",
     "knowledge_id": "equations",
     "title": "利润率",
     "prompt": "某商品进价 80 元，售价 104 元，利润率是？",
     "choices": "[\"30%\", \"24%\", \"26%\", \"130%\"]",
     "answer": "30%",
     "explanation": "利润率 = 利润÷进价 = 24÷80 = 30%。",
     "difficulty": 0.6
    },
    {
     "id": "q81",
     "knowledge_id": "functions",
     "title": "反求自变量",
     "prompt": "函数 y = 4x - 3，当 y = 5 时 x = ?",
     "choices": "[\"2\", \"8\", \"2.5\", \"-2\"]",
     "answer": "2",
     "explanation": "解方程 4x-3=5，得 x=2。",
     "difficulty": 0.42
    },
    {
     "id": "q82",
     "knowledge_id": "functions",
     "title": "斜率与常数",
     "prompt": "函数 y = -2x + 7 的斜率是？",
     "choices": "[\"-2\", \"7\", \"2\", \"-7\"]",
     "answer": "-2",
     "explanation": "y=kx+b 中 k 为斜率。",
     "difficulty": 0.3
    },
    {
     "id": "q83",
     "knowledge_id": "functions",
     "title": "识别一次函数",
     "prompt": "下列关系中，y 是 x 的一次函数的是？",
     "choices": "[\"y = -3x\", \"y = 5/x\", \"y = x² + 1\", \"y² = x\"]",
     "answer": "y = -3x",
     "explanation": "一次函数形如 y=kx+b（k≠0）。",
     "difficulty": 0.36
    },
    {
     "id": "q84",
     "knowledge_id": "functions",
     "title": "增减性",
     "prompt": "一次函数 y = 2x + 1，y 随 x 增大而？",
     "choices": "[\"增大\", \"减小\", \"不变\", \"先增后减\"]",
     "answer": "增大",
     "explanation": "k=2>0，y 随 x 增大而增大。",
     "difficulty": 0.34
    },
    {
     "id": "q85",
     "knowledge_id": "functions",
     "title": "图象过象限",
     "prompt": "一次函数 y = -x + 2 的图象不经过哪个象限？",
     "choices": "[\"第一象限\", \"第二象限\", \"第三象限\", \"第四象限\"]",
     "answer": "第三象限",
     "explanation": "k<0、b>0，图象经过一、二、四象限。",
     "difficulty": 0.62
    },
    {
     "id": "q86",
     "knowledge_id": "functions",
     "title": "待定系数法",
     "prompt": "一次函数图象过点 (0,3) 和 (1,5)，其解析式是？",
     "choices": "[\"y=2x+3\", \"y=3x+2\", \"y=5x+3\", \"y=2x+5\"]",
     "answer": "y=2x+3",
     "explanation": "b=3，k=(5-3)÷1=2。",
     "difficulty": 0.55
    },
    {
     "id": "q87",
     "knowledge_id": "functions",
     "title": "函数值代入",
     "prompt": "y = x/2 + 4，当 x = 6 时 y = ?",
     "choices": "[\"7\", \"5\", \"10\", \"3.5\"]",
     "answer": "7",
     "explanation": "代入得 6/2+4=7。",
     "difficulty": 0.32
    },
    {
     "id": "q88",
     "knowledge_id": "functions",
     "title": "正比例函数",
     "prompt": "正比例函数 y = kx 的图象过点 (2, 10)，k = ?",
     "choices": "[\"5\", \"10\", \"2\", \"20\"]",
     "answer": "5",
     "explanation": "k = 10÷2 = 5。",
     "difficulty": 0.38
    },
    {
     "id": "q89",
     "knowledge_id": "functions",
     "title": "图象平移",
     "prompt": "直线 y = 2x 向上平移 3 个单位后的解析式是？",
     "choices": "[\"y=2x+3\", \"y=5x\", \"y=2x-3\", \"y=2(x+3)\"]",
     "answer": "y=2x+3",
     "explanation": "向上平移在原解析式上加 3。",
     "difficulty": 0.5
    },
    {
     "id": "q90",
     "knowledge_id": "functions",
     "title": "行程计费",
     "prompt": "出租车起步价 8 元（含 3 公里），之后每公里 2 元，行驶 x（x>3）公里的费用 y = ?",
     "choices": "[\"y=2x+2\", \"y=2x+8\", \"y=8x+2\", \"y=2x-2\"]",
     "answer": "y=2x+2",
     "explanation": "8 + 2(x-3) = 2x+2。",
     "difficulty": 0.64
    },
    {
     "id": "q91",
     "knowledge_id": "geometry",
     "title": "面积公式",
     "prompt": "三角形的面积公式是？",
     "choices": "[\"底×高÷2\", \"底×高\", \"底+高\", \"底×高×2\"]",
     "answer": "底×高÷2",
     "explanation": "三角形面积等于底与高乘积的一半。",
     "difficulty": 0.22
    },
    {
     "id": "q92",
     "knowledge_id": "geometry",
     "title": "面积单位换算",
     "prompt": "0.5 m² 等于多少 cm²？",
     "choices": "[\"500 cm²\", \"50 cm²\", \"5000 cm²\", \"0.005 cm²\"]",
     "answer": "5000 cm²",
     "explanation": "1 m² = 10000 cm²。",
     "difficulty": 0.48
    },
    {
     "id": "q93",
     "knowledge_id": "geometry",
     "title": "等面积求高",
     "prompt": "三角形面积 24 cm²、底 8 cm，对应的高是？",
     "choices": "[\"6 cm\", \"3 cm\", \"12 cm\", \"4 cm\"]",
     "answer": "6 cm",
     "explanation": "高 = 2×24÷8 = 6。",
     "difficulty": 0.42
    },
    {
     "id": "q94",
     "knowledge_id": "geometry",
     "title": "中线平分面积",
     "prompt": "三角形的一条中线把原三角形分成的两个小三角形面积？",
     "choices": "[\"相等\", \"一个大一个小\", \"无法确定\", \"相差一半\"]",
     "answer": "相等",
     "explanation": "等底等高的两个三角形面积相等。",
     "difficulty": 0.52
    },
    {
     "id": "q95",
     "knowledge_id": "geometry",
     "title": "正方形对角线",
     "prompt": "正方形被一条对角线分成两个三角形，每个三角形的面积是正方形的？",
     "choices": "[\"一半\", \"四分之一\", \"三分之一\", \"两倍\"]",
     "answer": "一半",
     "explanation": "对角线把正方形面积等分。",
     "difficulty": 0.3
    },
    {
     "id": "q96",
     "knowledge_id": "geometry",
     "title": "平行四边形面积",
     "prompt": "平行四边形底 12 cm、高 5 cm，面积是？",
     "choices": "[\"60 cm²\", \"30 cm²\", \"17 cm²\", \"24 cm²\"]",
     "answer": "60 cm²",
     "explanation": "平行四边形面积 = 底×高。",
     "difficulty": 0.35
    },
    {
     "id": "q97",
     "knowledge_id": "geometry",
     "title": "同底等高",
     "prompt": "一个三角形与一个平行四边形同底等高，三角形面积是平行四边形的？",
     "choices": "[\"一半\", \"相等\", \"两倍\", \"四分之一\"]",
     "answer": "一半",
     "explanation": "同底等高时，三角形面积是平行四边形的一半。",
     "difficulty": 0.46
    },
    {
     "id": "q98",
     "knowledge_id": "geometry",
     "title": "勾股定理",
     "prompt": "直角三角形两直角边分别为 3 cm 和 4 cm，斜边长是？",
     "choices": "[\"5 cm\", \"7 cm\", \"6 cm\", \"3.5 cm\"]",
     "answer": "5 cm",
     "explanation": "由勾股定理，斜边²=3²+4²=25，斜边=5。",
     "difficulty": 0.55
    },
    {
     "id": "q99",
     "knowledge_id": "geometry",
     "title": "面积缩放",
     "prompt": "三角形的底和高都扩大为原来的 3 倍，面积变为原来的？",
     "choices": "[\"9 倍\", \"3 倍\", \"6 倍\", \"不变\"]",
     "answer": "9 倍",
     "explanation": "面积与底、高的乘积成正比，3×3=9。",
     "difficulty": 0.6
    },
    {
     "id": "q100",
     "knowledge_id": "geometry",
     "title": "土地测量",
     "prompt": "一块三角形土地底 20 m、高 15 m，面积是？",
     "choices": "[\"150 m²\", \"300 m²\", \"35 m²\", \"75 m²\"]",
     "answer": "150 m²",
     "explanation": "20×15÷2=150。",
     "difficulty": 0.28
    }
   ]
  },
  "interactions": {
   "columns": [
    "id",
    "student_id",
    "knowledge_id",
    "question_id",
    "correct",
    "answered_at",
    "duration_sec"
   ],
   "rows": [
    {
     "id": 3729,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q01",
     "correct": 1,
     "answered_at": "2026-08-09T11:25:49.808112+00:00",
     "duration_sec": 22.0
    },
    {
     "id": 3730,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q02",
     "correct": 1,
     "answered_at": "2026-08-09T20:25:49.808112+00:00",
     "duration_sec": 35.0
    },
    {
     "id": 3731,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q03",
     "correct": 1,
     "answered_at": "2026-08-10T05:25:49.808112+00:00",
     "duration_sec": 48.0
    },
    {
     "id": 3732,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q04",
     "correct": 1,
     "answered_at": "2026-08-10T14:25:49.808112+00:00",
     "duration_sec": 61.0
    },
    {
     "id": 3733,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q05",
     "correct": 0,
     "answered_at": "2026-08-10T23:25:49.808112+00:00",
     "duration_sec": 74.0
    },
    {
     "id": 3734,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q06",
     "correct": 1,
     "answered_at": "2026-08-11T08:25:49.808112+00:00",
     "duration_sec": 87.0
    },
    {
     "id": 3735,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q07",
     "correct": 1,
     "answered_at": "2026-08-11T17:25:49.808112+00:00",
     "duration_sec": 25.0
    },
    {
     "id": 3736,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q08",
     "correct": 1,
     "answered_at": "2026-08-12T02:25:49.808112+00:00",
     "duration_sec": 38.0
    },
    {
     "id": 3737,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q09",
     "correct": 1,
     "answered_at": "2026-08-12T11:25:49.808112+00:00",
     "duration_sec": 51.0
    },
    {
     "id": 3738,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q10",
     "correct": 1,
     "answered_at": "2026-08-12T20:25:49.808112+00:00",
     "duration_sec": 64.0
    },
    {
     "id": 3739,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q11",
     "correct": 1,
     "answered_at": "2026-08-13T05:25:49.808112+00:00",
     "duration_sec": 77.0
    },
    {
     "id": 3740,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q12",
     "correct": 1,
     "answered_at": "2026-08-13T14:25:49.808112+00:00",
     "duration_sec": 90.0
    },
    {
     "id": 3741,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q13",
     "correct": 1,
     "answered_at": "2026-08-13T23:25:49.808112+00:00",
     "duration_sec": 28.0
    },
    {
     "id": 3742,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q14",
     "correct": 1,
     "answered_at": "2026-08-14T08:25:49.808112+00:00",
     "duration_sec": 41.0
    },
    {
     "id": 3743,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q15",
     "correct": 1,
     "answered_at": "2026-08-14T17:25:49.808112+00:00",
     "duration_sec": 54.0
    },
    {
     "id": 3744,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q16",
     "correct": 1,
     "answered_at": "2026-08-15T02:25:49.808112+00:00",
     "duration_sec": 67.0
    },
    {
     "id": 3745,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q17",
     "correct": 1,
     "answered_at": "2026-08-15T11:25:49.808112+00:00",
     "duration_sec": 80.0
    },
    {
     "id": 3746,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q18",
     "correct": 1,
     "answered_at": "2026-08-15T20:25:49.808112+00:00",
     "duration_sec": 93.0
    },
    {
     "id": 3747,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q19",
     "correct": 1,
     "answered_at": "2026-08-16T05:25:49.808112+00:00",
     "duration_sec": 31.0
    },
    {
     "id": 3748,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q20",
     "correct": 1,
     "answered_at": "2026-08-16T14:25:49.808112+00:00",
     "duration_sec": 44.0
    },
    {
     "id": 3749,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q21",
     "correct": 0,
     "answered_at": "2026-08-16T23:25:49.808112+00:00",
     "duration_sec": 57.0
    },
    {
     "id": 3750,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q22",
     "correct": 1,
     "answered_at": "2026-08-17T08:25:49.808112+00:00",
     "duration_sec": 70.0
    },
    {
     "id": 3751,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q23",
     "correct": 1,
     "answered_at": "2026-08-17T17:25:49.808112+00:00",
     "duration_sec": 83.0
    },
    {
     "id": 3752,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q24",
     "correct": 1,
     "answered_at": "2026-08-18T02:25:49.808112+00:00",
     "duration_sec": 96.0
    },
    {
     "id": 3753,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q25",
     "correct": 0,
     "answered_at": "2026-08-18T11:25:49.808112+00:00",
     "duration_sec": 34.0
    },
    {
     "id": 3754,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q26",
     "correct": 1,
     "answered_at": "2026-08-18T20:25:49.808112+00:00",
     "duration_sec": 47.0
    },
    {
     "id": 3755,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q27",
     "correct": 1,
     "answered_at": "2026-08-19T05:25:49.808112+00:00",
     "duration_sec": 60.0
    },
    {
     "id": 3756,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q28",
     "correct": 1,
     "answered_at": "2026-08-19T14:25:49.808112+00:00",
     "duration_sec": 73.0
    },
    {
     "id": 3757,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q29",
     "correct": 0,
     "answered_at": "2026-08-19T23:25:49.808112+00:00",
     "duration_sec": 86.0
    },
    {
     "id": 3758,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q30",
     "correct": 1,
     "answered_at": "2026-08-20T08:25:49.808112+00:00",
     "duration_sec": 24.0
    },
    {
     "id": 3759,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q31",
     "correct": 1,
     "answered_at": "2026-08-20T17:25:49.808112+00:00",
     "duration_sec": 37.0
    },
    {
     "id": 3760,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q32",
     "correct": 1,
     "answered_at": "2026-08-21T02:25:49.808112+00:00",
     "duration_sec": 50.0
    },
    {
     "id": 3761,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q33",
     "correct": 0,
     "answered_at": "2026-08-21T11:25:49.808112+00:00",
     "duration_sec": 63.0
    },
    {
     "id": 3762,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q34",
     "correct": 1,
     "answered_at": "2026-08-21T20:25:49.808112+00:00",
     "duration_sec": 76.0
    },
    {
     "id": 3763,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q35",
     "correct": 1,
     "answered_at": "2026-08-22T05:25:49.808112+00:00",
     "duration_sec": 89.0
    },
    {
     "id": 3764,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q36",
     "correct": 1,
     "answered_at": "2026-08-22T14:25:49.808112+00:00",
     "duration_sec": 27.0
    },
    {
     "id": 3765,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q37",
     "correct": 1,
     "answered_at": "2026-08-22T23:25:49.808112+00:00",
     "duration_sec": 40.0
    },
    {
     "id": 3766,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q38",
     "correct": 1,
     "answered_at": "2026-08-23T08:25:49.808112+00:00",
     "duration_sec": 53.0
    },
    {
     "id": 3767,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q39",
     "correct": 1,
     "answered_at": "2026-08-23T17:25:49.808112+00:00",
     "duration_sec": 66.0
    },
    {
     "id": 3768,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q40",
     "correct": 1,
     "answered_at": "2026-08-24T02:25:49.808112+00:00",
     "duration_sec": 79.0
    },
    {
     "id": 3769,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q41",
     "correct": 1,
     "answered_at": "2026-08-24T11:25:49.808112+00:00",
     "duration_sec": 92.0
    },
    {
     "id": 3770,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q42",
     "correct": 1,
     "answered_at": "2026-08-24T20:25:49.808112+00:00",
     "duration_sec": 30.0
    },
    {
     "id": 3771,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q43",
     "correct": 1,
     "answered_at": "2026-08-25T05:25:49.808112+00:00",
     "duration_sec": 43.0
    },
    {
     "id": 3772,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q44",
     "correct": 1,
     "answered_at": "2026-08-25T14:25:49.808112+00:00",
     "duration_sec": 56.0
    },
    {
     "id": 3773,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q45",
     "correct": 1,
     "answered_at": "2026-08-25T23:25:49.808112+00:00",
     "duration_sec": 69.0
    },
    {
     "id": 3774,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q46",
     "correct": 1,
     "answered_at": "2026-08-26T08:25:49.808112+00:00",
     "duration_sec": 82.0
    },
    {
     "id": 3775,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q47",
     "correct": 1,
     "answered_at": "2026-08-26T17:25:49.808112+00:00",
     "duration_sec": 95.0
    },
    {
     "id": 3776,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q48",
     "correct": 1,
     "answered_at": "2026-08-27T02:25:49.808112+00:00",
     "duration_sec": 33.0
    },
    {
     "id": 3777,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q49",
     "correct": 1,
     "answered_at": "2026-08-27T11:25:49.808112+00:00",
     "duration_sec": 46.0
    },
    {
     "id": 3778,
     "student_id": "demo_student",
     "knowledge_id": "geometry",
     "question_id": "q50",
     "correct": 1,
     "answered_at": "2026-08-27T20:25:49.808112+00:00",
     "duration_sec": 59.0
    },
    {
     "id": 3779,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q51",
     "correct": 1,
     "answered_at": "2026-08-28T05:25:49.808112+00:00",
     "duration_sec": 72.0
    },
    {
     "id": 3780,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q52",
     "correct": 1,
     "answered_at": "2026-08-28T14:25:49.808112+00:00",
     "duration_sec": 85.0
    },
    {
     "id": 3781,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q53",
     "correct": 1,
     "answered_at": "2026-08-28T23:25:49.808112+00:00",
     "duration_sec": 23.0
    },
    {
     "id": 3782,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q54",
     "correct": 1,
     "answered_at": "2026-08-29T08:25:49.808112+00:00",
     "duration_sec": 36.0
    },
    {
     "id": 3783,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q55",
     "correct": 1,
     "answered_at": "2026-08-29T17:25:49.808112+00:00",
     "duration_sec": 49.0
    },
    {
     "id": 3784,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q56",
     "correct": 1,
     "answered_at": "2026-08-30T02:25:49.808112+00:00",
     "duration_sec": 62.0
    },
    {
     "id": 3785,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q57",
     "correct": 1,
     "answered_at": "2026-08-30T11:25:49.808112+00:00",
     "duration_sec": 75.0
    },
    {
     "id": 3786,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q58",
     "correct": 1,
     "answered_at": "2026-08-30T20:25:49.808112+00:00",
     "duration_sec": 88.0
    },
    {
     "id": 3787,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q59",
     "correct": 1,
     "answered_at": "2026-08-31T05:25:49.808112+00:00",
     "duration_sec": 26.0
    },
    {
     "id": 3788,
     "student_id": "demo_student",
     "knowledge_id": "integer",
     "question_id": "q60",
     "correct": 1,
     "answered_at": "2026-08-31T14:25:49.808112+00:00",
     "duration_sec": 39.0
    },
    {
     "id": 3789,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q61",
     "correct": 0,
     "answered_at": "2026-08-31T23:25:49.808112+00:00",
     "duration_sec": 52.0
    },
    {
     "id": 3790,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q62",
     "correct": 1,
     "answered_at": "2026-09-01T08:25:49.808112+00:00",
     "duration_sec": 65.0
    },
    {
     "id": 3791,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q63",
     "correct": 1,
     "answered_at": "2026-09-01T17:25:49.808112+00:00",
     "duration_sec": 78.0
    },
    {
     "id": 3792,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q64",
     "correct": 1,
     "answered_at": "2026-09-02T02:25:49.808112+00:00",
     "duration_sec": 91.0
    },
    {
     "id": 3793,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q65",
     "correct": 0,
     "answered_at": "2026-09-02T11:25:49.808112+00:00",
     "duration_sec": 29.0
    },
    {
     "id": 3794,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q66",
     "correct": 1,
     "answered_at": "2026-09-02T20:25:49.808112+00:00",
     "duration_sec": 42.0
    },
    {
     "id": 3795,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q67",
     "correct": 1,
     "answered_at": "2026-09-03T05:25:49.808112+00:00",
     "duration_sec": 55.0
    },
    {
     "id": 3796,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q68",
     "correct": 1,
     "answered_at": "2026-09-03T14:25:49.808112+00:00",
     "duration_sec": 68.0
    },
    {
     "id": 3797,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q69",
     "correct": 0,
     "answered_at": "2026-09-03T23:25:49.808112+00:00",
     "duration_sec": 81.0
    },
    {
     "id": 3798,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q70",
     "correct": 1,
     "answered_at": "2026-09-04T08:25:49.808112+00:00",
     "duration_sec": 94.0
    },
    {
     "id": 3799,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q71",
     "correct": 1,
     "answered_at": "2026-09-04T17:25:49.808112+00:00",
     "duration_sec": 32.0
    },
    {
     "id": 3800,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q72",
     "correct": 1,
     "answered_at": "2026-09-05T02:25:49.808112+00:00",
     "duration_sec": 45.0
    },
    {
     "id": 3801,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q04",
     "correct": 1,
     "answered_at": "2026-09-07T02:26:40.262243+00:00",
     "duration_sec": 14.2
    },
    {
     "id": 3802,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q33",
     "correct": 1,
     "answered_at": "2026-09-07T02:26:50.887302+00:00",
     "duration_sec": 9.4
    },
    {
     "id": 3803,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q22",
     "correct": 1,
     "answered_at": "2026-09-07T02:26:59.798994+00:00",
     "duration_sec": 7.9
    },
    {
     "id": 3804,
     "student_id": "demo_student",
     "knowledge_id": "functions",
     "question_id": "q90",
     "correct": 1,
     "answered_at": "2026-09-07T02:27:27.078337+00:00",
     "duration_sec": 26.2
    },
    {
     "id": 3805,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q26",
     "correct": 1,
     "answered_at": "2026-09-07T02:27:38.002248+00:00",
     "duration_sec": 9.2
    },
    {
     "id": 3806,
     "student_id": "demo_student",
     "knowledge_id": "equations",
     "question_id": "q06",
     "correct": 1,
     "answered_at": "2026-09-07T02:28:15.063613+00:00",
     "duration_sec": 7.3
    },
    {
     "id": 3807,
     "student_id": "demo_student",
     "knowledge_id": "fractions",
     "question_id": "q70",
     "correct": 1,
     "answered_at": "2026-09-07T02:28:40.027273+00:00",
     "duration_sec": 6.4
    }
   ]
  },
  "knowledge_points": {
   "columns": [
    "id",
    "name",
    "description",
    "ordinal"
   ],
   "rows": [
    {
     "id": "integer",
     "name": "整数运算",
     "description": "掌握正负数与四则运算",
     "ordinal": 1
    },
    {
     "id": "fractions",
     "name": "分数运算",
     "description": "掌握约分、通分与分数加减",
     "ordinal": 2
    },
    {
     "id": "equations",
     "name": "一元一次方程",
     "description": "掌握等式变形与求解",
     "ordinal": 3
    },
    {
     "id": "functions",
     "name": "一次函数",
     "description": "掌握函数关系和图像",
     "ordinal": 4
    },
    {
     "id": "geometry",
     "name": "三角形面积",
     "description": "掌握底乘高除以二",
     "ordinal": 5
    }
   ]
  },
  "edges": {
   "columns": [
    "source_id",
    "target_id",
    "relation"
   ],
   "rows": [
    {
     "source_id": "integer",
     "target_id": "fractions",
     "relation": "prerequisite"
    },
    {
     "source_id": "fractions",
     "target_id": "equations",
     "relation": "prerequisite"
    },
    {
     "source_id": "equations",
     "target_id": "functions",
     "relation": "prerequisite"
    },
    {
     "source_id": "integer",
     "target_id": "geometry",
     "relation": "related"
    }
   ]
  },
  "favorites": {
   "columns": [
    "student_id",
    "question_id",
    "created_at"
   ],
   "rows": []
  },
  "learner_settings": {
   "columns": [
    "student_id",
    "daily_goal",
    "updated_at"
   ],
   "rows": [
    {
     "student_id": "demo_student",
     "daily_goal": 3,
     "updated_at": "2026-09-07T01:55:47.730629+00:00"
    }
   ]
  }
 }
};