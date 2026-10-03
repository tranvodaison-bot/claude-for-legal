import datetime as dt
from pathlib import Path

import pytest
import yaml

from crosscheck.cli import DEFAULT_REGISTRY, DEFAULT_RULES, DEFAULT_TRANSITIONS, main
from crosscheck.engine import GAP, HARD, INFO, SOFT, RuleError, evaluate, load_project, load_rules
from crosscheck.temporal import (check_citations, load_registry, load_transitions, norm_so_hieu,
                                 regime_map)

ROOT = Path(__file__).resolve().parent.parent
REG = load_registry(DEFAULT_REGISTRY)
TRS = load_transitions(DEFAULT_TRANSITIONS, REG)
D = dt.date


def cite(docs, **project):
    return check_citations({"documents": docs, **project}, REG, TRS)


def by_id(findings):
    return {f.rule_id: f for f in findings}


@pytest.mark.parametrize("text,key", [
    ("Nghị định số 06/2021/NĐ-CP", "6/2021/NĐ-CP"),
    ("Nghị định 217/2026/NÐ-CP", "217/2026/NĐ-CP"),  # chữ Ð (U+00D0) hay gặp trên web
    ("Luật Xây dựng số 135/2025/QH15", "135/2025/QH15"),
    ("91/2026/VBHN-NĐ-BXD", "91/2026/VBHN-NĐ-BXD"),
    ("không có số hiệu", None),
])
def test_norm_so_hieu(text, key):
    assert norm_so_hieu(text) == key


def test_lookup_by_alias():
    assert REG.lookup("Luật Xây dựng 2014")["id"] == "luat_50_2014"


def test_expiry_derived_from_replacement_and_amendment():
    assert REG.docs["nd_175_2024"]["het_hieu_luc"] == D(2026, 7, 1)
    assert REG.docs["nd_59_2015"]["het_hieu_luc"] == D(2021, 3, 3)
    assert REG.docs["luat_62_2020"]["het_hieu_luc"] == D(2026, 7, 1)  # theo văn bản bị sửa đổi
    assert REG.docs["nd_217_2026"].get("het_hieu_luc") is None


@pytest.mark.parametrize("day,expected", [
    (D(2021, 3, 2), "59/2015/NĐ-CP"), (D(2021, 3, 3), "15/2021/NĐ-CP"),
    (D(2024, 12, 29), "15/2021/NĐ-CP"), (D(2024, 12, 30), "175/2024/NĐ-CP"),
    (D(2026, 6, 30), "175/2024/NĐ-CP"), (D(2026, 7, 1), "217/2026/NĐ-CP"),
])
def test_regime_boundaries(day, expected):
    assert REG.regime_at("hoat_dong_xd", day)["so_hieu"] == expected


def test_partial_effect_of_law_135():
    law = REG.docs["luat_135_2025"]
    day = D(2026, 2, 10)
    assert REG.status_at(law, day) == "chua"
    assert REG.status_at(law, day, "Điều 43 khoản 2") == "con"
    assert REG.status_at(law, day, "điều 71  khoản 1") == "con"
    assert REG.status_at(law, day, "Điều 43 khoản 1") == "chua"
    assert REG.status_at(law, D(2025, 12, 31), "Điều 71") == "chua"


def test_transition_allowed_by_submission_date():
    f = cite([{"id": "X", "ngay_ky": D(2021, 6, 10), "ngay_nop": D(2021, 2, 20), "can_cu": ["59/2015/NĐ-CP"]}])
    assert set(by_id(f)) == {"CIT-TRANSITION-TR-HDXD-2021"} and f[0].severity == INFO


def test_expired_without_transition_is_capped_soft_when_unverified():
    f = cite([{"id": "X", "ngay_ky": D(2026, 9, 1), "ngay_nop": D(2026, 7, 20), "can_cu": ["175/2024/NĐ-CP"]}])
    x = by_id(f)["CIT-EXPIRED-TR-HDXD-2026"]
    assert x.severity == SOFT and not x.verified


def test_contract_signing_date_resolved_from_contracts():
    f = cite([{"id": "PL", "ngay_ky": D(2026, 8, 10), "hop_dong": "HD", "can_cu": ["37/2015/NĐ-CP"]}],
             contracts={"HD": {"ngay_ky": D(2024, 11, 15)}})
    assert set(by_id(f)) == {"CIT-TRANSITION-TR-HD-2026"}


def test_amending_doc_follows_base_transition():
    f = cite([{"id": "PL", "ngay_ky": D(2026, 8, 10), "hop_dong": "HD", "can_cu": ["50/2021/NĐ-CP"]}],
             contracts={"HD": {"ngay_ky": D(2024, 11, 15)}})
    assert set(by_id(f)) == {"CIT-TRANSITION-TR-HD-2026"}


