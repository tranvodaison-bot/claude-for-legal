# SA hiện trạng - cross-check-engine

Cập nhật lần cuối: 03/10/2026, sau CR-001 (đối soát nhất quán thông tin).

## 1. Thành phần

| Thành phần | Tệp | Vai trò |
|---|---|---|
| CLI | `crosscheck/cli.py`, `__main__.py` | Nạp dữ liệu, gọi các bước đối soát, chọn định dạng xuất, mã thoát (0/1/2) |
| Engine trình tự | `crosscheck/engine.py` | Mô hình `Finding`; nạp/kiểm `procedure_rules.yaml` (trùng id, tham chiếu hỏng, vòng lặp); đánh giá tiên quyết và thứ tự thời gian; tra căn cứ theo lĩnh vực + ngày |
| Engine thời gian | `crosscheck/temporal.py` | Sổ văn bản (`Registry`), hiệu lực từng phần, suy ngày hết hiệu lực, quy tắc chuyển tiếp, đối soát căn cứ viện dẫn, bản đồ chế độ pháp lý |
| Engine nhất quán | `crosscheck/consistency.py` | Nạp/kiểm `consistency_rules.yaml`; chuỗi phiên bản văn bản (`thay_the` + ngày ký); so văn bản đích với chuẩn có hiệu lực tại ngày ký; bảng đối chiếu (CR-001) |
| Báo cáo văn bản | `crosscheck/report.py` | Markdown, JSON |
| Báo cáo web | `crosscheck/dashboard.py` | HTML tự chứa: tổng quan, cần xử lý, bản đồ chế độ, danh sách phát hiện, lọc, CSV, in |

## 2. Luồng dữ liệu

```
project.yaml ──┐
procedure_rules.yaml ──► engine.evaluate ─────────────┐
legal_registry.yaml ──► temporal.load_registry ───────┤
transition_rules.yaml ─► temporal.check_citations ────┼─► findings (sắp theo mức) ─► md | json | html
consistency_rules.yaml ► consistency.check_consistency┤        + regime map + bảng đối chiếu
                         temporal.regime_map ─────────┘
```

## 3. Mô hình dữ liệu (YAML, chưa có CSDL)

- **Hồ sơ dự án:** `project{id,name}`, `attributes{...}`, `steps{step_id: {status, date, start_date, evidence, na_basis}}`,
  `contracts{ma: {ngay_ky}}`, `key_dates{}`, `documents[{id, loai, nhom, ngay_ky, ngay_nop, ngay_phat_hanh_hsmt, hop_dong,
  can_cu[], thay_the[], thong_tin{ten_du_an, tong_muc_dau_tu, von_duoc_giao, dien_tich_san, chieu_cao, so_tang,
  thoi_gian_thuc_hien{tu, den}}}]`.
- **Quy tắc nhất quán:** `groups{}`, `fields{label, kind, unit}`, `rules[{id, fields, master, master_field, targets,
  compare (equal_text|equal_number|within_period|sum_not_exceed), tolerance{abs,pct}, severity, applies_if, fix}]`.
- **Quy tắc trình tự:** `steps[{id, name, phase, applies_if, prerequisites[{step, severity, basis[], fix, note}]}]`.
- **Sổ văn bản:** `documents[{id, so_hieu, ten, domain, role, hieu_luc_tu, het_hieu_luc, partial_effect, replaces, amends, level, derive_expiry}]`.
- **Quy tắc chuyển tiếp:** `transitions[{id, from, to, boundary, allow_old_if[{date_ref, label}], basis}]`.
- **Finding:** `severity (HARD|SOFT|DATA_GAP|INFO), rule_id, step, title, where, basis[], fix, trace[], verified`.

## 4. Tích hợp ngoài
Không có. Không gọi mạng; báo cáo HTML không tải tài nguyên ngoài.

## 5. Kiểm thử
`tests/test_engine.py`, `tests/test_temporal.py`, `tests/test_dashboard.py`, `tests/test_consistency.py`
(pytest, 80 test); `tests/ui_acceptance.mjs` (Playwright, 17 trường hợp); sổ truy vết `docs/uc-master.yaml` + `check_trace.py`.

## 6. Nợ kỹ thuật / giới hạn đã biết
- `thong_tin` nhập tay; chưa trích tự động từ PDF/Word (M4) - số liệu là khai báo, chưa ai xác minh.
- Trên điện thoại, bảng đối chiếu cuộn ngang, cột Kết quả nằm cuối (đúng đặc tả đã chốt; đề xuất CR-002).
- Chưa có CSDL, vòng đời Finding, phân quyền (kế hoạch M1, M3, M5).
- Mọi ngày hiệu lực chưa ở mức `primary`.
