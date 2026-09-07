const restorationTargets = Array.isArray(window.ABANDONWARE_GAMES)
  ? window.ABANDONWARE_GAMES
  : [];

const grid = document.getElementById("game-grid");
const emptyState = document.getElementById("empty-state");
const searchInput = document.getElementById("archive-search");
const filterButtons = [...document.querySelectorAll("[data-filter]")];
const detailsModal = document.getElementById("details-modal");
const detailsContent = document.getElementById("details-content");
let activeFilter = "all";

function renderGames() {
  const query = searchInput.value.trim().toLowerCase();
  const visible = restorationTargets.filter((game) => {
    const inFilter = activeFilter === "all" || game.filter === activeFilter;
    const haystack = `${game.title} ${game.year} ${game.studio} ${game.platform}`.toLowerCase();
    return inFilter && (!query || haystack.includes(query));
  });

  grid.innerHTML = visible.map((game, index) => `
    <article class="game-card" role="button" tabindex="0" data-game-id="${escapeAttribute(game.id)}" aria-label="View ${escapeAttribute(game.title)} restoration record">
      <div class="game-cover">
        <div class="game-cover-inner ${game.cover}">
          <span class="cover-number">REC ${String(index + 1).padStart(2, "0")}</span>
          ${game.hostedUrl ? `<span class="cover-live">PLAYABLE</span>` : ""}
          <span class="cover-title">${escapeHtml(game.title)}</span>
        </div>
      </div>
      <div class="game-card-body">
        <div class="game-meta"><span>${escapeHtml(game.year)}</span><span>${escapeHtml(game.platform)}</span></div>
        <h3>${escapeHtml(game.title)}</h3>
        <div class="studio">${escapeHtml(game.studio)}</div>
        <div class="game-card-footer">
          <span class="rights-badge ${game.statusClass}">${escapeHtml(game.status)}</span>
          <span class="card-arrow">↗</span>
        </div>
      </div>
    </article>
  `).join("");

  emptyState.hidden = visible.length !== 0;
  document.getElementById("status-catalog-count").textContent = String(restorationTargets.length).padStart(2, "0");

  const hosted = restorationTargets.filter((game) => game.hostedUrl && game.hostable);
  const hostedCounter = document.getElementById("status-hosted-count") || document.querySelector(".status-strip div:nth-child(3) strong");
  if (hostedCounter) hostedCounter.textContent = String(hosted.length).padStart(2, "0");

  const engineCounter = document.getElementById("status-engine-count");
  if (engineCounter) {
    const engines = new Set(hosted.map((game) => game.runtimeType || "jsdos"));
    engineCounter.textContent = String(engines.size).padStart(2, "0");
  }
}

function openDetails(gameId) {
  const game = restorationTargets.find((item) => item.id === gameId);
  if (!game) return;

  const canUseWorkbench = game.filter === "dos";
  const action = game.hostedUrl
    ? `<button class="button button-primary" id="details-play-hosted">PLAY IN BROWSER <span>↗</span></button>`
    : canUseWorkbench
      ? `<button class="button button-primary" id="details-open-workbench">RUN MY LOCAL COPY <span>↗</span></button>`
      : `<button class="button" disabled aria-disabled="true">${escapeHtml(game.runtime.toUpperCase())} PROFILE NOT YET ENABLED</button>`;

  const provenance = game.sourcePage
    ? `<div class="record-links">
        <a href="${escapeAttribute(game.sourcePage)}" target="_blank" rel="noreferrer">UPSTREAM RECORD ↗</a>
        ${game.rightsRecord ? `<a href="${escapeAttribute(game.rightsRecord)}" target="_blank" rel="noreferrer">RIGHTS RECORD ↗</a>` : ""}
      </div>`
    : "";

  detailsContent.innerHTML = `
    <div class="details-hero ${game.cover}">
      <div class="eyebrow">RESTORATION RECORD / ${escapeHtml(game.year)}</div>
      <h2>${escapeHtml(game.title)}</h2>
    </div>
    <div class="details-body">
      <div class="details-ledger">
        <div><span>ORIGINAL PLATFORM</span><b>${escapeHtml(game.platform)}</b></div>
        <div><span>EXECUTION PATH</span><b>${escapeHtml(game.runtime)}</b></div>
        <div><span>RIGHTS MODE</span><b>${escapeHtml(game.rights)}</b></div>
      </div>
      <p>${escapeHtml(game.summary)}</p>
      <p><strong>Current compatibility record:</strong> ${escapeHtml(game.compatibility)}. A game is only promoted to browser-ready after its boot path, execution package, and rights basis have been pinned.</p>
      ${provenance}
      ${action}
    </div>
  `;
  detailsModal.showModal();

  document.getElementById("details-play-hosted")?.addEventListener("click", () => {
    detailsModal.close();
    startHostedGame(game);
  });

  document.getElementById("details-open-workbench")?.addEventListener("click", () => {
    detailsModal.close();
    openLauncher();
  });
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((candidate) => candidate.classList.toggle("active", candidate === button));
    renderGames();
  });
});

