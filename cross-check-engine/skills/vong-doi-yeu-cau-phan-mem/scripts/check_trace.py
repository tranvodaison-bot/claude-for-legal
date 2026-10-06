#!/usr/bin/env python3
"""Kiểm sổ UC Master: truy vết UC -> US/API/màn hình -> test -> HDSD và biên bản GATE.

Dùng: python3 check_trace.py docs/uc-master.yaml [--strict]
Mã thoát: 0 sạch (hoặc chỉ có cảnh báo khi không --strict), 1 có lỗi, 2 không đọc được file.
Định dạng sổ: xem references/mau-tai-lieu.md mục 2.
"""
from __future__ import annotations

import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    print("Cần PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ORDER = ["draft", "approved", "built", "tested", "live"]


def check(data: dict) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    gates = {}
    for g in data.get("gates") or []:
        gid = g.get("id")
        if not gid:
            errors.append(f"GATE thiếu id: {g}")
            continue
        gates[gid] = g
        if not g.get("by") or not g.get("date"):
            errors.append(f"{gid}: chưa có người chốt/ngày chốt -> chưa qua GATE")

    tests = {}
    for t in data.get("tests") or []:
        tests[t.get("id")] = t
        if t.get("result") not in ("pass", "fail", "not_run"):
            errors.append(f"{t.get('id')}: result phải là pass | fail | not_run")

    ucs, referenced_tests = {}, set()
    for uc in data.get("use_cases") or []:
        uid = uc.get("id")
        if not uid:
            errors.append(f"UC thiếu id: {uc.get('name')}")
            continue
        if uid in ucs:
            errors.append(f"{uid}: trùng mã UC")
        ucs[uid] = uc
        status = uc.get("status", "draft")
        if status == "retired":
            continue
        if status not in ORDER:
            errors.append(f"{uid}: status `{status}` không hợp lệ ({' | '.join(ORDER)} | retired)")
            continue
        level = ORDER.index(status)
        for gid in uc.get("gates") or []:
            if gid not in gates:
                errors.append(f"{uid}: tham chiếu {gid} không có trong danh sách gates")
        for tid in uc.get("tests") or []:
            referenced_tests.add(tid)
            if tid not in tests:
                warns.append(f"{uid}: test {tid} chưa khai báo trong mục tests (không biết kết quả)")
        if level >= ORDER.index("approved"):
            if not uc.get("gates"):
                errors.append(f"{uid}: trạng thái `{status}` nhưng không gắn GATE nào")
            if not uc.get("stories"):
                errors.append(f"{uid}: trạng thái `{status}` nhưng chưa có user story")
        if level >= ORDER.index("built") and not (uc.get("screens") or uc.get("apis")):
            warns.append(f"{uid}: không có màn hình lẫn API - kiểm lại UC chỉ chạy nền hay thiếu đặc tả")
        if level >= ORDER.index("tested"):
            ts = uc.get("tests") or []
            if not ts:
                errors.append(f"{uid}: trạng thái `{status}` nhưng không có testcase")
            bad = [t for t in ts if (tests.get(t) or {}).get("result") != "pass"]
            if bad:
                errors.append(f"{uid}: trạng thái `{status}` nhưng test chưa đạt/chưa chạy: {', '.join(bad)}")
        if level >= ORDER.index("live") and not uc.get("hdsd"):
            errors.append(f"{uid}: đã LIVE nhưng chưa có mục HDSD")

    for tid, t in tests.items():
        if t.get("uc") not in ucs:
            errors.append(f"{tid}: trỏ tới UC không tồn tại `{t.get('uc')}`")
        elif tid not in referenced_tests:
            warns.append(f"{tid}: có trong mục tests nhưng UC {t.get('uc')} không liệt kê")
    return errors, warns


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    strict = "--strict" in args
    args = [a for a in args if a != "--strict"]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        with open(args[0], encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        print(f"Không đọc được {args[0]}: {e}", file=sys.stderr)
        return 2
    errors, warns = check(data)
    ucs = data.get("use_cases") or []
    by_status: dict = {}
    for uc in ucs:
        by_status[uc.get("status", "draft")] = by_status.get(uc.get("status", "draft"), 0) + 1
    print(f"Dự án {data.get('project', '?')}: {len(ucs)} UC "
          + ", ".join(f"{k}={v}" for k, v in sorted(by_status.items()))
          + f"; {len(data.get('gates') or [])} GATE; {len(data.get('tests') or [])} test")
    for e in errors:
        print(f"LỖI      {e}")
    for w in warns:
        print(f"CẢNH BÁO {w}")
    if not errors and not warns:
        print("Sạch: mọi UC truy vết đủ theo trạng thái của nó.")
    return 1 if errors or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
