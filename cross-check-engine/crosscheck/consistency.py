"""Đối soát nhất quán thông tin giữa các văn bản dự án (CR-001, đặc tả docs/spec/SPEC-CR-001.md).

Mỗi văn bản đích được so với văn bản chuẩn mới nhất (thuộc nhóm chuẩn, có trường cần so) ký trước hoặc
cùng ngày văn bản đích - văn bản cũ không bị báo oan khi dự án điều chỉnh về sau.
"""
from __future__ import annotations

import re
import unicodedata

from .engine import GAP, HARD, SOFT, Finding, RuleError, _fmt, _load_yaml, parse_date

COMPARES = {"equal_text": "text", "equal_number": "number", "within_period": "period", "sum_not_exceed": "number"}
BASIS = [{"doc": "Nguyên tắc nhất quán dữ liệu (đặc tả gốc §3.4, PRD-CR-001)",
          "provision": "không áp dụng - so sánh dữ liệu dự án", "verified": True}]


def load_consistency_rules(path) -> dict:
    data = _load_yaml(path)
    groups, fields = data.get("groups") or {}, data.get("fields") or {}
    for fid, f in fields.items():
        if f.get("kind") not in ("text", "number", "period"):
            raise RuleError(f"{path}: trường `{fid}` cần kind text | number | period")
    seen, rules = set(), []
    for r in data.get("rules") or []:
        rid = r.get("id")
        if not rid or rid in seen:
            raise RuleError(f"{path}: quy tắc thiếu id hoặc trùng id: {rid}")
        seen.add(rid)
        kind = COMPARES.get(r.get("compare"))
        if kind is None:
            raise RuleError(f"{path}: `{rid}` compare phải là {' | '.join(COMPARES)}")
        if r.get("severity") not in ("hard", "soft"):
            raise RuleError(f"{path}: `{rid}` severity phải là hard | soft")
        for g in [r.get("master")] + list(r.get("targets") or []):
            if g not in groups:
                raise RuleError(f"{path}: `{rid}` tham chiếu nhóm văn bản không khai báo: {g}")
        if not r.get("targets") or not r.get("fields"):
            raise RuleError(f"{path}: `{rid}` cần fields và targets")
        for fid in list(r["fields"]) + ([r["master_field"]] if r.get("master_field") else []):
            if fid not in fields:
                raise RuleError(f"{path}: `{rid}` tham chiếu trường không khai báo: {fid}")
            if fields[fid]["kind"] != kind:
                raise RuleError(f"{path}: `{rid}` so `{r['compare']}` không hợp với trường `{fid}` ({fields[fid]['kind']})")
        rules.append(r)
    return {"groups": groups, "fields": fields, "rules": rules}


def _norm_text(s) -> str:
    s = unicodedata.normalize("NFC", str(s)).lower()
    return " ".join(re.sub(r"[^\w\s]", " ", s).split())


def fmt_num(v) -> str:
    if isinstance(v, float) and not v.is_integer():
        txt = f"{v:,.2f}".rstrip("0").rstrip(".")
    else:
        txt = f"{int(v):,}"
    return txt.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _period(v, where):
    if not isinstance(v, dict):
        return None
    tu, den = parse_date(v.get("tu"), f"{where}.tu"), parse_date(v.get("den"), f"{where}.den")
    return (tu, den) if tu and den else None


def show(field: dict, v) -> str:
    if field["kind"] == "number" and _is_num(v):
        return f"{fmt_num(v)} {field.get('unit', '')}".strip()
    if field["kind"] == "period" and isinstance(v, dict):
        return f"{_fmt(parse_date(v.get('tu'), 'tu'))} – {_fmt(parse_date(v.get('den'), 'den'))}"
    return str(v)


