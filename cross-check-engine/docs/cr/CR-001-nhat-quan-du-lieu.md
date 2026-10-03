# CR-001: Đối soát nhất quán thông tin giữa các văn bản dự án · 03/10/2026

- Người đề nghị: Boss (đặc tả gốc §3.4 "Đối soát theo tính nhất quán dữ liệu"; kế hoạch M3).
- AS-IS: văn bản dự án chỉ khai báo ngày và căn cứ viện dẫn; engine không biết nội dung (tên, TMĐT, quy mô,
  thời gian) nên không phát hiện được lệch thông tin giữa các văn bản.
- TO-BE: văn bản mang trường thông tin; engine so từng văn bản với văn bản chuẩn **có hiệu lực tại ngày ký**
  của nó (tính cả văn bản điều chỉnh), xuất phát hiện + bảng đối chiếu trên báo cáo.

## Phân loại (references/phan-loai-cr.md)
| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Chạm mô hình dữ liệu | **Có** - thêm `nhom`, `thay_the`, `thong_tin` cho văn bản; file quy tắc mới |
| 2 | Máy trạng thái | Không |
| 3 | Phân quyền | Không |
| 4 | Quy tắc pháp lý/tài chính | **Có** - so TMĐT và vốn được giao |
| 5 | Tích hợp ngoài | Không |
| 6 | Dữ liệu LIVE cần migrate | Không (trường mới là tùy chọn; hồ sơ cũ chạy như trước) |
| 7 | > 2 chức năng / > 1 module | **Có** - 4 nhóm trường + văn bản điều chỉnh + màn hình mới |

**Kết luận: CR LỚN** → PRD → GATE 1 → tri thức → đặc tả → GATE 2, GATE 3 → coding.

## Phân tích ảnh hưởng
- **UC trực tiếp:** UC-007 (mới). **UC gián tiếp:** UC-004 (báo cáo web thêm vùng "Bảng đối chiếu"),
  UC-005 (Markdown/JSON thêm phần đối chiếu).
- **Không ảnh hưởng:** UC-001/002/003 - trường mới là tùy chọn, logic cũ không đổi.
- **Test chạy lại:** TC-ENG, TC-TMP, TC-DSB, TC-UI (hồi quy) + test mới TC-NQ, TC-UI mở rộng.
- **HDSD:** chưa có HDSD (phát hiện từ sổ truy vết) - viết mục cho UC-007 ở bước 6.
- **Dữ liệu cũ:** không migrate; hai hồ sơ mẫu hiện có phải cho kết quả **y hệt** trước CR (kiểm hồi quy).
- **UC mới đăng ký vào sổ Master:** UC-007 (trạng thái `draft` đến khi qua GATE 1).

## Trạng thái (cập nhật 03/10/2026)
- GATE CR001-G1/G2/G3: chấp thuận (docs/gates/). Đã dựng, test đạt (TC-NQ 22 ca mới; TC-UI 17/17), hồi quy:
  hai hồ sơ mẫu cũ cho báo cáo Markdown y hệt trước CR.
- Lệch đặc tả phát hiện ở test E2E và đã sửa giao diện (không sửa đặc tả): bảng TMĐT tràn ở 1440px làm mất cột
  Kết quả; giá trị chữ hiển thị như số.
- Chờ GATE 4 (UAT): docs/gates/GATE4-CR001-checklist.md.
