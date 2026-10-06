# PRD: Nhập hồ sơ dự án từ Excel · v1.0 · 04/10/2026

## Bối cảnh và vấn đề
Engine đã đối soát được trình tự, hiệu lực căn cứ và nhất quán thông tin, nhưng hồ sơ phải viết YAML. Cán bộ
QLDA quen Excel; viết YAML dễ sai thụt lề, sai mã, và không có danh sách chọn. Đây là điều kiện để chạy
GATE 4 (UAT) của CR-001 trên hồ sơ thật.

## Mục tiêu / không phải mục tiêu
- Mục tiêu: điền Excel → chạy `python3 -m crosscheck ho_so.xlsx` như với YAML; lỗi nhập liệu chỉ rõ
  **sheet + ô + cách sửa**; có file mẫu với danh sách chọn; chuyển được hồ sơ YAML sang Excel.
- Không phải mục tiêu: trích từ PDF/Word (M4); nhiều dự án trong một file; đọc `.xls` đời cũ; sửa file Excel
  của người dùng (engine chỉ đọc).

## Người dùng
Cán bộ Ban QLDA nhập liệu; pháp chế/kiểm toán chạy báo cáo.

## Danh sách UC
| Mã | Tên | Ưu tiên |
|---|---|---|
| UC-008 | Nhập hồ sơ dự án từ Excel (đọc, kiểm lỗi theo ô, tạo mẫu, chuyển YAML→Excel) | Cao |

## Mô hình dữ liệu
Không đổi. Mỗi sheet ánh xạ một phần của hồ sơ hiện có (chi tiết: SPEC-CR-003 mục 1).

## Giả định mặc định (chờ xác nhận ở GATE 1)
| # | Giả định | Lý do |
|---|---|---|
| B1 | Chỉ `.xlsx` (Excel 2007+, LibreOffice lưu dạng xlsx); một dự án một file | Đủ cho Ban QLDA; `.xls` cần thư viện khác |
| B2 | Danh sách chọn hiển thị nhãn tiếng Việt ("Hoàn thành", "Phê duyệt dự án"); engine nhận cả nhãn lẫn mã | Người nhập không phải nhớ mã |
| B3 | Ngày: ô kiểu ngày của Excel, hoặc chữ `dd/mm/yyyy`, hoặc `yyyy-mm-dd` | Ba cách nhập phổ biến |
| B4 | Số: ô kiểu số; nếu là chữ thì theo quy ước Việt Nam - dấu chấm phân cách nghìn, dấu phẩy thập phân (`120.000.000.000`, `24,5`) | Tránh hiểu nhầm `1.500` |
| B5 | Có lỗi nhập liệu → **không chạy đối soát**, liệt kê toàn bộ lỗi một lần (mã thoát 2) | Không ra báo cáo từ dữ liệu sai |
| B6 | Ô công thức: đọc giá trị đã tính lưu trong file; ô công thức chưa có giá trị → báo lỗi ô đó | Engine không tự tính công thức |

## Câu hỏi làm rõ
1. Đơn vị đã có mẫu Excel theo dõi hồ sơ riêng không? Nếu có, CR sau sẽ ánh xạ theo mẫu đó - **mở**.

## Ngoài phạm vi
Ghi vị trí ô Excel vào phần truy vết của từng phát hiện (đề xuất CR sau); bảo vệ file bằng mật khẩu.
