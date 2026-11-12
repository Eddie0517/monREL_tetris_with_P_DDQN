# Reward / Hyper-parameter Sweep – P-DDQN

Train: 2000 episodes/run (trần 1500 khối/episode). Eval: 100 games, trần 1000 bước, eval seed 12345 (mọi cấu hình gặp cùng chuỗi khối gạch).
Metric theo Table 1 của report. Δ Lines tính so với `baseline`.

## Checkpoint `best_model.pth`

| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `baseline` | reward | Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10 | 3 | 298.2 ± 101.7 (±60.9 giữa seed) | 323.5 | 399 | 24174.9 | 775.3 | 81.8 | 52.0/100 | — | 60.3 |
| `gamma_095` | hparam | Discount gamma=0.95 (mặc định 0.99) | 3 | 395.2 ± 15.2 (±2.7 giữa seed) | 397.7 | 399 | 20421.9 | 995.0 | 51.7 | 98.7/100 | +97.1 | 95.2 |
| `lr_5e-4` | hparam | Learning rate 5e-4 (mặc định 1e-3) | 3 | 124.0 ± 58.3 (±132.7 giữa seed) | 147.0 | 219 | 12347.0 | 343.0 | 73.8 | 19.7/100 | -174.2 | 19.1 |
| `target_5` | hparam | Đồng bộ target net mỗi 5 ep (mặc định 10) | 3 | 331.7 ± 95.6 (±34.0 giữa seed) | 370.8 | 399 | 26750.7 | 853.4 | 79.4 | 65.0/100 | +33.5 | 72.9 |
| `target_25` | hparam | Đồng bộ target net mỗi 25 ep | 3 | 327.3 ± 85.3 (±64.9 giữa seed) | 343.5 | 399 | 21830.9 | 839.6 | 65.0 | 68.0/100 | +29.1 | 86.1 |
| `eps_decay_600` | hparam | Epsilon giảm trong 600 ep (mặc định 1200) | 3 | 351.1 ± 82.4 (±19.8 giữa seed) | 394.3 | 399 | 25216.7 | 897.1 | 71.8 | 73.7/100 | +52.9 | 121.4 |
| `hidden_128` | hparam | MLP 128 neuron/lớp (mặc định 64) | 3 | 389.2 ± 25.2 (±11.2 giữa seed) | 397.0 | 399 | 24083.5 | 982.3 | 62.2 | 96.3/100 | +91.0 | 130.8 |
| `batch_256` | hparam | Batch 256 (mặc định 512) | 3 | 263.4 ± 93.6 (±80.0 giữa seed) | 266.5 | 395 | 25369.3 | 692.9 | 92.5 | 40.0/100 | -34.8 | 45.6 |

## Checkpoint `latest_model.pth`

| Config | Nhóm | Thay đổi | Seeds | Lines (Mean ± Std) | Median | Max | Mean Score | Placements | Pts/Line | Cap hits | Δ Lines | Train (phút) |
|---|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| `baseline` | reward | Cấu hình report: alive=1, lines=10, holes=1.5, bump=0.5, height=0.5, over=10 | 3 | 307.5 ± 89.2 (±73.5 giữa seed) | 324.8 | 398 | 24255.9 | 795.7 | 80.7 | 57.7/100 | — | 60.3 |
| `gamma_095` | hparam | Discount gamma=0.95 (mặc định 0.99) | 3 | 130.8 ± 12.4 (±184.9 giữa seed) | 132.7 | 134 | 7398.7 | 344.8 | 46.5 | 32.7/100 | -176.7 | 95.2 |
| `lr_5e-4` | hparam | Learning rate 5e-4 (mặc định 1e-3) | 3 | 132.4 ± 59.2 (±135.3 giữa seed) | 147.8 | 259 | 10283.3 | 365.6 | 63.4 | 20.7/100 | -175.2 | 19.1 |
| `target_5` | hparam | Đồng bộ target net mỗi 5 ep (mặc định 10) | 3 | 365.9 ± 71.5 (±6.1 giữa seed) | 392.7 | 399 | 28806.7 | 935.2 | 78.7 | 83.7/100 | +58.4 | 72.9 |
| `target_25` | hparam | Đồng bộ target net mỗi 25 ep | 3 | 345.5 ± 60.9 (±62.8 giữa seed) | 350.0 | 399 | 22810.8 | 882.4 | 64.5 | 76.0/100 | +37.9 | 86.1 |
| `eps_decay_600` | hparam | Epsilon giảm trong 600 ep (mặc định 1200) | 3 | 371.5 ± 70.6 (±10.0 giữa seed) | 394.7 | 399 | 27485.9 | 945.6 | 74.1 | 88.0/100 | +63.9 | 121.4 |
| `hidden_128` | hparam | MLP 128 neuron/lớp (mặc định 64) | 3 | 377.9 ± 65.2 (±3.2 giữa seed) | 395.0 | 399 | 27713.3 | 959.7 | 73.3 | 92.3/100 | +70.4 | 130.8 |
| `batch_256` | hparam | Batch 256 (mặc định 512) | 3 | 307.0 ± 86.4 (±70.4 giữa seed) | 327.8 | 397 | 27524.5 | 795.4 | 91.5 | 57.7/100 | -0.6 | 45.6 |
