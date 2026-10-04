"""TC-XL: kiểm CR-003 theo US-008a…f (docs/spec/SPEC-CR-003.md mục 6, 7)."""
import datetime as dt
import shutil
import subprocess
from pathlib import Path

import pytest

openpyxl = pytest.importorskip("openpyxl")

from crosscheck.cli import DEFAULT_CONSISTENCY, DEFAULT_RULES, main          # noqa: E402
from crosscheck.consistency import load_consistency_rules                    # noqa: E402
from crosscheck.engine import load_project, load_rules                       # noqa: E402
from crosscheck.excel import SHEETS, ExcelInputError, load_project_xlsx, write_workbook  # noqa: E402
from crosscheck.excel import main as excel_main                              # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RULES, CFG = load_rules(DEFAULT_RULES), load_consistency_rules(DEFAULT_CONSISTENCY)
SAMPLES = ["du_an_mau", "du_an_nhieu_nam", "du_an_nhat_quan"]


def to_xlsx(tmp_path, sample="du_an_nhieu_nam"):
    out = tmp_path / f"{sample}.xlsx"
    write_workbook(out, RULES, CFG, load_project(ROOT / "examples" / f"{sample}.yaml"))
    return out


def edit(path, sheet, cell, value):
    wb = openpyxl.load_workbook(path)
    wb[sheet][cell] = value
    wb.save(path)


def errors_of(path):
    with pytest.raises(ExcelInputError) as e:
        load_project_xlsx(path, RULES, CFG)
    return e.value.errors


def col(sheet_cols, header):
    return next(openpyxl.utils.get_column_letter(i) for i, (_k, h) in enumerate(sheet_cols, 1) if h == header)


# US-008a + US-008f: khứ hồi YAML -> Excel -> báo cáo y hệt
@pytest.mark.parametrize("sample", SAMPLES)
def test_roundtrip_markdown_identical(tmp_path, capsys, sample):
    xlsx = to_xlsx(tmp_path, sample)
    rc_y = main([str(ROOT / "examples" / f"{sample}.yaml"), "--as-of", "2026-10-04"])
    md_y = capsys.readouterr().out
    rc_x = main([str(xlsx), "--as-of", "2026-10-04"])
    md_x = capsys.readouterr().out
    assert rc_x == rc_y and md_x == md_y


def test_roundtrip_project_structure(tmp_path):
    p = load_project_xlsx(to_xlsx(tmp_path), RULES, CFG)
    y = load_project(ROOT / "examples" / "du_an_nhieu_nam.yaml")
    assert p["steps"] == y["steps"] and p["contracts"] == y["contracts"]
    assert [d["id"] for d in p["documents"]] == [d["id"] for d in y["documents"]]
    assert p["documents"][5]["can_cu"][0] == {"van_ban": "135/2025/QH15", "dieu_khoan": "Điều 43 khoản 2"}


# US-008b: lỗi theo ô, gom hết, mã thoát 2, không ra báo cáo
def test_cell_errors_collected_and_cli_exit_2(tmp_path, capsys):
    from crosscheck.excel import CANCU, TRINHTU, VANBAN
    x = to_xlsx(tmp_path)
    edit(x, "TrinhTu", f"{col(TRINHTU, 'Trạng thái *')}4", "xong")
    edit(x, "VanBan", f"{col(VANBAN, 'Ngày ký')}7", "31/02/2023")
    edit(x, "CanCu", f"{col(CANCU, 'Mã văn bản *')}3", "QD-PD-DAA")
    errs = errors_of(x)
    assert len(errs) == 3
    assert errs[0].startswith("TrinhTu!B4") and "Hoàn thành" in errs[0]
    assert any(e.startswith("VanBan!D7") and "31/02/2023" in e for e in errs)
    assert any(e.startswith("CanCu!A3") and "QD-PD-DAA" in e for e in errs)
    assert main([str(x)]) == 2
    err = capsys.readouterr()
    assert "có 3 lỗi nhập liệu, chưa chạy đối soát" in err.err and err.out == ""


def test_required_unknown_duplicate_and_reference_errors(tmp_path):
    from crosscheck.excel import VANBAN
    x = to_xlsx(tmp_path)
    edit(x, "DuAn", "B3", None)                                    # Tên dự án trống
    edit(x, "VanBan", f"{col(VANBAN, 'Nhóm')}2", "Nhóm lạ")        # nhãn không có trong danh mục
    edit(x, "VanBan", "A3", "QD-PD-DA")                            # trùng mã văn bản
    edit(x, "VanBan", f"{col(VANBAN, 'Mã hợp đồng')}4", "HD-X")    # hợp đồng không tồn tại
    edit(x, "TrinhTu", "A2", "Bước không có")
    errs = " | ".join(errors_of(x))
    for needle in ("DuAn!B3", "Nhóm lạ", "\"QD-PD-DA\" trùng", "HD-X", "Bước không có"):
        assert needle in errs


def test_missing_sheet_and_column(tmp_path):
    x = to_xlsx(tmp_path)
    wb = openpyxl.load_workbook(x)
    del wb["VanBan"]
    wb["TrinhTu"]["B1"] = "Tình trạng"
    wb.save(x)
    errs = " | ".join(errors_of(x))
    assert "Thiếu sheet bắt buộc \"VanBan\"" in errs and "TrinhTu!1  Thiếu cột bắt buộc \"Trạng thái\"" in errs


