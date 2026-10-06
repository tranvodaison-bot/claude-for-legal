"""TC-NQ: kiểm CR-001 theo US-007a…f (docs/spec/SPEC-CR-001.md mục 5, 6)."""
import datetime as dt
from pathlib import Path

import pytest
import yaml

from crosscheck.cli import DEFAULT_CONSISTENCY, main
from crosscheck.consistency import check_consistency, fmt_num, load_consistency_rules
from crosscheck.engine import GAP, HARD, SOFT, RuleError, load_project

ROOT = Path(__file__).resolve().parent.parent
CFG = load_consistency_rules(DEFAULT_CONSISTENCY)
D = dt.date


def run(docs, **attrs):
    return check_consistency({"attributes": attrs, "documents": docs}, CFG)


def doc(i, nhom, day, **info):
    return {"id": i, "nhom": nhom, "ngay_ky": day, "thong_tin": info}


def ids(findings, gaps=False):
    """Mặc định bỏ phát hiện XÁM: dữ liệu test tối giản thường thiếu văn bản chuẩn tầng trên,
    engine báo XÁM đúng đặc tả mục 2; hành vi XÁM có test riêng (gaps=True)."""
    return sorted((f.rule_id, f.step) for f in findings if gaps or f.severity != GAP)


def violations(findings):
    return [f for f in findings if f.severity != GAP]


# US-007a
def test_name_ignores_case_spacing_punctuation():
    f, m = run([doc("CT", "chu_truong", D(2021, 1, 1), ten_du_an="Nhà xưởng A"),
                doc("PD", "phe_duyet_du_an", D(2021, 6, 1), ten_du_an="  nhà XƯỞNG  a. ")])
    assert ids(f, gaps=True) == [] and m["ten_du_an"]["rows"][0]["result"] == "khop"


def test_name_mismatch_reports_both_values():
    f, _ = run([doc("PD", "phe_duyet_du_an", D(2021, 6, 1), ten_du_an="Nhà xưởng A"),
                doc("GP", "gpxd", D(2022, 1, 1), ten_du_an="Nhà xưởng B")])
    v = violations(f)
    assert ids(f) == [("NQ-TEN-2", "GP")] and v[0].severity == SOFT
    assert "Nhà xưởng B" in v[0].where and "Nhà xưởng A" in v[0].where


# US-007b
def test_tmdt_difference_with_percent():
    f, _ = run([doc("BC", "bcnckt_hoan_thien", D(2021, 5, 1), tong_muc_dau_tu=118_000_000_000),
                doc("PD", "phe_duyet_du_an", D(2021, 6, 1), tong_muc_dau_tu=120_000_000_000)])
    assert ids(f) == [("NQ-TMDT-1", "PD")]
    assert "+2.000.000.000 đồng (+1,69%)" in violations(f)[0].where


def test_cumulative_capital_over_tmdt_is_red_only_for_public_capital():
    docs = [doc("PD", "phe_duyet_du_an", D(2021, 6, 1), tong_muc_dau_tu=100),
            doc("K1", "ke_hoach_von", D(2022, 1, 1), von_duoc_giao=60),
            doc("K2", "ke_hoach_von", D(2023, 1, 1), von_duoc_giao=50)]
    f, m = run(docs, von_dau_tu_cong=True)
    v = violations(f)
    assert ids(f) == [("NQ-VON-1", "K2")] and v[0].severity == HARD and v[0].verified
    assert [r["result"] for r in m["tong_muc_dau_tu"]["rows"] if r["rule"] == "NQ-VON-1"] == ["trong_han_muc", "vuot"]
    assert ids(run(docs)[0]) == []                       # dự án tư nhân / không khai báo
    assert ids(run(docs, von_dau_tu_cong=False)[0]) == []


# US-007c
def test_scale_mismatch_floors():
    f, _ = run([doc("TK", "phe_duyet_thiet_ke", D(2022, 1, 1), so_tang=3, chieu_cao=24.5),
                doc("GP", "gpxd", D(2022, 6, 1), so_tang=4, chieu_cao=24.5)])
    v = violations(f)
    assert ids(f) == [("NQ-QM-2", "GP")] and "4 tầng" in v[0].where and "3 tầng" in v[0].where


