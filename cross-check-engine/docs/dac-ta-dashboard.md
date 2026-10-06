# Đặc tả giao diện: Báo cáo đối soát dạng web (`--format html`)

Lập theo skill `dac-ta-ui-nghiep-vu` (khung 9 mục, phong cách Cockpit).

## 1. Việc cần làm
- Người dùng: Ban QLDA, pháp chế, kiểm toán viên nội bộ.
- Việc chính: **biết ngay phát hiện nào cần xử lý trước, vì sao, và truy về căn cứ.**
- Dữ liệu vào: kết quả engine (phát hiện, bản đồ chế độ pháp lý, phạm vi kiểm).
- Đầu ra: một file HTML tự chứa (mở offline, gửi kèm email), in được, xuất CSV theo bộ lọc.
- Giả định: không tải font/thư viện từ mạng; trình duyệt hiện đại; JS tắt thì vẫn đọc và in được đầy đủ.

## 2. Phong cách
- Cockpit trên màn hình (tối); bản in chuyển sang Tài liệu tối giản (nền trắng, chữ đen).
- Dấu hiệu giữ: nền #101720/panel #182330; cảnh báo đứng trên bảng; số tabular; trạng thái chữ + màu;
  mã quy tắc dạng mono.

## 3. Nội dung mở đầu
- H1: "<tên dự án>: N điểm cần xử lý" (N = đỏ + vàng, tính từ dữ liệu; N = 0 → "không phát hiện
  điểm cần xử lý trong phạm vi đã kiểm").
- Lời dẫn: ngày đối soát, số văn bản dự án, nhãn "Bản nháp – cần xác minh".
- Hành động chính: "Xem điểm cần xử lý" (nhảy tới vùng 2).

## 4. Từng vùng
### 1. Tổng quan
**Bố cục và hành vi:** 4 ô theo mức (đỏ, vàng, xám, xanh) + dòng phạm vi kiểm.
**Nội dung và đầu ra:** số đếm từ danh sách phát hiện; phạm vi = số quy tắc trình tự, số văn bản dự án,
số văn bản trong sổ và số đã đối chiếu văn bản gốc.

### 2. Cần xử lý
**Bố cục và hành vi:** danh sách đỏ rồi vàng, mỗi mục có mức, tiêu đề, sai ở đâu, cách khắc phục,
liên kết "Xem truy vết" tới chi tiết trong bảng.
**Nội dung và đầu ra:** không có mục → câu "không có điểm đỏ/vàng trong phạm vi đã kiểm" (không ghi "đạt").

### 3. Bản đồ chế độ pháp lý
**Bố cục và hành vi:** bảng bước × lĩnh vực; cuộn ngang trong vùng có nhãn khi màn hẹp.
**Nội dung và đầu ra:** ghi rõ "theo ngày sự kiện, chưa xét chuyển tiếp".

### 4. Tất cả phát hiện
**Bố cục và hành vi:** tìm kiếm, lọc mức, lọc đối tượng, xóa lọc; "Đang hiện N/M"; mỗi phát hiện mở/đóng
chi tiết (`<details>`), mặc định đóng; mobile hiển thị dạng thẻ.
**Nội dung và đầu ra:** chi tiết gồm sai ở đâu, căn cứ (kèm "chưa xác minh"), độ tin cậy, cách khắc phục,
truy vết.

### 5. Xuất CSV
**Bố cục và hành vi:** nút "Xuất CSV (N dòng đang hiện)"; chỉ xuất dòng đang hiện.
**Nội dung và đầu ra:** UTF-8 có BOM; chặn công thức (= + - @ tab CR); tải bị chặn → hiện văn bản để sao chép.

## 5. Dữ liệu và trạng thái
- Mọi chuỗi từ hồ sơ được thoát HTML khi dựng; JS chỉ đọc thuộc tính dữ liệu và `textContent`.
- Lọc không còn dòng → thông báo + nút xóa lọc.
- Không phát hiện nào → vẫn hiện phạm vi kiểm.

## 6. Responsive
- 1440: vùng chính tối đa 1200px; 768: ô tổng quan 2×2; 390: một cột, bảng phát hiện thành thẻ,
  bảng chế độ pháp lý cuộn trong vùng riêng; nút ≥ 44px.

## 7. Chuyển động
- Hover/focus 150ms; `prefers-reduced-motion` tắt chuyển động.

## 8. In
- Nền trắng, chữ đen; ẩn thanh lọc và nút; mở toàn bộ chi tiết; không ngắt giữa một phát hiện.

## 9. Nghiệm thu riêng
1. Tổng 4 ô = tổng phát hiện.
2. Lọc mức "ĐỎ" rồi xuất CSV → số dòng CSV = số đang hiện.
3. Chuỗi `=HYPERLINK(...)` và `<script>` trong dữ liệu: CSV bị vô hiệu hóa công thức; HTML hiện nguyên văn.
4. `check_layout.mjs` sạch ở 390/768/1440.
