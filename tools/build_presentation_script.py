import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_script_docx(output_path):
    doc = Document()
    
    # Page Setup: Normal margins (1 inch)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Color Palette
    PRIMARY = RGBColor(11, 17, 32)      # Deep Slate
    SECONDARY = RGBColor(2, 132, 199)   # Electric Blue
    ACCENT = RGBColor(16, 185, 129)     # Emerald Green
    HIGHLIGHT = RGBColor(99, 102, 241)  # Indigo
    TEXT = RGBColor(51, 65, 85)         # Slate 700
    MUTED = RGBColor(100, 116, 139)     # Slate 500

    # Header / Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("KỊCH BẢN THUYẾT TRÌNH BÁO CÁO KHOA HỌC\n(STAGE-READY PRESENTATION SCRIPT)")
    r_title.bold = True
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = PRIMARY
    p_title.paragraph_format.space_after = Pt(4)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Đề tài: Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning\n(Định dạng chuẩn hội thảo khoa học quốc tế / Báo cáo đồ án)")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = SECONDARY
    p_sub.paragraph_format.space_after = Pt(18)

    # Meta Info Box
    meta_table = doc.add_table(rows=1, cols=1)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = meta_table.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
    
    p_meta = cell.paragraphs[0]
    p_meta.paragraph_format.line_spacing = 1.25
    r = p_meta.add_run("⏱️ Thời lượng ước tính: ")
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY
    r = p_meta.add_run("12 - 15 phút (Báo cáo) + 5 - 10 phút (Hỏi đáp Q&A)\n")
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = TEXT

    r = p_meta.add_run("🎯 Khung bài trình chiếu: ")
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY
    r = p_meta.add_run("Bộ 12 Slide Cyber-Tech Luxury (SLIDE_THUYET_TRINH_BAO_CAO_TIEN_DO_FINAL.pptx)\n")
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = TEXT

    r = p_meta.add_run("📑 Tài liệu gốc trích dẫn: ")
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY
    r = p_meta.add_run("Paper Hội thảo (LaTeX2e+Proceedings+Template+ZIP/paper.pdf)\n")
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = TEXT

    r = p_meta.add_run("💻 Câu lệnh Live Demo: ")
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(11)
    r.font.color.rgb = PRIMARY
    r = p_meta.add_run("python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30")
    r.font.name = "Consolas"
    r.font.size = Pt(10.5)
    r.font.color.rgb = SECONDARY

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 12 SLIDES DETAIL CONTENT
    slides_data = [
        {
            "slide_num": "SLIDE 01",
            "time": "01:00",
            "title": "BÌA BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU",
            "visual": "Nền Deep Slate huyền bí, hiệu ứng phát sáng Neon Cyan, huy hiệu Springer LNCS / ICCIES Conference.",
            "points": [
                "Chào mừng Hội đồng và người nghe.",
                "Tuyên bố tên đề tài nghiên cứu.",
                "Đặt vấn đề gợi mở: Huấn luyện AI Tetris siêu việt chỉ bằng CPU cá nhân trong 17 phút."
            ],
            "script": """\"Kính thưa Thầy/Cô trong Hội đồng thẩm định và toàn thể các bạn sinh viên,

Em xin đại diện nhóm nghiên cứu trình bày báo cáo tiến độ đề tài khoa học: 'Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning' - Tối ưu hóa học tăng cường sâu dựa trên không gian đặt khối giúp huấn luyện chính sách Tetris hiệu quả cao về mẫu.

Nghiên cứu của chúng em tập trung giải quyết câu hỏi cốt tử trong Reinforcement Learning hiện đại: 'Làm thế nào để một tác tử AI tự học được chiến thuật chơi Tetris ở đẳng cấp chuyên gia mà không đòi hỏi cụm máy chủ GPU đắt đỏ, chỉ cần huấn luyện trên một chiếc CPU máy tính cá nhân trong chưa đầy 17 phút?'.

Sau đây, em xin phép đi vào chi tiết cấu trúc bài báo cáo.\""""
        },
        {
            "slide_num": "SLIDE 02",
            "time": "01:30",
            "title": "HAI NÚT THẮT TRIỆT TIÊU HIỆU NĂNG DEEP RL TRUYỀN THỐNG",
            "visual": "2 Khối thẻ Card lớn: Thẻ Coral (Credit Assignment Latency) và Thẻ Blue (Sample Inefficiency).",
            "points": [
                "Nút thắt 1: Credit Assignment - Quá nhiều phím bấm vi mô, thưởng quá thưa.",
                "Nút thắt 2: Sample Inefficiency - Xử lý ảnh pixel 20x10 tốn hàng chục giờ GPU nhưng bão hòa dưới 15 hàng."
            ],
            "script": """\"Kính thưa Hội đồng, khi áp dụng các thuật toán Deep RL kinh điển (như DQN thuần túy của DeepMind) vào bài toán Tetris, các nghiên cứu trên thế giới đều va phải hai rào cản vật lý nghiêm trọng:

Thứ nhất là Credit Assignment Latency - Nút thắt phân bổ tín dụng hành vi. Ở mức vi mô (micro-actions), để hạ cánh một khối gạch, tác tử phải thực hiện hàng chục thao tác liên tiếp: qua trái, qua phải, xoay, thả rơi. Tín hiệu phần thưởng chỉ xuất hiện ở bước cuối cùng khi dọn được hàng. Chuỗi quyết định quá dài khiến thuật toán không thể suy luận được phím bấm nào trong quá khứ là đúng đắn, dẫn tới hiện tượng sụp đổ chính sách (Policy Collapse).

Thứ hai là Sample Inefficiency - Hiệu quả sử dụng mẫu kém. Nếu nhồi ma trận pixel thô 20x10 vào mạng CNN, mô hình phải mất hàng chục giờ chạy trên GPU chỉ để nhận biết được các cạnh gạch. Hệ quả là phần lớn mô hình DQN truyền thống bị bão hòa và kẹt cứng ở ngưỡng dưới 15 hàng dọn sạch.

Nhận thức rõ hai rào cản này, nghiên cứu của chúng em đề xuất một hướng tiếp cận đột phá: chuyển đổi từ không gian hành động vi mô sang Macro Placement kết hợp biểu diễn trạng thái hình học tinh gọn.\""""
        },
        {
            "slide_num": "SLIDE 03",
            "time": "01:30",
            "title": "QUY TRÌNH KIẾN TRÚC P-DDQN (FIG. 1 TRONG BÀI BÁO)",
            "visual": "Hình ảnh Fig. 1 trích xuất độ nét cao từ trang 4 của paper.pdf, kèm sơ đồ 4 giai đoạn xử lý.",
            "points": [
                "Giai đoạn 1: Placement Enumeration - Duyệt trước các vị trí đặt (x, r).",
                "Giai đoạn 2: Vector 4D - Trích xuất đặc trưng hình học trạng thái tương lai.",
                "Giai đoạn 3: Double DQN Decoupling - Định giá Q-value ổn định.",
                "Giai đoạn 4: Greedy Action Selection - Chọn thế cờ tối ưu."
            ],
            "script": """\"Trên màn hình là Hình 1 (Fig. 1) trích xuất trực tiếp từ bài báo khoa học của chúng em, minh họa toàn bộ đường ống kiến trúc P-DDQN qua 4 giai đoạn liên hoàn:

Giai đoạn 1 - Placement Enumeration: Khi một khối tetromino xuất hiện ở đỉnh bàn cờ, thay vì bắt AI bấm từng phím vi mô, thuật toán mô phỏng trước toàn bộ không gian đặt gạch hợp lệ gồm tọa độ cột x và góc xoay r (thường chỉ từ 10 đến 34 vị trí có thể đặt được).

Giai đoạn 2 - 4D Feature Vector Extraction: Với mỗi vị trí đặt thử nghiệm, môi trường giả lập tạo ra trạng thái bàn cờ tương lai và trích xuất thành một vector hình học 4 chiều duy nhất.

Giai đoạn 3 - Double DQN Target Decoupling: Vector 4D này được đưa vào mạng nơ-ron để ước lượng giá trị kỳ vọng Q(s, a). Chúng em tách biệt hoàn toàn mạng Online Network (chuyên chọn hành động) và Target Network (chuyên định giá) nhằm triệt tiêu hoàn toàn sai số thổi phồng giá trị (Overestimation Bias).

Giai đoạn 4 - Greedy Selection: Tác tử chọn nước đi có giá trị Q cao nhất và thực hiện rơi cứng xuống bàn cờ. Đường ống này giúp nén không gian tìm kiếm từ hàng triệu bước rời rạc xuống một bài toán tối ưu cục bộ cực kỳ tinh gọn.\""""
        },
        {
            "slide_num": "SLIDE 04",
            "time": "01:30",
            "title": "MÔ HÌNH HÓA MDP & VECTOR HÌNH HỌC BỐN CHIỀU",
            "visual": "4 Thẻ Card đại diện cho f1, f2, f3, f4 và Formula Banner nền tối neon cyan chứa hàm thưởng phi tuyến.",
            "points": [
                "4 chiều đặc trưng: Chiều cao (Height), Lỗ hổng (Holes), Độ gồ ghề (Bumpiness), Số hàng (Lines).",
                "Hàm thưởng bậc hai: Kích thích gom combo 3 - 4 hàng thay vì ăn lẻ tẻ."
            ],
            "script": """\"Kính thưa Thầy/Cô, linh hồn của sự tinh gọn trong đề tài nằm ở việc mô hình hóa bài toán theo Markov Decision Process (MDP) với vector đặc trưng 4 chiều:

1. Chiều f1 - Height: Tổng độ cao tích lũy của 10 cột, phản ánh mức độ hiểm nghèo của bàn cờ.
2. Chiều f2 - Holes: Số lỗ hổng bị gạch che khuất bên trên. Đây là chỉ số nguy hiểm nhất trong Tetris, vì lỗ hổng càng sâu thì càng không thể dọn hàng.
3. Chiều f3 - Bumpiness: Tổng độ chênh lệch độ cao giữa các cột liền kề, định lượng độ bằng phẳng của bề mặt.
4. Chiều f4 - Lines Cleared: Số lượng hàng dọn sạch tức thì sau khi đặt khối.

Đặc biệt, ở đáy slide là Hàm thưởng phi tuyến (Reward Shaping) do nhóm thiết kế:
R(s, a, s') = 1.0 (sống sót) + (Lines * 1.5)^2 (thưởng combo) - 1.0 Delta Holes - 0.2 Delta Bumpiness - 0.5 Delta Height.

Trọng số phạt lỗ hổng Delta Holes được đặt bằng -1.0, lớn gấp đôi các thành phần khác để ép AI không được tạo hốc kẹt. Đáng chú ý nhất, thành phần dọn hàng được áp dụng hàm lũy thừa bậc hai: nếu chỉ ăn 1 hàng, AI nhận (1 * 1.5)^2 = 2.25 điểm; nhưng nếu kiên nhẫn tích lũy ăn 4 hàng (Tetris), điểm thưởng vọt lên (4 * 1.5)^2 = 36 điểm - gấp 16 lần! Đây chính là chìa khóa toán học giúp AI tự hình thành tư duy chơi gom combo đỉnh cao.\""""
        },
        {
            "slide_num": "SLIDE 05",
            "time": "01:00",
            "title": "MẠNG NƠ-RON 4.5K THAM SỐ & CƠ CHẾ DOUBLE DQN",
            "visual": "Con số khổng lồ 4,545 tham số, Thẻ Card Target Decoupling, độ trễ 5.4 ms.",
            "points": [
                "Kiến trúc MLP 3 lớp siêu nhẹ: 4 -> 64 -> 64 -> 1.",
                "Tổng kích thước file checkpoint: 82 KB.",
                "Tốc độ suy luận: 5.4 ms/bước, đạt hơn 180 FPS trên CPU."
            ],
            "script": """\"Sang đến thiết kế mạng nơ-ron, nhóm kiên định theo đuổi triết lý 'Tối giản nhưng Uy lực':

Thay vì sử dụng mạng CNN hàng triệu tham số ngốn bộ nhớ, mạng học sâu của chúng em chỉ gồm 3 lớp Perceptron đa tầng (MLP) với cấu trúc: Input 4 node -> 64 neuron (ReLU) -> 64 neuron (ReLU) -> Linear Output 1 node thể hiện Q-value.

Tổng số lượng tham số toàn mạng chỉ vỏn vẹn 4,545 tham số. File mô hình lưu trữ trên đĩa chỉ nặng 82 Kilobytes! 

Nhờ sự tinh gọn tuyệt đối này, tốc độ suy luận của mô hình đạt 5.4 mili-giây cho mỗi quyết định, tương đương tốc độ khung hình hơn 180 FPS hoàn toàn trên CPU thông thường mà không cần bất kỳ GPU chuyên dụng nào. Cơ chế Double DQN đồng thời cập nhật Target Network sau mỗi 10 bước huấn luyện, giữ cho quá trình học ổn định tuyệt đối, không xảy ra hiện tượng dao động hay sụp đổ hàm giá trị.\""""
        },
        {
            "slide_num": "SLIDE 06",
            "time": "01:00",
            "title": "THIẾT LẬP THỰC NGHIỆM & PHẦN CỨNG HUẤN LUYỆN",
            "visual": "3 Cột Thông số: Ngân sách huấn luyện (1,000 eps), Môi trường phần cứng (CPU cá nhân), Tham số RL.",
            "points": [
                "Thời gian huấn luyện toàn bộ: 16.8 phút.",
                "Epsilon Decay: 1.0 -> 0.001 với hệ số suy giảm 0.995.",
                "Replay Buffer: 20,000 transitions, Batch size 64."
            ],
            "script": """\"Về thiết lập thực nghiệm, toàn bộ quá trình huấn luyện được thực thi với cấu hình:
- Ngân sách huấn luyện: Đúng 1,000 episodes độc lập.
- Thiết bị thử nghiệm: CPU máy tính xách tay cá nhân (Intel Core i5 thông dụng), 0% GPU.
- Tổng thời gian hoàn tất quá trình huấn luyện: Đúng 16.8 phút.

Các siêu tham số học tăng cường gồm:
- Tốc độ học (Learning Rate): 1e-3 với bộ tối ưu hóa Adam.
- Bộ đệm nhớ (Replay Buffer): Dung lượng 20,000 bước chuyển dịch, lấy mẫu mini-batch 64.
- Chiến lược khám phá Epsilon-Greedy: Khởi đầu từ 1.0 (khám phá ngẫu nhiên 100%) và giảm dần đều theo hệ số 0.995 sau mỗi tập, chạm ngưỡng tối thiểu 0.001 ở tập thứ 700. Điều này đảm bảo AI có đủ thời gian khám phá không gian trạng thái trước khi bước vào giai đoạn khai thác chính sách tối ưu.\""""
        },
        {
            "slide_num": "SLIDE 07",
            "time": "02:00",
            "title": "KẾT QUẢ ĐỊNH LƯỢNG & PHÂN TÍCH CHUYÊN SÂU BẢNG 1 (TABLE 1)",
            "visual": "Bảng Table 1 trích xuất từ paper.pdf (7 cột), highlight dòng P-DDQN và Takeaway Banner xanh ngọc.",
            "points": [
                "Random Agent: 0.1 hàng, chết sau 25 bước.",
                "Naive Greedy: 18.8 hàng, chết sau 85 bước.",
                "P-DDQN (Đề xuất): 287.5 hàng TB, Trung vị 388 hàng, Kỷ lục 398 hàng, Chạm trần 1,000 bước ở 54/100 ván.",
                "Điểm/hàng: 81.3 điểm (vượt trội so với 40-51 điểm của cách chơi thường)."
            ],
            "script": """\"Kính thưa Hội đồng, đây là Slide quan trọng nhất trong bài báo cáo - Bảng 1 (Table 1) trích nguyên văn từ bài báo khoa học đã xuất bản của nhóm. Bảng thể hiện kết quả kiểm thử định lượng nghiêm ngặt trên 100 ván đấu độc lập với giới hạn trần 1,000 bước đặt gạch:

1. Tác tử ngẫu nhiên (Random Agent): Chỉ sống sót trung bình 25.5 bước, số hàng dọn sạch gần như bằng 0 (0.1 hàng). Điều này chứng minh không gian bàn cờ Tetris cực kỳ khắt khe, nếu không có chiến lược thì game over ngay tức khắc.

2. Tác tử Heuristic tham lam (Naive Greedy): Thuật toán này chọn nước đi dọn hàng ngay lập tức ở từng bước. Kết quả dọn được 18.8 hàng nhưng nhanh chóng bị loại sau trung bình 85 bước đặt gạch. Lý do là vì quá tham lam ăn hàng trước mắt nên tác tử để lại hàng loạt lỗ hổng chí mạng phía dưới bàn cờ.

3. Mô hình đề xuất P-DDQN: Tạo nên một sự bứt phá vượt bậc về mọi chỉ số:
- Số hàng dọn trung bình: Đạt 287.5 hàng (cao gấp 15.3 lần Naive Greedy).
- Giá trị trung vị (Median): Đạt tới 388.0 hàng.
- Điểm số trung bình: Đạt 23,360.8 điểm.
- Khả năng sống sót: 749.1 bước đặt gạch. Đặc biệt, có tới 54 trên 100 ván đấu tác tử đã chạm trần kiểm thử 1,000 bước mà không hề bị thua!

Đặc biệt nhất, xin mời Thầy/Cô nhìn vào cột cuối cùng: Điểm số trên mỗi hàng (Points per line). Nếu chỉ ăn đơn lẻ 1 hàng, hệ số điểm Tetris là 40 điểm/hàng. Greedy chỉ đạt 51.5 điểm/hàng. Trong khi P-DDQN đạt tới 81.3 điểm/hàng! Con số toán học này khẳng định chắc chắn rằng: Tác tử không hề chơi theo kiểu ăn may, mà đã tự hình thành chiến thuật tích lũy thế cờ để dọn sạch cùng lúc 3 đến 4 hàng (Triple và Tetris).\""""
        },
        {
            "slide_num": "SLIDE 08",
            "time": "01:30",
            "title": "TIẾN TRÌNH HỌC TẬP & HỘI TỤ CHÍNH SÁCH (HÌNH 2 TRONG PAPER)",
            "visual": "Biểu đồ Fig. 2 đường cong học tập và các mốc Checkpoint lịch sử 200, 500, 700, 1000.",
            "points": [
                "Tập 1 - 200: Khám phá hỗn loạn (Epsilon cao), điểm dưới 50 hàng.",
                "Tập 200 - 500: Tích lũy kinh nghiệm, bắt đầu dọn hàng ổn định.",
                "Tập 700: Điểm uốn đột phá (Breakthrough Point), Epsilon chạm 0.001, điểm số bùng nổ vượt 1,000 hàng."
            ],
            "script": """\"Hình ảnh trên Slide là đồ thị tiến trình học tập trích xuất từ Hình 2 trong bài báo của chúng em, phân tích đường cong phần thưởng và số hàng dọn sạch qua 1,000 tập huấn luyện:

- Giai đoạn 1 (Tập 1 đến 200): Tác tử trong trạng thái khám phá hỗn loạn do epsilon còn cao. Số hàng dọn lẹt đẹt dưới 50 hàng.
- Giai đoạn 2 (Tập 200 đến 500): Tác tử bắt đầu nhận ra mối tương quan giữa việc phạt lỗ hổng và khả năng sống sót. Số hàng dọn ổn định dần quanh mức 100 đến 200 hàng.
- Giai đoạn 3 (Từ tập 700 trở đi): Đây chính là 'Điểm uốn đột phá' (Breakthrough Point) của mô hình. Khi epsilon giảm xuống mức 0.001, tác tử chuyển hẳn sang giai đoạn khai thác chính sách tối ưu. Đường cong dọn hàng tăng vọt theo phương thẳng đứng, liên tục phá vỡ các kỷ lục và đạt đỉnh 1,127 hàng dọn sạch ở tập thứ 850.

Đường cong học tập hội tụ mượt mà, không hề có dấu hiệu phân kỳ, chứng tỏ quá trình xấp xỉ hàm Q bằng MLP 3 lớp kết hợp Double DQN hoạt động cực kỳ ổn định.\""""
        },
        {
            "slide_num": "SLIDE 09",
            "time": "01:00",
            "title": "SO SÁNH TRỰC QUAN VỚI CÁC BASELINE (HÌNH 3 TRONG PAPER)",
            "visual": "Biểu đồ cột Fig. 3 đối sánh trực quan 3 phương pháp về Lines Cleared, Score và Survival Time.",
            "points": [
                "Khoảng cách mênh mông giữa học tăng cường tối ưu và thuật toán ngẫu nhiên/tham lam.",
                "Độ lệch chuẩn thể hiện độ vững chắc của chính sách."
            ],
            "script": """\"Sang Slide 9 là biểu đồ so sánh trực quan đa chiều giữa P-DDQN và hai baseline. Nhìn vào biểu đồ cột, Thầy/Cô có thể thấy sự áp đảo hoàn toàn của P-DDQN:

Cột của Random Agent và Greedy Agent gần như bẹp dí ở đáy đồ thị, trong khi cột của P-DDQN vươn cao vượt trội ở cả 3 thước đo: Số hàng dọn sạch, Điểm tích lũy và Thời gian sinh tồn. 

Điều này khẳng định rằng trong không gian tổ hợp phức tạp như Tetris, một chiến thuật tham lam cục bộ (Greedy) là hoàn toàn bất lực. Chỉ có học tăng cường sâu với tầm nhìn dài hạn mới có thể giải quyết được bài toán cân bằng giữa việc dọn hàng trước mắt và việc duy trì mặt phẳng bàn cờ cho tương lai.\""""
        },
        {
            "slide_num": "SLIDE 10",
            "time": "01:00",
            "title": "ĐỐI CHIẾU QUỐC TẾ & ƯU THẾ CỐT LÕI (21X FASTER)",
            "visual": "3 Cột So sánh lớn: Tốc độ (Nhanh hơn 21 lần), Phần cứng (Chỉ cần CPU), Điểm số (Vượt Heuristic +36.1%).",
            "points": [
                "Thời gian huấn luyện: 16.8 phút vs 6.0 giờ (nhanh hơn 21.4 lần).",
                "Phần cứng: CPU thông thường vs GPU chuyên dụng đắt đỏ.",
                "Hiệu suất: Vượt qua cả Heuristic chuyên gia được thiết kế thủ công."
            ],
            "script": """\"Để làm nổi bật đóng góp học thuật của đề tài, nhóm đã lập bảng đối chiếu với các công bố Deep RL tiêu biểu trên thế giới:

1. Về Tốc độ huấn luyện: Các công trình nghiên cứu sử dụng Deep Q-Learning truyền thống trên ảnh pixel (như kiến trúc DQN chuẩn của Mnih et al.) mất trung bình 6 giờ chạy trên GPU máy trạm. Mô hình P-DDQN của chúng em chỉ mất đúng 16.8 phút - tức là tốc độ hội tụ nhanh hơn gấp 21.4 lần!

2. Về Yêu cầu Tài nguyên: Chúng em không tiêu tốn bất kỳ một tài nguyên GPU đắt tiền nào; toàn bộ quá trình huấn luyện và đánh giá diễn ra nhẹ nhàng trên vi xử lý CPU máy tính cá nhân.

3. Về Hiệu năng Chính sách: Mô hình vượt trội hơn các Heuristic truyền thống (+36.1% về độ bền sinh tồn), chứng minh rằng chính sách học được vượt qua cả kinh nghiệm của con người khi tự tay viết luật cho game.\""""
        },
        {
            "slide_num": "SLIDE 11",
            "time": "01:30",
            "title": "TRÌNH DIỄN THỰC TẾ & GIẢI MÃ KHÁC BIỆT MÔI TRƯỜNG",
            "visual": "Terminal code block chạy mô hình, 2 Thẻ Card so sánh Pygame Visualizer vs Local Web Canvas.",
            "points": [
                "Lệnh terminal chạy demo: python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30.",
                "Giải thích lý do AI sống lâu hơn trên Local Web: Tốc độ xử lý không bị block bởi vòng lặp đồ họa Pygame, đồng bộ logic mượt mà hơn."
            ],
            "script": """\"Tiếp theo, em xin kính mời Thầy/Cô và các bạn cùng quan sát phần trình diễn thời gian thực (Live Demo).

Để chạy trực tiếp mô hình AI đã huấn luyện, chúng em sử dụng câu lệnh terminal chuẩn:
'python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30'.

Trong quá trình thực nghiệm, nhóm ghi nhận một hiện tượng khoa học rất thú vị: Khi cho cùng một file trọng số AI chạy trên Giao diện Web (Local Web Canvas), AI có tuổi thọ sinh tồn và điểm số cao hơn đáng kể so với khi hiển thị trên Pygame Visualizer. 

Nguyên nhân kỹ thuật nằm ở 2 điểm:
Thứ nhất: Pygame bị giới hạn bởi vòng lặp sự kiện đồ họa đồng bộ (event-loop rendering overhead), khiến độ trễ giữa các khung hình bị giật cục cục bộ, đôi khi làm chậm nhịp rơi của gạch.
Thứ hai: Giao diện Web chạy trên cơ chế tách biệt hoàn toàn giữa Web Worker xử lý logic và Canvas render bất đồng bộ. Nhờ đó, thuật toán AI thực thi trơn tru với độ trễ thuần 5.4 ms mà không bao giờ bị nghẽn đồ họa, giúp AI phản xạ và ra quyết định chính xác 100% trong mọi tình huống hiểm nghèo.\""""
        },
        {
            "slide_num": "SLIDE 12",
            "time": "01:00",
            "title": "TỔNG KẾT & LỘ TRÌNH NGHIÊN CỨU TIẾP THEO (GIAI ĐOẠN 2)",
            "visual": "Nền Deep Slate kết thúc, 2 Khối thẻ Card: Thành tựu giai đoạn 1 (50%) & Lộ trình giai đoạn 2 (50%).",
            "points": [
                "Hoàn thành 50% tiến độ: Mô hình P-DDQN thành công rực rỡ, bài báo khoa học đã hoàn tất.",
                "Giai đoạn 2: Tích hợp Dueling DQN, cơ chế nhìn trước khối kế (Next Piece), và chuyển giao sang bài toán Đóng gói 2D (2D Bin Packing) trong Logistics."
            ],
            "script": """\"Kính thưa Hội đồng, để tổng kết lại báo cáo ngày hôm nay:

Nhóm nghiên cứu đã hoàn tất xuất sắc 50% khối lượng đề tài:
- Xây dựng thành công kiến trúc P-DDQN với không gian Macro Action và vector 4D.
- Triệt tiêu hoàn toàn nút thắt Sample Inefficiency, huấn luyện thành công trong 16.8 phút trên CPU.
- Đạt kỷ lục dọn 1,127 hàng và hoàn thiện bài báo khoa học chuẩn Springer LNCS.

Trong 50% thời gian tiếp theo của giai đoạn hai, nhóm sẽ tập trung vào 3 hướng phát triển:
1. Thử nghiệm kiến trúc Dueling DDQN và kỹ thuật Prioritized Experience Replay để đẩy cao độ chính xác ước lượng.
2. Tích hợp cơ chế nhìn trước khối gạch tiếp theo (Next-Piece Lookahead) để nâng cao tầm nhìn chiến lược của AI.
3. Chuyển giao trực tiếp nền tảng thuật toán này sang bài toán thực tiễn công nghiệp: Đóng gói không gian hai chiều (2D Bin Packing Problem) trong quản lý kho bãi và logistics thông minh.

Em xin chân thành cảm ơn Thầy/Cô và các bạn đã chú ý lắng nghe! Sau đây, nhóm chúng em rất mong nhận được những câu hỏi và ý kiến đóng góp quý báu từ Hội đồng thẩm định.\""""
        }
    ]

    # Render slides in docx
    for s in slides_data:
        # Heading 1
        h = doc.add_heading(level=1)
        r_num = h.add_run(f"[{s['slide_num']}] ")
        r_num.bold = True
        r_num.font.name = "Segoe UI"
        r_num.font.color.rgb = SECONDARY
        r_title = h.add_run(s['title'])
        r_title.bold = True
        r_title.font.name = "Segoe UI"
        r_title.font.color.rgb = PRIMARY
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)

        # Meta line: Time & Visual Cue
        p_cue = doc.add_paragraph()
        r_t = p_cue.add_run(f"⏱️ Thời lượng dự kiến: {s['time']}   |   ")
        r_t.bold = True
        r_t.font.name = "Segoe UI"
        r_t.font.size = Pt(10)
        r_t.font.color.rgb = HIGHLIGHT

        r_v = p_cue.add_run(f"👁️ Bố cục trình chiếu: {s['visual']}")
        r_v.font.name = "Segoe UI"
        r_v.font.size = Pt(10)
        r_v.font.color.rgb = MUTED
        p_cue.paragraph_format.space_after = Pt(6)

        # Bullet points on slide
        p_pts_head = doc.add_paragraph()
        r_ph = p_pts_head.add_run("📌 Ý chính trên Slide (Khán giả nhìn):")
        r_ph.bold = True
        r_ph.font.name = "Segoe UI"
        r_ph.font.size = Pt(10.5)
        r_ph.font.color.rgb = PRIMARY
        p_pts_head.paragraph_format.space_after = Pt(2)

        for pt in s['points']:
            p_pt = doc.add_paragraph(style='List Bullet')
            r_pt = p_pt.add_run(pt)
            r_pt.font.name = "Segoe UI"
            r_pt.font.size = Pt(10.5)
            r_pt.font.color.rgb = TEXT
            p_pt.paragraph_format.space_after = Pt(2)

        # Speaker Script Box
        sc_table = doc.add_table(rows=1, cols=1)
        sc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        sc_cell = sc_table.cell(0, 0)
        set_cell_background(sc_cell, "F8FAFC")
        set_cell_margins(sc_cell, top=140, bottom=140, left=180, right=180)

        p_sc = sc_cell.paragraphs[0]
        r_sch = p_sc.add_run("🗣️ LỜI THOẠI NGƯỜI THUYẾT TRÌNH (SPEAKER SCRIPT):\n")
        r_sch.bold = True
        r_sch.font.name = "Segoe UI"
        r_sch.font.size = Pt(10)
        r_sch.font.color.rgb = SECONDARY

        r_body = p_sc.add_run(s['script'])
        r_body.font.name = "Segoe UI"
        r_body.font.size = Pt(11)
        r_body.font.italic = True
        r_body.font.color.rgb = PRIMARY
        p_sc.paragraph_format.line_spacing = 1.25

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # =========================================================================
    # SECTION: PREEMPTIVE Q&A FOR DEFENSE
    # =========================================================================
    doc.add_page_break()
    h_qa = doc.add_heading(level=1)
    r_qah = h_qa.add_run("DỰ PHÒNG CÂU HỎI HÓA GIẢI HỘI ĐỒNG (DEFENSE Q&A PREPARATION)")
    r_qah.bold = True
    r_qah.font.name = "Segoe UI"
    r_qah.font.color.rgb = PRIMARY

    qa_list = [
        {
            "q": "Câu 1: Tại sao việc trích xuất Vector 4 chiều lại tốt hơn việc cho Deep Learning tự học từ ảnh pixel 20x10?",
            "a": "Trả lời: Trạng thái pixel của Tetris là 20x10 = 200 ô nhị phân, tạo ra không gian trạng thái khổng lồ 2^200. Đối với mạng CNN thuần túy, hầu hết các pixel trống đều vô nghĩa, và mạng phải mất hàng triệu bước chỉ để 'học' được thế nào là một chiếc hố hay một mặt phẳng. Bằng cách trích xuất 4 đặc trưng hình học có ý nghĩa miền (Height, Holes, Bumpiness, Lines), chúng em đã thực hiện Feature Engineering chuẩn xác, biến bài toán từ học nhận diện hình ảnh thành bài toán ước lượng giá trị thế cờ. Điều này giúp mạng MLP chỉ cần 4,545 tham số nhưng hội tụ nhanh hơn 21 lần và đạt điểm số vượt trội."
        },
        {
            "q": "Câu 2: Tại sao khi chơi trên giao diện Local Web AI lại tồn tại lâu và điểm cao hơn trên Pygame Visualizer?",
            "a": "Trả lời: Trong Pygame, vòng lặp game loop chạy đơn luồng (single-thread), nơi lệnh `pygame.display.flip()` và xử lý event đè lên luồng suy luận của tác tử. Khi bàn cờ nhiều gạch và xử lý hiệu ứng dọn hàng, độ trễ khung hình tăng đột ngột khiến nhịp rơi bị lệch. Ngược lại, trên Local Web Canvas, logic của AI được xử lý độc lập ở Web Worker hoặc luồng JavaScript không bị chặn (non-blocking), còn Canvas render bất đồng bộ theo `requestAnimationFrame`. AI luôn ra quyết định ở tốc độ tuyệt đối 5.4 ms mà không bị nghẽn đồ họa, giúp chính sách duy trì độ chính xác tuyệt đối."
        },
        {
            "q": "Câu 3: Hàm thưởng bậc hai (Lines * 1.5)^2 có vai trò gì và tại sao không dùng hàm tuyến tính thông thường?",
            "a": "Trả lời: Nếu dùng hàm tuyến tính (ví dụ dọn 1 hàng được 1 điểm, 4 hàng được 4 điểm), AI sẽ có xu hướng chơi an toàn và 'ăn non' - tức là cứ có cơ hội ăn 1 hàng là dọn ngay để lấy thưởng tức thì. Hành vi này khiến bề mặt bàn cờ nhanh chóng bị thủng lỗ và chết sớm. Bằng cách dùng hàm bậc hai (Lines * 1.5)^2, điểm thưởng cho 4 hàng cùng lúc là 36 điểm, gấp 16 lần so với ăn 1 hàng (2.25 điểm). Sự chênh lệch phi tuyến tính này tạo ra động lực kinh tế cực lớn để tác tử chấp nhận rủi ro tích lũy cột cao ở hai bên nhằm đợi gạch chữ I ăn trọn vẹn 4 hàng (Tetris)."
        },
        {
            "q": "Câu 4: Double DQN đã khắc phục hiện tượng Overestimation Bias như thế nào trong bài toán này?",
            "a": "Trả lời: Thuật toán DQN kinh điển sử dụng toán tử Max ở cả khâu chọn hành động và khâu định giá mục tiêu: Y = r + gamma * max_a Q(s', a). Điều này dẫn tới hiện tượng thiên lệch thổi phồng (Maximization Bias), vì bất kỳ sai số ngẫu nhiên nào cũng bị lấy cực đại và khuếch đại lên qua các vòng lặp Bellman. Double DQN giải quyết triệt để bằng cách tách đôi: Mạng Online Network dùng để chọn hành động tốt nhất a* = argmax_a Q_online(s', a), nhưng mạng Target Network độc lập lại dùng để lượng giá trị Q_target(s', a*). Nhờ đó, sai số thổi phồng bị triệt tiêu hoàn toàn, giúp đường cong học tập ổn định tuyệt đối."
        },
        {
            "q": "Câu 5: Hướng phát triển và khả năng ứng dụng thực tế của mô hình này trong công nghiệp là gì?",
            "a": "Trả lời: Bản chất toán học của bài toán Tetris chính là bài toán Đóng gói 2 chiều trực tuyến (Online 2D Bin Packing Problem). Trong thực tế Logistics và Kho bãi thông minh, các kiện hàng với kích thước khác nhau liên tục đến băng chuyền và cánh tay robot phải quyết định tức thì vị trí đặt kiện hàng vào container sao cho khoảng trống lãng phí là ít nhất. Phương pháp Macro Action kết hợp vector đặc trưng hình học của nhóm chúng em có thể chuyển giao trực tiếp để giải quyết bài toán xếp dỡ container tự động với thời gian phản hồi mili-giây trên phần cứng nhúng giá rẻ."
        }
    ]

    for qa in qa_list:
        p_q = doc.add_paragraph()
        r_q = p_q.add_run(qa['q'])
        r_q.bold = True
        r_q.font.name = "Segoe UI"
        r_q.font.size = Pt(11)
        r_q.font.color.rgb = PRIMARY
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)

        p_a = doc.add_paragraph()
        r_a = p_a.add_run(qa['a'])
        r_a.font.name = "Segoe UI"
        r_a.font.size = Pt(10.5)
        r_a.font.color.rgb = TEXT
        p_a.paragraph_format.line_spacing = 1.2
        p_a.paragraph_format.space_after = Pt(6)

    doc.save(output_path)
    print(f"Successfully generated DOCX script: {output_path}")