def test_missing_governing_date_is_gap():
    f = cite([{"id": "BB", "ngay_ky": D(2026, 8, 20), "can_cu": ["06/2021/NĐ-CP"]}])
    assert set(by_id(f)) == {"CIT-TRANSITION-NO-DATA"} and f[0].severity == GAP


def test_expired_without_rule_is_soft():
    f = cite([{"id": "X", "ngay_ky": D(2023, 1, 1), "can_cu": ["55/2014/QH13"]}])
    assert set(by_id(f)) == {"CIT-EXPIRED-NO-RULE"} and f[0].severity == SOFT


def test_not_yet_effective_with_partial_hint():
    f = cite([{"id": "X", "ngay_ky": D(2026, 2, 10), "can_cu": ["135/2025/QH15"]}])
    x = by_id(f)["CIT-NOT-YET"]
    assert x.severity == SOFT and "một số điều/khoản" in x.where
    assert cite([{"id": "X", "ngay_ky": D(2026, 2, 10),
                  "can_cu": [{"van_ban": "135/2025/QH15", "dieu_khoan": "Điều 43 khoản 2"}]}]) == []


def test_unknown_citation_and_missing_date_are_gaps():
    assert set(by_id(cite([{"id": "X", "ngay_ky": D(2022, 1, 1), "can_cu": ["12/2021/TT-BXD"]}]))) == {"CIT-UNKNOWN"}
    assert set(by_id(cite([{"id": "X", "can_cu": ["15/2021/NĐ-CP"]}]))) == {"CIT-NO-DATE"}


def test_missing_amendment_is_info():
    f = cite([{"id": "X", "ngay_ky": D(2022, 3, 20), "can_cu": ["50/2014/QH13"]}])
    assert set(by_id(f)) == {"CIT-AMEND-MISSING"} and f[0].severity == INFO
    assert cite([{"id": "X", "ngay_ky": D(2022, 3, 20), "can_cu": ["50/2014/QH13", "62/2020/QH14"]}]) == []


def test_vbhn_is_flagged():
    f = cite([{"id": "X", "ngay_ky": D(2026, 10, 1), "can_cu": ["91/2026/VBHN-NĐ-BXD"]}])
    assert set(by_id(f)) == {"CIT-VBHN"}


def test_red_only_when_everything_primary_and_verified(tmp_path):
    reg = {"domains": {"x": "X"}, "documents": [
        {"id": "a", "so_hieu": "1/2020/NĐ-CP", "ten": "A", "domain": "x", "role": "chinh", "hieu_luc_tu": D(2020, 1, 1), "level": "primary"},
        {"id": "b", "so_hieu": "2/2022/NĐ-CP", "ten": "B", "domain": "x", "role": "chinh", "hieu_luc_tu": D(2022, 1, 1),
         "replaces": ["a"], "level": "primary"}]}
    tr = {"transitions": [{"id": "T", "from": "a", "to": "b", "verified": True,
                           "allow_old_if": [{"date_ref": "ngay_nop", "label": "nộp trước"}]}]}
    (tmp_path / "r.yaml").write_text(yaml.safe_dump(reg, allow_unicode=True), encoding="utf-8")
    (tmp_path / "t.yaml").write_text(yaml.safe_dump(tr, allow_unicode=True), encoding="utf-8")
    r = load_registry(tmp_path / "r.yaml")
    t = load_transitions(tmp_path / "t.yaml", r)
    doc = {"id": "X", "ngay_ky": D(2022, 6, 1), "ngay_nop": D(2022, 3, 1), "can_cu": ["1/2020/NĐ-CP"]}
    f = check_citations({"documents": [doc]}, r, t)
    assert f[0].severity == HARD and f[0].verified
    tr["transitions"][0]["verified"] = False
    (tmp_path / "t.yaml").write_text(yaml.safe_dump(tr, allow_unicode=True), encoding="utf-8")
    assert check_citations({"documents": [doc]}, r, load_transitions(tmp_path / "t.yaml", r))[0].severity == SOFT


def _reg_file(tmp_path, docs):
    p = tmp_path / "r.yaml"
    p.write_text(yaml.safe_dump({"domains": {"x": "X"}, "documents": docs}, allow_unicode=True), encoding="utf-8")
    return p


def test_registry_rejects_inconsistent_expiry(tmp_path):
    p = _reg_file(tmp_path, [
        {"id": "a", "so_hieu": "1/2020/NĐ-CP", "ten": "A", "domain": "x", "role": "chinh", "level": "recall",
         "hieu_luc_tu": D(2020, 1, 1), "het_hieu_luc": D(2021, 5, 1)},
        {"id": "b", "so_hieu": "2/2021/NĐ-CP", "ten": "B", "domain": "x", "role": "chinh", "level": "recall",
         "hieu_luc_tu": D(2021, 6, 1), "replaces": ["a"]}])
    with pytest.raises(RuleError, match="hết hiệu lực"):
        load_registry(p)


