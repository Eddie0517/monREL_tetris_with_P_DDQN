"""
Tạo slide thuyết trình (.pptx) theo style MoE-MMR (nền trắng, tiêu đề xám căn giữa,
thanh xanh dưới tiêu đề, thẻ xanh nhạt có số tròn) + speaker notes tiếng Việt.
  python tools/make_slides.py
Ghi ra: presentation/P-DDQN_Tetris_WhatMatters.pptx
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(ROOT, "paper write", "LaTeX2e+Proceedings+Template+ZIP (1)", "figures", "png")
LOGO = os.path.join(ROOT, "presentation", "assets", "fpt_logo.png")
OUT = os.path.join(ROOT, "presentation", "P-DDQN_Tetris_WhatMatters.pptx")

FONT = "Arial"
GRAY_TITLE = RGBColor(0x6E, 0x68, 0x63)
INK = RGBColor(0x2B, 0x2B, 0x2B)
BODY = RGBColor(0x33, 0x33, 0x33)
MUTED = RGBColor(0x6E, 0x68, 0x63)
BAR = RGBColor(0x3A, 0xA9, 0xEE)
CIRCLE = RGBColor(0x2A, 0xA1, 0xE8)
HEAD = RGBColor(0x1E, 0x8A, 0xD6)
CARD = RGBColor(0xE9, 0xF4, 0xFD)
CARD_LINE = RGBColor(0xD4, 0xE9, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
TBL_HEAD = RGBColor(0x1E, 0x88, 0xD4)
TBL_ALT = RGBColor(0xEE, 0xF6, 0xFD)
HILITE = RGBColor(0xD6, 0xEC, 0xFB)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- helpers
def text(slide, x, y, w, h, runs, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.15, margin=0.0):
    """runs: str | list of paragraphs; a paragraph = str | list of (text, {bold,color,size})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        parts = para if isinstance(para, list) else [(para, {})]
        for t, o in parts:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name = FONT
            f.size = Pt(o.get("size", size))
            f.bold = o.get("bold", bold)
            f.color.rgb = o.get("color", color)
    return tb


def rect(slide, x, y, w, h, fill, line=None, rounded=False, radius=0.08):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                 Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(1)
    if rounded:
        shp.adjustments[0] = radius
    shp.shadow.inherit = False
    return shp


def circle(slide, x, y, d, label, size=16):
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    c.fill.solid()
    c.fill.fore_color.rgb = CIRCLE
    c.line.fill.background()
    c.shadow.inherit = False
    tf = c.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(label)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = FONT, Pt(size), True, WHITE
    return c


