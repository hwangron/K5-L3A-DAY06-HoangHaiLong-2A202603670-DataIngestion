# Quyết định chọn cấu hình (trên dev, trước khi chạy test)

Thời điểm: 2026-11-13, sau `evaluate --split dev`. Lúc này test chưa chạy lần nào.

| Strategy | Dev Hit@1 | Dev Evidence Hit@3 | Chunk |
|---|---|---|---|
| A | 9/18 | 14/18 | 226 |
| B | 8/18 | 16/18 | 144 |
| C | 9/18 | 16/18 | 144 |

Áp tiêu chí đã chốt trong `benchmark/README.md`:
1. Hit@3: B và C bằng nhau (16/18).
2. Hit@1: C (9) > B (8).

**Chọn C.** Không đổi tham số hay benchmark sau bước này.
