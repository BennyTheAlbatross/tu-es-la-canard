/* ================================================================
   WEBSITE NAVIGATION

   Each tab's aria-controls points to its room's HTML id.
   The selected room is also reflected in the URL hash, so links such as
   index.html#music open that room directly. No routing library is used.
   ================================================================ */
(() => {
  const tabs = [...document.querySelectorAll('.tabs [role="tab"]')];
  const rooms = [...document.querySelectorAll('.room')];
  const game = document.getElementById('game');

  function showRoom(roomId) {
    const selected = tabs.find(tab => tab.getAttribute('aria-controls') === roomId);
    if (!selected) return;

    /* GAME LIFETIME
       Keeping the iframe element preserves the existing controls' reference.
       Setting its source to about:blank destroys the Python game and audio.
       Only load the game when entering its room; HOME loads no game runtime. */
    if (roomId === 'game-panel') {
      if (game.getAttribute('src') === 'about:blank') {
        game.src = game.dataset.gameSrc;
      }
    } else if (game.getAttribute('src') !== 'about:blank') {
      window.dispatchEvent(new Event('canard-room-change'));
      game.src = 'about:blank';
    }

    tabs.forEach(tab => {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    rooms.forEach(room => { room.hidden = room.id !== roomId; });
    // The song is not automatically started, paused or restarted by navigation.
    // Music behaviour beyond the normal HTML5 player needs Benny's decision.
  }

  /* BUTTON / KEYBOARD NAVIGATION
     Left/right cycle through tabs. Home/End choose the first/last tab.
     These keys apply only while a navigation button has keyboard focus;
     they do not intercept keys inside the game. */
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      const roomId = tab.getAttribute('aria-controls');
      history.replaceState(null, '', '#' + roomId);
      showRoom(roomId);
    });
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      tabs[next].focus();
      tabs[next].click();
    });
  });

  function openHash() {
    const requested = location.hash.slice(1);
    showRoom(rooms.some(room => room.id === requested) ? requested : 'home');
  }
  window.addEventListener('hashchange', openHash);
  openHash();

  /* FIXED HEADER / PHONE WIDTHS
     Measure actual wrapped header height rather than guessing a fixed pixel
     offset. This prevents the title/tabs covering content when fonts load,
     when a phone rotates or when the browser text size changes. */
  const header = document.getElementById('site-header');
  const updateHeaderHeight = () => {
    document.documentElement.style.setProperty('--header-height', header.offsetHeight + 'px');
  };
  new ResizeObserver(updateHeaderHeight).observe(header);
  updateHeaderHeight();
})();
