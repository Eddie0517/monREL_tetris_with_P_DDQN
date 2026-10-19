# 🎮 Tetris with Reinforcement Learning (monREL_tetris_with_P_DDQN)

> **Dự án Nghiên cứu & Huấn luyện AI Tự Động Chơi Tetris Bằng Học Tăng Cường (Reinforcement Learning)**  
> Kho lưu trữ mã nguồn cho môn học **Reinforcement Learning** kèm giao diện mô phỏng game **Cyber Tetris** hiện đại.

[![GitHub Repo](https://img.shields.io/badge/GitHub-Eddie0517%2FmonREL__tetris__with__P__DDQN-blue?logo=github)](https://github.com/Eddie0517/monREL_tetris_with_P_DDQN)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![HTML5 / Canvas](https://img.shields.io/badge/HTML5-Canvas%20Game-E34F26?logo=html5&logoColor=white)](index.html)

---

## 📌 1. Giới thiệu đề tài (Project Overview)

Tetris là một trong những bài toán kinh điển trong khoa học máy tính thuộc lớp độ phức tạp **NP-Complete**. Dự án này tập trung vào việc nghiên cứu, mô hình hóa toán học và áp dụng các thuật toán **Học tăng cường (Reinforcement Learning)** — trọng tâm là **Deep Q-Network (DQN / Double DQN)** kết hợp kỹ thuật trích xuất đặc trưng hình học (*Geometric Feature Representation*) để huấn luyện tác tử AI có khả năng tự động chơi Tetris đạt hiệu suất cao.

Đồng thời, dự án cung cấp một giao diện game **Cyber Tetris** theo phong cách Cyberpunk hiện đại (Canvas, Web Audio API, Glassmorphism) sẵn sàng để chơi thủ công hoặc kết nối trực quan hóa mô hình AI theo thời gian thực.

Chi tiết đề cương nghiên cứu khoa học được trình bày tại file:  
👉 **[Xem chi tiết Đề cương nghiên cứu (PROPOSAL.md)](PROPOSAL.md)**

---

## 📑 2. Mô hình hóa bài toán (MDP Formulation)

Bài toán được chuẩn hóa thành một quá trình quyết định Markov hữu hạn $\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma \rangle$:

### 2.1. Không gian trạng thái (State Space $\mathcal{S}$)
Thay vì sử dụng ma trận pixel thô, trạng thái bàn cờ sau mỗi nước đi dự kiến được mã hóa bằng vector 4 chiều đặc trưng:

$$s_t = \left[ \text{AggHeight}, \text{Holes}, \text{Bumpiness}, \text{Lines} \right]^T$$

1. **Tổng chiều cao các cột (Aggregate Height):** $\sum_{c=1}^{10} h_c$
2. **Số lượng lỗ hổng (Holes):** Số ô trống bị các khối gạch khác che phủ bên trên.
3. **Độ gồ ghề bề mặt (Bumpiness):** $\sum_{c=1}^{9} |h_c - h_{c+1}|$ (đo độ mấp mô).
4. **Số hàng dọn sạch ngay lập tức (Cleared Lines):** $0, 1, 2, 3, 4$.

### 2.2. Không gian hành động (Action Space $\mathcal{A}$)
Sử dụng **Placement-based Action Space**:
* Với mỗi khối gạch hiện tại, tác tử duyệt qua tất cả các cặp vị trí hợp lệ $(x, r)$ (với $x$ là cột thả và $r$ là góc xoay).
* Quyết định nước đi tối ưu:
  $$a^* = \arg\max_{a \in \mathcal{A}(s_t)} Q(s'(s_t, a))$$

### 2.3. Hàm thưởng (Reward Function $\mathcal{R}$)
$$\mathcal{R} = w_1 \cdot (\text{Lines})^2 - w_2 \cdot \Delta \text{Holes} - w_3 \cdot \Delta \text{Bumpiness} - w_4 \cdot \Delta \text{AggHeight} + r_{\text{alive}}$$

* **Thưởng dọn hàng:** Bình phương số hàng để khuyến khích nước đi ăn combo 4 hàng (TETRIS).
* **Phạt lỗ hổng & độ gồ ghề:** Tránh tạo các hốc kẹt không thể lấp đầy và giữ bề mặt bằng phẳng.
* **Thưởng sống sót:** $+1$ điểm mỗi bước hợp lệ.

---

## 🗂️ 3. Cấu trúc thư mục (Repository Structure)

```text
monREL_tetris_with_P_DDQN/
├── checkpoints/                                 # Lưu trữ trọng số mô hình đã huấn luyện (best_model.pth, latest_model.pth)
├── reports/                                     # Báo cáo kết quả và biểu đồ benchmark
│   ├── EVALUATION_REPORT.md                     # Báo cáo đánh giá hiệu suất mô hình và bảng chỉ số chi tiết
│   └── figures/                                 # Biểu đồ so sánh (benchmark_comparison.png, benchmark_results.json...)
├── logs/                                        # TensorBoard logs giám sát tiến trình huấn luyện
├── src/                                         # Toàn bộ mã nguồn module Reinforcement Learning (PyTorch)
│   ├── env/                                     # Môi trường mô phỏng Tetris Gym tốc độ cao (tetris_env.py)
│   ├── models/                                  # Kiến trúc mạng nơ-ron Deep Q-Network (dqn_model.py)
│   ├── agents/                                  # DQN Agent (dqn_agent.py) & Heuristic Baseline (heuristic_agent.py)
│   ├── train.py                                 # Pipeline huấn luyện tự động với Replay Buffer & Double DQN
│   ├── evaluate.py                              # Đánh giá benchmark định lượng & xuất biểu đồ khoa học
│   └── play_ai.py                               # Trực quan hóa AI chơi Tetris thời gian thực bằng Pygame
├── tools/                                       # Các công cụ sinh slide, script và phân tích checkpoint
├── audio.js                                     # Bộ tổng hợp âm thanh 8-bit & nhạc nền (Web Audio API)
├── index.html                                   # Giao diện chính game Cyber Tetris kèm chế độ AI Autoplay trên Web
├── push_to_github.bat                           # Script tự động đồng bộ mã nguồn lên GitHub (Windows CMD)
├── push_to_github.ps1                           # Script tự động đồng bộ mã nguồn lên GitHub (PowerShell)
├── requirements.txt                             # Danh sách thư viện Python phụ thuộc (PyTorch, Pygame, Matplotlib...)
├── style.css                                    # Thiết kế Cyberpunk Glassmorphism & layout tương thích thiết bị
├── tetris.js                                    # Engine game chuẩn Guideline kèm thuật toán AI Web Heuristic
├── SLIDE_THUYET_TRINH_BAO_CAO_TIEN_DO_FINAL.pptx # Slide thuyết trình báo cáo tiến độ (Bản Final)
├── KICH_BAN_THUYET_TRINH_HOAN_CHINH_FINAL.md    # Kịch bản thuyết trình chi tiết từng slide (Markdown)
├── KICH_BAN_THUYET_TRINH_HOAN_CHINH_FINAL.docx  # Kịch bản thuyết trình chi tiết từng slide (Word)
├── TRAINING_PLAN.md                             # Kế hoạch chi tiết huấn luyện mô hình RL nhiều giai đoạn
├── PROPOSAL.md                                  # Bản đề cương chi tiết đề tài nghiên cứu Reinforcement Learning
└── README.md                                    # Tài liệu hướng dẫn tổng quan & mô tả kho lưu trữ
```

---

## 🕹️ 4. Tính năng của Game Cyber Tetris

* **Chuẩn cơ chế Tetris hiện đại (Tetris Guideline):**
  * Hệ thống chọn khối **7-Bag Randomizer** công bằng.
  * Tính năng **Hold Piece** (giữ lại khối gạch).
  * Hàng chờ **Next Pieces** (hiển thị trước 3 khối tiếp theo).
  * **Ghost Piece** (bóng định vị vị trí rơi của khối gạch).
  * Cơ chế xoay hỗ trợ **Wall Kicks** cơ bản.
  * Hiệu ứng rung màn hình (*Screen Shake*) và nổ hạt neon (*Particle Explosion*) khi dọn hàng.
* **Âm thanh Arcade tích hợp:**
  * Sử dụng **Web Audio API** tạo trực tiếp âm thanh từ sóng dao động (không lo lỗi thiếu file mp3).
  * Có nhạc nền Synthwave 8-bit lặp tuần hoàn và nút bật/tắt tiện lợi.
* **Hỗ trợ đa nền tảng:**
  * Bàn phím máy tính (Desktop).
  * Phím cảm ứng ảo trên màn hình cho điện thoại / máy tính bảng (Mobile Touch Controls).

### Bảng phím tắt điều khiển:
| Thao tác | Phím bấm trên bàn phím |
| :--- | :--- |
| **Sang trái / Sang phải** | Phím mũi tên `←` `→` hoặc `A` `D` |
| **Xoay theo chiều kim đồng hồ** | Phím mũi tên `↑` hoặc `W` / `X` |
| **Xoay ngược chiều** | Phím `Z` hoặc `Ctrl` |
| **Thả rơi chậm (Soft Drop)** | Phím mũi tên `↓` hoặc `S` |
| **Thả rơi tức thì (Hard Drop)** | Phím `Space` |
| **Giữ khối gạch (Hold)** | Phím `C` hoặc `Shift` |
| **Tạm dừng / Tiếp tục** | Phím `P` hoặc `Esc` |
| **Chơi ván mới** | Phím `R` |

---

## 🚀 5. Hướng dẫn chạy thử nghiệm tại máy cục bộ (Local Run)

Bạn có thể chạy trực tiếp trò chơi trên bất kỳ trình duyệt nào:

### Cách 1: Sử dụng Python HTTP Server
```bash
# Di chuyển vào thư mục dự án
cd monREL_tetris_with_P_DDQN

# Khởi chạy máy chủ HTTP nội bộ
python -m http.server 8080
```
Mở trình duyệt và truy cập: **`http://localhost:8080`**

### Cách 2: Mở trực tiếp file HTML
Nhấp đúp chuột vào file `index.html` hoặc mở bằng trình duyệt (Chrome, Edge, Firefox, Brave...).

---

## 🤖 6. Hướng dẫn Huấn luyện & Chạy AI (RL Execution Guide)

Dự án đã tích hợp đầy đủ pipeline Học tăng cường (Reinforcement Learning) từ môi trường mô phỏng Gym, mô hình Deep Q-Network đến các công cụ trực quan hóa thời gian thực.

### 6.1. Cài đặt môi trường Python
```bash
pip install -r requirements.txt
```

### 6.2. Khởi chạy AI trực tiếp trên Trình duyệt Web (Web Autoplay)
1. Mở file [index.html](index.html) hoặc chạy qua máy chủ HTTP:
   ```bash
   python -m http.server 8080
   ```
2. Mở trình duyệt tại **`http://localhost:8080`**.
3. Nhấp nút **`🤖 BẬT AI AUTOPLAY`** ở góc phải: AI (dựa trên Heuristic Pierre Dellacherie & RL Policy) sẽ tự động tính toán thế cờ tối ưu, né hốc kẹt, làm phẳng bề mặt và dọn hàng liên tục!

---

### 6.3. Chạy giao diện Trực quan hóa Real-time bằng Pygame
Bạn có thể theo dõi AI chơi game trực quan với bảng thông số đánh giá feature theo thời gian thực:
```bash
# Chạy với thuật toán Baseline Heuristic (Dellacherie)
python src/play_ai.py --agent heuristic --fps 20

# Chạy với mô hình Deep Q-Network đã huấn luyện
python src/play_ai.py --agent dqn --model-path checkpoints/best_model.pth --fps 20
```
* **Phím tắt trong cửa sổ Pygame:**
  * `Phím cách (Space)`: Tạm dừng / Tiếp tục.
  * `Mũi tên Lên / Xuống (↑ / ↓)`: Tăng / Giảm tốc độ khung hình (1 – 120 FPS).
  * `Phím R`: Chơi lại ván mới.
  * `Phím H`: Chuyển sang tác tử Heuristic.
  * `Phím D`: Chuyển sang tác tử DQN.

---

### 6.4. Huấn luyện mô hình Double Deep Q-Network (Training)
Chạy script huấn luyện tự động với Experience Replay và Target Network:
```bash
# Huấn luyện nhanh 200 episodes
python src/train.py --episodes 200 --batch-size 128 --decay-episodes 150

# Huấn luyện quy mô lớn đầy đủ (2000 episodes) kèm TensorBoard
python src/train.py --episodes 2000 --batch-size 512 --decay-episodes 1200
```
* **Theo dõi quá trình huấn luyện bằng TensorBoard:**
  ```bash
  tensorboard --logdir logs
  ```
  Truy cập `http://localhost:6006` để xem đồ thị Loss, Cleared Lines, Score, và Epsilon.
* Trọng số mô hình tốt nhất được tự động lưu tại `checkpoints/best_model.pth`.

---

### 6.5. Đánh giá Benchmark & Xuất biểu đồ khoa học (Evaluation)
Chạy thử nghiệm so sánh định lượng giữa **Random Agent vs Heuristic Baseline vs DDQN Agent**:
```bash
python src/evaluate.py --games 10 --output-dir reports/figures
```
* Script tự động xuất bảng so sánh thống kê (Mean Lines, Max Lines, Mean Score).
* Tự động lưu biểu đồ so sánh vào: `reports/figures/benchmark_comparison.png`.
* Lưu dữ liệu JSON chi tiết vào: `reports/figures/benchmark_results.json`.

---

## 📦 7. Lộ trình phát triển đề tài (Implementation Roadmap)

1. [x] **Xây dựng đề cương nghiên cứu khoa học:** Hoàn thành [`PROPOSAL.md`](PROPOSAL.md).
2. [x] **Giao diện game Cyberpunk Arcade:** HTML5 Canvas, Web Audio API, Neon effects ([`index.html`](index.html)).
3. [x] **Môi trường Tetris Gym tốc độ cao:** [`src/env/tetris_env.py`](src/env/tetris_env.py) trích xuất 4 đặc trưng hình học.
4. [x] **Baseline Heuristic Agent:** [`src/agents/heuristic_agent.py`](src/agents/heuristic_agent.py) thuật toán Dellacherie.
5. [x] **Kiến trúc Deep Q-Network & Double DQN:** [`src/models/dqn_model.py`](src/models/dqn_model.py) & [`src/agents/dqn_agent.py`](src/agents/dqn_agent.py).
6. [x] **Pipeline Huấn luyện & Checkpoint:** [`src/train.py`](src/train.py) hỗ trợ TensorBoard & Replay Buffer.
7. [x] **Hệ thống Đánh giá Benchmark & Đồ thị:** [`src/evaluate.py`](src/evaluate.py) xuất biểu đồ Boxplot/Barchart.
8. [x] **Demo Trực quan hóa:** Desktop Pygame [`src/play_ai.py`](src/play_ai.py) và Web Autoplay trực tiếp trên trình duyệt.

---

## 👤 8. Tác giả & Đóng góp
* **Họ và tên:** Eddie / Khang
* **Kho lưu trữ:** [github.com/Eddie0517/monREL_tetris_with_P_DDQN](https://github.com/Eddie0517/monREL_tetris_with_P_DDQN)
* **Môn học:** Reinforcement Learning (REL)

*Giữ bản quyền mã nguồn theo giấy phép MIT.*

