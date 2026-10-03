# Hai phong cách mặc định

Chọn theo **việc**, không theo sở thích. Cần phong cách khác → dùng skill `ui-ux-pro-max`, nhưng giữ
nguyên quy tắc nghiệp vụ của skill này.

## A. Cockpit (tối) – màn làm việc, dashboard, bảng theo dõi

Nguồn: prompt-driven-ui `prompts/40.md`.

| Token | Giá trị | Vai trò |
|---|---|---|
| background | #101720 | nền trang |
| surface | #182330 | panel |
| surface-raised | #203041 | panel nổi, hàng đang chọn |
| foreground | #EDF3F7 | chữ chính |
| muted | #A6B7C5 | chữ phụ, metadata |
| accent | #69D4E4 | hành động chính, liên kết |
| on-accent | #101720 | chữ trên nền accent |
| border | #2B3A49 | đường phân cách |
| focus | #A6EAF2 | vòng focus |
| warning | #F3C56A | cảnh báo |
| error | #EE8A91 | lỗi |
| success | #92D7B5 | đạt |

- Font: IBM Plex Sans 400/500/600; IBM Plex Mono cho số, mã, log. Fallback hệ thống có dấu tiếng Việt
  (`"IBM Plex Sans", "Segoe UI", Roboto, "Noto Sans", Arial, sans-serif`). File offline: không tải font
  mạng, dùng fallback.
- Cỡ: H1 32px/1.25; H2 22px; KPI 32–40px tabular; body 16px; bảng 14–16px; metadata 14px.
- Lưới: sidebar 220px (nếu có điều hướng) + vùng chính `minmax(0,1fr)`; không ép max-width kiểu landing.
- Radius 6px, viền 1px, **không đổ bóng mọi panel**; phân lớp bằng surface/surface-raised.
- Cảnh báo đứng trước biểu đồ; không sparkline khi không có chuỗi dữ liệu thật; không đếm nhảy số.
- Chuyển trạng thái 150ms; reduced-motion: tắt chuyển động, giữ nguyên thông tin.
- Mobile 390px: điều hướng thành menu; bảng → danh sách thẻ giữ đủ trường, hoặc bảng cuộn trong vùng có nhãn.
- Tránh: KPI ngẫu nhiên, nút "chạy lại" thực thi thật khi chỉ là mô phỏng, nhiều biểu đồ trang trí,
  nút chỉ có icon không tên.

## B. Tài liệu tối giản (sáng) – báo cáo đọc, in, gửi đi

Nguồn: prompt-driven-ui `prompts/45.md`.

| Token | Giá trị |
|---|---|
| canvas | #F5F5F5 (in: #FFFFFF) |
| text | #111111 |
| muted | #555555 (đậm hơn bản gốc #666 để đạt 4.5:1 ở 14px) |
| rule | #E5E5E5 |
| tag-bg | #EAEAEA hoặc màu trạng thái 10–15% |

- Một họ font sans (Inter/Helvetica/hệ thống). Tiêu đề 20px; body 14–16px, line-height 1.7–1.8;
  tiêu đề phần 14px viết hoa có giãn chữ, **line-height ≥ 1.4 để không cắt dấu tiếng Việt**.
- Không bóng, gần như không viền; chỉ `<hr>` 1px giữa các phần. Phân cấp bằng cỡ/độ đậm/khoảng trắng.
- Lưới bất đối xứng: cột trái hẹp (ngày, nhãn phần), cột phải rộng (nội dung); dòng 65–75 ký tự.
- Màu trạng thái chỉ dùng cho thẻ nhỏ, luôn kèm chữ.

## Nguyên tắc chung (rút từ policies/design-principles-vi.md)

- Một màn một việc chính; làm yếu chỗ phụ để chỗ chính tự nổi.
- Một thang khoảng cách (8–12–16–24–40), một thang chữ 4–5 cỡ, một màu nhấn.
- Cùng chức năng thì cùng hình, cùng chỗ. Nút có hover/active/focus rõ.
- Việc chờ có chữ "đang…"; trạng thái trống có chữ và đường đi tiếp.
- Việc dài chia bước, có chỉ báo bước; ẩn thứ chưa cần.
- Tương phản ≥ 4.5:1 (chữ lớn ≥ 3:1); Tab đi hết; vùng bấm ≥ 44px trên điện thoại.
- Dưới 640px: một cột, không cuộn ngang, nút gần hết bề ngang.
- Lỗi phải có chữ, không chỉ đổi màu. Không chữ xám trên nền màu.
