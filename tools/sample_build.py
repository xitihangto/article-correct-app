# -*- coding: utf-8 -*-
"""格式冒烟测试：按《作文批改规则.md》的版式生成一份最小批改稿。
用法：EssayCorrect --runpython tools/sample_build.py
只为验证 run 级字体/字号/颜色、A4 页边距、五部分结构，不追求内容质量。
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BLACK = RGBColor(0x00, 0x00, 0x00)
RED = RGBColor(0xFF, 0x00, 0x00)
BLUE = RGBColor(0x1F, 0x4E, 0x79)


def style_run(run, size, color=BLACK, bold=False, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
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


def h1(doc, text):
    """章节标题：12pt 加粗，段前 8pt、段后 0"""
    p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=8, after=0)
    style_run(p.add_run(text), 12, bold=True)


def h2(doc, text):
    """二级标题：11pt 加粗，段前 6pt、段后 0"""
    p = para(doc, WD_ALIGN_PARAGRAPH.LEFT, Pt(0), before=6, after=0)
    style_run(p.add_run(text), 11, bold=True)


def note(doc, text, align=WD_ALIGN_PARAGRAPH.LEFT, before=0, after=0):
    """说明性小字：9pt 斜体"""
    p = para(doc, align, Pt(0), before=before, after=after)
    style_run(p.add_run(text), 9, italic=True)


def body(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = para(doc, align)
    style_run(p.add_run(text), 10.5)
    return p


def body_flat(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """题面里的英文行（Guided Writing / Directions）：顶格不缩进"""
    p = para(doc, align, Pt(0))
    style_run(p.add_run(text), 10.5)
    return p


def gap(doc):
    """空段落：只在 4 个章节交界 + 纠错|补充意见之间各留一个，共 5 个"""
    doc.add_paragraph()


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.0)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.header_distance = sec.footer_distance = Cm(1.27)

# 大标题 / 副标题
p = para(doc, WD_ALIGN_PARAGRAPH.CENTER, Pt(0), before=0, after=0)
style_run(p.add_run("高三英语写作训练《AI 时代的语言学习》批改与升格（终稿版）"), 14, bold=True)
note(doc, "书信（电子邮件）；黑色原文＋红色＝需改处；小号蓝色〔〕＝终稿与意见的对应编号；"
          "未标注的句子为原文保留句", align=WD_ALIGN_PARAGRAPH.CENTER, before=2, after=4)

# 一、作文要求（英文行顶格，中文题面缩进 12pt）
h1(doc, "一、作文要求")
body_flat(doc, "Guided Writing")
body_flat(doc, "Directions: Write an English composition in 120-150 words according to the "
               "instructions given below in Chinese.")
body(doc, "假如你是明启中学高三学生李华，收到国外朋友 Bill 的邮件，说他有打算要好好学习汉语……")
body(doc, "1. 你的立场")
body(doc, "2. 你的理由")
gap(doc)

# 二、学生作文
h1(doc, "二、学生作文（原文完整转录，保留原有语言表达与错误）")
body(doc, "Dear Bill,")
body(doc, "I'm thrilled to hear about your interest in learning Chinese. I strongly support you.")
body(doc, "Firstly, despite the significant strides in AI translation technology, it still lack of "
          "ability to capture the emotion.")
body(doc, "Yours sincerely,")
note(doc, "（正文共 34 词；全文无署名。）", before=2)
gap(doc)

# 三、修改意见
h1(doc, "三、修改意见（纠错 ＋ 补充意见）")
note(doc, "【纠错】原文的语言硬伤，必须改。")
note(doc, "【补充意见】原文没错、但补上能更充实更贴题的内容。")
h2(doc, "（一）纠错")

p = body(doc, "")
style_run(p.add_run("纠1·主谓一致　Firstly, despite the significant strides in AI translation "
                    "technology, it still "), 10.5)
style_run(p.add_run("lack of ability"), 10.5, RED)
style_run(p.add_run(" to capture the emotion.　→　修改为：it still fails to capture the emotion."
                    "　说明：① lack 是名词/动词，不能接 of ability 作谓语；② still 后需实义动词，"
                    "改为 fails to capture。"), 10.5)

p = body(doc, "")
style_run(p.add_run("纠2·用词过重　I'm "), 10.5)
style_run(p.add_run("thrilled"), 10.5, RED)
style_run(p.add_run(" to hear about your interest in learning Chinese.　→　修改为：I'm delighted "
                    "to hear about your interest in learning Chinese.　说明：thrilled 意为"
                    "“极其兴奋”，朋友只是说想学语言，语域过重，改用 delighted 更贴合书信分寸。"), 10.5)

gap(doc)
h2(doc, "（二）补充意见（原文没错，是为了充实内容、提升表达而增加的）")
body(doc, "意1·给“AI 翻不出的东西”一个具体例证　位置：第二段，capture the emotion 之后。"
          "　增加：Take the word “homesick”: no engine can tell you why it stings.　"
          "说明：原文只有论断没有例证，补一个具体词例，扣住“语言承载情感”这一理由。")
gap(doc)

# 四、终稿
h1(doc, "四、终稿")
note(doc, "（唯一版本，38 词；每句后小号蓝色〔〕为该句落实的意见编号。）")
p = body(doc, "")
style_run(p.add_run("Dear Bill,"), 10.5)
p = body(doc, "")
style_run(p.add_run("I'm delighted to hear about your interest in learning Chinese."), 10.5)
style_run(p.add_run("〔纠2〕"), 8.5, BLUE)
style_run(p.add_run(" Admittedly, AI translation has made remarkable progress, yet it still fails to "
                    "capture the emotion."), 10.5)
style_run(p.add_run("〔纠1、意1〕"), 8.5, BLUE)
p = para(doc, WD_ALIGN_PARAGRAPH.RIGHT)
style_run(p.add_run("Yours sincerely,"), 10.5)
p = para(doc, WD_ALIGN_PARAGRAPH.RIGHT)
style_run(p.add_run("Li Hua"), 10.5)
gap(doc)

# 五、参考翻译
h1(doc, "五、参考翻译")
note(doc, "（终稿的中文译文，仅供理解改后大意，不作批改依据。）")
body(doc, "亲爱的比尔：很高兴听说你有兴趣学中文。诚然，人工智能翻译进步很大，但它仍然捕捉不到"
          "语言里的情感——比如“想家”这个词，任何引擎都说不清它为什么让人心里一紧。")

# 文末提示行：本稿来源 + 自动纠正的识别错误
note(doc, "（提示：本稿由电子稿转录。已自动纠正的识别错误：① 原句号后缺空格，终稿已按英文规范"
          "补齐。以上均不计为批改意见。）", before=8)

out = "AI时代的语言学习-批改与升格.docx"
doc.save(out)
print("saved:", out)
print("paragraphs:", len(doc.paragraphs))
