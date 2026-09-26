/* LOSELESS — page « Réserver un appel » : étape 1 formulaire, étape 2 agenda Cal.com */
(() => {
  'use strict';

  // Lien Cal.com de l'événement, par langue de page (compte « lossless »).
  // TODO : créer dans Cal.com un événement en anglais (ex. « lossless/30min-en ») et le mettre ici,
  // sinon la page anglaise affiche le titre et la description français de l'événement.
  const CAL_LINKS = { fr: 'lossless/30min', en: 'lossless/30min' };
  const BRAND = '#D2401C';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  const LANG = (root.lang || 'fr').slice(0, 2) === 'en' ? 'en' : 'fr';
  const CAL_LINK = CAL_LINKS[LANG] || CAL_LINKS.fr;

  const T = {
    fr: {
      required: 'Ce champ est requis.',
      choose: 'Choisissez une tranche.',
      email: 'Cet email ne semble pas valide.',
      phone: 'Ce numéro ne semble pas valide.',
      notes: {
        phone: 'WhatsApp', handle: 'Instagram / site', audience: 'Audience', price: 'Prix de l\'accompagnement',
        leads: 'Leads qualifiés / mois', revenue: 'CA mensuel', story: 'Où il en est',
      },
    },
    en: {
      required: 'This field is required.',
      choose: 'Please select a range.',
      email: 'This email doesn’t look right.',
      phone: 'This number doesn’t look right.',
      notes: {
        phone: 'WhatsApp', handle: 'Instagram / website', audience: 'Audience', price: 'Program price',
        leads: 'Qualified leads / month', revenue: 'Monthly revenue', story: 'Where they’re at',
      },
    },
  }[LANG];

  const motion = root.classList.contains('motion') && window.gsap && window.SplitText && window.CustomEase;
  if (!motion) root.classList.remove('motion');
  if (motion) {
    gsap.registerPlugin(SplitText, CustomEase);
    CustomEase.create('lossless', '0.22,1,0.36,1');
    gsap.defaults({ ease: 'lossless', duration: 1 });
  }

  // ---------------------------------------------------------------
  // Étape 1 — formulaire
  // ---------------------------------------------------------------
  const form = $('#apply-form');
  const stepForm = $('#apply');
  const stepAgenda = $('#step-agenda');

  const fieldOf = el => el.closest('.afield');
  const setError = (el, msg) => {
    const f = fieldOf(el);
    const box = $('.afield__error', f);
    f.classList.toggle('is-invalid', !!msg);
    el.setAttribute('aria-invalid', msg ? 'true' : 'false');
    box.textContent = msg || '';
    box.hidden = !msg;
  };
  const check = el => {
    const v = el.value.trim();
    if (el.required && !v) return el.tagName === 'SELECT' ? T.choose : T.required;
    if (el.type === 'email' && v && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return T.email;
    if (el.type === 'tel' && v && v.replace(/\D/g, '').length < 6) return T.phone;
    return '';
  };
  const fields = $$('.afield__input[required]', form);

  // les erreurs s'affichent après une première tentative, puis se corrigent en direct
  let tried = false;
  fields.forEach(el => {
    const live = () => { if (tried || fieldOf(el).classList.contains('is-invalid')) setError(el, check(el)); };
    el.addEventListener('input', live);
    el.addEventListener('change', live);
    el.addEventListener('blur', () => { if (el.value.trim()) setError(el, check(el)); });
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    tried = true;
    let first = null;
    fields.forEach(el => {
      const msg = check(el);
      setError(el, msg);
      if (msg && !first) first = el;
    });
    if (first) { first.focus(); return; }
    goToAgenda(new FormData(form));
  });

  const labelOf = name => {
    const el = form.elements[name];
    if (!el) return '';
    if (el.tagName === 'SELECT') return el.selectedOptions[0] ? el.selectedOptions[0].textContent.trim() : '';
    return el.value.trim();
  };

  function notesFrom(data) {
    const dial = data.get('dial') === 'other' ? '' : data.get('dial') + ' ';
    const lines = [
      [T.notes.phone, (dial + data.get('phone')).trim()],
      [T.notes.handle, labelOf('handle')],
      [T.notes.audience, labelOf('audience')],
      [T.notes.price, labelOf('price')],
      [T.notes.leads, labelOf('leads')],
      [T.notes.revenue, labelOf('revenue')],
      [T.notes.story, labelOf('story')],
    ];
    return lines.filter(([, v]) => v).map(([k, v]) => `${k} : ${v}`.replace(' : ', LANG === 'fr' ? ' : ' : ': ')).join('\n');
  }

  // ---------------------------------------------------------------
  // Étape 2 — agenda Cal.com, pré-rempli avec les réponses
  // ---------------------------------------------------------------
  let calStarted = false;
  function startCal(prefill) {
    if (calStarted) return;
    calStarted = true;
    (function (C, A, L) { let p = function (a, ar) { a.q.push(ar); }; let d = C.document; C.Cal = C.Cal || function () { let cal = C.Cal; let ar = arguments; if (!cal.loaded) { cal.ns = {}; cal.q = cal.q || []; d.head.appendChild(d.createElement('script')).src = A; cal.loaded = true; } if (ar[0] === L) { const api = function () { p(api, arguments); }; const namespace = ar[1]; api.q = api.q || []; if (typeof namespace === 'string') { cal.ns[namespace] = cal.ns[namespace] || api; p(cal.ns[namespace], ar); p(cal, ['initNamespace', namespace]); } else p(cal, ar); return; } p(cal, ar); }; })(window, 'https://app.cal.com/embed/embed.js', 'init');

    Cal('init', '30min', { origin: 'https://app.cal.com' });
    Cal.config = Cal.config || {};
    Cal.config.forwardQueryParams = true;
    Cal.ns['30min']('inline', {
      elementOrSelector: '#cal-agenda',
      config: Object.assign({ layout: 'month_view', useSlotsViewOnSmallScreen: 'true', theme: 'light' }, prefill),
      calLink: CAL_LINK,
    });
    Cal.ns['30min']('ui', {
      theme: 'light',
      cssVarsPerTheme: { light: { 'cal-brand': BRAND }, dark: { 'cal-brand': BRAND } },
      hideEventTypeDetails: false,
      layout: 'month_view',
    });
    // le texte « Chargement… » disparaît dès que l'agenda est prêt
    Cal.ns['30min']('on', {
      action: 'linkReady',
      callback: () => { const l = $('.book__loading'); if (l) l.remove(); },
    });
  }

  function goToAgenda(data) {
    startCal({ name: data.get('name').trim(), email: data.get('email').trim(), notes: notesFrom(data) });

    const show = () => {
      stepForm.hidden = true;
      stepAgenda.hidden = false;
      const header = $('.site-header');
      header.classList.remove('is-dark');
      header.classList.add('is-scrolled');
      window.scrollTo(0, 0);
      $('#t-agenda').focus({ preventScroll: true });
    };
    if (!motion) { show(); return; }

    gsap.to(stepForm, {
      autoAlpha: 0, y: -24, duration: 0.5, ease: 'power2.in',
      onComplete: () => {
        show();
        gsap.set(stepForm, { clearProps: 'all' });
        const split = SplitText.create('.book__title', { type: 'lines', mask: 'lines', linesClass: 'split-line' });
        gsap.from(split.lines, { yPercent: 112, duration: 1.1, stagger: 0.08, onComplete: () => split.revert() });
        gsap.from(['.book__intro .eyebrow', '.book__lead', '.book__agenda'], { autoAlpha: 0, y: 20, stagger: 0.08, delay: 0.15 });
      },
    });
  }

  // ---------------------------------------------------------------
  // Apparition du formulaire
  // ---------------------------------------------------------------
  if (!motion) return;
  const start = () => {
    const split = SplitText.create('.apply__title', { type: 'lines', mask: 'lines', linesClass: 'split-line' });
    gsap.from(split.lines, { yPercent: 112, duration: 1.1, stagger: 0.08, delay: 0.1, onComplete: () => split.revert() });
    gsap.from($$('.apply [data-fade]'), { autoAlpha: 0, y: 20, stagger: 0.08, delay: 0.25 });
  };
  const fontsReady = document.fonts ? document.fonts.ready : Promise.resolve();
  Promise.race([fontsReady, new Promise(r => setTimeout(r, 1500))]).then(start);
})();
