// Controles de vídeo compartidos: reproducir / pausa, barra de progreso con salto y sonido.
// Solo suena un vídeo a la vez; al activar el sonido el vídeo vuelve al principio
// para que el diseño sonoro se oiga sincronizado.

const ICONS = {
  play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/></svg>',
  pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5.5h3.6v13H7zM13.4 5.5H17v13h-3.6z" fill="currentColor"/></svg>',
  soundOff: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 9.3h3.4l4.6-4v13.4l-4.6-4H3.5z" fill="currentColor"/><path d="M15.5 9.5l5 5M20.5 9.5l-5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  soundOn: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 9.3h3.4l4.6-4v13.4l-4.6-4H3.5z" fill="currentColor"/><path d="M15 9a4.2 4.2 0 0 1 0 6M17.8 6.3a8 8 0 0 1 0 11.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
};
const clamp01 = (x) => Math.min(1, Math.max(0, x));

export function ensureLoaded(v) {
  if (v.dataset.loaded || !v.dataset.src) return;
  const webm = v.dataset.srcWebm;
  v.src = webm && v.canPlayType('video/webm; codecs="vp9, opus"') ? webm : v.dataset.src;
  v.dataset.loaded = '1';
}

export function muteOthers(except) {
  document.querySelectorAll('video').forEach((o) => { if (o !== except) o.muted = true; });
}

export function setupVideo(v) {
  if (v.closest('.vwrap')) return v.closest('.vwrap');
  const wrap = document.createElement('div');
  wrap.className = 'vwrap';
  v.parentNode.insertBefore(wrap, v);
  wrap.appendChild(v);
  const tag = v.closest('figure')?.querySelector(':scope > .tag');
  if (tag) wrap.appendChild(tag);
  wrap.insertAdjacentHTML('beforeend', `
    <div class="vctl">
      <button class="vbtn vplay" type="button" aria-label="Play">${ICONS.play}${ICONS.pause}</button>
      <div class="vbar" role="slider" aria-label="Progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" tabindex="0"><i></i></div>
      <button class="vbtn vsound" type="button" aria-label="Sound on" aria-pressed="false">${ICONS.soundOff}${ICONS.soundOn}</button>
    </div>`);
  const btnPlay = wrap.querySelector('.vplay');
  const btnSound = wrap.querySelector('.vsound');
  const bar = wrap.querySelector('.vbar');
  const fill = bar.firstElementChild;

  const sync = () => {
    wrap.dataset.state = v.paused ? 'paused' : 'playing';
    wrap.dataset.sound = v.muted ? 'off' : 'on';
    btnPlay.setAttribute('aria-label', v.paused ? 'Play' : 'Pause');
    btnSound.setAttribute('aria-label', v.muted ? 'Sound on' : 'Sound off');
    btnSound.setAttribute('aria-pressed', v.muted ? 'false' : 'true');
  };
  const progress = () => {
    const p = v.duration ? v.currentTime / v.duration : 0;
    fill.style.transform = `scaleX(${p})`;
    bar.setAttribute('aria-valuenow', String(Math.round(p * 100)));
  };
  const togglePlay = () => {
    ensureLoaded(v);
    if (v.paused) { delete v.dataset.userPaused; v.play().catch(() => {}); }
    else { v.dataset.userPaused = '1'; v.pause(); }
  };
  v.addEventListener('play', sync);
  v.addEventListener('pause', sync);
  v.addEventListener('volumechange', sync);
  v.addEventListener('timeupdate', progress);
  // la forma del reproductor sigue al vídeo real (vertical, 16:9, panorámico), sin recortar
  v.addEventListener('loadedmetadata', () => {
    const fig = v.closest('.d-piece, .d-film, .lb-video');
    if (fig && v.videoWidth && v.videoHeight) fig.style.setProperty('--ar', (v.videoWidth / v.videoHeight).toFixed(4));
  });
  v.addEventListener('click', togglePlay);
  btnPlay.addEventListener('click', togglePlay);
  btnSound.addEventListener('click', () => {
    ensureLoaded(v);
    if (v.muted) {
      muteOthers(v);
      v.muted = false;
      v.volume = 1;
      v.currentTime = 0;
      delete v.dataset.userPaused;
      v.play().catch(() => {});
    } else v.muted = true;
  });
  const seek = (clientX) => {
    ensureLoaded(v);
    const r = bar.getBoundingClientRect();
    if (v.duration) v.currentTime = clamp01((clientX - r.left) / r.width) * v.duration;
    progress();
  };
  bar.addEventListener('click', (e) => seek(e.clientX));
  bar.addEventListener('keydown', (e) => {
    if (!v.duration) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); v.currentTime = Math.min(v.duration, v.currentTime + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); v.currentTime = Math.max(0, v.currentTime - 1); }
  });
  sync();
  return wrap;
}
