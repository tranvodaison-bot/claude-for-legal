# cross-check-engine - quy tắc làm việc

Dự án này được phát triển theo skill `skills/vong-doi-yeu-cau-phan-mem` (vòng đời có GATE) và
`skills/dac-ta-ui-nghiep-vu` (giao diện). Đọc `docs/sa-hien-trang.md` trước khi sửa code.

- Mọi thay đổi chức năng đi qua: phân loại CR (`docs/cr/`) → PRD/đặc tả (`docs/prd/`, `docs/spec/`) →
  GATE có biên bản (`docs/gates/`) → code → test → HDSD. Không code phần chưa qua GATE.
- Trước mỗi GATE và trước khi báo xong: `python3 skills/vong-doi-yeu-cau-phan-mem/scripts/check_trace.py docs/uc-master.yaml`.
- Kiểm tra: `python3 -m pytest -q`; sửa giao diện thì thêm `node tests/ui_acceptance.mjs` và
  `node skills/dac-ta-ui-nghiep-vu/scripts/check_layout.mjs <báo cáo.html>`, rồi xem ảnh chụp.
- Đặc tả là chuẩn: test lệch thì sửa code; đặc tả sai thì mở CR. Tối đa 3 vòng tự sửa.
- Căn cứ pháp lý: không tự nâng `level` lên `primary`, không điền điều/khoản từ trí nhớ.
- Hai hồ sơ mẫu cũ (`du_an_mau`, `du_an_nhieu_nam`) phải cho báo cáo Markdown y hệt sau mỗi CR không chạm chúng.
- Điều phối agent (explorer / worker / researcher, advisor): `claude-config/README.md`.
