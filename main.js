/* LOSELESS — interactions & motion */
(() => {
  'use strict';

  // ---------------------------------------------------------------
  // À renseigner
  // ---------------------------------------------------------------
  const CONFIG = {
    bookingUrl: null,         // [À COMPLÉTER] lien de prise de rendez-vous (ex. Calendly)
  };

  // Section 05 — simulateur (aucun montant affiché, uniquement des leads).
  // defauts : position de départ des 2 curseurs (leads / mois, % sans budget).
  // seuilGrille / leadsParPoint : au-delà de 300 leads, 1 point de la grille = 5 leads.
  const SIMULATEUR = {
    defauts: { leads: 200, sansBudget: 50 },
    seuilGrille: 300,
    leadsParPoint: 5,
  };

  // Section 01 — grand chiffre « [X %] des leads en appel repartent sans rien acheter ».
  // Mettre null pour réafficher le placeholder.
  const PROBLEME_STATS = { x: 80 };

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  // Langue de la page (<html lang="fr"> ou <html lang="en">) : textes et formats de nombres
  const LANG = (root.lang || 'fr').slice(0, 2) === 'en' ? 'en' : 'fr';
  const LOCALE = LANG === 'en' ? 'en-US' : 'fr-FR';
  const fmt = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 0 });
  const pct = n => (LANG === 'en' ? `${n}%` : `${n}\u00a0%`);
  const eur = n => (LANG === 'en' ? `€${fmt.format(n)}` : `${fmt.format(n)}\u00a0€`);
  const T = {
    fr: {
      perYear: n => `soit ${fmt.format(n)} leads par an.`,
      live: (n, y) => `${fmt.format(n)} ${n > 1 ? 'leads repartent' : 'lead repart'} sans rien chaque mois, soit ${fmt.format(y)} par an.`,
      curtainAfter: 'Surtout « avec loseless »',
      curtainBefore: 'Surtout « aujourd\'hui »',
      curtainHalf: 'Moitié-moitié',
      ringStart: 'pour démarrer',
      ringEnd: 'pour vous, sur chaque vente',
    },
    en: {
      perYear: n => `that’s ${fmt.format(n)} leads a year.`,
      live: (n, y) => `${fmt.format(n)} ${n > 1 ? 'leads walk' : 'lead walks'} away with nothing every month, that’s ${fmt.format(y)} a year.`,
      curtainAfter: 'Mostly “with loseless”',
      curtainBefore: 'Mostly “today”',
      curtainHalf: 'Half and half',
      ringStart: 'to get started',
      ringEnd: 'for you, on every sale',
    },
  }[LANG];
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

  const hasGsap = !!(window.gsap && window.ScrollTrigger && window.SplitText && window.CustomEase);
  const motion = root.classList.contains('motion') && hasGsap && !!window.Lenis;
  if (!motion) root.classList.remove('motion');

  // Déclencheur d'apparition : par défaut sur l'élément ; une section avec data-reveal-start
  // (ex. le bandeau de chiffres, caché sous le hero pendant son retrait) impose le sien.
  const revealAt = (el, start) => {
    const host = el.closest('[data-reveal-start]');
    return host ? { trigger: host, start: host.dataset.revealStart, once: true } : { trigger: el, start, once: true };
  };

  let lenis = null;
  let refreshTimer = 0;
  const refresh = () => {
    if (!motion) return;
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => ScrollTrigger.refresh(), 60);
  };

  if (CONFIG.bookingUrl) {
    $$('[data-book]').forEach(a => {
      a.href = CONFIG.bookingUrl;
      a.target = '_blank';
      a.rel = 'noopener';
    });
  }

  function applyProblemStats() {
    const { x } = PROBLEME_STATS;
    if (typeof x === 'number') $('.problem .stat__num').dataset.count = String(x);
  }

  // ---------------------------------------------------------------
  // Simulateur (fonctionne avec ou sans animations)
  // ---------------------------------------------------------------
  function initSim() {
    const leadsIn = $('#s-leads'), sansBudgetIn = $('#s-nobudget');
    const leadsOut = $('#o-leads'), sansBudgetOut = $('#o-nobudget');
    const valueEl = $('#sim-value'), unitEl = $('#sim-unit'), yearEl = $('#sim-year');
    const grid = $('#sim-dots'), legend = $('#sim-legend'), live = $('#sim-live');
    const leadsWord = n => (n > 1 ? 'leads' : 'lead');
    const shown = { v: 0 };
    const dots = [];

    leadsIn.value = SIMULATEUR.defauts.leads;
    sansBudgetIn.value = SIMULATEUR.defauts.sansBudget;

    // Grille : on ne crée des points que lorsqu'il en faut plus, puis on les masque / colore.
    function drawGrid(leads, perdus) {
      const parPoint = leads > SIMULATEUR.seuilGrille ? SIMULATEUR.leadsParPoint : 1;
      const total = Math.ceil(leads / parPoint);
      const orange = Math.round(perdus / parPoint);
      while (dots.length < total) {
        const d = document.createElement('i');
        grid.appendChild(d);
        dots.push(d);
      }
      dots.forEach((d, i) => {
        d.hidden = i >= total;
        d.classList.toggle('is-lost', i < orange);
      });
      legend.hidden = parPoint === 1;
    }

    function compute() {
      [leadsIn, sansBudgetIn].forEach(i => {
        i.style.setProperty('--p', ((i.value - i.min) / (i.max - i.min)) * 100 + '%');
      });
      const leads = +leadsIn.value, part = +sansBudgetIn.value;
      const perdus = Math.round((leads * part) / 100);
      leadsOut.textContent = fmt.format(leads);
      sansBudgetOut.textContent = pct(part);
      unitEl.textContent = leadsWord(perdus);
      yearEl.textContent = T.perYear(perdus * 12);
      drawGrid(leads, perdus);

      if (motion) {
        gsap.to(shown, {
          v: perdus, duration: 0.6, ease: 'lossless', overwrite: true,
          onUpdate: () => { valueEl.textContent = fmt.format(Math.round(shown.v)); },
        });
      } else {
        shown.v = perdus;
        valueEl.textContent = fmt.format(perdus);
      }
      return perdus;
    }

    [leadsIn, sansBudgetIn].forEach(i => {
      i.addEventListener('input', compute);
      i.addEventListener('change', () => {
        const n = compute();
        live.textContent = T.live(n, n * 12);
      });
    });
    compute();
  }

  // Poignée du rideau (souris, doigt, clavier), avec ou sans animations
  const curtain = { touched: false, set: () => {} };
  function initCurtain() {
    const el = $('.curtain'), handle = $('.curtain__handle');
    if (!el) return;
    const MIN = 20, MAX = 55;
    const text = v => (v < 45 ? T.curtainAfter : v > 55 ? T.curtainBefore : T.curtainHalf);
    curtain.set = v => {
      el.style.setProperty('--split', v + '%');
      el.style.setProperty('--splitn', v);
      const n = Math.round(Math.min(MAX, Math.max(MIN, v)));
      handle.setAttribute('aria-valuenow', n);
      handle.setAttribute('aria-valuetext', text(n));
    };
    const move = v => { curtain.touched = true; curtain.set(Math.min(MAX, Math.max(MIN, v))); };
    const fromPointer = e => {
      const r = el.getBoundingClientRect();
      move(((e.clientX - r.left) / r.width) * 100);
    };
    handle.addEventListener('pointerdown', e => {
      e.preventDefault();
      handle.setPointerCapture(e.pointerId);
      el.classList.add('is-dragging');
      const up = () => {
        el.classList.remove('is-dragging');
        handle.removeEventListener('pointermove', fromPointer);
        handle.removeEventListener('pointerup', up);
        handle.removeEventListener('pointercancel', up);
      };
      handle.addEventListener('pointermove', fromPointer);
      handle.addEventListener('pointerup', up);
      handle.addEventListener('pointercancel', up);
    });
    handle.addEventListener('keydown', e => {
      const cur = parseFloat(getComputedStyle(el).getPropertyValue('--split')) || 50;
      const map = { ArrowLeft: cur - 5, ArrowDown: cur - 5, ArrowRight: cur + 5, ArrowUp: cur + 5, Home: MIN, End: MAX };
      if (!(e.key in map)) return;
      e.preventDefault();
      move(map[e.key]);
    });
  }

  // ---------------------------------------------------------------
  // FAQ : accordéon à hauteur animée
  // ---------------------------------------------------------------
  function initFaq() {
    const items = $$('.faq__item').map(item => ({
      btn: $('.faq__q', item),
      panel: $('.faq__panel', item),
    }));

    const set = (it, open, animate) => {
      const { btn, panel } = it;
      if ((btn.getAttribute('aria-expanded') === 'true') === open && animate) return;
      btn.setAttribute('aria-expanded', String(open));
      if (!animate) {
        panel.hidden = !open;
        return;
      }
      gsap.killTweensOf(panel);
      if (open) {
        panel.hidden = false;
        gsap.fromTo(panel, { height: 0 }, {
          height: 'auto', duration: 0.3, ease: 'power2.out',
          onComplete: () => { panel.style.height = ''; refresh(); },
        });
      } else {
        gsap.to(panel, {
          height: 0, duration: 0.3, ease: 'power2.out',
          onComplete: () => { panel.hidden = true; panel.style.height = ''; refresh(); },
        });
      }
    };

    // une seule question ouverte à la fois, la 01 par défaut
    items.forEach((it, i) => set(it, i === 0, false));
    items.forEach(it => {
      it.btn.addEventListener('click', () => {
        const open = it.btn.getAttribute('aria-expanded') !== 'true';
        items.forEach(other => { if (other !== it) set(other, false, motion); });
        set(it, open, motion);
      });
    });
  }

  // ---------------------------------------------------------------
  // Compteurs : actifs dès qu'un data-count numérique est renseigné
  // ---------------------------------------------------------------
  function initCounters() {
    $$('[data-count]').forEach(el => {
      const raw = el.dataset.count.trim();
      const n = parseFloat(raw.replace(',', '.'));
      if (!raw || Number.isNaN(n)) return; // placeholder conservé
      const decimals = (raw.split(/[.,]/)[1] || '').length;
      const f = new Intl.NumberFormat(LOCALE, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
      const prefix = el.dataset.prefix || '';
      const suffix = el.dataset.suffix || '';
      const out = v => { el.textContent = prefix + f.format(v) + suffix; };

      if (!motion) { out(n); return; }
      const o = { v: 0 };
      out(0);
      gsap.to(o, {
        v: n, duration: 1.6, onUpdate: () => out(o.v),
        scrollTrigger: revealAt(el, 'top 85%'),
      });
    });
  }

  // ---------------------------------------------------------------
  // Visualisation : les leads tombent hors de l'entonnoir
  // ---------------------------------------------------------------
  function initFunnel() {
    const canvas = $('.funnel__canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const TOP = 0.1, CALL = 0.46, NECK = 0.7, OUT = 0.93, MOUTH = 0.38, NECK_W = 0.065;
    const SPAWN = 0.1;    // un lead toutes les 100 ms
    const KEEP_EVERY = 5; // 1 lead sur 5 va jusqu'à la vente, les 4 autres sortent
    const SPEED = 0.55;   // vitesse de descente (hauteur / s)
    const GRAVITY = 0.25;
    const VERMILLON = '#D2401C', ENCRE = '#121212';
    let W = 0, H = 0, parts = [], acc = 0, count = 0, raf = 0, last = 0, visible = false;

    // aléatoire déterministe : même rendu à chaque chargement (utile pour l'état statique)
    let seed = 20260925;
    const rand = () => {
      seed = (seed + 0x6D2B79F5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };

    const half = y => (y < TOP ? MOUTH : y < NECK ? MOUTH + (NECK_W - MOUTH) * ((y - TOP) / (NECK - TOP)) : NECK_W);

    function spawn() {
      const kept = count++ % KEEP_EVERY === 2;
      parts.push({
        u: kept ? (rand() * 2 - 1) * 0.3 : (rand() * 2 - 1) * 0.85,
        x: 0.5, y: -0.03, vx: 0, vy: SPEED,
        lost: !kept,
        ey: CALL + 0.01 + rand() * 0.04, // sortie juste après la ligne « Appel de vente »
        free: false, a: 1,
      });
    }

    function step(dt) {
      acc += dt;
      while (acc > SPAWN) { acc -= SPAWN; spawn(); }
      for (const p of parts) {
        if (!p.free) {
          p.y += p.vy * dt;
          p.x = 0.5 + p.u * half(p.y);
          if (p.lost && p.y >= p.ey) {
            p.free = true;
            const side = p.u === 0 ? 1 : Math.sign(p.u);
            p.vx = side * (0.1 + rand() * 0.1);
            p.vy = -0.04 - rand() * 0.04;
          }
          if (!p.lost && p.y > OUT) p.a -= dt * 3;
        } else {
          p.vy += GRAVITY * dt;
          p.x += p.vx * dt;
          p.y += p.vy * dt;
        }
      }
      parts = parts.filter(p => p.a > 0 && p.y < 1.08 && p.x > -0.06 && p.x < 1.06);
    }

    function draw() {
      ctx.clearRect(0, 0, W, H);
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = ENCRE;
      ctx.beginPath();
      ctx.moveTo((0.5 - MOUTH) * W, TOP * H);
      ctx.lineTo((0.5 - NECK_W) * W, NECK * H);
      ctx.lineTo((0.5 - NECK_W) * W, OUT * H);
      ctx.moveTo((0.5 + MOUTH) * W, TOP * H);
      ctx.lineTo((0.5 + NECK_W) * W, NECK * H);
      ctx.lineTo((0.5 + NECK_W) * W, OUT * H);
      ctx.stroke();

      ctx.setLineDash([3, 5]);
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'rgba(107, 102, 96, .7)';
      ctx.beginPath();
      ctx.moveTo(0, CALL * H);
      ctx.lineTo(W, CALL * H);
      ctx.stroke();
      ctx.setLineDash([]);

      const r = W < 420 ? 3 : 4;
      for (const p of parts) {
        ctx.globalAlpha = Math.max(0, Math.min(1, p.a));
        ctx.fillStyle = p.free ? VERMILLON : ENCRE;
        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function size() {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = rect.width; H = rect.height;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }

    function loop(t) {
      const dt = Math.min((t - last) / 1000 || 0, 0.05);
      last = t;
      step(dt);
      draw();
      raf = requestAnimationFrame(loop);
    }
    const play = () => { if (!raf && visible && !document.hidden) { last = performance.now(); raf = requestAnimationFrame(loop); } };
    const pause = () => { cancelAnimationFrame(raf); raf = 0; };

    // régime établi dès la première image (et état final si animations désactivées)
    for (let i = 0; i < 480; i++) step(1 / 60);
    new ResizeObserver(size).observe(canvas);
    size();

    if (!motion) return;
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; visible ? play() : pause(); }).observe(canvas);
    document.addEventListener('visibilitychange', () => (document.hidden ? pause() : play()));
  }

  // ---------------------------------------------------------------
  // MOTION
  // ---------------------------------------------------------------
  function initMotion() {
    gsap.registerPlugin(ScrollTrigger, SplitText, CustomEase);
    CustomEase.create('lossless', '0.22,1,0.36,1');
    gsap.defaults({ ease: 'lossless', duration: 1 });
    ScrollTrigger.config({ ignoreMobileResize: true });

    // Smooth scroll
    lenis = new Lenis({ lerp: 0.09, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(t => lenis.raf(t * 1000));
    gsap.ticker.lagSmoothing(0);

    anchors();
    const loaderDone = intro();
    heroScroll();
    loopSection();
    curtainScroll();
    proofStats();
    modelRing();
    installSection();
    header();
    progress();
    reveals();
    rises();
    simBackground();
    ctaRing();
    initCounters();
    if (finePointer) { cursor(); magnetic(); }

    ScrollTrigger.sort();
    ScrollTrigger.refresh();
    return loaderDone;
  }

  function anchors() {
    const ease = t => 1 - Math.pow(1 - t, 5);
    $$('a[href^="#"]').forEach(a => {
      a.addEventListener('click', e => {
        const id = a.getAttribute('href');
        if (id === '#') { e.preventDefault(); return; }
        const target = $(id);
        if (!target) return;
        e.preventDefault();
        lenis.scrollTo(id === '#top' ? 0 : target, { duration: 1.6, easing: ease });
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
      });
    });
  }

  // 0 — Intro : anneau dessiné, point posé, logo vers le header (≤ 1,2 s)
  function intro() {
    const loader = $('.loader');
    const mark = $('.loader__mark');
    const ring = $('.loader__ring'), dot = $('.loader__dot'), gap = $('.loader__gap');
    const target = $('.site-header .mark');
    const word = $('.site-header .logo__word');

    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    window.scrollTo(0, 0);
    lenis.stop();

    gsap.set(target, { autoAlpha: 0 });
    gsap.set(word, { autoAlpha: 0, x: -10 });
    gsap.set(ring, { strokeDasharray: '100 100', strokeDashoffset: 100 });
    gsap.set(dot, { scale: 0, y: -34, transformOrigin: '50% 50%' });
    gsap.set(gap, { attr: { r: 0 } });
    gsap.set(mark, { visibility: 'visible' });

    const tl = gsap.timeline();
    tl.to(ring, { strokeDashoffset: 0, duration: 0.62 }, 0.04)
      .to(dot, { scale: 1, y: 0, duration: 0.5 }, 0.34)
      .to(gap, { attr: { r: 16 }, duration: 0.5 }, 0.34)
      .add(() => {
        const a = mark.getBoundingClientRect();
        const b = target.getBoundingClientRect();
        gsap.to(mark, {
          x: b.left + b.width / 2 - (a.left + a.width / 2),
          y: b.top + b.height / 2 - (a.top + a.height / 2),
          scale: b.width / a.width,
          duration: 0.42,
        });
      }, 0.76)
      .to(loader, { backgroundColor: 'rgba(18,18,18,0)', duration: 0.38, ease: 'none' }, 0.8)
      .add(heroIn, 0.72)
      .add(() => {
        gsap.set(target, { autoAlpha: 1 });
        loader.remove();
        lenis.start();
      }, 1.2)
      .to(word, { autoAlpha: 1, x: 0, duration: 0.7 }, 1.12);
    return tl;
  }



  function heroIn() {
    const split = SplitText.create('.hero__title', { type: 'words', mask: 'words' });
    // une fois le titre en place, on retire les masques (sinon les jambages p, y, g sont rognés)
    gsap.from(split.words, { yPercent: 112, duration: 1.2, stagger: 0.09, onComplete: () => split.revert() });
    gsap.from(['.hero__tag', '.hero__promise', '.hero__text', '.hero__ctas'], {
      autoAlpha: 0, y: 20, duration: 1, stagger: 0.08, delay: 0.3,
    });
    gsap.from('.hero__film', { autoAlpha: 0, y: 40, scale: 0.96, duration: 1.3, delay: 0.4 });
    gsap.fromTo('.hero__stroke', { strokeDasharray: '100 100', strokeDashoffset: 100 }, { strokeDashoffset: 0, duration: 1.2 });
    gsap.from('.hero__ring svg', { rotation: -50, duration: 1.2 });
    gsap.from('.hero__dot-in', { scale: 0, transformOrigin: '50% 50%', duration: 0.9, delay: 0.45 });
    gsap.from('.nav a, .site-header .lang, .site-header .btn', { autoAlpha: 0, y: -10, duration: 0.8, stagger: 0.06, delay: 0.25 });
  }

  // 1 → 01 : l'Encre se retire en cercle vers le point vermillon
  function heroScroll() {
    const hero = $('.hero'), ring = $('.hero__ring'), svg = $('.hero__ring svg'), inner = $('.hero__inner'), dot = $('.hero__dot-wrap');
    const st = { p: 0 };
    let tl = null, leaving = false, geo = null, last = '';
    // signale le début / la fin du retrait : le film muet se met en pause,
    // le header coupe son flou (recalculé sinon à chaque image sur un fond qui bouge)
    const flag = () => {
      const l = st.p > 0.01;
      if (l === leaving) return;
      leaving = l;
      root.classList.toggle('hero-leaving', l);
      document.dispatchEvent(new CustomEvent('hero:leaving', { detail: l }));
    };
    // Géométrie mesurée une fois (chargement, redimensionnement) : aucune lecture de mise en page pendant le scroll.
    // Centre de l'anneau en coordonnées du hero (la rotation ne déplace pas ce centre).
    const measure = () => {
      geo = {
        cx: ring.offsetLeft + ring.offsetWidth / 2,
        cy: ring.offsetTop + ring.offsetHeight / 2,
        d: ring.offsetWidth * 0.38,
        w: hero.offsetWidth, h: hero.offsetHeight,
      };
    };

    // Le cercle se referme vers l'emplacement du point vermillon ; le point, lui (calque à part),
    // disparaît pendant le retrait pour ne pas rester posé sur la section 01.
    const clip = () => {
      const trig = tl && tl.scrollTrigger;
      flag();
      if (!trig || trig.progress < 0.0005) { if (last) { hero.style.clipPath = ''; last = ''; } return; }
      if (!geo) measure();
      const a = ((-45 + gsap.getProperty(ring, 'rotation') + gsap.getProperty(svg, 'rotation')) * Math.PI) / 180;
      const cx = geo.cx + geo.d * Math.cos(a);
      const cy = geo.cy + geo.d * Math.sin(a);
      const rMax = Math.hypot(Math.max(cx, geo.w - cx), Math.max(cy, geo.h - cy));
      const r = Math.max(0, rMax * (1 - st.p));
      const v = `circle(${r.toFixed(1)}px at ${cx.toFixed(1)}px ${cy.toFixed(1)}px)`;
      if (v !== last) { hero.style.clipPath = v; last = v; }
    };

    tl = gsap.timeline({
      defaults: { ease: 'none' },
      onUpdate: clip,
      scrollTrigger: {
        // « bottom bottom » : si le hero dépasse l'écran (mobile), on le lit en entier avant le retrait
        trigger: hero, start: 'bottom bottom', end: '+=100%',
        pin: true, pinSpacing: false, scrub: true,
        onRefreshInit: () => { geo = null; },
        onRefresh: () => { measure(); clip(); },
      },
    });
    tl.to(ring, { rotation: -140, duration: 1 }, 0)
      .to(st, { p: 1, duration: 0.82 }, 0)
      .to(inner, { yPercent: -6, autoAlpha: 0, duration: 0.45 }, 0.02)
      .to(dot, { scale: 0, duration: 0.3 }, 0.3);
  }


  // 02 — La boucle
  function loopSection() {
    const mm = gsap.matchMedia();

    mm.add('(min-width: 900px)', () => {
      const section = $('.loop');
      const arc = $('.loop__arc'), track = $('.loop__track'), dot = $('.loop__dot'), gap = $('.loop__gap');
      const ticks = $$('.loop__ticks circle'), labels = $$('.loop__labels li');
      const steps = $$('.loop__step'), final = $('.loop__final');
      const count = $('.loop__count'), cur = $('.loop__count-cur');
      const N = steps.length, A0 = -45, STEP = 360 / N;
      const s = { a: A0, w: 0.9, r: 2.4, g: 0 };
      let active = -1;

      const render = () => {
        const rad = (s.a * Math.PI) / 180;
        const x = (50 + 38 * Math.cos(rad)).toFixed(3);
        const y = (50 + 38 * Math.sin(rad)).toFixed(3);
        dot.setAttribute('cx', x); dot.setAttribute('cy', y); dot.setAttribute('r', s.r.toFixed(3));
        gap.setAttribute('cx', x); gap.setAttribute('cy', y); gap.setAttribute('r', s.g.toFixed(3));
        arc.setAttribute('stroke-dashoffset', (100 - (s.a - A0) / 3.6).toFixed(3));
        arc.setAttribute('stroke-width', s.w.toFixed(3));

        const idx = Math.min(N - 1, Math.max(0, Math.round((s.a - A0) / STEP)));
        if (idx !== active) {
          active = idx;
          labels.forEach((l, i) => l.classList.toggle('is-active', i === idx));
          ticks.forEach((t, i) => t.classList.toggle('is-done', i <= idx));
          cur.textContent = String(idx + 1).padStart(2, '0');
        }
      };

      gsap.set(track, { opacity: 1 });
      gsap.set(steps.slice(1), { opacity: 0, y: 28 });
      gsap.set(final, { opacity: 0, y: 28 });
      render();

      const tl = gsap.timeline({
        defaults: { ease: 'lossless' },
        onUpdate: render,
        scrollTrigger: {
          trigger: section, start: 'top top',
          end: () => '+=' + window.innerHeight * 5.4,
          pin: true, scrub: 0.8, invalidateOnRefresh: true,
        },
      });

      tl.to({}, { duration: 0.35 });
      for (let k = 1; k < N; k++) {
        const t = tl.duration();
        tl.to(s, { a: A0 + k * STEP, duration: 1 }, t)
          .to(steps[k - 1], { opacity: 0, y: -28, duration: 0.4 }, t + 0.05)
          .fromTo(steps[k], { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.55 }, t + 0.45)
          .to({}, { duration: 0.45 });
      }
      const t = tl.duration();
      tl.to(s, { a: A0 + 360, duration: 1.1 }, t)
        .to(steps[N - 1], { opacity: 0, y: -28, duration: 0.4 }, t + 0.05)
        .to(count, { opacity: 0, duration: 0.3 }, t + 0.05)
        .to(labels, { opacity: 0, duration: 0.5, stagger: 0.03 }, t + 0.4)
        .to(s, { w: 16, r: 13, g: 16, duration: 1 }, t + 1.1)
        .to(track, { opacity: 0, duration: 0.5 }, t + 1.1)
        .fromTo(final, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.6 }, t + 1.45)
        .to({}, { duration: 0.5 });

      return () => {
        // retour à l'état final (logo) défini dans le HTML
        dot.setAttribute('cx', '76.87'); dot.setAttribute('cy', '23.13'); dot.setAttribute('r', '13');
        gap.setAttribute('cx', '76.87'); gap.setAttribute('cy', '23.13'); gap.setAttribute('r', '16');
        arc.setAttribute('stroke-dashoffset', '0'); arc.setAttribute('stroke-width', '16');
        labels.forEach(l => l.classList.remove('is-active'));
        ticks.forEach(tk => tk.classList.remove('is-done'));
      };
    });

    mm.add('(max-width: 899px)', () => {
      const rail = $('.loop__rail'), fill = $('.loop__rail-fill'), rdot = $('.loop__rail-dot');
      const list = $('.loop__steps'), steps = $$('.loop__step');
      const arc = $('.loop__arc'), dot = $('.loop__dot'), gap = $('.loop__gap');

      gsap.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: { trigger: list, start: 'top 62%', end: 'bottom 62%', scrub: 0.5, invalidateOnRefresh: true },
      })
        .fromTo(fill, { scaleY: 0 }, { scaleY: 1 }, 0)
        .fromTo(rdot, { y: 0 }, { y: () => rail.offsetHeight }, 0);

      steps.forEach(step => {
        gsap.fromTo(step, { opacity: 0.22 }, {
          opacity: 1, ease: 'none',
          scrollTrigger: { trigger: step, start: 'top 72%', end: 'top 56%', scrub: true },
        });
      });

      gsap.timeline({
        scrollTrigger: { trigger: '.loop__visual', start: 'top 85%', end: 'center 50%', scrub: 0.6 },
      })
        .fromTo(arc, { attr: { 'stroke-dashoffset': 100 } }, { attr: { 'stroke-dashoffset': 0 }, ease: 'none', duration: 1 }, 0)
        .fromTo(dot, { scale: 0, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.35 }, 0.75)
        .fromTo(gap, { attr: { r: 0 } }, { attr: { r: 16 }, duration: 0.35 }, 0.75);

      gsap.from('.loop__final', {
        autoAlpha: 0, y: 20, duration: 1,
        scrollTrigger: { trigger: '.loop__final', start: 'top 90%', once: true },
      });
    });
  }

  // 04 — Timeline horizontale épinglée (desktop), empilée (mobile)
  function installSection() {
    const mm = gsap.matchMedia();
    const track = $('.steps'), line = $('.steps__line'), sdot = $('.steps__dot');
    const steps = $$('.step');

    mm.add('(min-width: 900px)', () => {
      const dist = () => Math.max(0, track.scrollWidth - document.documentElement.clientWidth);
      const mark = () => {
        const px = gsap.getProperty(sdot, 'x');
        steps.forEach(st => st.classList.toggle('is-on', px >= st.offsetLeft - line.offsetLeft - 4));
      };
      const tl = gsap.timeline({
        defaults: { ease: 'none' },
        onUpdate: mark,
        scrollTrigger: {
          trigger: '.install', start: 'top top',
          end: () => '+=' + dist() * 1.15,
          pin: true, scrub: 0.6, invalidateOnRefresh: true,
          onRefresh: mark,
        },
      });
      tl.to(track, { x: () => -dist(), duration: 1 }, 0)
        .fromTo(sdot, { x: 0 }, { x: () => line.offsetWidth, duration: 1 }, 0);
      return () => steps.forEach(st => st.classList.remove('is-on'));
    });

    mm.add('(max-width: 899px)', () => {
      steps.forEach(st => ScrollTrigger.create({ trigger: st, start: 'top 72%', toggleClass: 'is-on' }));
      return () => steps.forEach(st => st.classList.remove('is-on'));
    });
  }

  // Header : transparent sur le hero, Papier flouté ensuite, se cache en descendant
  function header() {
    const h = $('.site-header');
    let last = 0;
    ScrollTrigger.create({
      start: 0, end: 'max',
      onUpdate: self => {
        const y = self.scroll();
        h.classList.toggle('is-scrolled', y > 24);
        if (y > last + 3 && y > 240) h.classList.add('is-hidden');
        else if (y < last - 3 || y < 240) h.classList.remove('is-hidden');
        last = y;
      },
    });
  }

  function progress() {
    const bar = $('.progress__bar'), pdot = $('.progress__dot'), wrap = $('.progress');
    const desk = matchMedia('(min-width: 900px)');
    ScrollTrigger.create({
      start: 0, end: 'max',
      onUpdate: self => {
        if (desk.matches) {
          gsap.set(bar, { scaleX: 1 });
          gsap.set(pdot, { y: self.progress * wrap.offsetHeight });
        } else {
          gsap.set(bar, { scaleX: self.progress });
        }
      },
    });
  }

  // Titres ligne à ligne, paragraphes en fondu, groupes en cascade
  function reveals() {
    $$('[data-split]').forEach(el => {
      SplitText.create(el, {
        type: 'lines', mask: 'lines', linesClass: 'split-line', autoSplit: true,
        onSplit: self => gsap.from(self.lines, {
          yPercent: 112, duration: 1.1, stagger: 0.08,
          scrollTrigger: revealAt(el, 'top 86%'),
        }),
      });
    });
    $$('[data-fade]').forEach(el => {
      gsap.from(el, {
        autoAlpha: 0, y: 20, duration: 1,
        scrollTrigger: revealAt(el, 'top 88%'),
      });
    });
    $$('[data-stagger]').forEach(el => {
      gsap.from(el.children, {
        autoAlpha: 0, y: 40, duration: 1.1, stagger: 0.08,
        scrollTrigger: revealAt(el, 'top 85%'),
      });
    });
  }

  // 03 — Rideau avant / après
  // Desktop : le fond Encre glisse de la droite jusqu'au milieu au scroll, puis la poignée prend le relais.
  // Mobile : le bloc « Avec lossless » remonte comme un rideau.
  function curtainScroll() {
    const mm = gsap.matchMedia();
    mm.add('(min-width: 768px)', () => {
      const o = { v: 100 };
      curtain.set(100);
      gsap.to(o, {
        v: 50, ease: 'none',
        onUpdate: () => { if (!curtain.touched) curtain.set(o.v); },
        scrollTrigger: { trigger: '.curtain', start: 'top 80%', end: 'top 15%', scrub: 0.6 },
      });
      return () => curtain.set(50);
    });
    mm.add('(max-width: 767px)', () => {
      gsap.fromTo('.curtain__layer--after', { clipPath: 'inset(100% 0% 0% 0%)' }, {
        clipPath: 'inset(0% 0% 0% 0%)', ease: 'none',
        scrollTrigger: { trigger: '.curtain__layer--after', start: 'top 95%', end: 'top 40%', scrub: true },
      });
    });
  }

  // 06 — La preuve : 300 puis 30 défilent, le 0 arrive en dernier
  function proofStats() {
    const counts = $$('.proof__count');
    const zero = $('.proof__num--zero');
    const tl = gsap.timeline({
      scrollTrigger: { trigger: '.proof__stats', start: 'top 80%', once: true },
    });
    counts.forEach((el, i) => {
      const o = { v: 0 };
      const to = +el.dataset.to;
      el.textContent = '0';
      tl.to(o, {
        v: to, duration: i === 0 ? 1.4 : 1, ease: 'lossless',
        onUpdate: () => { el.textContent = fmt.format(Math.round(o.v)); },
      }, i === 0 ? 0.3 : '-=0.35');
    });
    gsap.set(zero, { autoAlpha: 0 });
    tl.to(zero, { autoAlpha: 1, duration: 0.9 }, '-=0.1');
  }

  // 07 — L'anneau qui se partage : 65 % noir, 35 % orange, une seule fois
  function modelRing() {
    const you = $('.model__arc--you'), us = $('.model__arc--us');
    const big = $('.model__big'), small = $('.model__small');
    const tags = $$('.model__tag');
    const o = { you: 0, us: 0 };
    const draw = () => {
      you.setAttribute('stroke-dasharray', `${o.you.toFixed(2)} 100`);
      us.setAttribute('stroke-dasharray', `${o.us.toFixed(2)} 100`);
    };

    draw();
    big.textContent = eur(0);
    small.textContent = T.ringStart;
    gsap.set(big, { color: '#D2401C' });
    gsap.set(tags, { autoAlpha: 0, y: 8 });

    gsap.timeline({ scrollTrigger: { trigger: '.model__ring', start: 'top 75%', once: true } })
      .to(o, { you: 65, duration: 1.2, ease: 'power2.inOut', onUpdate: draw }, 0)
      .to(o, { us: 35, duration: 0.6, ease: 'power2.out', onUpdate: draw }, 1.2)
      .to([big, small], { autoAlpha: 0, duration: 0.3 }, 0.25)
      .call(() => {
        big.textContent = pct(65);
        small.textContent = T.ringEnd;
      }, null, 0.56)
      .to([big, small], { autoAlpha: 1, duration: 0.45 }, 0.58)
      .to(big, { color: '#121212', duration: 0.6 }, 1.05)
      .to(tags[0], { autoAlpha: 1, y: 0, duration: 0.7 }, 1.0)
      .to(tags[1], { autoAlpha: 1, y: 0, duration: 0.7 }, 1.55);
  }

  // Bords qui remontent entre Papier et Encre
  function rises() {
    $$('.rise').forEach(sec => {
      gsap.fromTo($('.rise__bg', sec),
        { clipPath: 'inset(14vh 3.5vw 0vh 3.5vw round 44px 44px 0px 0px)' },
        {
          clipPath: 'inset(0vh 0vw 0vh 0vw round 0px 0px 0px 0px)', ease: 'none',
          scrollTrigger: { trigger: sec, start: 'top bottom', end: 'top 25%', scrub: true },
        });
    });
  }

  // Papier → Craie en fondu lié au scroll
  function simBackground() {
    gsap.fromTo('.sim__bg', { opacity: 0 }, {
      opacity: 1, ease: 'none',
      scrollTrigger: { trigger: '.sim', start: 'top 80%', end: 'top 20%', scrub: true },
    });
  }

  // CTA : le grand anneau revient et se referme
  function ctaRing() {
    gsap.timeline({
      scrollTrigger: { trigger: '.cta', start: 'top 75%', end: 'top 5%', scrub: 0.8 },
    })
      .fromTo('.cta__stroke', { attr: { 'stroke-dashoffset': 100 } }, { attr: { 'stroke-dashoffset': 0 }, ease: 'none', duration: 1 }, 0)
      .fromTo('.cta__ring svg', { rotation: -120 }, { rotation: 0, ease: 'none', duration: 1.05 }, 0)
      .fromTo('.cta__dot', { scale: 0, transformOrigin: '50% 50%' }, { scale: 1, duration: 0.3 }, 0.8)
      .fromTo('.cta__gap', { attr: { r: 0 } }, { attr: { r: 16 }, duration: 0.3 }, 0.8);
  }

  // Curseur : point vermillon avec inertie, grossit au survol
  function cursor() {
    root.classList.add('has-cursor');
    const c = $('.cursor'), d = $('.cursor__dot'), r = $('.cursor__ring');
    const dx = gsap.quickTo(d, 'x', { duration: 0.2, ease: 'power3' });
    const dy = gsap.quickTo(d, 'y', { duration: 0.2, ease: 'power3' });
    const rx = gsap.quickTo(r, 'x', { duration: 0.6, ease: 'lossless' });
    const ry = gsap.quickTo(r, 'y', { duration: 0.6, ease: 'lossless' });
    const sel = 'a, button, input, label, [data-cursor]';
    gsap.set(r, { scale: 0.3 });

    window.addEventListener('pointermove', e => {
      c.classList.add('is-visible');
      dx(e.clientX); dy(e.clientY); rx(e.clientX); ry(e.clientY);
    }, { passive: true });
    document.addEventListener('mouseleave', () => c.classList.remove('is-visible'));
    document.addEventListener('pointerover', e => {
      if (!e.target.closest(sel)) return;
      c.classList.add('is-hover');
      gsap.to(r, { scale: 1, duration: 0.6, overwrite: 'auto' });
      gsap.to(d, { scale: 1.6, duration: 0.6, overwrite: 'auto' });
    });
    document.addEventListener('pointerout', e => {
      const from = e.target.closest(sel);
      const to = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest(sel) : null;
      if (!from || from === to) return;
      c.classList.remove('is-hover');
      gsap.to(r, { scale: 0.3, duration: 0.6, overwrite: 'auto' });
      gsap.to(d, { scale: 1, duration: 0.6, overwrite: 'auto' });
    });
  }

  function magnetic() {
    $$('[data-magnetic]').forEach(el => {
      const label = $('.btn__label', el) || el;
      const q = (t, p) => gsap.quickTo(t, p, { duration: 0.8, ease: 'lossless' });
      const x = q(el, 'x'), y = q(el, 'y'), lx = q(label, 'x'), ly = q(label, 'y');
      el.addEventListener('pointermove', e => {
        const b = el.getBoundingClientRect();
        const mx = e.clientX - (b.left + b.width / 2);
        const my = e.clientY - (b.top + b.height / 2);
        x(mx * 0.3); y(my * 0.4); lx(mx * 0.12); ly(my * 0.16);
      });
      el.addEventListener('pointerleave', () => { x(0); y(0); lx(0); ly(0); });
    });
  }

  // ---------------------------------------------------------------
  // Film du hero : boucle muette chargée après l'intro ;
  // « Activer le son » le relance au début avec le son, dans la même carte.
  // À la fin du film (ou son coupé), retour à la boucle muette.
  // ---------------------------------------------------------------
  function initFilm() {
    const card = $('.hero__film'), video = $('.hero__film-video'), btn = $('[data-film-sound]');
    if (!card || !video || !btn) return;
    const label = $('.hero__film-label', btn), bar = $('.hero__film-bar', card);
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const saveData = !!(navigator.connection && navigator.connection.saveData);
    const autoplay = !reduce && !saveData;
    let visible = true, leaving = false, sound = false, raf = 0;

    const load = () => { if (!video.getAttribute('src')) video.src = video.dataset.src; };
    const play = () => { load(); const p = video.play(); if (p && p.catch) p.catch(() => {}); };
    const tick = () => {
      raf = 0;
      if (!sound) return;
      if (bar && video.duration) bar.style.transform = `scaleX(${video.currentTime / video.duration})`;
      raf = requestAnimationFrame(tick);
    };
    const setSound = on => {
      sound = on;
      video.muted = !on;
      video.loop = !on;
      card.classList.toggle('is-sound', on);
      btn.setAttribute('aria-pressed', String(on));
      label.textContent = on ? label.dataset.on : label.dataset.off;
      if (on && !raf) tick();
      if (!on && bar) bar.style.transform = '';
    };

    btn.addEventListener('click', () => {
      if (sound) { setSound(false); return; }
      load();
      video.currentTime = 0;
      setSound(true);
      play();
    });
    video.addEventListener('ended', () => {
      setSound(false);
      video.currentTime = 0;
      if (autoplay && visible && !leaving) play();
    });

    // boucle lancée après l'intro et le chargement de la page, pour ne rien ralentir
    const kick = () => setTimeout(() => { if (autoplay && visible && !leaving) play(); }, motion ? 1300 : 0);
    if (document.readyState === 'complete') kick(); else window.addEventListener('load', kick, { once: true });

    // hors de l'écran, ou boucle muette pendant le retrait du hero : pause (scroll plus fluide) ;
    // au retour : reprise (avec le son s'il était activé)
    const sync = () => {
      const run = visible && (sound || (autoplay && !leaving));
      if (!run) video.pause();
      else if (video.getAttribute('src') && video.paused) play();
    };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(([e]) => { visible = e.isIntersecting; sync(); }).observe(card);
    }
    document.addEventListener('hero:leaving', e => { leaving = e.detail; sync(); });
  }

  // ---------------------------------------------------------------
  // Démarrage
  // ---------------------------------------------------------------
  function start() {
    applyProblemStats();
    initFilm();
    // avant les animations : la FAQ se replie et change la hauteur de page
    initSim();
    initFaq();
    initCurtain();
    if (motion) {
      try {
        initMotion();
      } catch (err) {
        console.error('[lossless] animations désactivées :', err);
        root.classList.remove('motion', 'has-cursor');
        const loader = $('.loader');
        if (loader) loader.remove();
        if (lenis) lenis.destroy();
        ScrollTrigger.getAll().forEach(t => t.kill());
        gsap.globalTimeline.clear();
        gsap.set('*', { clearProps: 'all' });
      }
    } else {
      initCounters();
      const h = $('.site-header');
      const onScroll = () => h.classList.toggle('is-scrolled', window.scrollY > 24);
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
    initFunnel();
  }

  const fontsReady = document.fonts ? document.fonts.ready : Promise.resolve();
  Promise.race([fontsReady, new Promise(r => setTimeout(r, 2000))]).then(start);
})();
