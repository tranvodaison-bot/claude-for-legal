# Mẫu tài liệu

## 1. PRD (bước 1)
```markdown
# PRD: <tên tính năng> · v<số> · <ngày>
## Bối cảnh và vấn đề           (ai đang gặp gì, bằng chứng)
## Mục tiêu / không phải mục tiêu
## Người dùng và vai trò
## Quy trình nghiệp vụ đề xuất   (AS-IS → TO-BE, mermaid nếu cần)
## Danh sách UC                  (mã UC-xxx, tên, vai trò, mức ưu tiên)
## Mô hình dữ liệu (nháp)        (đối tượng, trường, quan hệ)
## Sơ đồ trạng thái (nháp)
## Câu hỏi làm rõ / gap          (đánh số; trạng thái: mở / PO đã trả lời <ngày>)
## Giả định                      (mục nào AI tự giả định, chờ PO xác nhận)
## Ngoài phạm vi
```

## 2. Sổ UC Master – `docs/uc-master.yaml`
```yaml
project: <mã dự án>
gates:                       # biên bản chốt; thiếu by/date = chưa qua
  - {id: GATE-1, scope: "PRD v1.2", by: "<họ tên, chức vụ>", date: 2026-10-05, notes: ""}
use_cases:
  - id: UC-001
    name: Đối soát trình tự hồ sơ
    status: live              # draft | approved | built | tested | live | retired
    screens: [MH-01]          # mã màn hình (đặc tả)
    stories: [US-001, US-002]
    apis: [API-check]         # hoặc [] nếu không có API
    tests: [TC-001, TC-002]
    hdsd: [HDSD-2.1]          # mục trong hướng dẫn sử dụng
    gates: [GATE-1, GATE-2, GATE-3]
    cr: [CR-003]              # CR đã tác động UC này
tests:                        # để phát hiện test trỏ tới UC không tồn tại
  - {id: TC-001, uc: UC-001, result: pass}   # pass | fail | not_run
```

## 3. Biên bản GATE
```markdown
# Biên bản <GATE-x> · <dự án> · <ngày>
- Tài liệu được chốt: <tên, phiên bản, đường dẫn>
- Phạm vi: <UC-xxx…>
- Người chốt: <họ tên, chức vụ>     Người trình: <…>
- Kết luận: Chấp thuận / Chấp thuận có điều kiện / Chưa chấp thuận
- Điều kiện kèm theo và hạn: <…>
- Mục còn mở: <…>
```

## 4. Phiếu CR
```markdown
# CR-<số>: <tên> · người đề nghị · ngày
- Mô tả thay đổi (AS-IS → TO-BE)
- Phân loại: LỚN / NHỎ  (bảng 8 câu hỏi trong phan-loai-cr.md, kèm câu trả lời)
- Phân tích ảnh hưởng: UC trực tiếp / gián tiếp; test chạy lại; HDSD sửa; dữ liệu cũ
- UC mới đăng ký: <UC-xxx>
- GATE CR: người duyệt, ngày, kết luận
```

## 5. SA hiện trạng – `docs/sa-hien-trang.md`
Thành phần · luồng dữ liệu · mô hình dữ liệu · tích hợp ngoài · cấu hình môi trường · nợ kỹ thuật ·
"Cập nhật lần cuối: <ngày>, sau <CR/phiên bản>".

## 6. HDSD (khung, thay bằng template của đơn vị nếu có)
```markdown
# Hướng dẫn sử dụng <phần mềm> · phiên bản · ngày
## 1. Giới thiệu, đối tượng sử dụng, yêu cầu máy
## 2. <Chức năng> (UC-xxx)
   - Mục đích · Ai dùng · Điều kiện trước
   - Các bước (mỗi bước một ảnh chụp từ bản đã test, có chú thích)
   - Kết quả mong đợi · Lỗi thường gặp và cách xử lý
## Phụ lục: bảng mã lỗi, liên hệ hỗ trợ
```
