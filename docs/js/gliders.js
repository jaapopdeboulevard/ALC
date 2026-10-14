// Vliegende modelzwevers in de hero van de homepage.
// Elk toestel zweeft rustig rond, draait af en toe een thermiekbel en laat een vaag spoor achter.
(function () {
  var canvas = document.querySelector('.x-sky');
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W = 0, H = 0, dpr = 1, gliders = [], last = 0, running = true;

  var COLORS = [
    { body: '#0b1220', accent: '#facc15' },
    { body: '#2357d9', accent: '#ffffff' },
    { body: '#1e3a8a', accent: '#38bdf8' },
    { body: '#0b1220', accent: '#2357d9' }
  ];

  function rand(a, b) { return a + Math.random() * (b - a); }

  function resize() {
    var r = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function make(i, n) {
    var depth = rand(0.35, 1);              // verder weg = kleiner, lichter en trager
    var leftSide = i % 2 === 0;             // houd het midden (tekst) zo veel mogelijk vrij
    return {
      x: leftSide ? rand(0, W * 0.3) : rand(W * 0.7, W),
      y: rand(H * 0.05, H * 0.55),
      a: rand(0, Math.PI * 2),
      speed: 26 + 34 * depth,
      turn: 0,
      mode: 'cruise',
      timer: rand(2, 6),
      size: 0.45 + 0.75 * depth,
      alpha: 0.25 + 0.55 * depth,
      color: COLORS[i % COLORS.length],
      trail: []
    };
  }

  function init() {
    resize();
    var n = W < 640 ? 3 : W < 1000 ? 4 : 6;
    gliders = [];
    for (var i = 0; i < n; i++) gliders.push(make(i, n));
    gliders.sort(function (p, q) { return p.size - q.size; });
  }

  // Bovenaanzicht van een zwever, neus naar rechts (+x)
  function drawGlider(g) {
    var s = g.size;
    ctx.save();
    ctx.translate(g.x, g.y);
    ctx.rotate(g.a);
    // schaduw van de bocht: vleugel iets smaller in een draai (helling)
    var bank = Math.max(0.55, 1 - Math.abs(g.turn) * 0.9);
    ctx.scale(s, s);
    ctx.globalAlpha = g.alpha;
    ctx.fillStyle = g.color.body;
    // romp
    ctx.beginPath();
    ctx.ellipse(-8, 0, 30, 2.6, 0, 0, Math.PI * 2);
    ctx.fill();
    // vleugel (taps, met lichte pijlstelling)
    ctx.beginPath();
    ctx.moveTo(6, 0);
    ctx.lineTo(4, -62 * bank);
    ctx.lineTo(0, -62 * bank);
    ctx.lineTo(-4, 0);
    ctx.lineTo(0, 62 * bank);
    ctx.lineTo(4, 62 * bank);
    ctx.closePath();
    ctx.fill();
    // stabilo
    ctx.beginPath();
    ctx.moveTo(-31, 0);
    ctx.lineTo(-33, -13 * bank);
    ctx.lineTo(-36, -13 * bank);
    ctx.lineTo(-37, 0);
    ctx.lineTo(-36, 13 * bank);
    ctx.lineTo(-33, 13 * bank);
    ctx.closePath();
    ctx.fill();
    // gekleurde vleugeltips
    ctx.fillStyle = g.color.accent;
    ctx.fillRect(0, -62 * bank, 4, 9 * bank);
    ctx.fillRect(0, 53 * bank, 4, 9 * bank);
    ctx.restore();
  }

  function drawTrail(g) {
    if (g.trail.length < 2) return;
    ctx.save();
    ctx.lineWidth = 1.2;
    for (var i = 1; i < g.trail.length; i++) {
      var p = g.trail[i - 1], q = g.trail[i];
      if (Math.abs(p.x - q.x) > 100 || Math.abs(p.y - q.y) > 100) continue; // overgang langs de rand
      ctx.globalAlpha = (i / g.trail.length) * 0.22 * g.alpha;
      ctx.strokeStyle = '#2357d9';
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(q.x, q.y);
      ctx.stroke();
    }
    ctx.restore();
  }

  function step(g, dt) {
    g.timer -= dt;
    if (g.timer <= 0) {
      if (g.mode === 'cruise' && Math.random() < 0.6) {
        g.mode = 'thermal';                         // rondjes draaien in een thermiekbel
        g.turn = (Math.random() < 0.5 ? -1 : 1) * rand(0.45, 0.7);
        g.timer = rand(5, 11);
      } else {
        g.mode = 'cruise';
        g.turn = rand(-0.08, 0.08);
        g.timer = rand(3, 7);
      }
    }
    if (g.mode === 'cruise') g.turn += rand(-0.05, 0.05) * dt;
    g.a += g.turn * dt;
    g.x += Math.cos(g.a) * g.speed * dt;
    g.y += Math.sin(g.a) * g.speed * dt;
    var m = 80 * g.size;
    if (g.x < -m) g.x = W + m; else if (g.x > W + m) g.x = -m;
    if (g.y < -m) g.y = H * 0.6; else if (g.y > H * 0.75 + m) g.y = -m;
    g.trail.push({ x: g.x, y: g.y });
    if (g.trail.length > 70) g.trail.shift();
  }

  function frame(t) {
    if (!running) return;
    var dt = last ? Math.min((t - last) / 1000, 0.05) : 0;
    last = t;
    ctx.clearRect(0, 0, W, H);
    for (var i = 0; i < gliders.length; i++) {
      step(gliders[i], dt);
      drawTrail(gliders[i]);
      drawGlider(gliders[i]);
    }
    requestAnimationFrame(frame);
  }

  function still() {
    ctx.clearRect(0, 0, W, H);
    gliders.forEach(drawGlider);
  }

  init();
  window.addEventListener('resize', function () { init(); if (reduce) still(); });
  if (reduce) { still(); return; }

  // Alleen animeren als de hero in beeld is en het tabblad zichtbaar is
  var visible = true;
  function update() {
    var should = visible && !document.hidden;
    if (should && !running) { running = true; last = 0; requestAnimationFrame(frame); }
    running = should;
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; update(); }).observe(canvas);
  }
  document.addEventListener('visibilitychange', update);
  requestAnimationFrame(frame);
})();