def header(slide, title, size=36):
    text(slide, 0.5, 0.28, 12.33, 0.8, title, size=size, color=GRAY_TITLE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(slide, 0.3, 1.12, 12.73, 0.07, BAR)


def card(slide, x, y, w, h, num, heading, body, body_size=15, formula=None, head_size=19, formula_size=None):
    rect(slide, x, y, w, h, CARD, CARD_LINE, rounded=True, radius=0.05)
    cy = y + 0.25
    if num is not None:
        circle(slide, x + 0.25, cy, 0.42, num)
        text(slide, x + 0.82, cy - 0.04, w - 1.05, 0.5, heading, size=head_size, color=HEAD, bold=True,
             anchor=MSO_ANCHOR.MIDDLE)
        cy += 0.62
    else:
        text(slide, x + 0.25, cy, w - 0.5, 0.45, heading, size=head_size, color=HEAD, bold=True)
        cy += 0.55
    if formula:
        rect(slide, x + 0.25, cy, w - 0.5, 0.5, WHITE, RGBColor(0xC9, 0xDF, 0xF0), rounded=True, radius=0.15)
        text(slide, x + 0.35, cy, w - 0.7, 0.5, formula, size=formula_size or body_size, color=INK, anchor=MSO_ANCHOR.MIDDLE)
        cy += 0.62
    text(slide, x + 0.25, cy, w - 0.5, y + h - cy - 0.15, body, size=body_size, color=BODY, spacing=1.2)


def table(slide, x, y, w, rows, col_w, size=13, row_h=0.36, bold_rows=(), hilite_rows=(), aligns=None):
    nr, nc = len(rows), len(rows[0])
    shp = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    tbl = shp.table
    tbl.first_row = True
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i in range(nr):
        tbl.rows[i].height = Inches(row_h)
        for j in range(nc):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if i == 0:
                cell.fill.fore_color.rgb = TBL_HEAD
            elif i in hilite_rows:
                cell.fill.fore_color.rgb = HILITE
            else:
                cell.fill.fore_color.rgb = TBL_ALT if i % 2 == 0 else WHITE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = (aligns[j] if aligns else (PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER))
            r = p.add_run()
            r.text = str(rows[i][j])
            r.font.name, r.font.size = FONT, Pt(size)
            r.font.bold = i == 0 or i in bold_rows
            r.font.color.rgb = WHITE if i == 0 else INK
    return shp


def picture(slide, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return slide.shapes.add_picture(path, Inches(x), Inches(y), **kw)


def fit_picture(slide, path, x, y, box_w, box_h):
    """Ảnh vừa khung, giữ tỉ lệ, căn giữa."""
    from PIL import Image
    iw, ih = Image.open(path).size
    s = min(box_w / iw, box_h / ih)
    w, h = iw * s, ih * s
    return picture(slide, path, x + (box_w - w) / 2, y + (box_h - h) / 2, w=w, h=h)


def notes(slide, s):
    slide.notes_slide.notes_text_frame.text = s.strip()


def new(title=None):
    s = prs.slides.add_slide(BLANK)
    if title:
        header(s, title)
    return s


# ================================================================ slides
PIECE = RGBColor(0xF5, 0xA0, 0x0F)
BRICK = RGBColor(0x97, 0xA3, 0xB6)
EMPTY = RGBColor(0xE6, 0xEA, 0xF0)
COLLAPSE_PNG = os.path.join(ROOT, "presentation", "assets", "collapse_curves.png")


def make_collapse_png():
    """Đường cong Avg50 của 4 run bị sụp (đọc train.log trong result/)."""
    import re
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    runs = [("target", "expected_sarsa_s0", "#eda100", "Expected SARSA, seed 0"),
            ("target", "qlearning_s2", "#eb6834", "Q-learning, seed 2"),
            ("target", "baseline_s0", "#2a78d6", "SARSA, seed 0"),
            ("hparam", "gamma_095_s2", "#52514e", "γ = 0.95, seed 2")]
    fig, ax = plt.subplots(figsize=(7.4, 4.3), dpi=200)
    for g, run, col, lab in runs:
        f = os.path.join(ROOT, "result", f"results_{g}", f"results_{g}", "checkpoints", run, "train.log")
        pts = [(int(m[1]), float(m[2])) for m in
               (re.match(r"Ep\s+(\d+)/\d+.*Avg50:\s*([\d.]+)", l) for l in open(f, encoding="utf-8", errors="ignore")) if m]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=1.8, label=lab)
    ax.axhspan(560, 620, color="#dfeefb", zorder=0)
    ax.text(1010, 600, "episode cap (≈ 600 lines)", fontsize=9, color="#52514e", va="center")
    ax.set_xlim(1000, 2005)
    ax.set_ylim(-10, 630)
    ax.set_xlabel("Training episode", fontsize=11)
    ax.set_ylabel("Avg50 lines (training)", fontsize=11)
    ax.grid(color="#e4e4e0", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=4)
    fig.tight_layout()
    fig.savefig(COLLAPSE_PNG)
    plt.close(fig)


make_collapse_png()


# 1 ─ Cover
s = new()
picture(s, LOGO, 0.55, 0.28, h=0.88)
text(s, 3.2, 0.48, 9.6, 0.5, "Reinforcement Learning  |  Placement-Based Deep Value Learning for Tetris",
     size=15, color=INK, bold=True, anchor=MSO_ANCHOR.MIDDLE)
rect(s, 0.3, 1.35, 12.73, 0.07, BAR)
text(s, 0.6, 1.6, 12.13, 1.4, ["Off-Policy Targets, Not Reward Shaping:", "What Makes Placement-Based Deep Value Learning Work in Tetris"],
     size=28, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.1)
text(s, 1.0, 3.15, 11.33, 0.5, "A Multi-Seed Study of Reward Shaping, Hyper-Parameters and TD Targets",
     size=20, color=HEAD, align=PP_ALIGN.CENTER)
rect(s, 0.3, 3.85, 12.73, 0.07, BAR)
text(s, 1.0, 4.25, 11.33, 0.4, "Team members", size=16, color=MUTED, bold=True, align=PP_ALIGN.CENTER)
members = [("Lê Đặng Duy Khang", "SE192416"), ("Đặng Lan Thảo", "SE190575"),
           ("Trần Gia Bảo", "SE190316"), ("Nguyễn Trọng Nhân", "SE192003")]
for k, (name, sid) in enumerate(members):
    x = 0.9 + k * 2.95
    text(s, x, 4.85, 2.65, 0.45, name, size=18, color=INK, align=PP_ALIGN.CENTER)
    text(s, x, 5.3, 2.65, 0.4, sid, size=14, color=MUTED, align=PP_ALIGN.CENTER)
notes(s, """
Kính chào thầy cô và các bạn. Nhóm em gồm bốn thành viên: Lê Đặng Duy Khang, Đặng Lan Thảo, Trần Gia Bảo và Nguyễn Trọng Nhân. Hôm nay nhóm em xin trình bày đề tài “Off-Policy Targets, Not Reward Shaping: What Makes Placement-Based Deep Value Learning Work in Tetris”, tạm dịch là: mục tiêu học off-policy, chứ không phải hàm thưởng, mới là điều giúp AI học chơi Tetris dựa trên vị trí đặt khối.

Ở báo cáo tiến độ trước, nhóm đã xây dựng agent P-DDQN chơi Tetris. Ở giai đoạn này, thay vì chỉ báo cáo một con số, nhóm thực hiện một nghiên cứu có kiểm soát gồm 84 lần huấn luyện với nhiều seed khác nhau, để trả lời câu hỏi: trong ba yếu tố là hàm thưởng, siêu tham số và cách tính mục tiêu học (TD target), yếu tố nào thật sự quyết định kết quả.
""")

# 1b ─ Contents / outline
s = new("Contents")
outline = [("Motivation & Contribution", "Why revisit P-DDQN, and our four contributions"),
           ("Tetris as an RL Problem", "Placements, board features and the shaped reward"),
           ("Method", "Afterstate value network and the four TD targets"),
           ("Experimental Setup", "84 runs: reward, hyper-parameter and TD-target groups"),
           ("Results", "Reference agents, reward weights, hyper-parameters, TD targets"),
           ("Stability & Conclusion", "Collapse, CPU vs GPU, trade-off, limitations")]
for k, (h, b) in enumerate(outline):
    col, row = k % 2, k // 2
    x, y = 0.6 + col * 6.18, 1.55 + row * 1.75
    rect(s, x, y, 5.95, 1.55, CARD, CARD_LINE, rounded=True, radius=0.08)
    circle(s, x + 0.3, y + 0.43, 0.7, k + 1, size=22)
    text(s, x + 1.25, y + 0.25, 4.5, 0.5, h, size=21, color=HEAD, bold=True)
    text(s, x + 1.25, y + 0.8, 4.5, 0.6, b, size=15, color=BODY)
notes(s, """
Bài trình bày của nhóm gồm sáu phần.

Phần một là động lực và đóng góp: vì sao nhóm xem lại agent P-DDQN và bốn đóng góp chính.

Phần hai trình bày Tetris dưới dạng một bài toán học tăng cường: agent liệt kê các vị trí đặt khối, nén bàn cờ thành bốn đặc trưng và nhận hàm thưởng như thế nào.

Phần ba là phương pháp: mạng giá trị afterstate và bốn cách tính mục tiêu học, gồm SARSA, Q-learning, Double Q và Expected SARSA.

Phần bốn là thiết lập thí nghiệm với 84 lần huấn luyện, chia thành ba nhóm.

Phần năm là kết quả: các agent tham chiếu, ảnh hưởng của trọng số reward, siêu tham số và cách tính mục tiêu học.

Phần cuối nói về độ ổn định, gồm hiện tượng sụp và sự khác biệt giữa CPU và GPU, sau đó là sự đánh đổi, các hạn chế và kết luận.
""")

# 2 ─ Motivation
s = new("Motivation & Problem")
text(s, 0.8, 1.45, 11.7, 0.8,
     "Our P-DDQN agent reached 287.5 lines in the progress report, but which design choices produced "
     "that number, and how reliable is it?", size=18, color=INK)
items = [("Single-seed reporting",
          "Placement-based DRL agents for Tetris are usually reported from one training run, although RL results vary strongly across seeds."),
         ("Unverified update rule",
          "The agent is described as Double DQN, but the TD target it actually computes had never been checked against the theory."),
         ("Credit given to reward shaping",
          "The hole, bumpiness and height weights are hand-tuned and assumed to drive learning, yet their effect was never measured.")]
for k, (h, b) in enumerate(items):
    y = 2.45 + k * 1.55
    rect(s, 0.8, y, 11.73, 1.35, CARD, CARD_LINE, rounded=True, radius=0.08)
    circle(s, 1.1, y + 0.45, 0.45, k + 1)
    text(s, 1.85, y + 0.17, 10.4, 0.45, h, size=20, color=HEAD, bold=True)
    text(s, 1.85, y + 0.62, 10.4, 0.65, b, size=15, color=BODY)
notes(s, """
Trước hết là động lực của nghiên cứu. Ở báo cáo tiến độ, agent P-DDQN của nhóm đạt trung bình 287,5 hàng mỗi ván. Nhưng con số đó đặt ra hai câu hỏi: những lựa chọn thiết kế nào thật sự tạo ra kết quả đó, và kết quả đó có đáng tin không.

Nhóm nhận thấy ba vấn đề. Thứ nhất, các agent Tetris dạng này thường chỉ được báo cáo từ một lần huấn luyện duy nhất, trong khi học tăng cường dao động rất mạnh theo seed, tức là theo yếu tố ngẫu nhiên. Thứ hai, agent được gọi là Double DQN, nhưng chưa ai kiểm tra công thức cập nhật trong code có đúng là Double DQN hay không. Thứ ba, các trọng số trong hàm thưởng như phạt lỗ, phạt gồ ghề, phạt chiều cao được chỉnh tay và mặc định là quan trọng, nhưng chưa từng được đo xem chúng ảnh hưởng thế nào.

Nghiên cứu này được thiết kế để trả lời cả ba vấn đề đó.
""")

# 3 ─ Contribution
s = new("Our Contribution")
contrib = [("Correct diagnosis", "The implemented update bootstraps from the ε-greedy choice: it is SARSA on afterstates, not Double DQN."),
           ("Three new TD targets", "Afterstate Q-learning, Double Q-learning and Expected SARSA, computed from all candidate placements of the next piece."),
           ("84-run controlled study", "28 configurations × 3 seeds over reward weights, hyper-parameters and TD targets, under one fixed evaluation protocol."),
           ("Fast, exact tooling", "A vectorised environment 2.5× faster and bit-exact against the original, plus resumable cloud sweep notebooks.")]
for k, (h, b) in enumerate(contrib):
    x = 0.6 + k * 3.1
    rect(s, x, 1.6, 2.9, 4.9, CARD, CARD_LINE, rounded=True, radius=0.05)
    circle(s, x + 0.3, 1.95, 0.55, k + 1, size=18)
    text(s, x + 0.3, 2.7, 2.35, 0.9, h, size=20, color=HEAD, bold=True, spacing=1.05)
    text(s, x + 0.3, 3.6, 2.35, 2.7, b, size=15, color=BODY, spacing=1.25)
notes(s, """
Nghiên cứu có bốn đóng góp chính.

Thứ nhất là chẩn đoán đúng phương pháp. Khi đọc kỹ code, nhóm phát hiện công thức cập nhật lấy giá trị của nước đi mà chính sách ε-greedy thực sự chọn ở bước sau. Về lý thuyết, đó là SARSA trên afterstate, không phải Double DQN như tên gọi.

Thứ hai, dựa trên bài giảng 2.8 về Q-learning và 2.9 về Expected SARSA, nhóm xây dựng ba cách tính mục tiêu học mới: Q-learning, Double Q-learning và Expected SARSA. Môi trường đã tính sẵn mọi vị trí đặt của khối kế tiếp, nên chỉ cần lưu thêm vào bộ nhớ là dùng được.

Thứ ba là một nghiên cứu có kiểm soát gồm 84 lần huấn luyện: 28 cấu hình, mỗi cấu hình 3 seed, chia thành ba nhóm thí nghiệm, tất cả đánh giá theo cùng một quy trình.

Thứ tư là công cụ: nhóm viết lại môi trường Tetris nhanh hơn 2,5 lần nhưng cho kết quả giống từng bit so với bản gốc, cùng các notebook chạy trên Kaggle có thể chạy tiếp khi bị ngắt.
""")

# 4 ─ Overview (pipeline)
s = new("Placement-Based Afterstate Learning")
fit_picture(s, os.path.join(FIG, "fig_pipeline.png"), 0.9, 1.45, 11.5, 4.9)
text(s, 0.8, 6.55, 11.73, 0.5,
     "(1) enumerate placements    (2) score afterstates    (3) ε-greedy action    (4) learn from replay with a TD target",
     size=13, color=MUTED, align=PP_ALIGN.CENTER)
notes(s, """
Đây là sơ đồ tổng quan của agent, gồm hai vòng lặp.

Vòng trên là vòng chơi. Môi trường Tetris đưa ra khối hiện tại. Agent không bấm phím trái phải mà liệt kê tất cả các vị trí có thể đặt khối, tức là mọi cách xoay nhân mọi cột. Với mỗi vị trí, nó hình dung bàn cờ sau khi đặt, gọi là afterstate, rồi tóm tắt bàn cờ đó bằng bốn đặc trưng. Mạng online chấm điểm từng afterstate, và chính sách ε-greedy chọn vị trí điểm cao nhất, thỉnh thoảng chọn ngẫu nhiên để khám phá.

Vòng dưới là vòng học. Mỗi bước đi được lưu vào replay buffer. Agent rút ngẫu nhiên các mẫu từ bộ nhớ, dùng target network (một bản sao của mạng online, cập nhật định kỳ mỗi 10 ván) để tính TD target, rồi cập nhật mạng online bằng loss.

Điểm quan trọng nhất: bốn phương pháp nhóm so sánh có toàn bộ hệ thống giống hệt nhau, chỉ khác đúng một khối, là khối TD target màu vàng.
""")

# 5a ─ Enumerating placements (adapted from progress report)
s = new("Enumerating Every Placement")
rect(s, 0.6, 1.45, 12.13, 1.2, RGBColor(0x14, 0x21, 0x3D), rounded=True, radius=0.1)
text(s, 0.9, 1.5, 11.6, 0.35, "NUMBER OF LEGAL PLACEMENTS OF THE CURRENT PIECE", size=12, color=RGBColor(0x7F, 0xD8, 0xFF), bold=True)
text(s, 0.9, 1.8, 11.6, 0.5, "K = Σᵣ (10 − wᵣ + 1)  −  placements that overflow the top", size=26, color=WHITE, bold=True)
text(s, 0.9, 2.28, 11.6, 0.35, "A placement is a pair (rotation r, left column x); wᵣ = width of rotation r;  K ≤ 34", size=13,
     color=RGBColor(0xCF, 0xDD, 0xEA))
rect(s, 0.6, 2.9, 7.4, 3.85, CARD, CARD_LINE, rounded=True, radius=0.05)
text(s, 0.85, 3.0, 7.0, 0.4, "Example: the L piece has 4 rotations", size=17, color=HEAD, bold=True)
L_ROT = [["..#", "###"], ["#.", "#.", "##"], ["###", "#.."], ["##", ".#", ".#"]]
cell = 0.24
for k, shape in enumerate(L_ROT):
    bx = 0.95 + k * 1.75
    h = len(shape)
    for i, row in enumerate(shape):
        for j, c in enumerate(row):
            if c == "#":
                rect(s, bx + j * cell, 3.55 + (3 - h + i) * cell, cell - 0.02, cell - 0.02, PIECE)
    w = len(shape[0])
    text(s, bx - 0.05, 4.35, 1.6, 0.3, f"r{k} · width {w}", size=13, color=INK, bold=True)
    text(s, bx - 0.05, 4.65, 1.6, 0.3, [[(f"10 − {w} + 1 = ", {}), (str(11 - w), {"bold": True, "color": RGBColor(0xC2, 0x5E, 0x00)})]],
         size=13, color=BODY)
text(s, 0.85, 5.15, 7.0, 0.45, "K = 8 + 9 + 8 + 9 = 34", size=22, color=INK, bold=True)
text(s, 0.85, 5.65, 7.0, 1.0, "No rotation can overflow while the stack is low, so all 34 placements are legal. "
     "K = 0 means the next piece has no legal placement: the game is lost.", size=13, color=BODY, spacing=1.2)
rows = [["Piece", "Rotations (widths)", "Max K"], ["O", "1 (2)", "9"], ["I", "2 (4, 1)", "7 + 10 = 17"],
        ["S, Z", "2 (3, 2)", "8 + 9 = 17"], ["T, J, L", "4 (3, 2, 3, 2)", "8 + 9 + 8 + 9 = 34"]]
table(s, 8.3, 2.9, 4.43, rows, [1.0, 1.55, 1.88], size=13, row_h=0.55, hilite_rows=(4,))
text(s, 8.3, 5.85, 4.43, 0.9, "19 distinct rotations in total: O never changes shape; I, S and Z repeat after 180°.",
     size=13, color=BODY, spacing=1.2)
notes(s, """
Trước khi vào mạng nơ-ron, nhóm giải thích agent “nhìn” Tetris như thế nào. Thay vì bấm phím, ở mỗi lượt agent liệt kê mọi cách đặt khối đang cầm. Một cách đặt là một cặp: góc xoay r và cột mép trái x.

Số cách đặt hợp lệ K tính bằng: với mỗi góc xoay, số cột có thể đặt là 10 trừ bề ngang của khối cộng 1; cộng lại cho mọi góc xoay, rồi trừ đi những cách làm khối tràn khỏi đỉnh.

Ví dụ khối L có 4 góc xoay với bề ngang 3, 2, 3, 2, nên có 8, 9, 8, 9 cách, tổng cộng 34. Đây cũng là con số lớn nhất: khối T, J, L có 34 cách; khối I, S, Z có 17; khối O chỉ có 9. Khi K bằng 0, tức khối kế tiếp không còn chỗ đặt, thì thua ván.

Như vậy mỗi lượt agent chỉ phải chọn trong tối đa 34 lựa chọn, thay vì một chuỗi dài các phím bấm. Đây là lý do phương pháp này học nhanh hơn nhiều so với điều khiển từng phím.
""")

# 5b ─ Four board features (adapted from progress report)
s = new("Four Board Features: a Whole Board in 4 Numbers")
rect(s, 0.6, 1.45, 6.3, 5.35, CARD, CARD_LINE, rounded=True, radius=0.05)
text(s, 0.85, 1.55, 5.9, 0.35, "Example: dropping an L into columns 9–10", size=16, color=HEAD, bold=True)
BEFORE = ["..........", "..........", "..ggg...oo", "gghggg.ggo", "gggggggggo"]
AFTER = ["..........", "..........", "..........", "..ggg...oo", "gghggg.ggo"]


def board(slide, x, y, grid, heights, phi, label, cell=0.255, full_row=None):
    text(slide, x, y, 2.8, 0.3, label, size=12, color=INK, bold=True)
    gy = y + 0.38
    for i, row in enumerate(grid):
        for j, c in enumerate(row):
            fill = {"g": BRICK, "o": PIECE, "h": RGBColor(0xFD, 0xE4, 0xE4)}.get(c, EMPTY)
            r_ = rect(slide, x + j * cell, gy + i * cell, cell - 0.025, cell - 0.025, fill)
            if c == "h":
                r_.line.color.rgb = RGBColor(0xE0, 0x3E, 0x3E)
                r_.line.width = Pt(1.5)
    if full_row is not None:
        fr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x - 0.04), Inches(gy + full_row * cell - 0.04),
                                    Inches(10 * cell + 0.05), Inches(cell + 0.05))
        fr.fill.background()
        fr.line.color.rgb = RGBColor(0x1B, 0xAF, 0x7A)
        fr.line.width = Pt(2)
    for j, hv in enumerate(heights):
        text(slide, x + j * cell, gy + 5 * cell + 0.03, cell, 0.25, str(hv), size=11, color=MUTED, align=PP_ALIGN.CENTER)
    text(slide, x, gy + 5 * cell + 0.32, 2.8, 0.35, phi, size=15, color=HEAD, bold=True)


