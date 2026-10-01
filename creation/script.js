(() => {
  const story = document.getElementById('story');
  const root = document.documentElement;
  const status = document.getElementById('touch-status');
  const dialog = document.getElementById('about-dialog');
  let scheduled = false;
  let connected = false;
  const clamp = value => Math.max(0, Math.min(1, value));

  function render() {
    const travel = story.offsetHeight - window.innerHeight;
    const raw = clamp(-story.getBoundingClientRect().top / Math.max(1, travel));
    // Hold the final touch for the last part of the scroll, without overshooting.
    const progress = clamp(raw / .86);
    const arrival = clamp((progress - .76) / .24);
    const width = document.querySelector('.artwork').getBoundingClientRect().width;
    // Reference fingertips: (292,289) and (427,249) on a 735×479 image.
    // Move both axes equally so the two tips meet exactly at (359.5,269).
    document.querySelector('.hand-left').style.transform = `translate(${progress * width * 67.5 / 735}px,${-progress * width * 20 / 735}px)`;
    document.querySelector('.hand-right').style.transform = `translate(${-progress * width * 67.5 / 735}px,${progress * width * 20 / 735}px)`;
    root.style.setProperty('--progress', progress.toFixed(5));
    root.style.setProperty('--arrival', arrival.toFixed(5));
    root.style.setProperty('--depart', (1 - arrival).toFixed(5));
    document.getElementById('progress-number').textContent = String(Math.round(progress * 100)).padStart(3, '0');
    const isConnected = progress >= .999;
    document.body.classList.toggle('connected', isConnected);
    document.getElementById('live-state').textContent = isConnected ? 'A CONNECTION MADE' : progress > .15 ? 'COMING CLOSER' : 'APART, FOR NOW';
    if (isConnected !== connected) {
      status.textContent = isConnected ? 'The fingertips have touched.' : 'The hands are moving apart.';
      connected = isConnected;
    }
    scheduled = false;
  }

  function schedule() {
    if (!scheduled) { scheduled = true; requestAnimationFrame(render); }
  }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  document.getElementById('replay').addEventListener('click', () => window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' }));
  document.getElementById('about-button').addEventListener('click', () => dialog.showModal());
  document.getElementById('close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
  render();
})();
