// Vistas de detalle: cada sección se abre a pantalla completa sobre la ciudad desenfocada.
// Works con filtros y proyectos, galerías con visor, reproductores con sonido.
import { CONTENT } from './content.js?v=20260922141825';
import { setupVideo, ensureLoaded, muteOthers } from './video.js?v=20260922141825';

const esc = (s = '') => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NAMES = { motion: 'Motion', works: 'Works', built: 'Built', architect: 'The architect of form', vienna: 'Vienna', world: 'World', about: 'About' };

function videoTag({ src, srcWebm, poster, autoplay = false, light = false }) {
  return `<video ${autoplay ? 'data-autoplay' : ''} muted loop playsinline preload="none" poster="${esc(poster || '')}"
    data-src="${esc(src)}" ${srcWebm ? `data-src-webm="${esc(srcWebm)}"` : ''} class="${light ? 'is-light' : ''}"></video>`;
}
function head(c, key) {
  return `<header class="d-head">
      <p class="mono d-num">&gt; ${esc(c.num)} / ${esc(NAMES[key].toUpperCase())}</p>
      <h2 class="d-title" id="detail-title">${esc(c.title)}</h2>
      <p class="mono d-sub">${esc(c.sub)}</p>
      ${c.intro ? `<p class="d-intro">${esc(c.intro)}</p>` : ''}
    </header>`;
}

