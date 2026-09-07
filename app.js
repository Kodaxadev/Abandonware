const restorationTargets = [
  {
    id: "doom",
    title: "DOOM",
    year: "1993",
    studio: "id Software",
    platform: "DOS",
    filter: "dos",
    runtime: "DOSBox",
    status: "LOCAL FILES",
    statusClass: "local",
    cover: "cover-doom",
    summary: "The browser runtime is capable of running the original DOS release from a user-supplied copy. No WADs or commercial game data are hosted by this project.",
    rights: "Game data not distributed",
    compatibility: "Profile pending verification"
  },
  {
    id: "keen4",
    title: "Commander Keen 4",
    year: "1991",
    studio: "id Software / Apogee",
    platform: "DOS",
    filter: "dos",
    runtime: "DOSBox",
    status: "LOCAL FILES",
    statusClass: "local",
    cover: "cover-keen",
    summary: "A target for a tested keyboard, sound, scaling, and save profile. Use your own legally obtained DOS files through the local workbench.",
    rights: "Game data not distributed",
    compatibility: "Profile pending verification"
  },
  {
    id: "jazz",
    title: "Jazz Jackrabbit",
    year: "1994",
    studio: "Epic MegaGames",
    platform: "DOS",
    filter: "dos",
    runtime: "DOSBox",
    status: "LOCAL FILES",
    statusClass: "local",
    cover: "cover-jazz",
    summary: "Fast DOS-era platforming is a useful stress test for timing, audio latency, keyboard handling, and pixel-perfect scaling in the browser runtime.",
    rights: "Game data not distributed",
    compatibility: "Profile pending verification"
  },
  {
    id: "simcity2000",
    title: "SimCity 2000",
    year: "1993",
    studio: "Maxis",
    platform: "DOS",
    filter: "dos",
    runtime: "DOSBox",
    status: "LOCAL FILES",
    statusClass: "local",
    cover: "cover-simcity",
    summary: "A mouse-heavy restoration target that will help harden pointer capture, save persistence, aspect handling, and longer play sessions.",
    rights: "Game data not distributed",
    compatibility: "Profile pending verification"
  },
  {
    id: "monkey",
    title: "The Secret of Monkey Island",
    year: "1990",
    studio: "Lucasfilm Games",
    platform: "SCUMMVM",
    filter: "scummvm",
    runtime: "ScummVM",
    status: "ENGINE PLANNED",
    statusClass: "planned",
    cover: "cover-monkey",
    summary: "ScummVM is the planned second execution layer for classic adventures. The project will require user-supplied game data unless a title has explicit redistribution permission.",
    rights: "Game data not distributed",
    compatibility: "ScummVM web layer planned"
  },
  {
    id: "diablo",
    title: "Diablo",
    year: "1996",
    studio: "Blizzard North",
    platform: "WIN9X",
    filter: "win9x",
    runtime: "DOSBox-X",
    status: "ENGINE PLANNED",
    statusClass: "planned",
    cover: "cover-diablo",
    summary: "A later Windows-era restoration target. js-dos can support Windows 9x through DOSBox-X, but this project will not claim one-click compatibility until a reproducible local-file profile is tested.",
    rights: "Game data not distributed",
    compatibility: "Win9x profile planned"
  }
];

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
    <article class="game-card" role="button" tabindex="0" data-game-id="${game.id}" aria-label="View ${game.title} restoration record">
      <div class="game-cover">
        <div class="game-cover-inner ${game.cover}">
          <span class="cover-number">REC ${String(index + 1).padStart(2, "0")}</span>
          <span class="cover-title">${game.title}</span>
        </div>
      </div>
      <div class="game-card-body">
        <div class="game-meta"><span>${game.year}</span><span>${game.platform}</span></div>
        <h3>${game.title}</h3>
        <div class="studio">${game.studio}</div>
        <div class="game-card-footer">
          <span class="rights-badge ${game.statusClass}">${game.status}</span>
          <span class="card-arrow">↗</span>
        </div>
      </div>
    </article>
  `).join("");

  emptyState.hidden = visible.length !== 0;
  document.getElementById("status-catalog-count").textContent = String(restorationTargets.length).padStart(2, "0");
}

function openDetails(gameId) {
  const game = restorationTargets.find((item) => item.id === gameId);
  if (!game) return;

  const canUseWorkbench = game.filter === "dos";
  detailsContent.innerHTML = `
    <div class="details-hero ${game.cover}">
      <div class="eyebrow">RESTORATION RECORD / ${game.year}</div>
      <h2>${game.title}</h2>
    </div>
    <div class="details-body">
      <div class="details-ledger">
        <div><span>ORIGINAL PLATFORM</span><b>${game.platform}</b></div>
        <div><span>EXECUTION PATH</span><b>${game.runtime}</b></div>
        <div><span>RIGHTS MODE</span><b>${game.rights}</b></div>
      </div>
      <p>${game.summary}</p>
      <p><strong>Current compatibility record:</strong> ${game.compatibility}. A game is not promoted to browser-ready until its boot path, input, audio, save behavior, and rights basis have been checked.</p>
      ${canUseWorkbench
        ? `<button class="button button-primary" id="details-open-workbench">RUN MY LOCAL COPY <span>↗</span></button>`
        : `<button class="button" disabled aria-disabled="true">${game.runtime.toUpperCase()} PROFILE NOT YET ENABLED</button>`}
    </div>
  `;
  detailsModal.showModal();

  const workbenchButton = document.getElementById("details-open-workbench");
  if (workbenchButton) {
    workbenchButton.addEventListener("click", () => {
      detailsModal.close();
      openLauncher();
    });
  }
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

// ----- Local restoration workbench -----
const launcherModal = document.getElementById("launcher-modal");
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
  dos: null
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

function openLauncher() {
  if (!launcherModal.open) launcherModal.showModal();
}

async function disposeEmulator() {
  if (launcherState.dos) {
    try { await launcherState.dos.stop(); } catch (error) { console.warn("Emulator stop failed", error); }
    launcherState.dos = null;
  }
  if (launcherState.objectUrl) {
    URL.revokeObjectURL(launcherState.objectUrl);
    launcherState.objectUrl = null;
  }
  dosPlayer.innerHTML = "";
}

async function closeLauncher() {
  await disposeEmulator();
  launcherModal.close();
  showLauncherStep(launcherState.file ? 2 : 1);
}

document.querySelectorAll("[data-open-launcher]").forEach((button) => button.addEventListener("click", openLauncher));
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
    bootTarget.innerHTML = targets.map((target, index) => `<option value="${escapeAttribute(target)}">${index === 0 ? "★ " : ""}${escapeHtml(target)}</option>`).join("");
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
  const bundle = await zip.generateAsync({ type: "blob", compression: "DEFLATE", compressionOptions: { level: 6 } });
  return URL.createObjectURL(bundle);
}

startButton.addEventListener("click", async () => {
  if (!rightsConfirm.checked || !launcherState.file) return;
  startButton.disabled = true;
  setError();
  emulatorStatus.textContent = "PREPARING BUNDLE";

  try {
    await disposeEmulator();
    launcherState.objectUrl = await makePlayableUrl();
    showLauncherStep(3);
    emulatorStatus.textContent = "LOADING RUNTIME";

    launcherState.dos = Dos(dosPlayer, {
      url: launcherState.objectUrl,
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
        if (event === "ci-ready") emulatorStatus.textContent = "RUNNING";
      }
    });
    launcherState.dos.setNoCloud(true);
  } catch (error) {
    console.error(error);
    setError(`Could not start this game: ${error?.message || "unknown emulator error"}`);
    showLauncherStep(2);
    startButton.disabled = false;
  }
});

document.getElementById("emulator-fullscreen").addEventListener("click", () => {
  launcherState.dos?.setFullScreen(true);
});

document.getElementById("emulator-stop").addEventListener("click", async () => {
  emulatorStatus.textContent = "STOPPING";
  await disposeEmulator();
  emulatorStatus.textContent = "STOPPED";
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
