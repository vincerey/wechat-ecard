/* 本地自动化验证：截图封面层 / 内页层，检查 JS 报错与音乐状态。
 * 用法：先启动静态服务，再运行 node tools/test_page.mjs
 */
import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire("file:///C:/Users/lhm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/");
const { chromium } = require("playwright-core");

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const OUT = path.join(ROOT, "tools", "shots");
fs.mkdirSync(OUT, { recursive: true });

const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const BASE = process.env.TEST_URL || "http://127.0.0.1:8000/";

const browser = await chromium.launch({ executablePath: EDGE, headless: true });
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
  isMobile: true,
  hasTouch: true,
});
const page = await ctx.newPage();

const errors = [];
page.on("console", (m) => {
  if (m.type() === "error") errors.push("[console] " + m.text());
});
page.on("pageerror", (e) => errors.push("[pageerror] " + e.message));
page.on("response", (r) => {
  if (r.status() >= 400) errors.push("[http " + r.status() + "] " + r.url());
});

await page.goto(BASE + "?name=小美", { waitUntil: "networkidle" });
await page.waitForTimeout(1600);
await page.screenshot({ path: path.join(OUT, "1-cover.png") });

const coverInfo = await page.evaluate(() => ({
  title: document.title,
  name: document.getElementById("name").textContent,
  stars: document.querySelectorAll(".star").length,
  hearts: document.querySelectorAll("#coverHearts .floater").length,
  coverVisible: getComputedStyle(document.getElementById("cover")).visibility,
}));

await page.click("#openBtn");
await page.waitForTimeout(1600);
await page.screenshot({ path: path.join(OUT, "2-inner.png") });

const innerInfo = await page.evaluate(() => {
  const audio = document.getElementById("bgm");
  return {
    bodyOpen: document.body.classList.contains("open"),
    innerVisible: getComputedStyle(document.getElementById("inner")).visibility,
    cardText: document.querySelector(".message").innerText.replace(/\s+/g, " "),
    musicText: document.getElementById("musicBtn").textContent,
    audioReady: audio.readyState,
    audioTime: audio.currentTime.toFixed(2),
    confetti: document.querySelectorAll(".confetti-piece").length,
    sparkles: document.querySelectorAll(".sparkle").length,
  };
});

await page.click("#replayBtn");
await page.waitForTimeout(1200);
const replayInfo = await page.evaluate(() => ({
  bodyOpen: document.body.classList.contains("open"),
  coverVisible: getComputedStyle(document.getElementById("cover")).visibility,
  innerVisible: getComputedStyle(document.getElementById("inner")).visibility,
}));
await page.screenshot({ path: path.join(OUT, "3-replay-cover.png") });

console.log(JSON.stringify({ coverInfo, innerInfo, replayInfo, errors }, null, 2));
await browser.close();
