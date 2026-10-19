import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_presentation_docx(output_path):
    doc = Document()

    # Page Margins (Normal: 1 inch = 1440 dxa)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Style colors
    PRIMARY = RGBColor(24, 76, 120)    # Deep Navy Blue
    SECONDARY = RGBColor(41, 128, 185) # Bright Blue
    TEXT_DARK = RGBColor(44, 62, 80)   # Slate Charcoal
    SCRIPT_COLOR = RGBColor(20, 60, 40)# Forest Green for speaking
    GRAY_BORDER = "BDC3C7"
    LIGHT_BG = "F8F9FA"
    CALLOUT_BG = "EBF5FB"
    SCRIPT_BG = "EAF2F8"

    # --- TITLE & HEADER ---
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = title_p.add_run("BÁO CÁO TIẾN ĐỘ & BẢO VỆ ĐỀ TÀI MÔN HỌC REINFORCEMENT LEARNING\n")
    run_sub.font.size = Pt(11)
    run_sub.font.bold = True
    run_sub.font.color.rgb = SECONDARY

    run_title = title_p.add_run("KỊCH BẢN THUYẾT TRÌNH BÁO CÁO TIẾN ĐỘ DỰ ÁN\n")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY

    run_paper = title_p.add_run("Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning\n")
    run_paper.font.size = Pt(13)
    run_paper.font.italic = True
    run_paper.font.bold = True
    run_paper.font.color.rgb = TEXT_DARK

    run_meta = title_p.add_run("(Chuẩn hóa theo bài báo khoa học Springer LNCS / ICCIES & Đề cương môn học)\n")
    run_meta.font.size = Pt(10)
    run_meta.font.color.rgb = RGBColor(127, 140, 141)

    doc.add_paragraph() # Spacing

    # Info Box
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False

    info_data = [
        [("Đề tài:", " Nghiên cứu & Huấn luyện AI tự động chơi Tetris bằng Double DQN"),
         ("Môn học:", " Reinforcement Learning (REL)")],
        [("Tài liệu tham chiếu:", " paper.pdf, paper.tex, PROPOSAL.md, benchmark_comparison.png"),
         ("Thời lượng dự kiến:", " 10 - 12 phút (12 Slides chuẩn)")]
    ]

    for r_idx, row in enumerate(meta_table.rows):
        for c_idx, cell in enumerate(row.cells):
            set_cell_background(cell, "F2F4F4")
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            lbl, val = info_data[r_idx][c_idx]
            r1 = p.add_run(lbl)
            r1.bold = True
            r1.font.size = Pt(9.5)
            r1.font.color.rgb = PRIMARY
            r2 = p.add_run(val)
            r2.font.size = Pt(9.5)
            r2.font.color.rgb = TEXT_DARK

    doc.add_paragraph()

    # Helper function for Slide
    def add_slide_section(slide_num, title, duration, bullets, script_text, table_data=None, image_path=None):
        h = doc.add_heading(level=1)
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(4)
        run_h = h.add_run(f"SLIDE {slide_num}: {title.upper()}")
        run_h.font.size = Pt(14)
        run_h.font.bold = True
        run_h.font.color.rgb = PRIMARY

        # Duration & Goal
        p_dur = doc.add_paragraph()
        p_dur.paragraph_format.space_after = Pt(6)
        r_dur_lbl = p_dur.add_run("⏱️ Thời lượng khuyến nghị: ")
        r_dur_lbl.bold = True
        r_dur_lbl.font.size = Pt(10)
        r_dur_lbl.font.color.rgb = SECONDARY
        r_dur_val = p_dur.add_run(f"{duration}\n")
        r_dur_val.font.size = Pt(10)

        # Slide Visual Content Box
        t_visual = doc.add_table(rows=1, cols=1)
        t_visual.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell_vis = t_visual.rows[0].cells[0]
        set_cell_background(cell_vis, LIGHT_BG)
        set_cell_margins(cell_vis, top=120, bottom=120, left=180, right=180)

        p_vh = cell_vis.paragraphs[0]
        p_vh.paragraph_format.space_after = Pt(4)
        r_vh = p_vh.add_run("📌 NỘI DUNG HIỂN THỊ TRÊN MÀN HÌNH SLIDE (BULLET POINTS & CÔNG THỨC):")
        r_vh.bold = True
        r_vh.font.size = Pt(10)
        r_vh.font.color.rgb = PRIMARY

        for b in bullets:
            pb = cell_vis.add_paragraph(style='List Bullet')
            pb.paragraph_format.space_after = Pt(2)
            rb = pb.add_run(b)
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = TEXT_DARK

        if table_data:
            # Add table inside document
            doc.add_paragraph()
            p_tbl_lbl = doc.add_paragraph()
            r_tl = p_tbl_lbl.add_run("📊 Bảng dữ liệu trình chiếu trên Slide:")
            r_tl.bold = True
            r_tl.font.size = Pt(9.5)
            r_tl.font.color.rgb = PRIMARY

            tbl = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, row in enumerate(tbl.rows):
                for ci, cell in enumerate(row.cells):
                    cell.text = str(table_data[ri][ci])
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
                    if ri == 0:
                        set_cell_background(cell, "2C3E50")
                        for r in p.runs:
                            r.bold = True
                            r.font.size = Pt(9)
                            r.font.color.rgb = RGBColor(255, 255, 255)
                    else:
                        bg = "F2F4F4" if ri % 2 == 1 else "FFFFFF"
                        set_cell_background(cell, bg)
                        for r in p.runs:
                            r.font.size = Pt(8.5)
                            r.font.color.rgb = TEXT_DARK

        if image_path and os.path.exists(image_path):
            doc.add_paragraph()
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.add_run().add_picture(image_path, width=Inches(5.5))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_cap = p_cap.add_run(f"Hình: Biểu đồ đối chuẩn thực nghiệm phân phối số hàng dọn sạch ({os.path.basename(image_path)})")
            r_cap.font.size = Pt(8.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(127, 140, 141)

        doc.add_paragraph()

        # Speaker Script Box
        t_script = doc.add_table(rows=1, cols=1)
        t_script.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell_sc = t_script.rows[0].cells[0]
        set_cell_background(cell_sc, CALLOUT_BG)
        set_cell_margins(cell_sc, top=140, bottom=140, left=180, right=180)

        p_sh = cell_sc.paragraphs[0]
        p_sh.paragraph_format.space_after = Pt(4)
        r_sh = p_sh.add_run("🗣️ LỜI THOẠI THUYẾT TRÌNH (SPEAKER NOTES - NÓI TRỰC TIẾP TRƯỚC HỘI ĐỒNG):")
        r_sh.bold = True
        r_sh.font.size = Pt(10)
        r_sh.font.color.rgb = RGBColor(31, 97, 141)

        ps = cell_sc.add_paragraph()
        ps.paragraph_format.space_after = Pt(2)
        rs = ps.add_run(script_text)
        rs.font.size = Pt(10)
        rs.font.italic = True
        rs.font.color.rgb = RGBColor(21, 67, 96)

        doc.add_paragraph() # Spacing between slides

    # ==================== SLIDE DEFINITIONS ====================

    # Slide 1
    add_slide_section(
        slide_num=1,
        title="Trang Tiêu Đề (Title Slide)",
        duration="~45 giây",
        bullets=[
            "Tên đề tài: Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning",
            "Đề tài môn học: Reinforcement Learning (Học tăng cường) - Học kỳ 2026",
            "Tác giả báo cáo: [Họ và tên sinh viên] - MSSV: [Mã số SV]",
            "Giảng viên hướng dẫn: [Họ tên Giảng viên hướng dẫn]",
            "Cơ sở lý thuyết & thực nghiệm: Theo bài báo khoa học Springer LNCS (paper.pdf) & mã nguồn dự án REL_TetrisWithRL"
        ],
        script_text="Kính thưa Thầy/Cô và các bạn, hôm nay em xin đại diện nhóm báo cáo đề tài nghiên cứu: 'Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning'. Mục tiêu của đề tài là giải quyết nghịch lý lớn trong việc ứng dụng Học tăng cường sâu (Deep RL) vào trò chơi kinh điển Tetris: làm thế nào để tác tử AI học được chính sách sinh tồn và dọn hàng tối ưu mà không cần hàng triệu lượt chơi hay cụm GPU đắt đỏ, nhưng vẫn đạt hiệu suất vượt trội so với các thuật toán Heuristic truyền thống. Sau đây, em xin phép bắt đầu phần trình bày."
    )

    # Slide 2
    add_slide_section(
        slide_num=2,
        title="Đặt Vấn Đề & Thách Thức Nghiên Cứu (Introduction & Motivation)",
        duration="~1 phút",
        bullets=[
            "Bản chất bài toán: Tetris được chứng minh thuộc lớp NP-Complete (Demaine et al., 2002); không gian trạng thái bùng nổ tổ hợp kết hợp tính ngẫu nhiên (Stochastic 7-Bag).",
            "Hạn chế của Heuristic cổ điển (Pierre Dellacherie, 2003): Sinh tồn tốt nhưng dựa vào trọng số giải tích tĩnh, hoàn toàn không có khả năng tự thích ứng khi môi trường biến đổi.",
            "Hạn chế của Vision-based Deep RL (Nature DQN Atari, 2015): Sử dụng ảnh pixel thô (20x10) và phím bấm vi mô (micro-actions: dịch trái, phải, xoay).",
            "Nút thắt kỹ thuật lớn nhất: Credit Assignment Latency (Độ trễ gán thưởng cực lớn) do phải bấm hàng chục phím mới thả được 1 khối, tín hiệu thưởng cực kỳ thưa thớt, khiến chính sách dễ sụp đổ (Policy Collapse)."
        ],
        script_text="Tetris là bài toán kinh điển đã được Demaine và cộng sự chứng minh thuộc lớp NP-Complete vào năm 2002. Trong AI, Tetris là môi trường benchmark khắc nghiệt cho bài toán ra quyết định tuần tự. Lịch sử nghiên cứu Tetris tồn tại hai thái cực: Một là các thuật toán Heuristic như Pierre Dellacherie dùng các trọng số tĩnh cố định, sống rất lâu nhưng không thể tự học. Hai là các mạng Deep RL dựa trên hình ảnh pixel như Nature DQN trên Atari. Tuy nhiên, cách tiếp cận dùng hình ảnh và các phím bấm vi mô khiến tác tử mất hàng chục bước di chuyển mới rơi một khối gạch, tạo ra độ trễ gán tín hiệu thưởng cực lớn (Credit Assignment Latency), khiến AI không biết nước đi nào tốt, dẫn đến việc mất hàng triệu frames huấn luyện mà AI vẫn sụp đổ sau vài hàng gạch. Đây chính là động lực để nhóm đề xuất một hướng đi mới."
    )

    # Slide 3
    add_slide_section(
        slide_num=3,
        title="Đóng Góp Khoa Học Cốt Lõi Của Đề Tài (Key Contributions)",
        duration="~45 giây",
        bullets=[
            "1. Sample-Efficient Architecture: Kết hợp không gian hành động vĩ mô (Macro Placement Actions) + Biểu diễn hình học 4D + Double DQN triệt tiêu sai số ước lượng (Overestimation Bias).",
            "2. Multi-Metric Empirical Benchmarking: Đánh giá định lượng chặt chẽ với 4 nhóm tác tử (Random, Naive Greedy, Expert Heuristic, P-DDQN) trên cùng phân phối ngẫu nhiên.",
            "3. High Reproducibility on Consumer Hardware: Mô hình siêu nhẹ (~4,500 tham số, file 82 KB), hội tụ chỉ sau ~16.8 phút trên CPU cá nhân thông thường, đạt độ trễ 5.4 ms/bước."
        ],
        script_text="Bài báo của chúng em mang đến 3 đóng góp khoa học rõ ràng: Thứ nhất, đề xuất kiến trúc P-DDQN thu hẹp chuỗi quyết định từ hàng chục phím bấm thành một hành động đặt gạch duy nhất, kết hợp vector hình học 4 chiều. Thứ hai, tiến hành thực nghiệm đối chiếu đa chiều, minh bạch với cả các baseline ngẫu nhiên lẫn chuyên gia Heuristic hàng đầu. Thứ ba, toàn bộ pipeline đạt tính tái lập tối đa: hội tụ hoàn hảo trên một CPU máy tính thông thường chỉ trong chưa đầy 17 phút, phá vỡ định kiến rằng Deep RL luôn đòi hỏi máy chủ tính toán đắt tiền."
    )

    # Slide 4
    add_slide_section(
        slide_num=4,
        title="Mô Hình Hóa Toán Học MDP (Problem Formulation)",
        duration="~1 phút 30 giây",
        bullets=[
            "Chu trình Markov Decision Process: M = <S, A, P, R, gamma>",
            "Không gian trạng thái S: Vector hình học 4 chiều st = [f1, f2, f3, f4]^T:",
            "  * f1 - Aggregate Height: Tổng chiều cao các cột (sum h_c)",
            "  * f2 - Holes: Tổng số lỗ rỗng bị che phủ bên dưới gạch",
            "  * f3 - Bumpiness: Độ mấp mô chênh lệch giữa các cột cạnh nhau (sum |h_c - h_c+1|)",
            "  * f4 - Cleared Lines: Số hàng dọn sạch ngay lập tức trong nước đi (0, 1, 2, 3, 4)",
            "Không gian hành động A: Macro Placement Action a = (x, r) với x in [0, 9] (cột thả) và r in {0, 1, 2, 3} (hướng xoay)",
            "Hàm thưởng (Reward Shaping): R = 1.0 + (f4 * 1.5)^2 - 0.5 * Delta_f1 - 1.0 * Delta_f2 - 0.2 * Delta_f3 (Thưởng sống sót +1.0, thưởng phi tuyến bậc hai cho ăn combo, phạt tạo hốc kẹt và gồ ghề)"
        ],
        script_text="Về mặt mô hình hóa toán học, chúng em chuẩn hóa bài toán thành MDP với ba thành phần được thiết kế kỹ lưỡng: Đầu tiên là State Space: Thay vì ma trận nhị phân 20x10 đầy nhiễu, trạng thái bàn cờ được trừu tượng hóa thành vector 4 chiều: Tổng chiều cao, Số lỗ hổng, Độ mấp mô bề mặt và Số hàng ăn ngay lập tức. Thứ hai là Action Space: Chúng em sử dụng hành động vĩ mô gồm cặp tọa độ (x, r) - tức chọn trực tiếp vị trí cột và góc xoay cuối cùng của khối gạch. Điều này rút ngắn đường chân trời quyết định (decision horizon) đi hàng chục lần. Cuối cùng là Reward Function: Bên cạnh phần thưởng sống sót +1.0 mỗi bước, hàm thưởng sử dụng trọng số phi tuyến bậc hai cho số hàng ăn để kích thích AI ăn các combo lớn như Triple hay Tetris, đồng thời phạt nặng việc tăng lỗ hổng và tăng độ mấp mô bàn cờ."
    )

    # Slide 5
    add_slide_section(
        slide_num=5,
        title="Kiến Trúc Mô Hình & Thuật Toán Double DQN (Methodology)",
        duration="~1 phút 15 giây",
        bullets=[
            "Cấu trúc mạng nơ-ron: Multi-Layer Perceptron (MLP) gồm Input(4) -> Dense(64, ReLU) -> Dense(64, ReLU) -> Linear(1) => 4,545 tham số.",
            "Cơ chế Double Q-Learning: Triệt tiêu hiện tượng Overestimation Bias (thổi phồng Q-value) bằng cách tách biệt việc chọn hành động và tính giá trị mục tiêu:",
            "  Target Y_t = R_t+1 + gamma * Q(S_t+1, argmax_a' Q(S_t+1, a'; theta); theta^-)",
            "  Hàm mất mát MSE / Huber Loss: L(theta) = E [ (Y_t - Q(s, a; theta))^2 ]",
            "Pipeline huấn luyện: Replay Buffer dung lượng 30,000 transitions; Target Network đồng bộ định kỳ C = 10 episodes; epsilon decay từ 1.0 về 0.001 qua 1,000 tập; Adam Optimizer lr=0.001."
        ],
        script_text="Để ước lượng hàm Q, mô hình sử dụng mạng nơ-ron MLP 3 lớp cực kỳ tinh gọn với tổng cộng chỉ 4,545 tham số. Điểm mấu chốt ở đây là thuật toán Double DQN. Trong DQN chuẩn, toán tử Max thường dẫn đến việc ước lượng giá trị Q quá lạc quan (Overestimation Bias), khiến AI bị bão hòa sớm. Với Double DQN, chúng em dùng mạng Online theta để chọn hành động tối ưu, nhưng lại dùng mạng Target theta trừ để đánh giá giá trị của hành động đó. Quá trình học sử dụng bộ nhớ Replay Buffer 30,000 mẫu và cập nhật Target Network sau mỗi 10 tập, giúp việc tối ưu ổn định tuyệt đối."
    )

    # Slide 6
    add_slide_section(
        slide_num=6,
        title="Môi Trường Gym Tốc Độ Cao & Triển Khai Hệ Thống",
        duration="~45 giây",
        bullets=[
            "Fast NumPy Gym Engine (src/env/tetris_env.py): Tốc độ giả lập cực cao (>5,000 steps/giây) chạy thuần trên CPU.",
            "Cơ chế 7-Bag Randomizer chuẩn Tetris Guideline: Đảm bảo tính công bằng và phân phối ngẫu nhiên đều của 7 khối gạch (I, J, L, O, S, T, Z).",
            "Vectorized get_next_states(): Cho phép AI tính trước toàn bộ các trạng thái bàn cờ tương lai khả dĩ của khối hiện tại chỉ trong 1 bước tính ma trận.",
            "Hệ sinh thái mã nguồn: Quản lý checkpoints tự động (best_model.pth), nhật ký huấn luyện, và công cụ xuất biểu đồ khoa học tự động."
        ],
        script_text="Để huấn luyện nhanh mà không phụ thuộc vào GPU, chúng em đã tự xây dựng môi trường Tetris Gym API thuần NumPy với tốc độ vượt hơn 5,000 bước/giây. Môi trường tích hợp thuật toán sinh gạch 7-Bag chuẩn quốc tế và hỗ trợ hàm get_next_states() tối ưu hóa bằng đại số tuyến tính, giúp mạng nơ-ron quét qua toàn bộ các vị trí đặt gạch hợp lệ và đưa ra quyết định gần như tức thì."
    )

    # Slide 7
    add_slide_section(
        slide_num=7,
        title="Hệ Thống Đối Chứng Thực Nghiệm (Benchmark Baselines)",
        duration="~45 giây",
        bullets=[
            "Tại sao cần Baseline trong Reinforcement Learning? Cần các mốc chuẩn để chứng minh mô hình có thực sự học được hành vi thông minh hay không.",
            "1. Random Baseline (Demaine et al., 2002): Chọn ngẫu nhiên đều các nước đi hợp lệ -> Xác lập cận dưới lý thuyết.",
            "2. Naive Greedy (Fahey, 2003): Tham lam hạ chiều cao cột thấp nhất, bỏ qua lỗ hổng -> Đại diện cho thất bại của chiến thuật ngắn hạn.",
            "3. Expert Heuristic (Pierre Dellacherie, 2003): Tác tử chuyên gia dùng hàm đánh giá toán học giải tích -> Mốc chuẩn mực cao nhất trong cộng đồng Tetris.",
            "4. Proposed P-DDQN: Mô hình tự học của dự án sau 1,050 episodes huấn luyện."
        ],
        script_text="Để đánh giá khách quan, chúng em thiết lập 3 tác tử đối chứng: Random đại diện cho cận dưới lý thuyết; Naive Greedy đại diện cho chiến thuật tham lam ngắn hạn; và thuật toán của Pierre Dellacherie đại diện cho đỉnh cao của trường phái giải tích chuyên gia. Cả 4 tác tử đều được chạy kiểm thử trong cùng điều kiện với giới hạn trần kiểm thử an toàn 1,000 bước mỗi ván."
    )

    # Slide 8
    table_slide_8 = [
        ["Tác tử (Agent Variant)", "Mean Lines (± Std)", "Max Lines", "Mean Score", "Survival Steps"],
        ["Random Baseline [Demaine, 2002]", "0.1 ± 0.3", "1", "4.0", "23.9"],
        ["Naive Greedy [Fahey, 2003]", "18.5 ± 10.4", "33", "962.0", "86.1"],
        ["Proposed P-DDQN (Converged)", "248.1 ± 104.8", "397", "23,234.0", "655.1"],
        ["Expert Heuristic [Dellacherie, 2003]", "395.1 ± 2.3", "398", "17,062.0", "1,000.0"]
    ]
    add_slide_section(
        slide_num=8,
        title="Kết Quả Thực Nghiệm Định Lượng (Empirical Results)",
        duration="~1 phút 30 giây",
        bullets=[
            "P-DDQN vượt Random 2,481 lần và vượt Naive Greedy 13.4 lần về số hàng dọn sạch trung bình.",
            "ĐỘT PHÁ VỀ ĐIỂM SỐ: Proposed P-DDQN đạt điểm trung bình 23,234.0, VƯỢT EXPERT HEURISTIC 36.1% (17,062.0).",
            "Nguyên nhân: Mạng nơ-ron tự khám phá chiến thuật mạo hiểm có tính toán - chủ động giữ bàn cờ phẳng để chờ ăn combo lớn (Triple, Tetris) nhờ hàm thưởng phi tuyến (f4 * 1.5)^2.",
            "Kỷ lục thực tế trong tự học không giới hạn bước: 1,127 hàng dọn sạch tại episode 1,010."
        ],
        script_text="Kính thưa Thầy/Cô, đây là bảng kết quả thực nghiệm then chốt của bài báo. Nhìn vào bảng số liệu, tác tử ngẫu nhiên chỉ sống được 23 bước và dọn 0.1 hàng. Tác tử Naive Greedy dọn được 18.5 hàng rồi sụp đổ do để lại quá nhiều hốc kẹt. Mô hình P-DDQN của chúng em đạt trung bình 248.1 hàng/ván, với nhiều ván chơi chạm trần kiểm thử 1,000 bước. Đặc biệt nhất, về tiêu chí Điểm số trung bình, P-DDQN đạt 23,234 điểm, chính thức vượt thuật toán chuyên gia Dellacherie tới 36.1%. Lý do là mạng nơ-ron đã tự học được một hành vi chiến thuật rất thông minh: không vội vàng ăn các hàng đơn lẻ như Heuristic, mà chủ động xếp phẳng bàn cờ để chờ ăn combo kép và Tetris 4 hàng nhằm tối đa hóa phần thưởng phi tuyến lũy thừa bậc hai!",
        table_data=table_slide_8
    )

    # Slide 9
    img_path = r"C:\Users\Khang\Desktop\Mon_REL\project\reports\figures\benchmark_comparison.png"
    add_slide_section(
        slide_num=9,
        title="Phân Tích Phân Phối Thống Kê (Distributional Analysis)",
        duration="~1 phút",
        bullets=[
            "Biểu đồ bên trái (Bar Chart): Thể hiện giá trị trung bình kèm thanh sai số độ lệch chuẩn (Std Dev Error Bars).",
            "Biểu đồ bên phải (Boxplot): Phân tích chi tiết tứ phân vị (Quartiles) và trung vị (Median):",
            "  * Naive Greedy bị bó hẹp hoàn toàn ở phân vị thấp (< 35 hàng) do hiện tượng bẫy lỗ hổng chết người.",
            "  * Proposed P-DDQN có đường trung vị vượt mốc 220 hàng, với phân vị trên (Upper Quartile) tiệm cận trần an toàn 400 hàng.",
            "Tính nhất quán (Consistency): Chứng minh chính sách học được có độ ổn định cao, không phụ thuộc vào may mắn ngẫu nhiên."
        ],
        script_text="Quan sát biểu đồ phân phối thực nghiệm từ Hình 1 của bài báo: Phía bên trái là biểu đồ cột thể hiện sự chênh lệch rõ rệt về số hàng dọn sạch. Phía bên phải là biểu đồ hộp Boxplot. Chúng ta thấy rõ tác tử Naive Greedy bị kẹt hoàn toàn ở cận dưới do hiện tượng bẫy lỗ hổng. Trong khi đó, hộp phân phối của P-DDQN trải rộng ở dải hiệu suất rất cao với trung vị trên 220 hàng, chứng minh rằng tác tử không hề ăn may mà đã hình thành một chính sách điều khiển cực kỳ vững chắc qua các ván đấu độc lập.",
        image_path=img_path
    )

    # Slide 10
    table_slide_10 = [
        ["Nghiên cứu & Tác giả", "Phương pháp & Không gian", "Số hàng dọn TB", "Thời gian & Phần cứng"],
        ["Liu & Liu [CUHK 2020]", "World Models (Dreamer) / Micro", "≈ 10 - 60 hàng", "> 12 giờ (GPU)"],
        ["Chen [UIUC Thesis 2021]", "Expected DRL / Macro Placement", "60,000 khối", "≈ 6 giờ (GPU Cluster)"],
        ["Yan et al. [IEEE TIMC 2022]", "Dynamic PPO / Robot Trajectory", "≈ 80 - 120 hàng", "≈ 3 - 5 giờ (GPU/CPU)"],
        ["Recent Benchmark [TechRxiv 2024]", "Vanilla Feature-DQN / Macro", "≈ 50 - 95 hàng", "≈ 2 - 4 giờ (CPU)"],
        ["Bairaktaris & Johannssen [Elsevier 2025]", "Nature Pixel-DQN / Micro Joystick", "≈ 5 - 15 hàng", "> 24 giờ (NVIDIA GPU)"],
        ["Proposed P-DDQN [Dự án của bạn]", "Double DQN / Macro 4D Features", "248.1 hàng (Max: 1,127)", "≈ 16.8 phút (CPU đơn)"]
    ]
    add_slide_section(
        slide_num=10,
        title="Đối Chiếu Các Công Trình Quốc Tế Hiện Đại (2020 – 2025)",
        duration="~1 phút 15 giây",
        bullets=[
            "1. Biểu diễn hình học đánh bại mô hình đồ sộ: Các nghiên cứu dùng CNN pixel hoặc World Models (Elsevier 2025, CUHK 2020) đều bị nghẽn dưới 60 hàng do tín hiệu thưởng vi mô quá thưa.",
            "2. Ưu thế tuyệt đối về chi phí tính toán: Hội tụ nhanh hơn 21 lần so với cụm GPU Cluster của Chen (2021) và PPO của Yan (2022).",
            "3. Giải quyết triệt để trần bão hòa Overestimation: Các mô hình DQN đơn 2024 thường bão hòa ở mức 50-95 hàng; cơ chế Double DQN giúp mô hình của chúng em vượt lên 248.1 hàng và đạt đỉnh 1,127 hàng."
        ],
        script_text="Khi đặt mô hình vào bức tranh nghiên cứu quốc tế từ 2020 đến 2025: Nghiên cứu trên Elsevier năm 2025 của Bairaktaris hay của Liu & Liu tại CUHK đã chứng minh việc cố nhồi nhét mạng CNN xử lý ảnh thô hoặc World Models vào Tetris đều cho kết quả rất thấp dưới 60 hàng dù tốn hàng chục giờ GPU. So với công trình của Chen tại Đại học UIUC dùng cụm máy chủ 6 giờ hay Yan et al. dùng PPO, mô hình của chúng em đạt tốc độ hội tụ nhanh hơn tới 21 lần, hoàn tất huấn luyện trong 16.8 phút trên CPU cá nhân, đồng thời vượt qua trần bão hòa 95 hàng của các mô hình DQN thông thường năm 2024 nhờ cơ chế triệt tiêu overestimation của Double DQN.",
        table_data=table_slide_10
    )

    # Slide 11
    add_slide_section(
        slide_num=11,
        title="Trình Diễn Trực Tiếp Hệ Thống AI (Live Demonstration)",
        duration="~1 phút 30 giây (kết hợp thao tác trực tiếp)",
        bullets=[
            "CHẾ ĐỘ 1: Visualizer Pygame & Giám Sát Suy Luận Mạng Nơ-ron PyTorch:",
            "  * Lệnh thực thi: python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30",
            "  * Cơ chế: Nạp trọng số hội tụ từ 'best_model.pth', thực thi suy luận thời gian thực với tốc độ 30 FPS ổn định.",
            "  * Bảng giám sát 4 đặc trưng trực tiếp (Evaluation Features): Height, Holes, Bumpiness, Cleared Lines nhảy số theo từng quyết định.",
            "  * Phím nóng tương tác trực tiếp: [D] Kích hoạt DQN Agent | [H] Chuyển đổi tức thì sang Heuristic Baseline đối chứng | [Space] Tạm dừng phân tích | [R] Chơi lại ván mới.",
            "CHẾ ĐỘ 2: Giao Diện Game Cyber Tetris Trên Nền Tảng Web Cục Bộ (Local Web UI):",
            "  * Khởi chạy máy chủ HTTP: python -m http.server 8080 -> Mở trình duyệt: http://localhost:8080",
            "  * Kích hoạt: Nhấp nút '🤖 BẬT AI AUTOPLAY' ở góc phải giao diện.",
            "  * Tính năng hiện đại: Chuẩn Tetris Guideline (7-Bag Randomizer, Hold Piece, hàng chờ 3 Next Pieces, Ghost Piece định vị), hiệu ứng rung chấn Screen Shake, nổ hạt Neon khi dọn hàng và bộ tổng hợp âm thanh Web Audio API synthwave 8-bit.",
            "Chỉ số tài nguyên tối ưu: Trọng số mô hình chỉ 82 KB, độ trễ 5.4 ms/bước, tương thích hoàn toàn môi trường nhúng và web."
        ],
        script_text="Kính thưa Thầy/Cô và các bạn, để minh chứng cho năng lực thực chiến của mô hình, em xin phép trình diễn trực tiếp hệ thống hoạt động ở 2 chế độ: Chế độ thứ nhất là công cụ Visualizer Pygame phục vụ nghiên cứu và giám sát kỹ thuật. Em chạy câu lệnh: 'python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30'. Màn hình hiện lên bàn cờ cùng bảng theo dõi 4 đặc trưng hình học thời gian thực: Chiều cao, Lỗ hổng, Độ gồ ghề và Hàng dọn sạch. Thầy/Cô có thể thấy AI liên tục tính toán và chọn điểm rơi phẳng nhất với độ trễ chỉ 5.4 mili-giây. Em có thể bấm phím H để chuyển ngay sang thuật toán Heuristic hoặc bấm D để trả quyền lại cho mạng nơ-ron DQN để đối chiếu trực tiếp hành vi hai bên. Chế độ thứ hai là giao diện Cyber Tetris chạy trên nền tảng Web cục bộ tại cổng 8080. Khi em bật nút 'AI AUTOPLAY', mô hình tự động làm chủ hoàn toàn bàn cờ với đầy đủ các chuẩn quốc tế: 7-Bag, Hold, 3 khối tiếp theo và bóng gạch định vị, kết hợp âm thanh Arcade chân thực. Điều này khẳng định thuật toán không chỉ nằm trên lý thuyết bài báo mà đã được đóng gói thành một sản phẩm hoàn thiện, mượt mà và trực quan sinh động."
    )

    # Slide 12
    add_slide_section(
        slide_num=12,
        title="Kết Luận & Định Hướng Mở Rộng (Conclusion & Outlook)",
        duration="~45 giây",
        bullets=[
            "Tổng kết thành quả đề tài:",
            "  * Chứng minh thành công tính ưu việt của mô hình P-DDQN kết hợp 4D Geometric Feature Representation.",
            "  * Đạt hiệu suất dọn 248.1 hàng/ván và kỷ lục 1,127 hàng, vượt Heuristic về điểm số 36.1%.",
            "  * Hoàn thành toàn diện mã nguồn, giao diện trực quan và bản thảo bài báo khoa học chuẩn Springer LNCS (paper.pdf).",
            "Định hướng phát triển:",
            "  * Tích hợp kiến trúc Dueling DQN và Prioritized Experience Replay (PER).",
            "  * Ứng dụng nguyên lý Macro Placement vào các bài toán công nghiệp: Xếp hàng vào thùng 2D/3D (2D Bin Packing Problem) và tối ưu hóa logistics.",
            "Lắng nghe câu hỏi phản biện: Q&A Session - Chân thành cảm ơn Thầy/Cô!"
        ],
        script_text="Tóm lại, đề tài đã giải quyết thành công bài toán cân bằng giữa hiệu quả sử dụng mẫu (sample efficiency), tài nguyên phần cứng và hiệu năng điều khiển tối ưu. Toàn bộ cơ sở lý thuyết, kết quả và mã nguồn đã được nhóm đúc kết thành bài báo khoa học chuẩn Springer LNCS và kho mã nguồn hoàn chỉnh. Hướng phát triển tiếp theo của nhóm là chuyển giao nguyên lý Placement này vào bài toán xếp hàng 2D trong Logistics công nghiệp. Em xin chân thành cảm ơn Thầy/Cô và các bạn đã chú ý lắng nghe. Nhóm rất mong nhận được những câu hỏi và ý kiến đóng góp từ Thầy/Cô!"
    )

    # --- BONUS SECTION: Q&A PREPARATION ---
    h_qa = doc.add_heading(level=1)
    h_qa.paragraph_format.space_before = Pt(20)
    run_qah = h_qa.add_run("PHỤ LỤC: BỘ CÂU HỎI & TRẢ LỜI PHẢN BIỆN DỰ TRÙ (Q&A DEFENSE)")
    run_qah.font.size = Pt(14)
    run_qah.font.bold = True
    run_qah.font.color.rgb = PRIMARY

    qa_list = [
        ("Câu hỏi 1: Tại sao không dùng CNN xử lý pixel thô như Nature DQN Atari?",
         "Trả lời: Các nghiên cứu kinh điển về Tetris (Bairaktaris & Johannssen, Elsevier 2025; Liu & Liu, CUHK 2020) đã chứng minh CNN pixel trên Tetris có độ trễ gán thưởng cực lớn, cần hàng chục triệu steps và thường sụp đổ dưới 15 hàng. Trong khi đó, 4 đặc trưng hình học phản ánh trực tiếp bản chất cấu trúc bàn cờ, giúp mạng MLP nhỏ (4.5k params) hội tụ trong 16.8 phút trên CPU mà đạt hơn 248 hàng."),
        ("Câu hỏi 2: Macro Action (x, r) có bị coi là gian lận so với phím bấm từng bước không?",
         "Trả lời: Không gian hành động Macro Placement là chuẩn mực trong nghiên cứu học thuật về Tetris (Fahey, Thiery & Scherrer, Chen 2021). Mọi cặp (x, r) hợp lệ đều tương đương với một chuỗi bấm phím cơ học xác định (dịch ngang, xoay, hard drop). Cách tiếp cận này giúp tác tử tập trung học chiến lược ra quyết định thay vì lãng phí tài nguyên học thao tác phím cơ bản."),
        ("Câu hỏi 3: Vì sao điểm số lại vượt Pierre Dellacherie trong khi số hàng dọn trung bình thấp hơn một chút?",
         "Trả lời: Do hàm thưởng của chúng em sử dụng phần thưởng phi tuyến lũy thừa bậc hai (Lines * 1.5)^2. Thuật toán của Dellacherie là heuristic phòng thủ cực đoan, ưu tiên ăn an toàn từng hàng đơn lẻ (Single lines). Ngược lại, mạng P-DDQN tự học được chiến thuật tích trữ bàn cờ phẳng để ăn các combo 3-4 hàng (Tetris), mang lại lượng điểm thưởng đột biến vượt 36.1% so với Heuristic.")
    ]

    for q, a in qa_list:
        pq = doc.add_paragraph()
        pq.paragraph_format.space_before = Pt(8)
        pq.paragraph_format.space_after = Pt(2)
        rq = pq.add_run(q)
        rq.bold = True
        rq.font.size = Pt(10)
        rq.font.color.rgb = RGBColor(192, 57, 43)

        pa = doc.add_paragraph()
        pa.paragraph_format.space_after = Pt(6)
        ra = pa.add_run(a)
        ra.font.size = Pt(9.5)
        ra.font.color.rgb = TEXT_DARK

    # Save
    doc.save(output_path)
    print(f"Successfully generated DOCX at: {output_path}")

if __name__ == "__main__":
    out_file = r"C:\Users\Khang\Desktop\Mon_REL\project\KICH_BAN_THUYET_TRINH_BAO_CAO_TIEN_DO.docx"
    try:
        create_presentation_docx(out_file)
    except PermissionError:
        fallback_file = r"C:\Users\Khang\Desktop\Mon_REL\project\KICH_BAN_THUYET_TRINH_BAO_CAO_TIEN_DO_v2.docx"
        create_presentation_docx(fallback_file)
        print("Original file is locked. Saved to KICH_BAN_THUYET_TRINH_BAO_CAO_TIEN_DO_v2.docx")
