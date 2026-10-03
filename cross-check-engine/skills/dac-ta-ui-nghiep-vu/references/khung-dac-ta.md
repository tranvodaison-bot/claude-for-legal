# Mẫu đặc tả 9 mục

Điền ngắn gọn. Mục nào không áp dụng thì ghi "không áp dụng – lý do", đừng bỏ trống im lặng.

```markdown
# Đặc tả giao diện: <tên màn hình>

## 1. Việc cần làm
- Người dùng: <vai trò>
- Việc chính trên màn hình: <một câu>
- Dữ liệu vào: <nguồn, định dạng, có thật hay mẫu>
- Đầu ra: <xem / in / CSV / chuyển tiếp>
- Giả định đã tự chọn: <liệt kê>

## 2. Phong cách
- Chọn: <Cockpit | Tài liệu tối giản | khác> – lý do
- 3–5 dấu hiệu nhận diện phải giữ: <...>
- Token: màu theo vai trò, font, thang chữ, khoảng cách, bo góc, viền (bảng)

## 3. Nội dung mở đầu
- H1: <nói được việc/lợi ích, không khẩu hiệu>
- Lời dẫn: <một câu, có phạm vi dữ liệu và ngày>
- Hành động chính: <nhãn nút nói kết quả của thao tác>

## 4. Từng vùng nội dung
### <Vùng 1>
**Bố cục và hành vi:** ...
**Nội dung và đầu ra:** ...
(lặp cho từng vùng, theo thứ tự đọc)

## 5. Dữ liệu và trạng thái
- Nguồn từng con số (tính từ đâu, phạm vi lọc nào)
- Trạng thái: trống / đang tải / lỗi / thành công – chữ hiển thị cho từng trạng thái
- Phân biệt dữ liệu mẫu với dữ liệu thật; thao tác nào chỉ mô phỏng

## 6. Responsive và thứ tự đọc
- 390 / 768 / 1440 px: bố cục từng mức; bảng → thẻ hay cuộn trong vùng riêng
- Thứ tự DOM = thứ tự việc; không cuộn ngang toàn trang

## 7. Chuyển động
- Thời lượng, cái gì chuyển động, bản prefers-reduced-motion

## 8. In ấn / xuất bản (thay cho "ảnh bìa" của bản gốc)
- Có in không; @media print giữ gì, bỏ gì; xuất CSV/PDF

## 9. Trường hợp nghiệm thu riêng
1. <kiểm được bằng số hoặc thao tác cụ thể>
2. ...
3. ...
Cộng bộ kiểm chung: scripts/check_layout.mjs, focus bàn phím, zoom 200%, trạng thái trống, reset.
```

## Ví dụ ngắn (dashboard đối soát)

- Việc chính: "Biết ngay phát hiện nào cần xử lý trước và vì sao."
- H1: "Hồ sơ dự án X – 8 điểm cần xác minh" (số lấy từ dữ liệu, không viết cứng).
- Vùng "Cần xử lý" đứng **trên** bảng chi tiết; mỗi dòng có hướng khắc phục.
- Nghiệm thu riêng: tổng các mức = tổng phát hiện; lọc rồi xuất CSV đúng số dòng đang hiện;
  chuỗi `=HYPERLINK(...)` trong dữ liệu xuất ra CSV bị vô hiệu hóa.
