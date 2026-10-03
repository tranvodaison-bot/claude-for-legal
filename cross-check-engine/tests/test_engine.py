import datetime as dt
from pathlib import Path

import pytest
import yaml

from crosscheck.cli import DEFAULT_RULES, main
from crosscheck.engine import GAP, HARD, SOFT, RuleError, evaluate, load_project, load_rules

ROOT = Path(__file__).resolve().parent.parent
RULES = load_rules(DEFAULT_RULES)
D = dt.date


def run(steps, attrs=None):
    project = {"attributes": attrs or {}, "steps": steps}
    return evaluate(project, RULES, as_of=D(2026, 10, 3))


CHAIN = {
    "lap_bcnckt": {"status": "completed", "date": D(2025, 1, 1)},
    "tham_dinh_bcnckt": {"status": "completed", "date": D(2025, 2, 1)},
    "phe_duyet_du_an": {"status": "completed", "date": D(2025, 3, 1)},
}


def ids(findings, sev=None):
    return {f.rule_id for f in findings if sev is None or f.severity == sev}


def test_default_rules_load_and_acyclic():
    assert "khoi_cong" in RULES


def test_clean_chain_has_no_findings():
    f = run({
        "lap_bcnckt": {"status": "completed", "date": D(2025, 1, 1)},
        "tham_dinh_bcnckt": {"status": "completed", "date": D(2025, 2, 1)},
        "phe_duyet_du_an": {"status": "completed", "date": D(2025, 3, 1)},
    })
    assert f == []


def test_same_day_is_allowed():
    f = run({
        "tham_dinh_bcnckt": {"status": "completed", "date": D(2025, 2, 1)},
        "lap_bcnckt": {"status": "completed", "date": D(2025, 2, 1)},
    })
    assert f == []


def test_started_before_prereq_done_is_hard():
    f = run({
        "lap_bcnckt": {"status": "not_started"},
        "tham_dinh_bcnckt": {"status": "in_progress", "start_date": D(2025, 2, 1)},
    })
    assert ids(f, HARD) == {"PRE-tham_dinh_bcnckt-lap_bcnckt"}


def test_temporal_violation_is_hard():
    f = run({
        "lap_bcnckt": {"status": "completed", "date": D(2025, 3, 1)},
        "tham_dinh_bcnckt": {"status": "completed", "date": D(2025, 2, 1)},
    })
    assert ids(f, HARD) == {"TEMP-tham_dinh_bcnckt-lap_bcnckt"}


def test_missing_prereq_record_is_gap_not_violation():
    f = run({"tham_dinh_bcnckt": {"status": "completed", "date": D(2025, 2, 1)}})
    assert ids(f) == {"GAP-PRE-tham_dinh_bcnckt-lap_bcnckt"}
    assert f[0].severity == GAP


def test_soft_prereq_gives_soft():
    f = run({
        "phe_duyet_du_an": {"status": "not_started"},
        "khao_sat": {"status": "completed", "date": D(2025, 4, 1)},
    })
    assert ids(f, SOFT) == {"PRE-khao_sat-phe_duyet_du_an"}


def test_conditional_prereq_skipped_when_not_required():
    steps = {**CHAIN, "phe_duyet_thiet_ke_du_toan": {"status": "completed", "date": D(2025, 5, 1)}}
    assert run(steps, {"requires_design_verification": False}) == []


def test_conditional_prereq_undeclared_attr_is_gap():
    steps = {**CHAIN, "phe_duyet_thiet_ke_du_toan": {"status": "completed", "date": D(2025, 5, 1)}}
    f = run(steps)
    assert ids(f) == {"GAP-ATTR-tham_tra_thiet_ke"} and f[0].severity == GAP


