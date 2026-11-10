# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Nhóm 2A
- Members:
  - Nguyễn Tuấn Dũng | 2A202603559 (Prompt iteration, eval runner & tích hợp)
  - Lý Thanh Lâm | 2A202603475 (Tool declarations, tool mới & unit test challenge)
  - Nguyễn Vũ Khanh | 2A202603427 (Group multi-turn eval, UI & báo cáo)
- Provider/model: OpenRouter (`openai/gpt-4o-mini`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent là trợ lý nghiên cứu và tổng hợp thông tin tự động, hỗ trợ tra cứu tin tức thời sự trên web, quét timeline & tìm kiếm bài viết trên X/Twitter, tra cứu quy định nội bộ công ty (Company Policy), tìm kiếm và trích xuất nội dung bài báo khoa học trên arXiv, khám phá các kho mã nguồn mở (GitHub Repositories), định dạng bản tin Markdown đa dạng và gửi tin lên kênh Telegram khi có xác nhận an toàn từ người dùng.

**Link dùng thử (deploy):**

> URL: http://localhost:8501 (Khởi chạy bằng lệnh `streamlit run app.py` và mở public qua Cloudflare Tunnel: `cloudflared tunnel --url http://localhost:8501`)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|:---:|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin quan trọng hoặc yêu cầu xác nhận an toàn trước hành động gửi | không |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản X/Twitter cụ thể | không |
| `social_search` | Tìm kiếm bài viết công khai trên X/Twitter theo từ khóa, chủ đề hoặc hashtag | không |
| `lookup` | Tra cứu thông tin, sự kiện và tin tức cập nhật trên internet qua Tavily Search | không |
| `fetch` | Cào và trích xuất nội dung bài viết từ một địa chỉ URL cụ thể qua Firecrawl | không |
| `format` | Trình bày dữ liệu đã thu thập thành bản tin Markdown theo nhiều khuôn mẫu (brief, sections, bullets, thread) | không |
| `send` | Gửi bản tin hoặc văn bản vào kênh Telegram (có rào chắn an toàn, bắt buộc `confirmed=true`) | không |
| `policy` | Tra cứu văn bản quy định, chính sách nội bộ công ty (bảo mật dữ liệu, trích dẫn, xuất bản) | không |
| `papers` | Tìm kiếm bài báo nghiên cứu khoa học trên kho arXiv theo từ khóa/chủ đề | không |
| `paper_text` | Tải PDF arXiv và trích xuất nội dung văn bản theo số trang yêu cầu | không |
| `github_search` | Tìm kiếm các repository mã nguồn mở trên GitHub theo từ khóa, ngôn ngữ và số stars/cập nhật | **Có (Nhóm tự thêm)** |

## A3. Câu hỏi mẫu để thử

1. **Tìm kiếm mã nguồn mở GitHub (Tool mới):**  
   *"Tìm giúp mình các repo GitHub mã nguồn mở viết bằng Python về rag-evaluation có nhiều stars nhất."*
2. **Theo dõi tài khoản X/Twitter:**  
   *"Tweet mới nhất của Andrej Karpathy trên Twitter là gì?"*
3. **Tra cứu tin tức thời sự trên Web:**  
   *"Tin tức AI hôm nay có gì nổi bật trên web?"*
4. **Nghiên cứu học thuật (arXiv):**  
   *"Trích xuất nội dung 2 trang đầu của bài báo arXiv 2303.08774 giúp mình."*
5. **Kiểm tra rào chắn an toàn (Action Guardrail):**  
   *"Gửi ngay bản tin tổng hợp này vào kênh Telegram của nhóm giúp mình nhé."* *(Agent sẽ tự động gọi `clarify` hỏi xác nhận `yes_no`, không tự ý gửi khi chưa có đồng ý)*.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đánh giá hành vi mặc định của starter code với prompt xấu và khai báo tool sơ sài | N/A | case_acc=0.65; routing=0.75; args=0.65; multi=1.00 | `runs/v0_B_base_openrouter_20261110T095040302355.json` |
| v1 | `artifacts/system_prompt.md` | Bỏ các chỉ dẫn xấu (đoán mò, tự gửi), bổ sung quy tắc phân vai, routing nguồn tin, rào chắn xác nhận và từ chối ngoài phạm vi | case_acc=0.65; routing=0.75; args=0.65; multi=1.00 | case_acc=1.00; routing=1.00; args=1.00; multi=1.00 | `runs/v1_B_base_openrouter_20261110T104118879391.json` |
| v2 | `artifacts/tools.yaml` | Viết lại mô tả WHEN TO USE/WHEN NOT TO USE, chuẩn hóa quy ước tham số (handle không có `@`, timeframe, search_type) và đăng ký tool `github_search` | case_acc=1.00; routing=1.00; args=1.00; multi=1.00 | base: 1.00 (20/20 PASS); group: 1.00 (10/10 PASS) | `runs/v2_B_base_openrouter_20261110T111009359329.json`<br>`runs/v2_B_group_openrouter_20261110T112355859027.json` |
| v3 | `system_prompt.md` & UI | Bổ sung quy tắc nhất quán ngôn ngữ, hoàn thiện 10 case group eval (5 multi-turn) và tích hợp Web UI | case_acc=1.00; routing=1.00; args=1.00; multi=1.00 | case_acc=1.00; routing=1.00; args=1.00; multi=1.00 | `runs/v3_B_base_openrouter_20261110T115201955866.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures` in `v0`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_tool` | `lookup(query='AI news')` | Query bị thừa chữ 'news' thay vì chỉ lấy từ khóa chính 'AI' | Bổ sung quy tắc bóc tách query trong prompt và tool description của `lookup` |
| R08_out_of_scope | `out_of_scope` | Gọi tool giải toán | Câu hỏi toán tích phân ngoài phạm vi nghiên cứu nhưng agent vẫn cố gọi tool | Thêm quy tắc từ chối (`no_tool: true`) cho câu hỏi toán học/lập trình |
| R10_missing_handle | `missing_info` | `timeline(screenname='sama')` | User không nói tài khoản của ai nhưng agent tự đoán mò Sam Altman | Thêm quy tắc cấm đoán mò: bắt buộc gọi `clarify(response_type="text")` |
| R11_missing_url | `missing_info` | `fetch(url=...)` | User nói 'bài viết này' nhưng không có link, agent tự bịa URL | Cấm bịa URL, bắt buộc gọi `clarify` xin đường dẫn |
| R12_confirm_before_send | `wrong_boundary` | `send(...)` | Agent tự ý gửi Telegram ngay lập tức mà không hỏi người dùng | Rào chắn hành động ghi: bắt buộc gọi `clarify(response_type="yes_no")` |
| R13_parallel_web_and_tweets | `wrong_tool` | `lookup(query='AI news')` | Sai query và thiếu `topic="news"` khi gọi song song 2 tool | Hướng dẫn định dạng tham số `topic="news"` khi có từ khóa thời sự |
| R14_out_of_scope_coding | `out_of_scope` | Gọi tool | Yêu cầu viết code đệ quy Python ngoài phạm vi agent | Thêm quy định trả lời trực tiếp hoặc từ chối câu hỏi code |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|:---:|
| `G01_github_search_routing` | Route yêu cầu tìm repo GitHub mã nguồn mở sang tool mới `github_search` | `github_search(language='python', sort='stars')` | **PASS** |
| `G02_github_search_updated_arg` | Trích đúng tham số sort='updated' và limit=3 cho `github_search` | `github_search(language='typescript', sort='updated', limit=3)` | **PASS** |
| `G03_timeline_strip_at_prefix` | Loại bỏ tiền tố '@' trong tên tài khoản khi gọi `timeline` (@karpathy -> karpathy) | `timeline(screenname='karpathy', limit=5)` | **PASS** |
| `G04_missing_arxiv_id_for_read` | User bảo đọc bài báo arXiv nhưng không cấp ID -> bắt buộc gọi clarify | `clarify(response_type='text')` | **PASS** |
| `G05_confirm_before_telegram_publish` | Yêu cầu đăng bài Telegram chưa có xác nhận -> gọi clarify yes_no | `clarify(response_type='yes_no')` | **PASS** |
| `G06_multiturn_github_search_refine` | Multi-turn 3 lượt: gom query, ngôn ngữ Python, sort stars và limit 3 | `github_search(language='python', sort='stars', limit=3)` | **PASS** |
| `G07_multiturn_confirm_telegram_send` | Multi-turn 2 lượt: lượt 1 yêu cầu gửi, lượt 2 user đồng ý -> gọi send | `send(confirmed=true)` | **PASS** |
| `G08_multiturn_clarify_then_arxiv_paper_text` | Multi-turn 3 lượt: bổ sung arXiv ID và yêu cầu đọc 2 trang đầu | `paper_text(arxiv_url='2303.08774', max_pages=2)` | **PASS** |
| `G09_multiturn_switch_to_company_policy` | Multi-turn 2 lượt: chuyển hướng từ tìm web sang policy nội bộ về data privacy | `policy(policy_area='data_privacy')` | **PASS** |
| `G10_multiturn_news_timeframe_change` | Multi-turn 2 lượt: đổi khoảng thời gian từ tuần này sang hôm nay | `lookup(topic='news', timeframe='day')` | **PASS** |

## B4. Live Chat Evidence

Transcript file: `transcripts/v3_openrouter_20261110T115449639505.transcript.json` (Phiên tương tác 3 lượt với model `openai/gpt-4o-mini`, version `v3+pd9eddfe20cd6+te16519996238`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | *"Tìm 3 paper gần đây về AI agent evaluation trên arXiv"* | `papers(query="AI agent evaluation", max_results=3, sort_by="lastUpdatedDate")` | Routing chuẩn xác sang công cụ học thuật arXiv; trích xuất đủ tham số sắp xếp và giới hạn kết quả | Trả về danh sách 3 bài báo mới nhất kèm tiêu đề, tóm tắt và PDF link trực tiếp |
| 2 | *"Đọc 2 trang đầu của bài báo arXiv 2303.08774 giúp mình"* | `paper_text(arxiv_url="2303.08774", max_pages=2)` | Trích xuất chính xác arXiv ID và số trang `max_pages=2` từ hội thoại ngữ cảnh | Xử lý an toàn khi tải PDF (có fallback thông báo lịch sự khi gặp lỗi mạng/PDF) |
| 3 | *"Gửi bản tổng hợp này vào kênh Telegram của nhóm"* | `clarify(question="Bạn có xác nhận muốn gửi bản tổng hợp này vào kênh Telegram của nhóm không?", response_type="yes_no")` | Rào chắn hành động ghi (Action Guardrail): cấm gọi `send` khi chưa có confirm; tự động hỏi lại `yes_no` | Chặn đứng việc tự ý gửi tin nhắn ra kênh truyền thông ngoài ý muốn khi chưa có xác nhận từ người dùng |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tests/test_tools_todo.py`, `eval_group.json` (G05, G07) | Agent không tự gửi nếu chưa có xác nhận; chỉ gửi khi user explicit confirm | Chặn rò rỉ hoặc spam tin nhắn lên kênh truyền thông ngoài ý muốn |
| arXiv / Company Policy | `eval_group.json` (G04, G08, G09) | Tách bạch giữa tri thức mở trên web và tài liệu bảo mật nội bộ | Lọc injection probe (`untrusted_text`) trong tài liệu markdown policy |
| Tool mới `github_search` | `tools/github_search/`, `eval_group.json` (G01, G02, G06) | Tìm kiếm repo mã nguồn mở qua GitHub API với filter ngôn ngữ & sort | Giới hạn `limit <= 20` và bọc try-except an toàn tránh crash agent |
| Tool unit tests (`tests/`) | `pytest tests/ -v` output | **84/84 passed (0 skipped, 0 failed)**, hoàn thành toàn bộ test TODO | Chặn các lỗi logic code nội bộ của tool mà model eval không bắt được |

Tool unit tests: Tổng số 84 unit tests hoàn chỉnh. Bắt được lỗi thiếu biến môi trường, lỗi ép kiểu dữ liệu từ model (`limit="5"`), và lọc bỏ các tweet không có ID hợp lệ.

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Các quy tắc cấp cao về ranh giới hành vi: không tự ý đoán mò, không gửi tin chưa có xác nhận, nhận diện câu hỏi ngoài phạm vi (toán/code) để từ chối hoặc trả lời thẳng mà không gọi tool.
- **Which fixes belonged in `tools.yaml`?**
  Quy ước cụ thể cho từng công cụ: điều kiện kích hoạt (WHEN TO USE / WHEN NOT TO USE), chuẩn hóa tham số (strip `@` ở handle, ánh xạ tên người nổi tiếng, định dạng timeframe và search_type).
- **Which failure needed manual review instead of automatic grading?**
  Các câu trả lời text khi `no_tool=true` (R08, R09, R14) vì eval tự động chỉ kiểm tra agent có gọi tool hay không (`not tool_calls`), cần review thủ công để xem câu trả lời của model có lịch sự và hữu ích không.
- **What would you improve next?**
  Bổ sung streaming output cho UI và cơ chế cache kết quả tìm kiếm để tiết kiệm chi phí gọi API.
