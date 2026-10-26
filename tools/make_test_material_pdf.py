# -*- coding: utf-8 -*-
"""生成 PDF 版测试素材：题目 + 学生作文（故意带错）。

用法（用托管 venv，不污染系统 Python）：
  /Users/linquin/.workbuddy-ai/binaries/python/envs/default/bin/python \
      tools/make_test_material_pdf.py [4|5|all]

不传参数只生成第 5 套（最新的一套）；all 生成 4 和 5。
依赖：fpdf2（`pip install fpdf2`），字体用系统自带的宋体 + Times New Roman。
产物：~/Documents/作文批改测试/第N套-题目.pdf、第N套-学生作文.pdf

为什么单独一个脚本：docx 版靠 python-docx（App 自带运行时里有），
PDF 版要 fpdf2，那个不能装进 App 的运行时（包里只该有 python-docx）。
"""
import os
import sys

from fpdf import FPDF

OUT_DIR = os.path.expanduser("~/Documents/作文批改测试")
SONG = "/System/Library/Fonts/Supplemental/Songti.ttc"
TIMES = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"


def topic_block(directions_cn, points):
    """题面：标题行 + 英文 Directions + 中文说明 + 若干要点。"""
    rows = [
        ("en", "IV. Guided Writing (25%)"),
        ("en", "Directions: Write an English composition in 120-150 words according to the "
               "instructions given below in Chinese."),
        ("cn", directions_cn),
    ]
    for i, p in enumerate(points, 1):
        rows.append(("cn", f"{i}. {p}"))
    return rows


# ---------------- 第 4 套：日记（校园义卖） ----------------
# 埋的错（12 处，见当日工作日志）：hold→held、I am→I was、There are→There were、
# many people come→coming、come→came、ask→asked、how much is…→how much … was、
# tell→told、take→took、count→counted、moving→moved、give→gave、
# 逗号粘连(it is more…)→which was、happy→happiness、wonderfull→wonderful、
# forget it→forget、more activity→more activities
TOPIC4 = topic_block(
    "假如你是明启中学高三学生李华。上周六你校在操场举办了一场校园义卖"
    "（charity sale），你作为志愿者参与其中。请用英语写一篇日记，内容须包括：",
    ["义卖的经过", "一件让你印象深刻的小事", "你的感受"],
)
ESSAY4 = [
    ("right", "June 15th, Saturday            Sunny"),
    ("body", "Today our school hold a charity sale on the playground. "
             "I am a volunteer of Class Three."),
    ("body", "We set up our stall at eight o'clock. There are many people come to the playground. "
             "A little girl come to our stall and ask me how much is the teddy bear. I tell her it was "
             "ten yuan. She take out a small purse and count the coins one by one. She said she saved the "
             "money for three months. I was very moving, so I give her a discount and she was very happy."),
    ("body", "In the end, we raised 3,200 yuan, it is more than we expected. I learned that helping "
             "others can bring us happy. This is a wonderfull day that I will never forget it."),
    ("body", "I hope our school will hold more activity like this."),
]

# ---------------- 第 5 套：通知（英语戏剧节） ----------------
# 体裁换成「通知」：有居中标题、有落款，比前四套多一层格式判断。
# 埋的错（12 处）：a English→an、will be hold→be held、Everybody are→is、
# welcomed→welcome、three part→parts、plays perform→performed、
# is aim to→is aimed at、should sent→send、are interest→interested、
# who want→wants（+缺逗号）、looking forward your→forward to your、wonderfull→wonderful
TOPIC5 = topic_block(
    "假如你是明启中学学生会主席李华。你校英语社团将于下周五举办"
    "“英语戏剧节”（English Drama Festival）。请用英语写一则通知，内容须包括：",
    ["活动的时间与地点", "活动的主要内容", "报名方式与截止时间"],
)
ESSAY5 = [
    ("center", "NOTICE"),
    ("body", "To help students learn more about English culture, our English Club will hold "
             "a English drama festival next Friday. Everybody are welcomed to join in."),
    ("body", "The festival will be hold in the school hall at 2:00 pm, and it will last about "
             "two hours. There are three part in this activity. First, we will enjoy some classic "
             "English plays perform by our members. Second, students can take part in a short play "
             "competition, which is aim to improve our spoken English. Third, a foreign teacher will "
             "give us a talk about the history of English drama. Each class should sent two students "
             "to attend the competition."),
    ("body", "If you are interest in acting, you should sign up before Wednesday. Anyone who want "
             "to join please send your name to the club office. We are looking forward your reply. "
             "Don't miss this wonderfull chance!"),
    ("right", "The Student Union"),
]

