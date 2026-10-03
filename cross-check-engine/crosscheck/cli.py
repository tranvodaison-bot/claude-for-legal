"""Dòng lệnh: python -m crosscheck <ho_so.yaml> [--rules ...] [--format md|json]."""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from .engine import HARD, SEVERITY_ORDER, RuleError, evaluate, load_project, load_rules, parse_date
from .report import to_json, to_markdown
from .temporal import check_citations, load_registry, load_transitions, regime_map

DATA = Path(__file__).resolve().parent.parent / "data"
DEFAULT_RULES = DATA / "procedure_rules.yaml"
DEFAULT_REGISTRY = DATA / "legal_registry.yaml"
DEFAULT_TRANSITIONS = DATA / "transition_rules.yaml"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="crosscheck", description="Đối soát trình tự - tiên quyết hồ sơ dự án")
    ap.add_argument("project", help="file YAML hồ sơ dự án")
    ap.add_argument("--rules", default=str(DEFAULT_RULES), help="file YAML quy tắc")
    ap.add_argument("--registry", default=str(DEFAULT_REGISTRY), help="file YAML sổ văn bản theo thời gian")
    ap.add_argument("--transitions", default=str(DEFAULT_TRANSITIONS), help="file YAML quy tắc chuyển tiếp")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--as-of", help="ngày đối soát YYYY-MM-DD (mặc định: hôm nay)")
    ap.add_argument("--out", help="ghi ra file thay vì stdout (không ghi đè nếu đã tồn tại)")
    args = ap.parse_args(argv)
    try:
        rules = load_rules(args.rules)
        project = load_project(args.project)
        as_of = parse_date(args.as_of, "--as-of") or dt.date.today()
        registry = load_registry(args.registry)
        transitions = load_transitions(args.transitions, registry)
        findings = evaluate(project, rules, as_of, registry=registry)
        findings += check_citations(project, registry, transitions)
        findings.sort(key=lambda f: SEVERITY_ORDER[f.severity])
        regime = regime_map(project, rules, registry)
    except (RuleError, OSError) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    text = (to_json if args.format == "json" else to_markdown)(project, findings, as_of, regime, registry.domains)
    if args.out:
        out = Path(args.out)
        if out.exists():
            print(f"Lỗi: {out} đã tồn tại, không ghi đè", file=sys.stderr)
            return 2
        out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 1 if any(f.severity == HARD for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