searchInput.addEventListener("input", renderGames);

grid.addEventListener("click", (event) => {
  const card = event.target.closest("[data-game-id]");
  if (card) openDetails(card.dataset.gameId);
});

grid.addEventListener("keydown", (event) => {
  if (event.key !== "Enter" && event.key !== " ") return;
  const card = event.target.closest("[data-game-id]");
  if (!card) return;
  event.preventDefault();
  openDetails(card.dataset.gameId);
});

document.querySelector("[data-close-details]").addEventListener("click", () => detailsModal.close());
detailsModal.addEventListener("click", (event) => {
  if (event.target === detailsModal) detailsModal.close();
});

// ----- Browser/local restoration workbench -----
const launcherModal = document.getElementById("launcher-modal");
const launcherTitle = document.getElementById("launcher-title") || document.querySelector(".modal-header h2");
const fileInput = document.getElementById("game-file");
const dropZone = document.getElementById("drop-zone");
const selectedFileName = document.getElementById("selected-file-name");
const targetPickerWrap = document.getElementById("target-picker-wrap");
const bootTarget = document.getElementById("boot-target");
const rightsConfirm = document.getElementById("rights-confirm");
const startButton = document.getElementById("start-emulation");
const launcherError = document.getElementById("launcher-error");
const dosPlayer = document.getElementById("dos-player");
const emulatorStatus = document.getElementById("emulator-status");

const launcherState = {
  file: null,
  type: null,
  zip: null,
  targets: [],
  objectUrl: null,
  dos: null,
  frame: null,
  mode: "local",
  hostedGame: null
};

function setError(message = "") {
  launcherError.textContent = message;
  launcherError.hidden = !message;
}

function showLauncherStep(stepNumber) {
  [1, 2, 3].forEach((step) => {
    document.getElementById(`launcher-step-${step}`).hidden = step !== stepNumber;
    const marker = document.querySelector(`[data-step-marker="${step}"]`);
    marker?.classList.toggle("active", step === stepNumber);
    marker?.classList.toggle("done", step < stepNumber);
  });
}

function openLauncher(title = "Restoration Workbench") {
  launcherTitle.textContent = title;
  if (!launcherModal.open) launcherModal.showModal();
}

async function disposeEmulator() {
  if (launcherState.dos) {
    try {
      await launcherState.dos.stop();
    } catch (error) {
      console.warn("Emulator stop failed", error);
    }
    launcherState.dos = null;
  }

  if (launcherState.frame) {
    launcherState.frame.src = "about:blank";
    launcherState.frame.remove();
    launcherState.frame = null;
  }

  if (launcherState.objectUrl) {
    URL.revokeObjectURL(launcherState.objectUrl);
    launcherState.objectUrl = null;
  }

  dosPlayer.innerHTML = "";
  dosPlayer.classList.remove("scummvm-player");
}

async function closeLauncher() {
  await disposeEmulator();
  launcherModal.close();
  launcherState.mode = "local";
  launcherState.hostedGame = null;
  launcherTitle.textContent = "Restoration Workbench";
  showLauncherStep(launcherState.file ? 2 : 1);
}

document.querySelectorAll("[data-open-launcher]").forEach((button) => {
  button.addEventListener("click", () => openLauncher());
});

document.querySelector("[data-close-launcher]").addEventListener("click", closeLauncher);
launcherModal.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeLauncher();
});
launcherModal.addEventListener("click", (event) => {
  if (event.target === launcherModal) closeLauncher();
});

function targetScore(path) {
  const name = path.split("/").pop().toLowerCase();
  let score = 0;
  if (/^(game|play|start|run|launch)\.(exe|com|bat)$/.test(name)) score += 100;
  if (/\.exe$/.test(name)) score += 25;
  if (/\.com$/.test(name)) score += 20;
  if (/\.bat$/.test(name)) score += 15;
  if (/(setup|install|uninst|uninstall|config|sound|setsound|readme|help|update|patch)/.test(name)) score -= 80;
  score -= path.split("/").length * 2;
  return score;
}

