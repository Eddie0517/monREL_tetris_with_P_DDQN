# Reward / Hyper-parameter Sweep – P-DDQN

Train: 2000 episodes/run (trần 1500 khối/episode). Eval: 100 games, trần 1000 bước, eval seed 12345 (mọi cấu hình gặp cùng chuỗi khối gạch).
Metric theo Table 1 của report. Δ Lines tính so với `baseline`.

## Checkpoint `best_model.pth`

| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `baseline` | reward | Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10 | 3 | 378.7 ± 61.5 (±7.1 giữa seed) | 396.0 | 399 | 28133.1 | 960.2 | 74.3 | 93.0/100 | — | 68.3 |
| `qlearning` | target | Q-learning: max_a' U⁻(s'_a') | 3 | 349.6 ± 77.2 (±49.9 giữa seed) | 378.5 | 399 | 21791.7 | 889.2 | 61.0 | 78.0/100 | -29.1 | 77.1 |
| `double_q` | target | Double Q: U⁻(argmax_a' U_online) | 3 | 319.0 ± 84.0 (±70.7 giữa seed) | 326.2 | 398 | 25782.1 | 820.7 | 87.8 | 62.3/100 | -59.7 | 81.1 |
| `expected_sarsa` | target | Expected SARSA: (1-ε)·max + ε·mean | 3 | 397.4 ± 1.3 (±0.5 giữa seed) | 397.7 | 399 | 20719.0 | 1000.0 | 52.1 | 100.0/100 | +18.7 | 123.0 |
| `sarsa_1050` | target | SARSA (gốc), 1050 ep | 3 | 3.1 ± 2.7 (±0.2 giữa seed) | 2.7 | 13 | 187.7 | 49.2 | 60.6 | 0.0/100 | -375.6 | 3.4 |
| `qlearning_1050` | target | Q-learning, 1050 ep | 3 | 137.9 ± 19.2 (±177.1 giữa seed) | 140.0 | 161 | 7477.1 | 374.7 | 63.6 | 31.7/100 | -240.8 | 4.2 |
| `double_q_1050` | target | Double Q, 1050 ep | 3 | 96.0 ± 44.8 (±132.3 giữa seed) | 125.7 | 139 | 6591.9 | 276.7 | 65.7 | 16.0/100 | -282.6 | 4.2 |
| `expected_sarsa_1050` | target | Expected SARSA, 1050 ep | 3 | 273.7 ± 8.9 (±173.2 giữa seed) | 273.0 | 296 | 13364.9 | 702.7 | 49.6 | 66.3/100 | -105.0 | 4.8 |

## Checkpoint `latest_model.pth`

| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `baseline` | reward | Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10 | 3 | 266.1 ± 48.0 (±172.3 giữa seed) | 263.8 | 378 | 19855.0 | 685.7 | 74.4 | 64.0/100 | — | 68.3 |
| `qlearning` | target | Q-learning: max_a' U⁻(s'_a') | 3 | 260.1 ± 18.9 (±183.2 giữa seed) | 264.7 | 273 | 17312.3 | 667.6 | 59.6 | 63.7/100 | -6.0 | 77.1 |
| `double_q` | target | Double Q: U⁻(argmax_a' U_online) | 3 | 322.9 ± 88.9 (±54.1 giữa seed) | 340.7 | 398 | 26620.1 | 831.9 | 84.4 | 62.0/100 | +56.8 | 81.1 |
| `expected_sarsa` | target | Expected SARSA: (1-ε)·max + ε·mean | 3 | 260.3 ± 19.9 (±183.9 giữa seed) | 263.7 | 267 | 18760.4 | 670.8 | 62.5 | 65.0/100 | -5.9 | 123.0 |
| `sarsa_1050` | target | SARSA (gốc), 1050 ep | 3 | 3.3 ± 2.8 (±0.1 giữa seed) | 2.7 | 11 | 185.7 | 49.6 | 56.7 | 0.0/100 | -262.8 | 3.4 |
| `qlearning_1050` | target | Q-learning, 1050 ep | 3 | 137.8 ± 22.1 (±177.4 giữa seed) | 139.7 | 175 | 7891.5 | 372.8 | 63.2 | 31.7/100 | -128.3 | 4.2 |
| `double_q_1050` | target | Double Q, 1050 ep | 3 | 96.0 ± 44.8 (±132.3 giữa seed) | 125.7 | 140 | 6600.1 | 276.6 | 69.5 | 16.0/100 | -170.1 | 4.2 |
| `expected_sarsa_1050` | target | Expected SARSA, 1050 ep | 3 | 274.9 ± 17.9 (±169.7 giữa seed) | 274.7 | 311 | 13605.9 | 706.1 | 49.8 | 66.3/100 | +8.8 | 4.8 |
