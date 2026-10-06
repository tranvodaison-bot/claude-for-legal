# CR-002: Bảng đối chiếu thông tin dạng thẻ trên điện thoại · 04/10/2026

- Người đề nghị: Claude (phát hiện khi test E2E CR-001). GATE CR + GATE 2: Boss chấp thuận 04/10/2026.
- AS-IS (đúng đặc tả CR-001 đã chốt): dưới 768px mỗi bảng con cuộn ngang; cột **Kết quả** là cột cuối,
  người xem điện thoại phải vuốt ngang mới thấy văn bản nào lệch.
- TO-BE: dưới 768px mỗi dòng thành **một thẻ**, kết quả đứng đầu thẻ. Từ 768px trở lên giữ nguyên bảng.

## Phân loại (references/phan-loai-cr.md)
Câu 1–7: **Không** (không đổi dữ liệu, quy tắc, luồng). Câu 8: chỉ đổi hiển thị của 1 chức năng →
**CR NHỎ**. Đổi màn hình → vẫn qua **GATE 2** (quy tắc 4 của skill).

## Phân tích ảnh hưởng
- UC trực tiếp: UC-007 (vùng Bảng đối chiếu). Gián tiếp: UC-004 (báo cáo web). Markdown/JSON không đổi.
- Test chạy lại: TC-UI (thêm ca 390px), TC-DSB, check_layout 390/768/1440. HDSD: không đổi (ảnh chụp ở 1280px).

## Màn hình đề xuất (GATE 2)
```
390px                                   ≥ 768px: giữ nguyên bảng hiện tại
┌ TỔNG MỨC ĐẦU TƯ ───────────────────┐
│ ▲ Lệch                QD-PD-DA     │  ← kết quả + mã văn bản ở dòng đầu
│ Phê duyệt dự án · 10/06/2021       │
│ Giá trị   120.000.000.000 đồng     │
│ Chuẩn     BCNCKT-HT (20/05/2021):  │
│           118.000.000.000 đồng     │
│ chênh +2.000.000.000 đồng (+1,69%) │  ← ghi chú, chữ phụ
├────────────────────────────────────┤
│ ✓ Trong hạn mức       KHV-2022     │
│ Kế hoạch vốn được giao · 15/01/2022│
│ Giá trị   40.000.000.000 đồng      │
│           lũy kế 40.000.000.000    │
│ Chuẩn     QD-PD-DA (10/06/2021):…  │
└────────────────────────────────────┘
```
Cùng dữ liệu, cùng thứ tự DOM (bảng HTML giữ nguyên; chỉ CSS đổi cách trình bày) → trình đọc màn hình và
bản in không đổi. Nhãn "Giá trị", "Chuẩn" hiện trên thẻ bằng thuộc tính dữ liệu của ô.

## Nghiệm thu
1. 390px: ô Kết quả của mỗi dòng nằm trong khung nhìn mà không cần cuộn ngang.
2. 768px và 1440px: bảng như cũ (không cuộn ngang ở 1024/1440).
3. check_layout sạch 390/768/1440; báo cáo Markdown của 3 hồ sơ mẫu y hệt.

## Trạng thái (04/10/2026)
Đã dựng bằng CSS (HTML vẫn là bảng, thứ tự đọc không đổi). TC-UI thêm 4 ca, 21/21 đạt; check_layout sạch
390/768/1440; Markdown hai hồ sơ mẫu cũ y hệt. Lệch mockup phát hiện khi xem ảnh (ghi chú nằm dưới kết quả
thay vì cuối thẻ) đã sửa giao diện.
