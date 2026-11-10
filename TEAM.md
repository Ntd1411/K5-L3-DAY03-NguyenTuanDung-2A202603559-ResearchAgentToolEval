Danh sách sinh viên thực hiện:

1. Nguyễn Tuấn Dũng | 2A202603559 
2. Lý Thanh Lâm | 2A202603475
3. Nguyễn Vũ Khanh | 2A202603427

## Phân công công việc

### 1. Nguyễn Tuấn Dũng — Prompt, eval và tích hợp

- Setup môi trường, API key và kiểm tra provider/tool.
- Chạy baseline `v0`, phân tích các case fail và lưu run JSON.
- Chỉnh `artifacts/system_prompt.md` và chạy phiên bản `v1`.
- Theo dõi kết quả `v0`–`v3`, cập nhật `artifacts/version_log.csv`.
- Review thay đổi của các thành viên, chạy test và eval tổng trước khi nộp.
- Kiểm tra repo không chứa `.env`, API key hoặc file không cần thiết.

Kết quả cần bàn giao:

- `runs/v0_*.json`, `runs/v1_*.json`.
- `artifacts/system_prompt.md`.
- `artifacts/version_log.csv` có đủ `v0`, `v1`, `v2`, `v3`.
- Kết quả `pytest` và base eval cuối cùng.

### 2. Lý Thanh Lâm — Tool declaration, tool mới và unit test

- Viết lại description và parameter convention trong `artifacts/tools.yaml`.
- Chạy phiên bản `v2` để đo ảnh hưởng của tool declaration.
- Thiết kế và cài đặt ít nhất 1 tool mới, gồm `tool.py` và `TOOL.md`.
- Đăng ký tool mới trong `tools/__init__.py` và `artifacts/tools.yaml`.
- Viết ít nhất 3 unit test cho tool mới: happy path, input không hợp lệ và failure path.
- Hoàn thiện các test TODO nếu còn thời gian; đảm bảo contract test luôn pass.
- Viết 5 eval case single-turn trong `data/eval_group.json`, có ít nhất 1 case cho tool mới.

Kết quả cần bàn giao:

- `artifacts/tools.yaml`.
- `tools/<ten_tool_moi>/tool.py`.
- `tools/<ten_tool_moi>/TOOL.md`.
- Phần test tool mới trong `tests/test_tools_todo.py`.
- 5 eval case single-turn.
- `runs/v2_*.json`.

### 3. Nguyễn Vũ Khanh — Group eval, UI và báo cáo

- Viết 5 eval case multi-turn trong `data/eval_group.json`.
- Phân tích lỗi còn lại sau `v2`, đề xuất một giả thuyết và chạy phiên bản `v3`.
- Xây dựng UI bằng Streamlit và kiểm tra luồng chat/tool call.
- Chạy `chat.py` ít nhất 3 tình huống và lưu transcript.
- Deploy UI hoặc mở Cloudflare Tunnel, ghi lại link dùng thử.
- Hoàn thiện `artifacts/REPORT.md`: Phần A cho demo và Phần B dựa trên log thật.

Kết quả cần bàn giao:

- 5 eval case multi-turn.
- `runs/v3_*.json` và run group eval.
- File UI, dự kiến `app.py`.
- `transcripts/*.transcript.json`.
- `artifacts/REPORT.md` và link demo.

## Quy ước phối hợp

- Không sửa `data/eval_base.json`.
- Mỗi version chỉ kiểm chứng một giả thuyết chính.
- Trước khi merge/chuyển việc, chạy `pytest tests/ -v`.
- Mọi metric trong report phải lấy từ `runs/*.json`, không tự ước lượng.
- Không commit `.env`, API key, token Telegram hoặc thông tin bí mật.
- Khi thêm hoặc đổi tên tool, phải đồng bộ `tools.yaml`, `tools/__init__.py`, `TOOL.md` và eval case.

## Tiến độ hiện tại

- [x] Setup môi trường và kiểm tra đầy đủ API key.
- [x] Provider preflight thành công.
- [x] Chạy baseline `v0` và ghi version log.
- [x] Hoàn thành `v1` (`case_accuracy=1.00`, `routing=1.00`).
- [ ] Hoàn thành `v2`.
- [ ] Hoàn thành `v3`.
- [ ] Thêm tool mới và unit test.
- [ ] Viết 10 group eval case: 5 single-turn, 5 multi-turn.
- [ ] Hoàn thành UI, transcript và report.
