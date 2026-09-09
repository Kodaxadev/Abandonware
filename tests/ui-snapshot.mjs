import { chromium } from "playwright";
import fs from "node:fs/promises";

const baseUrl = process.env.ABANDONWARE_BASE_URL || "http://127.0.0.1:8080";
const outputDir = process.env.ABANDONWARE_UI_OUTPUT || "ui-snapshots";

await fs.mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });

async function preparePage(viewport) {
  const page = await browser.newPage({ viewport });
  const consoleErrors = [];
  page.on("console", message => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForSelector(".classic-site");
  await page.waitForSelector("#game-grid [data-game-id]");
  await page.waitForSelector(".n99-browser");
  await page.waitForSelector(".n99-banner");
  return { page, consoleErrors };
}

async function verifyPage(page, consoleErrors, name, viewport) {
  const facts = await page.evaluate(() => {
    const launcher = document.getElementById("launcher-modal");
    const details = document.getElementById("details-modal");
    return {
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      classicSite: Boolean(document.querySelector(".classic-site")),
      cards: document.querySelectorAll("#game-grid [data-game-id]").length,
      stylesheetLoaded: [...document.styleSheets].some(sheet => String(sheet.href || "").includes("classic-mplayer.css")),
      polishStylesheetLoaded: [...document.styleSheets].some(sheet => String(sheet.href || "").includes("classic-polish.css")),
      nostalgiaStylesheetLoaded: [...document.styleSheets].some(sheet => String(sheet.href || "").includes("nostalgia-99.css")),
      nostalgiaBrowser: Boolean(document.querySelector(".n99-browser")),
      nostalgiaBanner: Boolean(document.querySelector(".n99-banner")),
      nostalgiaSession: Boolean(document.querySelector(".n99-sessionbar")),
      nostalgiaStatus: Boolean(document.querySelector(".n99-statusbar")),
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      launcherOpen: Boolean(launcher?.open),
      launcherDisplay: launcher ? getComputedStyle(launcher).display : "missing",
      detailsOpen: Boolean(details?.open),
      detailsDisplay: details ? getComputedStyle(details).display : "missing"
    };
  });

  if (facts.viewportWidth !== viewport.width || facts.viewportHeight !== viewport.height) {
    throw new Error(`${name} viewport mismatch: expected ${viewport.width}x${viewport.height}, got ${facts.viewportWidth}x${facts.viewportHeight}`);
  }
  if (
    !facts.classicSite ||
    !facts.stylesheetLoaded ||
    !facts.polishStylesheetLoaded ||
    !facts.nostalgiaStylesheetLoaded ||
    !facts.nostalgiaBrowser ||
    !facts.nostalgiaBanner ||
    !facts.nostalgiaSession ||
    !facts.nostalgiaStatus ||
    facts.cards < 1
  ) {
    throw new Error(`${name} classic UI did not initialize: ${JSON.stringify(facts)}`);
  }
  if (facts.horizontalOverflow) {
    throw new Error(`${name} has horizontal viewport overflow`);
  }
  if (facts.launcherOpen || facts.launcherDisplay !== "none" || facts.detailsOpen || facts.detailsDisplay !== "none") {
    throw new Error(`${name} leaked a closed dialog into the page: ${JSON.stringify(facts)}`);
  }
  if (consoleErrors.some(message => message.includes("Failed to load resource"))) {
    throw new Error(`${name} resource error: ${consoleErrors.join(" | ")}`);
  }
  return facts;
}

async function capture(name, viewport) {
  const { page, consoleErrors } = await preparePage(viewport);
  const facts = await verifyPage(page, consoleErrors, name, viewport);
  await page.screenshot({ path: `${outputDir}/${name}.png`, fullPage: true });
  await page.close();
  console.log(JSON.stringify({ name, ...facts }));
}

async function captureDialogs() {
  const viewport = { width: 1280, height: 900 };
  const { page, consoleErrors } = await preparePage(viewport);
  await verifyPage(page, consoleErrors, "classic-dialogs-1280", viewport);

  await page.locator('[data-game-id="xargon"]').click();
  await page.waitForFunction(() => document.getElementById("details-modal")?.open === true);
  await page.locator("#details-modal .details-frame").screenshot({
    path: `${outputDir}/classic-details-1280.png`
  });
  await page.locator("[data-close-details]").click();
  await page.waitForFunction(() => document.getElementById("details-modal")?.open !== true);

  await page.locator(".n99-banner").click();
  await page.waitForFunction(() => document.getElementById("launcher-modal")?.open === true);

  const launcherSteps = await page.evaluate(() => {
    const step1 = document.getElementById("launcher-step-1");
    const step2 = document.getElementById("launcher-step-2");
    const step3 = document.getElementById("launcher-step-3");
    return {
      step1Hidden: Boolean(step1?.hidden),
      step1Display: step1 ? getComputedStyle(step1).display : "missing",
      step2Hidden: Boolean(step2?.hidden),
      step2Display: step2 ? getComputedStyle(step2).display : "missing",
      step3Hidden: Boolean(step3?.hidden),
      step3Display: step3 ? getComputedStyle(step3).display : "missing"
    };
  });

  if (launcherSteps.step1Hidden || launcherSteps.step1Display === "none") {
    throw new Error(`launcher step 1 is not visible: ${JSON.stringify(launcherSteps)}`);
  }
  for (const number of [2, 3]) {
    if (!launcherSteps[`step${number}Hidden`] || launcherSteps[`step${number}Display`] !== "none") {
      throw new Error(`launcher inactive step ${number} leaked into the UI: ${JSON.stringify(launcherSteps)}`);
    }
  }

  await page.locator("#launcher-modal .modal-frame").screenshot({
    path: `${outputDir}/classic-launcher-1280.png`
  });

  if (consoleErrors.some(message => message.includes("Failed to load resource"))) {
    throw new Error(`dialog resource error: ${consoleErrors.join(" | ")}`);
  }
  await page.close();
}

await capture("classic-desktop-1280", { width: 1280, height: 900 });
await capture("classic-mobile-390", { width: 390, height: 844 });
await captureDialogs();
await browser.close();
