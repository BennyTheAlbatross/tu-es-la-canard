/* EXISTING GAME CONTROLS
   These buttons send the same input messages as before. The game iframe
   element remains in place when changing rooms. Clear held keys on exit
   so returning to the game cannot leave a movement button stuck. */
(() => {
  const game = document.getElementById('game');
  const held = new Set();
  const send = (actions = []) => game.contentWindow.postMessage({type:'canard-input',held:[...held],actions}, location.origin);
  const release = () => {
    held.clear(); send();
    document.querySelectorAll('.pressed').forEach(button => button.classList.remove('pressed'));
  };
  document.querySelectorAll('[data-key]').forEach(button => {
    button.addEventListener('pointerdown', event => {
      event.preventDefault(); button.setPointerCapture(event.pointerId);
      held.add(button.dataset.key); button.classList.add('pressed'); send([button.dataset.key]);
    });
    const up = () => {held.delete(button.dataset.key);button.classList.remove('pressed');send();};
    button.addEventListener('pointerup', up);
    button.addEventListener('pointercancel', up);
    button.addEventListener('lostpointercapture', up);
  });
  window.addEventListener('canard-room-change', release);
  window.addEventListener('blur', release);
  document.addEventListener('visibilitychange', () => {if(document.hidden) release();});
  const playArea = document.getElementById('play-area');
  const fullscreenButton = document.getElementById('fullscreen');
  fullscreenButton.addEventListener('click', async () => {
    if (document.fullscreenElement === playArea) {
      await document.exitFullscreen?.();
    } else {
      await playArea.requestFullscreen?.();
      game.contentWindow.focus();
    }
  });
  document.addEventListener('fullscreenchange', () => {
    const active = document.fullscreenElement === playArea;
    fullscreenButton.textContent = active ? 'Exit full screen' : 'Full screen';
    fullscreenButton.setAttribute('aria-pressed', String(active));
  });
})();
