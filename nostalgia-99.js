(() => {
  const site = document.querySelector('.classic-site');
  const utility = document.querySelector('.utility-strip');
  const ticker = document.querySelector('.ticker-bar');
  const main = document.querySelector('.classic-main');
  const footer = document.querySelector('.classic-footer');
  const games = Array.isArray(window.ABANDONWARE_GAMES) ? window.ABANDONWARE_GAMES : [];

  if (!site || !utility || !ticker || !main || !footer) return;
  if (document.querySelector('.n99-browser')) return;

  const hosted = games.filter(game => game.hostable && game.hostedUrl);
  const runtimeCount = new Set(hosted.map(game => game.runtimeType || 'jsdos')).size;

  const browser = document.createElement('section');
  browser.className = 'n99-browser';
  browser.setAttribute('aria-label', '1999 browser nostalgia frame');
  browser.innerHTML = `
    <div class="n99-titlebar">
      <span class="n99-titlebar-logo">A</span>
      <span class="n99-window-title">ABANDONWARE Navigator 4.0 — [ABANDONWARE NETWORK]</span>
      <span class="n99-window-controls" aria-hidden="true"><i>_</i><i>□</i><i>×</i></span>
    </div>
    <div class="n99-menubar" aria-hidden="true">
      <span>File</span><span>Edit</span><span>View</span><span>Go</span><span>Bookmarks</span><span>Help</span>
    </div>
    <div class="n99-toolbar">
      <button class="n99-tool" type="button" data-n99-home title="Home"><b>⌂</b><span>HOME</span></button>
      <button class="n99-tool" type="button" data-n99-games title="Game channels"><b>▶</b><span>GAMES</span></button>
      <button class="n99-tool" type="button" data-n99-search title="Find a game"><b>⌕</b><span>SEARCH</span></button>
      <div class="n99-location"><b>Location:</b><span class="n99-address">abw://network/games/home</span></div>
      <button class="n99-sfx" type="button" data-n99-sfx aria-pressed="false">SFX: OFF</button>
    </div>
  `;
  site.insertBefore(browser, utility);

  let guestId = 'GUEST_1999';
  try {
    guestId = localStorage.getItem('abw-n99-guest') || '';
    if (!guestId) {
      guestId = `GUEST_${String(Math.floor(1000 + Math.random() * 9000))}`;
      localStorage.setItem('abw-n99-guest', guestId);
    }
  } catch {
    guestId = 'GUEST_1999';
  }

  const sessionBar = document.createElement('div');
  sessionBar.className = 'n99-sessionbar';
  sessionBar.innerHTML = `
    <div class="n99-session-chip"><span class="lamp"></span><b>CONNECTED</b></div>
    <div class="n99-session-chip">HANDLE: <b>${guestId}</b> <span>(LOCAL)</span></div>
    <div class="n99-marquee" aria-label="Network bulletin">
      <div class="n99-marquee-track"><b>NETWORK BULLETIN:</b> ${hosted.length} classics are browser-ready // ${games.length} restoration records online // LOCAL DOS WORKBENCH READY // NO GAME-DATA UPLOADS // SOURCE + RIGHTS RECORDS AVAILABLE //</div>
    </div>
    <div class="n99-session-chip"><b>${runtimeCount}</b> ENGINES</div>
  `;
  ticker.insertAdjacentElement('afterend', sessionBar);

  const adDeck = document.createElement('section');
  adDeck.className = 'n99-ad-deck';
  adDeck.setAttribute('aria-label', 'Classic web promotion deck');
  adDeck.innerHTML = `
    <button class="n99-banner" type="button" data-n99-open-launcher aria-label="Open local game workbench">
      <span class="n99-banner-mark">A</span>
      <span class="n99-banner-copy"><small>ABANDONWARE GIZMO 4.0</small><strong>YOUR OLD GAME.<br>ONE CLICK AWAY.</strong><span>RUN A DOS COPY LOCALLY IN YOUR BROWSER</span></span>
      <span class="n99-banner-go">OPEN<br>NOW!</span>
    </button>
    <div class="n99-badges" aria-label="Archive capability badges">
      <span class="n99-badge"><b>1024 × 768</b>BEST VIEWED ANYWAY</span>
      <span class="n99-badge"><b>WASM</b>RUNTIME READY</span>
      <span class="n99-badge"><b>LOCAL</b>NO UPLOADS</span>
      <span class="n99-badge"><b>SOURCE</b>OPEN LEDGER</span>
    </div>
  `;
  main.insertBefore(adDeck, main.firstChild);

  const linkbar = document.createElement('nav');
  linkbar.className = 'n99-linkbar';
  linkbar.setAttribute('aria-label', 'Classic portal shortcuts');
  linkbar.innerHTML = `
    <a href="#featured">HOT GAMES</a>
    <a href="#archive">GAME DIRECTORY</a>
    <button type="button" data-n99-open-launcher>MY DOS GAMES</button>
    <a href="#principles">HELP DESK</a>
    <a href="https://github.com/Kodaxadev/Abandonware" target="_blank" rel="noreferrer">SOURCE CODE</a>
  `;
  adDeck.insertAdjacentElement('afterend', linkbar);

  const statusbar = document.createElement('div');
  statusbar.className = 'n99-statusbar';
  statusbar.innerHTML = `
    <span class="n99-status-cell">Done. <b>${games.length}</b> restoration records loaded.</span>
    <span class="n99-status-cell">${hosted.length} PLAYABLE / ${runtimeCount} ENGINES</span>
    <span class="n99-status-cell">INTERNET ZONE</span>
  `;
  footer.insertAdjacentElement('beforebegin', statusbar);

  function scrollToTarget(selector) {
    document.querySelector(selector)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function openLauncher() {
    const existingTrigger = document.querySelector('.classic-join[data-open-launcher], .classic-button[data-open-launcher]');
    existingTrigger?.click();
  }

  browser.querySelector('[data-n99-home]')?.addEventListener('click', () => scrollToTarget('#top'));
  browser.querySelector('[data-n99-games]')?.addEventListener('click', () => scrollToTarget('#archive'));
  browser.querySelector('[data-n99-search]')?.addEventListener('click', () => {
    scrollToTarget('#archive');
    setTimeout(() => document.getElementById('archive-search')?.focus(), 300);
  });
  adDeck.querySelector('[data-n99-open-launcher]')?.addEventListener('click', openLauncher);
  linkbar.querySelector('[data-n99-open-launcher]')?.addEventListener('click', openLauncher);

  let soundEnabled = false;
  let audioContext = null;
  const sfxButton = browser.querySelector('[data-n99-sfx]');

  function context() {
    if (!audioContext) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) audioContext = new AudioContext();
    }
    return audioContext;
  }

  function blip(frequency = 660, duration = 0.045, gainValue = 0.028) {
    if (!soundEnabled) return;
    const ctx = context();
    if (!ctx) return;
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);
    gain.gain.setValueAtTime(gainValue, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    oscillator.connect(gain).connect(ctx.destination);
    oscillator.start();
    oscillator.stop(ctx.currentTime + duration);
  }

  function connectChime() {
    if (!soundEnabled) return;
    [392, 523, 659, 784].forEach((freq, index) => {
      setTimeout(() => blip(freq, 0.06, 0.024), index * 65);
    });
  }

  sfxButton?.addEventListener('click', async () => {
    soundEnabled = !soundEnabled;
    if (soundEnabled) {
      const ctx = context();
      try { await ctx?.resume(); } catch {}
    }
    sfxButton.setAttribute('aria-pressed', String(soundEnabled));
    sfxButton.textContent = soundEnabled ? 'SFX: ON' : 'SFX: OFF';
    if (soundEnabled) connectChime();
  });

  site.addEventListener('click', event => {
    if (!soundEnabled) return;
    if (event.target.closest('a, button, [role="button"]')) blip(610, 0.035, 0.018);
  }, true);

  const flagLabels = ['HOT', 'NEW', 'TOP', 'NEW'];
  function decorateGameCards() {
    document.querySelectorAll('#game-grid [data-game-id]').forEach((card, index) => {
      if (card.querySelector('.n99-card-flag')) return;
      const game = games.find(item => item.id === card.dataset.gameId);
      if (!game) return;
      const flag = document.createElement('span');
      flag.className = `n99-card-flag${game.hostable && game.hostedUrl ? ' ready' : ''}`;
      flag.textContent = index < flagLabels.length ? flagLabels[index] : (game.hostable && game.hostedUrl ? 'PLAY' : 'INFO');
      card.appendChild(flag);
    });
  }

  decorateGameCards();
  const grid = document.getElementById('game-grid');
  if (grid) new MutationObserver(decorateGameCards).observe(grid, { childList: true });
})();