async function inspectSelectedFile(file) {
  setError();
  launcherState.mode = "local";
  launcherState.hostedGame = null;
  launcherTitle.textContent = "Restoration Workbench";

  const lowerName = file.name.toLowerCase();
  if (!lowerName.endsWith(".jsdos") && !lowerName.endsWith(".zip")) {
    setError("Unsupported file. Choose a .jsdos bundle or a .zip containing a DOS game.");
    return;
  }

  if (file.size > 300 * 1024 * 1024) {
    setError("This archive is over 300 MB. Large games may exceed browser memory; a future sockdrive profile will handle large installations better.");
    return;
  }

  launcherState.file = file;
  launcherState.type = lowerName.endsWith(".jsdos") ? "jsdos" : "zip";
  launcherState.zip = null;
  launcherState.targets = [];
  selectedFileName.textContent = `${file.name}  ·  ${formatBytes(file.size)}`;
  rightsConfirm.checked = false;
  startButton.disabled = true;

  if (launcherState.type === "jsdos") {
    targetPickerWrap.hidden = true;
    bootTarget.innerHTML = `<option value="">Use bundle configuration</option>`;
    showLauncherStep(2);
    return;
  }

  try {
    const zip = await JSZip.loadAsync(file);
    const targets = Object.values(zip.files)
      .filter((entry) => !entry.dir && !entry.name.startsWith("__MACOSX/") && /\.(exe|com|bat)$/i.test(entry.name))
      .map((entry) => entry.name)
      .sort((a, b) => targetScore(b) - targetScore(a) || a.localeCompare(b));

    if (!targets.length) {
      launcherState.file = null;
      setError("No .EXE, .COM, or .BAT launch target was found in that ZIP. A prepared .jsdos bundle may still work for unusual disk layouts.");
      showLauncherStep(1);
      return;
    }

    launcherState.zip = zip;
    launcherState.targets = targets;
    bootTarget.innerHTML = targets
      .map((target, index) => `<option value="${escapeAttribute(target)}">${index === 0 ? "★ " : ""}${escapeHtml(target)}</option>`)
      .join("");
    targetPickerWrap.hidden = false;
    showLauncherStep(2);
  } catch (error) {
    console.error(error);
    launcherState.file = null;
    setError("The ZIP could not be read. It may be damaged, encrypted, or use an unsupported archive format.");
    showLauncherStep(1);
  }
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (file) inspectSelectedFile(file);
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");
  const file = event.dataTransfer?.files?.[0];
  if (file) inspectSelectedFile(file);
});

document.getElementById("choose-another").addEventListener("click", () => {
  launcherState.file = null;
  launcherState.type = null;
  launcherState.zip = null;
  launcherState.targets = [];
  fileInput.value = "";
  rightsConfirm.checked = false;
  startButton.disabled = true;
  setError();
  showLauncherStep(1);
});

rightsConfirm.addEventListener("change", () => {
  startButton.disabled = !rightsConfirm.checked || !launcherState.file;
});

function createDosboxConfig(target) {
  const normalized = target.replaceAll("\\", "/");
  const pieces = normalized.split("/");
  const executable = pieces.pop();
  const directory = pieces.join("\\");
  const cdLine = directory ? `cd "\\${directory}"` : "cd \\";
  return `[sdl]\nautolock=true\n\n[dosbox]\nmachine=svga_s3\nmemsize=32\n\n[cpu]\ncore=auto\ncputype=auto\ncycles=auto\n\n[mixer]\nrate=44100\nblocksize=1024\nprebuffer=25\n\n[sblaster]\nsbtype=sb16\n\n[autoexec]\n@echo off\nmount c .\nc:\n${cdLine}\n"${executable}"\n`;
}

async function makePlayableUrl() {
  if (launcherState.type === "jsdos") {
    return URL.createObjectURL(launcherState.file);
  }

  const target = bootTarget.value;
  if (!target) throw new Error("Choose a boot target.");

  const zip = launcherState.zip;
  zip.file(".jsdos/dosbox.conf", createDosboxConfig(target));
  zip.file(".jsdos/jsdos.json", JSON.stringify({ version: 1 }, null, 2));
  const bundle = await zip.generateAsync({
    type: "blob",
    compression: "DEFLATE",
    compressionOptions: { level: 6 }
  });
  return URL.createObjectURL(bundle);
}