SETS = {
    "4": (TOPIC4, ESSAY4),
    "5": (TOPIC5, ESSAY5),
}


class Sheet(FPDF):
    """A4、上下 2.0 cm、左右 2.2 cm，和 docx 版素材的版心一致。"""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(left=22, top=20, right=22)
        self.set_auto_page_break(auto=True, margin=20)
        # Songti.ttc 里有 8 个字面，默认取 #0 = Songti SC **Black**（中文发胖、不像考卷）。
        # #6 才是 Songti SC Regular。fpdf2 2.8 起用 collection_font_number 指定。
        self.add_font("song", "", SONG, collection_font_number=6)
        # 字体名不能叫 "times"：会和 fpdf2 的核心字体撞名，add_font 静默失败。
        self.add_font("tsr", "", TIMES)
        self.h_line = 5.2          # 行高（mm），11 pt 正文配 5.2 约 1.3 倍

    def para(self, text, lang="cn", indent=True, align=None):
        """一段话。首行缩进靠 `write()` 实现 —— `multi_cell` 会把整块都缩进，不是首行。"""
        self.set_font("song" if lang == "cn" else "tsr", size=11)
        if align in ("right", "center"):
            self.set_x(self.l_margin)
            self.cell(0, self.h_line, text, align="R" if align == "right" else "C")
            self.ln(self.h_line)
            return
        # 中文缩两个字（22 pt ≈ 7.8 mm），英文缩 8 mm
        pad = (7.8 if lang == "cn" else 8.0) if indent else 0.0
        self.set_x(self.l_margin + pad)
        self.write(self.h_line, text)
        self.ln(self.h_line)

    def gap(self, mm=1.6):
        self.ln(mm)


def build_topic(path, rows):
    pdf = Sheet()
    pdf.add_page()
    for i, (lang, text) in enumerate(rows):
        # 题面里的英文行顶格，中文行缩进（和 docx 版一致）
        pdf.para(text, lang=lang, indent=(lang == "cn"))
        if i == 1:
            pdf.gap(1.2)
    pdf.output(path)


def build_essay(path, blocks):
    pdf = Sheet()
    pdf.add_page()
    for align, text in blocks:
        pdf.para(text, lang="en", indent=(align == "body"), align=None if align == "body" else align)
        if align == "body":
            pdf.gap(1.6)
    pdf.output(path)


def build(no):
    topic_rows, essay_blocks = SETS[no]
    t = os.path.join(OUT_DIR, f"第{no}套-题目.pdf")
    e = os.path.join(OUT_DIR, f"第{no}套-学生作文.pdf")
    build_topic(t, topic_rows)
    build_essay(e, essay_blocks)
    words = sum(len(x.split()) for a, x in essay_blocks if a == "body")
    print(f"第{no}套-题目.pdf  {os.path.getsize(t)//1024} KB")
    print(f"第{no}套-学生作文.pdf  {os.path.getsize(e)//1024} KB  正文 {words} 词")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    want = sys.argv[1] if len(sys.argv) > 1 else "5"
    for no in (["4", "5"] if want == "all" else [want]):
        build(no)
    print("目录:", OUT_DIR)


if __name__ == "__main__":
    main()
