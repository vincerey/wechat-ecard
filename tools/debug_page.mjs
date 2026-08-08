import { createRequire } from "module";

const require = createRequire("file:///C:/Users/lhm/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/");
const { chromium } = require("playwright-core");

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const url = process.env.TEST_URL;
const proxy = process.env.TEST_PROXY;

const browser = await chromium.launch({ executablePath: CHROME, headless: true });
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  ...(proxy ? { proxy: { server: proxy } } : {}),
});
const page = await ctx.newPage();
page.on("response", (r) => {
  if (r.url().includes("jsdelivr")) console.log("RESP", r.status(), r.url().slice(0, 120));
});
try {
  const resp = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
  console.log("final url:", page.url());
  console.log("title:", await page.title());
  const text = await page.evaluate(() => document.body ? document.body.innerText.slice(0, 200) : "NO BODY");
  console.log("body:", text.replace(/\s+/g, " "));
} catch (e) {
  console.log("goto error:", e.message.split("\n")[0]);
}
await browser.close();
