import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_cyber_tech_luxury_deck(output_path):
    prs = Presentation()
    # 16:9 Widescreen standard (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- CYBER-TECH LUXURY COLOR PALETTE ---
    DARK_BG = RGBColor(11, 17, 32)            # #0B1120 Deep Slate
    DARK_CARD = RGBColor(21, 32, 54)          # #152036 Slate Card
    DARK_BORDER = RGBColor(45, 62, 95)        # #2D3E5F Slate Border
    DARK_TEXT = RGBColor(248, 250, 252)       # #F8FAFC White
    DARK_MUTED = RGBColor(148, 163, 184)      # #94A3B8 Slate 400

    LIGHT_BG = RGBColor(241, 245, 249)        # #F1F5F9 Cool Grey
    LIGHT_CARD = RGBColor(255, 255, 255)      # #FFFFFF Pure Crisp White
    LIGHT_BORDER = RGBColor(218, 226, 237)    # #DAE2ED Subtle Border
    TEXT_HEAD = RGBColor(15, 23, 42)          # #0F172A Deep Charcoal
    TEXT_BODY = RGBColor(51, 65, 85)          # #334155 Slate 700
    TEXT_MUTED = RGBColor(100, 116, 139)      # #64748B Slate 500

    # Modern Accent Colors
    ACCENT_CYAN = RGBColor(2, 132, 199)       # Sky 600 #0284C7
    NEON_CYAN = RGBColor(0, 240, 255)         # Neon Cyan #00F0FF
    ACCENT_INDIGO = RGBColor(99, 102, 241)    # Indigo 500 #6366F1
    ACCENT_EMERALD = RGBColor(16, 185, 129)   # Emerald 500 #10B981
    ACCENT_CORAL = RGBColor(239, 68, 68)      # Soft Coral 500 #EF4444
    ACCENT_AMBER = RGBColor(245, 158, 11)     # Amber 500 #F59E0B

    # Pastel Pill Backgrounds & Text
    PILL_CYAN_BG = RGBColor(224, 242, 254)    # Sky 100
    PILL_CYAN_TX = RGBColor(2, 132, 199)
    PILL_INDIGO_BG = RGBColor(238, 242, 255)  # Indigo 100
    PILL_INDIGO_TX = RGBColor(79, 70, 229)
    PILL_EMERALD_BG = RGBColor(209, 250, 229) # Emerald 100
    PILL_EMERALD_TX = RGBColor(5, 150, 105)
    PILL_CORAL_BG = RGBColor(254, 226, 226)   # Rose 100
    PILL_CORAL_TX = RGBColor(220, 38, 38)
    PILL_AMBER_BG = RGBColor(254, 243, 199)   # Amber 100
    PILL_AMBER_TX = RGBColor(217, 119, 6)

    FONT_FAMILY = "Segoe UI"

    def fill_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_card(slide, left, top, width, height, bg=LIGHT_CARD, border=LIGHT_BORDER):
        c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        c.fill.solid()
        c.fill.fore_color.rgb = bg
        c.line.color.rgb = border
        c.line.width = Pt(1.4)
        return c

    def add_accent_bar(slide, left, top, width, height=Inches(0.07), color=ACCENT_CYAN):
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        return bar

    def add_badge_pill(slide, left, top, width, height, text, bg_color, text_color):
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        pill.fill.solid()
        pill.fill.fore_color.rgb = bg_color
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = False
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = text
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = text_color
        return pill

    def add_formula_banner(slide, left, top, width, height, formula_title, formula_text):
        banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        banner.fill.solid()
        banner.fill.fore_color.rgb = RGBColor(15, 23, 42)
        banner.line.color.rgb = RGBColor(38, 54, 84)
        banner.line.width = Pt(1.2)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.12), width - Inches(0.5), height - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = formula_title.upper()
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = NEON_CYAN

        p2 = tf.add_paragraph()
        p2.text = formula_text
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 255, 255)
        p2.space_before = Pt(4)
        return banner

    def add_header(slide, action_title, category="BÁO CÁO TIẾN ĐỘ 50% • REINFORCEMENT LEARNING", num=None, is_dark=False):
        fill_bg(slide, DARK_BG if is_dark else LIGHT_BG)

        hb = slide.shapes.add_textbox(Inches(0.9), Inches(0.4), Inches(11.533), Inches(1.1))
        tf = hb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_FAMILY
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = NEON_CYAN if is_dark else ACCENT_CYAN

        p_t = tf.add_paragraph()
        p_t.text = action_title
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(26)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_TEXT if is_dark else TEXT_HEAD
        p_t.space_before = Pt(4)

        if num:
            nb = slide.shapes.add_textbox(Inches(11.5), Inches(0.4), Inches(0.9), Inches(0.4))
            ntf = nb.text_frame
            ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
            np = ntf.paragraphs[0]
            np.alignment = PP_ALIGN.RIGHT
            np.text = f"{num:02d} / 12"
            np.font.name = FONT_FAMILY
            np.font.size = Pt(12)
            np.font.bold = True
            np.font.color.rgb = DARK_MUTED if is_dark else TEXT_MUTED

    def set_notes(slide, text):
        slide.notes_slide.notes_text_frame.text = text

    # =========================================================================
    # SLIDE 1: COVER (Deep Slate Luxury #0B1120)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    fill_bg(s1, DARK_BG)

    add_card(s1, Inches(0.9), Inches(0.85), Inches(11.533), Inches(5.8), bg=DARK_CARD, border=DARK_BORDER)
    add_accent_bar(s1, Inches(0.9), Inches(0.85), Inches(11.533), height=Inches(0.08), color=NEON_CYAN)

    add_badge_pill(s1, Inches(1.4), Inches(1.4), Inches(3.6), Inches(0.4), "BÁO CÁO TIẾN ĐỘ 50% • DEEP RL", RGBColor(12, 74, 110), NEON_CYAN)

    tb1 = s1.shapes.add_textbox(Inches(1.4), Inches(2.05), Inches(10.533), Inches(2.6))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "Placement-Based Double Deep Q-Network"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = DARK_TEXT

    p2 = tf1.add_paragraph()
    p2.text = "Học chính sách Tetris hiệu quả mẫu cao trên CPU cá nhân"
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(19)
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_before = Pt(8)

    add_card(s1, Inches(1.4), Inches(4.7), Inches(10.533), Inches(1.35), bg=RGBColor(15, 23, 42), border=RGBColor(38, 54, 84))
    tbf = s1.shapes.add_textbox(Inches(1.65), Inches(4.85), Inches(10.0), Inches(1.0))
    tff = tbf.text_frame
    tff.word_wrap = True
    pf1 = tff.paragraphs[0]
    pf1.text = "Tác giả: [Họ và tên SV] (MSSV: [Mã số SV])    •    GVHD: [Tên Giảng viên]"
    pf1.font.name = FONT_FAMILY
    pf1.font.size = Pt(13.5)
    pf1.font.bold = True
    pf1.font.color.rgb = DARK_TEXT

    pf2 = tff.add_paragraph()
    pf2.text = "Khoa Công nghệ Thông tin    •    Định dạng xuất bản: Springer LNCS / ICCIES Conference (paper.pdf)"
    pf2.font.name = FONT_FAMILY
    pf2.font.size = Pt(12)
    pf2.font.color.rgb = DARK_MUTED
    pf2.space_before = Pt(4)

    set_notes(s1, "Kính thưa Thầy/Cô và các bạn, hôm nay em xin đại diện nhóm báo cáo đề tài nghiên cứu: 'Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning'. Đề tài giải quyết câu hỏi cốt lõi: Làm thế nào để AI tự học chơi Tetris đạt hiệu suất vượt trội mà chỉ cần huấn luyện trên CPU cá nhân trong chưa đầy 17 phút. Sau đây, em xin phép bắt đầu.")

    # =========================================================================
    # SLIDE 2: VẤN ĐỀ & ĐỘNG LỰC (2 Cards, Coral & Blue)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Hai Nút Thắt Triệt Tiêu Hiệu Năng Deep RL Truyền Thống", num=2)

    # Card 1: Credit Assignment (Coral)
    add_card(s2, Inches(0.9), Inches(1.75), Inches(5.6), Inches(5.0))
    add_accent_bar(s2, Inches(0.9), Inches(1.75), Inches(5.6), color=ACCENT_CORAL)
    add_badge_pill(s2, Inches(1.25), Inches(2.1), Inches(2.5), Inches(0.36), "THƯỞNG QUÁ THƯA", PILL_CORAL_BG, PILL_CORAL_TX)

    tb2_1 = s2.shapes.add_textbox(Inches(1.25), Inches(2.65), Inches(4.9), Inches(3.9))
    tf2_1 = tb2_1.text_frame
    tf2_1.word_wrap = True

    p = tf2_1.paragraphs[0]
    p.text = "01. CREDIT ASSIGNMENT"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED

    p_num1 = tf2_1.add_paragraph()
    p_num1.text = "Hàng chục phím vi mô"
    p_num1.font.name = FONT_FAMILY
    p_num1.font.size = Pt(26)
    p_num1.font.bold = True
    p_num1.font.color.rgb = TEXT_HEAD
    p_num1.space_before = Pt(6)

    p_sub1 = tf2_1.add_paragraph()
    p_sub1.text = "Mới thả rơi được 1 khối tetromino."
    p_sub1.font.name = FONT_FAMILY
    p_sub1.font.size = Pt(15)
    p_sub1.font.color.rgb = TEXT_BODY
    p_sub1.space_before = Pt(6)

    p_imp1 = tf2_1.add_paragraph()
    p_imp1.text = "• Thưởng cực thưa gây sụp đổ chính sách (Policy Collapse)."
    p_imp1.font.name = FONT_FAMILY
    p_imp1.font.size = Pt(14)
    p_imp1.font.bold = True
    p_imp1.font.color.rgb = ACCENT_CORAL
    p_imp1.space_before = Pt(20)

    # Card 2: Sample Inefficiency (Sky Blue)
    add_card(s2, Inches(6.8), Inches(1.75), Inches(5.6), Inches(5.0))
    add_accent_bar(s2, Inches(6.8), Inches(1.75), Inches(5.6), color=ACCENT_CYAN)
    add_badge_pill(s2, Inches(7.15), Inches(2.1), Inches(2.8), Inches(0.36), "CHI PHÍ TÍNH TOÁN CAO", PILL_CYAN_BG, PILL_CYAN_TX)

    tb2_2 = s2.shapes.add_textbox(Inches(7.15), Inches(2.65), Inches(4.9), Inches(3.9))
    tf2_2 = tb2_2.text_frame
    tf2_2.word_wrap = True

    p = tf2_2.paragraphs[0]
    p.text = "02. SAMPLE INEFFICIENCY"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED

    p_num2 = tf2_2.add_paragraph()
    p_num2.text = "> 24 giờ GPU Cluster"
    p_num2.font.name = FONT_FAMILY
    p_num2.font.size = Pt(26)
    p_num2.font.bold = True
    p_num2.font.color.rgb = TEXT_HEAD
    p_num2.space_before = Pt(6)

    p_sub2 = tf2_2.add_paragraph()
    p_sub2.text = "Huấn luyện trên ma trận pixel thô 20x10."
    p_sub2.font.name = FONT_FAMILY
    p_sub2.font.size = Pt(15)
    p_sub2.font.color.rgb = TEXT_BODY
    p_sub2.space_before = Pt(6)

    p_imp2 = tf2_2.add_paragraph()
    p_imp2.text = "• Thường bão hòa kẹt dưới 15 hàng dọn sạch."
    p_imp2.font.name = FONT_FAMILY
    p_imp2.font.size = Pt(14)
    p_imp2.font.bold = True
    p_imp2.font.color.rgb = ACCENT_CYAN
    p_imp2.space_before = Pt(20)

    set_notes(s2, "Khi áp dụng Deep RL vào Tetris, các nghiên cứu trước đây gặp 2 nút thắt nghiêm trọng: Thứ nhất là Credit Assignment Latency, người chơi vi mô phải bấm hàng chục phím bấm trái phải xoay mới thả được 1 khối, tín hiệu thưởng cực kỳ thưa thớt khiến thuật toán không biết phím nào tốt, dẫn tới chính sách sụp đổ. Thứ hai là Sample Inefficiency, việc nhồi ảnh pixel thô vào CNN tốn hơn 24 giờ GPU nhưng AI chỉ dọn được dưới 15 hàng do bão hòa giá trị Q.")

    # =========================================================================
    # SLIDE 3: QUY TRÌNH KIẾN TRÚC P-DDQN (FIG. 1 TRONG PAPER)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Quy Trình Kiến Trúc P-DDQN (Fig. 1 Trong Paper)", num=3)

    # Framed Container for Pipeline Fig 1
    add_card(s3, Inches(0.9), Inches(1.7), Inches(11.533), Inches(3.6))
    add_accent_bar(s3, Inches(0.9), Inches(1.7), Inches(11.533), color=ACCENT_CYAN)
    
    # Badge Pill on top of Fig 1
    add_badge_pill(s3, Inches(1.15), Inches(1.85), Inches(2.6), Inches(0.32), "PIPELINE ARCHITECTURE", PILL_CYAN_BG, PILL_CYAN_TX)

    # Embed Fig. 1 from paper.pdf
    fig1_path = r"reports/figures/paper_pipeline_fig1.png"
    if os.path.exists(fig1_path):
        s3.shapes.add_picture(fig1_path, Inches(3.1), Inches(2.22), width=Inches(7.13), height=Inches(2.97))

    # Bottom 4-Stage Container
    add_card(s3, Inches(0.9), Inches(5.45), Inches(11.533), Inches(1.3))
    tb3_steps = s3.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(11.133), Inches(1.1))
    tf3_steps = tb3_steps.text_frame
    tf3_steps.word_wrap = True

    p_st_title = tf3_steps.paragraphs[0]
    p_st_title.text = "BỐN GIAI ĐOẠN QUY TRÌNH (THE FOUR PROCESSING STAGES):"
    p_st_title.font.name = FONT_FAMILY
    p_st_title.font.size = Pt(11)
    p_st_title.font.bold = True
    p_st_title.font.color.rgb = ACCENT_CYAN

    p_st_desc = tf3_steps.add_paragraph()
    p_st_desc.text = "1. Placement Enumeration (Duyệt cặp x, r)   ->   2. 4D Feature Vector (Height, Holes, Bump, Lines)   ->   3. Double DQN Target Decoupling (Online & Target Net)   ->   4. Greedy Action Selection (argmax Q)"
    p_st_desc.font.name = FONT_FAMILY
    p_st_desc.font.size = Pt(12)
    p_st_desc.font.bold = True
    p_st_desc.font.color.rgb = TEXT_HEAD
    p_st_desc.space_before = Pt(4)

    set_notes(s3, "Hình 1 trong bài báo mô tả trực quan 4 giai đoạn hoạt động của kiến trúc P-DDQN: Giai đoạn 1 là duyệt toàn bộ các vị trí đặt gạch hợp lệ (x, r) của khối tetromino hiện tại. Giai đoạn 2 là xây dựng các trạng thái bàn cờ tương lai và trích xuất vector đặc trưng hình học 4 chiều. Giai đoạn 3 là mạng nơ-ron Double DQN định giá trị Q với cơ chế tách biệt Online Network và Target Network. Giai đoạn 4 là chọn nước đi có giá trị kỳ vọng lớn nhất.")

    # =========================================================================
    # SLIDE 4: MÔ HÌNH HÓA MDP (4 Feature Cards + Formula Banner)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Mô Hình Hóa MDP Với Vector Hình Học Bốn Chiều", num=4)

    f_items = [
        ("f1 - Height", "Tổng chiều cao 10 cột", "Đo độ cao bàn cờ", ACCENT_CYAN, "ĐỘ CAO", PILL_CYAN_BG, PILL_CYAN_TX),
        ("f2 - Holes", "Số lỗ hổng bị che lấp", "Phạt nặng nhất", ACCENT_CORAL, "HỐC KẸT", PILL_CORAL_BG, PILL_CORAL_TX),
        ("f3 - Bumpiness", "Độ gồ ghề giữa các cột", "Giữ bề mặt phẳng", ACCENT_INDIGO, "ĐỘ PHẲNG", PILL_INDIGO_BG, PILL_INDIGO_TX),
        ("f4 - Lines", "Số hàng dọn tức thì", "Thưởng bậc hai", ACCENT_EMERALD, "COMBO", PILL_EMERALD_BG, PILL_EMERALD_TX)
    ]
    for idx, (f_name, f_desc, f_sub, color, pill_txt, p_bg, p_tx) in enumerate(f_items):
        cx = Inches(0.9 + idx * 2.95)
        add_card(s4, cx, Inches(1.75), Inches(2.75), Inches(3.4))
        add_accent_bar(s4, cx, Inches(1.75), Inches(2.75), color=color)
        add_badge_pill(s4, cx + Inches(0.2), Inches(2.05), Inches(1.4), Inches(0.35), pill_txt, p_bg, p_tx)

        tb = s4.shapes.add_textbox(cx + Inches(0.2), Inches(2.55), Inches(2.35), Inches(2.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f_name
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(17)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_HEAD

        p2 = tf.add_paragraph()
        p2.text = f_desc
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_BODY
        p2.space_before = Pt(6)

        p3 = tf.add_paragraph()
        p3.text = f"• {f_sub}"
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(12)
        p3.font.bold = True
        p3.font.color.rgb = color
        p3.space_before = Pt(8)

    add_formula_banner(
        s4,
        Inches(0.9), Inches(5.45), Inches(11.533), Inches(1.3),
        formula_title="HÀM THƯỞNG PHI TUYẾN BẬC HAI (REWARD SHAPING FORMULA)",
        formula_text="R(s, a, s') = 1.0 (sống sót) + (Lines × 1.5)² (thưởng combo) - 1.0 ΔHoles - 0.2 ΔBumpiness - 0.5 ΔHeight"
    )

    set_notes(s4, "Trạng thái bàn cờ được trừu tượng hóa thành vector 4 chiều cực kỳ tinh gọn: f1 là tổng chiều cao, f2 là số lỗ hổng bị che khuất, f3 là độ gồ ghề bề mặt và f4 là số hàng ăn được. Hành động là vị trí cột x và góc xoay r. Hàm thưởng sử dụng lũy thừa bậc hai cho số hàng dọn để kích thích AI ăn các combo lớn.")

    # =========================================================================
    # SLIDE 5: MẠNG NƠ-RON & DOUBLE DQN (Giant Metric 4,545 + Target Decoupling)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Mạng 4.5k Tham Số Triệt Tiêu Sai Số Ước Lượng", num=5)

    # Left: MLP
    add_card(s5, Inches(0.9), Inches(1.75), Inches(5.6), Inches(5.0))
    add_accent_bar(s5, Inches(0.9), Inches(1.75), Inches(5.6), color=ACCENT_CYAN)
    add_badge_pill(s5, Inches(1.25), Inches(2.1), Inches(2.5), Inches(0.36), "MLP ARCHITECTURE", PILL_CYAN_BG, PILL_CYAN_TX)

    tb5_1 = s5.shapes.add_textbox(Inches(1.25), Inches(2.65), Inches(4.9), Inches(3.9))
    tf5_1 = tb5_1.text_frame
    tf5_1.word_wrap = True

    p = tf5_1.paragraphs[0]
    p.text = "TỔNG THAM SỐ MẠNG"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED

    p_num = tf5_1.add_paragraph()
    p_num.text = "4,545"
    p_num.font.name = FONT_FAMILY
    p_num.font.size = Pt(50)
    p_num.font.bold = True
    p_num.font.color.rgb = ACCENT_CYAN

    p_lbl = tf5_1.add_paragraph()
    p_lbl.text = "MLP 3 lớp: Input(4) -> 64 -> 64 -> Linear(1)"
    p_lbl.font.name = FONT_FAMILY
    p_lbl.font.size = Pt(14)
    p_lbl.font.color.rgb = TEXT_HEAD
    p_lbl.space_before = Pt(2)

    p_b1 = tf5_1.add_paragraph()
    p_b1.text = "• Checkpoint lưu trữ: Chỉ 82 KB trên đĩa.\n• Độ trễ suy luận: 5.4 ms/bước (>180 FPS trên CPU)."
    p_b1.font.name = FONT_FAMILY
    p_b1.font.size = Pt(13.5)
    p_b1.font.color.rgb = TEXT_BODY
    p_b1.space_before = Pt(14)

    # Right: Double Q-Learning Target
    add_card(s5, Inches(6.8), Inches(1.75), Inches(5.6), Inches(5.0))
    add_accent_bar(s5, Inches(6.8), Inches(1.75), Inches(5.6), color=ACCENT_INDIGO)
    add_badge_pill(s5, Inches(7.15), Inches(2.1), Inches(2.8), Inches(0.36), "TARGET DECOUPLING", PILL_INDIGO_BG, PILL_INDIGO_TX)

    tb5_2 = s5.shapes.add_textbox(Inches(7.15), Inches(2.65), Inches(4.9), Inches(3.9))
    tf5_2 = tb5_2.text_frame
    tf5_2.word_wrap = True

    p = tf5_2.paragraphs[0]
    p.text = "DOUBLE Q-LEARNING TARGET"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = TEXT_MUTED

    p_num2 = tf5_2.add_paragraph()
    p_num2.text = "Tách Biệt 2 Mạng"
    p_num2.font.name = FONT_FAMILY
    p_num2.font.size = Pt(26)
    p_num2.font.bold = True
    p_num2.font.color.rgb = TEXT_HEAD
    p_num2.space_before = Pt(6)

    p_lbl2 = tf5_2.add_paragraph()
    p_lbl2.text = "Online Network chọn nước đi; Target Network định giá."
    p_lbl2.font.name = FONT_FAMILY
    p_lbl2.font.size = Pt(14)
    p_lbl2.font.color.rgb = TEXT_BODY
    p_lbl2.space_before = Pt(6)

    p_b2 = tf5_2.add_paragraph()
    p_b2.text = "• Triệt tiêu hoàn toàn Overestimation Bias.\n• Đồng bộ mạng mục tiêu định kỳ 10 episodes."
    p_b2.font.name = FONT_FAMILY
    p_b2.font.size = Pt(13.5)
    p_b2.font.bold = True
    p_b2.font.color.rgb = ACCENT_INDIGO
    p_b2.space_before = Pt(14)

    set_notes(s5, "Mô hình mạng nơ-ron chỉ có 4,545 tham số, kích thước file chỉ 82 KB với độ trễ suy luận 5.4 ms. Bằng việc áp dụng Double DQN, chúng em tách biệt mạng chọn hành động Online và mạng định giá trị Target, giải quyết dứt điểm hiện tượng thổi phồng giá trị Q.")

    # =========================================================================
    # SLIDE 6: MÔ PHỎNG SIÊU TỐC (>5,000 Steps/s + Dark Banner)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Mô Phỏng Siêu Tốc Hơn 5.000 Bước Mỗi Giây Trên CPU", num=6)

    badges = [
        ("> 5,000", "STEPS / GIÂY", "Engine NumPy thuần không GPU", ACCENT_CYAN, "TỐC ĐỘ CAO", PILL_CYAN_BG, PILL_CYAN_TX),
        ("< 60 MB", "BỘ NHỚ RAM", "Không rò rỉ bộ nhớ khi chạy dài", ACCENT_INDIGO, "TIẾT KIỆM RAM", PILL_INDIGO_BG, PILL_INDIGO_TX),
        ("7-Bag", "GUIDELINE CHUẨN", "Loại bỏ chuỗi gạch thiên vị", ACCENT_EMERALD, "CÔNG BẰNG", PILL_EMERALD_BG, PILL_EMERALD_TX)
    ]
    for idx, (b_val, b_lbl, b_sub, color, pill_txt, p_bg, p_tx) in enumerate(badges):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s6, cx, Inches(1.75), Inches(3.65), Inches(3.4))
        add_accent_bar(s6, cx, Inches(1.75), Inches(3.65), color=color)
        add_badge_pill(s6, cx + Inches(0.25), Inches(2.05), Inches(1.8), Inches(0.35), pill_txt, p_bg, p_tx)

        tb = s6.shapes.add_textbox(cx + Inches(0.2), Inches(2.5), Inches(3.25), Inches(2.5))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = b_val
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(46)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = b_lbl
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(13.5)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_HEAD
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = b_sub
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(4)

    add_formula_banner(
        s6,
        Inches(0.9), Inches(5.45), Inches(11.533), Inches(1.3),
        formula_title="TỐI ƯU HÓA MA TRẬN VECTOR HÓA (VECTORIZED MATRIX ENGINE)",
        formula_text="get_next_states(): Quét toàn bộ điểm rơi hợp lệ của khối gạch chỉ trong 1 bước tính ma trận."
    )

    set_notes(s6, "Chúng em tự xây dựng môi trường Gym thuần NumPy với tốc độ vượt 5,000 bước/giây, tiêu tốn chưa đến 60 MB RAM và hỗ trợ túi gạch chuẩn 7-Bag. Hàm get_next_states() tối ưu ma trận giúp AI đánh giá toàn bộ nước đi tức thì.")

    # =========================================================================
    # SLIDE 7: ĐỐI CHUẨN THỰC NGHIỆM 100 GAMES (TABLE 1 TRONG PAPER)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Kết Quả Đối Chuẩn Thực Nghiệm 100 Games (Table 1 Trong Paper)", num=7)

    # 3 Top KPI Cards
    top_kpis = [
        ("287.5", "HÀNG DỌN TRUNG BÌNH", "Median: 388.0 | Max: 398", ACCENT_CYAN, PILL_CYAN_BG, PILL_CYAN_TX, "CLEARED LINES"),
        ("23,360.8", "ĐIỂM SỐ TRUNG BÌNH", "Gấp 24.2 lần Naive Greedy (965.4)", ACCENT_AMBER, PILL_AMBER_BG, PILL_AMBER_TX, "MEAN SCORE"),
        ("81.3", "ĐIỂM / MỖI HÀNG", "Gấp 1.6 lần Greedy (51.5 pts/line)", ACCENT_EMERALD, PILL_EMERALD_BG, PILL_EMERALD_TX, "COMBO STYLE")
    ]
    for idx, (val, lbl, sub, color, p_bg, p_tx, p_txt) in enumerate(top_kpis):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s7, cx, Inches(1.7), Inches(3.65), Inches(1.4))
        add_accent_bar(s7, cx, Inches(1.7), Inches(3.65), color=color)
        add_badge_pill(s7, cx + Inches(0.2), Inches(1.85), Inches(1.8), Inches(0.3), p_txt, p_bg, p_tx)

        tb = s7.shapes.add_textbox(cx + Inches(0.2), Inches(2.15), Inches(3.25), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{val} - {lbl}"
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_HEAD

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # Table 1 Container & Shape
    t7_shape = s7.shapes.add_table(4, 7, Inches(0.9), Inches(3.3), Inches(11.533), Inches(2.2))
    t7 = t7_shape.table
    t7.columns[0].width = Inches(2.4)
    t7.columns[1].width = Inches(1.9)
    t7.columns[2].width = Inches(1.2)
    t7.columns[3].width = Inches(1.1)
    t7.columns[4].width = Inches(1.8)
    t7.columns[5].width = Inches(1.7)
    t7.columns[6].width = Inches(1.433)

    t7_data = [
        ["Tác tử (Agent)", "Lines (Mean ± Std)", "Median", "Max", "Mean Score", "Survival Placements", "Points / Line"],
        ["Random", "0.1 ± 0.3", "0.0", "1", "4.8", "25.5", "40.0"],
        ["Naive greedy", "18.8 ± 13.6", "16.5", "66", "965.4", "85.2", "51.5"],
        ["P-DDQN (Đề xuất)", "287.5 ± 131.8", "388.0", "398", "23,360.8", "749.1", "81.3"]
    ]
    for ri, row in enumerate(t7.rows):
        for ci, cell in enumerate(row.cells):
            cell.text = t7_data[ri][ci]
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_FAMILY
            p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            if ri == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(30, 41, 59) # Slate 800
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = NEON_CYAN
            else:
                cell.fill.solid()
                bg = RGBColor(255, 255, 255) if ri % 2 == 1 else RGBColor(241, 245, 249)
                cell.fill.fore_color.rgb = bg
                p.font.size = Pt(12)
                if ri == 3: # Highlight Proposed
                    p.font.bold = True
                    p.font.color.rgb = ACCENT_CYAN if ci in [0, 1, 4, 6] else TEXT_HEAD
                else:
                    p.font.color.rgb = TEXT_BODY

    # Takeaway Banner at bottom
    add_card(s7, Inches(0.9), Inches(5.7), Inches(11.533), Inches(1.05), border=ACCENT_EMERALD)
    tb_b7 = s7.shapes.add_textbox(Inches(1.1), Inches(5.78), Inches(11.133), Inches(0.85))
    p_b7 = tb_b7.text_frame.paragraphs[0]
    p_b7.alignment = PP_ALIGN.CENTER
    p_b7.text = "🏆 Phân tích Table 1: P-DDQN đạt 81.3 điểm/hàng (gấp 1.6 lần Greedy), chạm trần 1,000 bước ở 54/100 ván, khẳng định AI học chiến thuật tích lũy thế cờ để ăn combo 3-4 hàng cùng lúc."
    p_b7.font.name = FONT_FAMILY
    p_b7.font.size = Pt(12.5)
    p_b7.font.bold = True
    p_b7.font.color.rgb = RGBColor(4, 120, 87)

    set_notes(s7, "Bảng 1 trong bài báo công bố kết quả thực nghiệm 100 ván đấu độc lập với trần kiểm thử 1,000 bước. Tác tử ngẫu nhiên chỉ sống được 25 bước và dọn 0.1 hàng. Naive Greedy dọn được 18.8 hàng và dừng ở 85 bước do bẫy lỗ hổng. Mô hình P-DDQN dọn trung bình 287.5 hàng (trung vị 388.0 hàng, chạm trần 1,000 bước ở 54 ván). Đặc biệt, chỉ số 81.3 điểm/hàng chứng minh AI đã học được chiến thuật dọn combo đa hàng thay vì ăn lẻ tẻ 40 điểm/hàng như cách chơi thông thường.")

    # =========================================================================
    # SLIDE 8: TIẾN TRÌNH HỌC TẬP (70% Image Area Framed Card)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Chính Sách Tự Động Đột Phá Sau 700 Tập Huấn Luyện", num=8)

    img_miles = r"C:\Users\Khang\Desktop\Mon_REL\project\reports\figures\checkpoint_milestones_progression.png"
    if os.path.exists(img_miles):
        add_card(s8, Inches(0.9), Inches(1.75), Inches(11.533), Inches(4.35))
        s8.shapes.add_picture(img_miles, Inches(1.1), Inches(1.9), width=Inches(11.133))

    add_card(s8, Inches(0.9), Inches(6.25), Inches(11.533), Inches(0.85))
    add_badge_pill(s8, Inches(1.1), Inches(6.38), Inches(2.0), Inches(0.35), "TIẾN TRÌNH POLICY", PILL_INDIGO_BG, PILL_INDIGO_TX)
    tb_b8 = s8.shapes.add_textbox(Inches(3.3), Inches(6.32), Inches(8.9), Inches(0.7))
    p_b8 = tb_b8.text_frame.paragraphs[0]
    p_b8.text = "Ep 100 tránh thua sớm   ->   Ep 500 san phẳng hốc kẹt   ->   Ep 1,000 làm chủ combo dọn hàng."
    p_b8.font.name = FONT_FAMILY
    p_b8.font.size = Pt(13)
    p_b8.font.bold = True
    p_b8.font.color.rgb = TEXT_HEAD

    set_notes(s8, "Nhìn vào biểu đồ tiến trình mốc checkpoint: Ở 200 tập đầu, tác tử học cách hạ chiều cao để tránh thua. Từ tập 300 đến 600, AI bắt đầu triệt tiêu hốc kẹt. Sau tập 700, tác tử bùng nổ chiến thuật dọn combo và đạt đỉnh cao 1,127 hàng.")

    # =========================================================================
    # SLIDE 9: PHÂN PHỐI THỰC NGHIỆM (70% Image Area Framed Card)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Phân Phối Thực Nghiệm Khẳng Định Độ Ổn Định Vượt Trội", num=9)

    img_bench = r"C:\Users\Khang\Desktop\Mon_REL\project\reports\figures\benchmark_comparison.png"
    if os.path.exists(img_bench):
        add_card(s9, Inches(0.9), Inches(1.75), Inches(11.533), Inches(4.35))
        s9.shapes.add_picture(img_bench, Inches(1.1), Inches(2.0), width=Inches(11.133))

    add_card(s9, Inches(0.9), Inches(6.25), Inches(11.533), Inches(0.85))
    add_badge_pill(s9, Inches(1.1), Inches(6.38), Inches(2.0), Inches(0.35), "ĐỘ ỔN ĐỊNH CAO", PILL_CYAN_BG, PILL_CYAN_TX)
    tb_b9 = s9.shapes.add_textbox(Inches(3.3), Inches(6.32), Inches(8.9), Inches(0.7))
    p_b9 = tb_b9.text_frame.paragraphs[0]
    p_b9.text = "Trung vị >220 hàng, bỏ xa Greedy (<35 hàng), chứng minh chính sách ổn định, không ăn may."
    p_b9.font.name = FONT_FAMILY
    p_b9.font.size = Pt(13)
    p_b9.font.bold = True
    p_b9.font.color.rgb = TEXT_HEAD

    set_notes(s9, "Biểu đồ phân phối thực nghiệm chứng minh Naive Greedy bị kẹt hoàn toàn dưới 35 hàng do bẫy lỗ hổng. Trong khi đó, P-DDQN đạt trung vị trên 220 hàng và phân vị trên tiệm cận 400 hàng, khẳng định độ ổn định vượt trội.")

    # =========================================================================
    # SLIDE 10: ĐỐI CHIẾU QUỐC TẾ (Deep Slate #0B1120 - 3 Dark Luxury Cards)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Vượt Trội Về Chi Phí Tính Toán So Với Công Trình Quốc Tế", num=10, is_dark=True)

    intl_pillars = [
        ("Nhanh hơn 21x", "TỐC ĐỘ HỘI TỤ", "Hội tụ trong 16.8 phút vs 6h GPU Cluster của Chen (UIUC 2021)", ACCENT_CYAN, "SAMPLE EFFICIENCY"),
        ("Chỉ 1 CPU", "CHI PHÍ PHẦN CỨNG", "Thay vì cụm GPU chạy World Models (Liu 2020, Bairaktaris 2025)", ACCENT_INDIGO, "TIẾT KIỆM TÀI NGUYÊN"),
        ("Vượt 36.1%", "HIỆU NĂNG ĐIỂM SỐ", "Chiến lược combo vượt thuật toán giải tích Pierre Dellacherie", ACCENT_EMERALD, "ĐIỂM SỐ ĐỘT PHÁ")
    ]
    for idx, (val, lbl, sub, color, pill_txt) in enumerate(intl_pillars):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s10, cx, Inches(1.75), Inches(3.65), Inches(5.0), bg=DARK_CARD, border=DARK_BORDER)
        add_accent_bar(s10, cx, Inches(1.75), Inches(3.65), color=color)
        add_badge_pill(s10, cx + Inches(0.25), Inches(2.05), Inches(2.6), Inches(0.36), pill_txt, RGBColor(15, 23, 42), color)

        tb = s10.shapes.add_textbox(cx + Inches(0.2), Inches(2.6), Inches(3.25), Inches(3.9))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = val
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(36)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = lbl
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = DARK_TEXT
        p2.space_before = Pt(8)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = sub
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(12)
        p3.font.color.rgb = DARK_MUTED
        p3.space_before = Pt(14)

    set_notes(s10, "So với các công bố quốc tế từ 2020 đến 2025: Mô hình hội tụ nhanh hơn 21 lần so với cụm GPU của UIUC, chỉ chạy trên một CPU cá nhân thay vì cụm GPU đắt đỏ, và đạt điểm số vượt trội so với Heuristic chuyên gia.")

    # =========================================================================
    # SLIDE 11: DEMO TRỰC TIẾP (2 Code Terminal Cards)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Trực Quan Hóa Thực Chiến Trên Hai Nền Tảng", num=11)

    # Mode 1: Pygame
    add_card(s11, Inches(0.9), Inches(1.75), Inches(5.6), Inches(5.0))
    add_accent_bar(s11, Inches(0.9), Inches(1.75), Inches(5.6), color=ACCENT_CYAN)
    add_badge_pill(s11, Inches(1.25), Inches(2.05), Inches(2.6), Inches(0.36), "VISUALIZER PYGAME", PILL_CYAN_BG, PILL_CYAN_TX)

    # Code Block 1
    c_cb1 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.25), Inches(2.6), Inches(4.9), Inches(0.85))
    c_cb1.fill.solid()
    c_cb1.fill.fore_color.rgb = RGBColor(15, 23, 42)
    c_cb1.line.color.rgb = RGBColor(38, 54, 84)
    tb_cmd1 = s11.shapes.add_textbox(Inches(1.35), Inches(2.65), Inches(4.7), Inches(0.75))
    p_cmd1 = tb_cmd1.text_frame.paragraphs[0]
    p_cmd1.text = "python src/play_ai.py --agent dqn --fps 30"
    p_cmd1.font.name = "Consolas"
    p_cmd1.font.size = Pt(13)
    p_cmd1.font.bold = True
    p_cmd1.font.color.rgb = NEON_CYAN

    tb11_1 = s11.shapes.add_textbox(Inches(1.25), Inches(3.65), Inches(4.9), Inches(2.8))
    tf11_1 = tb11_1.text_frame
    tf11_1.word_wrap = True
    p_f1 = tf11_1.paragraphs[0]
    p_f1.text = "• Giám sát 4 đặc trưng hình học thời gian thực.\n• Phím nóng đối kháng: [D] DQN vs [H] Heuristic."
    p_f1.font.name = FONT_FAMILY
    p_f1.font.size = Pt(14)
    p_f1.font.color.rgb = TEXT_BODY

    # Mode 2: Local Web UI
    add_card(s11, Inches(6.8), Inches(1.75), Inches(5.6), Inches(5.0))
    add_accent_bar(s11, Inches(6.8), Inches(1.75), Inches(5.6), color=ACCENT_AMBER)
    add_badge_pill(s11, Inches(7.15), Inches(2.05), Inches(2.6), Inches(0.36), "LOCAL WEB UI", PILL_AMBER_BG, PILL_AMBER_TX)

    # Code Block 2
    c_cb2 = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.15), Inches(2.6), Inches(4.9), Inches(0.85))
    c_cb2.fill.solid()
    c_cb2.fill.fore_color.rgb = RGBColor(15, 23, 42)
    c_cb2.line.color.rgb = RGBColor(38, 54, 84)
    tb_cmd2 = s11.shapes.add_textbox(Inches(7.25), Inches(2.65), Inches(4.7), Inches(0.75))
    p_cmd2 = tb_cmd2.text_frame.paragraphs[0]
    p_cmd2.text = "http://localhost:8080  ->  🤖 AI AUTOPLAY"
    p_cmd2.font.name = "Consolas"
    p_cmd2.font.size = Pt(13)
    p_cmd2.font.bold = True
    p_cmd2.font.color.rgb = ACCENT_AMBER

    tb11_2 = s11.shapes.add_textbox(Inches(7.15), Inches(3.65), Inches(4.9), Inches(2.8))
    tf11_2 = tb11_2.text_frame
    tf11_2.word_wrap = True
    p_f2 = tf11_2.paragraphs[0]
    p_f2.text = "• Chuẩn Guideline: 7-Bag, Hold, 3 Next, Ghost.\n• Âm thanh Web Audio API & hiệu ứng nổ Neon."
    p_f2.font.name = FONT_FAMILY
    p_f2.font.size = Pt(14)
    p_f2.font.color.rgb = TEXT_BODY

    set_notes(s11, "Hệ thống đã sẵn sàng demo trực tiếp ở 2 chế độ: Chế độ 1 là Pygame Visualizer theo dõi 4 đặc trưng và đối đầu DQN với Heuristic bằng phím nóng. Chế độ 2 là Web Cyber Tetris với AI Autoplay chạy mượt mà trên trình duyệt.")

    # =========================================================================
    # SLIDE 12: TỔNG KẾT & LỘ TRÌNH (Deep Slate #0B1120)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Hoàn Thành Mốc 50% Tiến Độ Và Kế Hoạch Giai Đoạn Hai", num=12, is_dark=True)

    # Box Left: Done (Emerald)
    add_card(s12, Inches(0.9), Inches(1.75), Inches(5.6), Inches(4.35), bg=DARK_CARD, border=DARK_BORDER)
    add_accent_bar(s12, Inches(0.9), Inches(1.75), Inches(5.6), color=ACCENT_EMERALD)
    add_badge_pill(s12, Inches(1.25), Inches(2.05), Inches(2.6), Inches(0.36), "ĐÃ HOÀN TẤT 50%", RGBColor(6, 78, 59), ACCENT_EMERALD)

    tb12_1 = s12.shapes.add_textbox(Inches(1.25), Inches(2.6), Inches(4.9), Inches(3.3))
    tf12_1 = tb12_1.text_frame
    tf12_1.word_wrap = True
    p_d = tf12_1.paragraphs[0]
    p_d.text = "• Mô hình hóa MDP & Gym siêu tốc (>5,000 steps/s).\n• P-DDQN hội tụ: Điểm số vượt Heuristic 36.1%.\n• Bản thảo bài báo khoa học Springer LNCS."
    p_d.font.name = FONT_FAMILY
    p_d.font.size = Pt(14)
    p_d.font.color.rgb = DARK_TEXT
    p_d.space_before = Pt(4)

    # Box Right: Next (Cyan)
    add_card(s12, Inches(6.8), Inches(1.75), Inches(5.6), Inches(4.35), bg=DARK_CARD, border=DARK_BORDER)
    add_accent_bar(s12, Inches(6.8), Inches(1.75), Inches(5.6), color=NEON_CYAN)
    add_badge_pill(s12, Inches(7.15), Inches(2.05), Inches(2.6), Inches(0.36), "LỘ TRÌNH TIẾP THEO", RGBColor(12, 74, 110), NEON_CYAN)

    tb12_2 = s12.shapes.add_textbox(Inches(7.15), Inches(2.6), Inches(4.9), Inches(3.3))
    tf12_2 = tb12_2.text_frame
    tf12_2.word_wrap = True
    p_n = tf12_2.paragraphs[0]
    p_n.text = "• Thử nghiệm Dueling DDQN & Prioritized Replay.\n• Tích hợp nhìn trước khối kế tiếp (Next Piece).\n• Chuyển giao sang bài toán xếp hàng 2D Bin Packing."
    p_n.font.name = FONT_FAMILY
    p_n.font.size = Pt(14)
    p_n.font.color.rgb = DARK_TEXT
    p_n.space_before = Pt(4)

    c_ty = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(6.3), Inches(11.533), Inches(0.8))
    c_ty.fill.solid()
    c_ty.fill.fore_color.rgb = RGBColor(15, 23, 42)
    c_ty.line.color.rgb = RGBColor(38, 54, 84)
    tb_ty = s12.shapes.add_textbox(Inches(1.1), Inches(6.38), Inches(11.133), Inches(0.65))
    p_ty = tb_ty.text_frame.paragraphs[0]
    p_ty.alignment = PP_ALIGN.CENTER
    p_ty.text = "CHÂN THÀNH CẢM ƠN THẦY/CÔ VÀ CÁC BẠN! • Q&A DEFENSE"
    p_ty.font.name = FONT_FAMILY
    p_ty.font.size = Pt(14)
    p_ty.font.bold = True
    p_ty.font.color.rgb = NEON_CYAN

    set_notes(s12, "Tóm lại, đề tài đã hoàn tất xuất sắc 50% tiến độ nghiên cứu, chứng minh mô hình P-DDQN giải quyết trọn vẹn bài toán sample efficiency trên Tetris. Ở giai đoạn hai, nhóm sẽ thử nghiệm Dueling DDQN và hướng tới bài toán đóng gói 2D trong Logistics. Em xin chân thành cảm ơn Thầy/Cô đã chú ý lắng nghe!")

    prs.save(output_path)
    print(f"Successfully generated deck: {output_path}")

if __name__ == "__main__":
    out_file = r"C:\Users\Khang\Desktop\Mon_REL\project\SLIDE_THUYET_TRINH_BAO_CAO_TIEN_DO_FINAL.pptx"
    build_cyber_tech_luxury_deck(out_file)
