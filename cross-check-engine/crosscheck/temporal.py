"""Sổ văn bản theo thời gian, quy tắc chuyển tiếp và đối soát căn cứ viện dẫn của văn bản dự án."""
from __future__ import annotations

import re

from .engine import GAP, HARD, INFO, SOFT, Finding, RuleError, _fmt, _load_yaml, parse_date

ROLES = {"chinh", "sua_doi", "hop_nhat"}
LEVELS = {"primary", "secondary", "recall"}
LEVEL_LABEL = {"primary": "đã đối chiếu văn bản gốc", "secondary": "nguồn thứ cấp",
               "recall": "chưa tra cứu"}
_SO_HIEU = re.compile(r"(\d+)\s*/\s*(\d{4})\s*/\s*([0-9A-Za-zĐđÐ-]+)")


def norm_so_hieu(text: str):
    m = _SO_HIEU.search(text or "")
    if not m:
        return None
    return f"{int(m[1])}/{m[2]}/{m[3].upper().replace('Ð', 'Đ')}"


def _norm_prov(p: str) -> str:
    return " ".join(p.lower().split())


class Registry:
    def __init__(self, docs: dict, domains: dict, report_domains: list):
        self.docs, self.domains, self.report_domains = docs, domains, report_domains
        self.by_key, self.by_alias = {}, {}
        for d in docs.values():
            self.by_key[norm_so_hieu(d["so_hieu"])] = d
            for a in d.get("aliases") or []:
                self.by_alias[a.lower()] = d

    def lookup(self, text: str):
        key = norm_so_hieu(text)
        if key and key in self.by_key:
            return self.by_key[key]
        return self.by_alias.get((text or "").strip().lower())

    def label(self, d) -> str:
        return f"{d['ten']} ({d['so_hieu']})"

    def start_for(self, d, provision=None):
        if provision:
            p = _norm_prov(provision)
            for pe in d.get("partial_effect") or []:
                for item in pe["provisions"]:
                    item = _norm_prov(item)
                    if p == item or p.startswith(item + " "):
                        return pe["from"]
        return d.get("hieu_luc_tu")

    def status_at(self, d, date, provision=None) -> str:
        """'chua' | 'con' | 'het' | 'unknown'."""
        start, end = self.start_for(d, provision), d.get("het_hieu_luc")
        if end and date >= end:
            return "het"
        if start is None:
            return "unknown"  # không biết ngày bắt đầu thì không kết luận "còn hiệu lực"
        return "chua" if date < start else "con"

    def regime_at(self, domain: str, date):
        for d in self.docs.values():
            if d["domain"] != domain or d["role"] != "chinh":
                continue
            start, end = d.get("hieu_luc_tu"), d.get("het_hieu_luc")
            if start and start <= date and (not end or date < end):
                return d
        return None

    def successors(self, doc_id: str) -> list:
        return [d for d in self.docs.values() if doc_id in (d.get("replaces") or [])]

    def amendments_of(self, doc_id: str) -> list:
        return [d for d in self.docs.values() if doc_id in (d.get("amends") or [])]


