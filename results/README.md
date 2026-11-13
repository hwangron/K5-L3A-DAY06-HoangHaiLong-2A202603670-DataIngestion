# Results

| File | Nội dung |
|---|---|
| `benchmark_validation.json` | Kết quả kiểm chứng benchmark: số câu và 25/25 evidence có trên trang gold |
| `ingest_runs.jsonl` | 2 lần ingest. Mỗi lần ghi số chunk, độ dài, token, chi phí, thời gian. Lần 2 chứng minh nạp lại không trùng |
| `reingest_test.txt` | Thử tài liệu đổi: chunk cũ bị xóa (`deleted_obsolete`) |
| `metrics_dev.json`, `metrics_test.json` | Hit@1, Evidence Hit@3, filter tuân thủ, câu trượt, chi phí embed query |
| `selection_decision.md` | Chọn cấu hình trên dev trước khi chạy test |
| `traces/{A,B,C}_{dev,test}.jsonl` | Trace đầy đủ top-3: câu hỏi, filter, chunk_id, text, score, metadata, nhãn hit |
| `audit/coherence_samples.md` | 10 vị trí mẫu và chunk chứa vị trí đó (A, B; C dùng chung chunk với B) |
| `audit/coherence_labels.csv` | Nhãn coherence 0–2 kèm lý do |
| `audit/grounding_labels.csv` | Nhãn grounding 0–2 cho 7 câu test × 3 cấu hình |
| `audit/metadata_check.csv` | Kiểm tra metadata của 21 bản ghi top-3 test cho mỗi cấu hình |

Người chấm nhãn: AI assistant (Claude) đọc từng chunk và chấm theo thang trong GUIDE.md. Học viên cần đọc lại để xác nhận. Vì chỉ có một người chấm nên có nguy cơ thiên lệch.
