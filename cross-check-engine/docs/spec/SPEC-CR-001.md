# Đặc tả CR-001 · v1.0 · 03/10/2026

## 1. Quy tắc mặc định (`data/consistency_rules.yaml`)
| Mã | Trường | Chuẩn → Đích | Kiểu so | Mức | Áp dụng khi |
|---|---|---|---|---|---|
| NQ-TEN-1 | ten_du_an | chu_truong → phe_duyet_du_an | equal_text | VÀNG | luôn |
| NQ-TEN-2 | ten_du_an | phe_duyet_du_an → gpxd, hop_dong, phe_duyet_thiet_ke | equal_text | VÀNG | luôn |
| NQ-TMDT-1 | tong_muc_dau_tu | bcnckt_hoan_thien → phe_duyet_du_an | equal_number | VÀNG | luôn |
| NQ-VON-1 | von_duoc_giao (lũy kế) | phe_duyet_du_an.tong_muc_dau_tu → ke_hoach_von | sum_not_exceed | ĐỎ | `von_dau_tu_cong: true` |
| NQ-QM-1 | dien_tich_san, chieu_cao, so_tang | phe_duyet_du_an → phe_duyet_thiet_ke | equal_number | VÀNG | luôn |
| NQ-QM-2 | dien_tich_san, chieu_cao, so_tang | phe_duyet_thiet_ke → gpxd, hoan_cong | equal_number | VÀNG | luôn |
| NQ-TG-1 | thoi_gian_thuc_hien | chu_truong → phe_duyet_du_an | within_period | VÀNG | luôn |
| NQ-TG-2 | thoi_gian_thuc_hien | phe_duyet_du_an → hop_dong | within_period | VÀNG | luôn |

Kiểm văn bản điều chỉnh: `thay_the` trỏ tới văn bản không tồn tại, khác nhóm, hoặc ký sau văn bản điều
chỉnh → VÀNG `NQ-PB`.

## 2. Hành vi so sánh
- Chỉ so khi **văn bản đích có giá trị** của trường. Đích có giá trị mà không có văn bản chuẩn ký ≤ ngày
  đích, hoặc chuẩn không có trường đó → XÁM `NQ-*-GAP`.
- `equal_text`: chuẩn hóa NFC, chữ thường, bỏ dấu câu, gộp khoảng trắng; khác → phát hiện, nêu cả hai giá trị.
- `equal_number`: |đích − chuẩn| > dung sai → phát hiện, nêu chênh lệch tuyệt đối và %.
- `within_period`: đích.tu ≥ chuẩn.tu và đích.den ≤ chuẩn.den; vi phạm → nêu số ngày vượt.
- `sum_not_exceed`: với mỗi văn bản đích theo thứ tự ngày, lũy kế giá trị đến văn bản đó > chuẩn tại ngày đó → phát hiện.
- Phát hiện thuộc dữ liệu dự án (không dựa căn cứ pháp lý chưa xác minh) → `verified: true`; căn cứ ghi
  "Nguyên tắc nhất quán dữ liệu - đặc tả §3.4", không viện dẫn điều khoản.

## 3. Màn hình (GATE 2) - vùng mới "Bảng đối chiếu thông tin" trong báo cáo web
Vị trí: sau "Bản đồ chế độ pháp lý", trước "Tất cả phát hiện". Một bảng con cho mỗi trường có dữ liệu.

