/* Same-origin messages only. This supplies touch input to the existing game. */
(() => {
  const allowed = new Set(['up','down','left','right','enter','escape','torch','music','walls']);
  let held = [], actions = [];
  window.addEventListener('message', event => {
    if (event.origin !== location.origin || event.source !== parent || event.data?.type !== 'canard-input') return;
    held = (event.data.held || []).filter(key => allowed.has(key));
    actions.push(...(event.data.actions || []).filter(key => allowed.has(key)));
  });
  window.canardTakeInput = () => {
    const result = JSON.stringify({held, actions});
    actions = [];
    return result;
  };
})();
