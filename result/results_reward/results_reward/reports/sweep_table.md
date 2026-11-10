# Reward / Hyper-parameter Sweep – P-DDQN

Train: 2000 episodes/run (trần 1500 khối/episode). Eval: 100 games, trần 1000 bước, eval seed 12345 (mọi cấu hình gặp cùng chuỗi khối gạch).
Metric theo Table 1 của report. Δ Lines tính so với `baseline`.

## Checkpoint `best_model.pth`

| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `baseline` | reward | Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10 | 3 | 298.2 ± 101.7 (±60.9 giữa seed) | 323.5 | 399 | 24174.9 | 775.3 | 81.8 | 52.0/100 | — | 51.8 |
| `lines_x2` | reward | Thưởng dọn hàng ×2 (lines=20) | 3 | 312.2 ± 88.4 (±88.9 giữa seed) | 307.7 | 398 | 22556.9 | 802.6 | 73.6 | 65.0/100 | +14.0 | 76.2 |
| `lines_half` | reward | Thưởng dọn hàng ×0.5 (lines=5) | 3 | 335.7 ± 98.6 (±27.3 giữa seed) | 391.3 | 397 | 31806.6 | 863.9 | 96.3 | 70.3/100 | +37.5 | 55.8 |
| `holes_x2` | reward | Phạt lỗ ×2 (holes=3.0) | 3 | 348.8 ± 90.3 (±28.6 giữa seed) | 392.8 | 399 | 24668.4 | 890.7 | 70.6 | 74.0/100 | +50.6 | 40.9 |
| `holes_half` | reward | Phạt lỗ ×0.5 (holes=0.75) | 3 | 354.6 ± 71.9 (±35.7 giữa seed) | 392.2 | 399 | 25105.1 | 906.1 | 71.9 | 78.0/100 | +56.4 | 85.3 |
| `bump_x2` | reward | Phạt gồ ghề ×2 (bump=1.0) | 3 | 382.6 ± 50.5 (±5.9 giữa seed) | 395.2 | 399 | 27770.5 | 971.9 | 72.6 | 93.3/100 | +84.5 | 78.6 |
| `bump_0` | reward | Bỏ phạt gồ ghề (bump=0) | 3 | 344.2 ± 78.3 (±43.7 giữa seed) | 380.3 | 398 | 27218.1 | 884.0 | 79.3 | 73.0/100 | +46.1 | 55.0 |
| `height_x2` | reward | Phạt chiều cao ×2 (height=1.0) | 3 | 365.7 ± 67.9 (±23.4 giữa seed) | 392.8 | 399 | 26463.1 | 932.5 | 72.8 | 83.3/100 | +67.5 | 81.6 |
| `height_0` | reward | Bỏ phạt chiều cao (height=0) | 3 | 381.4 ± 47.8 (±6.3 giữa seed) | 393.3 | 398 | 29195.6 | 970.7 | 76.5 | 92.3/100 | +83.2 | 76.1 |
| `alive_0` | reward | Bỏ thưởng sống sót (alive=0) | 3 | 368.5 ± 66.2 (±20.3 giữa seed) | 394.0 | 399 | 27337.7 | 939.2 | 74.4 | 86.3/100 | +70.3 | 74.3 |
| `gameover_50` | reward | Phạt thua nặng (game_over=50) | 3 | 375.1 ± 54.1 (±22.0 giữa seed) | 395.0 | 399 | 27858.5 | 953.0 | 74.5 | 88.0/100 | +76.9 | 57.8 |
| `lines_only` | reward | Chỉ thưởng dọn hàng + sống (bỏ hết shaping) | 3 | 370.9 ± 68.7 (±9.6 giữa seed) | 395.0 | 399 | 25326.7 | 943.2 | 68.5 | 85.7/100 | +72.7 | 59.4 |

## Checkpoint `latest_model.pth`

| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `baseline` | reward | Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10 | 3 | 307.5 ± 89.2 (±73.5 giữa seed) | 324.8 | 398 | 24255.9 | 795.7 | 80.7 | 57.7/100 | — | 51.8 |
| `lines_x2` | reward | Thưởng dọn hàng ×2 (lines=20) | 3 | 235.8 ± 60.4 (±167.8 giữa seed) | 262.7 | 268 | 16665.6 | 609.7 | 60.5 | 53.7/100 | -71.7 | 76.2 |
| `lines_half` | reward | Thưởng dọn hàng ×0.5 (lines=5) | 3 | 321.8 ± 83.0 (±75.0 giữa seed) | 326.2 | 397 | 26750.6 | 829.0 | 87.1 | 65.0/100 | +14.3 | 55.8 |
| `holes_x2` | reward | Phạt lỗ ×2 (holes=3.0) | 3 | 383.8 ± 52.3 (±6.1 giữa seed) | 395.3 | 399 | 27439.1 | 972.9 | 71.5 | 93.7/100 | +76.3 | 40.9 |
| `holes_half` | reward | Phạt lỗ ×0.5 (holes=0.75) | 3 | 363.6 ± 75.8 (±20.3 giữa seed) | 393.7 | 399 | 27082.0 | 926.6 | 74.6 | 85.0/100 | +56.0 | 85.3 |
| `bump_x2` | reward | Phạt gồ ghề ×2 (bump=1.0) | 3 | 384.1 ± 44.0 (±0.9 giữa seed) | 395.0 | 399 | 29065.1 | 976.0 | 75.7 | 93.7/100 | +76.6 | 78.6 |
| `bump_0` | reward | Bỏ phạt gồ ghề (bump=0) | 3 | 349.9 ± 83.4 (±34.4 giữa seed) | 393.3 | 399 | 25693.3 | 893.5 | 73.7 | 78.0/100 | +42.4 | 55.0 |
| `height_x2` | reward | Phạt chiều cao ×2 (height=1.0) | 3 | 373.4 ± 64.7 (±13.3 giữa seed) | 395.0 | 399 | 27958.1 | 948.9 | 74.9 | 89.7/100 | +65.8 | 81.6 |
| `height_0` | reward | Bỏ phạt chiều cao (height=0) | 3 | 369.2 ± 65.0 (±8.3 giữa seed) | 394.0 | 399 | 27979.9 | 942.1 | 75.8 | 83.0/100 | +61.6 | 76.1 |
| `alive_0` | reward | Bỏ thưởng sống sót (alive=0) | 3 | 356.6 ± 77.9 (±26.5 giữa seed) | 392.7 | 399 | 27463.3 | 911.6 | 77.2 | 81.0/100 | +49.0 | 74.3 |
| `gameover_50` | reward | Phạt thua nặng (game_over=50) | 3 | 251.9 ± 37.3 (±178.4 giữa seed) | 263.3 | 266 | 19047.5 | 645.5 | 63.8 | 60.3/100 | -55.6 | 57.8 |
| `lines_only` | reward | Chỉ thưởng dọn hàng + sống (bỏ hết shaping) | 3 | 96.1 ± 35.8 (±135.8 giữa seed) | 107.3 | 134 | 6326.4 | 262.9 | 48.6 | 13.3/100 | -211.4 | 59.4 |
