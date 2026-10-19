import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_minimal_executive_deck(output_path):
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Executive Light Palette (McKinsey / Apple Keynote clean style)
    BG_LIGHT = RGBColor(250, 250, 252)       # Ultra-clean Off-White #FAFAFC
    CARD_LIGHT = RGBColor(255, 255, 255)     # Crisp White #FFFFFF
    BORDER_SUBTLE = RGBColor(226, 232, 240)  # Slate 200 #E2E8F0
    BORDER_HIGHLIGHT = RGBColor(186, 230, 253) # Sky 200
    
    TEXT_HEAD = RGBColor(15, 23, 42)         # Slate 900 #0F172A
    TEXT_BODY = RGBColor(71, 85, 105)        # Slate 600 #475569
    TEXT_MUTED = RGBColor(148, 163, 184)     # Slate 400 #94A3B8

    # Dark Covers
    BG_DARK = RGBColor(15, 23, 42)           # Slate 900
    CARD_DARK = RGBColor(30, 41, 59)         # Slate 800
    BORDER_DARK = RGBColor(51, 65, 85)       # Slate 700
    DARK_MUTED = RGBColor(148, 163, 184)     # Slate 400

    # Accents
    PRIMARY_BLUE = RGBColor(2, 132, 199)     # Sky 600 #0284C7
    PRIMARY_INDIGO = RGBColor(79, 70, 229)   # Indigo 600 #4F46E5
    ACCENT_EMERALD = RGBColor(16, 185, 129)  # Emerald 500 #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11)    # Amber 500 #F59E0B
    ACCENT_ROSE = RGBColor(225, 29, 72)      # Rose 600 #E11D48
    ACCENT_CYAN = RGBColor(6, 182, 212)      # Cyan 500 #06B6D4

    def fill_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_light_header(slide, action_title, category="BÁO CÁO TIẾN ĐỘ 50% • REINFORCEMENT LEARNING", num=None):
        fill_bg(slide, BG_LIGHT)

        # Header Box
        hb = slide.shapes.add_textbox(Inches(0.9), Inches(0.45), Inches(11.533), Inches(0.95))
        tf = hb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = PRIMARY_BLUE

        p_t = tf.add_paragraph()
        p_t.text = action_title
        p_t.font.size = Pt(21)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_HEAD
        p_t.space_before = Pt(3)

        if num:
            nb = slide.shapes.add_textbox(Inches(11.6), Inches(0.45), Inches(0.8), Inches(0.4))
            ntf = nb.text_frame
            ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
            np = ntf.paragraphs[0]
            np.alignment = PP_ALIGN.RIGHT
            np.text = f"{num:02d} / 12"
            np.font.size = Pt(10)
            np.font.bold = True
            np.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg=CARD_LIGHT, border=BORDER_SUBTLE):
        c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        c.fill.solid()
        c.fill.fore_color.rgb = bg
        c.line.color.rgb = border
        c.line.width = Pt(1.2)
        return c

    def set_notes(slide, text):
        slide.notes_slide.notes_text_frame.text = text

    # =========================================================================
    # SLIDE 1: COVER (Executive Dark Minimalist)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    fill_bg(s1, BG_DARK)

    # Hero Box
    h1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(0.9), Inches(11.533), Inches(5.7))
    h1.fill.solid()
    h1.fill.fore_color.rgb = CARD_DARK
    h1.line.color.rgb = ACCENT_CYAN
    h1.line.width = Pt(1.5)

    tb1 = s1.shapes.add_textbox(Inches(1.4), Inches(1.5), Inches(10.533), Inches(3.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU 50% • HỌC TĂNG CƯỜNG (REL)"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN

    p1 = tf1.add_paragraph()
    p1.text = "Placement-Based Double Deep Q-Network"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_before = Pt(8)

    p2 = tf1.add_paragraph()
    p2.text = "Học chính sách Tetris hiệu quả mẫu cao trên CPU"
    p2.font.size = Pt(16)
    p2.font.color.rgb = PRIMARY_BLUE
    p2.space_before = Pt(6)

    # Clean Author Footer
    tb_foot = s1.shapes.add_textbox(Inches(1.4), Inches(4.9), Inches(10.533), Inches(1.2))
    tff = tb_foot.text_frame
    pf = tff.paragraphs[0]
    pf.text = "Tác giả: [Họ và tên SV] (MSSV: [Mã số SV])    •    GVHD: [Tên Giảng viên]    •    Chuẩn Springer LNCS (paper.pdf)"
    pf.font.size = Pt(11)
    pf.font.color.rgb = DARK_MUTED

    set_notes(s1, "Kính thưa Thầy/Cô và các bạn, hôm nay em xin đại diện nhóm báo cáo đề tài nghiên cứu: 'Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning'. Đề tài giải quyết bài toán cốt lõi: Làm thế nào để AI tự học chơi Tetris đạt hiệu suất vượt trội mà chỉ cần huấn luyện trên CPU cá nhân trong chưa đầy 17 phút. Sau đây, em xin phép bắt đầu.")

    # =========================================================================
    # SLIDE 2: VẤN ĐỀ & ĐỘNG LỰC (2 Pain Points Only - 24 words total!)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_light_header(s2, "Hai Nút Thắt Triệt Tiêu Hiệu Năng Deep RL Truyền Thống", num=2)

    # Box 1: Credit Assignment Latency (Amber / Red)
    add_card(s2, Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.9))
    tb2_1 = s2.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(5.0), Inches(4.3))
    tf2_1 = tb2_1.text_frame
    tf2_1.word_wrap = True

    p = tf2_1.paragraphs[0]
    p.text = "01. CREDIT ASSIGNMENT"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ROSE

    p_num1 = tf2_1.add_paragraph()
    p_num1.text = "Hàng chục phím vi mô"
    p_num1.font.size = Pt(24)
    p_num1.font.bold = True
    p_num1.font.color.rgb = TEXT_HEAD
    p_num1.space_before = Pt(8)

    p_sub1 = tf2_1.add_paragraph()
    p_sub1.text = "Mới thả rơi được một khối tetromino."
    p_sub1.font.size = Pt(12)
    p_sub1.font.color.rgb = TEXT_BODY
    p_sub1.space_before = Pt(4)

    p_imp1 = tf2_1.add_paragraph()
    p_imp1.text = "• Hậu quả: Thưởng quá thưa gây Policy Collapse."
    p_imp1.font.size = Pt(11)
    p_imp1.font.bold = True
    p_imp1.font.color.rgb = ACCENT_ROSE
    p_imp1.space_before = Pt(18)

    # Box 2: Sample Inefficiency (Blue)
    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9))
    tb2_2 = s2.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.0), Inches(4.3))
    tf2_2 = tb2_2.text_frame
    tf2_2.word_wrap = True

    p = tf2_2.paragraphs[0]
    p.text = "02. SAMPLE INEFFICIENCY"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    p_num2 = tf2_2.add_paragraph()
    p_num2.text = "> 24 giờ GPU Cluster"
    p_num2.font.size = Pt(24)
    p_num2.font.bold = True
    p_num2.font.color.rgb = TEXT_HEAD
    p_num2.space_before = Pt(8)

    p_sub2 = tf2_2.add_paragraph()
    p_sub2.text = "Huấn luyện trên ảnh pixel thô 20x10."
    p_sub2.font.size = Pt(12)
    p_sub2.font.color.rgb = TEXT_BODY
    p_sub2.space_before = Pt(4)

    p_imp2 = tf2_2.add_paragraph()
    p_imp2.text = "• Hậu quả: Thường kẹt dưới 15 hàng dọn sạch."
    p_imp2.font.size = Pt(11)
    p_imp2.font.bold = True
    p_imp2.font.color.rgb = PRIMARY_BLUE
    p_imp2.space_before = Pt(18)

    set_notes(s2, "Kính thưa Thầy/Cô, khi áp dụng Deep RL vào Tetris, các nghiên cứu trước đây gặp 2 nút thắt nghiêm trọng: Thứ nhất là Credit Assignment Latency, người chơi vi mô phải bấm hàng chục phím bấm trái phải xoay mới thả được 1 khối, tín hiệu thưởng cực kỳ thưa thớt khiến thuật toán không biết phím nào tốt, dẫn tới chính sách sụp đổ. Thứ hai là Sample Inefficiency, việc nhồi ảnh pixel thô vào CNN tốn hơn 24 giờ GPU nhưng AI chỉ dọn được dưới 15 hàng do bão hòa giá trị Q.")

    # =========================================================================
    # SLIDE 3: KIẾN TRÚC & ĐÓNG GÓP (3 Clean Pillars - 32 words total!)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_light_header(s3, "Ba Trụ Cột Đột Phá Của Kiến Trúc P-DDQN", num=3)

    pillars = [
        ("01", "HÀNH ĐỘNG VĨ MÔ",
         "Macro Placement (x, r)",
         "• Rút ngắn chuỗi quyết định.\n• Vector 4D nắm bắt hình học."),
        ("02", "DOUBLE DQN",
         "Target Decoupling",
         "• Triệt tiêu Overestimation Bias.\n• Đồng bộ định kỳ 10 episodes."),
        ("03", "HIỆU QUẢ TRÊN CPU",
         "16.8 Phút Hội Tụ",
         "• Mạng chỉ 4,545 tham số.\n• Độ trễ 5.4 ms (>180 FPS).")
    ]
    for idx, (num, tag, title, body) in enumerate(pillars):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s3, cx, Inches(1.8), Inches(3.65), Inches(4.9))

        tb = s3.shapes.add_textbox(cx + Inches(0.25), Inches(2.1), Inches(3.15), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p_n = tf.paragraphs[0]
        p_n.text = num
        p_n.font.size = Pt(28)
        p_n.font.bold = True
        p_n.font.color.rgb = PRIMARY_BLUE

        p_tag = tf.add_paragraph()
        p_tag.text = tag
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = TEXT_MUTED
        p_tag.space_before = Pt(4)

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_HEAD
        p_t.space_before = Pt(4)

        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = TEXT_BODY
        p_b.space_before = Pt(14)

    set_notes(s3, "Đề tài giải quyết 2 nút thắt trên bằng 3 trụ cột: Thứ nhất, chuyển từ phím bấm vi mô sang hành động vĩ mô chọn điểm rơi (x, r) kết hợp vector hình học 4 chiều. Thứ hai, dùng cơ chế Double DQN tách biệt 2 mạng để triệt tiêu việc thổi phồng giá trị Q. Thứ ba, tối ưu toàn diện để hội tụ hoàn hảo chỉ trong 16.8 phút trên CPU cá nhân.")

    # =========================================================================
    # SLIDE 4: MÔ HÌNH HÓA MDP (Hero Formula + 4 Cards - 30 words total!)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_light_header(s4, "Mô Hình Hóa MDP Với Vector Hình Học Bốn Chiều", num=4)

    # Hero Formula Card at Top
    c_hero4 = add_card(s4, Inches(0.9), Inches(1.8), Inches(11.533), Inches(1.3))
    tb_h4 = s4.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(11.133), Inches(1.1))
    tf_h4 = tb_h4.text_frame
    p_h4 = tf_h4.paragraphs[0]
    p_h4.alignment = PP_ALIGN.CENTER
    p_h4.text = "Trạng thái:  s_t = [ f1,  f2,  f3,  f4 ]^T    •    Hành động:  a = (x, r)"
    p_h4.font.size = Pt(16)
    p_h4.font.bold = True
    p_h4.font.color.rgb = PRIMARY_BLUE

    # 4 Cards for f1, f2, f3, f4
    f_items = [
        ("f1 - Height", "Tổng chiều cao 10 cột", "Đo độ cao bàn cờ"),
        ("f2 - Holes", "Số lỗ hổng bị che lấp", "Phạt nặng nhất"),
        ("f3 - Bumpiness", "Độ gồ ghề giữa các cột", "Giữ bề mặt phẳng"),
        ("f4 - Lines", "Số hàng dọn tức thì", "Thưởng lũy thừa bậc hai")
    ]
    for idx, (f_name, f_desc, f_sub) in enumerate(f_items):
        cx = Inches(0.9 + idx * 2.95)
        add_card(s4, cx, Inches(3.35), Inches(2.75), Inches(2.2))

        tb = s4.shapes.add_textbox(cx + Inches(0.15), Inches(3.55), Inches(2.45), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f_name
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_HEAD

        p2 = tf.add_paragraph()
        p2.text = f_desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_BODY
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = f_sub
        p3.font.size = Pt(9.5)
        p3.font.italic = True
        p3.font.color.rgb = PRIMARY_BLUE
        p3.space_before = Pt(6)

    # Bottom Single-line Formula
    tb_bot4 = s4.shapes.add_textbox(Inches(0.9), Inches(5.8), Inches(11.533), Inches(0.8))
    p_b4 = tb_bot4.text_frame.paragraphs[0]
    p_b4.alignment = PP_ALIGN.CENTER
    p_b4.text = "Hàm thưởng: R = 1.0 (sống sót) + (Lines × 1.5)² (thưởng combo) - Phạt Holes - Phạt Bumpiness"
    p_b4.font.size = Pt(11)
    p_b4.font.bold = True
    p_b4.font.color.rgb = ACCENT_EMERALD

    set_notes(s4, "Trạng thái bàn cờ được trừu tượng hóa thành vector 4 chiều cực kỳ tinh gọn: f1 là tổng chiều cao, f2 là số lỗ hổng bị che khuất, f3 là độ gồ ghề bề mặt và f4 là số hàng ăn được. Hành động là vị trí cột x và góc xoay r. Hàm thưởng sử dụng lũy thừa bậc hai cho số hàng dọn để kích thích AI ăn các combo lớn.")

    # =========================================================================
    # SLIDE 5: MẠNG NƠ-RON & DOUBLE DQN (Clean Split - 34 words total!)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_light_header(s5, "Mạng 4.5k Tham Số Triệt Tiêu Sai Số Ước Lượng", num=5)

    # Left: MLP
    add_card(s5, Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.9))
    tb5_1 = s5.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(5.0), Inches(4.3))
    tf5_1 = tb5_1.text_frame
    tf5_1.word_wrap = True

    p = tf5_1.paragraphs[0]
    p.text = "MẠNG NƠ-RON TINH GỌN"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    p_num = tf5_1.add_paragraph()
    p_num.text = "4,545"
    p_num.font.size = Pt(40)
    p_num.font.bold = True
    p_num.font.color.rgb = PRIMARY_BLUE

    p_lbl = tf5_1.add_paragraph()
    p_lbl.text = "Tham số huấn luyện (MLP 3 lớp: 4 -> 64 -> 64 -> 1)"
    p_lbl.font.size = Pt(11)
    p_lbl.font.color.rgb = TEXT_HEAD

    p_b1 = tf5_1.add_paragraph()
    p_b1.text = "• Checkpoint: Chỉ 82 KB trên đĩa.\n• Độ trễ: 5.4 ms/bước (>180 FPS trên CPU)."
    p_b1.font.size = Pt(11)
    p_b1.font.color.rgb = TEXT_BODY
    p_b1.space_before = Pt(14)

    # Right: Double Q-Learning
    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9))
    tb5_2 = s5.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.0), Inches(4.3))
    tf5_2 = tb5_2.text_frame
    tf5_2.word_wrap = True

    p = tf5_2.paragraphs[0]
    p.text = "DOUBLE Q-LEARNING TARGET"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_INDIGO

    p_num2 = tf5_2.add_paragraph()
    p_num2.text = "Target Decoupling"
    p_num2.font.size = Pt(24)
    p_num2.font.bold = True
    p_num2.font.color.rgb = TEXT_HEAD
    p_num2.space_before = Pt(8)

    p_lbl2 = tf5_2.add_paragraph()
    p_lbl2.text = "Tách biệt mạng chọn nước đi và mạng định giá trị."
    p_lbl2.font.size = Pt(11)
    p_lbl2.font.color.rgb = TEXT_BODY
    p_lbl2.space_before = Pt(4)

    p_b2 = tf5_2.add_paragraph()
    p_b2.text = "• Triệt tiêu hoàn toàn Overestimation Bias.\n• Đồng bộ mạng mục tiêu định kỳ 10 episodes."
    p_b2.font.size = Pt(11)
    p_b2.font.color.rgb = PRIMARY_INDIGO
    p_b2.space_before = Pt(14)

    set_notes(s5, "Mô hình mạng nơ-ron chỉ có 4,545 tham số, kích thước file chỉ 82 KB với độ trễ suy luận 5.4 ms. Bằng việc áp dụng Double DQN, chúng em tách biệt mạng chọn hành động Online và mạng định giá trị Target, giải quyết dứt điểm hiện tượng thổi phồng giá trị Q.")

    # =========================================================================
    # SLIDE 6: MÔ PHỎNG SIÊU TỐC (3 Badges - 28 words total!)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_light_header(s6, "Mô Phỏng Siêu Tốc Hơn 5.000 Bước Mỗi Giây Trên CPU", num=6)

    badges = [
        ("> 5,000", "STEPS / GIÂY", "Engine NumPy thuần không GPU"),
        ("< 60 MB", "BỘ NHỚ RAM", "Không rò rỉ bộ nhớ khi chạy dài"),
        ("7-Bag", "GUIDELINE CHUẨN", "Loại bỏ chuỗi gạch thiên vị")
    ]
    for idx, (b_val, b_lbl, b_sub) in enumerate(badges):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s6, cx, Inches(1.8), Inches(3.65), Inches(3.4))

        tb = s6.shapes.add_textbox(cx + Inches(0.2), Inches(2.2), Inches(3.25), Inches(2.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = b_val
        p1.font.size = Pt(36)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY_BLUE

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = b_lbl
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_HEAD
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = b_sub
        p3.font.size = Pt(10)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(4)

    # Bottom Takeaway Card
    add_card(s6, Inches(0.9), Inches(5.5), Inches(11.533), Inches(1.2))
    tb_b6 = s6.shapes.add_textbox(Inches(1.1), Inches(5.6), Inches(11.133), Inches(1.0))
    p_b6 = tb_b6.text_frame.paragraphs[0]
    p_b6.alignment = PP_ALIGN.CENTER
    p_b6.text = "⚡ Vectorized get_next_states(): Quét trước toàn bộ vị trí đặt gạch hợp lệ chỉ trong 1 bước tính ma trận."
    p_b6.font.size = Pt(12)
    p_b6.font.bold = True
    p_b6.font.color.rgb = ACCENT_EMERALD

    set_notes(s6, "Chúng em tự xây dựng môi trường Gym thuần NumPy với tốc độ vượt 5,000 bước/giây, tiêu tốn chưa đến 60 MB RAM và hỗ trợ túi gạch chuẩn 7-Bag. Hàm get_next_states() tối ưu ma trận giúp AI đánh giá toàn bộ nước đi tức thì.")

    # =========================================================================
    # SLIDE 7: KẾT QUẢ ĐỊNH LƯỢNG - BIG NUMBERS (Hero Slide - 32 words total!)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_light_header(s7, "Điểm Số Trung Bình Vượt Pierre Dellacherie 36,1%", num=7)

    big_nums = [
        ("+36.1%", "ĐIỂM SỐ VƯỢT HEURISTIC", "Đạt 23,234.0 (vs Dellacherie 17,062)", ACCENT_AMBER),
        ("1,127", "KỶ LỤC HÀNG DỌN SẠCH", "Xác lập tại Episode 1,010 tự học", ACCENT_EMERALD),
        ("16.8 phút", "THỜI GIAN HUẤN LUYỆN", "1,050 tập trên một CPU cá nhân", PRIMARY_BLUE)
    ]
    for idx, (val, lbl, sub, color) in enumerate(big_nums):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s7, cx, Inches(1.8), Inches(3.65), Inches(3.5), border=color)

        tb = s7.shapes.add_textbox(cx + Inches(0.2), Inches(2.2), Inches(3.25), Inches(2.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = val
        p1.font.size = Pt(40)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = lbl
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_HEAD
        p2.space_before = Pt(8)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = sub
        p3.font.size = Pt(10)
        p3.font.color.rgb = TEXT_BODY
        p3.space_before = Pt(4)

    # Bottom Hero Takeaway
    add_card(s7, Inches(0.9), Inches(5.6), Inches(11.533), Inches(1.1), border=ACCENT_AMBER)
    tb_b7 = s7.shapes.add_textbox(Inches(1.1), Inches(5.7), Inches(11.133), Inches(0.9))
    p_b7 = tb_b7.text_frame.paragraphs[0]
    p_b7.alignment = PP_ALIGN.CENTER
    p_b7.text = "🏆 Đột phá chiến thuật: Mạng nơ-ron chủ động xếp phẳng bàn cờ để chờ ăn combo lớn (Triple, Tetris) thay vì ăn lẻ tẻ."
    p_b7.font.size = Pt(12)
    p_b7.font.bold = True
    p_b7.font.color.rgb = ACCENT_AMBER

    set_notes(s7, "Đây là slide kết quả đột phá nhất của đề tài: Điểm số trung bình của mô hình đạt 23,234 điểm, chính thức vượt thuật toán chuyên gia Dellacherie 36.1%. Kỷ lục dọn hàng thực tế đạt 1,127 hàng trong một ván. Toàn bộ quá trình hội tụ chỉ mất 16.8 phút trên 1 CPU cá nhân.")

    # =========================================================================
    # SLIDE 8: TIẾN TRÌNH HỌC TẬP (70% Image Area - 1 Takeaway - 18 words total!)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_light_header(s8, "Chính Sách Tự Động Đột Phá Sau 700 Tập Huấn Luyện", num=8)

    img_miles = r"C:\Users\Khang\Desktop\Mon_REL\project\reports\figures\checkpoint_milestones_progression.png"
    if os.path.exists(img_miles):
        add_card(s8, Inches(0.9), Inches(1.8), Inches(11.533), Inches(4.3))
        s8.shapes.add_picture(img_miles, Inches(1.1), Inches(1.95), width=Inches(11.133))

    # Single Takeaway Banner at Bottom
    add_card(s8, Inches(0.9), Inches(6.25), Inches(11.533), Inches(0.75))
    tb_b8 = s8.shapes.add_textbox(Inches(1.1), Inches(6.3), Inches(11.133), Inches(0.65))
    p_b8 = tb_b8.text_frame.paragraphs[0]
    p_b8.alignment = PP_ALIGN.CENTER
    p_b8.text = "Diễn tiến: Ep 100 tránh thua sớm  ->  Ep 500 san phẳng hốc kẹt  ->  Ep 1,000 làm chủ combo dọn hàng."
    p_b8.font.size = Pt(11)
    p_b8.font.bold = True
    p_b8.font.color.rgb = PRIMARY_INDIGO

    set_notes(s8, "Nhìn vào biểu đồ tiến trình mốc checkpoint: Ở 200 tập đầu, tác tử học cách hạ chiều cao để tránh thua. Từ tập 300 đến 600, AI bắt đầu triệt tiêu hốc kẹt. Sau tập 700, tác tử bùng nổ chiến thuật dọn combo và đạt đỉnh cao 1,127 hàng.")

    # =========================================================================
    # SLIDE 9: PHÂN PHỐI THỰC NGHIỆM (70% Image Area - 1 Takeaway - 16 words total!)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_light_header(s9, "Phân Phối Thực Nghiệm Khẳng Định Độ Ổn Định Vượt Trội", num=9)

    img_bench = r"C:\Users\Khang\Desktop\Mon_REL\project\reports\figures\benchmark_comparison.png"
    if os.path.exists(img_bench):
        add_card(s9, Inches(0.9), Inches(1.8), Inches(11.533), Inches(4.3))
        s9.shapes.add_picture(img_bench, Inches(1.1), Inches(2.05), width=Inches(11.133))

    # Single Takeaway Banner at Bottom
    add_card(s9, Inches(0.9), Inches(6.25), Inches(11.533), Inches(0.75))
    tb_b9 = s9.shapes.add_textbox(Inches(1.1), Inches(6.3), Inches(11.133), Inches(0.65))
    p_b9 = tb_b9.text_frame.paragraphs[0]
    p_b9.alignment = PP_ALIGN.CENTER
    p_b9.text = "Thống kê: Trung vị >220 hàng, bỏ xa Greedy (<35 hàng), chứng minh chính sách ổn định, không ăn may."
    p_b9.font.size = Pt(11)
    p_b9.font.bold = True
    p_b9.font.color.rgb = PRIMARY_BLUE

    set_notes(s9, "Biểu đồ phân phối thực nghiệm chứng minh Naive Greedy bị kẹt hoàn toàn dưới 35 hàng do bẫy lỗ hổng. Trong khi đó, P-DDQN đạt trung vị trên 220 hàng và phân vị trên tiệm cận 400 hàng, khẳng định độ ổn định vượt trội.")

    # =========================================================================
    # SLIDE 10: ĐỐI CHIẾU QUỐC TẾ (3 Strategic Pillars - 26 words total!)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_light_header(s10, "Vượt Trội Về Chi Phí Tính Toán So Với Công Trình Quốc Tế", num=10)

    intl_pillars = [
        ("Nhanh hơn 21x", "TỐC ĐỘ HỘI TỤ", "Hội tụ trong 16.8 phút vs 6h GPU Cluster của Chen (UIUC 2021)"),
        ("Chỉ 1 CPU", "CHI PHÍ PHẦN CỨNG", "Thay vì cụm GPU chạy World Models (Liu 2020, Bairaktaris 2025)"),
        ("Vượt 36.1%", "HIỆU NĂNG ĐIỂM SỐ", "Chiến lược combo vượt thuật toán giải tích Pierre Dellacherie")
    ]
    for idx, (val, lbl, sub) in enumerate(intl_pillars):
        cx = Inches(0.9 + idx * 3.95)
        add_card(s10, cx, Inches(1.8), Inches(3.65), Inches(4.9))

        tb = s10.shapes.add_textbox(cx + Inches(0.2), Inches(2.2), Inches(3.25), Inches(4.1))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.text = val
        p1.font.size = Pt(32)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY_BLUE

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = lbl
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_HEAD
        p2.space_before = Pt(8)

        p3 = tf.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        p3.text = sub
        p3.font.size = Pt(10)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(14)

    set_notes(s10, "So với các công bố quốc tế từ 2020 đến 2025: Mô hình hội tụ nhanh hơn 21 lần so với cụm GPU của UIUC, chỉ chạy trên một CPU cá nhân thay vì cụm GPU đắt đỏ, và đạt điểm số vượt trội so với Heuristic chuyên gia.")

    # =========================================================================
    # SLIDE 11: DEMO TRỰC TIẾP (2 Action Cards with Code - 30 words total!)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_light_header(s11, "Trực Quan Hóa Thực Chiến Trên Hai Nền Tảng", num=11)

    # Mode 1: Pygame
    add_card(s11, Inches(0.9), Inches(1.8), Inches(5.6), Inches(4.9), border=PRIMARY_BLUE)
    tb11_1 = s11.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(5.0), Inches(4.3))
    tf11_1 = tb11_1.text_frame
    tf11_1.word_wrap = True

    p = tf11_1.paragraphs[0]
    p.text = "01. PYGAME AI VISUALIZER"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    p_cmd = tf11_1.add_paragraph()
    p_cmd.text = "python src/play_ai.py --agent dqn --fps 30"
    p_cmd.font.size = Pt(11)
    p_cmd.font.bold = True
    p_cmd.font.color.rgb = TEXT_HEAD
    p_cmd.space_before = Pt(6)

    p_f1 = tf11_1.add_paragraph()
    p_f1.text = "• Giám sát 4 đặc trưng hình học thời gian thực.\n• Phím nóng đối kháng: [D] DQN vs [H] Heuristic."
    p_f1.font.size = Pt(11)
    p_f1.font.color.rgb = TEXT_BODY
    p_f1.space_before = Pt(12)

    # Mode 2: Local Web UI
    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9), border=ACCENT_AMBER)
    tb11_2 = s11.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.0), Inches(4.3))
    tf11_2 = tb11_2.text_frame
    tf11_2.word_wrap = True

    p = tf11_2.paragraphs[0]
    p.text = "02. CYBER TETRIS WEB UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    p_cmd2 = tf11_2.add_paragraph()
    p_cmd2.text = "http://localhost:8080  ->  🤖 AI AUTOPLAY"
    p_cmd2.font.size = Pt(11)
    p_cmd2.font.bold = True
    p_cmd2.font.color.rgb = TEXT_HEAD
    p_cmd2.space_before = Pt(6)

    p_f2 = tf11_2.add_paragraph()
    p_f2.text = "• Chuẩn Guideline: 7-Bag, Hold, 3 Next, Ghost.\n• Âm thanh Web Audio API & hiệu ứng nổ Neon."
    p_f2.font.size = Pt(11)
    p_f2.font.color.rgb = TEXT_BODY
    p_f2.space_before = Pt(12)

    set_notes(s11, "Hệ thống đã sẵn sàng demo trực tiếp ở 2 chế độ: Chế độ 1 là Pygame Visualizer theo dõi 4 đặc trưng và đối đầu DQN với Heuristic bằng phím nóng. Chế độ 2 là Web Cyber Tetris với AI Autoplay chạy mượt mà trên trình duyệt.")

    # =========================================================================
    # SLIDE 12: KẾT LUẬN & ĐỊNH HƯỚNG (Executive Dark Closing - 28 words total!)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    fill_bg(s12, BG_DARK)

    # Box Left: Done
    c12_1 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.2), Inches(5.6), Inches(4.6))
    c12_1.fill.solid()
    c12_1.fill.fore_color.rgb = CARD_DARK
    c12_1.line.color.rgb = ACCENT_EMERALD
    c12_1.line.width = Pt(1.2)

    tb12_1 = s12.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(5.0), Inches(4.0))
    tf12_1 = tb12_1.text_frame
    tf12_1.word_wrap = True

    p = tf12_1.paragraphs[0]
    p.text = "ĐÃ HOÀN TẤT 50%"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_EMERALD

    p_d = tf12_1.add_paragraph()
    p_d.text = "• Mô hình hóa MDP & Gym siêu tốc (>5,000 steps/s).\n• P-DDQN hội tụ: Điểm số vượt Heuristic 36.1%.\n• Bản thảo bài báo khoa học Springer LNCS."
    p_d.font.size = Pt(11)
    p_d.font.color.rgb = RGBColor(241, 245, 249)
    p_d.space_before = Pt(10)

    # Box Right: Next
    c12_2 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.2), Inches(5.6), Inches(4.6))
    c12_2.fill.solid()
    c12_2.fill.fore_color.rgb = CARD_DARK
    c12_2.line.color.rgb = ACCENT_CYAN
    c12_2.line.width = Pt(1.2)

    tb12_2 = s12.shapes.add_textbox(Inches(7.1), Inches(1.5), Inches(5.0), Inches(4.0))
    tf12_2 = tb12_2.text_frame
    tf12_2.word_wrap = True

    p = tf12_2.paragraphs[0]
    p.text = "LỘ TRÌNH GIAI ĐOẠN 2"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p_n = tf12_2.add_paragraph()
    p_n.text = "• Thử nghiệm Dueling DDQN & Prioritized Replay.\n• Tích hợp nhìn trước khối kế tiếp (Next Piece).\n• Chuyển giao sang bài toán xếp hàng 2D Bin Packing."
    p_n.font.size = Pt(11)
    p_n.font.color.rgb = RGBColor(241, 245, 249)
    p_n.space_before = Pt(10)

    # Bottom Thank You
    tb_ty = s12.shapes.add_textbox(Inches(0.9), Inches(6.1), Inches(11.533), Inches(0.8))
    p_ty = tb_ty.text_frame.paragraphs[0]
    p_ty.alignment = PP_ALIGN.CENTER
    p_ty.text = "CHÂN THÀNH CẢM ƠN THẦY/CÔ VÀ CÁC BẠN! • Q&A DEFENSE"
    p_ty.font.size = Pt(13)
    p_ty.font.bold = True
    p_ty.font.color.rgb = ACCENT_CYAN

    set_notes(s12, "Tóm lại, đề tài đã hoàn tất xuất sắc 50% tiến độ nghiên cứu, chứng minh mô hình P-DDQN giải quyết trọn vẹn bài toán sample efficiency trên Tetris. Ở giai đoạn hai, nhóm sẽ thử nghiệm Dueling DDQN và hướng tới bài toán đóng gói 2D trong Logistics. Em xin chân thành cảm ơn Thầy/Cô đã chú ý lắng nghe!")

    # Save presentation
    try:
        prs.save(output_path)
        print(f"Successfully generated radical executive deck at: {output_path}")
    except PermissionError:
        alt_path = output_path.replace(".pptx", "_v2.pptx")
        prs.save(alt_path)
        print(f"File locked. Successfully generated radical executive deck at: {alt_path}")

if __name__ == "__main__":
    out_file = r"C:\Users\Khang\Desktop\Mon_REL\project\SLIDE_THUYET_TRINH_BAO_CAO_TIEN_DO.pptx"
    build_minimal_executive_deck(out_file)
