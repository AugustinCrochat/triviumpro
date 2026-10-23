/* Galería de la ficha de producto: zoom tipo lupa + lightbox.
 *
 * Mismo comportamiento que la galería de Neumáticos Trivium:
 *  - Con mouse (pantalla ancha): una lente cuadrada sigue al cursor sobre la
 *    foto y un panel a un costado muestra esa zona ampliada (ZOOM veces).
 *  - Clic / tap: lightbox con la foto completa (Esc, clic afuera o ✕ cierran;
 *    flechas del teclado y botones si hay más de una foto).
 *  - Táctil: swipe horizontal para pasar de foto. No hay lupa (no hay hover).
 *
 * Se inicializa desde producto.html después de pintar la galería:
 *   initGalleryZoom(['assets/img/...', ...])  // rutas ya resueltas
 */
(function () {
  const ZOOM = 2.5;
  const GAP = 16;
  const SWIPE = 40;

  const hoverCapable = () =>
    window.matchMedia('(hover: hover) and (pointer: fine)').matches &&
    window.matchMedia('(min-width: 1024px)').matches;

  // Rectángulo que ocupa la foto dentro del marco con object-fit: contain.
  function containRect(fw, fh, aspect) {
    if (aspect > fw / fh) {
      const h = fw / aspect;
      return { left: 0, top: (fh - h) / 2, width: fw, height: h };
    }
    const w = fh * aspect;
    return { left: (fw - w) / 2, top: 0, width: w, height: fh };
  }

  window.initGalleryZoom = function (srcs, caps) {
    caps = caps || [];
    const main = document.getElementById('pd-main');
    if (!main || !srcs || !srcs.length) return;
    const thumbs = Array.from(document.querySelectorAll('.pd-gallery .thumb'));
    let index = 0;
    let lens = null;
    let panel = null;
    let swiped = false;
    let touchStart = null;

    main.classList.add('zoomable');
    const icon = document.createElement('span');
    icon.className = 'pd-zoom-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16zM11 8v6M8 11h6"/></svg>';
    main.appendChild(icon);
    main.setAttribute('role', 'button');
    main.setAttribute('tabindex', '0');
    main.setAttribute('aria-label', 'Ampliar imagen');

    const img = () => main.querySelector('img');
    const baseAlt = (img() && img().alt) || 'Imagen del producto';
    const capEl = document.getElementById('pd-cap');
    function setCaption() {
      const cap = caps[index] || '';
      const el = img();
      if (el) el.alt = cap ? baseAlt + ' — ' + cap : baseAlt;
      if (capEl) { capEl.textContent = cap; capEl.hidden = !cap; }
    }

    function show(i) {
      index = (i + srcs.length) % srcs.length;
      const el = img();
      if (el) { el.src = srcs[index]; el.style.display = ''; }
      thumbs.forEach((t, k) => t.classList.toggle('active', k === index));
      setCaption();
      closeZoom();
    }

    function closeZoom() {
      if (lens) { lens.remove(); lens = null; }
      if (panel) { panel.remove(); panel = null; }
    }

    function aspectOf(el) {
      return el && el.naturalWidth ? el.naturalWidth / el.naturalHeight : 1;
    }

    function move(e) {
      const el = img();
      if (!el || !hoverCapable()) return;
      const r = main.getBoundingClientRect();
      const c = containRect(r.width, r.height, aspectOf(el));
      const lw = c.width / ZOOM, lh = c.height / ZOOM;
      const mx = e.clientX - r.left, my = e.clientY - r.top;
      const left = Math.min(Math.max(mx - lw / 2, c.left), c.left + c.width - lw);
      const top = Math.min(Math.max(my - lh / 2, c.top), c.top + c.height - lh);
      if (!lens) { lens = document.createElement('span'); lens.className = 'pd-lens'; main.appendChild(lens); }
      lens.style.cssText = `left:${left}px;top:${top}px;width:${lw}px;height:${lh}px`;

      // Panel anclado al costado con más lugar, lo más grande que entre en la ventana.
      const panelTop = Math.max(GAP / 2, r.top);
      const maxH = window.innerHeight - panelTop - GAP;
      const spaceR = window.innerWidth - r.right - GAP * 2;
      const spaceL = r.left - GAP * 2;
      const onRight = spaceR >= spaceL;
      const maxW = Math.max(onRight ? spaceR : spaceL, r.width * 0.6);
      const size = Math.min(r.width * 1.8, maxW, maxH);
      const a = aspectOf(el);
      const bw = (a > 1 ? size : size * a) * ZOOM;
      const bh = (a > 1 ? size / a : size) * ZOOM;
      const fx = (left - c.left + lw / 2) / c.width;
      const fy = (top - c.top + lh / 2) / c.height;
      const bx = Math.min(0, Math.max(size - bw, size / 2 - fx * bw));
      const by = Math.min(0, Math.max(size - bh, size / 2 - fy * bh));
      if (!panel) { panel = document.createElement('div'); panel.className = 'pd-zoom-panel'; panel.setAttribute('aria-hidden', 'true'); document.body.appendChild(panel); }
      panel.style.cssText =
        `left:${onRight ? r.right + GAP : r.left - GAP - size}px;top:${panelTop}px;width:${size}px;height:${size}px;` +
        `background-image:url("${el.currentSrc || el.src}");background-size:${bw}px ${bh}px;background-position:${bx}px ${by}px`;
    }

    main.addEventListener('mousemove', move);
    main.addEventListener('mouseleave', closeZoom);
    window.addEventListener('scroll', closeZoom, { passive: true });

    main.addEventListener('touchstart', e => {
      const t = e.touches[0]; touchStart = { x: t.clientX, y: t.clientY };
    }, { passive: true });
    main.addEventListener('touchend', e => {
      const s = touchStart; touchStart = null;
      if (!s || srcs.length < 2) return;
      const t = e.changedTouches[0], dx = t.clientX - s.x, dy = t.clientY - s.y;
      // Solo cuenta si el gesto es sobre todo horizontal: si no, es un scroll.
      if (Math.abs(dx) > SWIPE && Math.abs(dx) > Math.abs(dy) * 1.5) { swiped = true; show(dx < 0 ? index + 1 : index - 1); }
    });

    main.addEventListener('click', () => {
      // El swipe también dispara un click al soltar el dedo: no abre el lightbox.
      if (swiped) { swiped = false; return; }
      openLightbox();
    });
    main.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLightbox(); }
    });
    thumbs.forEach((t, k) => t.addEventListener('click', () => show(k)));

    function openLightbox() {
      closeZoom();
      const alt = (img() && img().alt) || 'Imagen del producto';
      const lb = document.createElement('div');
      lb.className = 'pd-lightbox';
      lb.setAttribute('role', 'dialog');
      lb.setAttribute('aria-modal', 'true');
      lb.setAttribute('aria-label', alt);
      const multi = srcs.length > 1;
      lb.innerHTML =
        '<button type="button" class="pd-lb-close" aria-label="Cerrar">&#10005;</button>' +
        (multi ? '<button type="button" class="pd-lb-nav pd-lb-prev" aria-label="Foto anterior">&#10094;</button>' +
                 '<button type="button" class="pd-lb-nav pd-lb-next" aria-label="Foto siguiente">&#10095;</button>' : '') +
        `<img src="${srcs[index]}" alt="${alt.replace(/"/g, '&quot;')}"><p class="pd-lb-cap"></p>`;
      const previouslyFocused = document.activeElement;
      const prevOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      document.body.appendChild(lb);
      const lbImg = lb.querySelector('img');
      const lbCap = lb.querySelector('.pd-lb-cap');
      const paintCap = () => { lbCap.textContent = caps[index] || ''; lbCap.hidden = !caps[index]; };
      paintCap();
      const go = i => { index = (i + srcs.length) % srcs.length; lbImg.src = srcs[index]; show(index); paintCap(); };
      function close() {
        lb.remove(); document.body.style.overflow = prevOverflow;
        document.removeEventListener('keydown', onKey);
        if (previouslyFocused && previouslyFocused.focus) previouslyFocused.focus();
      }
      function onKey(e) {
        if (e.key === 'Escape') close();
        else if (multi && e.key === 'ArrowRight') go(index + 1);
        else if (multi && e.key === 'ArrowLeft') go(index - 1);
      }
      document.addEventListener('keydown', onKey);
      lb.addEventListener('click', e => {
        if (e.target.closest('.pd-lb-close') || e.target === lb) close();
        else if (e.target.closest('.pd-lb-prev')) go(index - 1);
        else if (e.target.closest('.pd-lb-next')) go(index + 1);
      });
      lb.querySelector('.pd-lb-close').focus();
    }
  };
})();
