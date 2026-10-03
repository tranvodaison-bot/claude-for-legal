---
name: dac-ta-ui-nghiep-vu
description: >
  Đặc tả, dựng và nghiệm thu GIAO DIỆN (màn hình, dashboard, báo cáo HTML) cho phần mềm nội bộ của Ban
  QLDA và pháp chế, theo khung 9 mục rút từ prompt-driven-ui: hiểu việc, phong cách và token, từng vùng
  màn hình, trạng thái dữ liệu, responsive, nghiệm thu. Kèm quy tắc hiển thị: không số liệu giả, nhãn độ
  tin cậy, trạng thái chữ kèm màu, truy vết trên màn hình, CSV chống chèn công thức, thoát HTML, bản in;
  có script chụp và kiểm bố cục 390/768/1440. Kích hoạt khi: dựng hoặc sửa giao diện web, dashboard,
  báo cáo HTML cho công cụ nội bộ; viết đặc tả màn hình; nghiệm thu giao diện trước bàn giao. KHÔNG dùng
  cho: nội dung nghiệp vụ (IPC, VO, kiểm toán, pháp lý) → skill chuyên ngành tương ứng; chọn phong cách
  thuần thẩm mỹ → ui-ux-pro-max; component shadcn/Tailwind → ui-styling; React/TDD → netninja-master;
  vòng đời CR/PRD/GATE → vong-doi-yeu-cau-phan-mem.
---

# Đặc tả giao diện nghiệp vụ

Phần mềm cho Ban QLDA, pháp chế, kiểm toán có một đặc thù: người xem dùng màn hình để **ra quyết định
và chịu trách nhiệm**. Một con số giả, một trạng thái "thành công" không có thật, hay một cảnh báo
không truy được về căn cứ đều có thể dẫn tới ký sai hoặc xuất toán. Vì vậy đặc tả ở đây nặng về
**trung thực dữ liệu và truy vết**, nhẹ về trang trí.

Phương pháp gốc: khung prompt của repo `vuhung16au/prompt-driven-ui` (MIT, xem `NOTICE.md`).
Skill này giữ khung, bỏ phần marketing/ảnh bìa/triển khai hosting, thêm quy tắc nghiệp vụ.

## Quy trình

### 1. Hiểu việc trước khi vẽ
Chốt bốn điều: **ai dùng** (CĐT, QLDA, pháp chế, kiểm toán viên), **một việc chính** họ phải xong trên
màn hình (ví dụ "biết ngay văn bản nào đang viện dẫn căn cứ hết hiệu lực"), **dữ liệu vào** (file,
API, engine nào) và **đầu ra** (xem, in, CSV, chuyển tiếp). Nếu thiếu, hỏi gộp một câu; chi tiết nhỏ thì
tự chọn và ghi rõ giả định. Màn quản trị ưu tiên công việc và dữ liệu, không biến thành trang quảng cáo
(không hero lớn, không ba thẻ tính năng).

### 2. Chọn phong cách và khóa token
Đọc `references/phong-cach.md`. Mặc định:
- **Cockpit** (tối) cho màn làm việc hằng ngày: dashboard, bảng theo dõi.
- **Tài liệu tối giản** (sáng) cho báo cáo đọc/in/gửi đi.
Khóa một bộ biến: màu theo vai trò, font có đủ dấu tiếng Việt, thang chữ 4–5 cỡ, thang khoảng cách
8–12–16–24–40, bo góc, viền. Số dùng `tabular-nums`, cột số căn phải.

### 3. Viết đặc tả 9 mục
Dùng mẫu trong `references/khung-dac-ta.md`. Mỗi vùng nội dung ghi hai dòng: **Bố cục và hành vi** /
**Nội dung và đầu ra**. Viết đặc tả ngắn rồi dựng luôn — đặc tả là công cụ, không phải sản phẩm.

Thứ tự trình bày cho người chốt: **phác ASCII** (bố cục + trường dữ liệu, sửa trong vài phút) → khi
bố cục ổn mới dựng **HTML tương tác với dữ liệu mẫu** để bấm thử → người dùng chốt (GATE 2 trong
skill `vong-doi-yeu-cau-phan-mem`, có biên bản). Dựng HTML khi bố cục chưa chốt là tốn công sửa lại.

### 4. Áp quy tắc nghiệp vụ (bắt buộc với dữ liệu pháp lý/tài chính)
Đọc `references/quy-tac-nghiep-vu.md`. Tóm tắt lý do từng nhóm:
- **Không số liệu giả, không thành công giả** — người xem sẽ tin và hành động theo.
- **Nhãn nguồn/độ tin cậy** cạnh mọi kết luận — "chưa xác minh" phải nhìn thấy được, không giấu trong tooltip.
- **Trạng thái = chữ + màu (+ ký hiệu)** — in đen trắng và người mù màu vẫn đọc được.
- **Truy vết** — từ mỗi cảnh báo mở được: sai ở đâu → căn cứ → dữ liệu thực tế → cách khắc phục.
- **An toàn dữ liệu** — thoát HTML mọi chuỗi lấy từ hồ sơ; CSV chặn ký tự đầu `= + - @`; không nhúng bí mật.
- **Trống / tải / lỗi** đều có chữ giải thích và đường đi tiếp.

### 5. Dựng
Giữ công nghệ đang có; dựng mới thì chọn cách đơn giản nhất chạy được (một file HTML tự chứa, không gọi
mạng, khi người dùng cần mở offline hoặc gửi kèm). Thứ tự DOM theo việc người xem cần làm để phím Tab đi
đúng. Có `@media print` nếu báo cáo sẽ được in.

### 6. Nghiệm thu có bằng chứng
Chạy `scripts/check_layout.mjs` (Playwright) để chụp 390/768/1440 px và kiểm tự động: cuộn ngang, số
lượng h1, chữ < 12px, vùng bấm < 44px trên điện thoại, ảnh thiếu alt, ô nhập thiếu nhãn, lỗi console.
```bash
node scripts/check_layout.mjs <file.html|url> --out <thư_mục_ảnh>
```
Xem lại ảnh chụp, sửa sai lệch, rồi mới báo xong. Chạy thêm các **trường hợp nghiệm thu riêng** đã ghi ở
mục 9 của đặc tả (ví dụ "tổng các mức = tổng phát hiện", "CSV theo bộ lọc đang xem").

Nếu trang có lọc/xuất CSV/mở chi tiết, viết thêm một script nghiệm thu riêng bằng Playwright cho các
trường hợp ở mục 9 (cài dữ liệu độc: `<script>`, ô bắt đầu bằng `=`), để chạy lại mỗi lần sửa.

Lệch giữa giao diện đã dựng và đặc tả đã chốt: sửa **giao diện**, không sửa đặc tả hay script nghiệm
thu cho khớp. Đặc tả sai thật thì mở CR. Tối đa 3 vòng tự sửa rồi dừng báo cáo.

### 7. Báo cáo bàn giao
Ngắn: đã làm gì, đã kiểm gì (kèm số liệu từ script), chưa kiểm gì, phần nào còn thiếu dữ liệu thật.
Không nói "đã kiểm tra" khi chưa chạy.
