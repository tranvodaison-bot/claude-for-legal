"""Xuất báo cáo Markdown / JSON từ danh sách phát hiện."""
from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from dataclasses import asdict

from .engine import GAP, HARD, INFO, SOFT, Finding

LEVELS = (HARD, SOFT, GAP, INFO)
LABEL = {HARD: "ĐỎ - lỗi cứng", SOFT: "VÀNG - lỗi mềm / cần xác minh", GAP: "XÁM - thiếu dữ liệu",
         INFO: "XANH - thông tin, chuyển tiếp được áp dụng"}
DISCLAIMER = ("Bản nháp hỗ trợ rà soát, không phải kết luận pháp lý hay thẩm định. "
              "Căn cứ và ngày hiệu lực chưa ở mức `đã đối chiếu văn bản gốc` phải được kiểm tra trước khi sử dụng; "
              "kết luận dựa trên dữ liệu chưa xác minh bị giới hạn tối đa ở mức VÀNG.")


def _basis(b: list) -> str:
    if not b:
        return "không có (quy tắc chưa gắn căn cứ)"
    parts = []
    for x in b:
        prov = x.get("provision") or "chưa điền điều/khoản"
        mark = "" if x.get("verified") else " - chưa xác minh"
        note = f" ({x['note']})" if x.get("note") else ""
        parts.append(f"{x['doc']}, {prov}{mark}{note}")
    return "; ".join(parts)


def _regime_table(regime: list, domains: dict) -> list[str]:
    cols = list(regime[0]["cells"]) if regime else []
    lines = ["## Bản đồ chế độ pháp lý theo ngày sự kiện",
             "_Văn bản chính có hiệu lực tại ngày của từng bước, CHƯA xét chuyển tiếp._", "",
             "| Bước | Ngày | " + " | ".join(domains.get(c, c) for c in cols) + " |",
             "|---|---|" + "---|" * len(cols)]
    for r in regime:
        lines.append(f"| {r['step']} | {r['date'].strftime('%d/%m/%Y')} | "
                     + " | ".join(r["cells"][c] for c in cols) + " |")
    return lines + [""]


RESULT = {"khop": "✓ Khớp", "lech": "▲ Lệch", "vuot": "▲ Vượt", "trong_han_muc": "✓ Trong hạn mức",
          "thieu_chuan": "○ Thiếu chuẩn"}


def _consistency_md(matrix: dict) -> list[str]:
    lines = ["## Bảng đối chiếu thông tin",
             "_So từng văn bản với văn bản chuẩn có hiệu lực tại ngày ký của nó._", ""]
    for block in matrix.values():
        lines += [f"### {block['label']}", "", "| Văn bản | Nhóm | Ngày ký | Giá trị | Chuẩn so sánh | Kết quả |",
                  "|---|---|---|---|---|---|"]
        for r in block["rows"]:
            res = RESULT[r["result"]] + (f": {r['note']}" if r["note"] and r["result"] == "thieu_chuan" else "")
            val = r["value"] + (f" ({r['extra']})" if r.get("extra") else "")
            lines.append(f"| {r['doc']} | {r['group']} | {r['date'].strftime('%d/%m/%Y')} | {val} | "
                         f"{r['master'] or '-'} | {res} |")
        lines.append("")
    return lines


def to_markdown(project: dict, findings: list[Finding], as_of: dt.date, regime=None, domains=None,
                consistency=None) -> str:
    meta = project.get("project") or {}
    c = Counter(f.severity for f in findings)
    lines = [f"# Báo cáo đối soát - {meta.get('name', 'dự án')}",
             f"Mã dự án: {meta.get('id', '-')} | Ngày đối soát: {as_of.strftime('%d/%m/%Y')}", "",
             "| Mức | Số phát hiện |", "|---|---|"]
    lines += [f"| {LABEL[s]} | {c.get(s, 0)} |" for s in LEVELS]
    lines.append("")
    if regime:
        lines += _regime_table(regime, domains or {})
    if consistency:
        lines += _consistency_md(consistency)
    for sev in LEVELS:
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        lines += [f"## {LABEL[sev]}", ""]
        for i, f in enumerate(group, 1):
            lines += [f"### {i}. {f.title} (`{f.rule_id}`)",
                      f"- **Sai ở đâu:** {f.where}",
                      f"- **Căn cứ:** {_basis(f.basis)}",
                      f"- **Độ tin cậy:** {'so sánh dữ liệu khai báo' if f.rule_id.startswith('NQ-') else 'đã xác minh' if f.verified else 'cần xác minh'}",
                      f"- **Cách khắc phục:** {f.fix or 'chưa có hướng dẫn'}",
                      "- **Truy vết:**", *[f"  - {t}" for t in f.trace], ""]
    if not findings:
        lines += ["Không có phát hiện nào.", ""]
    lines += ["---", f"_{DISCLAIMER}_", ""]
    return "\n".join(lines)


def to_json(project: dict, findings: list[Finding], as_of: dt.date, regime=None, domains=None,
            consistency=None) -> str:
    reg = [{"step": r["step"], "date": r["date"].isoformat(), "cells": r["cells"]} for r in regime or []]
    cons = {k: {"label": b["label"], "rows": [{**r, "date": r["date"].isoformat()} for r in b["rows"]]}
            for k, b in (consistency or {}).items()}
    return json.dumps({"project": project.get("project"), "as_of": as_of.isoformat(),
                       "disclaimer": DISCLAIMER, "regime_map": reg, "consistency": cons,
                       "findings": [asdict(f) for f in findings]},
                      ensure_ascii=False, indent=2) + "\n"
