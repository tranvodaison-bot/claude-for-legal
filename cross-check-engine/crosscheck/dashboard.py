"""Báo cáo đối soát dạng web: một file HTML tự chứa, không gọi mạng.

Đặc tả: docs/dac-ta-dashboard.md (skill dac-ta-ui-nghiep-vu, phong cách Cockpit; bản in sáng).
Toàn bộ nội dung được dựng sẵn và thoát HTML ở đây; JS chỉ lọc, mở chi tiết và xuất CSV.
"""
from __future__ import annotations

import datetime as dt
import html
import json
from collections import Counter

from .engine import GAP, HARD, INFO, SOFT, Finding
from .report import DISCLAIMER

# mức -> (lớp css, nhãn, mô tả, ký hiệu). Ký hiệu khác nhau để phân biệt khi in đen trắng.
SEV = {
    HARD: ("do", "ĐỎ", "lỗi cứng", "■"),
    SOFT: ("vang", "VÀNG", "lỗi mềm / cần xác minh", "▲"),
    GAP: ("xam", "XÁM", "thiếu dữ liệu", "○"),
    INFO: ("xanh", "XANH", "thông tin, chuyển tiếp", "●"),
}
ORDER = (HARD, SOFT, GAP, INFO)


def confidence(f: Finding) -> str:
    # NQ-*: phép so sánh chắc chắn, nhưng dữ liệu đầu vào là khai báo của người nhập, chưa ai xác minh.
    if f.rule_id.startswith("NQ-"):
        return "so sánh dữ liệu khai báo"
    return "đã xác minh" if f.verified else "cần xác minh"


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _chip(sev: str) -> str:
    cls, label, desc, mark = SEV[sev]
    return f'<span class="chip {cls}"><span aria-hidden="true">{mark}</span> {label}<span class="sr"> – {e(desc)}</span></span>'


def _basis_items(basis: list) -> str:
    if not basis:
        return "<li>Không có (quy tắc chưa gắn căn cứ)</li>"
    out = []
    for b in basis:
        prov = b.get("provision") or "chưa điền điều/khoản"
        mark = "" if b.get("verified") else ' <span class="tag warn">chưa xác minh</span>'
        note = f' <span class="muted">({e(b["note"])})</span>' if b.get("note") else ""
        out.append(f"<li>{e(b.get('doc'))}, {e(prov)}{mark}{note}</li>")
    return "".join(out)


def _basis_text(basis: list) -> str:
    parts = []
    for b in basis or []:
        parts.append(f"{b.get('doc')}, {b.get('provision') or 'chưa điền điều/khoản'}"
                     + ("" if b.get("verified") else " - chưa xác minh"))
    return "; ".join(parts)


def _finding(fid: str, f: Finding) -> str:
    cls = SEV[f.severity][0]
    conf = ('<span class="tag ok">so sánh dữ liệu khai báo</span>' if f.rule_id.startswith("NQ-")
            else '<span class="tag ok">đã xác minh</span>' if f.verified
            else '<span class="tag warn">cần xác minh</span>')
    search = " ".join([f.rule_id, f.step, f.title, f.where, f.fix or ""])
    trace = "".join(f"<li>{e(t)}</li>" for t in f.trace) or "<li>Không có</li>"
    return f"""
<article class="f {cls}" id="{fid}" data-sev="{e(f.severity)}" data-obj="{e(f.step)}" data-search="{e(search)}">
  <details>
    <summary>
      <span class="c-sev">{_chip(f.severity)}</span>
      <span class="c-obj mono">{e(f.step)}</span>
      <span class="c-title">{e(f.title)}<span class="rid mono">{e(f.rule_id)}</span></span>
      <span class="c-conf">{conf}</span>
    </summary>
    <dl class="detail">
      <dt>Sai ở đâu</dt><dd>{e(f.where)}</dd>
      <dt>Căn cứ</dt><dd><ul>{_basis_items(f.basis)}</ul></dd>
      <dt>Cách khắc phục</dt><dd>{e(f.fix or "Chưa có hướng dẫn")}</dd>
      <dt>Truy vết</dt><dd><ol class="trace mono">{trace}</ol></dd>
    </dl>
  </details>
</article>"""


