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
  window.addEventListener('blur', release);
  document.addEventListener('visibilitychange', () => {if(document.hidden) release();});
  document.getElementById('fullscreen').addEventListener('click', () => {
    document.getElementById('play-area').requestFullscreen?.(); game.contentWindow.focus();
  });
})();