def test_tolerance_from_rule(tmp_path):
    data = yaml.safe_load(open(DEFAULT_CONSISTENCY, encoding="utf-8"))
    for r in data["rules"]:
        if r["id"] == "NQ-QM-2":
            r["tolerance"] = {"pct": 1}
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    cfg = load_consistency_rules(p)
    docs = [doc("TK", "phe_duyet_thiet_ke", D(2022, 1, 1), dien_tich_san=10000),
            doc("GP", "gpxd", D(2022, 6, 1), dien_tich_san=10050)]
    assert ids(check_consistency({"documents": docs}, cfg)[0]) == []
    docs[1]["thong_tin"]["dien_tich_san"] = 10200
    assert ids(check_consistency({"documents": docs}, cfg)[0]) == [("NQ-QM-2", "GP")]


# US-007d
def test_contract_period_beyond_project():
    f, _ = run([doc("PD", "phe_duyet_du_an", D(2021, 6, 1), thoi_gian_thuc_hien={"tu": D(2021, 6, 1), "den": D(2025, 12, 31)}),
                doc("HD", "hop_dong", D(2024, 11, 15), thoi_gian_thuc_hien={"tu": D(2024, 12, 1), "den": D(2026, 6, 30)})])
    assert ids(f) == [("NQ-TG-2", "HD")] and "kết thúc sau 181 ngày" in violations(f)[0].where


def test_period_missing_end_is_gap():
    f, _ = run([doc("PD", "phe_duyet_du_an", D(2021, 6, 1), thoi_gian_thuc_hien={"tu": D(2021, 6, 1), "den": D(2025, 12, 31)}),
                doc("HD", "hop_dong", D(2024, 11, 15), thoi_gian_thuc_hien={"tu": D(2024, 12, 1)})])
    g = [x for x in f if x.step == "HD"]
    assert ids(g, gaps=True) == [("NQ-TG-2-GAP", "HD")] and g[0].severity == GAP and "thiếu `tu` hoặc `den`" in g[0].where


# US-007e
def test_master_is_version_in_force_at_target_date():
    pd0 = doc("PD", "phe_duyet_du_an", D(2021, 6, 1), thoi_gian_thuc_hien={"tu": D(2021, 6, 1), "den": D(2025, 12, 31)})
    pd1 = doc("PD-DC", "phe_duyet_du_an", D(2026, 9, 1), thoi_gian_thuc_hien={"tu": D(2021, 6, 1), "den": D(2026, 12, 31)})
    pd1["thay_the"] = ["PD"]
    hd = doc("HD", "hop_dong", D(2024, 11, 15), thoi_gian_thuc_hien={"tu": D(2024, 12, 1), "den": D(2026, 6, 30)})
    f, _ = run([pd0, pd1, hd])
    assert ids(f) == [("NQ-TG-2", "HD")] and "[PD]" in violations(f)[0].where  # so với bản 2021, không phải 2026
    hd2 = doc("HD2", "hop_dong", D(2026, 10, 1), thoi_gian_thuc_hien={"tu": D(2026, 10, 1), "den": D(2026, 12, 1)})
    assert ids(run([pd0, pd1, hd2])[0]) == []                          # ký sau điều chỉnh -> so với bản 2026


def test_same_day_master_counts_and_falls_back_to_version_with_field():
    pd0 = doc("PD", "phe_duyet_du_an", D(2021, 6, 1), ten_du_an="A", tong_muc_dau_tu=100)
    pd1 = doc("PD-DC", "phe_duyet_du_an", D(2023, 1, 1), tong_muc_dau_tu=150)  # điều chỉnh không nhắc tên
    gp = doc("GP", "gpxd", D(2023, 1, 1), ten_du_an="A")
    f, m = run([pd0, pd1, gp])
    gp_row = next(r for r in m["ten_du_an"]["rows"] if r["doc"] == "GP")
    assert ids(f) == [] and gp_row["master"].startswith("PD (") and gp_row["result"] == "khop"


