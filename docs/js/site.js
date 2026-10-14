// Mobiel menu, submenu en fotovergroting (lightbox)
(function () {
  var header = document.querySelector('.site-header');
  function onScroll() { header.classList.toggle('scrolled', window.scrollY > 40); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var toggle = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open);
      toggle.setAttribute('aria-label', open ? 'Menu sluiten' : 'Menu openen');
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }
  document.querySelectorAll('.sub-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.closest('.has-sub');
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });
  });

  // Lightbox voor foto's in galerijen en losse grote foto's
  var lb = document.querySelector('.lightbox');
  if (!lb) return;
  var lbImg = lb.querySelector('img');
  var lbCap = lb.querySelector('figcaption');
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-zoom], .gallery img'));
  var current = 0;

  function caption(img) {
    var fig = img.closest('figure');
    var cap = fig && fig.querySelector('figcaption');
    return cap ? cap.textContent : img.alt || '';
  }
  function show(i) {
    current = (i + items.length) % items.length;
    var img = items[current];
    lbImg.src = img.currentSrc || img.src;
    lbImg.alt = img.alt;
    lbCap.textContent = caption(img);
  }
  function close() {
    lb.hidden = true;
    document.body.style.overflow = '';
  }
  items.forEach(function (img, i) {
    img.addEventListener('click', function () {
      show(i);
      lb.hidden = false;
      document.body.style.overflow = 'hidden';
      lb.querySelector('.lb-close').focus();
    });
  });
  var multi = items.length > 1;
  lb.querySelector('.lb-prev').hidden = !multi;
  lb.querySelector('.lb-next').hidden = !multi;
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function () { show(current - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function () { show(current + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft' && multi) show(current - 1);
    if (e.key === 'ArrowRight' && multi) show(current + 1);
  });
})();