def load_registry(path) -> Registry:
    data = _load_yaml(path)
    domains = data.get("domains") or {}
    docs: dict = {}
    for d in data.get("documents") or []:
        did = d.get("id")
        if not did or "so_hieu" not in d or "ten" not in d:
            raise RuleError(f"{path}: văn bản cần id, so_hieu, ten: {d}")
        if did in docs:
            raise RuleError(f"{path}: trùng id văn bản `{did}`")
        if norm_so_hieu(d["so_hieu"]) is None:
            raise RuleError(f"{path}: `{did}` có số hiệu không đọc được: {d['so_hieu']}")
        if d.get("domain") not in domains:
            raise RuleError(f"{path}: `{did}` có lĩnh vực không khai báo: {d.get('domain')}")
        if d.get("role") not in ROLES or d.get("level") not in LEVELS:
            raise RuleError(f"{path}: `{did}` cần role {sorted(ROLES)} và level {sorted(LEVELS)}")
        for k in ("ngay_ban_hanh", "hieu_luc_tu", "het_hieu_luc"):
            d[k] = parse_date(d.get(k), f"{did}.{k}")
        for pe in d.get("partial_effect") or []:
            pe["from"] = parse_date(pe.get("from"), f"{did}.partial_effect.from")
        docs[did] = d
    for did, d in docs.items():
        for rel in ("replaces", "amends"):
            for ref in d.get(rel) or []:
                if ref not in docs:
                    raise RuleError(f"{path}: `{did}`.{rel} tham chiếu văn bản không có: `{ref}`")
    # Suy ra ngày hết hiệu lực từ văn bản thay thế; báo lỗi nếu khai báo mâu thuẫn.
    for did, d in docs.items():
        for ref in d.get("replaces") or []:
            old = docs[ref]
            if d.get("hieu_luc_tu") is None:
                continue
            if old.get("het_hieu_luc") is None:
                old["het_hieu_luc"], old["het_hieu_luc_suy_ra"] = d["hieu_luc_tu"], True
            elif old["het_hieu_luc"] != d["hieu_luc_tu"]:
                raise RuleError(f"{path}: `{ref}` hết hiệu lực {old['het_hieu_luc']} nhưng `{did}` "
                                f"thay thế có hiệu lực từ {d['hieu_luc_tu']}")
    # Văn bản sửa đổi hết hiệu lực cùng văn bản bị sửa đổi (nếu không khai báo khác).
    for d in docs.values():
        if d["role"] == "sua_doi" and d.get("het_hieu_luc") is None and d.get("derive_expiry", True):
            ends = [docs[b].get("het_hieu_luc") for b in d.get("amends") or []]
            if ends and all(ends):
                d["het_hieu_luc"] = max(ends)
    # Hai văn bản chính cùng lĩnh vực không được chồng khoảng hiệu lực (bản đồ chế độ sẽ mơ hồ).
    mains = sorted((d for d in docs.values() if d["role"] == "chinh" and d.get("hieu_luc_tu")),
                   key=lambda d: (d["domain"], d["hieu_luc_tu"]))
    for a, b in zip(mains, mains[1:]):
        if a["domain"] == b["domain"] and (a.get("het_hieu_luc") is None or a["het_hieu_luc"] > b["hieu_luc_tu"]):
            raise RuleError(f"{path}: `{a['id']}` và `{b['id']}` cùng lĩnh vực `{a['domain']}` chồng khoảng hiệu lực")
    report_domains = [x for x in data.get("report_domains") or [] if x in domains]
    return Registry(docs, domains, report_domains)


def load_transitions(path, registry: Registry) -> list:
    data = _load_yaml(path)
    out = []
    for t in data.get("transitions") or []:
        tid = t.get("id")
        for k in ("from", "to"):
            if t.get(k) not in registry.docs:
                raise RuleError(f"{path}: `{tid}`.{k} không có trong sổ văn bản: {t.get(k)}")
        for c in t.get("allow_old_if") or []:
            if not c.get("date_ref") or not c.get("label"):
                raise RuleError(f"{path}: `{tid}` mỗi điều kiện cần date_ref và label")
        t["boundary"] = parse_date(t.get("boundary"), f"{tid}.boundary") or registry.docs[t["to"]].get("hieu_luc_tu")
        if t["boundary"] is None:
            raise RuleError(f"{path}: `{tid}` không xác định được ranh giới (văn bản mới chưa có ngày hiệu lực)")
        out.append(t)
    return out


def _date_ref(name: str, doc: dict, project: dict):
    where = f"{doc.get('id')}.{name}"
    if name in doc:
        return parse_date(doc[name], where)
    if name == "ngay_ky_hop_dong" and doc.get("hop_dong"):
        hd = (project.get("contracts") or {}).get(doc["hop_dong"]) or {}
        return parse_date(hd.get("ngay_ky"), f"contracts.{doc['hop_dong']}.ngay_ky")
    if name in (project.get("key_dates") or {}):
        return parse_date(project["key_dates"][name], f"key_dates.{name}")
    if name == "ngay_phe_duyet_du_an":
        rec = (project.get("steps") or {}).get("phe_duyet_du_an") or {}
        return parse_date(rec.get("date"), "steps.phe_duyet_du_an.date")
    return None


def _effect_basis(registry: Registry, law: dict) -> list:
    return [{"doc": f"Điều khoản hiệu lực / thay thế của {registry.label(law)}", "provision": None,
             "verified": law["level"] == "primary"}]


def _cap(verified: bool) -> str:
    return HARD if verified else SOFT