def test_not_applicable_contradicting_required_attr_is_hard():
    steps = {
        **CHAIN,
        "tham_tra_thiet_ke": {"status": "not_applicable", "na_basis": "x"},
        "phe_duyet_thiet_ke_du_toan": {"status": "completed", "date": D(2025, 5, 1)},
    }
    f = run(steps, {"requires_design_verification": True})
    assert ids(f, HARD) == {"PRE-phe_duyet_thiet_ke_du_toan-tham_tra_thiet_ke"}


def test_na_without_basis_is_soft():
    f = run({"khao_sat": {"status": "not_applicable"}})
    assert ids(f, SOFT) == {"NA-NO-BASIS"}


def test_na_with_basis_is_clean():
    assert run({"khao_sat": {"status": "not_applicable", "na_basis": "đã có hồ sơ KS giai đoạn lập dự án"}}) == []


def test_completed_without_date_is_gap():
    f = run({"lap_bcnckt": {"status": "completed"}})
    assert ids(f) == {"DATA-NO-DATE"}


def test_future_date_and_reversed_dates_flagged():
    f = run({"lap_bcnckt": {"status": "completed", "start_date": D(2027, 1, 2), "date": D(2027, 1, 1)}})
    assert {"DATE-ORDER", "DATE-FUTURE"} <= ids(f, SOFT)


def test_unknown_step_is_gap():
    assert ids(run({"khoi_cogn": {"status": "completed", "date": D(2025, 1, 1)}})) == {"DATA-UNKNOWN-STEP"}


def test_string_dates_accepted_and_bad_date_rejected():
    run({"lap_bcnckt": {"status": "completed", "date": "2025-01-01"}})
    with pytest.raises(RuleError):
        run({"lap_bcnckt": {"status": "completed", "date": "01/01/2025"}})


def test_sorted_hard_first():
    f = load_project(ROOT / "examples" / "du_an_mau.yaml")
    sev = [x.severity for x in evaluate(f, RULES, as_of=D(2026, 10, 3))]
    assert sev == sorted(sev, key=lambda s: {HARD: 0, SOFT: 1, GAP: 2}[s])


def test_sample_project_counts():
    p = load_project(ROOT / "examples" / "du_an_mau.yaml")
    f = evaluate(p, RULES, as_of=D(2026, 10, 3))
    assert [x.severity for x in f].count(HARD) == 3
    assert [x.severity for x in f].count(SOFT) == 1
    assert [x.severity for x in f].count(GAP) == 1


def _write(tmp_path, steps):
    p = tmp_path / "r.yaml"
    p.write_text(yaml.safe_dump({"steps": steps}), encoding="utf-8")
    return p


def test_rules_reject_cycle(tmp_path):
    p = _write(tmp_path, [
        {"id": "a", "name": "A", "prerequisites": [{"step": "b", "severity": "hard"}]},
        {"id": "b", "name": "B", "prerequisites": [{"step": "a", "severity": "hard"}]},
    ])
    with pytest.raises(RuleError, match="Vòng lặp"):
        load_rules(p)


def test_rules_reject_dangling_and_bad_severity(tmp_path):
    with pytest.raises(RuleError, match="không tồn tại"):
        load_rules(_write(tmp_path, [{"id": "a", "name": "A", "prerequisites": [{"step": "zz", "severity": "hard"}]}]))
    with pytest.raises(RuleError, match="severity"):
        load_rules(_write(tmp_path, [
            {"id": "a", "name": "A", "prerequisites": [{"step": "b", "severity": "meh"}]},
            {"id": "b", "name": "B"}]))


def test_cli_exit_codes_and_no_overwrite(tmp_path, capsys):
    sample = str(ROOT / "examples" / "du_an_mau.yaml")
    assert main([sample, "--as-of", "2026-10-03"]) == 1
    out = tmp_path / "bc.md"
    assert main([sample, "--out", str(out)]) == 1 and out.exists()
    assert main([sample, "--out", str(out)]) == 2
    assert main([str(tmp_path / "missing.yaml")]) == 2
    assert main([sample, "--format", "json"]) == 1
