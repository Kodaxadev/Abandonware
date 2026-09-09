import { chromium } from "playwright";
import fs from "node:fs/promises";

const baseUrl = process.env.ABANDONWARE_BASE_URL || "http://127.0.0.1:8080";
const outputDir = process.env.ABANDONWARE_GAME_SHOT_OUTPUT || "featured-game-shots";

await fs.mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });

const targets = [
  { id: "xargon", file: "xargon.png", runtime: "jsdos", settle: 12000 },
  { id: "beneath-a-steel-sky", file: "beneath-a-steel-sky.png", runtime: "scummvm", settle: 10000 },
  { id: "dreamweb", file: "dreamweb.png", runtime: "scummvm", settle: 10000 },
  { id: "robins-rescue", file: "robins-rescue.png", runtime: "scummvm", settle: 10000 }
];

let captured = 0;

for (const target of targets) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const failures = [];
  page.on("pageerror", error => failures.push(error.message));

  try {
    await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector(`[data-game-id="${target.id}"]`);
    await page.locator(`[data-game-id="${target.id}"]`).click();
    await page.waitForFunction(() => document.getElementById("details-modal")?.open === true);
    await page.locator("#details-play-hosted").click();
    await page.waitForFunction(() => document.getElementById("launcher-modal")?.open === true);
    await page.waitForFunction(() => !document.getElementById("launcher-step-3")?.hidden);

    if (target.runtime === "scummvm") {
      const frame = page.locator("#dos-player iframe.scummvm-frame");
      await frame.waitFor({ state: "visible", timeout: 45000 });
      await page.waitForTimeout(target.settle);
      await frame.screenshot({ path: `${outputDir}/${target.file}` });
    } else {
      const player = page.locator("#dos-player");
      await player.waitFor({ state: "visible", timeout: 45000 });
      await page.waitForTimeout(target.settle);
      await player.screenshot({ path: `${outputDir}/${target.file}` });
    }

    captured += 1;
    console.log(`captured ${target.id} -> ${target.file}; status=${await page.locator("#emulator-status").textContent()}`);
  } catch (error) {
    console.warn(`capture failed for ${target.id}: ${error?.message || error}`);
  } finally {
    if (failures.length) {
      console.warn(`${target.id}: page errors observed: ${failures.join(" | ")}`);
    }
    await page.close();
  }
}

await browser.close();

if (captured === 0) {
  throw new Error("No featured runtime screenshots were captured.");
}

console.log(`captured ${captured}/${targets.length} featured game visuals`);