def _regime(regime: list, domains: dict) -> str:
    if not regime:
        return '<p class="muted">Chưa có bước nào có ngày để dựng bản đồ.</p>'
    cols = list(regime[0]["cells"])
    head = "".join(f'<th scope="col">{e(domains.get(c, c))}</th>' for c in cols)
    rows = "".join(
        f'<tr><th scope="row">{e(r["step"])}</th><td class="num">{r["date"].strftime("%d/%m/%Y")}</td>'
        + "".join(f'<td class="mono">{e(r["cells"][c])}</td>' for c in cols) + "</tr>"
        for r in regime)
    return (f'<div class="scroll" role="region" aria-label="Bảng chế độ pháp lý, cuộn ngang được" tabindex="0">'
            f'<table><thead><tr><th scope="col">Bước</th><th scope="col">Ngày</th>{head}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


RESULT = {"khop": ("ok", "✓", "Khớp"), "trong_han_muc": ("ok", "✓", "Trong hạn mức"),
          "lech": ("bad", "▲", "Lệch"), "vuot": ("bad", "▲", "Vượt"), "thieu_chuan": ("gap", "○", "Thiếu chuẩn")}


def _consistency(matrix: dict) -> str:
    if not matrix:
        return '<p class="empty">Chưa có văn bản nào khai báo thông tin để đối chiếu.</p>'
    out = []
    for key, block in matrix.items():
        rows = []
        for r in block["rows"]:
            cls, mark, text = RESULT[r["result"]]
            note = f'<span class="note">{e(r["note"])}</span>' if r["note"] else ""
            rows.append(
                f'<tr><th scope="row" class="mono">{e(r["doc"])}</th><td>{e(r["group"])}</td>'
                f'<td class="num">{r["date"].strftime("%d/%m/%Y")}</td>'
                f'<td class="{"num" if r.get("kind") == "number" else "txt"}">{e(r["value"])}'
                + (f'<span class="note">{e(r["extra"])}</span>' if r.get("extra") else "") + '</td>'
                f'<td>{e(r["master"] or "-")}</td>'
                f'<td><span class="res {cls}"><span aria-hidden="true">{mark}</span> {text}</span>{note}</td></tr>')
        out.append(
            f'<h3 id="dc-{e(key)}">{e(block["label"])}</h3>'
            f'<div class="scroll" role="region" aria-labelledby="dc-{e(key)}" tabindex="0"><table class="dc">'
            '<thead><tr><th scope="col">Văn bản</th><th scope="col">Nhóm</th><th scope="col">Ngày ký</th>'
            '<th scope="col">Giá trị</th><th scope="col">Chuẩn so sánh</th><th scope="col">Kết quả</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')
    return "".join(out)


def to_html(project: dict, findings: list[Finding], as_of: dt.date, regime=None, domains=None,
            scope: dict | None = None, consistency: dict | None = None) -> str:
    meta = project.get("project") or {}
    name = meta.get("name") or "Dự án"
    pid = meta.get("id") or "du-an"
    ids = [f"F{i:03d}" for i in range(1, len(findings) + 1)]
    count = Counter(f.severity for f in findings)
    urgent = [(i, f) for i, f in zip(ids, findings) if f.severity in (HARD, SOFT)]
    n_urgent = len(urgent)
    h1 = (f"{name}: {n_urgent} điểm cần xử lý" if n_urgent
          else f"{name}: không có điểm đỏ/vàng trong phạm vi đã kiểm")
    scope = scope or {}
    scope_txt = " · ".join(x for x in [
        f"{scope['rules']} quy tắc trình tự" if "rules" in scope else "",
        f"{scope['documents']} văn bản dự án" if "documents" in scope else "",
        (f"{scope['registry']} văn bản trong sổ ({scope.get('primary', 0)} đã đối chiếu văn bản gốc)"
         if "registry" in scope else ""),
        f"{scope['transitions']} quy tắc chuyển tiếp" if "transitions" in scope else "",
        f"{scope['consistency']} quy tắc nhất quán thông tin" if "consistency" in scope else "",
    ] if x)

    kpis = "".join(
        f'<div class="kpi {SEV[s][0]}"><span class="kpi-n">{count.get(s, 0)}</span>'
        f'<span class="kpi-l"><span aria-hidden="true">{SEV[s][3]}</span> {SEV[s][1]} – {e(SEV[s][2])}</span></div>'
        for s in ORDER)

    if urgent:
        urgent_html = "<ol class='urgent'>" + "".join(
            f'<li class="{SEV[f.severity][0]}">{_chip(f.severity)} <strong>{e(f.title)}</strong>'
            f'<p>{e(f.where)}</p><p class="fix"><span class="lbl">Khắc phục:</span> {e(f.fix or "Chưa có hướng dẫn")}</p>'
            f'<a class="btn ghost" href="#{fid}" data-open="{fid}">Xem truy vết <span class="mono">{e(f.rule_id)}</span></a></li>'
            for fid, f in urgent) + "</ol>"
    else:
        urgent_html = ('<p class="empty">Không có điểm đỏ/vàng trong phạm vi đã kiểm. Đây không phải kết luận '
                       '"tuân thủ": phạm vi kiểm được ghi ở phần Tổng quan.</p>')

    objects = sorted({f.step for f in findings})
    obj_opts = "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in objects)
    sev_opts = "".join(f'<option value="{s}">{SEV[s][1]} – {e(SEV[s][2])}</option>' for s in ORDER)
    rows = "".join(_finding(i, f) for i, f in zip(ids, findings))
    if not findings:
        rows = '<p class="empty">Không có phát hiện nào trong phạm vi đã kiểm.</p>'

    data = [{"id": i, "muc": f"{SEV[f.severity][1]} - {SEV[f.severity][2]}", "ma": f.rule_id, "doi_tuong": f.step,
             "tieu_de": f.title, "sai_o_dau": f.where, "can_cu": _basis_text(f.basis),
             "do_tin_cay": confidence(f), "khac_phuc": f.fix or ""}
            for i, f in zip(ids, findings)]
    data_json = json.dumps({"project": pid, "as_of": as_of.isoformat(), "rows": data},
                           ensure_ascii=False).replace("<", "\\u003c")

    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Báo cáo đối soát trình tự, hiệu lực và chuyển tiếp pháp luật của hồ sơ dự án {e(name)}">
<title>Đối soát – {e(name)}</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#can-xu-ly">Bỏ qua tới điểm cần xử lý</a>
<header class="top">
  <p class="eyebrow mono">{e(pid)} · đối soát {as_of.strftime("%d/%m/%Y")} <span class="tag warn">Bản nháp – cần xác minh</span></p>
  <h1>{e(h1)}</h1>
  <p class="lead">Kết quả đối soát trình tự - tiên quyết và hiệu lực căn cứ viện dẫn. Mọi số trên trang tính từ dữ liệu đầu vào của lần chạy này.</p>
  <p class="actions"><a class="btn primary" href="#can-xu-ly">Xem điểm cần xử lý</a></p>
</header>
<main>
<section aria-labelledby="h-tong-quan">
  <h2 id="h-tong-quan">Tổng quan</h2>
  <div class="kpis">{kpis}</div>
  <p class="scope"><span class="lbl">Phạm vi đã kiểm:</span> {e(scope_txt) or "không có thông tin phạm vi"}. Ngoài phạm vi này là chưa kiểm, không phải đạt.</p>
</section>
<section id="can-xu-ly" aria-labelledby="h-can-xu-ly" tabindex="-1">
  <h2 id="h-can-xu-ly">Cần xử lý</h2>
  {urgent_html}
</section>
<section aria-labelledby="h-che-do">
  <h2 id="h-che-do">Bản đồ chế độ pháp lý</h2>
  <p class="muted">Văn bản chính có hiệu lực tại ngày từng bước, theo ngày sự kiện, chưa xét chuyển tiếp.</p>
  {_regime(regime or [], domains or {})}
</section>
<section aria-labelledby="h-doi-chieu">
  <h2 id="h-doi-chieu">Bảng đối chiếu thông tin</h2>
  <p class="muted">So từng văn bản với văn bản chuẩn có hiệu lực tại ngày ký của nó.</p>
  {_consistency(consistency or {})}
</section>
<section aria-labelledby="h-tat-ca">
  <h2 id="h-tat-ca">Tất cả phát hiện</h2>
  <form class="toolbar" role="search" onsubmit="return false">
    <label>Tìm <input type="search" id="q" placeholder="mã, văn bản, nội dung…" autocomplete="off"></label>
    <label>Mức <select id="fsev"><option value="">Tất cả</option>{sev_opts}</select></label>
    <label>Đối tượng <select id="fobj"><option value="">Tất cả</option>{obj_opts}</select></label>
    <button type="button" class="btn ghost" id="reset">Xóa lọc</button>
    <button type="button" class="btn primary" id="csv">Xuất CSV</button>
  </form>
  <p class="count" id="count" aria-live="polite">{len(findings)} phát hiện</p>
  <p class="empty" id="nomatch" hidden>Không có phát hiện khớp bộ lọc. <button type="button" class="btn ghost" id="reset2">Xóa lọc</button></p>
  <div class="cols" aria-hidden="true"><span>Mức</span><span>Đối tượng</span><span>Nội dung</span><span>Độ tin cậy</span></div>
  <div id="list">{rows}</div>
  <div id="csvfallback" hidden>
    <p>Trình duyệt chặn tải file. Chọn toàn bộ nội dung dưới đây và lưu thành tệp .csv:</p>
    <label class="sr" for="csvtext">Nội dung CSV</label>
    <textarea id="csvtext" rows="8"></textarea>
  </div>
</section>
</main>
<footer><p>{e(DISCLAIMER)}</p><p class="muted">Sinh bởi cross-check-engine · {as_of.strftime("%d/%m/%Y")}</p></footer>
<script type="application/json" id="data">{data_json}</script>
<script>{JS}</script>
</body>
</html>
"""


CSS = """
:root{--bg:#101720;--surface:#182330;--raised:#203041;--fg:#EDF3F7;--muted:#A6B7C5;--accent:#69D4E4;
--on-accent:#101720;--border:#2B3A49;--focus:#A6EAF2;--warn:#F3C56A;--err:#EE8A91;--ok:#92D7B5;--info:#9FC3F0;
--s1:8px;--s2:12px;--s3:16px;--s4:24px;--s5:40px;--r:6px;
--sans:"IBM Plex Sans","Segoe UI",Roboto,"Noto Sans",Arial,sans-serif;--mono:"IBM Plex Mono",Consolas,"Noto Sans Mono","Courier New",monospace}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 var(--sans)}
.top,main,footer{max-width:1200px;margin:0 auto;padding:0 var(--s3)}
.top{padding-top:var(--s5);padding-bottom:var(--s4);border-bottom:1px solid var(--border)}
h1{font-size:32px;line-height:1.25;margin:var(--s1) 0 var(--s2);font-weight:600;overflow-wrap:anywhere}
h2{font-size:22px;line-height:1.3;margin:var(--s5) 0 var(--s3);font-weight:600}
p{margin:0 0 var(--s2)}
.lead{color:var(--muted);max-width:70ch}
.eyebrow{color:var(--muted);font-size:14px;display:flex;flex-wrap:wrap;gap:var(--s1);align-items:center}
.mono{font-family:var(--mono)}
.muted{color:var(--muted)}
.lbl{color:var(--muted);font-weight:500}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{position:absolute;left:-999px;display:inline-flex;align-items:center;min-height:44px}.skip:focus{left:var(--s3);top:var(--s1);background:var(--accent);color:var(--on-accent);padding:var(--s1) var(--s2);z-index:9}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.btn{display:inline-flex;align-items:center;gap:var(--s1);min-height:44px;padding:0 var(--s3);border-radius:var(--r);
border:1px solid var(--border);font:500 15px/1.2 var(--sans);text-decoration:none;cursor:pointer;transition:background .15s,border-color .15s}
.btn.primary{background:var(--accent);color:var(--on-accent);border-color:var(--accent)}
.btn.primary:hover{background:var(--focus)}
.btn.ghost{background:transparent;color:var(--fg)}
.btn.ghost:hover{background:var(--raised);border-color:var(--muted)}
.tag{display:inline-block;font-size:13px;line-height:1.4;padding:1px 8px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}
.tag.warn{color:var(--warn)}.tag.ok{color:var(--ok)}
.chip{display:inline-flex;gap:4px;align-items:center;font:600 13px/1.4 var(--sans);letter-spacing:.02em;white-space:nowrap}
.chip.do,.do .kpi-n{color:var(--err)}.chip.vang,.vang .kpi-n{color:var(--warn)}
.chip.xam,.xam .kpi-n{color:var(--muted)}.chip.xanh,.xanh .kpi-n{color:var(--info)}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:var(--s3)}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:var(--s3);display:flex;flex-direction:column;gap:4px}
.kpi.do{border-left:4px solid var(--err)}.kpi.vang{border-left:4px solid var(--warn)}.kpi.xam{border-left:4px solid var(--muted)}.kpi.xanh{border-left:4px solid var(--info)}
.kpi-n{font:600 36px/1.1 var(--mono);font-variant-numeric:tabular-nums}
.kpi-l{font-size:14px;color:var(--muted)}
.scope{margin-top:var(--s3);color:var(--muted);font-size:15px}
.urgent{list-style:none;margin:0;padding:0;display:grid;gap:var(--s2)}
.urgent li{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--warn);border-radius:var(--r);padding:var(--s3)}
.urgent li.do{border-left-color:var(--err)}
.urgent li p{margin:var(--s1) 0;overflow-wrap:anywhere}
.urgent .fix{color:var(--fg)}
.empty{background:var(--surface);border:1px dashed var(--border);border-radius:var(--r);padding:var(--s3)}
.scroll{overflow-x:auto;border:1px solid var(--border);border-radius:var(--r)}
h3{font-size:16px;font-weight:600;margin:var(--s4) 0 var(--s1);text-transform:uppercase;letter-spacing:.03em;line-height:1.4;color:var(--muted)}
.res{font-weight:600;white-space:nowrap}.res.ok{color:var(--ok)}.res.bad{color:var(--warn)}.res.gap{color:var(--muted)}
.note{display:block;font-size:13px;color:var(--muted);white-space:normal}
table.dc td,table.dc th{white-space:normal}
table.dc td.num,table.dc td:nth-child(3){white-space:nowrap}
table.dc td:last-child{min-width:180px}
table.dc .txt{font-family:var(--sans);min-width:150px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:var(--s1) var(--s2);border-bottom:1px solid var(--border);text-align:left;vertical-align:top;white-space:nowrap}
thead th{background:var(--surface);color:var(--muted);font-weight:500}
tbody th{font-weight:500;white-space:normal;min-width:200px}
.num{text-align:right;font-variant-numeric:tabular-nums;font-family:var(--mono)}
.toolbar{display:flex;flex-wrap:wrap;gap:var(--s2);align-items:flex-end;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:var(--s3)}
.toolbar label{display:flex;flex-direction:column;gap:4px;font-size:14px;color:var(--muted)}
.toolbar input,.toolbar select{min-height:44px;background:var(--bg);color:var(--fg);border:1px solid var(--border);border-radius:var(--r);padding:0 var(--s2);font:15px var(--sans);min-width:180px}
.toolbar input{min-width:240px}
.count{margin:var(--s2) 0;color:var(--muted);font-size:14px}
.cols,.f summary{display:grid;grid-template-columns:150px 150px minmax(0,1fr) 130px;gap:var(--s3);align-items:center}
.cols{padding:0 var(--s3) var(--s1);color:var(--muted);font-size:14px;border-bottom:1px solid var(--border)}
.f{border-bottom:1px solid var(--border)}
.f summary{list-style:none;cursor:pointer;min-height:44px;padding:var(--s2) var(--s3);transition:background .15s}
.f summary::-webkit-details-marker{display:none}
.f summary:hover,.f details[open] summary{background:var(--surface)}
.c-obj{font-size:14px;color:var(--muted);overflow-wrap:anywhere}
.c-title{overflow-wrap:anywhere}
.rid{display:block;font-size:13px;color:var(--muted);margin-top:2px}
.f.target summary{outline:2px solid var(--focus)}
.detail{display:grid;grid-template-columns:160px minmax(0,1fr);gap:var(--s1) var(--s3);margin:0;padding:var(--s3) var(--s3) var(--s4);background:var(--surface)}
.detail dt{color:var(--muted);font-size:14px}
.detail dd{margin:0;overflow-wrap:anywhere}
.detail ul,.detail ol{margin:0;padding-left:20px}
.trace{font-size:14px}
textarea{width:100%;background:var(--bg);color:var(--fg);border:1px solid var(--border);border-radius:var(--r);font:14px var(--mono);padding:var(--s2)}
footer{margin-top:var(--s5);padding-top:var(--s4);padding-bottom:var(--s5);border-top:1px solid var(--border);font-size:14px}
html:not(.js) .toolbar,html:not(.js) #csvfallback{display:none}
@media (max-width:1023px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:767px){
 h1{font-size:26px}
 .cols{display:none}
 .f summary{grid-template-columns:1fr;gap:4px}
 .detail{grid-template-columns:1fr}
 .detail dt{margin-top:var(--s1)}
 .toolbar label,.toolbar input,.toolbar select{width:100%;min-width:0}
 .toolbar .btn{flex:1 1 auto;justify-content:center}
 .urgent .btn{width:100%;justify-content:center}
}
@media (max-width:479px){.kpis{grid-template-columns:1fr 1fr;gap:var(--s2)}.kpi-n{font-size:30px}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
@media print{
 :root{--bg:#fff;--surface:#fff;--raised:#fff;--fg:#111;--muted:#444;--border:#ccc;--accent:#111;--err:#111;--warn:#111;--ok:#111;--info:#111}
 body{font-size:12pt}
 .toolbar,.actions,.skip,.btn,#csvfallback,.count,#nomatch{display:none!important}
 .f,.urgent li,.kpi{break-inside:avoid}
 details::details-content{content-visibility:visible;display:block}
 .scroll{overflow:visible}
 .f summary,.f summary:hover,.f details[open] summary,.detail{background:none!important;color:#111!important}
 .f.target summary{outline:none}
 th,td{white-space:normal}
 a{color:inherit;text-decoration:none}
}
"""

JS = r"""
(function(){
  document.documentElement.classList.add('js');
  var data = JSON.parse(document.getElementById('data').textContent);
  var list = Array.prototype.slice.call(document.querySelectorAll('#list .f'));
  var q = document.getElementById('q'), fsev = document.getElementById('fsev'), fobj = document.getElementById('fobj');
  var count = document.getElementById('count'), nomatch = document.getElementById('nomatch');
  var csvBtn = document.getElementById('csv');
  function norm(s){ return (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/đ/g,'d').replace(/Đ/g,'D').toLowerCase(); }
  list.forEach(function(el){ el._s = norm(el.getAttribute('data-search')); });
  function visible(){ return list.filter(function(el){ return !el.hidden; }); }
  function apply(){
    var t = norm(q.value.trim()), s = fsev.value, o = fobj.value;
    list.forEach(function(el){
      el.hidden = !((!t || el._s.indexOf(t) > -1) && (!s || el.getAttribute('data-sev') === s) && (!o || el.getAttribute('data-obj') === o));
    });
    var n = visible().length;
    count.textContent = 'Đang hiện ' + n + '/' + list.length + ' phát hiện';
    csvBtn.textContent = 'Xuất CSV (' + n + ' dòng)';
    csvBtn.disabled = n === 0;
    nomatch.hidden = n !== 0 || list.length === 0;
  }
  function reset(){ q.value=''; fsev.value=''; fobj.value=''; apply(); q.focus(); }
  [q, fsev, fobj].forEach(function(c){ c.addEventListener('input', apply); c.addEventListener('change', apply); });
  document.getElementById('reset').addEventListener('click', reset);
  document.getElementById('reset2').addEventListener('click', reset);
  function cell(v){
    var s = v == null ? '' : String(v);
    if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;  // chặn công thức khi mở bằng bảng tính
    return '"' + s.replace(/"/g, '""') + '"';
  }
  var cols = [['muc','Mức'],['ma','Mã quy tắc'],['doi_tuong','Đối tượng'],['tieu_de','Tiêu đề'],['sai_o_dau','Sai ở đâu'],
              ['can_cu','Căn cứ'],['do_tin_cay','Độ tin cậy'],['khac_phuc','Cách khắc phục']];
  function buildCsv(){
    var ids = {}; visible().forEach(function(el){ ids[el.id] = true; });
    var lines = [cols.map(function(c){ return cell(c[1]); }).join(',')];
    data.rows.forEach(function(r){ if (ids[r.id]) lines.push(cols.map(function(c){ return cell(r[c[0]]); }).join(',')); });
    return '﻿' + lines.join('\r\n') + '\r\n';
  }
  window.__buildCsv = buildCsv;
  csvBtn.addEventListener('click', function(){
    var text = buildCsv();
    try {
      var url = URL.createObjectURL(new Blob([text], {type:'text/csv;charset=utf-8'}));
      var a = document.createElement('a');
      a.href = url; a.download = 'doi-soat-' + data.project + '-' + data.as_of + '.csv';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
    } catch (err) {
      var fb = document.getElementById('csvfallback');
      document.getElementById('csvtext').value = text; fb.hidden = false;
    }
  });
  function openTarget(id){
    var el = document.getElementById(id);
    if (!el || !el.classList.contains('f')) return;
    if (el.hidden) reset();
    list.forEach(function(x){ x.classList.remove('target'); });
    el.classList.add('target');
    el.querySelector('details').open = true;
    el.querySelector('summary').focus();
  }
  document.addEventListener('click', function(ev){
    var a = ev.target.closest && ev.target.closest('[data-open]');
    if (a) { ev.preventDefault(); history.replaceState(null, '', '#' + a.getAttribute('data-open')); openTarget(a.getAttribute('data-open')); }
  });
  if (location.hash) openTarget(location.hash.slice(1));
  window.addEventListener('beforeprint', function(){ list.forEach(function(el){ el.querySelector('details').open = true; }); });
  apply();
})();
"""
