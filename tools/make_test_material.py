# -*- coding: utf-8 -*-
"""生成端到端测试素材：题目 + 学生作文（故意带错）。
用法：Runtime/python/bin/python3.12 tools/make_test_material.py      # 生成第 1、2 套
      Runtime/python/bin/python3.12 tools/make_test_material.py 3    # 只生成第 3 套
产物：~/Documents/作文批改测试/
  第1套（投稿，AI 与作业）、第2套（书信，生活场景）、第3套（演讲稿，英语文化周）
"""
import os
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

OUT_DIR = os.path.expanduser("~/Documents/作文批改测试")

# ---------------- 第 1 套：投稿 ----------------
S1_TOPIC = [
    "IV. Guided Writing (25%)",
    "Directions: Write an English composition in 120-150 words according to the instructions "
    "given below in Chinese.",
    "假如你是明启中学高三学生李华。校英文报“Opinion”栏目正在征稿，本期主题为"
    "“高三学生该不该用 AI 工具完成作业”。请你写一篇短文投稿，内容须包括：",
    "1. 你的观点",
    "2. 你的理由",
]
S1_ESSAY = [
    "In today's rapidly developing world, AI is becoming more and more popular among students. "
    "As a Senior Three student, I think we should use AI tools to help us with our homework. "
    "Here is why.",
    "First, AI can help us save a lot of time. We have so many homework every day that sometimes "
    "we can not finish them before twelve o'clock. With AI, we can get the answer quickly and "
    "have more time to sleep.",
    "Second, AI can explain things that teachers don't have time to explain in class. For example, "
    "when I don't understand a math problem, I ask AI and it explains it step by step. This is "
    "very convenience for us.",
    "Of course, some students just copy the answers. This is wrong, because it will make us lazy "
    "and we will lost the ability to think by ourselves. But I think this problem can be solved "
    "easily, teachers can check our homework more carefully.",
    "Last but not least, AI is just a tool, it can not replace our own thinking. As we all know, "
    "the world will be full of AI in the future, so we must learn to use it.",
    "In conclusion, I strongly believe that we should use AI tools. It is not only convenient but "
    "also necessary",
    "Li Hua",
]

# ---------------- 第 2 套：书信（生活场景） ----------------
S2_TOPIC = [
    "IV. Guided Writing (25%)",
    "Directions: Write an English composition in 120-150 words according to the instructions "
    "given below in Chinese.",
    "假如你是明启中学高三学生李华，你的英国笔友 Chris 来信说下个月要来上海，想体验"
    "“最真实的本地生活”。请你回信，内容须包括：",
    "1. 推荐一个你常去的本地场所（菜市场、小面馆、公园等）",
    "2. 说明它和商场、超市有什么不同",
]
S2_ESSAY = [
    "Dear Chris,",
    "I'm so happy to hear that you will come to Shanghai next month. You asked me where can you "
    "see the real local life. I want to recommend you a small noodle shop near my home.",
    "The shop is very small, only has five tables. The boss is a uncle about sixty years old. He "
    "get up at four o'clock every morning to make the soup, and the soup need to boil for six "
    "hours. Every time I go there, he always remember my order and ask me about my study.",
    "Compare with the supermarket, this shop is completely different. In the supermarket, you just "
    "take things from the shelf and pay, nobody talk to you. But here you can sit down, listen to "
    "the neighbours talk about their life, and the boss will tell you which noodle is the best "
    "today. It is not only a place to eat, but also a place to feel the warm of the city.",
    "I suggest you go there on Sunday morning, because the market next to it is also very lively. "
    "You can see old ladies bargaining, which is very interesting. I'm sure you will like it",
    "Yours sincerely",
    "Li Ming",
]


# ---------------- 第 3 套：演讲稿（英语文化周开幕式） ----------------
S3_TOPIC = [
    "IV. Guided Writing (25%)",
    "Directions: Write an English composition in 120-150 words according to the instructions "
    "given below in Chinese.",
    "假如你是明启中学高三学生李华。下周学校将举办“英语文化周”，开幕式上你作为学生代表"
    "用英语发言。请写一篇发言稿，内容须包括：",
    "1. 你对英语学习意义的理解",
    "2. 你推荐的一项活动及理由",
    "3. 对同学们的倡议",
]
# 故意埋的错（14 处，方便批改稿有活干）：
#  has learn→learned  which connect→connects  first time go→the first time I went
#  too nervous that→so  made me confidence→confident  I become→became
#  a English→an  many activity→activities  I strong recommend→strongly
#  Because 从句单独成句  no matter you are→whether  oportunity→opportunity
#  looking forward to see→seeing  Thank you for your listening→Thanks for listening
S3_ESSAY = [
    "Good morning, everyone! I'm Li Hua from Class Three, Grade Three. It's my great honor "
    "to speak here.",
    "As a student who has learn English for six years, I want to share my understanding of it. "
    "English is not only a tool of communication, but also a bridge which connect different "
    "cultures.",
    "I still remember when I first time go to the English corner, I was too nervous that I "
    "couldn't say a word. A teacher encouraged me, and it made me confidence. From then on, "
    "I become more and more interested in English.",
    "This week our school will hold a English culture week. There are many activity waiting for "
    "you. I strong recommend the singing contest, because you can not only practise your spoken "
    "English, but also make friends. Besides, it is a good oportunity to show your talent, no "
    "matter you are good at singing or not.",
    "Let's take part in them actively. I'm looking forward to see you there. Thank you for your "
    "listening!",
]


def new_doc():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    sec.left_margin = sec.right_margin = Cm(2.2)
    return doc


def add(doc, text, indent=True, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Pt(size * 2) if indent else Pt(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.15
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    r._element.rPr.rFonts.set(qn("w:cs"), "Times New Roman")
    return p


def build(topic, essay, topic_name, essay_name, signature=True):
    d = new_doc()
    for i, t in enumerate(topic):
        add(d, t, indent=(i >= 2))
    d.save(os.path.join(OUT_DIR, topic_name))

    d = new_doc()
    if signature:
        for t in essay[:-1]:
            add(d, t)
        # 最后一段是署名，右对齐不缩进
        add(d, essay[-1], indent=False, align=WD_ALIGN_PARAGRAPH.RIGHT)
    else:
        # 演讲稿没有署名，整篇都是正文
        for t in essay:
            add(d, t)
    d.save(os.path.join(OUT_DIR, essay_name))

    print(f"{topic_name:28s} {essay_name:28s} 正文 {sum(len(t.split()) for t in essay)} 词")


# 无参数生成第 1、2 套（保持原行为）；带数字参数只生成那一套，免得覆盖已有素材
# —— 第 2 套的 docx 里后来插过图片，重跑会把它冲掉。
want = sys.argv[1] if len(sys.argv) > 1 else "all"

if want in ("all", "1"):
    build(S1_TOPIC, S1_ESSAY, "第1套-题目.docx", "第1套-学生作文.docx")
if want in ("all", "2"):
    build(S2_TOPIC, S2_ESSAY, "第2套-题目.docx", "第2套-学生作文.docx")
if want in ("all", "3"):
    build(S3_TOPIC, S3_ESSAY, "第3套-题目.docx", "第3套-学生作文.docx", signature=False)
print("目录:", OUT_DIR)
