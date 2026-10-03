"""Xuất báo cáo Markdown / JSON từ danh sách phát hiện."""
from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from dataclasses import asdict

from .engine import GAP, HARD, SOFT, Finding

LABEL = {HARD: "ĐỎ - lỗi cứng", SOFT: "VÀNG - lỗi mềm", GAP: "XÁM - thiếu dữ liệu"}
DISCLAIMER = ("Bản nháp hỗ trợ rà soát, không phải kết luận pháp lý hay thẩm định. "
              "Căn cứ ghi `chưa xác minh` phải được đối chiếu văn bản gốc trước khi sử dụng.")


def _basis(b: list) -> str:
    if not b:
        return "không có (quy tắc chưa gắn căn cứ)"
    parts = []
    for x in b:
        prov = x.get("provision") or "chưa điền điều/khoản"
        mark = "" if x.get("verified") else " - chưa xác minh"
        parts.append(f"{x['doc']}, {prov}{mark}")
    return "; ".join(parts)


def to_markdown(project: dict, findings: list[Finding], as_of: dt.date) -> str:
    meta = project.get("project") or {}
    c = Counter(f.severity for f in findings)
    lines = [f"# Báo cáo đối soát trình tự - {meta.get('name', 'dự án')}",
             f"Mã dự án: {meta.get('id', '-')} | Ngày đối soát: {as_of.strftime('%d/%m/%Y')}", "",
             "| Mức | Số phát hiện |", "|---|---|"]
    lines += [f"| {LABEL[s]} | {c.get(s, 0)} |" for s in (HARD, SOFT, GAP)]
    lines.append("")
    for sev in (HARD, SOFT, GAP):
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        lines += [f"## {LABEL[sev]}", ""]
        for i, f in enumerate(group, 1):
            lines += [f"### {i}. {f.title} (`{f.rule_id}`)",
                      f"- **Sai ở đâu:** {f.where}",
                      f"- **Căn cứ:** {_basis(f.basis)}",
                      f"- **Cách khắc phục:** {f.fix or 'chưa có hướng dẫn'}",
                      "- **Truy vết:**", *[f"  - {t}" for t in f.trace], ""]
    if not findings:
        lines += ["Không có phát hiện nào.", ""]
    lines += ["---", f"_{DISCLAIMER}_", ""]
    return "\n".join(lines)


def to_json(project: dict, findings: list[Finding], as_of: dt.date) -> str:
    return json.dumps({"project": project.get("project"), "as_of": as_of.isoformat(),
                       "disclaimer": DISCLAIMER, "findings": [asdict(f) for f in findings]},
                      ensure_ascii=False, indent=2) + "\n"
