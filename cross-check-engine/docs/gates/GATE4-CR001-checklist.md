# GATE 4 - UAT CR-001 · checklist cho người dùng nghiệp vụ

Chạy trên **hồ sơ thật đã ẩn danh** của một dự án Ban QLDA nắm rõ (không dùng hồ sơ mẫu của AI).

| # | Kịch bản | Cách làm | Đạt khi |
|---|---|---|---|
| 1 | Lệch đã biết được phát hiện | Khai báo `thong_tin` cho 5-10 văn bản, trong đó có ít nhất 1 lệch Boss đã biết | Lệch đó xuất hiện, đúng văn bản, đúng chuẩn so sánh |
| 2 | Không báo oan khi điều chỉnh | Thêm một QĐ điều chỉnh với `thay_the` | Văn bản ký trước điều chỉnh vẫn so với bản cũ |
| 3 | Dự án vốn tư nhân | Bỏ `von_dau_tu_cong` | Không có NQ-VON-1 |
| 4 | Đọc hiểu báo cáo | Người chưa xem tài liệu mở bao_cao.html | Tự tìm được điểm cần xử lý và truy vết trong 2 phút |
| 5 | In và CSV | In bản PDF; lọc VÀNG rồi xuất CSV, mở bằng Excel | Bản in đủ nội dung, tiếng Việt đúng; CSV đúng số dòng |
| 6 | Hồ sơ cũ | Chạy lại hồ sơ đang dùng (chưa có `thong_tin`) | Kết quả như trước, bảng đối chiếu ghi trạng thái trống |

Go-live (bản dùng nội bộ, chạy trên máy): không có migrate, không có dữ liệu seed trên hồ sơ thật;
rollback = dùng lại commit trước CR-001.

Biên bản: người chạy UAT, ngày, kết quả từng dòng, kết luận (Chấp thuận / Có điều kiện / Chưa).