def check_consistency(project: dict, cfg: dict) -> tuple[list[Finding], dict]:
    groups, fields = cfg["groups"], cfg["fields"]
    attrs = project.get("attributes") or {}
    docs, out = [], []
    by_id = {d.get("id"): d for d in project.get("documents") or []}
    for d in project.get("documents") or []:
        if not d.get("nhom") and not d.get("thong_tin"):
            continue
        did = d.get("id", "?")
        if d.get("nhom") not in groups:
            out.append(Finding(GAP, "NQ-NHOM", did, "Văn bản chưa có nhóm hợp lệ",
                               f"Văn bản [{did}] có `thong_tin` nhưng `nhom` = {d.get('nhom')!r} không thuộc {sorted(groups)}",
                               fix="Khai báo `nhom` cho văn bản.", verified=True))
            continue
        date = parse_date(d.get("ngay_ky"), f"{did}.ngay_ky")
        if date is None:
            continue  # đã báo CIT-NO-DATE ở bước đối soát căn cứ
        docs.append({"id": did, "nhom": d["nhom"], "date": date, "info": d.get("thong_tin") or {}, "raw": d})
        for old in d.get("thay_the") or []:
            o = by_id.get(old)
            odate = parse_date((o or {}).get("ngay_ky"), f"{old}.ngay_ky") if o else None
            problem = ("không tồn tại" if o is None else
                       f"khác nhóm ({o.get('nhom')} ≠ {d['nhom']})" if o.get("nhom") != d["nhom"] else
                       f"không ký trước ({_fmt(odate)} ≥ {_fmt(date)})" if odate and odate >= date else None)
            if problem:
                out.append(Finding(SOFT, "NQ-PB", did, "Quan hệ văn bản điều chỉnh không hợp lệ",
                                   f"Văn bản [{did}] khai báo thay thế [{old}] nhưng văn bản đó {problem}",
                                   basis=BASIS, fix="Sửa `thay_the`: chỉ trỏ tới văn bản cùng nhóm, ký trước.",
                                   trace=[f"[{did}] {groups[d['nhom']]}, ký {_fmt(date)}"], verified=True))

    def master_at(group, field, date):
        cands = [m for m in docs if m["nhom"] == group and m["date"] <= date and field in m["info"]]
        return max(cands, key=lambda m: m["date"]) if cands else None

    def label(d):
        return f"{groups[d['nhom']]} [{d['id']}] ký {_fmt(d['date'])}"

    matrix: dict = {}
    for r in cfg["rules"]:
        cond = r.get("applies_if")
        if cond and attrs.get(cond["attr"]) != cond["equals"]:
            continue
        sev = HARD if r["severity"] == "hard" else SOFT
        targets = sorted((d for d in docs if d["nhom"] in r["targets"]), key=lambda d: (d["date"], d["id"]))
        for fid in r["fields"]:
            running = 0  # lũy kế cho sum_not_exceed, tính riêng từng trường
            f = fields[fid]
            mfid = r.get("master_field", fid)
            for t in targets:
                if fid not in t["info"]:
                    continue
                tv = t["info"][fid]
                m = master_at(r["master"], mfid, t["date"])
                row = {"rule": r["id"], "doc": t["id"], "group": groups[t["nhom"]], "date": t["date"],
                       "value": show(f, tv), "kind": f["kind"], "extra": "", "master": None,
                       "result": "thieu_chuan", "note": ""}
                key = fid if r["compare"] != "sum_not_exceed" else mfid
                matrix.setdefault(key, {"label": fields[key]["label"], "rows": []})["rows"].append(row)
                base_trace = [f"Đích: {label(t)} - {f['label']} = {show(f, tv)}"]
                if m is None:
                    row["note"] = f"chưa có {groups[r['master']]} có trường này, ký ≤ {_fmt(t['date'])}"
                    out.append(Finding(GAP, f"{r['id']}-GAP", t["id"], f"Thiếu văn bản chuẩn để so {f['label'].lower()}",
                                       f"{label(t)}: {row['note']}", basis=BASIS,
                                       fix=f"Khai báo `thong_tin.{mfid}` cho văn bản {groups[r['master']]}.",
                                       trace=base_trace, verified=True))
                    continue
                mf = fields[mfid]
                mv = m["info"][mfid]
                row["master"] = f"{m['id']} ({_fmt(m['date'])}): {show(mf, mv)}"
                trace = base_trace + [f"Chuẩn: {label(m)} - {mf['label']} = {show(mf, mv)}",
                                      f"Quy tắc {r['id']}: {r['compare']}, chuẩn = bản mới nhất ký ≤ ngày đích"]
                msg, kind_bad = _compare(r, f, tv, mv, t, m, running)
                if r["compare"] == "sum_not_exceed" and _is_num(tv):
                    running += tv
                    row["extra"] = f"lũy kế {show(f, running)}"
                if msg is None:
                    row["result"] = "trong_han_muc" if r["compare"] == "sum_not_exceed" else "khop"
                    continue
                if kind_bad == "gap":
                    row["result"], row["note"] = "thieu_chuan", msg
                    out.append(Finding(GAP, f"{r['id']}-GAP", t["id"], f"Không so được {f['label'].lower()}",
                                       f"{label(t)}: {msg}", basis=BASIS, fix="Sửa giá trị khai báo.",
                                       trace=trace, verified=True))
                    continue
                row["result"], row["note"] = kind_bad, msg
                out.append(Finding(sev, r["id"], t["id"], _title(r, f), f"{label(t)}: {msg}", basis=BASIS,
                                   fix=r.get("fix") or "Đối chiếu văn bản gốc; sửa văn bản sai hoặc lập văn bản điều chỉnh.",
                                   trace=trace, verified=True))
    for block in matrix.values():
        block["rows"].sort(key=lambda row: (row["date"], row["doc"], row["rule"]))
    return out, matrix