board(s, 0.85, 2.05, BEFORE, [2, 2, 3, 3, 3, 2, 1, 2, 2, 0], "φ = [20, 1, 6, 0]", "BEFORE", full_row=4)
text(s, 3.55, 2.95, 0.4, 0.4, "→", size=24, color=MUTED, bold=True)
board(s, 3.95, 2.05, AFTER, [1, 1, 2, 2, 2, 1, 0, 1, 2, 2], "φ = [14, 1, 5, 1]", "AFTER (afterstate)")
legend = [(BRICK, "old bricks"), (PIECE, "new L piece"), (RGBColor(0xFD, 0xE4, 0xE4), "hole"), (None, "full row → cleared")]
for k, (c, lab) in enumerate(legend):
    lx = 0.85 + (k % 2) * 2.9
    ly = 4.75 + (k // 2) * 0.38
    if c is None:
        b_ = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(lx), Inches(ly + 0.05), Inches(0.22), Inches(0.22))
        b_.fill.background()
        b_.line.color.rgb = RGBColor(0x1B, 0xAF, 0x7A)
        b_.line.width = Pt(2)
    else:
        rect(s, lx, ly + 0.05, 0.22, 0.22, c)
    text(s, lx + 0.32, ly, 2.4, 0.32, lab, size=12, color=BODY)
text(s, 0.85, 5.65, 5.9, 1.1, "hᵢ = height of column i (from the floor to its highest brick). "
     "The 2²⁰⁰ possible boards are compressed into φ, the input of the MLP.", size=12, color=BODY, spacing=1.2)
feats = [("f₁  Aggregate height", "f₁ = h₁ + h₂ + … + h₁₀", "Taller board → closer to losing. After: 1+1+2+2+2+1+0+1+2+2 = 14"),
         ("f₂  Holes", "f₂ = Σ empty cells with a brick above", "Counted per column; empty columns count 0. Here column 3 → f₂ = 1"),
         ("f₃  Bumpiness", "f₃ = Σ |hᵢ − hᵢ₊₁|", "Height differences of neighbours. After: 0+1+0+0+1+1+1+1+0 = 5"),
         ("f₄  Lines cleared", "f₄ ∈ {0, 1, 2, 3, 4}", "Lines removed by this placement. The L fills row 1 → f₄ = 1")]
