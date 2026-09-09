(() => {
  const games = Array.isArray(window.ABANDONWARE_GAMES) ? window.ABANDONWARE_GAMES : [];
  const byId = new Map(games.map(game => [game.id, game]));
  const grid = document.getElementById("game-grid");

  const style = document.createElement("style");
  style.textContent = `
    .archive-v2 .channel-summary {
      grid-column: 1;
      grid-row: 4;
      min-width: 0;
      margin: 8px 0 6px;
      color: #555867;
      font: 8px/1.4 Verdana, Tahoma, Arial, sans-serif;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
    }
    .archive-v2 .game-card:hover .channel-summary,
    .archive-v2 .game-card:focus .channel-summary { color: #424557; }
    .featured-game,
    .hero-network-foot a { cursor: pointer; }
    @media (max-width: 650px) {
      .archive-v2 .channel-summary {
        margin: 5px 0 4px;
        font-size: 7px;
        line-height: 1.3;
        -webkit-line-clamp: 1;
      }
    }
  `;
  document.head.append(style);

  function shortSummary(value, maxLength = 150) {
    const text = String(value || "").replace(/\s+/g, " ").trim();
    if (!text) return "Open the restoration record for compatibility, provenance and launch details.";

    const sentenceEnd = text.search(/[.!?](?:\s|$)/);
    const candidate = sentenceEnd >= 0 ? text.slice(0, sentenceEnd + 1) : text;
    if (candidate.length <= maxLength) return candidate;

    const clipped = candidate.slice(0, maxLength - 1).replace(/\s+\S*$/, "").trim();
    return `${clipped || candidate.slice(0, maxLength - 1)}…`;
  }

  function decorateCards() {
    if (!grid) return;

    grid.querySelectorAll("[data-game-id]").forEach(card => {
      if (card.querySelector(".channel-summary")) return;
      const game = byId.get(card.dataset.gameId);
      const body = card.querySelector(".game-card-body");
      const footer = card.querySelector(".game-card-footer");
      if (!game || !body || !footer) return;

      const summary = document.createElement("p");
      summary.className = "channel-summary";
      summary.textContent = shortSummary(game.summary);
      body.insertBefore(summary, footer);
    });
  }

  function openChannel(gameId) {
    const allFilter = document.querySelector('[data-filter="all"]');
    if (allFilter && !allFilter.classList.contains("active")) allFilter.click();

    requestAnimationFrame(() => {
      const card = document.querySelector(`[data-game-id="${CSS.escape(gameId)}"]`);
      if (!card) return;
      card.click();
    });
  }

  const featuredIds = ["xargon", "dreamweb", "robins-rescue"];
  document.querySelectorAll(".featured-game").forEach((link, index) => {
    const gameId = featuredIds[index];
    if (!gameId) return;
    link.dataset.featuredGame = gameId;
    link.addEventListener("click", event => {
      event.preventDefault();
      openChannel(gameId);
    });
  });

  const heroChannel = document.querySelector(".hero-network-foot a");
  if (heroChannel) {
    heroChannel.dataset.featuredGame = "beneath-a-steel-sky";
    heroChannel.addEventListener("click", event => {
      event.preventDefault();
      openChannel("beneath-a-steel-sky");
    });
  }

  decorateCards();

  if (grid) {
    const observer = new MutationObserver(() => decorateCards());
    observer.observe(grid, { childList: true });
  }
})();
