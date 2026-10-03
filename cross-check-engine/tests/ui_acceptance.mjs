#!/usr/bin/env node
// Nghiệm thu giao diện báo cáo HTML (docs/dac-ta-dashboard.md mục 9). Cần Node + Playwright + Chromium.
// Chạy từ cross-check-engine/:  node tests/ui_acceptance.mjs
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright");
const dir = mkdtempSync(join(tmpdir(), "xc-ui-"));
// Dự án có dữ liệu độc hại: mã văn bản chứa HTML, căn cứ chứa công thức bảng tính.
writeFileSync(join(dir, "p.yaml"), `project: {id: UI-TEST, name: "Kiểm thử <b>giao diện</b>"}
attributes: {}
steps:
  lap_bcnckt: {status: not_started}
  tham_dinh_bcnckt: {status: completed, date: 2025-02-01}
documents:
  - id: "<img src=x onerror=window.__xss=1>"
    ngay_ky: 2025-03-01
    can_cu: ['=HYPERLINK("http://x","bam")', "175/2024/NĐ-CP"]
  - id: '=HYPERLINK("http://x","bam")'
    ngay_ky: 2025-03-01
    can_cu: ["99/2099/TT-XX"]
  - id: QD-02
    ngay_ky: 2026-09-01
    ngay_nop: 2026-07-20
    can_cu: ["175/2024/NĐ-CP"]
`);
const out = join(dir, "r.html");
try { execFileSync("python3", ["-m", "crosscheck", join(dir, "p.yaml"), "--as-of", "2026-10-03", "--format", "html", "--out", out]); }
catch (e) { if (e.status !== 1) throw e; }  // 1 = có lỗi cứng, vẫn sinh file

const results = [];
const check = (name, ok, detail = "") => { results.push(ok); console.log(`${ok ? "ĐẠT " : "LỖI "} ${name}${detail ? " - " + detail : ""}`); };
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
let dialog = false; page.on("dialog", (d) => { dialog = true; d.dismiss(); });
const errors = []; page.on("pageerror", (e) => errors.push(String(e)));
await page.goto(pathToFileURL(out).href);

// 1. Tổng 4 ô = tổng phát hiện
const kpi = await page.$$eval(".kpi-n", (n) => n.map((x) => +x.textContent));
const total = await page.$$eval("#list .f", (n) => n.length);
check("Tổng các mức = tổng phát hiện", kpi.reduce((a, b) => a + b, 0) === total, `${kpi.join("+")} = ${total}`);

// 2. Dữ liệu độc hại hiển thị nguyên văn, không thực thi
check("Không thực thi mã chèn trong dữ liệu", !(await page.evaluate(() => window.__xss)) && !dialog);
const objText = await page.$$eval("#list .c-obj", (n) => n.map((x) => x.textContent));
check("Mã văn bản chứa HTML hiện nguyên văn", objText.some((t) => t.includes("<img src=x")));
check("H1 hiện nguyên văn thẻ <b>", (await page.textContent("h1")).includes("<b>giao diện</b>"));

// 3. Lọc rồi xuất CSV: số dòng = số đang hiện, công thức bị vô hiệu hóa
await page.selectOption("#fsev", "HARD");
const shown = await page.$$eval("#list .f", (n) => n.filter((x) => !x.hidden).length);
const btn = await page.textContent("#csv");
const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#csv")]);
const csv = (await (await dl.createReadStream()).toArray()).join("");
const csvRows = csv.trim().split("\r\n").length - 1;
check("Lọc ĐỎ: CSV đúng số dòng đang hiện", shown > 0 && csvRows === shown, `${csvRows} dòng / ${shown} đang hiện; nút "${btn}"`);
check("CSV có BOM UTF-8", csv.charCodeAt(0) === 0xfeff);
await page.selectOption("#fsev", "");
const all = await page.evaluate(() => window.__buildCsv());
check("Ô bắt đầu bằng công thức bị vô hiệu hóa trong CSV", all.includes(`,"'=HYPERLINK`) && !all.includes(`,"=HYPERLINK`));

// 4. Tìm không dấu, lọc rỗng có thông báo và xóa lọc
await page.fill("#q", "chuyen tiep");
const n1 = await page.$$eval("#list .f", (n) => n.filter((x) => !x.hidden).length);
check("Tìm không dấu khớp chữ có dấu", n1 > 0, `${n1} kết quả`);
await page.fill("#q", "khongcogiadaykhop");
check("Lọc rỗng hiện thông báo", await page.isVisible("#nomatch"));
await page.click("#reset2");
check("Xóa lọc trả lại đủ dòng", (await page.$$eval("#list .f", (n) => n.filter((x) => !x.hidden).length)) === total);

// 5. "Xem truy vết" mở đúng chi tiết
const link = await page.$("[data-open]");
if (link) { const id = await link.getAttribute("data-open"); await link.click();
  check("Xem truy vết mở chi tiết", await page.$eval(`#${id} details`, (d) => d.open)); }
check("Không có lỗi JS", errors.length === 0, errors.join("; "));
await browser.close();
const failed = results.filter((x) => !x).length;
console.log(failed ? `${failed} trường hợp LỖI` : `Tất cả ${results.length} trường hợp ĐẠT`);
process.exit(failed ? 1 : 0);
