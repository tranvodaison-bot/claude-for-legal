# cross-check-engine

Engine đối soát hồ sơ dự án đầu tư xây dựng theo hai trục:
1. **Trình tự - điều kiện tiên quyết** giữa các bước (G1).
2. **Hiệu lực và chuyển tiếp pháp luật 2021-2026**: căn cứ mà từng văn bản dự án viện dẫn có còn
   hiệu lực tại ngày ký không, nếu đã hết thì có thuộc trường hợp chuyển tiếp không. Đầu ra là **bản nháp hỗ trợ rà soát**,
không phải kết luận pháp lý hay thẩm định; người ký/duyệt vẫn là người chịu trách nhiệm.

## Chạy nhanh

Điều kiện: Python 3.10+ và PyYAML (`pip install pyyaml`; test cần thêm `pytest`).

```bash
cd cross-check-engine
python3 -m crosscheck examples/du_an_mau.yaml                 # báo cáo Markdown ra màn hình
python3 -m crosscheck examples/du_an_nhieu_nam.yaml           # dự án 2020-2026: hiệu lực + chuyển tiếp
python3 -m crosscheck examples/du_an_mau.yaml --format json   # JSON
python3 -m crosscheck <ho_so.yaml> --out bao_cao.md           # ghi file (không ghi đè file có sẵn)
python3 -m pytest -q                                           # chạy test
```

Mã thoát: `0` không có lỗi cứng, `1` có ít nhất một lỗi cứng, `2` lỗi đầu vào/cấu hình.

## Bốn mức phát hiện

| Mức | Ý nghĩa |
|---|---|
| HARD (đỏ) | Vi phạm tiên quyết/trình tự; hoặc viện dẫn căn cứ hết/chưa có hiệu lực **khi toàn bộ dữ liệu đã đối chiếu văn bản gốc** |
| SOFT (vàng) | Tiên quyết mức mềm, nhập liệu sai logic, hoặc kết luận về hiệu lực **dựa trên dữ liệu chưa xác minh** (ghi "cần xác minh") |
| DATA_GAP (xám) | Thiếu dữ liệu nên **chưa kết luận được**; không tính là vi phạm |
| INFO (xanh) | Văn bản cũ được áp dụng theo chuyển tiếp (kèm lý do), thiếu viện dẫn văn bản sửa đổi, viện dẫn VBHN |

Mỗi phát hiện nêu: sai ở đâu, căn cứ, độ tin cậy, cách khắc phục, truy vết.

## Hiệu lực và chuyển tiếp

- `data/legal_registry.yaml` - sổ văn bản theo 13 lĩnh vực (Luật XD, NĐ hoạt động XD, chi phí, chất lượng,
  hợp đồng, đấu thầu, đầu tư, đầu tư công, đất đai, môi trường, PCCC, thẩm quyền). Mỗi văn bản có ngày
  hiệu lực, **hiệu lực từng phần** (ví dụ Luật 135/2025), quan hệ thay thế/sửa đổi/hợp nhất và **mức nguồn**:
  `primary` (đã đối chiếu văn bản gốc), `secondary` (trang thứ cấp), `recall` (chưa tra cứu).
  Ngày hết hiệu lực được suy ra từ văn bản thay thế; khai báo mâu thuẫn hoặc chồng khoảng hiệu lực bị từ chối.
- `data/transition_rules.yaml` - quy tắc chuyển tiếp: khi văn bản dự án viện dẫn văn bản đã hết hiệu lực,
  văn bản cũ chỉ được tiếp tục áp dụng nếu **ngày quyết định** (ngày nộp hồ sơ, ngày ký hợp đồng, ngày phát
  hành HSMT, ngày phê duyệt dự án) trước ngày văn bản mới có hiệu lực.
- Báo cáo có **bản đồ chế độ pháp lý**: văn bản chính có hiệu lực tại ngày từng bước của dự án.
- Căn cứ của quy tắc trình tự khai báo theo lĩnh vực và được tra theo ngày sự kiện (không gắn cứng số hiệu).

