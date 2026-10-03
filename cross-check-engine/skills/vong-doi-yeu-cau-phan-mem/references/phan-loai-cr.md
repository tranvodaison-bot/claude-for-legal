# Phân loại CR (change request)

## Câu hỏi bắt buộc (trả lời Có/Không, ghi vào biên bản GATE CR)
| # | CR có chạm… | Có → |
|---|---|---|
| 1 | Mô hình dữ liệu (thêm/sửa/xóa bảng, trường, quan hệ) | LỚN |
| 2 | Máy trạng thái (thêm trạng thái, đổi điều kiện chuyển) | LỚN |
| 3 | Phân quyền, vai trò, phạm vi dữ liệu người dùng thấy | LỚN |
| 4 | Quy tắc pháp lý/tài chính (tính tiền, hiệu lực văn bản, mức cảnh báo, chữ ký) | LỚN |
| 5 | Tích hợp ngoài (API bên thứ ba, email, chữ ký số, đồng bộ) | LỚN |
| 6 | Dữ liệu đang có trên LIVE (cần migrate/sửa hàng loạt) | LỚN |
| 7 | Hơn 2 chức năng hoặc hơn 1 nhóm chức năng (module) | LỚN |
| 8 | Chỉ đổi hiển thị/nhãn/thứ tự/bộ lọc của ≤ 2 chức năng, không chạm 1–7 | NHỎ |

Không chắc một câu → trả lời "Có". Hạ LỚN → NHỎ phải ghi lý do và người duyệt.

## Phân tích ảnh hưởng (cả hai luồng)
Dựa trên `docs/uc-master.yaml` + `docs/sa-hien-trang.md` (đồ thị BA: UC ↔ màn hình ↔ API ↔ bảng dữ liệu):
- Liệt kê **UC bị chạm trực tiếp** và **UC chạm gián tiếp** (dùng chung bảng/API/trạng thái).
- Với mỗi UC bị chạm: testcase nào phải chạy lại, mục HDSD nào phải sửa.
- Dữ liệu cũ có bị ảnh hưởng không; có cần migrate không (Có → câu 6 → LỚN).
- Ghi kết quả vào biên bản; UC mới được **đăng ký vào sổ Master trước khi** sửa đặc tả.
