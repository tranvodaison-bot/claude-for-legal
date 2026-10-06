# Quy tắc nghiệp vụ cho giao diện QLDA / pháp lý / kiểm toán

Mỗi quy tắc có lý do — áp dụng theo tinh thần, không máy móc.

## 1. Trung thực dữ liệu
- Mọi con số hiển thị **tính từ dữ liệu đầu vào** tại thời điểm dựng/tải; không viết cứng, không số
  "minh họa" lẫn vào số thật. Nếu là dữ liệu mẫu: nhãn "Dữ liệu mẫu" đặt cạnh tiêu đề, không ở chân trang.
- Không hiển thị "Đạt / Hợp lệ / Thành công" khi hệ thống chỉ **không tìm thấy lỗi**. Ghi "Không phát hiện
  trong phạm vi đã kiểm" và nói phạm vi (bộ quy tắc nào, bao nhiêu văn bản). Lý do: không có cảnh báo
  ≠ tuân thủ; kiểm toán viên sẽ hỏi phạm vi.
- Kết luận dựa trên dữ liệu chưa xác minh phải mang nhãn **"cần xác minh"** nhìn thấy được ngay trên dòng.
- Thao tác chỉ mô phỏng (chạy lại, gửi, duyệt) phải nói rõ là mô phỏng; không giả vờ đã gửi/đã ký.

## 2. Mức độ và trạng thái
- Trạng thái = **chữ + màu (+ ký hiệu)**: ví dụ "● ĐỎ – lỗi cứng". In đen trắng vẫn phân biệt được.
- Thứ tự mặc định: nghiêm trọng nhất lên trước; "cần xử lý" đứng trên bảng chi tiết.
- Tổng các mức phải bằng tổng phát hiện (là một trường hợp nghiệm thu).

## 3. Truy vết
- Từ mỗi cảnh báo mở được chi tiết: **sai ở đâu → căn cứ (văn bản, điều, khoản, mức xác minh) →
  dữ liệu thực tế (ngày, số hiệu, chứng cứ) → cách khắc phục**.
- Mã quy tắc/mã phát hiện hiển thị dạng mono để người dùng trích dẫn khi trao đổi.
- Căn cứ chưa có điều/khoản ghi rõ "chưa điền điều/khoản", không để trống.

## 4. Bảng dữ liệu
- Tìm kiếm + lọc có nhãn; hiện "Đang hiện N/M"; lọc không có kết quả → có nút xóa lọc.
- Cột số/ngày căn phải, `font-variant-numeric: tabular-nums`; ngày dạng dd/mm/yyyy.
- Mobile: hàng → thẻ giữ đủ trường, hoặc bảng cuộn trong vùng riêng có nhãn; không thu nhỏ cả trang.

## 5. An toàn dữ liệu
- **Thoát HTML** mọi chuỗi lấy từ hồ sơ (`& < > " '`) trước khi đưa vào DOM; ưu tiên `textContent`.
  Hồ sơ trích từ PDF/Word có thể chứa ký tự lạ hoặc mã độc.
- Nhúng JSON vào trang: thay `<` bằng `<` để không đóng thẻ `<script>` sớm.
- **CSV**: ô bắt đầu bằng `=`, `+`, `-`, `@`, tab hoặc CR → thêm `'` phía trước; bọc ô bằng `"` và nhân
  đôi `"` bên trong; thêm BOM UTF-8 để Excel đọc đúng tiếng Việt. Gọi là "CSV", không gọi "Excel".
- Không nhúng khóa API, mật khẩu, đường dẫn nội bộ nhạy cảm; file tự chứa không gọi mạng ngoài.

## 6. Trống / tải / lỗi
- Trống: nói vì sao trống và làm gì tiếp ("Chưa có văn bản dự án – thêm mục `documents`").
- Lỗi: nói lỗi gì, ở đâu, cách sửa; không chỉ "Đã có lỗi xảy ra".
- Clipboard/tải file bị chặn: hiện nội dung để người dùng tự chọn.

## 7. In và lưu hồ sơ
- `@media print`: nền trắng, chữ đen, ẩn điều khiển (lọc, nút), mở toàn bộ chi tiết, tránh ngắt giữa
  một phát hiện (`break-inside: avoid`), in ngày đối soát và tuyên bố miễn trừ ở mỗi trang nếu có thể.
- Tuyên bố "bản nháp hỗ trợ rà soát, không phải kết luận pháp lý" hiển thị cả trên màn hình và bản in.

## 8. Bài học từ lần áp dụng thực tế (dashboard cross-check-engine, 10/2026)
- **Dựng sẵn nội dung, JS chỉ tăng cường.** Toàn bộ phát hiện được dựng thành HTML đã thoát ký tự; JS
  chỉ lọc, mở chi tiết, xuất CSV. Tắt JS hoặc in vẫn đủ nội dung — quan trọng khi file được lưu hồ sơ.
- **Test chống chèn công thức phải có ô BẮT ĐẦU bằng `=`.** Công thức nằm giữa ô không nguy hiểm và
  không chứng minh được gì; đưa chuỗi độc vào trường sẽ thành cột đầu ô (mã văn bản, tên đối tượng).
- **Liên kết "Bỏ qua tới nội dung" ẩn ngoài màn hình vẫn phải cao ≥ 44px** khi hiện ra bằng Tab.
- **Bản in phải triệt nền của trạng thái hover/đang chọn** (`background:none!important`), nếu không dòng
  đang trỏ chuột lúc bấm in sẽ ra nền xám, chữ mờ.
- **Đọc kỹ phần truy vết trên giao diện là một cách kiểm dữ liệu.** Lần đầu xem truy vết đã lộ một ngày
  hết hiệu lực bị suy ra sai — giao diện tốt làm lỗi dữ liệu dễ thấy, đừng chỉ nhìn bố cục.