function launchDosUrl(url) {
  dosPlayer.classList.remove("scummvm-player");
  launcherState.dos = Dos(dosPlayer, {
    url,
    theme: "dark",
    backend: "dosbox",
    backendLocked: true,
    autoStart: true,
    autoSave: true,
    workerThread: true,
    imageRendering: "pixelated",
    renderAspect: "Fit",
    mouseCapture: false,
    thinSidebar: true,
    fsChanges: { local: true },
    onEvent: (event) => {
      if (event === "emu-ready") emulatorStatus.textContent = "RUNTIME READY";
      if (event === "bnd-play") emulatorStatus.textContent = "STARTING";
      if (event === "ci-ready") emulatorStatus.textContent = "RUNNING / DOSBOX";
    }
  });
  launcherState.dos.setNoCloud(true);
}

function launchScummVmUrl(url, game) {
  dosPlayer.classList.add("scummvm-player");
  const frame = document.createElement("iframe");
  frame.className = "scummvm-frame";
  frame.title = `${game.title} — ScummVM browser runtime`;
  frame.src = url;
  frame.loading = "eager";
  frame.allow = "autoplay; fullscreen";
  frame.setAttribute("allowfullscreen", "");
  frame.addEventListener("load", () => {
    emulatorStatus.textContent = "RUNNING / SCUMMVM";
    frame.focus();
  }, { once: true });
  launcherState.frame = frame;
  dosPlayer.replaceChildren(frame);
}

async function verifyHostedArtifact(url) {
  const head = await fetch(url, { method: "HEAD", cache: "no-store" });
  if (head.ok) return;

  if (head.status === 405 || head.status === 501) {
    const probe = await fetch(url, {
      method: "GET",
      cache: "no-store",
      headers: { Range: "bytes=0-0" }
    });
    if (probe.ok || probe.status === 206) return;
  }

  throw new Error(`The audited browser artifact is unavailable on this deployment (${head.status}).`);
}

async function startHostedGame(game) {
  await disposeEmulator();
  setError();
  launcherState.mode = "hosted";
  launcherState.hostedGame = game;
  openLauncher(game.title);
  showLauncherStep(3);
  emulatorStatus.textContent = `VERIFYING ${game.title.toUpperCase()}`;

  try {
    await verifyHostedArtifact(game.hostedUrl);

    if (game.runtimeType === "scummvm") {
      emulatorStatus.textContent = "LOADING SCUMMVM WEB";
      launchScummVmUrl(game.hostedUrl, game);
    } else {
      emulatorStatus.textContent = "LOADING AUDITED JSDOS BUNDLE";
      launchDosUrl(game.hostedUrl);
    }
  } catch (error) {
    console.error(error);
    emulatorStatus.textContent = "ARTIFACT UNAVAILABLE";
    dosPlayer.innerHTML = `
      <div class="runtime-error">
        <b>RESTORATION ARTIFACT UNAVAILABLE</b>
        <p>${escapeHtml(error?.message || "The browser runtime could not be loaded.")}</p>
        <small>The rights/source record remains pinned; the automated materialization gate must succeed before this title can run here.</small>
      </div>
    `;
  }
}

startButton.addEventListener("click", async () => {
  if (!rightsConfirm.checked || !launcherState.file) return;
  startButton.disabled = true;
  setError();
  emulatorStatus.textContent = "PREPARING BUNDLE";

  try {
    await disposeEmulator();
    launcherState.mode = "local";
    launcherState.objectUrl = await makePlayableUrl();
    showLauncherStep(3);
    emulatorStatus.textContent = "LOADING RUNTIME";
    launchDosUrl(launcherState.objectUrl);
  } catch (error) {
    console.error(error);
    setError(`Could not start this game: ${error?.message || "unknown emulator error"}`);
    showLauncherStep(2);
    startButton.disabled = false;
  }
});

document.getElementById("emulator-fullscreen").addEventListener("click", async () => {
  if (launcherState.dos) {
    launcherState.dos.setFullScreen(true);
    return;
  }

  try {
    await dosPlayer.requestFullscreen?.();
  } catch (error) {
    console.warn("Fullscreen request failed", error);
  }
});

document.getElementById("emulator-stop").addEventListener("click", async () => {
  emulatorStatus.textContent = "STOPPING";
  const wasHosted = launcherState.mode === "hosted";
  await disposeEmulator();
  emulatorStatus.textContent = "STOPPED";

  if (wasHosted) {
    launcherState.mode = "local";
    launcherState.hostedGame = null;
    launcherTitle.textContent = "Restoration Workbench";
    showLauncherStep(1);
    return;
  }

  startButton.disabled = !rightsConfirm.checked;
  showLauncherStep(2);
});

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}

renderGames();
