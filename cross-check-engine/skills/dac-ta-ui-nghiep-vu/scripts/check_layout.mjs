#!/usr/bin/env node
// Chụp và kiểm bố cục một trang HTML ở nhiều bề rộng. Cần Playwright (npm i playwright) và Chromium.
// Dùng: node check_layout.mjs <file.html|url> [--out dir] [--widths 390,768,1440]
// Mã thoát: 0 sạch, 1 có vi phạm, 2 lỗi chạy.
import { createRequire } from "node:module";
import { mkdirSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
if (!args.length) { console.error("Dùng: node check_layout.mjs <file.html|url> [--out dir] [--widths 390,768,1440]"); process.exit(2); }
const target = args[0];
const opt = (k, d) => { const i = args.indexOf(k); return i > -1 ? args[i + 1] : d; };
const out = opt("--out", "layout-check");
const widths = opt("--widths", "390,768,1440").split(",").map(Number);
const url = /^https?:\/\//.test(target) ? target : pathToFileURL(resolve(target)).href;
if (!/^https?:/.test(url) && !existsSync(resolve(target))) { console.error(`Không thấy file: ${target}`); process.exit(2); }
mkdirSync(out, { recursive: true });

// require (không phải import) để tìm được Playwright cài toàn cục qua NODE_PATH.
let chromium;
try { ({ chromium } = createRequire(import.meta.url)("playwright")); }
catch { console.error("Chưa có Playwright: chạy `npm i playwright` (hoặc đặt NODE_PATH tới bản cài toàn cục)."); process.exit(2); }


const browser = await chromium.launch();
let violations = 0;
const report = [];
for (const w of widths) {
  const page = await browser.newPage({ viewport: { width: w, height: 900 } });
  const consoleErrors = [];
  page.on("console", (m) => { if (m.type() === "error") consoleErrors.push(m.text()); });
  page.on("pageerror", (e) => consoleErrors.push(String(e)));
  await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(200);
  const r = await page.evaluate((mobile) => {
    const vis = (el) => { const s = getComputedStyle(el); const b = el.getBoundingClientRect();
      return s.display !== "none" && s.visibility !== "hidden" && b.width > 0 && b.height > 0; };
    const doc = document.documentElement;
    const small = [];
    for (const el of document.querySelectorAll("body *")) {
      if (!vis(el)) continue;
      const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      if (own && parseFloat(getComputedStyle(el).fontSize) < 12) small.push(el.tagName.toLowerCase() + ": " + el.textContent.trim().slice(0, 40));
    }
    const tiny = [];
    if (mobile) for (const el of document.querySelectorAll("button, a[href], input, select, [role=button], summary")) {
      if (!vis(el)) continue;
      const b = el.getBoundingClientRect();
      if (b.height < 44 && !(el.tagName === "A" && el.closest("p, li, td"))) tiny.push(`${el.tagName.toLowerCase()} "${(el.textContent || el.value || el.getAttribute("aria-label") || "").trim().slice(0, 30)}" ${Math.round(b.height)}px`);
    }
    const unlabeled = [...document.querySelectorAll("input, select, textarea")].filter((el) => vis(el)
      && el.type !== "hidden" && !el.labels?.length && !el.getAttribute("aria-label") && !el.getAttribute("aria-labelledby"))
      .map((el) => el.outerHTML.slice(0, 60));
    return {
      overflowX: doc.scrollWidth > window.innerWidth + 1 ? `${doc.scrollWidth}px > ${window.innerWidth}px` : null,
      h1: document.querySelectorAll("h1").length,
      title: document.title,
      lang: doc.lang,
      smallText: small.slice(0, 10), smallTextCount: small.length,
      tinyTargets: tiny.slice(0, 10), tinyTargetCount: tiny.length,
      imgNoAlt: [...document.images].filter((i) => !i.hasAttribute("alt")).length,
      unlabeled,
    };
  }, w < 640);
  await page.screenshot({ path: `${out}/w${w}-first.png` });
  await page.screenshot({ path: `${out}/w${w}-full.png`, fullPage: true });
  const issues = [];
  if (r.overflowX) issues.push(`cuộn ngang ${r.overflowX}`);
  if (r.h1 !== 1) issues.push(`h1 = ${r.h1} (cần đúng 1)`);
  if (!r.title) issues.push("thiếu <title>");
  if (!r.lang) issues.push("thiếu lang trên <html>");
  if (r.smallTextCount) issues.push(`${r.smallTextCount} chữ < 12px`);
  if (r.tinyTargetCount) issues.push(`${r.tinyTargetCount} vùng bấm < 44px`);
  if (r.imgNoAlt) issues.push(`${r.imgNoAlt} ảnh thiếu alt`);
  if (r.unlabeled.length) issues.push(`${r.unlabeled.length} ô nhập thiếu nhãn`);
  if (consoleErrors.length) issues.push(`${consoleErrors.length} lỗi console`);
  violations += issues.length;
  report.push({ width: w, issues, details: { ...r, consoleErrors } });
  console.log(`${w}px: ${issues.length ? "VI PHẠM - " + issues.join("; ") : "sạch"}`);
  await page.close();
}
await browser.close();
const { writeFileSync } = await import("node:fs");
writeFileSync(`${out}/report.json`, JSON.stringify(report, null, 2));
console.log(`Ảnh và report.json: ${out}/`);
process.exit(violations ? 1 : 0);