def test_registry_rejects_dangling_ref_and_bad_domain(tmp_path):
    with pytest.raises(RuleError, match="không có"):
        load_registry(_reg_file(tmp_path, [{"id": "a", "so_hieu": "1/2020/NĐ-CP", "ten": "A", "domain": "x",
                                            "role": "chinh", "level": "recall", "replaces": ["zz"]}]))
    with pytest.raises(RuleError, match="lĩnh vực"):
        load_registry(_reg_file(tmp_path, [{"id": "a", "so_hieu": "1/2020/NĐ-CP", "ten": "A", "domain": "y",
                                            "role": "chinh", "level": "recall"}]))


def test_procedure_basis_resolved_by_event_date():
    rules = load_rules(DEFAULT_RULES)
    p = load_project(ROOT / "examples" / "du_an_mau.yaml")
    f = [x for x in evaluate(p, rules, D(2026, 10, 3), registry=REG) if x.rule_id == "TEMP-khoi_cong-cap_gpxd"][0]
    assert "50/2014/QH13" in f.basis[0]["doc"]  # khởi công 01/08/2025 -> Luật XD 2014
    late = {"attributes": {}, "steps": {
        "lap_bcnckt": {"status": "not_started"},
        "tham_dinh_bcnckt": {"status": "completed", "date": D(2026, 8, 1)}}}
    f = evaluate(late, rules, D(2026, 10, 3), registry=REG)[0]
    assert "217/2026/NĐ-CP" in f.basis[0]["doc"]


def test_multi_year_sample_expected_findings():
    rules = load_rules(DEFAULT_RULES)
    p = load_project(ROOT / "examples" / "du_an_nhieu_nam.yaml")
    assert evaluate(p, rules, D(2026, 10, 3), registry=REG) == []  # trình tự sạch
    got = sorted((f.step, f.rule_id) for f in check_citations(p, REG, TRS))
    assert got == sorted([
        ("QD-PD-DA", "CIT-TRANSITION-TR-HDXD-2021"),
        ("QD-PD-DA", "CIT-EXPIRED-TR-CP-2021"),
        ("QD-PD-TK", "CIT-UNKNOWN"),
        ("QD-PD-TK", "CIT-AMEND-MISSING"),
        ("GPXD-01", "CIT-NOT-YET"),
        ("QD-HSMT", "CIT-EXPIRED-TR-DT-2024"),
        ("QD-HSMT", "CIT-EXPIRED-TR-DTND-2024"),
        ("CV-MIEN-GP", "CIT-NOT-YET"),
        ("PL-HD-01", "CIT-TRANSITION-TR-HD-2026"),
        ("PL-HD-01", "CIT-TRANSITION-TR-HD-2026"),
        ("BB-NT-HM", "CIT-TRANSITION-NO-DATA"),
        ("QD-DC-DA", "CIT-EXPIRED-TR-LXD-2026"),
        ("QD-DC-DA", "CIT-EXPIRED-TR-HDXD-2026"),
        ("QD-DC-DA", "CIT-VBHN"),
        ("QD-DC-DA", "CIT-NOT-YET"),
    ])
    rows = regime_map(p, rules, REG)
    assert rows[0]["cells"]["hoat_dong_xd"] == "59/2015/NĐ-CP"
    assert rows[-1]["cells"]["luat_xd"] == "135/2025/QH15"


def test_cli_runs_multi_year_sample(capsys):
    assert main([str(ROOT / "examples" / "du_an_nhieu_nam.yaml"), "--as-of", "2026-10-03"]) == 0
    out = capsys.readouterr().out
    assert "Bản đồ chế độ pháp lý" in out and "CIT-TRANSITION-TR-HD-2026" in out


def test_unknown_start_is_not_treated_as_in_force():
    law = REG.docs["luat_95_2025"]  # chỉ nạp hiệu lực của Điều 56 khoản 1
    assert REG.status_at(law, D(2024, 1, 1)) == "unknown"
    assert REG.status_at(law, D(2025, 7, 1), "Điều 56 khoản 1") == "con"
    assert REG.status_at(law, D(2025, 6, 30), "Điều 56 khoản 1") == "chua"
    f = cite([{"id": "X", "ngay_ky": D(2024, 1, 1), "can_cu": ["95/2025/QH15"]}])
    assert set(by_id(f)) == {"CIT-NO-EFFECT-DATE"}


def test_registry_rejects_overlapping_main_documents(tmp_path):
    p = _reg_file(tmp_path, [
        {"id": "a", "so_hieu": "1/2020/NĐ-CP", "ten": "A", "domain": "x", "role": "chinh", "level": "recall",
         "hieu_luc_tu": D(2020, 1, 1)},
        {"id": "b", "so_hieu": "2/2021/NĐ-CP", "ten": "B", "domain": "x", "role": "chinh", "level": "recall",
         "hieu_luc_tu": D(2021, 6, 1)}])
    with pytest.raises(RuleError, match="chồng"):
        load_registry(p)