// ------------------------------------------------------------------ plantillas por sección
const RENDER = {
  motion(c) {
    return head(c, 'motion') + `
      <p class="mono d-disclaimer">${esc(c.disclaimer)}</p>
      <div class="d-pieces">${c.pieces.map((p) => `
        <figure class="d-piece">
          <span class="tag mono">Independent</span>
          ${videoTag({ ...p, autoplay: true })}
          <figcaption><strong>${esc(p.title)}</strong><span class="mono">${esc(p.meta)}</span><p>${esc(p.text)}</p></figcaption>
        </figure>`).join('')}</div>`;
  },

  works(c) {
    const cards = [
      ...c.experiments.map((e, i) => ({ kind: e.type, i, cat: e.cat, title: e.title, img: e.type === 'image' ? (e.thumb || e.src) : e.poster, preview: e.preview })),
      ...c.projects.map((p, i) => ({ kind: 'project', i, cat: p.cat, title: p.title, img: p.coverThumb || p.cover, tag: p.tag, count: p.photos.length + (p.video ? 1 : 0) })),
    ];
    return head(c, 'works') + `
      <nav class="d-filters" aria-label="Filter works">
        ${['All', '3D & Experiments', 'Branding', 'Campaigns'].map((f, i) => `<button class="pill ${i ? '' : 'is-active'}" type="button" data-filter="${esc(f)}">${esc(f)}</button>`).join('')}
      </nav>
      <div class="d-grid">${cards.map((k) => `
        <button class="d-card" type="button" data-cat="${esc(k.cat)}" data-kind="${k.kind}" data-i="${k.i}" aria-label="${esc(k.title)}">
          <img loading="lazy" src="${esc(k.img)}" alt="">
          ${k.kind === 'video' ? `<video class="d-preview" muted loop playsinline preload="none" data-src="${esc(k.preview)}"></video><span class="d-badge mono">Film</span>` : ''}
          ${k.kind === 'project' ? `<span class="d-badge mono">${k.count} pieces</span>` : ''}
          <span class="d-cap"><span class="mono">${esc(k.kind === 'project' ? `${k.cat} · ${k.tag}` : k.cat)}</span><b>${esc(k.title)}</b></span>
        </button>`).join('')}</div>`;
  },

  project(p) {
    return `<button class="pill d-back" type="button">&larr; All works</button>
      <header class="d-head">
        <p class="mono d-num">&gt; 02 / WORKS / ${esc(p.cat.toUpperCase())}</p>
        <h2 class="d-title" id="detail-title">${esc(p.title)}</h2>
        <p class="mono d-sub">${esc(p.tag)} · ${p.photos.length} images${p.video ? ' · film' : ''}</p>
      </header>
      ${p.video ? `<figure class="d-film">${videoTag({ src: p.video, poster: p.videoPoster, autoplay: true })}</figure>` : ''}
      <div class="d-grid d-grid--photos">${p.photos.map((ph, i) => `
        <button class="d-card" type="button" data-photo="${i}" aria-label="${esc(ph.label)}">
          <img loading="lazy" src="${esc(ph.thumb || ph.src)}" alt=""><span class="d-cap"><b>${esc(ph.label)}</b></span>
        </button>`).join('')}</div>`;
  },

  built(c) {
    return head(c, 'built') + `<ol class="d-builds">${c.items.map((b) => `
      <li class="d-build">
        <p class="mono"><span>${esc(b.n)}</span> ${esc(b.status)}</p>
        <h3>${esc(b.title)}</h3>
        <p class="mono d-kind">${esc(b.kind)}</p>
        <p class="d-text">${esc(b.text)}</p>
        <ul class="d-chips">${b.stack.map((s) => `<li class="mono">${esc(s)}</li>`).join('')}</ul>
        ${b.link ? `<a class="pill" href="${esc(b.link)}" target="_blank" rel="noopener">Open it &rarr;</a>` : ''}
      </li>`).join('')}</ol>`;
  },

  architect(c) {
    return head(c, 'architect') + `<dl class="d-facts">${c.facts.map((f) => `
      <div><dt class="mono">&gt; ${esc(f.k)}</dt><dd>${esc(f.v)}</dd></div>`).join('')}</dl>`;
  },

  vienna(c) {
    return head(c, 'vienna') + `<div class="d-masonry">${c.photos.map((p, i) => `
      <button class="d-photo" type="button" data-photo="${i}" aria-label="${esc(p.label)}"><img loading="lazy" src="${esc(p.thumb || p.src)}" alt=""></button>`).join('')}</div>`;
  },

  world(c) {
    return head(c, 'world') + `
      <h3 class="mono d-h3">&gt; The films</h3>
      <div class="d-films">${c.films.map((f) => `
        <figure class="d-piece">${videoTag({ src: f.src, poster: f.poster })}
          <figcaption><strong>${esc(f.title)}</strong><span class="mono">${esc(f.meta)}</span></figcaption></figure>`).join('')}</div>
      <h3 class="mono d-h3">&gt; Key visuals</h3>
      <div class="d-grid d-grid--wide">${c.visuals.map((v, i) => `
        <button class="d-card" type="button" data-photo="${i}" aria-label="${esc(v.label)}">
          <img loading="lazy" src="${esc(v.src)}" alt=""><span class="d-cap"><b>${esc(v.label)}</b></span></button>`).join('')}</div>`;
  },

  about(c) {
    return head(c, 'about') + `
      <div class="d-cols">
        <div><h3 class="mono d-h3">&gt; Experience</h3>
          <dl class="d-facts">${c.experience.map((e) => `<div><dt class="mono">${esc(e.k)}</dt><dd>${esc(e.v)}</dd></div>`).join('')}</dl></div>
        <div><h3 class="mono d-h3">&gt; Tools</h3>
          <ul class="d-tools">${c.tools.map(([t, l]) => `<li><span>${esc(t)}</span><span class="mono d-level" data-level="${esc(l)}">${esc(l)}</span></li>`).join('')}</ul>
          <h3 class="mono d-h3">&gt; Languages</h3>
          <p class="mono">${c.languages.map(esc).join(' &nbsp;·&nbsp; ')}</p></div>
      </div>
      <div class="d-actions">
        <a class="pill pill--solid" href="mailto:${esc(c.email)}?subject=Project%20Inquiry%20%C2%B7%20Baldomero%20Portfolio">Send an email</a>
        <a class="pill" href="${esc(c.cv)}" target="_blank" rel="noopener">CV · PDF</a>
      </div>`;
  },
};

