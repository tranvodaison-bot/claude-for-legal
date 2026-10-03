# cross-check-engine

Engine đối soát trình tự - điều kiện tiên quyết của hồ sơ dự án đầu tư xây dựng
(Giai đoạn 1 của "Bản đồ pháp lý dự án"). Đầu ra là **bản nháp hỗ trợ rà soát**,
không phải kết luận pháp lý hay thẩm định; người ký/duyệt vẫn là người chịu trách nhiệm.

## Chạy nhanh

Điều kiện: Python 3.10+ và PyYAML (`pip install pyyaml`; test cần thêm `pytest`).

```bash
cd cross-check-engine
python3 -m crosscheck examples/du_an_mau.yaml                 # báo cáo Markdown ra màn hình
python3 -m crosscheck examples/du_an_mau.yaml --format json   # JSON
python3 -m crosscheck <ho_so.yaml> --out bao_cao.md           # ghi file (không ghi đè file có sẵn)
python3 -m pytest -q                                           # chạy test
```

Mã thoát: `0` không có lỗi cứng, `1` có ít nhất một lỗi cứng, `2` lỗi đầu vào/cấu hình.

## Ba mức phát hiện

| Mức | Ý nghĩa |
|---|---|
| HARD (đỏ) | Làm trước khi bước tiên quyết bắt buộc hoàn thành, hoặc ngày thực hiện sớm hơn ngày hoàn thành bước tiên quyết |
| SOFT (vàng) | Tiên quyết mức mềm, thiếu căn cứ khi đánh dấu không áp dụng, ngày tháng nhập sai logic |
| DATA_GAP (xám) | Thiếu dữ liệu nên **chưa kết luận được**; không tính là vi phạm |

Mỗi phát hiện nêu: sai ở đâu, căn cứ, cách khắc phục, truy vết (bước + bước tiên quyết + chứng cứ).

## Định dạng hồ sơ dự án

Xem `examples/du_an_mau.yaml` (dữ liệu giả lập). Trạng thái bước: `not_started`,
`in_progress`, `completed`, `not_applicable` (kèm `na_basis`). Ngày dạng `YYYY-MM-DD`.
`attributes` khai báo các thuộc tính quyết định bước nào bắt buộc (ví dụ
`requires_permit`); thuộc tính chưa khai báo cho ra DATA_GAP chứ không đoán.

## Sửa quy tắc

Quy tắc nằm ở `data/procedure_rules.yaml` (không cần sửa code). Engine kiểm tra khi nạp:
trùng id, tham chiếu tiên quyết không tồn tại, severity sai, vòng lặp tiên quyết.

## Giới hạn đã biết

- **Căn cứ pháp lý chưa xác minh.** Mọi `basis` đang `verified: false` và chưa có điều/khoản.
  Chuỗi trình tự lấy từ bản thiết kế của Ban QLDA, chưa đối chiếu văn bản gốc.
- Một số quy tắc đáng ngờ đã gắn mức `soft` kèm `note` (khảo sát ← phê duyệt dự án;
  GPXD ← thiết kế đã phê duyệt, vì có trường hợp cấp phép theo giai đoạn).
- **Chưa có** hiệu lực văn bản và điều khoản chuyển tiếp (Giai đoạn 2). Engine không biết
  dự án áp dụng văn bản cũ hay mới; không dùng để kết luận "áp dụng sai văn bản".
- Chưa có đối soát nhất quán dữ liệu, năng lực nhà thầu, dashboard, chạy tự động khi dữ liệu đổi.
- Chưa có bộ trích xuất PDF/Word; hồ sơ phải được nhập thành YAML.
- Mỗi bước chỉ có một ngày bắt đầu và một ngày hoàn thành; chưa mô hình hóa nhiều đợt/hạng mục.

## Gỡ bỏ

Thư mục này độc lập với marketplace; xóa `cross-check-engine/` là gỡ hoàn toàn.