Văn bản dự án khai báo trong `documents` của hồ sơ (xem `examples/du_an_nhieu_nam.yaml`):
`ngay_ky`, tùy chọn `ngay_nop`, `ngay_phat_hanh_hsmt`, `hop_dong` (mã trong `contracts`), và `can_cu` -
mỗi căn cứ là chuỗi số hiệu/tên, hoặc `{van_ban, dieu_khoan}` khi viện dẫn điều khoản có hiệu lực riêng.

## Định dạng hồ sơ dự án

Xem `examples/du_an_mau.yaml` (dữ liệu giả lập). Trạng thái bước: `not_started`,
`in_progress`, `completed`, `not_applicable` (kèm `na_basis`). Ngày dạng `YYYY-MM-DD`.
`attributes` khai báo các thuộc tính quyết định bước nào bắt buộc (ví dụ
`requires_permit`); thuộc tính chưa khai báo cho ra DATA_GAP chứ không đoán.

## Sửa quy tắc

Quy tắc nằm ở `data/procedure_rules.yaml` (không cần sửa code). Engine kiểm tra khi nạp:
trùng id, tham chiếu tiên quyết không tồn tại, severity sai, vòng lặp tiên quyết.

## Giới hạn đã biết

- **Không có ngày hiệu lực nào ở mức `primary`.** Văn bản 2026 ở mức `secondary`; phần lớn văn bản
  2014-2024 ở mức `recall` (chưa tra). Vì vậy hiện **không có kết luận hiệu lực nào lên mức đỏ**.
- **Quy tắc chuyển tiếp là khung giả thuyết** theo mẫu thường gặp, chưa có số điều/khoản; chuyển tiếp chi phí
  thực tế tách nhiều trường hợp (TMĐT, dự toán, gói thầu) mà quy tắc hiện gộp một điều kiện.
- Chưa có: Thông tư, QCVN/TCVN, luật/nghị định ngoài 13 lĩnh vực; các luật sửa đổi Luật Đầu tư, Luật Đầu tư công
  sau 2025; quan hệ hiệu lực từng phần của văn bản **cũ** (điều khoản Luật 2014 bị thay sớm từ 01/01/2026);
  hiệu lực hồi tố của NĐ 140/2025; văn bản mà VBHN 91/2026 hợp nhất.
- Bản đồ chế độ pháp lý chỉ theo ngày sự kiện, chưa xét chuyển tiếp; kết luận chuyển tiếp nằm ở phần phát hiện.
- **Căn cứ pháp lý chưa xác minh.** Mọi `basis` đang `verified: false` và chưa có điều/khoản.
  Chuỗi trình tự lấy từ bản thiết kế của Ban QLDA, chưa đối chiếu văn bản gốc.
- Một số quy tắc đáng ngờ đã gắn mức `soft` kèm `note` (khảo sát ← phê duyệt dự án;
  GPXD ← thiết kế đã phê duyệt, vì có trường hợp cấp phép theo giai đoạn).
- **Chưa có** hiệu lực văn bản và điều khoản chuyển tiếp (Giai đoạn 2). Engine không biết
  dự án áp dụng văn bản cũ hay mới; không dùng để kết luận "áp dụng sai văn bản".
- Chưa có đối soát nhất quán dữ liệu, năng lực nhà thầu, dashboard, chạy tự động khi dữ liệu đổi.
- Chưa có bộ trích xuất PDF/Word; hồ sơ phải được nhập thành YAML.
- Mỗi bước chỉ có một ngày bắt đầu và một ngày hoàn thành; chưa mô hình hóa nhiều đợt/hạng mục.

## Kế hoạch tiếp theo

Xem `docs/PLOS-danh-gia-va-ke-hoach.md`.

## Gỡ bỏ

Thư mục này độc lập với marketplace; xóa `cross-check-engine/` là gỡ hoàn toàn.