def check_citations(project: dict, registry: Registry, transitions: list) -> list[Finding]:
    out: list[Finding] = []
    for doc in project.get("documents") or []:
        did = doc.get("id", "?")
        ngay = parse_date(doc.get("ngay_ky"), f"{did}.ngay_ky")
        head = f"{doc.get('loai', 'Văn bản')} [{did}]: ký {_fmt(ngay)}"
        if doc.get("ngay_nop"):
            head += f", nộp {_fmt(parse_date(doc['ngay_nop'], f'{did}.ngay_nop'))}"
        if doc.get("hop_dong"):
            head += f", thuộc hợp đồng {doc['hop_dong']}"
        if ngay is None:
            out.append(Finding(GAP, "CIT-NO-DATE", did, "Văn bản dự án thiếu ngày ký",
                               f"{head}; không đối soát được hiệu lực căn cứ viện dẫn",
                               fix="Bổ sung `ngay_ky`.", trace=[head]))
            continue
        cited: set = set()
        for c in doc.get("can_cu") or []:
            text, prov = (c, None) if isinstance(c, str) else (c.get("van_ban"), c.get("dieu_khoan"))
            shown = text + (f" {prov}" if prov else "")
            law = registry.lookup(text)
            if law is None:
                out.append(Finding(GAP, "CIT-UNKNOWN", did, "Căn cứ viện dẫn chưa có trong sổ văn bản",
                                   f"{head} viện dẫn `{shown}` - sổ văn bản chưa có, chưa đối soát được",
                                   fix="Bổ sung văn bản vào data/legal_registry.yaml hoặc sửa số hiệu.",
                                   trace=[head]))
                continue
            cited.add(law["id"])
            verified = law["level"] == "primary"
            trace = [head, f"Viện dẫn: {registry.label(law)}" + (f", {prov}" if prov else "")
                     + f" - hiệu lực {_fmt(registry.start_for(law, prov))} -> "
                     + (_fmt(law.get('het_hieu_luc')) if law.get("het_hieu_luc") else "nay")
                     + f" [{LEVEL_LABEL[law['level']]}]"]
            if law["role"] == "hop_nhat":
                out.append(Finding(INFO, "CIT-VBHN", did, "Viện dẫn văn bản hợp nhất",
                                   f"{head} viện dẫn VBHN `{law['so_hieu']}`; VBHN là lớp hiển thị, không phải nguồn gốc",
                                   fix="Xác định văn bản gốc/sửa đổi tạo ra nội dung được áp dụng và ghi rõ trong hồ sơ.",
                                   trace=trace, verified=False))
            st = registry.status_at(law, ngay, prov)
            if st == "unknown":
                out.append(Finding(GAP, "CIT-NO-EFFECT-DATE", did, "Sổ văn bản chưa có ngày hiệu lực",
                                   f"Chưa biết `{law['so_hieu']}`" + (f" {prov}" if prov else "")
                                   + f" có hiệu lực tại {_fmt(ngay)} hay không",
                                   fix="Bổ sung ngày hiệu lực (hoặc hiệu lực từng phần) vào sổ văn bản.", trace=trace))
            elif st == "chua":
                hint = (" Văn bản này chỉ có một số điều/khoản hiệu lực sớm; nếu viện dẫn các điều đó, ghi rõ điều/khoản."
                        if law.get("partial_effect") and not prov else "")
                out.append(Finding(_cap(verified), "CIT-NOT-YET", did,
                                   "Viện dẫn căn cứ chưa có hiệu lực tại ngày ký" + ("" if verified else " (cần xác minh)"),
                                   f"{head} viện dẫn `{shown}`, hiệu lực từ {_fmt(registry.start_for(law, prov))}.{hint}",
                                   basis=_effect_basis(registry, law),
                                   fix="Kiểm tra lại căn cứ tại ngày ký; nếu viện dẫn sai, đánh giá ảnh hưởng tới hiệu lực văn bản.",
                                   trace=trace, verified=verified))
            elif st == "het":
                out.extend(_expired(doc, did, head, law, prov, shown, ngay, trace, project, registry, transitions))
        # Văn bản chính được viện dẫn nhưng bỏ sót văn bản sửa đổi đang có hiệu lực.
        for lid in sorted(cited):
            law = registry.docs[lid]
            if law["role"] != "chinh":
                continue
            for am in registry.amendments_of(lid):
                if am["id"] not in cited and registry.status_at(am, ngay) == "con" and am.get("hieu_luc_tu"):
                    out.append(Finding(INFO, "CIT-AMEND-MISSING", did, "Chưa viện dẫn văn bản sửa đổi đang có hiệu lực",
                                       f"{head} viện dẫn `{law['so_hieu']}` nhưng không viện dẫn `{am['so_hieu']}` "
                                       f"(sửa đổi, hiệu lực từ {_fmt(am['hieu_luc_tu'])})",
                                       fix="Kiểm tra nội dung áp dụng có thuộc phần đã sửa đổi không.",
                                       trace=[head], verified=False))
    return out