for k, (h, f, b) in enumerate(feats):
    x, y = 7.15 + (k % 2) * 2.85, 1.45 + (k // 2) * 2.72
    card(s, x, y, 2.7, 2.6, None, h, b, body_size=12, formula=f, head_size=15, formula_size=11)
notes(s, """
Bàn cờ có 200 ô, tức khoảng 2 mũ 200 trạng thái, quá nhiều để học trực tiếp. Vì vậy mỗi bàn cờ sau khi đặt khối, gọi là afterstate, được nén thành bốn con số.

Ví dụ bên trái: thả khối L vào cột 9 và 10. Trước khi đặt, chiều cao các cột là 2, 2, 3, 3, 3, 2, 1, 2, 2, 0, nên φ bằng 20, 1, 6, 0. Khối L lấp đầy hàng dưới cùng, hàng đó bị xoá, và bàn cờ sau có φ bằng 14, 1, 5, 1.

Bốn đặc trưng là:
f1, tổng chiều cao 10 cột: bàn cờ càng cao càng gần thua.
f2, số lỗ: số ô trống bị gạch che phía trên; ở đây cột 3 có một lỗ.
f3, độ gồ ghề: tổng chênh lệch chiều cao giữa hai cột kề nhau.
f4, số hàng vừa xoá: ở đây là 1.

Bốn con số này là đầu vào của mạng MLP. Mạng không nhìn thấy bàn cờ, chỉ nhìn thấy bốn con số.
""")

# 5c ─ Reward function (adapted from progress report)
s = new("Reward: Pay for Lines, Penalise Bad Boards")
rect(s, 0.6, 1.45, 12.13, 1.25, RGBColor(0x14, 0x21, 0x3D), rounded=True, radius=0.1)
text(s, 0.9, 1.5, 11.6, 0.35, "REWARD OF EVERY PLACEMENT", size=12, color=RGBColor(0x7F, 0xD8, 0xFF), bold=True)
text(s, 0.9, 1.8, 11.6, 0.5, "r = 1 + 10·f₄² − 0.5·Δf₁ − 1.5·Δf₂ − 0.5·Δf₃", size=26, color=WHITE, bold=True)
text(s, 0.9, 2.3, 11.6, 0.35, "Δfᵢ = fᵢ(after) − fᵢ(before)   •   losing (next piece cannot be placed): −10", size=13,
     color=RGBColor(0xCF, 0xDD, 0xEA))
rows = [["Term", "Meaning", "Example"],
        ["+1", "survive one more placement", "always +1"],
        ["+10·f₄²", "line-clear bonus (quadratic)", "1 → +10 · 2 → +40 · 3 → +90 · 4 → +160"],
        ["−0.5·Δf₁", "board got taller", "+5 height → −2.5; −6 → +3"],
        ["−1.5·Δf₂", "new holes (heaviest penalty)", "+1 hole → −1.5; fill one → +1.5"],
        ["−0.5·Δf₃", "surface got bumpier", "+4 bumpiness → −2; −1 → +0.5"],
        ["−10", "game over", "next piece has no legal placement"]]
table(s, 0.6, 2.95, 7.2, rows, [1.25, 2.6, 3.35], size=12, row_h=0.53)
rect(s, 8.1, 2.95, 4.63, 1.85, CARD, CARD_LINE, rounded=True, radius=0.07)
text(s, 8.3, 3.05, 3.0, 0.35, "GOOD MOVE", size=12, color=RGBColor(0x0E, 0x8A, 0x5F), bold=True)
text(s, 8.3, 3.35, 4.2, 0.35, "L into columns 9–10, clears row 1", size=13, color=INK, bold=True)
text(s, 8.3, 3.7, 3.1, 1.0, ["φ: [20, 1, 6, 0] → [14, 1, 5, 1]", "r = 1 + 10·1² − 0.5·(−6) − 0 − 0.5·(−1)"], size=11, color=BODY)
text(s, 11.0, 3.5, 1.6, 0.8, "+14.5", size=30, color=RGBColor(0x0E, 0x8A, 0x5F), bold=True, align=PP_ALIGN.RIGHT)
rect(s, 8.1, 4.95, 4.63, 1.85, CARD, CARD_LINE, rounded=True, radius=0.07)
text(s, 8.3, 5.05, 3.0, 0.35, "CARELESS MOVE", size=12, color=RGBColor(0xC6, 0x28, 0x28), bold=True)
text(s, 8.3, 5.35, 4.2, 0.35, "L into columns 6–7, creates a hole", size=13, color=INK, bold=True)
text(s, 8.3, 5.7, 3.1, 1.0, ["φ: [20, 1, 6, 0] → [25, 2, 6, 0]", "r = 1 + 0 − 0.5·5 − 1.5·1 − 0"], size=11, color=BODY)
text(s, 11.0, 5.5, 1.6, 0.8, "−3.0", size=30, color=RGBColor(0xC6, 0x28, 0x28), bold=True, align=PP_ALIGN.RIGHT)
notes(s, """
Đây là hàm thưởng agent nhận sau mỗi lần đặt khối.

Agent được cộng 1 vì sống thêm một lượt, cộng 10 nhân bình phương số hàng xoá được. Vì là bình phương, xoá 1 hàng được 10 nhưng xoá 4 hàng cùng lúc được 160, gấp 16 lần, nên agent có động lực chờ để ăn combo.

Ba phần phạt tính theo độ thay đổi so với trước khi đặt: bàn cờ cao thêm thì bị trừ 0,5 mỗi đơn vị; tạo thêm lỗ bị trừ nặng nhất, 1,5 mỗi lỗ; mặt gạch gồ ghề hơn bị trừ 0,5. Ngược lại, nếu làm bàn cờ thấp đi, lấp được lỗ hay phẳng hơn thì được cộng điểm. Thua ván bị trừ 10.

Hai ví dụ bên phải dùng cùng bàn cờ của slide trước. Thả L vào cột 9 và 10 xoá được một hàng, bàn cờ thấp đi 6 và phẳng hơn 1, nên được cộng 14,5. Thả L vào cột 6 và 7 thì bàn cờ cao thêm 5 và tạo thêm một lỗ, nên bị trừ 3.

Câu hỏi nghiên cứu là: các trọng số 10, 1,5, 0,5 này có thật sự quan trọng không? Phần kết quả sẽ trả lời.
""")

# 5d ─ Value network & training
s = new("Value Network and Training")
cw, ch = 5.95, 2.45
pos = [(0.6, 1.5), (6.78, 1.5), (0.6, 4.15), (6.78, 4.15)]
card(s, *pos[0], cw, ch, 1, "Value network",
     "A small MLP 4–64–64–1 maps the four features of an afterstate to one score: how good this board is in the long run.",
     formula="U(φ) : (f₁, f₂, f₃, f₄) → score")
card(s, *pos[1], cw, ch, 2, "ε-greedy action",
     "With probability 1 − ε take the best-scoring placement, otherwise a random one. ε decays linearly from 1.0 to 0.001 over 1200 episodes.")
card(s, *pos[2], cw, ch, 3, "Replay buffer",
     "The last 30,000 transitions are stored; every placement trains on a random mini-batch of 512, which breaks the correlation between consecutive moves.")
card(s, *pos[3], cw, ch, 4, "Target network",
     "A frozen copy U⁻ computes the TD target and is refreshed every 10 episodes; Huber loss, Adam (lr 10⁻³), γ = 0.99.")
notes(s, """
Phần cuối của phương pháp là mạng và cách huấn luyện.

Một, mạng giá trị là một MLP nhỏ 4–64–64–1: nhận bốn đặc trưng của afterstate và trả ra một điểm số, nghĩa là bàn cờ này tốt đến đâu về lâu dài. Agent chấm điểm mọi cách đặt rồi chọn cách có điểm cao nhất.

Hai, chính sách ε-greedy: với xác suất 1 trừ ε agent chọn cách tốt nhất, còn lại chọn ngẫu nhiên để khám phá. ε giảm từ 1 xuống 0,001 trong 1200 ván.

Ba, replay buffer lưu 30 nghìn bước gần nhất; mỗi lần đặt khối, agent ôn lại một batch ngẫu nhiên 512 mẫu, giúp việc học ổn định hơn.

Bốn, target network là một bản sao đứng yên dùng để tính mục tiêu học, cập nhật mỗi 10 ván; dùng Huber loss, Adam với tốc độ học 0,001 và γ bằng 0,99.

Phần duy nhất các phương pháp khác nhau là cách tính mục tiêu học, ở slide tiếp theo.
""")

# 6 ─ Four TD targets
s = new("Four TD Targets")
rect(s, 2.4, 1.45, 8.53, 0.62, WHITE, BAR, rounded=True, radius=0.2)
text(s, 2.4, 1.45, 8.53, 0.62, "y = r + γ · (1 − d) · bootstrap over the next afterstates X′",
     size=20, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
tg = [("SARSA (original)", "U⁻(x′ picked by ε-greedy)", "On-policy: values the exploring policy, random moves included."),
      ("Q-learning", "max over X′ of U⁻(x)", "Off-policy: values the greedy policy, whatever the agent explored (lecture 2.8)."),
      ("Double Q", "U⁻(argmax over X′ of U)", "Online net selects, target net evaluates: less overestimation."),
      ("Expected SARSA", "(1−ε)·max U⁻ + ε·mean U⁻", "Exact expectation under ε-greedy: lower variance (lecture 2.9).")]
for k, (h, f, b) in enumerate(tg):
    card(s, 0.6 + k * 3.1, 2.35, 2.9, 3.0, None, h, b, body_size=15, formula=f, head_size=18, formula_size=13)
rect(s, 0.6, 5.6, 12.13, 1.0, CIRCLE, rounded=True, radius=0.12)
text(s, 0.9, 5.6, 11.6, 1.0,
     [[("Example   ", {"bold": True}),
       ("next values {50, 20, −10}, ε = 0.5, random pick −10  →  SARSA −10 · Q-learning 50 · Expected SARSA 35", {})]],
     size=16, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
notes(s, """
Đây là phần cốt lõi, nơi nhóm áp dụng trực tiếp hai bài giảng 2.8 Q-learning và 2.9 Expected SARSA.

Mọi phương pháp đều có dạng: mục tiêu học bằng phần thưởng nhận ngay cộng γ nhân giá trị bootstrap của bước sau. Chúng chỉ khác nhau ở cách lấy giá trị bootstrap đó.

SARSA, tức cách gốc của project, lấy giá trị của afterstate mà ε-greedy thực sự chọn, kể cả khi đó là nước đi ngẫu nhiên. Vì vậy nó học giá trị của chính sách đang khám phá.

Q-learning lấy giá trị lớn nhất trong mọi afterstate có thể của khối kế tiếp. Đó là off-policy: học giá trị của chính sách tốt nhất, bất kể agent đang khám phá thế nào.

Double Q để mạng online chọn nước tốt nhất, còn mạng target chấm điểm nước đó, giúp giảm việc đánh giá quá cao do lấy max. Đây mới đúng là Double DQN.

Expected SARSA lấy kỳ vọng chính xác theo chính sách ε-greedy: (1 trừ ε) nhân giá trị lớn nhất, cộng ε nhân giá trị trung bình, nên ít nhiễu hơn SARSA.

Ví dụ ở dải xanh: khối kế tiếp có ba vị trí với giá trị 50, 20 và âm 10; ε bằng 0,5 và agent lỡ chọn ngẫu nhiên vị trí âm 10. SARSA dùng âm 10, nên bàn cờ hiện tại bị chấm oan chỉ vì bước sau đi bừa. Q-learning dùng 50. Expected SARSA dùng 35.
""")

# 7 ─ Experimental setup
s = new("Experimental Setup")
rows = [["Group", "What changes (one factor at a time)", "Runs"],
        ["Reward weights", "double / halve / remove each weight, game-over 50, lines only", "12 × 3"],
        ["Hyper-parameters", "γ 0.95, lr 5e-4, sync 5 / 25 ep, ε-decay 600, hidden 128, batch 256", "8 × 3"],
        ["TD target", "SARSA, Q-learning, Double Q, Expected SARSA × {2000, 1050} ep", "8 × 3"],
        ["Total", "28 configurations, seeds 0 / 1 / 2", "84"]]
table(s, 0.6, 1.55, 7.6, rows, [1.75, 4.85, 1.0], size=13, row_h=0.62, bold_rows=(4,), hilite_rows=(4,))
text(s, 0.6, 4.9, 7.6, 1.5,
     [[("Training: ", {"bold": True, "color": HEAD}), ("2000 episodes, ε-decay 1200, episode cap 1500 placements.", {})],
      [("Compute: ", {"bold": True, "color": HEAD}), ("free Kaggle notebooks; CPU for groups 1–2, 2 × T4 GPU for group 3 (≈ 26 h).", {})]],
     size=14, color=BODY, spacing=1.35)
card(s, 8.5, 1.55, 4.23, 2.45, 1, "Evaluation",
     "100 greedy games (ε = 0), ≤ 1000 placements each (≈ 400-line ceiling), same piece seeds for every agent. "
     "Best and latest checkpoints.", body_size=14)
card(s, 8.5, 4.2, 4.23, 2.45, 2, "Statistics",
     "Seeds are the unit: mean ± sd over 3 seeds, Welch t-test. Collapse = best > 250 lines but latest < 50.",
     body_size=14)
notes(s, """
Về thiết lập thí nghiệm. Nguyên tắc xuyên suốt là mỗi lần chỉ thay đổi đúng một yếu tố so với baseline, để nếu kết quả khác thì biết chắc là do yếu tố đó.

Có ba nhóm. Nhóm reward gồm 12 cấu hình: nhân đôi, giảm nửa hoặc bỏ từng trọng số, tăng phạt thua lên 50, và cấu hình “lines only” bỏ cả ba phần phạt. Nhóm siêu tham số gồm 8 cấu hình: γ bằng 0,95, tốc độ học nhỏ hơn, đồng bộ target network nhanh hoặc chậm hơn, ε giảm nhanh hơn, mạng to hơn và batch nhỏ hơn. Nhóm TD target gồm 4 cách tính mục tiêu, mỗi cách chạy 2000 ván và 1050 ván, đúng con số trong report gốc. Mỗi cấu hình chạy 3 seed, tổng cộng 84 lần huấn luyện.

Khi đánh giá, mỗi agent chơi 100 ván không khám phá, mỗi ván tối đa 1000 khối, nên tối đa khoảng 400 hàng. Mọi agent gặp cùng một chuỗi khối để so sánh công bằng. Mỗi run được chấm hai phiên bản: bản best (ván train tốt nhất) và bản latest (cuối cùng).

Về thống kê, đơn vị là seed, không phải từng ván, nên nhóm dùng Welch t-test trên trung bình của các seed. “Collapse” nghĩa là bản best trên 250 hàng nhưng bản latest dưới 50 hàng. Toàn bộ chạy trên Kaggle miễn phí, khoảng 26 giờ.
""")

# 8 ─ Reference agents
s = new("Reference Agents")
rows = [["Agent", "Lines (mean ± sd)", "Median", "Max", "Score", "Pts / line", "Cap hits"],
        ["Random placement", "0.2 ± 0.4", "0", "2", "6", "40.0", "0"],
        ["Naive greedy", "16.5 ± 9.8", "16", "46", "926", "56.1", "0"],
        ["Linear heuristic (Lee, 2013)", "388.3 ± 34.5", "396", "399", "17,139", "44.1", "94"],
        ["P-DDQN checkpoint (original)", "266.8 ± 123.1", "295.5", "397", "21,595", "81.0", "37"]]
table(s, 0.8, 1.6, 11.73, rows, [3.6, 1.9, 1.1, 0.9, 1.4, 1.4, 1.43], size=15, row_h=0.55, hilite_rows=(4,))
card(s, 0.8, 4.65, 5.7, 1.95, None, "Heuristic: survives, but plays safe",
     "94 / 100 games reach the cap, yet only 44 points per line: it clears mostly single lines.", body_size=15)
card(s, 6.83, 4.65, 5.7, 1.95, None, "Learned agent: more combos",
     "81 points per line and a higher score: it waits for multi-line clears and accepts more risk.", body_size=15)
notes(s, """
Trước khi vào kết quả chính, đây là các mốc so sánh, đánh giá theo cùng quy trình.

Chơi ngẫu nhiên gần như không xoá được hàng nào. Chiến lược tham lam đơn giản đạt khoảng 16 hàng. Heuristic tuyến tính viết tay với trọng số của Lee năm 2013 đạt 388 hàng. Còn checkpoint P-DDQN gốc của nhóm đạt 266,8 hàng khi nhóm đánh giá lại, khớp với con số 287,5 trong report vì độ lệch chuẩn rất lớn.

Điều đáng chú ý là hai phong cách chơi khác nhau. Heuristic sống tới giới hạn ở 94 trên 100 ván nhưng chỉ được 44 điểm mỗi hàng, tức là chủ yếu xoá từng hàng một cho an toàn. Agent học được thì ít hàng hơn nhưng được 81 điểm mỗi hàng và tổng điểm cao hơn, vì nó chờ để xoá nhiều hàng cùng lúc. Sự đánh đổi giữa sống lâu và ăn combo này sẽ xuất hiện lại trong suốt các thí nghiệm.
""")

# 9 ─ Reward ablation (formula with named weights on top)
s = new("Reward Weights: Style, Not Learnability")
rect(s, 0.6, 1.4, 12.13, 1.15, RGBColor(0x14, 0x21, 0x3D), rounded=True, radius=0.1)
text(s, 0.9, 1.45, 11.6, 0.55,
     [[("r = ", {}), ("w_alive", {"color": RGBColor(0x7F, 0xD8, 0xFF)}), (" + ", {}),
       ("w_lines", {"color": RGBColor(0x7F, 0xD8, 0xFF)}), ("·f₄² − ", {}),
       ("w_height", {"color": RGBColor(0x7F, 0xD8, 0xFF)}), ("·Δf₁ − ", {}),
       ("w_holes", {"color": RGBColor(0x7F, 0xD8, 0xFF)}), ("·Δf₂ − ", {}),
       ("w_bump", {"color": RGBColor(0x7F, 0xD8, 0xFF)}), ("·Δf₃ − ", {}),
       ("w_over", {"color": RGBColor(0x7F, 0xD8, 0xFF)}), ("·[lost]", {})]],
     size=17, color=WHITE, bold=True)
text(s, 0.9, 2.02, 11.6, 0.4, "baseline:  w_alive = 1 · w_lines = 10 · w_height = 0.5 · w_holes = 1.5 · w_bump = 0.5 · w_over = 10"
     "     →  each run changes exactly one weight", size=13, color=RGBColor(0xCF, 0xDD, 0xEA))
rows = [["Config", "Change", "Lines (best)", "Lines (latest)", "Coll.", "Score", "Pts/line"],
        ["baseline", "—", "298 ± 75", "308 ± 90", "0", "24,175", "81.8"],
        ["lines ×2", "w_lines = 20", "312 ± 109", "236 ± 206", "0", "22,557", "73.6"],
        ["lines ×0.5", "w_lines = 5", "336 ± 33", "322 ± 92", "0", "31,807", "96.3"],
        ["holes ×2", "w_holes = 3", "349 ± 35", "384 ± 8", "0", "24,668", "70.6"],
        ["holes ×0.5", "w_holes = 0.75", "355 ± 44", "364 ± 25", "0", "25,105", "71.9"],
        ["bump ×2", "w_bump = 1", "383 ± 7", "384 ± 1", "0", "27,770", "72.6"],
        ["bump = 0", "w_bump = 0", "344 ± 54", "350 ± 42", "0", "27,218", "79.3"],
        ["height ×2", "w_height = 1", "366 ± 29", "373 ± 16", "0", "26,463", "72.8"],
        ["height = 0", "w_height = 0", "381 ± 8", "369 ± 10", "0", "29,196", "76.5"],
        ["alive = 0", "w_alive = 0", "369 ± 25", "357 ± 32", "0", "27,338", "74.4"],
        ["game-over 50", "w_over = 50", "375 ± 27", "252 ± 219", "1", "27,859", "74.5"],
        ["lines only", "holes = bump = height = 0", "371 ± 12", "96 ± 166", "2", "25,327", "68.5"]]
table(s, 0.6, 2.75, 8.45, rows, [1.25, 2.1, 1.15, 1.25, 0.6, 1.0, 1.1], size=11, row_h=0.32, hilite_rows=(6, 12))
stats = [("p > 0.14", "no weight change is statistically significant"),
         ("lines only: 371", "no shaping at all still learns, but 2 / 3 seeds collapse"),
         ("bump ×2: 383 ± 7", "most stable reward, no collapse at all"),
         ("lines ×0.5: 31,807", "highest score: 96 points per line (more combos)")]
for k, (big, small) in enumerate(stats):
    y = 2.75 + k * 1.05
    rect(s, 9.3, y, 3.43, 0.95, CARD, CARD_LINE, rounded=True, radius=0.1)
    text(s, 9.45, y + 0.06, 3.2, 0.4, big, size=17, color=HEAD, bold=True)
    text(s, 9.45, y + 0.46, 3.2, 0.45, small, size=11, color=BODY)
notes(s, """
Kết quả nhóm reward. Phía trên là hàm thưởng viết dưới dạng có tên từng trọng số, kèm giá trị baseline. Mỗi lần chạy chỉ đổi đúng một trọng số; cột “Change” trong bảng cho biết trọng số nào được đổi và giá trị mới.

Cách đọc tác động khi thay đổi từng tham số:
– w_lines, thưởng xoá hàng: tăng lên 20 làm việc học kém ổn định, một seed chỉ đạt 187 hàng rồi gần như về 0; giảm còn 5 lại cho tổng điểm cao nhất, 31.807, với 96 điểm mỗi hàng, tức agent ăn combo nhiều hơn.
– w_holes, phạt lỗ: nhân đôi hay giảm nửa đều cho 349–355 hàng, không khác biệt có ý nghĩa.
– w_bump, phạt gồ ghề: nhân đôi cho kết quả ổn định nhất nhóm, khoảng 383 hàng ở cả bản best lẫn latest, không sụp lần nào; bỏ hẳn thì dao động hơn.
– w_height, phạt chiều cao: bỏ đi vẫn đạt 381 hàng.
– w_alive và w_over: bỏ thưởng sống hay tăng phạt thua lên 50 cũng không thay đổi đáng kể, nhưng phạt thua 50 làm một seed bị sụp.
– Lines only, bỏ cả ba phần phạt: vẫn đạt 364 đến 384 hàng, nhưng 2 trên 3 seed bị sụp ở cuối.

Kết luận: không có thay đổi nào khác baseline có ý nghĩa thống kê, p lớn hơn 0,14. Trọng số reward quyết định phong cách chơi và độ ổn định, chứ không quyết định agent có học được hay không, đúng như phân tích shaping thế năng.
""")

# 10 ─ Hyper-parameters (baseline values on top)
s = new("Hyper-Parameter Ablation")
rect(s, 0.6, 1.4, 12.13, 0.95, RGBColor(0x14, 0x21, 0x3D), rounded=True, radius=0.1)
text(s, 0.9, 1.45, 11.6, 0.45,
     "baseline:  γ = 0.99 · lr = 10⁻³ · target sync = 10 ep · ε-decay = 1200 ep · hidden = 64 · batch = 512",
     size=16, color=WHITE, bold=True)
text(s, 0.9, 1.92, 11.6, 0.35, "reward = baseline weights; each run changes exactly one hyper-parameter",
     size=13, color=RGBColor(0xCF, 0xDD, 0xEA))
rows = [["Config", "Change", "Lines (best)", "Lines (latest)", "Coll.", "Score", "Pts/line"],
        ["baseline", "—", "298 ± 75", "308 ± 90", "0", "24,175", "81.8"],
        ["γ = 0.95", "shorter horizon", "395 ± 3", "131 ± 226", "2", "20,422", "51.7"],
        ["lr = 5e-4", "learn slower", "124 ± 163", "132 ± 166", "–", "12,347", "73.8"],
        ["sync 5 ep", "faster target update", "332 ± 42", "366 ± 8", "0", "26,751", "79.4"],
        ["sync 25 ep", "slower target update", "327 ± 80", "346 ± 77", "0", "21,831", "65.0"],
        ["ε-decay 600", "explore less", "351 ± 24", "372 ± 12", "0", "25,217", "71.8"],
        ["hidden 128", "wider network", "389 ± 14", "378 ± 4", "0", "24,083", "62.2"],
        ["batch 256", "smaller batch", "263 ± 98", "307 ± 86", "0", "25,369", "92.5"]]
table(s, 0.6, 2.6, 8.45, rows, [1.25, 2.1, 1.15, 1.25, 0.6, 1.0, 1.1], size=12, row_h=0.46, hilite_rows=(7,))
card(s, 9.3, 2.6, 3.43, 1.35, None, "hidden 128", "most robust of the study: 389 / 378 lines, no collapse", body_size=12, head_size=16)
card(s, 9.3, 4.05, 3.43, 1.35, None, "γ = 0.95", "hits the ceiling but 2 / 3 seeds collapse; only 52 pts / line", body_size=12, head_size=16)
card(s, 9.3, 5.5, 3.43, 1.35, None, "learning speed", "ε-decay 600 learns earlier; lr 5e-4 fails in 2 / 3 seeds", body_size=12, head_size=16)
notes(s, """
Nhóm siêu tham số. Dải phía trên ghi giá trị baseline của từng siêu tham số; mỗi lần chạy chỉ đổi đúng một giá trị, ghi ở cột “Change”.

Tác động khi thay đổi từng tham số:
– γ, hệ số chiết khấu, giảm từ 0,99 xuống 0,95: agent “nhìn ngắn” hơn, không chờ ăn combo, nên sống tới trần với 395 hàng nhưng chỉ 52 điểm mỗi hàng và tổng điểm thấp hơn baseline; đồng thời 2 trên 3 seed bị sụp ở cuối.
– Tốc độ học giảm còn 5e-4: học quá chậm, 2 trên 3 seed không kịp học trong 2000 ván. Đây là thay đổi duy nhất có hại rõ ràng.
– Đồng bộ target network nhanh hơn (5 ván) cho bản latest ổn định, khoảng 366 hàng; chậm hơn (25 ván) thì dao động hơn.
– ε giảm nhanh hơn, trong 600 ván: agent đạt mức 100 hàng sớm hơn, từ ván 800 đến 1450 so với 1250 đến 1800 của baseline.
– Mạng rộng hơn, 128 nơ-ron: bền vững nhất toàn bộ nghiên cứu, khoảng 389 hàng ở bản best và 378 ở bản latest, không sụp.
– Batch nhỏ hơn, 256: kém hơn và dao động hơn, nhưng nhiều combo hơn.
""")

# 11 ─ TD targets at 1050 episodes
s = new("TD Targets: the 1050-Episode Budget")
fit_picture(s, os.path.join(FIG, "fig_1050.png"), 0.5, 1.45, 8.0, 3.6)
rect(s, 8.85, 1.5, 3.88, 1.75, CARD, CARD_LINE, rounded=True, radius=0.08)
text(s, 9.05, 1.6, 3.5, 0.75, "0 / 3", size=40, color=HEAD, bold=True)
text(s, 9.05, 2.4, 3.5, 0.8, "seeds learn with SARSA (≈ 3 lines per game)", size=14, color=BODY)
rect(s, 8.85, 3.4, 3.88, 1.75, CARD, CARD_LINE, rounded=True, radius=0.08)
text(s, 9.05, 3.5, 3.5, 0.75, "4 / 9", size=40, color=HEAD, bold=True)
text(s, 9.05, 4.3, 3.5, 0.8, "seeds reach 283–396 lines with off-policy / expected targets", size=14, color=BODY)
rect(s, 0.6, 5.4, 12.13, 1.3, CIRCLE, rounded=True, radius=0.1)
text(s, 0.9, 5.4, 11.6, 1.3,
     "At episode 1050, ε ≈ 0.13, so every training curve looks poor (≤ 26 lines). Q-learning and Expected SARSA "
     "still learn the value of the greedy policy; SARSA learns the value of the exploring one.",
     size=16, color=WHITE, anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
notes(s, """
Đây là kết quả nổi bật nhất của nghiên cứu.

Với 1050 ván, đúng con số trong report gốc, cách SARSA gốc chỉ xoá khoảng 3 hàng mỗi ván ở cả 3 trên 3 seed, tức là thất bại hoàn toàn. Trong khi đó, ba cách thay thế đạt 283 đến 396 hàng ở 4 trên 9 seed: Q-learning 1 seed đạt 388 hàng, Double Q 1 seed đạt 283 hàng, Expected SARSA 2 seed đạt 393 và 396 hàng.

Trên hình, chấm xanh là kết quả khi cho agent chơi thật, còn ô vuông cam là thành tích trong lúc học. Điều thú vị là lúc học, tất cả đều trông rất tệ, dưới 26 hàng, vì ở ván 1050 ε vẫn còn khoảng 0,13, tức agent vẫn đi bừa 13% thời gian.

Lý do nằm ở lý thuyết: Q-learning và Expected SARSA học giá trị của chính sách tốt nhất ngay cả khi đang khám phá, đúng tính chất off-policy trong slide 2.8. SARSA thì học giá trị của chính sách có đi bừa, nên khi chơi thật nó không biết cách chơi tốt nhất.

Với 3 seed, đây là kết quả mô tả chứ chưa phải kết luận thống kê, nhưng chênh lệch lên tới hai bậc độ lớn và khớp hoàn toàn với lý thuyết.
""")

# 12 ─ TD targets at 2000 episodes
s = new("TD Targets with 2000 Episodes")
rows = [["Target", "Lines (best)", "Lines (latest)", "Coll.", "First 100", "Pts/line"],
        ["SARSA (baseline)", "379 ± 9", "266 ± 211", "1", "ep 1470", "74.3"],
        ["Q-learning", "350 ± 61", "260 ± 224", "1", "ep 1447", "61.0"],
        ["Double Q", "319 ± 87", "323 ± 66", "0", "ep 1413", "87.8"],
        ["Expected SARSA", "397 ± 0.6", "260 ± 225", "1", "ep 1163", "52.1"]]
table(s, 0.5, 1.55, 6.3, rows, [1.75, 1.05, 1.15, 0.6, 0.95, 0.8], size=12, row_h=0.55, hilite_rows=(4,))
fit_picture(s, os.path.join(FIG, "fig_curves.png"), 7.0, 1.45, 5.9, 3.3)
card(s, 0.5, 4.95, 4.0, 1.75, None, "Expected SARSA", "Learns first (ep ≈ 1160) and hits the ceiling in all seeds: 100 / 100 cap hits.", body_size=13, head_size=17)
card(s, 4.67, 4.95, 4.0, 1.75, None, "Double Q", "The only target without collapse, and the most combos (88 pts / line).", body_size=13, head_size=17)
card(s, 8.83, 4.95, 4.0, 1.75, None, "Q-learning", "No better than SARSA; one seed peaks at 279 lines, then collapses.", body_size=13, head_size=17)
notes(s, """
Khi có đủ 2000 ván, cả bốn cách đều học được; chúng khác nhau ở tốc độ, mức trần và phong cách.

Expected SARSA học sớm nhất: đạt mức trung bình 100 hàng ở khoảng ván 1160 với cả 3 seed, so với 1360 đến 1650 của SARSA. Đường màu vàng ở hình bên phải là đường cất cánh sớm nhất. Nó cũng là cấu hình duy nhất trong toàn bộ nghiên cứu mà bản best chạm trần ở mọi ván của cả 3 seed: 397 hàng, 100 trên 100 ván sống tới giới hạn. Điều này khớp với lý thuyết rằng Expected SARSA có phương sai thấp hơn.

Double Q là cách duy nhất không có seed nào bị sụp, và có nhiều combo nhất, 88 điểm mỗi hàng, nhưng độ lệch giữa các seed lớn nhất.

Q-learning thuần thì không hơn SARSA: một seed chỉ đạt 279 hàng rồi sụp, phù hợp với hiện tượng đánh giá quá cao do phép lấy max.

Bên phải phía dưới của hình là các ví dụ sụp đổ mà slide sau sẽ nói kỹ hơn.
""")

# 13a ─ What is a collapse?
s = new("What Is a Collapse?")
fit_picture(s, COLLAPSE_PNG, 0.5, 1.4, 7.4, 4.3)
rect(s, 8.15, 1.45, 4.58, 2.3, CARD, CARD_LINE, rounded=True, radius=0.06)
text(s, 8.4, 1.55, 4.1, 0.75, "8 / 84 runs", size=34, color=HEAD, bold=True)
text(s, 8.4, 2.3, 4.1, 1.4, "After hundreds of episodes at the cap (≈ 600 lines), the agent breaks down within 100–200 episodes.",
     size=14, color=BODY, spacing=1.2)
rect(s, 8.15, 3.9, 4.58, 1.8, CARD, CARD_LINE, rounded=True, radius=0.06)
text(s, 8.4, 4.0, 4.1, 0.6, "18–36 pieces", size=30, color=HEAD, bold=True)
text(s, 8.4, 4.6, 4.1, 1.1, "is all the collapsed final network survives in evaluation: no better than random play (26).",
     size=14, color=BODY, spacing=1.2)
rect(s, 0.6, 5.95, 12.13, 0.85, CIRCLE, rounded=True, radius=0.15)
text(s, 0.9, 5.95, 11.6, 0.85,
     "Collapse: the best checkpoint plays 279–398 lines, but the final network clears 0–22 lines. "
     "The best checkpoint is saved before the drop, so we keep it.", size=15, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
notes(s, """
Ở phần kết quả nhóm có nhắc tới hiện tượng “sụp” hay “chết”. Slide này giải thích nó là gì.

Hình bên trái là đường cong huấn luyện của bốn run bị sụp. Agent đã chơi rất giỏi, khoảng 600 hàng mỗi ván, tức là ván nào cũng sống tới giới hạn 1500 khối, và giữ mức đó hàng trăm ván. Rồi đột nhiên, chỉ trong 100 đến 200 ván, thành tích rơi xuống gần 0.

Tổng cộng có 8 trên 84 run như vậy. Khi đem mạng cuối cùng của các run này đi đánh giá, nó chỉ sống được 18 đến 36 khối rồi thua, không hơn chơi ngẫu nhiên (khoảng 26 khối). Trong khi đó, bản best của cùng run, được lưu trước lúc sụp, vẫn đạt 279 đến 398 hàng.

Vì vậy nhóm định nghĩa “collapse” là: bản best trên 250 hàng nhưng bản cuối dưới 50 hàng. Và đây cũng là lý do nhóm luôn báo cáo cả bản best lẫn bản latest. Slide tiếp theo giải thích vì sao agent lại sụp.
""")

# 13b ─ Why do agents collapse?
s = new("Why Do Agents Collapse?")
steps = [("No more game-overs", "Once every episode reaches the 1500-placement cap, episodes end by truncation, so no terminal (−10) transitions are created."),
         ("Buffer of clean boards", "The 30k replay buffer now holds only the last ≈ 20 capped episodes: low, clean boards. Dangerous boards disappear from training."),
         ("Values drift", "Without data, the values of tall or bumpy boards drift upwards; the agent starts preferring them and loses fast.")]
for k, (h, b) in enumerate(steps):
    x = 0.6 + k * 4.12
    card(s, x, 1.5, 3.85, 2.75, k + 1, h, b, body_size=14, head_size=17)
    if k < 2:
        text(s, x + 3.86, 2.6, 0.3, 0.5, "→", size=22, color=MUTED, bold=True)
text(s, 0.6, 4.45, 7.6, 0.4, "Evidence: the network’s own score change, best vs final checkpoint", size=15, color=HEAD, bold=True)
rows = [["Run", "Probe (change of board)", "Best", "Final"],
        ["Q-learning, seed 2", "+40 aggregate height", "−235", "+13"],
        ["Q-learning, seed 2", "+10 bumpiness", "−66", "+76"],
        ["Expected SARSA, seed 0", "clear one line", "+4", "−34"]]
table(s, 0.6, 4.9, 7.6, rows, [2.6, 2.8, 1.1, 1.1], size=13, row_h=0.45)
card(s, 8.5, 4.45, 4.23, 2.35, None, "What we do about it",
     "Report the best checkpoint (chosen on training data only). Possible fixes: keep game-over samples in the buffer, a larger buffer, learning-rate decay.",
     body_size=13, head_size=16)
notes(s, """
Vì sao agent lại sụp? Nhóm đưa ra một cơ chế gồm ba bước, kèm bằng chứng đo trực tiếp trên mạng.

Bước một: khi agent đã giỏi, ván nào cũng sống tới giới hạn 1500 khối. Ván kết thúc vì bị cắt chứ không phải vì thua, nên không còn mẫu “thua ván, bị trừ 10” nào được tạo ra.

Bước hai: replay buffer chỉ chứa 30 nghìn bước gần nhất, tương đương khoảng 20 ván cuối. Tất cả đều là bàn cờ thấp và sạch. Những bàn cờ nguy hiểm, cao và nhiều lỗ, biến mất khỏi dữ liệu huấn luyện. Hiện tượng này gọi là catastrophic forgetting: mạng quên những gì không còn được ôn lại.

Bước ba: không còn dữ liệu kéo xuống, giá trị mà mạng gán cho bàn cờ cao hoặc gồ ghề trôi dần lên. Agent bắt đầu thích những bàn cờ nguy hiểm, và thua rất nhanh.

Bằng chứng ở bảng: nhóm cho mạng chấm điểm cùng một thay đổi của bàn cờ, ở bản best và bản cuối. Với Q-learning seed 2, bàn cờ cao thêm 40 ô bị chấm âm 235 ở bản best, nhưng thành cộng 13 ở bản cuối; gồ ghề thêm 10 từ âm 66 thành cộng 76. Nghĩa là mạng đã chuyển sang thích bàn cờ nguy hiểm. Với Expected SARSA seed 0, xoá một hàng từ cộng 4 thành âm 34, tức mạng không muốn xoá hàng nữa.

Cách nhóm xử lý: báo cáo bản best, chọn chỉ dựa trên dữ liệu huấn luyện. Các cách khắc phục có thể thử: giữ lại các mẫu thua ván trong buffer, dùng buffer lớn hơn, hoặc giảm dần tốc độ học. Lưu ý đây là giả thuyết có bằng chứng, nhóm chưa làm thí nghiệm sửa lỗi để khẳng định.
""")

# 13c ─ Why do CPU and GPU runs differ?
s = new("Why Do CPU and GPU Runs Differ?")
chain = [("Summation order", "A GPU adds the products of each matrix multiply in parallel, in a different order than the CPU, so results differ around the 7th digit."),
         ("A near-tie flips", "When two placements score almost the same, that tiny difference can change which one argmax picks."),
         ("Divergence grows", "One different move gives a different board, different replay data and different updates; over ~10⁶ updates the runs diverge.")]
for k, (h, b) in enumerate(chain):
    x = 0.6 + k * 4.12
    card(s, x, 1.5, 3.85, 2.75, k + 1, h, b, body_size=14, head_size=17)
    if k < 2:
        text(s, x + 3.86, 2.6, 0.3, 0.5, "→", size=22, color=MUTED, bold=True)
rows = [["Baseline, seed 0", "CPU", "GPU"],
        ["Best checkpoint (lines)", "212", "377"],
        ["Final network (lines)", "208", "22"]]
table(s, 0.6, 4.55, 5.6, rows, [2.8, 1.4, 1.4], size=14, row_h=0.55)
text(s, 0.6, 6.3, 5.6, 0.5, "On CPU the same seed reproduces bit for bit.", size=13, color=MUTED)
card(s, 6.5, 4.55, 6.23, 2.25, None, "Not a bug: training is chaotic",
     "A fixed seed does not fix the outcome; only several seeds show the true spread. Every comparison in this study is made within one group on the same hardware.",
     body_size=14, head_size=17)
notes(s, """
Slide này giải thích vì sao cùng một seed mà chạy trên CPU và GPU lại cho kết quả khác nhau.

Thứ nhất, khi nhân ma trận, GPU cộng các tích theo kiểu song song, theo thứ tự khác với CPU. Phép cộng số thực trên máy tính không có tính kết hợp tuyệt đối, nên đổi thứ tự cộng làm kết quả lệch nhau ở khoảng chữ số thứ bảy.

Thứ hai, độ lệch rất nhỏ đó thường không quan trọng. Nhưng khi hai vị trí đặt khối có điểm gần bằng nhau, nó đủ làm phép argmax chọn vị trí khác.

Thứ ba, chỉ cần một nước đi khác là bàn cờ khác, dữ liệu trong replay buffer khác, các lần cập nhật mạng khác. Qua khoảng một triệu lần cập nhật, hai lần chạy rẽ sang hai quỹ đạo hoàn toàn khác. Đây là hiệu ứng cánh bướm.

Ví dụ với baseline seed 0: trên CPU bản best đạt 212 hàng, trên GPU 377 hàng; bản cuối 208 so với 22. Trên CPU, chạy lại cùng seed cho kết quả giống hệt từng bit, nên đây không phải lỗi code.

Kết luận: cố định seed không cố định được kết quả; chỉ chạy nhiều seed mới thấy được độ dao động thật. Trong nghiên cứu này, mọi so sánh đều thực hiện trong cùng một nhóm, trên cùng một loại phần cứng, nên vẫn công bằng.
""")

# 14 ─ Trade-off
s = new("Survival versus Combos")
fit_picture(s, os.path.join(FIG, "fig_tradeoff.png"), 0.4, 1.45, 8.2, 5.2)
card(s, 8.85, 1.55, 3.88, 2.4, 1, "Survive to the ceiling",
     "Expected SARSA, γ = 0.95, hidden 128: ≈ 400 lines but 52–62 pts / line → 20–25k points.", body_size=14)
card(s, 8.85, 4.15, 3.88, 2.5, 2, "Score the most",
     "lines ×0.5, height = 0, SARSA (GPU): more risk, more multi-line clears → 28–32k points.", body_size=14)
notes(s, """
Hình này đặt tất cả các cấu hình 2000 ván lên cùng một mặt phẳng: trục ngang là số hàng, đại diện cho khả năng sống lâu; trục dọc là điểm mỗi hàng, đại diện cho mức độ thích combo. Các đường cong xám nối những điểm có cùng tổng điểm.

Góc dưới bên phải là các cấu hình sống tới trần như Expected SARSA, γ bằng 0,95 và mạng 128: chúng xoá gần 400 hàng nhưng chỉ 52 đến 62 điểm mỗi hàng, nên tổng điểm khoảng 20 đến 25 nghìn.

Phía trên là các cấu hình chấp nhận rủi ro để ăn combo như giảm nửa thưởng xoá hàng, bỏ phạt chiều cao, hay SARSA trên GPU: ít hàng hơn một chút nhưng tổng điểm cao hơn, 28 đến 32 nghìn.

Kết luận: cấu hình nào “tốt nhất” phụ thuộc vào mục tiêu là sống lâu hay ghi nhiều điểm. Một con số duy nhất như trong report gốc không thể hiện được sự đánh đổi này.
""")

# 15 ─ Limitations
s = new("Limitations")
lim = [("Few seeds", "Three seeds expose large effects and failure modes, but cannot separate the strong configurations statistically."),
       ("Saturated metric", "The 1000-placement cap puts several configurations at the ≈ 400-line ceiling; an uncapped evaluation is needed."),
       ("One factor at a time", "Interactions are untested; Expected SARSA + hidden 128 + bump ×2 is a natural next run."),
       ("Small feature set, no remedy yet", "Four features and no preview stay far below CEM controllers; remedies for collapse are future work.")]
for k, (h, b) in enumerate(lim):
    x, y = (0.6, 6.78)[k % 2], (1.55, 4.2)[k // 2]
    card(s, x, y, 5.95, 2.45, k + 1, h, b, body_size=17, head_size=21)
notes(s, """
Nhóm cũng xin thẳng thắn nêu các hạn chế.

Một, chỉ có 3 seed mỗi cấu hình. Như vậy đủ để thấy các hiệu ứng lớn và các kiểu thất bại, nhưng chưa đủ để phân biệt thống kê giữa các cấu hình đều tốt.

Hai, giới hạn 1000 khối khi đánh giá làm metric bị bão hoà: nhiều cấu hình chạm trần khoảng 400 hàng nên không xếp hạng được. Cần đánh giá không giới hạn để tách chúng ra.

Ba, mỗi lần chỉ đổi một yếu tố nên chưa biết các yếu tố kết hợp với nhau thế nào. Bước tiếp theo tự nhiên là thử Expected SARSA cùng mạng 128 và phạt gồ ghề gấp đôi.

Bốn, chỉ dùng 4 đặc trưng và không nhìn khối kế tiếp, nên còn kém xa các phương pháp cổ điển mạnh nhất như cross-entropy method, vốn xoá được hàng triệu hàng. Các cách chống sụp như bộ nhớ lớn hơn, giảm tốc độ học dần hay kiểm tra định kỳ cũng để dành cho nghiên cứu sau.
""")

# 16 ─ Conclusion
s = new("Conclusion")
concl = ["The update used in practice is afterstate SARSA, not Double DQN.",
         "Off-policy and expected targets learn near-optimal greedy policies within 1050 episodes, where SARSA fails in every seed; Expected SARSA is the most reliable.",
         "Reward weights mostly change the style of play; a shaping-free reward still learns, as near potential-based shaping predicts.",
         "Network width, exploration schedule and bumpiness weight drive stability; late collapse and CPU/GPU non-determinism are the real risks.",
         "Recommendation: Expected SARSA or Double Q targets, a wider network, ≥ 3 seeds, and report both best and latest checkpoints."]
tb = s.shapes.add_textbox(Inches(0.9), Inches(1.6), Inches(11.5), Inches(5.0))
tf = tb.text_frame
tf.word_wrap = True
for i, line in enumerate(concl):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(14)
    p.line_spacing = 1.15
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(Emu(Inches(0.35))))
    pPr.set("indent", str(-Emu(Inches(0.35))))
    from pptx.oxml.ns import qn
    bu = pPr.makeelement(qn("a:buChar"), {"char": "•"})
    pPr.append(bu)
    r = p.add_run()
    r.text = line
    r.font.name, r.font.size, r.font.color.rgb = FONT, Pt(21), INK
notes(s, """
Tóm lại, nghiên cứu rút ra năm điểm.

Một, phương pháp đang dùng thực chất là SARSA trên afterstate, không phải Double DQN.

Hai, đổi sang các mục tiêu off-policy hoặc kỳ vọng giúp agent học được chính sách gần tối ưu chỉ trong 1050 ván, trong khi SARSA thất bại ở mọi seed. Expected SARSA là lựa chọn đáng tin cậy nhất.

Ba, trọng số reward chủ yếu thay đổi phong cách chơi; bỏ hẳn shaping agent vẫn học được, đúng như lý thuyết shaping thế năng dự đoán.

Bốn, độ rộng mạng, lịch khám phá và phạt gồ ghề quyết định độ ổn định; còn rủi ro thật sự nằm ở hiện tượng sụp cuối huấn luyện và sự khác biệt giữa CPU và GPU.

Năm, khuyến nghị cho các nghiên cứu tương tự: dùng Expected SARSA hoặc Double Q, mạng rộng hơn, ít nhất 3 seed, và báo cáo cả bản best lẫn latest.
""")

# 17 ─ Thank you
s = new()
picture(s, LOGO, 0.55, 0.28, h=0.88)
rect(s, 0.3, 1.35, 12.73, 0.07, BAR)
text(s, 1.0, 2.4, 11.33, 1.2, "Thank you!", size=54, color=GRAY_TITLE, bold=True, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE)
text(s, 1.0, 3.7, 11.33, 0.6, "Questions & Discussion", size=24, color=HEAD, align=PP_ALIGN.CENTER)
rect(s, 0.3, 4.75, 12.73, 0.07, BAR)
text(s, 1.0, 5.2, 11.33, 0.5, "Lê Đặng Duy Khang  ·  Đặng Lan Thảo  ·  Trần Gia Bảo  ·  Nguyễn Trọng Nhân",
     size=16, color=MUTED, align=PP_ALIGN.CENTER)
notes(s, """
Phần trình bày của nhóm em đến đây là kết thúc. Nhóm em xin cảm ơn thầy cô và các bạn đã lắng nghe, và rất mong nhận được câu hỏi cùng góp ý.

Gợi ý trả lời một số câu hỏi có thể gặp:
– Vì sao nói phương pháp gốc là SARSA? Vì mục tiêu học dùng giá trị của nước thực sự được chọn ở bước sau, kể cả nước ngẫu nhiên; không có phép lấy max hay tách việc chọn và chấm điểm.
– 3 seed có đủ không? Đủ để thấy hiệu ứng lớn (SARSA 0/3 so với off-policy 4/9) và hiện tượng sụp, nhưng chưa đủ để kết luận thống kê giữa các cấu hình tốt.
– Chọn bản best có phải ăn gian không? Không, bản best chọn chỉ dựa trên thành tích lúc train, không dùng dữ liệu đánh giá; nhóm vẫn báo cáo cả bản latest.
""")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