// ------------------------------------------------------------------ montaje
export function initDetail({ onOpen, onClose }) {
  document.body.insertAdjacentHTML('beforeend', `
    <div class="detail" id="detail" role="dialog" aria-modal="true" aria-labelledby="detail-title" hidden>
      <div class="detail-bar">
        <span class="mono" id="detail-crumb"></span>
        <button class="pill detail-close" type="button" aria-label="Close section">Close &nbsp;&#x2715;</button>
      </div>
      <div class="detail-scroll" data-lenis-prevent><div class="detail-inner" id="detail-body"></div></div>
    </div>
    <div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Viewer" hidden>
      <button class="lb-btn lb-close pill" type="button" aria-label="Close viewer">Close &nbsp;&#x2715;</button>
      <button class="lb-btn lb-prev" type="button" aria-label="Previous">&larr;</button>
      <button class="lb-btn lb-next" type="button" aria-label="Next">&rarr;</button>
      <figure class="lb-fig"><div class="lb-media"></div><figcaption class="mono lb-cap"></figcaption></figure>
    </div>`);
  const detail = document.getElementById('detail');
  const body = document.getElementById('detail-body');
  const crumb = document.getElementById('detail-crumb');
  const scroller = detail.querySelector('.detail-scroll');
  const lb = document.getElementById('lightbox');
  const lbMedia = lb.querySelector('.lb-media');
  const lbCap = lb.querySelector('.lb-cap');
  let current = null, opener = null, lbItems = [], lbIndex = 0;

  // vídeos del contenido: controles + arranque en silencio de los marcados
  function wireVideos(root) {
    root.querySelectorAll('video:not(.d-preview)').forEach((v) => {
      setupVideo(v);
      if (v.hasAttribute('data-autoplay')) { ensureLoaded(v); v.play().catch(() => {}); }
    });
    root.querySelectorAll('.d-card[data-kind="video"]').forEach((card) => {
      const pv = card.querySelector('.d-preview');
      card.addEventListener('mouseenter', () => { ensureLoaded(pv); pv.play().then(() => card.classList.add('is-playing')).catch(() => {}); });
      card.addEventListener('mouseleave', () => { pv.pause(); card.classList.remove('is-playing'); });
    });
  }
  function stopVideos(root) { root.querySelectorAll('video').forEach((v) => v.pause()); }

  // ---------------------------------------------------------------- vistas (sin tocar el historial)
  let viewProject = null;
  function render(key, sub) {
    stopVideos(body);
    viewProject = key === 'works' && sub != null ? sub : null;
    if (viewProject != null) {
      const p = CONTENT.works.projects[sub];
      body.innerHTML = RENDER.project(p);
      body.querySelector('.d-back').addEventListener('click', backFromProject);
      body.querySelectorAll('[data-photo]').forEach((b) => b.addEventListener('click', () =>
        openLightbox(p.photos.map((ph) => ({ type: 'image', src: ph.src, label: `${p.title} · ${ph.label}` })), +b.dataset.photo)));
    } else {
      body.innerHTML = RENDER[key](CONTENT[key]);
      bindSection(key);
    }
    wireVideos(body);
    scroller.scrollTop = 0;
    crumb.textContent = `> ${CONTENT[key].num} / ${NAMES[key].toUpperCase()}${sub != null ? ' / ' + CONTENT.works.projects[sub].title.toUpperCase() : ''}`;
  }

  function bindSection(key) {
    const c = CONTENT[key];
    if (key === 'works') {
      const cards = [...body.querySelectorAll('.d-card')];
      body.querySelectorAll('[data-filter]').forEach((btn) => btn.addEventListener('click', () => {
        body.querySelectorAll('[data-filter]').forEach((b) => b.classList.toggle('is-active', b === btn));
        const f = btn.dataset.filter;
        cards.forEach((card) => { card.hidden = !(f === 'All' || card.dataset.cat === f); });
      }));
      const expItems = c.experiments.map((e) => e.type === 'video'
        ? { type: 'video', src: e.src, poster: e.poster, label: `${e.cat} · ${e.title}` }
        : { type: 'image', src: e.src, label: `${e.cat} · ${e.title}` });
      cards.forEach((card) => card.addEventListener('click', () => {
        const i = +card.dataset.i;
        if (card.dataset.kind === 'project') goProject(i);
        else openLightbox(expItems, i);
      }));
    }
    if (key === 'vienna') {
      const items = c.photos.map((p) => ({ type: 'image', src: p.src, label: p.label }));
      body.querySelectorAll('[data-photo]').forEach((b) => b.addEventListener('click', () => openLightbox(items, +b.dataset.photo)));
    }
    if (key === 'world') {
      const items = c.visuals.map((v) => ({ type: 'image', src: v.src, label: v.label }));
      body.querySelectorAll('[data-photo]').forEach((b) => b.addEventListener('click', () => openLightbox(items, +b.dataset.photo)));
    }
  }

  function showDetail(key, trigger) {
    opener = trigger || opener || document.activeElement;
    const wasOpen = !!current;
    current = key;
    render(key);
    detail.hidden = false;
    requestAnimationFrame(() => detail.classList.add('is-open'));
    document.body.classList.add('detail-open');
    detail.querySelector('.detail-close').focus();
    if (!wasOpen) onOpen?.(key);
  }
  function hideDetail() {
    if (!current) return;
    hideLightbox();
    stopVideos(body);
    detail.classList.remove('is-open');
    document.body.classList.remove('detail-open');
    setTimeout(() => { if (!current) { detail.hidden = true; body.innerHTML = ''; } }, 450);
    const k = current;
    current = null;
    viewProject = null;
    opener?.focus?.();
    opener = null;
    onClose?.(k);
  }

  // ---------------------------------------------------------------- historial
  // Cada paso hacia dentro (sección, proyecto, visor) es una entrada del historial: el botón de
  // atrás del ratón o del navegador cierra lo último que se abrió y nunca saca de la web.
  const level = () => (history.state && history.state.vd ? history.state.lv : 0);
  const idOf = (i) => CONTENT.works.projects[i].id;

  function open(key, trigger, projectId) {
    if (!RENDER[key]) return;
    if (current === key && viewProject == null) return;
    history.pushState({ vd: key, p: null, lb: false, lv: level() + 1 }, '', `#${key}`);
    showDetail(key, trigger);
    if (key === 'works' && projectId) {
      const i = CONTENT.works.projects.findIndex((p) => p.id === projectId);
      if (i >= 0) goProject(i);
    }
  }
  function goProject(i) {
    history.pushState({ vd: 'works', p: i, lb: false, lv: level() + 1 }, '', `#works/${idOf(i)}`);
    render('works', i);
  }
  function backFromProject() {
    if (history.state && history.state.p != null) history.back();
    else render('works');
  }
  function close() {                                   // botón Close y Esc: cierra la sección entera
    const lv = level();
    if (lv > 0) history.go(-lv);
    else hideDetail();
  }

  addEventListener('popstate', (e) => {
    const s = e.state;
    if (!s || !s.vd) { hideDetail(); return; }
    if (current !== s.vd) showDetail(s.vd);
    if (s.p != null && viewProject !== s.p) render('works', s.p);
    if (s.p == null && viewProject != null) render(s.vd);
    if (!s.lb) hideLightbox();
    else if (lb.hidden && lastLb) showLightbox(lastLb.items, lastLb.index);
  });

  // ---------------------------------------------------------------- visor
  let lastLb = null;
  function showLb() {
    const it = lbItems[lbIndex];
    lbMedia.querySelectorAll('video').forEach((v) => v.pause());
    if (it.type === 'video') {
      lbMedia.innerHTML = `<figure class="lb-video">${videoTag({ src: it.src, poster: it.poster })}</figure>`;
      const v = lbMedia.querySelector('video');
      setupVideo(v);
      ensureLoaded(v);
      muteOthers(v);
      v.muted = false;                                   // abrir un film es un gesto del usuario: suena
      v.play().catch(() => { v.muted = true; v.play().catch(() => {}); });
    } else {
      lbMedia.innerHTML = `<img src="${esc(it.src)}" alt="${esc(it.label)}">`;
    }
    lbCap.textContent = `${String(lbIndex + 1).padStart(2, '0')} / ${String(lbItems.length).padStart(2, '0')} · ${it.label}`;
    lb.querySelector('.lb-prev').hidden = lb.querySelector('.lb-next').hidden = lbItems.length < 2;
  }
  function showLightbox(items, index) {
    stopVideos(body);
    lbItems = items; lbIndex = index;
    lastLb = { items, index };
    lb.hidden = false;
    requestAnimationFrame(() => lb.classList.add('is-open'));
    showLb();
    lb.querySelector('.lb-close').focus();
  }
  function hideLightbox() {
    if (lb.hidden) return false;
    lbMedia.querySelectorAll('video').forEach((v) => v.pause());
    lbMedia.innerHTML = '';
    lb.classList.remove('is-open');
    lb.hidden = true;
    return true;
  }
  function openLightbox(items, index) {
    const s = history.state && history.state.vd ? history.state : { vd: current, p: viewProject, lv: 0 };
    history.pushState({ ...s, lb: true, lv: s.lv + 1 }, '');
    showLightbox(items, index);
  }
  function closeLightbox() {
    if (lb.hidden) return false;
    if (history.state && history.state.lb) history.back();
    else hideLightbox();
    return true;
  }
  const step = (d) => { lbIndex = (lbIndex + d + lbItems.length) % lbItems.length; lastLb = { items: lbItems, index: lbIndex }; showLb(); };
  lb.querySelector('.lb-close').addEventListener('click', closeLightbox);
  lb.querySelector('.lb-prev').addEventListener('click', () => step(-1));
  lb.querySelector('.lb-next').addEventListener('click', () => step(1));
  lb.addEventListener('click', (e) => { if (e.target === lb) closeLightbox(); });

  detail.querySelector('.detail-close').addEventListener('click', close);
  addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && current) { if (!closeLightbox()) close(); }
    if (!lb.hidden && e.key === 'ArrowRight') step(1);
    if (!lb.hidden && e.key === 'ArrowLeft') step(-1);
  });
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-open]');
    if (t) { e.preventDefault(); open(t.dataset.open, t); }
  });
  document.addEventListener('keydown', (e) => {
    const t = e.target.closest?.('[data-open][role="button"]');
    if (t && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); open(t.dataset.open, t); }
  });

  return { open, close, isOpen: () => !!current };
}