def test_formula_without_cached_value_is_error(tmp_path):
    from crosscheck.excel import VANBAN
    x = to_xlsx(tmp_path, "du_an_nhat_quan")
    edit(x, "VanBan", f"{col(VANBAN, 'TMĐT (đồng)')}3", "=100+20")   # openpyxl không lưu giá trị đã tính
    errs = errors_of(x)
    assert len(errs) == 1 and "công thức chưa có giá trị" in errs[0]


def test_not_xlsx(tmp_path):
    bad = tmp_path / "ho_so.xlsx"
    bad.write_text("không phải excel", encoding="utf-8")
    assert "không phải file .xlsx hợp lệ" in errors_of(bad)[0]
    xls = tmp_path / "ho_so.xls"
    xls.write_text("x", encoding="utf-8")
    assert "chỉ nhận file .xlsx" in errors_of(xls)[0]


# US-008c: nhãn hoặc mã
def test_labels_or_codes_accepted(tmp_path):
    x = to_xlsx(tmp_path)
    edit(x, "TrinhTu", "B2", "completed")
    edit(x, "TrinhTu", "A3", "tham_dinh_bcnckt")
    p = load_project_xlsx(x, RULES, CFG)
    assert p["steps"]["lap_bcnckt"]["status"] == "completed" and "tham_dinh_bcnckt" in p["steps"]


# US-008d: ngày, số kiểu Việt Nam dạng chữ
def test_vietnamese_text_dates_and_numbers(tmp_path):
    from crosscheck.excel import VANBAN
    x = to_xlsx(tmp_path, "du_an_nhat_quan")
    edit(x, "VanBan", f"{col(VANBAN, 'Ngày ký')}4", "10/06/2021")
    edit(x, "VanBan", f"{col(VANBAN, 'TMĐT (đồng)')}4", "120.000.000.000")
    edit(x, "VanBan", f"{col(VANBAN, 'Chiều cao (m)')}4", "24,5")
    edit(x, "VanBan", f"{col(VANBAN, 'Số tầng')}4", "abc")
    errs = errors_of(x)
    assert len(errs) == 1 and "\"abc\" không phải số" in errs[0]
    edit(x, "VanBan", f"{col(VANBAN, 'Số tầng')}4", 3)
    d = next(d for d in load_project_xlsx(x, RULES, CFG)["documents"] if d["id"] == "QD-PD-DA")
    assert d["ngay_ky"] == dt.date(2021, 6, 10)
    assert d["thong_tin"]["tong_muc_dau_tu"] == 120_000_000_000 and d["thong_tin"]["chieu_cao"] == 24.5


# US-008e: file mẫu
def test_template_structure_and_dropdowns(tmp_path):
    out = tmp_path / "mau.xlsx"
    assert excel_main(["mau", str(out)]) == 0
    assert excel_main(["mau", str(out)]) == 2                      # không ghi đè
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == SHEETS
    formulas = {dv.formula1 for ws in wb for dv in ws.data_validations.dataValidation}
    assert len(formulas) == 4 and all(f.startswith("'HuongDan'!") for f in formulas)
    hd = wb["HuongDan"]
    names = {c.value for row in hd.iter_rows() for c in row if c.value}
    assert {r["name"] for r in RULES.values()} <= names and set(CFG["groups"].values()) <= names
    with pytest.raises(ExcelInputError):                          # mẫu trống: thiếu mã/tên dự án
        load_project_xlsx(out, RULES, CFG)


def test_convert_refuses_unsupported_keys(tmp_path):
    y = tmp_path / "p.yaml"
    y.write_text("project: {id: X, name: Y}\nsteps: {}\nkey_dates: {ngay_phe_duyet_du_an: 2021-01-01}\n", encoding="utf-8")
    assert excel_main(["tu-yaml", str(y), str(tmp_path / "p.xlsx")]) == 2
    assert not (tmp_path / "p.xlsx").exists()


def _calc_available() -> bool:
    return bool(shutil.which("soffice")) and Path("/etc/libreoffice/registry/calc.xcd").exists()


@pytest.mark.skipif(not _calc_available(), reason="không có LibreOffice Calc")
def test_files_open_and_reread_in_libreoffice(tmp_path):
    """Mẫu trống và hồ sơ đã chuyển mở được bằng LibreOffice Calc; file Calc lưu lại vẫn đọc ra hồ sơ như cũ."""
    x = to_xlsx(tmp_path)
    mau = tmp_path / "mau.xlsx"
    write_workbook(mau, RULES, CFG)
    re_dir = tmp_path / "re"
    for f in (x, mau):
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp_path}/lo", "--headless", "--convert-to",
                        "xlsx:Calc MS Excel 2007 XML", "--outdir", str(re_dir), str(f)],
                       check=True, capture_output=True, timeout=180)
        assert (re_dir / f.name).stat().st_size > 1000
    resaved = load_project_xlsx(re_dir / x.name, RULES, CFG)
    assert resaved == load_project_xlsx(x, RULES, CFG)
    wb = openpyxl.load_workbook(re_dir / mau.name)
    assert wb.sheetnames == SHEETS and sum(len(ws.data_validations.dataValidation) for ws in wb) == 4
