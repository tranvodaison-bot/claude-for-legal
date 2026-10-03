import datetime as dt
import re

from crosscheck.dashboard import to_html
from crosscheck.engine import GAP, HARD, INFO, SOFT, Finding

D = dt.date(2026, 10, 3)
EVIL = '<script>alert(1)</script>'


def _f(sev, **kw):
    base = dict(rule_id="R-1", step="S", title="t", where="w", basis=[], fix="", trace=[])
    base.update(kw)
    return Finding(sev, **base)


def test_all_project_strings_are_escaped():
    project = {"project": {"id": "X", "name": EVIL}}
    f = _f(HARD, step=EVIL, title=EVIL, where=EVIL, fix=EVIL, trace=[EVIL],
           basis=[{"doc": EVIL, "provision": EVIL, "verified": False, "note": EVIL}])
    out = to_html(project, [f], D)
    assert out.count("<script") == 2  # chỉ khối JSON và khối JS của chính trang
    assert "alert(1)</script>" not in out.split('<script type="application/json"')[0]
    json_block = re.search(r'id="data">(.*?)</script>', out, re.S).group(1)
    assert "<" not in json_block  # JSON nhúng không chứa "<" thô


def test_counts_and_headline_from_data():
    fs = [_f(HARD), _f(SOFT), _f(SOFT), _f(GAP), _f(INFO)]
    out = to_html({"project": {"name": "P"}}, fs, D, scope={"rules": 15, "documents": 2, "registry": 3, "primary": 0})
    assert "P: 3 điểm cần xử lý" in out
    assert [int(x) for x in re.findall(r'class="kpi-n">(\d+)<', out)] == [1, 2, 1, 1]
    assert "0 đã đối chiếu văn bản gốc" in out
    assert out.count('class="f ') == 5


def test_empty_state_does_not_claim_compliance():
    out = to_html({"project": {"name": "P"}}, [], D)
    assert "không có điểm đỏ/vàng trong phạm vi đã kiểm" in out
    assert "không phải kết luận" in out
    assert "Đạt" not in out and "tuân thủ\"" not in out.replace('"tuân thủ"', "")


def test_unverified_marked_visibly():
    out = to_html({"project": {"name": "P"}}, [_f(SOFT, verified=False), _f(HARD, verified=True)], D)
    assert out.count("cần xác minh</span>") >= 1 and "đã xác minh</span>" in out
