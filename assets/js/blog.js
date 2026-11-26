// Blog: índice de la nota, video de YouTube y filtros del listado. Todo el contenido ya viene en el HTML.
(function () {
  var indice = document.querySelector('.nota-indice');
  if (indice) {
    var ancho = window.matchMedia('(min-width: 1040px)');
    var ajustar = function () { indice.open = ancho.matches; };
    ajustar();
    if (ancho.addEventListener) ancho.addEventListener('change', ajustar);
    indice.addEventListener('click', function (e) { if (e.target.closest('a') && !ancho.matches) indice.open = false; });
    // marca en el índice la sección que se está leyendo
    var enlaces = {}, titulos = [];
    indice.querySelectorAll('a[href^="#"]').forEach(function (a) {
      var h = document.getElementById(a.getAttribute('href').slice(1));
      if (h) { enlaces[h.id] = a; titulos.push(h); }
    });
    var marcar = function () {
      var actual = titulos[0];
      titulos.forEach(function (h) { if (h.getBoundingClientRect().top < 180) actual = h; });
      Object.keys(enlaces).forEach(function (k) { enlaces[k].classList.toggle('activo', !!actual && k === actual.id); });
    };
    window.addEventListener('scroll', marcar, { passive: true });
    marcar();
  }

  // Video de YouTube: se muestra la portada y el reproductor se carga recién al tocarla. Sin JavaScript es un enlace normal.
  document.querySelectorAll('.nota-video__marco[data-youtube]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey) return;
      e.preventDefault();
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(a.dataset.youtube) + '?autoplay=1&rel=0&playsinline=1';
      f.title = a.dataset.titulo || 'Video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      f.referrerPolicy = 'strict-origin-when-cross-origin';
      var caja = document.createElement('div');
      caja.className = 'nota-video__marco';
      caja.appendChild(f);
      a.replaceWith(caja);
      f.focus();
    });
  });

  var grilla = document.getElementById('blog-grid');
  if (!grilla) return;
  var buscar = document.getElementById('blog-buscar');
  var chips = Array.prototype.slice.call(document.querySelectorAll('.nota-chip'));
  var sin = document.getElementById('blog-sin');
  var tema = new URLSearchParams(location.search).get('tema') || '';
  var plano = function (s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
  var tarjetas = Array.prototype.map.call(grilla.children, function (el) { return { el: el, texto: plano(el.textContent) }; });
  function filtrar() {
    var terminos = plano(buscar ? buscar.value : '').split(/\s+/).filter(Boolean), n = 0;
    tarjetas.forEach(function (t) {
      var ver = (!tema || t.el.dataset.sec === tema) && terminos.every(function (x) { return t.texto.indexOf(x) !== -1; });
      t.el.hidden = !ver; if (ver) n++;
    });
    chips.forEach(function (c) { c.setAttribute('aria-pressed', String(c.dataset.tema === tema)); });
    if (sin) sin.hidden = n > 0;
  }
  chips.forEach(function (c) { c.addEventListener('click', function () { tema = c.dataset.tema; filtrar(); }); });
  if (buscar) buscar.addEventListener('input', filtrar);
  filtrar();
})();
