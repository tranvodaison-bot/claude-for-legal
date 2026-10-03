"""Dòng lệnh: python -m crosscheck <ho_so.yaml> [--rules ...] [--format md|json]."""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from .engine import HARD, RuleError, evaluate, load_project, load_rules, parse_date
from .report import to_json, to_markdown

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "data" / "procedure_rules.yaml"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="crosscheck", description="Đối soát trình tự - tiên quyết hồ sơ dự án")
    ap.add_argument("project", help="file YAML hồ sơ dự án")
    ap.add_argument("--rules", default=str(DEFAULT_RULES), help="file YAML quy tắc")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--as-of", help="ngày đối soát YYYY-MM-DD (mặc định: hôm nay)")
    ap.add_argument("--out", help="ghi ra file thay vì stdout (không ghi đè nếu đã tồn tại)")
    args = ap.parse_args(argv)
    try:
        rules = load_rules(args.rules)
        project = load_project(args.project)
        as_of = parse_date(args.as_of, "--as-of") or dt.date.today()
        findings = evaluate(project, rules, as_of)
    except (RuleError, OSError) as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    text = (to_json if args.format == "json" else to_markdown)(project, findings, as_of)
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