def test_invalid_supersession_and_missing_master():
    bad = doc("TK2", "phe_duyet_thiet_ke", D(2026, 9, 20), so_tang=3)
    bad["thay_the"] = ["GP", "KHONG-CO"]
    f, _ = run([doc("GP", "gpxd", D(2023, 5, 10), so_tang=4), bad])
    got = ids(f, gaps=True)
    assert ("NQ-PB", "TK2") in got and got.count(("NQ-PB", "TK2")) == 2
    assert ("NQ-QM-2-GAP", "GP") in got        # GPXD có số tầng nhưng chưa có thiết kế chuẩn ký trước


def test_unknown_group_is_gap_and_undated_doc_skipped():
    f, _ = run([{"id": "X", "nhom": "la", "ngay_ky": D(2022, 1, 1), "thong_tin": {"so_tang": 1}},
                {"id": "Y", "nhom": "gpxd", "thong_tin": {"so_tang": 1}}])
    assert ids(f, gaps=True) == [("NQ-NHOM", "X")]


# Nạp quy tắc
@pytest.mark.parametrize("patch,msg", [
    ({"compare": "gan_bang"}, "compare"),
    ({"severity": "vua"}, "severity"),
    ({"master": "khong_co"}, "nhóm"),
    ({"fields": ["khong_co"]}, "trường"),
    ({"fields": ["ten_du_an"], "compare": "equal_number"}, "không hợp"),
])
def test_rules_rejected(tmp_path, patch, msg):
    data = yaml.safe_load(open(DEFAULT_CONSISTENCY, encoding="utf-8"))
    data["rules"][0].update(patch)
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    with pytest.raises(RuleError, match=msg):
        load_consistency_rules(p)


def test_fmt_num_vietnamese():
    assert fmt_num(125_000_000_000) == "125.000.000.000" and fmt_num(24.5) == "24,5" and fmt_num(3.0) == "3"


# US-007f + mẫu end-to-end + hồi quy
def test_sample_project_expected_findings():
    f, m = check_consistency(load_project(ROOT / "examples" / "du_an_nhat_quan.yaml"), CFG)
    assert ids(f, gaps=True) == sorted([("NQ-PB", "QD-DC-TK"), ("NQ-TEN-2", "GPXD-01"), ("NQ-TMDT-1", "QD-PD-DA"),
                             ("NQ-TMDT-1", "QD-DC-DA"), ("NQ-VON-1", "KHV-2024"), ("NQ-QM-2", "GPXD-01"),
                             ("NQ-TG-1", "QD-DC-DA"), ("NQ-TG-2", "HD-TC-01")])
    assert set(m) == {"ten_du_an", "tong_muc_dau_tu", "dien_tich_san", "chieu_cao", "so_tang", "thoi_gian_thuc_hien"}


@pytest.mark.parametrize("sample", ["du_an_mau.yaml", "du_an_nhieu_nam.yaml"])
def test_regression_old_samples_unaffected(sample):
    assert check_consistency(load_project(ROOT / "examples" / sample), CFG) == ([], {})


def test_cli_outputs_include_matrix(tmp_path, capsys):
    sample = str(ROOT / "examples" / "du_an_nhat_quan.yaml")
    assert main([sample, "--as-of", "2026-10-03"]) == 1            # có ĐỎ (NQ-VON-1)
    assert "## Bảng đối chiếu thông tin" in capsys.readouterr().out
    out = tmp_path / "r.html"
    main([sample, "--as-of", "2026-10-03", "--format", "html", "--out", str(out)])
    html = out.read_text(encoding="utf-8")
    assert "Bảng đối chiếu thông tin" in html and "8 quy tắc nhất quán thông tin" in html
    bad = tmp_path / "bad.yaml"
    bad.write_text("rules: [{id: X, compare: sai}]", encoding="utf-8")
    assert main([sample, "--consistency", str(bad)]) == 2
