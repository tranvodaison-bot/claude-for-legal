# PRD: Đối soát nhất quán thông tin giữa các văn bản dự án · v1.0 · 03/10/2026

## Bối cảnh và vấn đề
Cùng một thông tin (tên dự án, TMĐT, quy mô, thời gian) xuất hiện ở nhiều văn bản ký vào các thời điểm
khác nhau. Lệch giữa chúng là dấu hiệu kiểm toán hay hỏi: giấy phép cấp cho quy mô khác quy mô đã duyệt,
hợp đồng có tiến độ vượt thời gian thực hiện dự án, vốn giao vượt TMĐT. Hiện engine không đọc nội dung
văn bản nên bỏ sót toàn bộ nhóm lỗi này.

## Mục tiêu / không phải mục tiêu
- Mục tiêu: phát hiện lệch thông tin giữa văn bản đích và **văn bản chuẩn có hiệu lực tại ngày ký của văn
  bản đích**; có bảng đối chiếu để người xem tự thấy giá trị từng văn bản.
- Không phải mục tiêu: trích tự động từ PDF (M4); đánh giá việc điều chỉnh dự án có hợp pháp không
  (cần lập luận pháp lý - skill project-legal-reasoning); kiểm chi phí chi tiết (kiem-toan-chi-phi-dtxd).

## Người dùng
Ban QLDA (rà trước khi trình), pháp chế, kiểm toán nội bộ.

## Quy trình nghiệp vụ đề xuất
1. Người nhập khai báo cho mỗi văn bản: `nhom` (loại), `thong_tin` (các trường có trong văn bản đó),
   `thay_the` (nếu là văn bản điều chỉnh).
2. Engine, với mỗi quy tắc: lấy văn bản chuẩn mới nhất thuộc nhóm chuẩn **ký trước hoặc cùng ngày** văn bản
   đích → so trường → phát hiện.
3. Báo cáo hiện phát hiện (VÀNG mặc định) + bảng đối chiếu theo trường.

## Danh sách UC
| Mã | Tên | Vai trò | Ưu tiên |
|---|---|---|---|
| UC-007 | Đối soát nhất quán thông tin giữa các văn bản dự án | Ban QLDA, pháp chế, kiểm toán | Cao |

## Mô hình dữ liệu (bổ sung, đều tùy chọn)
```yaml
documents:
  - id: QD-DC-DA
    nhom: phe_duyet_du_an          # chu_truong | bcnckt_hoan_thien | phe_duyet_du_an | phe_duyet_thiet_ke
                                   # | gpxd | hop_dong | ke_hoach_von | hoan_cong | khac
    thay_the: [QD-PD-DA]           # văn bản điều chỉnh: cùng nhóm, ký sau
    thong_tin:
      ten_du_an: "Nhà xưởng A"
      tong_muc_dau_tu: 125000000000          # đồng
      dien_tich_san: 12500                   # m2
      chieu_cao: 24.5                        # m
      so_tang: 3
      thoi_gian_thuc_hien: {tu: 2021-06-01, den: 2024-12-31}
      von_duoc_giao: 30000000000             # chỉ cho nhom ke_hoach_von
```
Quy tắc trong `data/consistency_rules.yaml` (sửa không cần code): trường, nhóm chuẩn, nhóm đích, kiểu so
(`equal_text` | `equal_number` | `within_period` | `sum_not_exceed`), dung sai, mức, điều kiện áp dụng.

## Sơ đồ trạng thái
Không có máy trạng thái mới. Quan hệ phiên bản văn bản: gốc → điều chỉnh lần 1 → lần 2 (theo `thay_the`,
mỗi bản có ngày ký); "bản có hiệu lực tại ngày D" = bản mới nhất ký ≤ D.

## Phản biện đặc tả gốc §3.4 (đề xuất sửa, cần Boss chốt)
1. **"TMĐT tại BCNCKT ↔ QĐ phê duyệt"**: BCNCKT *trình* thường khác QĐ vì thẩm định cắt/điều chỉnh - so
   bản trình sẽ báo lệch giả. Đề xuất chỉ so **BCNCKT hoàn thiện sau thẩm định** (`bcnckt_hoan_thien`).
2. **"TMĐT ↔ Kế hoạch vốn được giao"**: kế hoạch vốn giao **theo năm**, không bằng TMĐT. Đúng là
   **lũy kế vốn giao ≤ TMĐT** đang hiệu lực. Ngoài ra dự án **vốn tư nhân** (KCN/KĐT) không có kế hoạch vốn
   được giao → quy tắc chỉ bật khi `attributes.von_dau_tu_cong: true`.

## Giả định mặc định (chờ xác nhận ở GATE 1)
| # | Giả định | Lý do |
|---|---|---|
| A1 | Tên dự án: khác chữ hoa, khoảng trắng, dấu câu → coi là khớp | Tránh báo lệch vụn; khác chữ thật vẫn báo |
| A2 | Dung sai số = 0 (TMĐT, diện tích, chiều cao, số tầng) | An toàn; chỉnh được trong file quy tắc |
| A3 | Mức mặc định VÀNG (lỗi mềm); riêng lũy kế vốn giao vượt TMĐT = ĐỎ | Đúng nguyên tắc 5 của đặc tả gốc |
| A4 | Văn bản chuẩn = bản mới nhất ký ≤ ngày văn bản đích | Văn bản cũ đúng với chuẩn tại thời điểm của nó, không bị báo oan khi dự án điều chỉnh sau |
| A5 | Hai sửa đổi ở mục "Phản biện" được chấp nhận | Như trên |

## Câu hỏi làm rõ / gap
1. Có cần thêm trường nào ngoài 4 nhóm của §3.4 không (vd. địa điểm, diện tích đất, cấp công trình)? - mở.
2. Hợp đồng nhiều gói thầu: tiến độ từng gói phải nằm trong thời gian thực hiện dự án - đã đưa vào quy tắc.
3. Ai nhập `thong_tin` khi chưa có M4 (trích tự động)? - giả định: cán bộ QLDA nhập tay.

## Ngoài phạm vi
Trích xuất PDF; CSDL; vòng đời xử lý phát hiện; so khối lượng/đơn giá.
