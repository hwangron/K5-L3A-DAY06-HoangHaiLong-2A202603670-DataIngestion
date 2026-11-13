# Day 06 · Data Ingestion Engineering

## Bài làm: cách chạy lại

**Corpus:** OpenStax *Calculus Volume 1*, các mục 2.3, 2.4, 3.1, 3.2 (67 trang PDF). **Embedding:** OpenAI `text-embedding-3-small` (1536 chiều). **Vector store:** PostgreSQL 16 + pgvector 0.8.7 (Docker), cosine, exact search.

Chạy từ thư mục `starter/` (Windows PowerShell; Python 3.14):

```bash
python -m venv .venv; .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env        # điền OPENAI_API_KEY
docker compose -p day6_student_starter up -d --wait
mkdir data/raw; curl.exe -L -o data/raw/CalculusVolume1.pdf https://assets.openstax.org/oscms-prodcms/media/documents/CalculusVolume1-OP.pdf
python -m src.run prepare          # PDF -> ../data/pages.jsonl, ../data/manifest.json
python -m src.run validate         # kiểm benchmark/questions.json
python -m src.run ingest           # chunk A/B/C, embed, lưu pgvector (chạy lại không trùng)
python -m src.run evaluate --split dev
python -m src.run evaluate --split test
python -m src.run audit-prep       # mẫu coherence + kiểm metadata
```

Kiểm tra database: `python scripts/check_setup.py` (cần `psycopg`) hoặc `python scripts/check_setup_pg8000.py` (cùng chức năng, dùng khi `psycopg` bị chặn).

- **Driver:** pipeline dùng `pg8000` thay `psycopg`, vì Windows Smart App Control chặn DLL của `psycopg-binary` trên máy làm bài.
- **Vị trí file:** code ở [starter/src/](starter/src/), cấu hình ở [starter/config.json](starter/config.json), benchmark ở [benchmark/](benchmark/), kết quả ở [results/](results/), báo cáo ở [report/individual/](report/individual/).
- **Chi phí:** khoảng $0,0013 cho toàn bộ embedding (62,7k token).

---

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

## Bắt đầu nhanh

Dùng [starter PostgreSQL + pgvector](starter/README.md) để dựng database và hoàn thiện các hàm TODO, hoặc tự chọn vector store tương đương. Starter chỉ là khung: **bạn tự hiện thực pipeline và benchmark**.

## 1. Xây pipeline

![Đọc tài liệu, chuẩn hóa, chia chunk, tạo vector, lưu và kiểm tra](assets/ingestion-pipeline.svg)

Chọn tài liệu được phép sử dụng; giữ **ID tài liệu, nguồn, trang/vị trí** và metadata phù hợp. Dùng embedding model thật qua API hoặc chạy local; lưu và truy xuất bằng pgvector, Qdrant, Chroma hoặc một store tương đương.

## 2. So sánh và đánh giá

![Ba chiến lược được đánh giá trên cùng corpus và benchmark dev/test](assets/benchmark-workflow.svg)

Dùng cùng dữ liệu, model và câu hỏi cho cả ba cấu hình. Tách **15 câu dev / 5 câu test** trước khi chạy; chọn cấu hình trên dev, rồi đánh giá test sau khi cố định. Mỗi câu hỏi cần có đoạn bằng chứng và trang nguồn; thiết kế bộ câu hỏi và đánh giá theo [BENCHMARK.md](BENCHMARK.md).

Đánh giá theo năm khía cạnh: **độ chính xác truy xuất**, **tính mạch lạc của chunk**, **tính hữu dụng của metadata**, **chất lượng grounding** và **tác động của chiến lược dữ liệu**. Giải thích lựa chọn bằng kết quả, ví dụ lỗi và các đánh đổi.

## 3. Chuẩn bị bài nộp

1. Chạy pipeline và lưu cấu hình, kết quả top-3, trace cùng nhãn đánh giá thủ công.
2. Điền [thông tin học viên](STUDENT.md), [nhật ký thí nghiệm](artifacts/experiment_log.csv) và bản sao [mẫu báo cáo cá nhân](report/individual/MSSV_HoTen.md).
3. Kiểm tra mã nguồn, cách chạy, manifest dữ liệu và checklist trong [SUBMISSION.md](SUBMISSION.md).

## Tài liệu hướng dẫn

| Bạn cần tìm | Tài liệu |
|---|---|
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |

[data/format-example.json](data/format-example.json) chỉ minh họa định dạng, không phải corpus đủ điều kiện. Phần xử lý và benchmark do bạn tự hiện thực; không bắt buộc xây chatbot.
