/* 验证进页面（无任何点击）时音乐是否自动播放。
 * 用法：node tools/test_autoplay.mjs
 */
import { createRequire } from "module";

const require = createRequire("file:///C:/Users/lhm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/");
const { chromium } = require("playwright-core");

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const BASE = process.env.TEST_URL || "http://127.0.0.1:8000/";
const PROXY = process.env.TEST_PROXY;

const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
  isMobile: true,
  hasTouch: true,
  ...(PROXY ? { proxy: { server: PROXY } } : {}),
});
const page = await ctx.newPage();
const errors = [];
page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
page.on("pageerror", (e) => errors.push(e.message));

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForTimeout(4500);
const state = await page.evaluate(() => {
  const a = document.getElementById("bgm");
  return {
    paused: a.paused,
    readyState: a.readyState,
    currentTime: a.currentTime.toFixed(2),
    btn: document.getElementById("musicBtn").textContent,
    coverBtn: document.getElementById("coverMusicBtn").textContent,
  };
});
console.log(JSON.stringify({ state, errors }, null, 2));

// 模拟用户第一次触摸屏幕（不点开卡片，只摸一下）
await page.touchscreen.tap(12, 400);
await page.waitForTimeout(1200);
const afterTap = await page.evaluate(() => {
  const a = document.getElementById("bgm");
  return {
    paused: a.paused,
    currentTime: a.currentTime.toFixed(2),
    coverBtn: document.getElementById("coverMusicBtn").textContent,
    coverOpen: document.body.classList.contains("open"),
  };
});
console.log("after first touch: " + JSON.stringify(afterTap));
await browser.close();
