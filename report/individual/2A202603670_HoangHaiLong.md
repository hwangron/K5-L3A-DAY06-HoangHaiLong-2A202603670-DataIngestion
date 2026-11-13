# Báo cáo cá nhân — Day 6

## Dữ liệu và pipeline
- Chủ đề, nguồn/quyền, số trang và quy tắc tính trang: Giải tích. Nguồn là OpenStax *Calculus Volume 1* (2018), giấy phép CC BY-NC-SA 4.0 (ghi ở trang 4 của PDF). Lấy 4 mục 2.3, 2.4, 3.1, 3.2, gồm 67 trang PDF (168–186, 187–201, 222–239, 240–254): 53 trang lý thuyết và 14 trang bài tập. Một trang được tính nếu có ít nhất 200 ký tự sau chuẩn hóa. Không lấy bìa, mục lục, glossary. Chi tiết trong [data/manifest.json](../../data/manifest.json).
- Chuẩn hóa, lỗi và giới hạn: Dùng pypdf. Chuẩn hóa NFKC, bỏ glyph ngoặc lớn (U+239B–23AD), header/footer lặp lại và số đếm lề. Không có trang rỗng, không cần OCR. Giới hạn: công thức toán bị dàn phẳng (`x2` nghĩa là x²), một số từ bị dính (`ofa`, `atb`), hình chỉ còn chú thích. Các lỗi này ghi trong `known_issues` của manifest.
- Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí: OpenAI `text-embedding-3-small`, 1536 chiều, SDK `openai` 3.50.0. Query và document embed cùng một cách, không có prefix. Store là PostgreSQL 16.16 + pgvector 0.8.7 (Docker `pgvector/pgvector:0.8.7-pg16`), driver `pg8000` 1.31.6. Metric cosine (`<=>`), exact search, không dùng index. Lệnh chạy xem README. Chi phí ingest 62.668 token ≈ $0,00125; query 471 token ≈ $0,00001.
- Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn: Bắt buộc có `document_id`, `source`, `page` (trang PDF vật lý). Bổ sung:
  - `printed_page`: lấy từ header của trang.
  - `chapter`, `section`, `section_title`: lấy từ bookmark (outline) của PDF.
  - `page_type` (text/exercises): lấy từ heading "X.Y EXERCISES".
  - `char_start`/`char_end`: vị trí chunk trong trang.

  Trường lọc là `chapter` và `section`. Lý do: người học ôn theo mục, và cùng một khái niệm (limit, continuity, velocity) xuất hiện ở nhiều chương.

## Cấu hình và benchmark
- A / B / C (tham số cụ thể, khác biệt duy nhất B–C):
  - A: cửa sổ cố định 500 ký tự, overlap 50, chia trong từng trang.
  - B: chia theo cấu trúc (heading, Example, Theorem, Definition, Proof), tối đa 1000 ký tự, chỉ bắt đầu chunk mới khi chunk hiện tại đã ≥ 250 ký tự; mảnh < 125 ký tự gộp vào chunk bên cạnh.
  - C: giống hệt B (cùng chunk, cùng vector), chỉ thêm filter SQL theo `chapter`/`section` khi câu hỏi có filter.
  - A–B chỉ khác cách chunk; B–C chỉ khác filter.
- ≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence: 25 câu (18 dev, 7 test), chốt trước khi chạy. Có 5 câu filter (q12, q22–q25), trong đó q12 và q23 thuộc test. Lệnh `validate` kiểm tra cả 25 evidence đều nằm trên trang gold sau chuẩn hóa, và mọi giá trị filter đều có trong metadata. Chi tiết trong [benchmark/README.md](../../benchmark/README.md).
- Tiêu chí chọn chiến lược đã chốt trước khi xem test: Dev Hit@3 cao nhất, sau đó Hit@1, sau đó ít chunk hơn. Kết quả là chọn C, ghi ở [results/selection_decision.md](../../results/selection_decision.md).

## Kết quả
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
|---|---|---|---|---|---|---|
| A | dev | 9/18 | 14/18 | 226 | ingest 4,06 s; search 0,08 s | $0,000657 (ingest) |
| A | test | 4/7 | 7/7 | 226 | search 0,03 s | dùng chung query |
| B | dev | 8/18 | 16/18 | 144 | ingest 1,85 s; search 0,07 s | $0,000596 (ingest) |
| B | test | 4/7 | 7/7 | 144 | search 0,03 s | dùng chung query |
| C | dev | 9/18 | 16/18 | 144 | ingest 0,49 s (dùng lại vector B); search 0,08 s | $0 |
| C | test | 4/7 | 7/7 | 144 | search 0,02 s | dùng chung query |

| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|
| A | 0,8 (10) | 21/21 | test 2/2; dev 1/3 | 0/0/7, 2,0 |
| B | 1,8 (10) | 21/21 | test 2/2; dev 2/3 | 0/0/7, 2,0 |
| C | 1,8 (10, chung chunk với B) | 21/21 | test 2/2; dev 3/3 | 0/0/7, 2,0 |

Đường dẫn trace, nhãn thủ công và cách chọn mẫu:
- Trace: [results/traces/](../../results/traces/).
- Nhãn: [coherence_labels.csv](../../results/audit/coherence_labels.csv), [grounding_labels.csv](../../results/audit/grounding_labels.csv), [metadata_check.csv](../../results/audit/metadata_check.csv).
- Cách chọn mẫu coherence: lấy 10 trang lý thuyết cách đều nhau trong danh sách trang đã sắp xếp; vị trí là ký tự giữa trang. Mẫu được chọn theo quy tắc trước khi xem điểm.
- Grounding: chấm 7 câu test × top-3.
- Metadata: kiểm 21 bản ghi mỗi cấu hình. Text chunk phải có trên đúng trang PDF, và section/chapter/page_type phải khớp outline. Ngoài ra tự so `printed_page` với footer cho 3 trang.
- Ở A và B, "filter tuân thủ" chỉ đo xem top-3 có nằm trong phạm vi hay không, vì hai cấu hình này không lọc.

## Phân tích và kết luận
- So sánh A–B và B–C; 2 ví dụ sai có ID câu và nguồn:
  - **A→B:** dev Hit@3 tăng 14→16, Hit@1 giảm 9→8, số chunk giảm 226→144, coherence tăng 0,8→1,8. Test không đổi (7/7).
  - **B→C:** filter chỉ đổi kết quả ở q24. Dev Hit@1 tăng 8→9 và filter tuân thủ tăng 2/3→3/3. Trên test, 2 câu filter vốn đã nằm đúng phạm vi nên không thay đổi.
  - **Sai 1 — q21 (A, trang 235):** evidence "Since … P′(10,000) > 0 … should increase production" bị cắt qua 2 chunk fixed-size. Chunk r3 chỉ còn nửa sau nên bị tính trượt. B giữ trọn câu này trong một chunk.
  - **Sai 2 — q06 (B/C, trang 176):** Example 2.21 bắt đầu ở trang 175 (r1) nhưng lời giải ở trang 176. Vì B chia chunk trong từng trang nên trang gold không vào top-3.
- Chiến lược chọn, đánh đổi, điều kiện áp dụng: Chọn C theo tiêu chí đã chốt. Chunk theo cấu trúc cho ít chunk hơn, dễ đọc hơn, và giữ trọn evidence. Đổi lại cần heuristic heading riêng cho loại sách này. Filter chỉ có ích khi người dùng cho biết phạm vi trước, và khi khái niệm lặp lại ở nhiều chương. Nếu không có filter thì C giống hệt B.
- Hạn chế của dữ liệu, nhãn, test nhỏ, đo thời gian/chi phí:
  - Chỉ có một cuốn sách, nên dev và test có nguy cơ rò rỉ chủ đề.
  - Test có 7 câu và đều dễ (Hit@3 = 7/7 ở cả ba), nên không phân biệt được cấu hình. Chênh 1–2 câu trên dev không có ý nghĩa thống kê.
  - Nhãn coherence và grounding do AI assistant (Claude) chấm, chỉ một người chấm, học viên cần xem lại.
  - Thời gian ingest đo một lần và gồm cả độ trễ mạng của API.
  - Chunk không vượt qua ranh giới trang.
  - Công thức toán bị dàn phẳng.
  - Có dùng AI (Claude Code) để viết code và chạy thử; kết quả được kiểm bằng lệnh `validate`, trace và đọc chunk.
- Nếu làm lại hoặc mở rộng, cải tiến gì?
  - Cho chunk B nối qua ranh giới trang và lưu danh sách trang của chunk.
  - Lấy text từ bản HTML của OpenStax để giữ công thức.
  - Làm bộ test lớn hơn và khó hơn, có nhiều câu filter thật sự mơ hồ.
  - Thử hybrid BM25 cho câu hỏi chứa công thức.
  - Thêm người chấm thứ hai.
