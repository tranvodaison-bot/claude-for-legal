"""Nạp quy tắc, nạp hồ sơ dự án và đánh giá trình tự - tiên quyết."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HARD, SOFT, GAP = "HARD", "SOFT", "DATA_GAP"
SEVERITY_ORDER = {HARD: 0, SOFT: 1, GAP: 2}
STARTED = {"in_progress", "completed"}
STATUSES = {"not_started", "in_progress", "completed", "not_applicable"}
_MISSING = object()


class RuleError(ValueError):
    """File quy tắc hoặc hồ sơ không hợp lệ."""


@dataclass
class Finding:
    severity: str
    rule_id: str
    step: str
    title: str
    where: str
    basis: list = field(default_factory=list)
    fix: str = ""
    trace: list = field(default_factory=list)


def _load_yaml(path) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise RuleError(f"{path}: nội dung gốc phải là một mapping")
    return data


def parse_date(value, where: str):
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            pass
    raise RuleError(f"{where}: ngày không hợp lệ ({value!r}), cần dạng YYYY-MM-DD")


def load_rules(path) -> dict:
    """Nạp và kiểm tra file quy tắc. Trả về {step_id: rule}."""
    data = _load_yaml(path)
    rules = {}
    for s in data.get("steps") or []:
        if "id" not in s or "name" not in s:
            raise RuleError(f"{path}: mỗi bước cần `id` và `name`: {s}")
        if s["id"] in rules:
            raise RuleError(f"{path}: trùng id bước `{s['id']}`")
        rules[s["id"]] = s
    for sid, s in rules.items():
        for p in s.get("prerequisites") or []:
            if p.get("step") not in rules:
                raise RuleError(f"{path}: bước `{sid}` tham chiếu tiên quyết không tồn tại `{p.get('step')}`")
            if p.get("severity") not in ("hard", "soft"):
                raise RuleError(f"{path}: `{sid}` <- `{p['step']}` cần severity hard|soft")
    _assert_acyclic(rules)
    return rules


def _assert_acyclic(rules: dict) -> None:
    state: dict = {}

    def visit(n, stack):
        if state.get(n) == 2:
            return
        if state.get(n) == 1:
            raise RuleError("Vòng lặp tiên quyết: " + " -> ".join(stack + [n]))
        state[n] = 1
        for p in rules[n].get("prerequisites") or []:
            visit(p["step"], stack + [n])
        state[n] = 2

    for n in rules:
        visit(n, [])


def _applies(rule: dict, attrs: dict):
    """True / False / None (chưa đủ dữ liệu để biết)."""
    cond = rule.get("applies_if")
    if not cond:
        return True
    val = attrs.get(cond["attr"], _MISSING)
    if val is _MISSING or val is None:
        return None
    return val == cond["equals"]


def _fmt(d) -> str:
    return d.strftime("%d/%m/%Y") if d else "chưa có ngày"


def evaluate(project: dict, rules: dict, as_of: dt.date | None = None) -> list[Finding]:
    as_of = as_of or dt.date.today()
    attrs = project.get("attributes") or {}
    recs = {k: dict(v or {}) for k, v in (project.get("steps") or {}).items()}
    out: list[Finding] = []

    for sid in recs:
        if sid not in rules:
            out.append(Finding(GAP, "DATA-UNKNOWN-STEP", sid, f"Bước `{sid}` không có trong bộ quy tắc",
                               f"Hồ sơ khai báo bước `{sid}` nhưng quy tắc không biết bước này (sai chính tả?)",
                               fix="Sửa mã bước hoặc bổ sung vào file quy tắc."))

    def dates(sid):
        r = recs.get(sid, {})
        return (parse_date(r.get("start_date"), f"{sid}.start_date"),
                parse_date(r.get("date"), f"{sid}.date"))

    for sid, rule in rules.items():
        rec = recs.get(sid)
        if rec is None:
            continue
        status = rec.get("status")
        start, done = dates(sid)
        ev = rec.get("evidence")
        trace_self = [f"{rule['name']} [{sid}]: trạng thái={status}, bắt đầu={_fmt(start)}, ngày={_fmt(done)}"
                      + (f", chứng cứ={ev}" if ev else "")]

        if status is not None and status not in STATUSES:
            out.append(Finding(SOFT, "DATA-BAD-STATUS", sid, "Trạng thái không hợp lệ",
                               f"`{status}` không thuộc {sorted(STATUSES)}", trace=trace_self))
            continue
        if status is None:
            if start or done:
                out.append(Finding(GAP, "DATA-NO-STATUS", sid, "Có ngày nhưng thiếu trạng thái",
                                   f"{rule['name']} có ngày nhưng không có `status`, chưa đối soát được",
                                   fix="Bổ sung `status`.", trace=trace_self))
            continue

        if status == "not_applicable":
            if rec.get("na_basis") is None and _applies(rule, attrs) is not False:
                out.append(Finding(SOFT, "NA-NO-BASIS", sid, "Đánh dấu không áp dụng nhưng không nêu căn cứ",
                                   f"{rule['name']} ghi `not_applicable` mà thiếu `na_basis` và không có điều kiện áp dụng nào loại trừ",
                                   fix="Ghi căn cứ miễn/không thuộc diện (điều khoản, văn bản) vào `na_basis`.",
                                   trace=trace_self))
            continue

        if start and done and start > done:
            out.append(Finding(SOFT, "DATE-ORDER", sid, "Ngày bắt đầu sau ngày hoàn thành",
                               f"{rule['name']}: bắt đầu {_fmt(start)} > hoàn thành {_fmt(done)}",
                               fix="Kiểm tra lại nhập liệu.", trace=trace_self))
        for label, d in (("bắt đầu", start), ("hoàn thành", done)):
            if d and d > as_of:
                out.append(Finding(SOFT, "DATE-FUTURE", sid, "Ngày nằm sau ngày đối soát",
                                   f"{rule['name']}: ngày {label} {_fmt(d)} sau ngày đối soát {_fmt(as_of)} nhưng đã ghi `{status}`",
                                   fix="Kiểm tra lại nhập liệu hoặc trạng thái.", trace=trace_self))

        if status not in STARTED:
            continue
        if status == "completed" and not done:
            out.append(Finding(GAP, "DATA-NO-DATE", sid, "Đã hoàn thành nhưng thiếu ngày",
                               f"{rule['name']} `completed` nhưng không có `date`; không kiểm tra được thứ tự thời gian",
                               fix="Bổ sung ngày theo văn bản/biên bản.", trace=trace_self))
        step_start = start or done

        for p in rule.get("prerequisites") or []:
            pid, sev = p["step"], (HARD if p["severity"] == "hard" else SOFT)
            prule = rules[pid]
            base = dict(basis=p.get("basis") or [], fix=p.get("fix", ""))
            applies = _applies(prule, attrs)
            if applies is False:
                continue
            if applies is None:
                cond = prule["applies_if"]["attr"]
                out.append(Finding(GAP, f"GAP-ATTR-{pid}", sid, f"Chưa khai báo thuộc tính `{cond}`",
                                   f"Không biết `{prule['name']}` có bắt buộc hay không nên chưa đánh giá điều kiện tiên quyết của `{rule['name']}`",
                                   basis=base["basis"], fix=f"Khai báo `attributes.{cond}` (true/false) trong hồ sơ.",
                                   trace=trace_self))
                continue

            prec = recs.get(pid)
            pstatus = (prec or {}).get("status")
            if pstatus is None:
                out.append(Finding(GAP, f"GAP-PRE-{sid}-{pid}", sid, "Chưa có dữ liệu bước tiên quyết",
                                   f"`{rule['name']}` đã `{status}` nhưng hồ sơ chưa khai báo trạng thái của `{prule['name']}`",
                                   basis=base["basis"], fix=f"Khai báo bước `{pid}`.", trace=trace_self))
                continue

            # Tới đây `applies` luôn là True. Nếu quy tắc có điều kiện áp dụng đang thỏa
            # mà hồ sơ lại ghi not_applicable thì là mâu thuẫn -> chưa đạt tiên quyết.
            # Không có điều kiện: not_applicable được chấp nhận (thiếu căn cứ -> NA-NO-BASIS).
            na_ok = pstatus == "not_applicable" and "applies_if" not in prule
            satisfied = pstatus == "completed" or na_ok
            pstart, pdone = dates(pid)
            trace = trace_self + [
                f"{prule['name']} [{pid}]: trạng thái={pstatus}, ngày={_fmt(pdone)}"
                + (f", chứng cứ={prec.get('evidence')}" if prec.get("evidence") else "")]

            if not satisfied:
                out.append(Finding(sev, f"PRE-{sid}-{pid}", sid,
                                   "Vi phạm điều kiện tiên quyết" if sev == HARD else "Thiếu điều kiện tiên quyết (mức mềm)",
                                   f"`{rule['name']}` đã `{status}` trong khi `{prule['name']}` mới ở trạng thái `{pstatus}`",
                                   trace=trace, **base))
                continue
            if pstatus == "completed" and pdone and step_start and step_start < pdone:
                out.append(Finding(sev, f"TEMP-{sid}-{pid}", sid, "Sai trình tự thời gian",
                                   f"`{rule['name']}` bắt đầu {_fmt(step_start)} trước khi `{prule['name']}` hoàn thành {_fmt(pdone)}",
                                   trace=trace, **base))

    out.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.step, f.rule_id))
    return out


def load_project(path) -> dict:
    data = _load_yaml(path)
    if "steps" not in data:
        raise RuleError(f"{path}: thiếu khóa `steps`")
    return data
