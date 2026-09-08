import { chromium } from "playwright";
import fs from "node:fs/promises";

const baseUrl = process.env.ABANDONWARE_BASE_URL || "http://127.0.0.1:8080";
const outputDir = process.env.ABANDONWARE_UI_OUTPUT || "ui-snapshots";

await fs.mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });

async function capture(name, viewport) {
  const page = await browser.newPage({ viewport });
  const consoleErrors = [];
  page.on("console", message => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForSelector(".classic-site");
  await page.waitForSelector("#game-grid [data-game-id]");

  const facts = await page.evaluate(() => ({
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    classicSite: Boolean(document.querySelector(".classic-site")),
    cards: document.querySelectorAll("#game-grid [data-game-id]").length,
    stylesheetLoaded: [...document.styleSheets].some(sheet => String(sheet.href || "").includes("classic-mplayer.css")),
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  }));

  if (facts.viewportWidth !== viewport.width || facts.viewportHeight !== viewport.height) {
    throw new Error(`${name} viewport mismatch: expected ${viewport.width}x${viewport.height}, got ${facts.viewportWidth}x${facts.viewportHeight}`);
  }
  if (!facts.classicSite || !facts.stylesheetLoaded || facts.cards < 1) {
    throw new Error(`${name} classic UI did not initialize: ${JSON.stringify(facts)}`);
  }
  if (facts.horizontalOverflow) {
    throw new Error(`${name} has horizontal viewport overflow`);
  }
  if (consoleErrors.some(message => message.includes("Failed to load resource"))) {
    throw new Error(`${name} resource error: ${consoleErrors.join(" | ")}`);
  }

  await page.screenshot({ path: `${outputDir}/${name}.png`, fullPage: true });
  await page.close();
  console.log(JSON.stringify({ name, ...facts }));
}

await capture("classic-desktop-1280", { width: 1280, height: 900 });
await capture("classic-mobile-390", { width: 390, height: 844 });
await browser.close();
