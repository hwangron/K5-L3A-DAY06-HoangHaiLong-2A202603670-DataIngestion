# Benchmark

File: `questions.json`, gồm 25 câu: 18 dev và 7 test. Bộ câu được chốt ngày 2026-11-13, trước khi chạy truy xuất lần nào.

- **Trường của mỗi câu:** `id`, `split`, `type`, `question`, `expected_answer`, `gold_source_id`, `gold_page` (trang PDF vật lý), `evidence_quote`, `filter`. Có thể thêm `alternatives` khi câu có nhiều evidence hợp lệ.
- **Loại câu:** direct 8, paraphrase 4, condition 8, filter 5.
- **Câu có filter:** q12, q22, q23, q24, q25. Trong đó q12 và q23 thuộc test. Filter được hiểu là phạm vi người học đang ôn, do người dùng cung cấp trước khi truy xuất (ví dụ "đang học chương 3"). Filter không lấy từ đáp án. Cấu hình C chỉ áp filter cho 5 câu này; các câu còn lại C chạy không filter.
- **Cách chia dev/test:** chọn tay sao cho test có đủ cả 4 mục (2.3: q09; 2.4: q12, q14, q16; 3.1: q19, q20; 3.2: q23). Cả hai split lấy từ cùng một cuốn sách, nên có nguy cơ rò rỉ: dev và test dùng chung văn phong và chủ đề gần nhau.
- **Kiểm chứng evidence:** lệnh `python -m src.run validate` kiểm tra từng `evidence_quote` có nằm trong text đã chuẩn hóa của trang gold hay không, cùng với số lượng câu tối thiểu và giá trị filter. Kết quả lưu ở `results/benchmark_validation.json` (0 lỗi).
- **Quy ước text:** quote giữ nguyên text sau khi pypdf trích xuất, kể cả các chỗ bị dính chữ như `ofa`, `atb`. Đây là text thật mà chunk chứa.

## Tiêu chí chọn chiến lược (chốt trước khi xem test)

1. Evidence Hit@3 trên dev cao nhất.
2. Nếu bằng nhau thì so Hit@1 trên dev.
3. Nếu vẫn bằng nhau thì chọn cấu hình có ít chunk hơn (ít tài nguyên hơn).

Test chỉ chạy một lần, sau khi đã chọn cấu hình trên dev.
