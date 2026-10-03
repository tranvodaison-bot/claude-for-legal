# User stories

US-001…005: viết bù ngày 03/10/2026 cho chức năng đã dựng trước khi có quy trình (mô tả hành vi hiện có,
không thêm chức năng). US-007a…f: thuộc CR-001 - nội dung tại docs/spec/SPEC-CR-001.md mục 5 (đã qua GATE, đã dựng, kiểm bằng TC-NQ, TC-UI).

## US-001 · UC-001 · Đối soát trình tự - tiên quyết
Là cán bộ Ban QLDA, tôi muốn biết bước nào đã làm khi bước tiên quyết chưa xong hoặc làm sớm hơn ngày
bước tiên quyết hoàn thành, để xử lý trước khi bị thanh tra/kiểm toán phát hiện.
- Given bước B đã `completed`, tiên quyết A (mức hard) `not_started` → When chạy đối soát → Then có phát hiện ĐỎ `PRE-B-A`.
- Given cả hai `completed`, ngày B < ngày A → Then ĐỎ `TEMP-B-A`, nêu hai ngày.
- Given A chưa khai báo trong hồ sơ → Then XÁM (thiếu dữ liệu), không phải ĐỎ.
Kiểm bằng: `tests/test_engine.py` (TC-ENG).

## US-002 · UC-002 · Hiệu lực căn cứ viện dẫn và chuyển tiếp
Là pháp chế, tôi muốn biết văn bản dự án nào viện dẫn căn cứ chưa có/hết hiệu lực tại ngày ký, và nếu hết
hiệu lực thì có thuộc trường hợp chuyển tiếp không, kèm lý do.
- Given văn bản ký sau ngày văn bản cũ hết hiệu lực, ngày quyết định < ranh giới → Then XANH "áp dụng chuyển tiếp" nêu điều kiện.
- Given không điều kiện nào thỏa → Then VÀNG (hoặc ĐỎ nếu toàn bộ dữ liệu `primary` và quy tắc đã xác minh).
- Given thiếu ngày quyết định → Then XÁM nêu ngày còn thiếu.
Kiểm bằng: `tests/test_temporal.py` (TC-TMP).

## US-003 · UC-003 · Bản đồ chế độ pháp lý
Là kiểm toán viên, tôi muốn thấy văn bản chính có hiệu lực tại ngày từng bước của dự án, để biết dự án
trải qua những chế độ pháp lý nào.
- Given bước có ngày 03/03/2021 → Then cột NĐ hoạt động XD hiện 15/2021/NĐ-CP; ngày 02/03/2021 → 59/2015/NĐ-CP.
Kiểm bằng: `tests/test_temporal.py` (TC-TMP).

## US-004 · UC-004 · Báo cáo web
Là lãnh đạo Ban QLDA, tôi muốn mở một file báo cáo, thấy ngay điểm cần xử lý, lọc, mở truy vết, xuất CSV
và in, không cần cài phần mềm.
- Given báo cáo có phát hiện ĐỎ → When lọc mức ĐỎ và xuất CSV → Then CSV đúng số dòng đang hiện, ô bắt đầu bằng `=` bị vô hiệu hóa.
- Given dữ liệu chứa `<script>` → Then hiện nguyên văn, không thực thi.
Kiểm bằng: `tests/test_dashboard.py` (TC-DSB), `tests/ui_acceptance.mjs` (TC-UI).

## US-005 · UC-005 · Báo cáo Markdown / JSON
Là người dùng kỹ thuật, tôi muốn xuất kết quả dạng Markdown/JSON để lưu hồ sơ hoặc nạp sang hệ thống khác.
- Given `--format json` → Then JSON có `findings`, `regime_map`, `disclaimer`; mã thoát 1 khi có ĐỎ.
Kiểm bằng: `tests/test_engine.py` (TC-ENG).
