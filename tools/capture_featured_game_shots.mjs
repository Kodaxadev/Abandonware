import { chromium } from "playwright";
import fs from "node:fs/promises";

const baseUrl = process.env.ABANDONWARE_BASE_URL || "http://127.0.0.1:8080";
const outputDir = process.env.ABANDONWARE_GAME_SHOT_OUTPUT || "featured-game-shots";

await fs.mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });

const targets = [
  { id: "xargon", file: "xargon", runtime: "jsdos", settle: 6500, keys: ["Enter", "Escape", "Space"] },
  { id: "beneath-a-steel-sky", file: "beneath-a-steel-sky", runtime: "scummvm", settle: 4500, keys: ["Escape", "Escape"] },
  { id: "dreamweb", file: "dreamweb", runtime: "scummvm", settle: 4500, keys: ["Escape", "Escape", "Enter"] },
  { id: "robins-rescue", file: "robins-rescue", runtime: "scummvm", settle: 4500, keys: ["Escape", "Enter"] }
];

let captured = 0;

async function runtimeFrameFor(page, timeout = 45000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const frame = page.frames().find(candidate => candidate.url().includes("/runtime/scummvm/index.html"));
    if (frame) return frame;
    await page.waitForTimeout(100);
  }
  throw new Error("ScummVM runtime iframe never attached");
}

async function captureScummVmCandidates(page, target) {
  const frameElement = page.locator("#dos-player iframe.scummvm-frame");
  await frameElement.waitFor({ state: "visible", timeout: 45000 });
  const frame = await runtimeFrameFor(page);
  const canvas = frame.locator("canvas").first();
  await canvas.waitFor({ state: "visible", timeout: 45000 });

  await page.waitForTimeout(target.settle);
  await canvas.screenshot({ path: `${outputDir}/${target.file}-0.png` });

  for (const key of target.keys) {
    try {
      await canvas.press(key, { timeout: 5000 });
    } catch {
      try { await frame.locator("body").press(key, { timeout: 5000 }); } catch {}
    }
    await page.waitForTimeout(900);
  }

  await page.waitForTimeout(2500);
  await canvas.screenshot({ path: `${outputDir}/${target.file}-1.png` });
  await page.waitForTimeout(5000);
  await canvas.screenshot({ path: `${outputDir}/${target.file}-2.png` });
}

async function captureJsDosCandidates(page, target) {
  const player = page.locator("#dos-player");
  await player.waitFor({ state: "visible", timeout: 45000 });
  await page.waitForTimeout(target.settle);
  await player.screenshot({ path: `${outputDir}/${target.file}-0.png` });

  try { await player.click({ position: { x: 180, y: 120 } }); } catch {}
  for (const key of target.keys) {
    try { await page.keyboard.press(key); } catch {}
    await page.waitForTimeout(800);
  }

  await page.waitForTimeout(3000);
  const visibleCanvas = page.locator("#dos-player canvas:visible").last();
  if (await visibleCanvas.count()) {
    await visibleCanvas.screenshot({ path: `${outputDir}/${target.file}-1.png` });
    await page.waitForTimeout(4500);
    await visibleCanvas.screenshot({ path: `${outputDir}/${target.file}-2.png` });
  } else {
    await player.screenshot({ path: `${outputDir}/${target.file}-1.png` });
    await page.waitForTimeout(4500);
    await player.screenshot({ path: `${outputDir}/${target.file}-2.png` });
  }
}

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
      await captureScummVmCandidates(page, target);
    } else {
      await captureJsDosCandidates(page, target);
    }

    captured += 1;
    console.log(`captured candidate frames for ${target.id}; status=${await page.locator("#emulator-status").textContent()}`);
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

console.log(`captured gameplay candidates for ${captured}/${targets.length} featured titles`);