```
┌ Bảng đối chiếu thông tin ────────────────────────────────────────────────────────────────┐
│ So từng văn bản với văn bản chuẩn có hiệu lực tại ngày ký của nó.                         │
│                                                                                            │
│ TỔNG MỨC ĐẦU TƯ (đồng)                                                                     │
│ Văn bản       Nhóm             Ngày ký     Giá trị            Chuẩn so sánh       Kết quả   │
│ QD-PD-DA      phê duyệt DA     10/06/2021  120.000.000.000    BCNCKT-HT 01/06/21  ✓ Khớp   │
│ QD-DC-DA      phê duyệt DA     01/09/2026  135.000.000.000    BCNCKT-HT 01/06/21  ▲ Lệch   │
│                                                               +15.000.000.000 (+12,5%)     │
│ KHV-2022      kế hoạch vốn     15/01/2022  lũy kế 40.000.000.000  QD-PD-DA       ✓ Trong   │
│                                                                                            │
│ THỜI GIAN THỰC HIỆN                                                                        │
│ HD-TC-01      hợp đồng         15/11/2024  01/12/24–30/06/26  QD-PD-DA 06/21–12/25  ▲ Vượt │
│                                                               181 ngày sau hạn dự án       │
└────────────────────────────────────────────────────────────────────────────────────────────┘
Mobile (< 768px): mỗi bảng con cuộn ngang trong vùng có nhãn; cột "Kết quả" giữ chữ + ký hiệu.
Không có dữ liệu `thong_tin` → vùng hiện: "Chưa có văn bản nào khai báo thông tin để đối chiếu."
```
Kết quả dùng chữ + ký hiệu: `✓ Khớp`, `▲ Lệch`, `▲ Vượt`, `○ Thiếu chuẩn`. Số căn phải, tabular, phân cách
nghìn bằng dấu chấm. Phát hiện tương ứng vẫn nằm trong "Tất cả phát hiện" (lọc, CSV như cũ).
Markdown: thêm mục "Bảng đối chiếu thông tin" cùng nội dung dạng bảng. JSON: thêm khóa `consistency`.

## 4. Luồng xử lý (GATE 3)
```mermaid
sequenceDiagram
  participant U as Người dùng (CLI)
  participant C as cli.main
  participant K as consistency
  participant R as report/dashboard
  U->>C: python -m crosscheck ho_so.yaml [--consistency rules.yaml]
  C->>K: load_consistency_rules(path)  (kiểm: trường, nhóm, kiểu so, mức hợp lệ)
  C->>K: check_consistency(project, rules)
  K->>K: lập chuỗi phiên bản theo nhóm (thay_the + ngày ký)
  K->>K: với mỗi quy tắc × văn bản đích: tìm chuẩn ký ≤ ngày đích → so
  K-->>C: findings[] + matrix{trường: [dòng đối chiếu]}
  C->>R: to_markdown / to_json / to_html(..., consistency=matrix)
  R-->>U: báo cáo; mã thoát 1 nếu có ĐỎ
```
CLI: thêm tùy chọn `--consistency` (mặc định `data/consistency_rules.yaml`). File quy tắc lỗi → mã thoát 2.

## 5. User stories (UC-007)
- **US-007a Tên dự án.** Given chủ trương "Nhà xưởng A", phê duyệt "Nhà xưởng  A." → Then khớp (A1);
  Given GPXD "Nhà xưởng B" → Then VÀNG `NQ-TEN-2`, nêu hai tên.
- **US-007b TMĐT và vốn.** Given phê duyệt DA 120 tỷ, BCNCKT hoàn thiện 118 tỷ → Then VÀNG `NQ-TMDT-1`
  chênh +2 tỷ (+1,69%); Given `von_dau_tu_cong: true`, lũy kế KHV 125 tỷ > 120 tỷ → Then ĐỎ `NQ-VON-1`;
  Given dự án tư nhân (thuộc tính false/không khai báo) → Then không chạy NQ-VON-1.
- **US-007c Quy mô.** Given TK triển khai 3 tầng, GPXD 4 tầng → Then VÀNG `NQ-QM-2`.
- **US-007d Thời gian.** Given dự án 06/2021–12/2025, hợp đồng đến 30/06/2026 → Then VÀNG `NQ-TG-2`, vượt 181 ngày.
- **US-007e Văn bản điều chỉnh.** Given GPXD ký 2023 so với phê duyệt gốc 2021, điều chỉnh DA ký 2026 →
  Then GPXD so với bản 2021 (không báo oan); Given `thay_the` trỏ tới văn bản khác nhóm → VÀNG `NQ-PB`.
- **US-007f Bảng đối chiếu.** Given có `thong_tin` → Then báo cáo web/Markdown có bảng theo trường, mỗi dòng
  nêu chuẩn so sánh; không có → câu trạng thái trống.

## 6. Nghiệm thu (testcase sẽ viết ở bước 4–5)
- TC-NQ (pytest): mỗi US-007a…e ít nhất 1 ca đúng + 1 ca lệch; quy tắc lỗi bị từ chối khi nạp;
  **hồi quy**: hai hồ sơ mẫu cũ cho kết quả y hệt trước CR.
- TC-UI mở rộng: bảng đối chiếu hiển thị, tổng các mức = tổng phát hiện, check_layout sạch 390/768/1440.