def _title(r, f) -> str:
    return {"equal_text": f"Lệch {f['label'].lower()} so với văn bản chuẩn",
            "equal_number": f"Lệch {f['label'].lower()} so với văn bản chuẩn",
            "within_period": f"{f['label']} vượt khung của văn bản chuẩn",
            "sum_not_exceed": f"Lũy kế {f['label'].lower()} vượt hạn mức"}[r["compare"]]


def _compare(r, f, tv, mv, t, m, running):
    """(None, None) nếu đạt; (thông điệp, 'lech'|'vuot'|'gap') nếu không."""
    c = r["compare"]
    if c == "equal_text":
        if _norm_text(tv) == _norm_text(mv):
            return None, None
        return f"ghi \"{tv}\", văn bản chuẩn [{m['id']}] ghi \"{mv}\"", "lech"
    if c in ("equal_number", "sum_not_exceed"):
        if not _is_num(tv) or not _is_num(mv):
            return f"giá trị không phải số (đích {tv!r}, chuẩn {mv!r})", "gap"
        if c == "sum_not_exceed":
            total = running + tv
            if total <= mv:
                return None, None
            return (f"lũy kế {show(f, total)} vượt hạn mức {show(f, mv)} của [{m['id']}] "
                    f"thêm {show(f, total - mv)}"), "vuot"
        tol = r.get("tolerance") or {}
        allowed = max(float(tol.get("abs", 0)), float(tol.get("pct", 0)) / 100 * abs(mv))
        diff = tv - mv
        if abs(diff) <= allowed:
            return None, None
        pct = f" ({'+' if diff > 0 else '−'}{fmt_num(round(abs(diff) / abs(mv) * 100, 2))}%)" if mv else ""
        return (f"ghi {show(f, tv)}, văn bản chuẩn [{m['id']}] ghi {show(f, mv)}; "
                f"chênh {'+' if diff > 0 else '−'}{show(f, abs(diff))}{pct}"), "lech"
    if c == "within_period":
        tp, mp = _period(tv, f"{t['id']}.thoi_gian"), _period(mv, f"{m['id']}.thoi_gian")
        if tp is None or mp is None:
            return "thời gian thiếu `tu` hoặc `den`", "gap"
        parts = []
        if tp[0] < mp[0]:
            parts.append(f"bắt đầu sớm hơn {(mp[0] - tp[0]).days} ngày")
        if tp[1] > mp[1]:
            parts.append(f"kết thúc sau {(tp[1] - mp[1]).days} ngày")
        if not parts:
            return None, None
        return (f"{show(f, tv)} so với khung {show(f, mv)} của [{m['id']}]: " + "; ".join(parts)), "vuot"
    raise RuleError(f"compare không hỗ trợ: {c}")
