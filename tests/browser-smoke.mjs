import { chromium } from "playwright";

const baseUrl = process.env.ABANDONWARE_BASE_URL || "http://127.0.0.1:8080";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });

const requests = [];
const consoleErrors = [];
const pageErrors = [];

page.on("request", request => requests.push(request.url()));
page.on("console", message => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("pageerror", error => pageErrors.push(error.message));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForRequestPart(part, timeout = 30000) {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    if (requests.some(url => url.includes(part))) return;
    await page.waitForTimeout(100);
  }
  throw new Error(`Timed out waiting for request containing ${part}`);
}

async function stopAndCloseRuntime() {
  const stop = page.locator("#emulator-stop");
  if (await stop.isVisible()) {
    await stop.click();
    await page.waitForTimeout(500);
  }

  const dialog = page.locator("#launcher-modal");
  if (await dialog.getAttribute("open") !== null) {
    const close = dialog.locator("[data-close-launcher]");
    if (await close.isVisible()) {
      await close.click();
      await page.waitForFunction(() => !document.getElementById("launcher-modal")?.open);
    }
  }
}

try {
  await page.goto(baseUrl, { waitUntil: "networkidle", timeout: 30000 });

  const runtime = await page.evaluate(() => ({
    hasDos: typeof window.Dos === "function",
    hasZip: typeof window.JSZip === "function",
    jsdos: window.ABANDONWARE_JSDOS || null,
    gameCount: Array.isArray(window.ABANDONWARE_GAMES) ? window.ABANDONWARE_GAMES.length : 0,
    hostedCount: Array.isArray(window.ABANDONWARE_GAMES)
      ? window.ABANDONWARE_GAMES.filter(game => game.hostable).length
      : 0,
    localDosCount: Array.isArray(window.ABANDONWARE_GAMES)
      ? window.ABANDONWARE_GAMES.filter(game => !game.hostable && game.filter === "dos").length
      : 0
  }));

  assert(runtime.hasDos, "Pinned js-dos global did not initialize");
  assert(runtime.hasZip, "Pinned local JSZip global did not initialize");
  assert(runtime.jsdos?.version === "8.4.1", `Unexpected js-dos version marker: ${runtime.jsdos?.version}`);
  assert(runtime.jsdos?.pathPrefix === "runtime/jsdos/emulators/", "js-dos local emulator bridge is not active");
  assert(runtime.gameCount >= 13, `Catalog unexpectedly small: ${runtime.gameCount}`);
  assert(runtime.hostedCount >= 13, `Hosted catalog unexpectedly small: ${runtime.hostedCount}`);
  assert(runtime.localDosCount >= 1, "No local DOS restoration targets were found");

  // Capability-aware filtering must reflect the same catalog truth used by the launch actions.
  await page.locator('[data-filter="playable"]').click();
  await page.waitForFunction(
    expected => document.querySelectorAll('#game-grid [data-game-id]').length === expected,
    runtime.hostedCount
  );
  let filteredIds = await page.locator("#game-grid [data-game-id]").evaluateAll(nodes => nodes.map(node => node.dataset.gameId));
  let filterTruth = await page.evaluate(ids => {
    const byId = new Map(window.ABANDONWARE_GAMES.map(game => [game.id, game]));
    return ids.every(id => byId.get(id)?.hostable && byId.get(id)?.hostedUrl);
  }, filteredIds);
  assert(filterTruth, "PLAYABLE filter exposed a non-hosted game");

  await page.locator('[data-filter="local-dos"]').click();
  await page.waitForFunction(
    expected => document.querySelectorAll('#game-grid [data-game-id]').length === expected,
    runtime.localDosCount
  );
  filteredIds = await page.locator("#game-grid [data-game-id]").evaluateAll(nodes => nodes.map(node => node.dataset.gameId));
  filterTruth = await page.evaluate(ids => {
    const byId = new Map(window.ABANDONWARE_GAMES.map(game => [game.id, game]));
    return ids.every(id => !byId.get(id)?.hostable && byId.get(id)?.filter === "dos");
  }, filteredIds);
  assert(filterTruth, "LOCAL DOS filter exposed an unsupported or hosted record");

  await page.locator('[data-filter="all"]').click();
  await page.waitForFunction(
    expected => document.querySelectorAll('#game-grid [data-game-id]').length === expected,
    runtime.gameCount
  );

  // Launch a real hosted DOS title through the same UI path a user follows.
  await page.locator('[data-game-id="xargon"]').click();
  await page.locator("#details-play-hosted").click();
  await waitForRequestPart("games/xargon.jsdos");
  await waitForRequestPart("runtime/jsdos/emulators/emulators.js");
  await waitForRequestPart("runtime/jsdos/emulators/wdosbox.wasm");
  await page.waitForTimeout(1200);

  assert(
    !requests.some(url => url.includes("v8.js-dos.com/latest")),
    "DOS launch contacted the mutable js-dos /latest CDN"
  );

  await stopAndCloseRuntime();

  // Build a tiny DOS ZIP with the exact vendored JSZip running in the page, then put it
  // through the local-file workbench. No binary fixture or server upload is involved.
  const localZipBase64 = await page.evaluate(async () => {
    const zip = new window.JSZip();
    zip.file("GAME.BAT", "@echo off\r\necho ABANDONWARE_LOCAL_IMPORT_OK\r\npause\r\n");
    return zip.generateAsync({ type: "base64", compression: "DEFLATE" });
  });

  await page.locator("[data-open-launcher]").first().click();
  await page.locator("#game-file").setInputFiles({
    name: "local-workbench-test.zip",
    mimeType: "application/zip",
    buffer: Buffer.from(localZipBase64, "base64")
  });
  await page.waitForFunction(() => !document.getElementById("launcher-step-2")?.hidden);

  const selectedArchive = await page.locator("#selected-file-name").textContent();
  assert(selectedArchive?.includes("local-workbench-test.zip"), "Local ZIP was not accepted by the workbench");

  const bootOptions = await page.locator("#boot-target option").allTextContents();
  assert(bootOptions.some(value => value.includes("GAME.BAT")), `GAME.BAT was not detected: ${bootOptions.join(", ")}`);

  await page.locator("#rights-confirm").check();
  assert(!(await page.locator("#start-emulation").isDisabled()), "Rights confirmation did not unlock local emulation");
  await page.locator("#start-emulation").click();
  await page.waitForFunction(() => !document.getElementById("launcher-step-3")?.hidden);
  await page.waitForTimeout(1200);

  assert(await page.locator("#dos-player").count() === 1, "Local ZIP did not reach the js-dos player");
  assert(await page.locator("#launcher-error").isHidden(), "Local ZIP workbench reported a launcher error");

  await stopAndCloseRuntime();

  // Launch Steel Sky and prove WASM, relocatable HTTP-FS, and actual game data load.
  await page.locator('[data-game-id="beneath-a-steel-sky"]').click();
  await page.locator("#details-play-hosted").click();
  await waitForRequestPart("runtime/scummvm/scummvm.wasm", 45000);
  await waitForRequestPart("runtime/scummvm/data/index.json", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/sky-BASS-Floppy-1.3/index.json", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/sky-BASS-Floppy-1.3/sky.dsk", 45000);
  await page.waitForTimeout(1000);

  let frame = page.locator("#dos-player iframe.scummvm-frame");
  assert(await frame.count() === 1, "ScummVM player iframe was not created");
  assert((await frame.getAttribute("src"))?.endsWith("#sky"), "ScummVM did not receive the direct #sky target");

  await stopAndCloseRuntime();

  // Exercise the exact nested payload path that previously caught a false-positive intake configuration.
  await page.locator('[data-game-id="sfinx"]').click();
  await page.locator("#details-play-hosted").click();
  await waitForRequestPart("runtime/scummvm/data/games/sfinx-en-v1.1/sfinx-en-v1.1/index.json", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/sfinx-en-v1.1/sfinx-en-v1.1/vol.cat", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/sfinx-en-v1.1/sfinx-en-v1.1/vol.dat", 45000);
  await page.waitForTimeout(1000);

  frame = page.locator("#dos-player iframe.scummvm-frame");
  assert(await frame.count() === 1, "Sfinx ScummVM player iframe was not created");
  assert((await frame.getAttribute("src"))?.endsWith("#sfinx"), "ScummVM did not receive the direct #sfinx target");

  await stopAndCloseRuntime();

  // Nippon's freeware preservation release is a real multi-disk DOS payload. Require the
  // direct target and at least one original disk file to be fetched, not just the iframe.
  await page.locator('[data-game-id="nippon-safes"]').click();
  await page.locator("#details-play-hosted").click();
  await waitForRequestPart("runtime/scummvm/data/games/nippon-1.0/index.json", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/nippon-1.0/DISK1", 45000);
  await page.waitForTimeout(1000);

  frame = page.locator("#dos-player iframe.scummvm-frame");
  assert(await frame.count() === 1, "Nippon ScummVM player iframe was not created");
  assert((await frame.getAttribute("src"))?.endsWith("#nippon"), "ScummVM did not receive the direct #nippon target");

  await stopAndCloseRuntime();

  // Robin's Rescue is the first source-backed open-license intake. Require the user-facing
  // catalog launch to reach the Sludge target and request the exact audited SLG payload.
  await page.locator('[data-game-id="robins-rescue"]').click();
  await page.locator("#details-play-hosted").click();
  await waitForRequestPart("runtime/scummvm/data/games/robins-rescue/robinsrescue/index.json", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/robins-rescue/robinsrescue/robins_rescue.slg", 45000);
  await page.waitForTimeout(1000);

  frame = page.locator("#dos-player iframe.scummvm-frame");
  assert(await frame.count() === 1, "Robin's Rescue ScummVM player iframe was not created");
  assert(
    (await frame.getAttribute("src"))?.endsWith("#robinsrescue"),
    "ScummVM did not receive the direct #robinsrescue target"
  );

  await stopAndCloseRuntime();

  // The Secret of Tremendous Corporation is the second source-backed SLUDGE title. Its
  // nested Version 6 payload must be requested through the direct #tsotc launch path.
  await page.locator('[data-game-id="the-secret-of-tremendous-corporation"]').click();
  await page.locator("#details-play-hosted").click();
  await waitForRequestPart("runtime/scummvm/data/games/tremendous-corporation-v6/tsotc-v6/index.json", 45000);
  await waitForRequestPart("runtime/scummvm/data/games/tremendous-corporation-v6/tsotc-v6/gamedata.slg", 45000);
  await page.waitForTimeout(1000);

  frame = page.locator("#dos-player iframe.scummvm-frame");
  assert(await frame.count() === 1, "Tremendous Corporation ScummVM player iframe was not created");
  assert(
    (await frame.getAttribute("src"))?.endsWith("#tsotc"),
    "ScummVM did not receive the direct #tsotc target"
  );

  await stopAndCloseRuntime();

  const originRootDataRequests = requests.filter(url => {
    try {
      return new URL(url).pathname === "/data/index.json";
    } catch {
      return false;
    }
  });
  assert(
    originRootDataRequests.length === 0,
    `ScummVM escaped its relocatable runtime and requested origin-root /data/index.json: ${originRootDataRequests.join(", ")}`
  );

  const functionalCdns = requests.filter(url =>
    url.includes("v8.js-dos.com/latest") ||
    url.includes("cdn.jsdelivr.net/npm/jszip")
  );
  assert(functionalCdns.length === 0, `Functional runtime CDN request detected: ${functionalCdns.join(", ")}`);

  // Headless Chromium has no speech-synthesis voices; ScummVM reports that optional
  // accessibility limitation through stderr/console.error. Keep every other error strict.
  const fatalConsoleErrors = consoleErrors.filter(message =>
    !message.includes("No MIDI support in your browser") &&
    !message.includes("WARNING: No voice is available for language:")
  );

  assert(pageErrors.length === 0, `Page errors: ${pageErrors.join(" | ")}`);
  assert(fatalConsoleErrors.length === 0, `Console errors: ${fatalConsoleErrors.join(" | ")}`);

  console.log(JSON.stringify({
    gameCount: runtime.gameCount,
    hostedCount: runtime.hostedCount,
    localDosCount: runtime.localDosCount,
    requestsObserved: requests.length,
    jsdosLocalEmulatorRequests: requests.filter(url => url.includes("runtime/jsdos/emulators/")).length,
    scummvmWasmRequests: requests.filter(url => url.includes("runtime/scummvm/scummvm.wasm")).length,
    scummvmRelativeDataRequests: requests.filter(url => url.includes("runtime/scummvm/data/")).length,
    steelSkyPayloadRequests: requests.filter(url => url.includes("sky-BASS-Floppy-1.3/sky.dsk")).length,
    sfinxPayloadRequests: requests.filter(url => url.includes("sfinx-en-v1.1/sfinx-en-v1.1/vol.dat")).length,
    nipponPayloadRequests: requests.filter(url => url.includes("nippon-1.0/DISK1")).length,
    robinsRescuePayloadRequests: requests.filter(url => url.includes("robins-rescue/robinsrescue/robins_rescue.slg")).length,
    tremendousCorporationPayloadRequests: requests.filter(url => url.includes("tremendous-corporation-v6/tsotc-v6/gamedata.slg")).length,
    localWorkbenchZipDetected: true
  }, null, 2));
} finally {
  await browser.close();
}
