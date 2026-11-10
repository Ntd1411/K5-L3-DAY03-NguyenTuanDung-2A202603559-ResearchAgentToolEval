Danh sách sinh viên thực hiện:

1. Nguyễn Tuấn Dũng | 2A202603559 | https://github.com/Ntd1411
2. Lý Thanh Lâm | 2A202603475 | https://github.com/LysLama
3. Nguyễn Vũ Khanh | 2A202603427 | https://github.com/vukhanhkg2005-lang

## Công việc đã thực hiện

### 1. Nguyễn Tuấn Dũng — Prompt, baseline, v1 và UI ban đầu

- Setup môi trường, API key và kiểm tra provider/tool.
- Chạy baseline `v0`, phân tích các case fail và lưu run JSON.
- Chỉnh `artifacts/system_prompt.md` và chạy phiên bản `v1`.
- Ghi kết quả baseline và `v1` vào `artifacts/version_log.csv`.
- Xây dựng UI Streamlit ban đầu: chat nhiều vòng, chọn provider/model, hiển thị tool trace và tải transcript JSON.
- Thêm chế độ so sánh ba phiên bản từ run eval đã lưu.
- Bổ sung quy tắc trả lời theo ngôn ngữ người dùng trong system prompt.
- Thêm cấu hình theme, dependency Streamlit và hướng dẫn chạy UI trong `README.md`.
- Cập nhật danh sách thành viên và thông tin GitHub trong `TEAM.md`.

Sản phẩm đã thực hiện:

- `runs/v0_*.json`, `runs/v1_*.json`.
- `artifacts/system_prompt.md`.
- Các dòng `v0`, `v1` trong `artifacts/version_log.csv`.
- UI ban đầu trong `app.py`, cấu hình `.streamlit/config.toml` và các transcript demo ban đầu.
- Phần hướng dẫn UI trong `README.md` và dependency trong `requirements.txt`.

### 2. Lý Thanh Lâm — Tools, unit test, group eval, v2–v3 và báo cáo

- Viết lại description và parameter convention trong `artifacts/tools.yaml`.
- Chạy phiên bản `v2` để đo ảnh hưởng của tool declaration.
- Thiết kế và cài đặt tool mới `github_search`, gồm `tool.py` và `TOOL.md`.
- Đăng ký tool mới trong `tools/__init__.py` và `artifacts/tools.yaml`.
- Viết 3 unit test cho tool mới: happy path, input không hợp lệ và failure path.
- Hoàn thiện các test TODO; toàn bộ suite đạt 84 passed, 0 skipped, 0 failed.
- Viết đủ 10 eval case trong `data/eval_group.json`: 5 single-turn (`G01`–`G05`) và 5 multi-turn (`G06`–`G10`).
- Chạy và lưu base/group eval cho `v2`, `v3`; cập nhật các dòng version log tương ứng.
- Bổ sung transcript live chat 3 lượt và bảng phân tích run CSV.
- Hoàn thiện `artifacts/REPORT.md` Phần A, Phần B và poster HTML phục vụ demo.

Sản phẩm đã thực hiện:

- `artifacts/tools.yaml`.
- `tools/github_search/tool.py`, `tools/github_search/TOOL.md` và đăng ký trong `tools/__init__.py`.
- Các test đã hoàn thiện trong `tests/test_tools_todo.py`.
- `data/eval_group.json` với 10 case.
- `runs/v2_*.json`, `runs/v3_*.json` và các dòng `v2`, `v3` trong `artifacts/version_log.csv`.
- `transcripts/v3_openrouter_20261110T115449639505.transcript.json`.
- `analysis/base_runs.csv`, `artifacts/REPORT.md`, `artifacts/poster.html`.

### 3. Nguyễn Vũ Khanh — Cải tiến UI, snapshot phiên bản và tích hợp

- Cải tiến giao diện Streamlit phục vụ demo local: bố cục, màu sắc và các thành phần hiển thị phiên nghiên cứu.
- Bổ sung snapshot system prompt và tool declaration cho `v0`, `v1`, `v2`, `v3` trong `artifacts/versions/`.
- Tích hợp chọn phiên bản trong UI để nạp prompt/tool declaration tương ứng khi chat.
- Merge các thay đổi UI với run group eval, dữ liệu phân tích và báo cáo của nhóm.

Sản phẩm đã thực hiện:

- Các phần cải tiến UI và chọn phiên bản trong `app.py`.
- `artifacts/versions/v0/`, `artifacts/versions/v1/`, `artifacts/versions/v2/`, `artifacts/versions/v3/`.
- Bản tích hợp UI, run eval và báo cáo tại merge commit `9660387`.

## Quy ước phối hợp

- Không sửa `data/eval_base.json`.
- Mỗi version chỉ kiểm chứng một giả thuyết chính.
- Trước khi merge/chuyển việc, chạy `pytest tests/ -v`.
- Mọi metric trong report phải lấy từ `runs/*.json`, không tự ước lượng.
- Không commit `.env`, API key, token Telegram hoặc thông tin bí mật.
- Khi thêm hoặc đổi tên tool, phải đồng bộ `tools.yaml`, `tools/__init__.py`, `TOOL.md` và eval case.

## Tiến độ hiện tại

- [X] Setup môi trường và kiểm tra đầy đủ API key.
- [X] Provider preflight thành công.
- [X] Chạy baseline `v0` và ghi version log.
- [x] Hoàn thành `v1` (`case_accuracy=1.00`, `routing=1.00`).
- [x] Hoàn thành `v2` (`case_accuracy=1.00`, `routing=1.00`, `group_single_turn=1.00`).
- [x] Hoàn thành `v3` (`case_accuracy=1.00`, `routing=1.00`, `group_accuracy=1.00`).
- [x] Thêm tool mới (`github_search`) và unit test (84 passed, 0 skipped, 0 failed).
- [x] Viết 10 group eval case: 5 single-turn (đã xong `G01`–`G05`), 5 multi-turn (`G06`–`G10`).
- [x] Hoàn thành UI Streamlit (`app.py`), gồm chat và so sánh ba phiên bản.
- [x] Bổ sung snapshot prompt/tool declaration cho `v0`–`v3` và chọn phiên bản khi chat.
- [x] Có transcript live chat 3 lượt đã lưu trong repo.
- [x] Hoàn thiện report Phần A, Phần B và poster demo.
