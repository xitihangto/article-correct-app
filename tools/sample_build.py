# -*- coding: utf-8 -*-
"""格式冒烟测试：按《作文批改规则.md》的版式生成一份最小批改稿。
用法：EssayCorrect --runpython tools/sample_build.py
只为验证 run 级字体/字号/颜色、A4 页边距、四段结构，不追求内容质量。
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BLACK = RGBColor(0x00, 0x00, 0x00)
RED = RGBColor(0xFF, 0x00, 0x00)
BLUE = RGBColor(0x1F, 0x4E, 0x79)


def style_run(run, size, color=BLACK, bold=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run._element.rPr.rFonts.set(qn("w:cs"), "Times New Roman")


def para(doc, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=Pt(12), before=0, after=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = indent
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = 1.15
    return p


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.0)
sec.left_margin = sec.right_margin = Cm(2.2)

# 主标题 / 副标题
p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, Pt(0))
style_run(p.add_run("高三英语写作训练《AI 时代的语言学习》批改与升格"), 14, bold=True)
p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, Pt(0), before=6, after=4)
style_run(p.add_run("书信（电子邮件）；黑色原文＋红色＝需改处；小号蓝色〔〕＝终稿与意见的对应编号；"
                    "未标注的句子为原文保留句"), 9)

# 一、作文要求
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=6)
style_run(p.add_run("一、作文要求"), 12, bold=True)
for line in ["IV. Guided Writing (25%)",
             "Directions: Write an English composition in 120-150 words according to the instructions given below in Chinese.",
             "假如你是明启中学高三学生李华，收到国外朋友 Bill 的邮件，说他有打算要好好学习汉语……",
             "1. 你的立场",
             "2. 你的理由"]:
    p = para(doc, WD_ALIGN_PARAGRAPH.JUSTIFY, Pt(0))
    style_run(p.add_run(line), 10.5)

# 二、学生作文
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=6)
style_run(p.add_run("二、学生作文（手写原文完整转录，保留原有语言表达与错误）"), 12, bold=True)
for line in ["Dear Bill,",
             "I'm thrilled to hear about your interest in learning Chinese. I strongly support you.",
             "Firstly, despite the significant strides in AI translation technology, it still lack of ability to capture the emotion."]:
    p = para(doc)
    style_run(p.add_run(line), 10.5)
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=2)
style_run(p.add_run("（正文共 32 词；手写原文完整转录，保留原有语言表达与错误；全文无结束语与署名。）"), 9)

# 三、修改意见
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=6)
style_run(p.add_run("三、修改意见（纠错 ＋ 补充意见）"), 12, bold=True)
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0))
style_run(p.add_run("【纠错】原文的语言硬伤，必须改。"), 9)
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0))
style_run(p.add_run("【补充意见】原文没错、但补上能更充实更贴题的内容。"), 9)

p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=6)
style_run(p.add_run("（一）纠错"), 11, bold=True)

p = para(doc)
style_run(p.add_run("纠1·主谓一致　Firstly, despite the significant strides in AI translation technology, it still "), 10.5)
style_run(p.add_run("lack of ability"), 10.5, RED)
style_run(p.add_run(" to capture the emotion.　→　修改为：it still fails to capture the emotion."), 10.5)

p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=6)
style_run(p.add_run("（二）补充意见（原文没错，是为了充实内容、提升表达而增加的）"), 11, bold=True)

p = para(doc)
style_run(p.add_run("意1·给“AI 翻不出的东西”一个具体例证　位置：第二段，emotion 之后。"
                    "　增加：Take the word “homesick”: no engine can tell you why it stings."), 10.5)

# 四、终稿
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=8)
style_run(p.add_run("四、终稿"), 12, bold=True)
p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0))
style_run(p.add_run("（唯一版本，34 词；每句后小号蓝色〔〕为该句落实的意见编号。）"), 9)

p = para(doc)
style_run(p.add_run("Dear Bill,"), 10.5)
p = para(doc)
style_run(p.add_run("I'm delighted to hear that you're planning to learn Chinese."), 10.5)
style_run(p.add_run("〔纠1〕"), 8.5, BLUE)
style_run(p.add_run(" Admittedly, AI translation has made remarkable progress, yet it still fails to capture the emotion."), 10.5)
style_run(p.add_run("〔意1〕"), 8.5, BLUE)
p = para(doc)
style_run(p.add_run("Yours sincerely,"), 10.5)
p = para(doc)
style_run(p.add_run("Li Hua"), 10.5)

out = "AI时代的语言学习-批改与升格.docx"
doc.save(out)
print("saved:", out)
print("paragraphs:", len(doc.paragraphs))