def _expired(doc, did, head, law, prov, shown, ngay, trace, project, registry, transitions):
    base_ids = [law["id"]] if law["role"] != "sua_doi" else list(law.get("amends") or [])
    rules = [t for t in transitions if t["from"] in base_ids]
    succ = [s for b in base_ids for s in registry.successors(b)]
    succ_txt = "; ".join(f"{registry.label(s)} hiệu lực {_fmt(s.get('hieu_luc_tu'))}" for s in succ) or "chưa có trong sổ"
    base = f"{head} viện dẫn `{shown}`, đã hết hiệu lực từ {_fmt(law.get('het_hieu_luc'))}"
    if not rules:
        return [Finding(SOFT, "CIT-EXPIRED-NO-RULE", did, "Viện dẫn văn bản đã hết hiệu lực - chưa có quy tắc chuyển tiếp",
                        f"{base}. Thư viện chưa có quy tắc chuyển tiếp cho văn bản này nên chưa kết luận được.",
                        basis=_effect_basis(registry, law),
                        fix=f"Bóc điều khoản chuyển tiếp của văn bản thay thế ({succ_txt}) và bổ sung quy tắc.",
                        trace=trace, verified=False)]
    missing, findings = [], []
    for t in rules:
        verified = law["level"] == "primary" and registry.docs[t["to"]]["level"] == "primary" and bool(t.get("verified"))
        lines = [f"Quy tắc {t['id']}: ranh giới {_fmt(t['boundary'])}" + (f" - {t['note']}" if t.get("note") else "")]
        for c in t.get("allow_old_if") or []:
            d = _date_ref(c["date_ref"], doc, project)
            lines.append(f"  {c['label']}: {c['date_ref']} = {_fmt(d)}")
            if d is None:
                missing.append(c["date_ref"])
            elif d < t["boundary"]:
                return [Finding(INFO, f"CIT-TRANSITION-{t['id']}", did, "Áp dụng văn bản cũ theo chuyển tiếp",
                                f"{base}; được tiếp tục áp dụng theo điều kiện: {c['label']} ({_fmt(d)} < {_fmt(t['boundary'])})",
                                basis=t.get("basis") or [],
                                fix="Xác nhận điều khoản chuyển tiếp thật khớp với điều kiện này.",
                                trace=trace + lines, verified=verified)]
        findings.append((t, lines, verified))
    if missing:
        t, lines, _ = findings[0]
        return [Finding(GAP, "CIT-TRANSITION-NO-DATA", did, "Thiếu ngày để xác định chuyển tiếp",
                        f"{base}; cần {', '.join(sorted(set(missing)))} để biết có thuộc trường hợp chuyển tiếp không",
                        basis=t.get("basis") or [], fix="Bổ sung ngày còn thiếu vào văn bản dự án hoặc key_dates.",
                        trace=trace + lines)]
    t, lines, verified = findings[0]
    return [Finding(_cap(verified), f"CIT-EXPIRED-{t['id']}", did,
                    "Viện dẫn văn bản đã hết hiệu lực, không thuộc trường hợp chuyển tiếp" + ("" if verified else " (cần xác minh)"),
                    f"{base}; không điều kiện chuyển tiếp nào thỏa",
                    basis=t.get("basis") or [],
                    fix=f"Văn bản thay thế: {succ_txt}. Đánh giá lại căn cứ và hiệu lực của văn bản dự án.",
                    trace=trace + lines, verified=verified)]


def regime_map(project: dict, rules: dict, registry: Registry, domains=None) -> list[dict]:
    """Văn bản chính của từng lĩnh vực có hiệu lực tại ngày mỗi bước (chưa xét chuyển tiếp)."""
    domains = domains or registry.report_domains
    rows = []
    for sid, rule in rules.items():
        rec = (project.get("steps") or {}).get(sid) or {}
        d = parse_date(rec.get("start_date"), f"{sid}.start_date") or parse_date(rec.get("date"), f"{sid}.date")
        if d is None:
            continue
        cells = {}
        for dom in domains:
            law = registry.regime_at(dom, d)
            cells[dom] = law["so_hieu"] if law else "-"
        rows.append({"step": rule["name"], "date": d, "cells": cells})
    rows.sort(key=lambda r: r["date"])
    return rows
