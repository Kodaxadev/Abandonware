(() => {
  const games = Array.isArray(window.ABANDONWARE_GAMES) ? window.ABANDONWARE_GAMES : [];
  const hosted = games.filter(game => game.hostable && game.hostedUrl);
  const runtimeCount = new Set(hosted.map(game => game.runtimeType || 'jsdos')).size;
  const heroCopy = document.querySelector('.hero-panel .welcome-copy');
  if (!heroCopy || document.querySelector('.n99-home-bulletin')) return;

  const kicker = heroCopy.querySelector('.welcome-kicker');
  const heading = heroCopy.querySelector('h1');
  const lead = heroCopy.querySelector(':scope > p');

  if (kicker) kicker.textContent = 'WELCOME, GUEST // CLASSIC PC GAMING SERVICE';
  if (heading) heading.innerHTML = 'WELCOME TO THE<br>ABANDONWARE NETWORK.';
  if (lead) {
    lead.textContent = 'Pick a browser-ready game channel, jump into the archive lobby, or bring your own DOS copy. The old PC is waiting behind the next click.';
  }

  const bulletin = document.createElement('section');
  bulletin.className = 'n99-home-bulletin';
  bulletin.setAttribute('aria-label', 'Today on the Abandonware network');
  bulletin.innerHTML = `
    <div class="n99-home-bulletin-head"><b>TODAY ON THE NETWORK</b><span>LIVE ARCHIVE INDEX</span></div>
    <div class="n99-home-bulletin-list">
      <button type="button" data-n99-home-target="#n99-lobby">${hosted.length} browser-ready game rooms are open</button>
      <button type="button" data-n99-home-target="#n99-lobby">Enter the Archive Lobby / Quick Join</button>
      <button type="button" data-n99-home-target="#workbench">Local DOS Workbench — files stay on your machine</button>
      <button type="button" data-n99-home-target="#principles">Rights ledger + preservation policy</button>
    </div>
  `;

  if (lead) lead.insertAdjacentElement('afterend', bulletin);
  else heroCopy.prepend(bulletin);

  bulletin.querySelectorAll('[data-n99-home-target]').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelector(button.dataset.n99HomeTarget)?.scrollIntoView({ block: 'start' });
    });
  });

  let localVisits = 1;
  try {
    const current = Number.parseInt(localStorage.getItem('abw-n99-local-visits') || '0', 10);
    localVisits = Number.isFinite(current) ? current + 1 : 1;
    localStorage.setItem('abw-n99-local-visits', String(localVisits));
  } catch {
    localVisits = 1;
  }

  const statusbar = document.querySelector('.n99-statusbar');
  if (statusbar) {
    const counter = document.createElement('span');
    counter.className = 'n99-local-counter';
    counter.title = 'This counter is stored only in this browser profile. It is not a global visitor count.';
    counter.innerHTML = `LOCAL VISITS <b>${String(localVisits).padStart(6, '0')}</b>`;
    statusbar.appendChild(counter);
  }

  const networkLine = document.querySelector('.n99-lobby-log');
  if (networkLine) {
    const p = document.createElement('p');
    p.innerHTML = `<b>*** SERVICE:</b> ${runtimeCount} browser engine${runtimeCount === 1 ? '' : 's'} online // choose a room and hit JOIN`;
    networkLine.appendChild(p);
  }
})();
