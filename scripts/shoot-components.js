#!/usr/bin/env node
/*
 * Screenshot our Tailwind version of each Platforms Code component, as it
 * renders on the homepage, into assets/ours/<official-tag>.png. Elements are
 * found by their data-pc="<official tag>" marker.
 *
 * The official reference shots in assets/official/ were captured once from
 * @platformscode/core@0.0.53 web components and don't need regenerating.
 *
 * Usage (repo root, local server on :8765):
 *   python3 -m http.server 8765 &
 *   node scripts/shoot-components.js [chromium-executable]
 */
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const URL = process.env.URL || "http://localhost:8765/index.html";
const OUT = path.join(__dirname, "..", "assets", "ours");
const PAD = 12;
// Pick the same instance the official reference shows
const PICK = {
  "dga-featured-icon": '[aria-labelledby=h-tilawat] [data-pc="dga-featured-icon"]',
  "dga-icon": '[data-pc="dga-header-search-action"] [data-pc="dga-icon"]',
};
const MOBILE = ["dga-drawer-v2", "dga-drawer-header", "dga-drawer-nav", "dga-drawer-nav-item"];

async function shoot(page, tag) {
  const el = page.locator(PICK[tag] || `[data-pc="${tag}"]:visible`).first();
  if (!(await el.count())) return false;
  await el.scrollIntoViewIfNeeded();
  await page.waitForTimeout(200);
  const box = await el.boundingBox();
  if (!box || box.width < 2 || box.height < 2) return false;
  const vp = page.viewportSize();
  const x = Math.max(0, box.x - PAD), y = Math.max(0, box.y - PAD);
  await page.screenshot({
    path: path.join(OUT, `${tag}.png`),
    clip: { x, y, width: Math.min(vp.width - x, box.width + PAD * 2), height: Math.min(vp.height - y, box.height + PAD * 2) },
  });
  return true;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
  const tags = [...new Set([...html.matchAll(/data-pc="([a-z0-9-]+)"/g)].map((m) => m[1]))];
  const browser = await chromium.launch(process.argv[2] ? { executablePath: process.argv[2] } : {});
  const results = {};

  let page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2 });
  await page.goto(URL, { waitUntil: "networkidle" });
  for (let y = 0; y < 9000; y += 700) { await page.evaluate((y) => scrollTo(0, y), y); await page.waitForTimeout(100); }
  await page.addStyleTag({ content: ".proto-bar{display:none!important} header{position:static!important}" });
  for (const tag of tags) {
    if (MOBILE.includes(tag)) continue;
    results[tag] = await shoot(page, tag);
  }
  await page.close();

  page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.addStyleTag({ content: ".proto-bar{display:none!important}" });
  await page.locator("#menu-button").click();
  await page.waitForTimeout(500);
  for (const tag of MOBILE) if (tags.includes(tag)) results[tag] = await shoot(page, tag);
  await browser.close();

  const missed = Object.entries(results).filter(([, ok]) => !ok).map(([t]) => t);
  console.log(`captured ${Object.values(results).filter(Boolean).length}/${tags.length}`, missed.length ? `missed: ${missed.join(", ")}` : "");
})();
