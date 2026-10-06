# CR-003: Nhập hồ sơ dự án từ Excel · 04/10/2026

- Người đề nghị: Boss (chọn ưu tiên 04/10/2026).
- AS-IS: hồ sơ dự án phải viết bằng YAML - rào cản lớn nhất để Ban QLDA dùng thật và chạy UAT.
- TO-BE: Ban QLDA điền một file Excel mẫu; engine đọc trực tiếp `.xlsx`, báo lỗi theo từng ô; có lệnh tạo
  file mẫu và lệnh chuyển hồ sơ YAML có sẵn sang Excel.

## Phân loại
| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Mô hình dữ liệu | Không - Excel ánh xạ đúng cấu trúc hồ sơ hiện có |
| 2–6 | Trạng thái, phân quyền, quy tắc pháp lý/tài chính, tích hợp ngoài, migrate | Không |
| 7 | > 2 chức năng | **Có** - đọc Excel + tạo mẫu + chuyển YAML→Excel; thêm phụ thuộc `openpyxl` |
**Kết luận: CR LỚN** → PRD (GATE 1) → đặc tả mẫu Excel (GATE 2) và luồng/kiểm lỗi (GATE 3).

## Phân tích ảnh hưởng
- UC mới: UC-008. Gián tiếp: UC-001…007 (nhận thêm nguồn đầu vào; **logic đối soát không đổi**).
- Test: TC-ENG/TMP/NQ/DSB/UI hồi quy + TC-XL mới, trong đó **ca khứ hồi**: 3 hồ sơ mẫu YAML → Excel →
  đọc lại → báo cáo Markdown phải **y hệt** báo cáo từ YAML.
- HDSD: thêm mục nhập liệu Excel. Dữ liệu cũ: YAML vẫn dùng được, không migrate.

## Trạng thái (04/10/2026)
- GATE CR003-G1/G2/G3: chấp thuận. Đã dựng `crosscheck/excel.py`; CLI nhận `.xlsx`.
- TC-XL 14 ca đạt, gồm khứ hồi 3 hồ sơ mẫu (Markdown y hệt) và mở/lưu lại bằng LibreOffice Calc (đọc lại y hệt,
  danh sách chọn còn nguyên). Toàn bộ 94 test, TC-UI 21/21; Markdown hai hồ sơ mẫu cũ y hệt.
- Lỗi tự phát hiện và đã sửa trong lúc dựng: lỗi nhập liệu ban đầu thoát bằng traceback thay vì danh sách lỗi;
  cột Nhóm quá hẹp làm cắt nhãn; ô tiền không có phân cách nghìn (chỉ đổi định dạng hiển thị).
- Môi trường build thiếu LibreOffice Calc - đã cài `libreoffice-calc` trong container (tạm thời) để kiểm.
- Chờ GATE 4 (UAT): Boss điền thử file mẫu bằng Microsoft Excel và chạy checklist CR-001.