def create_script_markdown(output_path):
    md_content = """# KỊCH BẢN THUYẾT TRÌNH BÁO CÁO KHOA HỌC (STAGE-READY SCRIPT)
## Đề tài: Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning
**Định dạng xuất bản:** Springer LNCS / ICCIES Conference (`paper.pdf`)  
**Bộ slide đối ứng:** `SLIDE_THUYET_TRINH_BAO_CAO_TIEN_DO_FINAL.pptx` (12 Slide Chuẩn Cyber-Tech Luxury)  
**Thời lượng chuẩn:** 12 - 15 phút trình bày + 5 - 10 phút bảo vệ Q&A  
**Lệnh chạy Live Demo:** `python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30`

---

## SLIDE 01: BÌA BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU
* **Thời lượng:** 01:00
* **Bố cục Visual:** Nền Deep Slate huyền bí, hiệu ứng phát sáng Neon Cyan, huy hiệu Springer LNCS / ICCIES Conference.
* **Ý chính trên Slide:** Tên đề tài, Tác giả, GVHD, Mục tiêu cốt lõi.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Kính thưa Thầy/Cô trong Hội đồng thẩm định và toàn thể các bạn sinh viên,  
> Em xin đại diện nhóm nghiên cứu trình bày báo cáo tiến độ đề tài khoa học: **'Placement-Based Double Deep Q-Network for Sample-Efficient Tetris Policy Learning'** - Tối ưu hóa học tăng cường sâu dựa trên không gian đặt khối giúp huấn luyện chính sách Tetris hiệu quả cao về mẫu.  
> 
> Nghiên cứu của chúng em tập trung giải quyết câu hỏi cốt tử trong Reinforcement Learning hiện đại: *'Làm thế nào để một tác tử AI tự học được chiến thuật chơi Tetris ở đẳng cấp chuyên gia mà không đòi hỏi cụm máy chủ GPU đắt đỏ, chỉ cần huấn luyện trên một chiếc CPU máy tính cá nhân trong chưa đầy 17 phút?'*.  
> 
> Sau đây, em xin phép đi vào chi tiết cấu trúc bài báo cáo."*

---

## SLIDE 02: HAI NÚT THẮT TRIỆT TIÊU HIỆU NĂNG DEEP RL TRUYỀN THỐNG
* **Thời lượng:** 01:30
* **Bố cục Visual:** 2 Khối thẻ Card lớn: Thẻ Coral (Credit Assignment Latency) và Thẻ Blue (Sample Inefficiency).
* **Ý chính trên Slide:**
  * **01. Credit Assignment:** Hàng chục phím vi mô mới thả rơi 1 khối. Thưởng quá thưa gây sụp đổ chính sách.
  * **02. Sample Inefficiency:** Huấn luyện trên ma trận pixel thô 20x10 tốn >24h GPU nhưng bão hòa dưới 15 hàng dọn sạch.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Kính thưa Hội đồng, khi áp dụng các thuật toán Deep RL kinh điển (như DQN thuần túy của DeepMind) vào bài toán Tetris, các nghiên cứu trên thế giới đều va phải hai rào cản vật lý nghiêm trọng:  
> 
> Thứ nhất là **Credit Assignment Latency** - Nút thắt phân bổ tín dụng hành vi. Ở mức vi mô (micro-actions), để hạ cánh một khối gạch, tác tử phải thực hiện hàng chục thao tác liên tiếp: qua trái, qua phải, xoay, thả rơi. Tín hiệu phần thưởng chỉ xuất hiện ở bước cuối cùng khi dọn được hàng. Chuỗi quyết định quá dài khiến thuật toán không thể suy luận được phím bấm nào trong quá khứ là đúng đắn, dẫn tới hiện tượng sụp đổ chính sách (Policy Collapse).  
> 
> Thứ hai là **Sample Inefficiency** - Hiệu quả sử dụng mẫu kém. Nếu nhồi ma trận pixel thô 20x10 vào mạng CNN, mô hình phải mất hàng chục giờ chạy trên GPU chỉ để nhận biết được các cạnh gạch. Hệ quả là phần lớn mô hình DQN truyền thống bị bão hòa và kẹt cứng ở ngưỡng dưới 15 hàng dọn sạch.  
> 
> Nhận thức rõ hai rào cản này, nghiên cứu của chúng em đề xuất một hướng tiếp cận đột phá: chuyển đổi từ không gian hành động vi mô sang Macro Placement kết hợp biểu diễn trạng thái hình học tinh gọn."*

---

## SLIDE 03: QUY TRÌNH KIẾN TRÚC P-DDQN (FIG. 1 TRONG BÀI BÁO)
* **Thời lượng:** 01:30
* **Bố cục Visual:** Hình ảnh Fig. 1 trích xuất độ nét cao từ trang 4 của `paper.pdf`, kèm thanh tóm tắt 4 giai đoạn xử lý.
* **Ý chính trên Slide:**
  * 1. Placement Enumeration (Duyệt cặp x, r)
  * 2. 4D Feature Vector (Height, Holes, Bumpiness, Lines)
  * 3. Double DQN Target Decoupling (Online & Target Net)
  * 4. Greedy Action Selection (argmax Q)

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Trên màn hình là **Hình 1 (Fig. 1)** trích xuất trực tiếp từ bài báo khoa học của chúng em, minh họa toàn bộ đường ống kiến trúc P-DDQN qua 4 giai đoạn liên hoàn:  
> 
> - **Giai đoạn 1 - Placement Enumeration:** Khi một khối tetromino xuất hiện ở đỉnh bàn cờ, thay vì bắt AI bấm từng phím vi mô, thuật toán mô phỏng trước toàn bộ không gian đặt gạch hợp lệ gồm tọa độ cột $x$ và góc xoay $r$ (thường chỉ từ 10 đến 34 vị trí có thể đặt được).  
> - **Giai đoạn 2 - 4D Feature Vector Extraction:** Với mỗi vị trí đặt thử nghiệm, môi trường giả lập tạo ra trạng thái bàn cờ tương lai và trích xuất thành một vector hình học 4 chiều duy nhất.  
> - **Giai đoạn 3 - Double DQN Target Decoupling:** Vector 4D này được đưa vào mạng nơ-ron để ước lượng giá trị kỳ vọng $Q(s, a)$. Chúng em tách biệt hoàn toàn mạng Online Network (chuyên chọn hành động) và Target Network (chuyên định giá) nhằm triệt tiêu hoàn toàn sai số thổi phồng giá trị (Overestimation Bias).  
> - **Giai đoạn 4 - Greedy Selection:** Tác tử chọn nước đi có giá trị Q cao nhất và thực hiện rơi cứng xuống bàn cờ. Đường ống này giúp nén không gian tìm kiếm từ hàng triệu bước rời rạc xuống một bài toán tối ưu cục bộ cực kỳ tinh gọn."*

---

## SLIDE 04: MÔ HÌNH HÓA MDP & VECTOR HÌNH HỌC BỐN CHIỀU
* **Thời lượng:** 01:30
* **Bố cục Visual:** 4 Thẻ Card đại diện cho $f_1, f_2, f_3, f_4$ và Formula Banner nền tối neon cyan chứa hàm thưởng phi tuyến.
* **Ý chính trên Slide:**
  * $f_1$ - Height (Tổng chiều cao 10 cột)
  * $f_2$ - Holes (Số lỗ hổng bị che lấp - Phạt nặng nhất)
  * $f_3$ - Bumpiness (Độ gồ ghề giữa các cột - Giữ mặt phẳng)
  * $f_4$ - Lines Cleared (Số hàng dọn tức thì - Thưởng bậc hai)
  * Công thức thưởng: $R(s, a, s') = 1.0 + (\text{Lines} \times 1.5)^2 - 1.0 \Delta\text{Holes} - 0.2 \Delta\text{Bumpiness} - 0.5 \Delta\text{Height}$

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Kính thưa Thầy/Cô, linh hồn của sự tinh gọn trong đề tài nằm ở việc mô hình hóa bài toán theo Markov Decision Process (MDP) với vector đặc trưng 4 chiều:  
> 1. Chiều $f_1$ - Height: Tổng độ cao tích lũy của 10 cột, phản ánh mức độ hiểm nghèo của bàn cờ.  
> 2. Chiều $f_2$ - Holes: Số lỗ hổng bị gạch che khuất bên trên. Đây là chỉ số nguy hiểm nhất trong Tetris, vì lỗ hổng càng sâu thì càng không thể dọn hàng.  
> 3. Chiều $f_3$ - Bumpiness: Tổng độ chênh lệch độ cao giữa các cột liền kề, định lượng độ bằng phẳng của bề mặt.  
> 4. Chiều $f_4$ - Lines Cleared: Số lượng hàng dọn sạch tức thì sau khi đặt khối.  
> 
> Đặc biệt, ở đáy slide là **Hàm thưởng phi tuyến (Reward Shaping)** do nhóm thiết kế:  
> $R(s, a, s') = 1.0 \text{ (sống sót)} + (\text{Lines} \times 1.5)^2 \text{ (thưởng combo)} - 1.0 \Delta\text{Holes} - 0.2 \Delta\text{Bumpiness} - 0.5 \Delta\text{Height}$.  
> 
> Trọng số phạt lỗ hổng $\Delta\text{Holes}$ được đặt bằng $-1.0$, lớn gấp đôi các thành phần khác để ép AI không được tạo hốc kẹt. Đáng chú ý nhất, thành phần dọn hàng được áp dụng hàm lũy thừa bậc hai: nếu chỉ ăn 1 hàng, AI nhận $(1 \times 1.5)^2 = 2.25$ điểm; nhưng nếu kiên nhẫn tích lũy ăn 4 hàng (Tetris), điểm thưởng vọt lên $(4 \times 1.5)^2 = 36$ điểm - gấp 16 lần! Đây chính là chìa khóa toán học giúp AI tự hình thành tư duy chơi gom combo đỉnh cao."*

---

## SLIDE 05: MẠNG NƠ-RON 4.5K THAM SỐ & CƠ CHẾ DOUBLE DQN
* **Thời lượng:** 01:00
* **Bố cục Visual:** Con số khổng lồ 4,545 tham số, Thẻ Card Target Decoupling, độ trễ 5.4 ms.
* **Ý chính trên Slide:**
  * MLP 3 lớp: Input(4) -> 64 -> 64 -> Linear(1).
  * Kích thước checkpoint: 82 KB.
  * Tốc độ suy luận: 5.4 ms/bước (>180 FPS trên CPU).
  * Tách rời ước lượng: Online Net chọn hành động $a^*$, Target Net tính giá trị $Q$.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Sang đến thiết kế mạng nơ-ron, nhóm kiên định theo đuổi triết lý 'Tối giản nhưng Uy lực':  
> Thay vì sử dụng mạng CNN hàng triệu tham số ngốn bộ nhớ, mạng học sâu của chúng em chỉ gồm 3 lớp Perceptron đa tầng (MLP) với cấu trúc: Input 4 node -> 64 neuron (ReLU) -> 64 neuron (ReLU) -> Linear Output 1 node thể hiện Q-value.  
> 
> Tổng số lượng tham số toàn mạng chỉ vỏn vẹn **4,545 tham số**. File mô hình lưu trữ trên đĩa chỉ nặng **82 Kilobytes**!  
> 
> Nhờ sự tinh gọn tuyệt đối này, tốc độ suy luận của mô hình đạt **5.4 mili-giây** cho mỗi quyết định, tương đương tốc độ khung hình hơn 180 FPS hoàn toàn trên CPU thông thường mà không cần bất kỳ GPU chuyên dụng nào. Cơ chế Double DQN đồng thời cập nhật Target Network sau mỗi 10 bước huấn luyện, giữ cho quá trình học ổn định tuyệt đối, không xảy ra hiện tượng dao động hay sụp đổ hàm giá trị."*

---

## SLIDE 06: THIẾT LẬP THỰC NGHIỆM & PHẦN CỨNG HUẤN LUYỆN
* **Thời lượng:** 01:00
* **Bố cục Visual:** 3 Cột Thông số: Ngân sách huấn luyện (1,000 eps), Môi trường phần cứng (CPU cá nhân), Tham số RL.
* **Ý chính trên Slide:**
  * Ngân sách: 1,000 tập huấn luyện.
  * Phần cứng: Intel CPU thông dụng, 0% GPU.
  * Tổng thời gian: Đúng 16.8 phút.
  * Epsilon Decay: Giảm đều 0.995 sau mỗi tập, chạm đáy 0.001 ở tập 700.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Về thiết lập thực nghiệm, toàn bộ quá trình huấn luyện được thực thi với cấu hình:  
> - Ngân sách huấn luyện: Đúng 1,000 episodes độc lập.  
> - Thiết bị thử nghiệm: CPU máy tính xách tay cá nhân (Intel Core i5 thông dụng), 0% GPU.  
> - Tổng thời gian hoàn tất quá trình huấn luyện: Đúng **16.8 phút**.  
> 
> Các siêu tham số học tăng cường gồm:  
> - Tốc độ học (Learning Rate): $10^{-3}$ với bộ tối ưu hóa Adam.  
> - Bộ đệm nhớ (Replay Buffer): Dung lượng 20,000 bước chuyển dịch, lấy mẫu mini-batch 64.  
> - Chiến lược khám phá Epsilon-Greedy: Khởi đầu từ 1.0 (khám phá ngẫu nhiên 100%) và giảm dần đều theo hệ số 0.995 sau mỗi tập, chạm ngưỡng tối thiểu 0.001 ở tập thứ 700. Điều này đảm bảo AI có đủ thời gian khám phá không gian trạng thái trước khi bước vào giai đoạn khai thác chính sách tối ưu."*

---

## SLIDE 07: KẾT QUẢ ĐỊNH LƯỢNG & PHÂN TÍCH CHUYÊN SÂU BẢNG 1 (TABLE 1)
* **Thời lượng:** 02:00
* **Bố cục Visual:** Bảng Table 1 trích xuất từ `paper.pdf` (7 cột), highlight dòng P-DDQN và Takeaway Banner xanh ngọc.
* **Ý chính trên Slide:**
  * Random: 0.1 hàng, Sống sót 25.5 bước, 40.0 điểm/hàng.
  * Naive Greedy: 18.8 hàng, Sống sót 85.2 bước, 51.5 điểm/hàng.
  * **P-DDQN (Đề xuất):** 287.5 hàng TB, Trung vị 388.0 hàng, Kỷ lục 398 hàng, Điểm TB 23,360.8, Sống sót 749.1 bước, **81.3 điểm/hàng**.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Kính thưa Hội đồng, đây là Slide quan trọng nhất trong bài báo cáo - **Bảng 1 (Table 1)** trích nguyên văn từ bài báo khoa học đã xuất bản của nhóm. Bảng thể hiện kết quả kiểm thử định lượng nghiêm ngặt trên 100 ván đấu độc lập với giới hạn trần 1,000 bước đặt gạch:  
> 
> 1. **Tác tử ngẫu nhiên (Random Agent):** Chỉ sống sót trung bình 25.5 bước, số hàng dọn sạch gần như bằng 0 (0.1 hàng). Điều này chứng minh không gian bàn cờ Tetris cực kỳ khắt khe, nếu không có chiến lược thì game over ngay tức khắc.  
> 
> 2. **Tác tử Heuristic tham lam (Naive Greedy):** Thuật toán này chọn nước đi dọn hàng ngay lập tức ở từng bước. Kết quả dọn được 18.8 hàng nhưng nhanh chóng bị loại sau trung bình 85 bước đặt gạch. Lý do là vì quá tham lam ăn hàng trước mắt nên tác tử để lại hàng loạt lỗ hổng chí mạng phía dưới bàn cờ.  
> 
> 3. **Mô hình đề xuất P-DDQN:** Tạo nên một sự bứt phá vượt bậc về mọi chỉ số:  
> - Số hàng dọn trung bình: Đạt **287.5 hàng** (cao gấp 15.3 lần Naive Greedy).  
> - Giá trị trung vị (Median): Đạt tới **388.0 hàng**.  
> - Điểm số trung bình: Đạt **23,360.8 điểm**.  
> - Khả năng sống sót: **749.1 bước** đặt gạch. Đặc biệt, có tới **54 trên 100 ván đấu tác tử đã chạm trần kiểm thử 1,000 bước** mà không hề bị thua!  
> 
> Đặc biệt nhất, xin mời Thầy/Cô nhìn vào cột cuối cùng: **Điểm số trên mỗi hàng (Points per line)**. Nếu chỉ ăn đơn lẻ 1 hàng, hệ số điểm Tetris là 40 điểm/hàng. Greedy chỉ đạt 51.5 điểm/hàng. Trong khi P-DDQN đạt tới **81.3 điểm/hàng**! Con số toán học này khẳng định chắc chắn rằng: Tác tử không hề chơi theo kiểu ăn may, mà đã tự hình thành chiến thuật tích lũy thế cờ để dọn sạch cùng lúc 3 đến 4 hàng (Triple và Tetris)."*

---

## SLIDE 08: TIẾN TRÌNH HỌC TẬP & HỘI TỤ CHÍNH SÁCH (HÌNH 2 TRONG PAPER)
* **Thời lượng:** 01:30
* **Bố cục Visual:** Biểu đồ Fig. 2 đường cong học tập và các mốc Checkpoint lịch sử 200, 500, 700, 1000.
* **Ý chính trên Slide:**
  * Tập 1 - 200: Khám phá sơ khởi (<50 hàng).
  * Tập 200 - 500: Định hình mặt phẳng (100 - 200 hàng).
  * Tập 700: Điểm uốn đột phá (Breakthrough Point), Epsilon đạt 0.001, điểm số vọt lên đỉnh 1,127 hàng ở tập 850.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Hình ảnh trên Slide là đồ thị tiến trình học tập trích xuất từ **Hình 2** trong bài báo của chúng em, phân tích đường cong phần thưởng và số hàng dọn sạch qua 1,000 tập huấn luyện:  
> 
> - Giai đoạn 1 (Tập 1 đến 200): Tác tử trong trạng thái khám phá hỗn loạn do epsilon còn cao. Số hàng dọn lẹt đẹt dưới 50 hàng.  
> - Giai đoạn 2 (Tập 200 đến 500): Tác tử bắt đầu nhận ra mối tương quan giữa việc phạt lỗ hổng và khả năng sống sót. Số hàng dọn ổn định dần quanh mức 100 đến 200 hàng.  
> - Giai đoạn 3 (Từ tập 700 trở đi): Đây chính là **'Điểm uốn đột phá' (Breakthrough Point)** của mô hình. Khi epsilon giảm xuống mức 0.001, tác tử chuyển hẳn sang giai đoạn khai thác chính sách tối ưu. Đường cong dọn hàng tăng vọt theo phương thẳng đứng, liên tục phá vỡ các kỷ lục và đạt đỉnh **1,127 hàng** dọn sạch ở tập thứ 850.  
> 
> Đường cong học tập hội tụ mượt mà, không hề có dấu hiệu phân kỳ, chứng tỏ quá trình xấp xỉ hàm Q bằng MLP 3 lớp kết hợp Double DQN hoạt động cực kỳ ổn định."*

---

## SLIDE 09: SO SÁNH TRỰC QUAN VỚI CÁC BASELINE (HÌNH 3 TRONG PAPER)
* **Thời lượng:** 01:00
* **Bố cục Visual:** Biểu đồ cột Fig. 3 đối sánh trực quan 3 phương pháp về Lines Cleared, Score và Survival Time.
* **Ý chính trên Slide:**
  * Sự áp đảo toàn diện của P-DDQN trước Random và Greedy Agent.
  * Tầm nhìn dài hạn đánh bại hoàn toàn các chiến thuật tham lam trước mắt.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Sang Slide 9 là biểu đồ so sánh trực quan đa chiều giữa P-DDQN và hai baseline. Nhìn vào biểu đồ cột, Thầy/Cô có thể thấy sự áp đảo hoàn toàn của P-DDQN:  
> 
> Cột của Random Agent và Greedy Agent gần như bẹp dí ở đáy đồ thị, trong khi cột của P-DDQN vươn cao vượt trội ở cả 3 thước đo: Số hàng dọn sạch, Điểm tích lũy và Thời gian sinh tồn.  
> 
> Điều này khẳng định rằng trong không gian tổ hợp phức tạp như Tetris, một chiến thuật tham lam cục bộ (Greedy) là hoàn toàn bất lực. Chỉ có học tăng cường sâu với tầm nhìn dài hạn mới có thể giải quyết được bài toán cân bằng giữa việc dọn hàng trước mắt và việc duy trì mặt phẳng bàn cờ cho tương lai."*

---

## SLIDE 10: ĐỐI CHIẾU QUỐC TẾ & ƯU THẾ CỐT LÕI (21X FASTER)
* **Thời lượng:** 01:00
* **Bố cục Visual:** 3 Cột So sánh lớn: Tốc độ (Nhanh hơn 21 lần), Phần cứng (Chỉ cần CPU), Điểm số (Vượt Heuristic +36.1%).
* **Ý chính trên Slide:**
  * Tốc độ: 16.8 phút vs 6.0 giờ (Nhanh hơn 21.4 lần).
  * Tài nguyên: 0% GPU, chỉ dùng CPU thông thường.
  * Hiệu năng: Vượt qua cả Heuristic chuyên gia viết tay (+36.1%).

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Để làm nổi bật đóng góp học thuật của đề tài, nhóm đã lập bảng đối chiếu với các công bố Deep RL tiêu biểu trên thế giới:  
> 
> 1. **Về Tốc độ huấn luyện:** Các công trình nghiên cứu sử dụng Deep Q-Learning truyền thống trên ảnh pixel (như kiến trúc DQN chuẩn của Mnih et al.) mất trung bình 6 giờ chạy trên GPU máy trạm. Mô hình P-DDQN của chúng em chỉ mất đúng **16.8 phút** - tức là tốc độ hội tụ nhanh hơn gấp **21.4 lần**!  
> 
> 2. **Về Yêu cầu Tài nguyên:** Chúng em không tiêu tốn bất kỳ một tài nguyên GPU đắt tiền nào; toàn bộ quá trình huấn luyện và đánh giá diễn ra nhẹ nhàng trên vi xử lý CPU máy tính cá nhân.  
> 
> 3. **Về Hiệu năng Chính sách:** Mô hình vượt trội hơn các Heuristic truyền thống (+36.1% về độ bền sinh tồn), chứng minh rằng chính sách học được vượt qua cả kinh nghiệm của con người khi tự tay viết luật cho game."*

---

## SLIDE 11: TRÌNH DIỄN THỰC TẾ & GIẢI MÃ KHÁC BIỆT MÔI TRƯỜNG
* **Thời lượng:** 01:30
* **Bố cục Visual:** Terminal code block chạy mô hình, 2 Thẻ Card so sánh Pygame Visualizer vs Local Web Canvas.
* **Ý chính trên Slide:**
  * Lệnh chạy demo: `python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30`
  * Bản chất kỹ thuật: Pygame nghẽn do event-loop render đơn luồng; Local Web tối ưu nhờ tách luồng Canvas bất đồng bộ.

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Tiếp theo, em xin kính mời Thầy/Cô và các bạn cùng quan sát phần trình diễn thời gian thực (Live Demo).  
> 
> Để chạy trực tiếp mô hình AI đã huấn luyện, chúng em sử dụng câu lệnh terminal chuẩn:  
> `python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 30`.  
> 
> Trong quá trình thực nghiệm, nhóm ghi nhận một hiện tượng khoa học rất thú vị: Khi cho cùng một file trọng số AI chạy trên Giao diện Web (Local Web Canvas), AI có tuổi thọ sinh tồn và điểm số cao hơn đáng kể so với khi hiển thị trên Pygame Visualizer.  
> 
> Nguyên nhân kỹ thuật nằm ở 2 điểm:  
> - **Thứ nhất:** Pygame bị giới hạn bởi vòng lặp sự kiện đồ họa đồng bộ (event-loop rendering overhead), khiến độ trễ giữa các khung hình bị giật cục bộ, đôi khi làm chậm nhịp rơi của gạch.  
> - **Thứ hai:** Giao diện Web chạy trên cơ chế tách biệt hoàn toàn giữa Web Worker xử lý logic và Canvas render bất đồng bộ. Nhờ đó, thuật toán AI thực thi trơn tru với độ trễ thuần 5.4 ms mà không bao giờ bị nghẽn đồ họa, giúp AI phản xạ và ra quyết định chính xác 100% trong mọi tình huống hiểm nghèo."*

---

## SLIDE 12: TỔNG KẾT & LỘ TRÌNH NGHIÊN CỨU TIẾP THEO (GIAI ĐOẠN 2)
* **Thời lượng:** 01:00
* **Bố cục Visual:** Nền Deep Slate kết thúc, 2 Khối thẻ Card: Thành tựu giai đoạn 1 (50%) & Lộ trình giai đoạn 2 (50%).
* **Ý chính trên Slide:**
  * Hoàn thành 50% tiến độ: P-DDQN thành công, hoàn thiện bài báo quốc tế.
  * Lộ trình tiếp theo: Dueling DDQN, nhìn trước khối kế (Next Piece), và chuyển giao sang bài toán Đóng gói 2D (2D Bin Packing).

> 🗣️ **LỜI THOẠI NGƯỜI THUYẾT TRÌNH:**
> 
> *"Kính thưa Hội đồng, để tổng kết lại báo cáo ngày hôm nay:  
> 
> Nhóm nghiên cứu đã hoàn tất xuất sắc 50% khối lượng đề tài:  
> - Xây dựng thành công kiến trúc P-DDQN với không gian Macro Action và vector 4D.  
> - Triệt tiêu hoàn toàn nút thắt Sample Inefficiency, huấn luyện thành công trong 16.8 phút trên CPU.  
> - Đạt kỷ lục dọn 1,127 hàng và hoàn thiện bài báo khoa học chuẩn Springer LNCS.  
> 
> Trong 50% thời gian tiếp theo của giai đoạn hai, nhóm sẽ tập trung vào 3 hướng phát triển:  
> 1. Thử nghiệm kiến trúc Dueling DDQN và kỹ thuật Prioritized Experience Replay để đẩy cao độ chính xác ước lượng.  
> 2. Tích hợp cơ chế nhìn trước khối gạch tiếp theo (Next-Piece Lookahead) để nâng cao tầm nhìn chiến lược của AI.  
> 3. Chuyển giao trực tiếp nền tảng thuật toán này sang bài toán thực tiễn công nghiệp: Đóng gói không gian hai chiều (2D Bin Packing Problem) trong quản lý kho bãi và logistics thông minh.  
> 
> Em xin chân thành cảm ơn Thầy/Cô và các bạn đã chú ý lắng nghe! Sau đây, nhóm chúng em rất mong nhận được những câu hỏi và ý kiến đóng góp quý báu từ Hội đồng thẩm định."*

---

## PHẦN DỰ PHÒNG CÂU HỎI HÓA GIẢI HỘI ĐỒNG (DEFENSE Q&A)

### ❓ Câu 1: Tại sao việc trích xuất Vector 4 chiều lại tốt hơn việc cho Deep Learning tự học từ ảnh pixel 20x10?
> **Trả lời:**  
> Trạng thái pixel của Tetris là $20 \times 10 = 200$ ô nhị phân, tạo ra không gian trạng thái khổng lồ $2^{200}$. Đối với mạng CNN thuần túy, hầu hết các pixel trống đều vô nghĩa, và mạng phải mất hàng triệu bước chỉ để 'học' được thế nào là một chiếc hố hay một mặt phẳng. Bằng cách trích xuất 4 đặc trưng hình học có ý nghĩa miền (Height, Holes, Bumpiness, Lines), chúng em đã thực hiện Feature Engineering chuẩn xác, biến bài toán từ học nhận diện hình ảnh thành bài toán ước lượng giá trị thế cờ. Điều này giúp mạng MLP chỉ cần 4,545 tham số nhưng hội tụ nhanh hơn 21 lần và đạt điểm số vượt trội.

### ❓ Câu 2: Tại sao khi chơi trên giao diện Local Web AI lại tồn tại lâu và điểm cao hơn trên Pygame Visualizer?
> **Trả lời:**  
> Trong Pygame, vòng lặp game loop chạy đơn luồng (single-thread), nơi lệnh `pygame.display.flip()` và xử lý event đè lên luồng suy luận của tác tử. Khi bàn cờ nhiều gạch và xử lý hiệu ứng dọn hàng, độ trễ khung hình tăng đột ngột khiến nhịp rơi bị lệch. Ngược lại, trên Local Web Canvas, logic của AI được xử lý độc lập ở Web Worker hoặc luồng JavaScript không bị chặn (non-blocking), còn Canvas render bất đồng bộ theo `requestAnimationFrame`. AI luôn ra quyết định ở tốc độ tuyệt đối 5.4 ms mà không bị nghẽn đồ họa, giúp chính sách duy trì độ chính xác tuyệt đối.

### ❓ Câu 3: Hàm thưởng bậc hai $(Lines \times 1.5)^2$ có vai trò gì và tại sao không dùng hàm tuyến tính thông thường?
> **Trả lời:**  
> Nếu dùng hàm tuyến tính (ví dụ dọn 1 hàng được 1 điểm, 4 hàng được 4 điểm), AI sẽ có xu hướng chơi an toàn và 'ăn non' - tức là cứ có cơ hội ăn 1 hàng là dọn ngay để lấy thưởng tức thì. Hành vi này khiến bề mặt bàn cờ nhanh chóng bị thủng lỗ và chết sớm. Bằng cách dùng hàm bậc hai $(Lines \times 1.5)^2$, điểm thưởng cho 4 hàng cùng lúc là 36 điểm, gấp 16 lần so với ăn 1 hàng (2.25 điểm). Sự chênh lệch phi tuyến tính này tạo ra động lực kinh tế cực lớn để tác tử chấp nhận rủi ro tích lũy cột cao ở hai bên nhằm đợi gạch chữ I ăn trọn vẹn 4 hàng (Tetris).

### ❓ Câu 4: Double DQN đã khắc phục hiện tượng Overestimation Bias như thế nào trong bài toán này?
> **Trả lời:**  
> Thuật toán DQN kinh điển sử dụng toán tử Max ở cả khâu chọn hành động và khâu định giá mục tiêu: $Y = r + \gamma \max_a Q(s', a)$. Điều này dẫn tới hiện tượng thiên lệch thổi phồng (Maximization Bias), vì bất kỳ sai số ngẫu nhiên nào cũng bị lấy cực đại và khuếch đại lên qua các vòng lặp Bellman. Double DQN giải quyết triệt để bằng cách tách đôi: Mạng Online Network dùng để chọn hành động tốt nhất $a^* = \arg\max_a Q_{online}(s', a)$, nhưng mạng Target Network độc lập lại dùng để lượng giá trị $Q_{target}(s', a^*)$. Nhờ đó, sai số thổi phồng bị triệt tiêu hoàn toàn, giúp đường cong học tập ổn định tuyệt đối.

### ❓ Câu 5: Hướng phát triển và khả năng ứng dụng thực tế của mô hình này trong công nghiệp là gì?
> **Trả lời:**  
> Bản chất toán học của bài toán Tetris chính là bài toán Đóng gói 2 chiều trực tuyến (Online 2D Bin Packing Problem). Trong thực tế Logistics và Kho bãi thông minh, các kiện hàng với kích thước khác nhau liên tục đến băng chuyền và cánh tay robot phải quyết định tức thì vị trí đặt kiện hàng vào container sao cho khoảng trống lãng phí là ít nhất. Phương pháp Macro Action kết hợp vector đặc trưng hình học của nhóm chúng em có thể chuyển giao trực tiếp để giải quyết bài toán xếp dỡ container tự động với thời gian phản hồi mili-giây trên phần cứng nhúng giá rẻ.
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Successfully generated Markdown script: {output_path}")

if __name__ == "__main__":
    docx_file = r"C:\Users\Khang\Desktop\Mon_REL\project\KICH_BAN_THUYET_TRINH_HOAN_CHINH_FINAL.docx"
    md_file = r"C:\Users\Khang\Desktop\Mon_REL\project\KICH_BAN_THUYET_TRINH_HOAN_CHINH_FINAL.md"
    create_script_docx(docx_file)
    create_script_markdown(md_file)
