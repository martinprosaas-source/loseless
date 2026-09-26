#!/usr/bin/env python3
"""Formulaire « Réserver un appel » (étape 1), en français et en anglais.

Les textes du formulaire vivent ici, dans les deux langues.
- `python3 tools/apply_form.py` réécrit le bloc du formulaire dans reserver.html (FR) ;
- tools/build_en.py utilise render('en') pour la page anglaise.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
START, END = '<!-- formulaire:debut -->', '<!-- formulaire:fin -->'

T = {
    'fr': {
        'eyebrow': '01 — Votre business',
        'title': 'Parlez-nous de votre business.',
        'lead': 'Quelques questions avant de choisir votre créneau. On arrive à l\'appel en connaissant déjà vos chiffres, et on va droit à l\'essentiel.',
        'name': 'Prénom et nom',
        'email': 'Email',
        'phone': 'Numéro WhatsApp',
        'phone_hint': 'C\'est là qu\'on vous joindra.',
        'dial_label': 'Indicatif du pays',
        'phone_ph': '6 12 34 56 78',
        'handle': 'Instagram ou site',
        'handle_ph': '@votremarque',
        'audience': 'Taille de votre audience',
        'price': 'Prix de votre accompagnement',
        'leads': 'Leads qualifiés par mois',
        'revenue': 'Chiffre d\'affaires mensuel',
        'choose': 'Choisir une tranche',
        'story': 'Où en êtes-vous aujourd\'hui&nbsp;?',
        'optional': 'Facultatif',
        'story_ph': 'Votre offre, votre process de vente, ce qui coince.',
        'submit': 'Prendre mon appel',
        'next': 'Étape suivante&nbsp;: choisir votre créneau.',
        'noscript': 'Le formulaire a besoin de JavaScript. Vous pouvez aussi <a class="link link--strong" href="https://cal.com/lossless/30min">réserver directement sur Cal.com</a>.',
        'default_dial': '+33',
        'dials': [
            ('+33', 'France'), ('+32', 'Belgique'), ('+41', 'Suisse'), ('+352', 'Luxembourg'),
            ('+1', 'Canada / USA'), ('+212', 'Maroc'), ('+213', 'Algérie'), ('+216', 'Tunisie'),
            ('+221', 'Sénégal'), ('+225', 'Côte d\'Ivoire'), ('+44', 'Royaume-Uni'), ('+34', 'Espagne'),
            ('+971', 'EAU'), ('+52', 'Mexique'), ('other', 'Autre pays'),
        ],
        'ranges': {
            'audience': ['Moins de 5&#8239;000', '5&#8239;000 à 20&#8239;000', '20&#8239;000 à 100&#8239;000', '100&#8239;000 à 500&#8239;000', 'Plus de 500&#8239;000'],
            'price': ['Moins de 1&#8239;000&nbsp;€', '1&#8239;000 à 3&#8239;000&nbsp;€', '3&#8239;000 à 6&#8239;000&nbsp;€', '6&#8239;000 à 10&#8239;000&nbsp;€', 'Plus de 10&#8239;000&nbsp;€'],
            'leads': ['Moins de 20', '20 à 50', '50 à 150', '150 à 500', 'Plus de 500'],
            'revenue': ['Moins de 10&#8239;000&nbsp;€', '10&#8239;000 à 30&#8239;000&nbsp;€', '30&#8239;000 à 100&#8239;000&nbsp;€', '100&#8239;000 à 300&#8239;000&nbsp;€', 'Plus de 300&#8239;000&nbsp;€'],
        },
    },
    'en': {
        'eyebrow': '01 — Your business',
        'title': 'Tell us about your business.',
        'lead': 'A few questions before you pick a time. We’ll come to the call already knowing your numbers, and get straight to the point.',
        'name': 'Full name',
        'email': 'Email',
        'phone': 'WhatsApp number',
        'phone_hint': 'This is how we’ll reach you.',
        'dial_label': 'Country code',
        'phone_ph': 'Phone number',
        'handle': 'Instagram or website',
        'handle_ph': '@yourbrand',
        'audience': 'Audience size',
        'price': 'Price of your program',
        'leads': 'Qualified leads per month',
        'revenue': 'Monthly revenue',
        'choose': 'Select a range',
        'story': 'Where are you at today?',
        'optional': 'Optional',
        'story_ph': 'Your offer, your sales process, what’s holding you back.',
        'submit': 'Book my call',
        'next': 'Next step: pick your time slot.',
        'noscript': 'This form needs JavaScript. You can also <a class="link link--strong" href="https://cal.com/lossless/30min">book directly on Cal.com</a>.',
        'default_dial': '+1',
        'dials': [
            ('+1', 'US / Canada'), ('+44', 'United Kingdom'), ('+33', 'France'), ('+32', 'Belgium'),
            ('+41', 'Switzerland'), ('+352', 'Luxembourg'), ('+212', 'Morocco'), ('+213', 'Algeria'),
            ('+216', 'Tunisia'), ('+221', 'Senegal'), ('+225', 'Côte d’Ivoire'), ('+34', 'Spain'),
            ('+971', 'UAE'), ('+52', 'Mexico'), ('other', 'Other country'),
        ],
        'ranges': {
            'audience': ['Under 5,000', '5,000 to 20,000', '20,000 to 100,000', '100,000 to 500,000', 'Over 500,000'],
            'price': ['Under €1,000', '€1,000 to €3,000', '€3,000 to €6,000', '€6,000 to €10,000', 'Over €10,000'],
            'leads': ['Under 20', '20 to 50', '50 to 150', '150 to 500', 'Over 500'],
            'revenue': ['Under €10,000', '€10,000 to €30,000', '€30,000 to €100,000', '€100,000 to €300,000', 'Over €300,000'],
        },
    },
}


def render(lang):
    t = T[lang]

    def label(fid, text, extra=''):
        return f'<label class="afield__label" for="{fid}">{text}{extra}</label>'

    def err(fid):
        return f'<p class="afield__error" id="{fid}-err" hidden></p>'

    def text_field(fid, name, key, kind='text', auto='', ph='', required=True, mode=''):
        attrs = f' autocomplete="{auto}"' if auto else ''
        attrs += f' inputmode="{mode}"' if mode else ''
        attrs += f' placeholder="{ph}"' if ph else ''
        attrs += ' required' if required else ''
        return (f'        <div class="afield">\n'
                f'          {label(fid, t[key])}\n'
                f'          <input class="afield__input" id="{fid}" name="{name}" type="{kind}"{attrs} aria-describedby="{fid}-err">\n'
                f'          {err(fid)}\n'
                f'        </div>\n')

    def range_field(fid, key):
        opts = ''.join(f'<option>{o}</option>' for o in t['ranges'][key])
        return (f'        <div class="afield">\n'
                f'          {label(fid, t[key])}\n'
                f'          <select class="afield__input afield__select" id="{fid}" name="{key}" required aria-describedby="{fid}-err">'
                f'<option value="" disabled selected>{t["choose"]}</option>{opts}</select>\n'
                f'          {err(fid)}\n'
                f'        </div>\n')

    optional = ' <span class="afield__opt">' + t['optional'] + '</span>'
    dials = ''.join(
        f'<option value="{code}"{" selected" if code == t["default_dial"] else ""}>'
        f'{code + " " if code != "other" else ""}{name}</option>'
        for code, name in t['dials']
    )

    return (
        f'{START}\n'
        f'  <section class="apply" id="apply" aria-labelledby="t-apply">\n'
        f'    <div class="wrap apply__wrap">\n'
        f'      <p class="eyebrow" data-fade>{t["eyebrow"]}</p>\n'
        f'      <h1 class="apply__title" id="t-apply" data-split>{t["title"]}</h1>\n'
        f'      <p class="apply__lead" data-fade>{t["lead"]}</p>\n'
        f'      <form class="apply__form" id="apply-form" novalidate data-fade>\n'
        f'       <div class="apply__grid">\n'
        + text_field('f-name', 'name', 'name', auto='name')
        + text_field('f-email', 'email', 'email', kind='email', auto='email', mode='email')
        + f'        <div class="afield">\n'
          f'          {label("f-phone", t["phone"])}\n'
          f'          <p class="afield__hint" id="f-phone-hint">{t["phone_hint"]}</p>\n'
          f'          <div class="afield__phone">\n'
          f'            <select class="afield__input afield__select" id="f-dial" name="dial" aria-label="{t["dial_label"]}" autocomplete="tel-country-code">{dials}</select>\n'
          f'            <input class="afield__input" id="f-phone" name="phone" type="tel" autocomplete="tel-national" inputmode="tel" placeholder="{t["phone_ph"]}" required aria-describedby="f-phone-hint f-phone-err">\n'
          f'          </div>\n'
          f'          {err("f-phone")}\n'
          f'        </div>\n'
        + text_field('f-handle', 'handle', 'handle', ph=t['handle_ph'], required=False)
        + range_field('f-audience', 'audience')
        + range_field('f-price', 'price')
        + range_field('f-leads', 'leads')
        + range_field('f-revenue', 'revenue')
        + f'        <div class="afield afield--full">\n'
          f'          {label("f-story", t["story"], optional)}\n'
          f'          <textarea class="afield__input afield__textarea" id="f-story" name="story" rows="3" placeholder="{t["story_ph"]}"></textarea>\n'
          f'        </div>\n'
          f'       </div>\n'
          f'       <div class="apply__actions">\n'
          f'         <button class="btn btn--primary btn--lg" type="submit" data-magnetic><span class="btn__label">{t["submit"]}</span></button>\n'
          f'         <p class="apply__next">{t["next"]}</p>\n'
          f'       </div>\n'
          f'      </form>\n'
          f'      <noscript><p class="apply__lead">{t["noscript"]}</p></noscript>\n'
          f'    </div>\n'
          f'  </section>\n'
          f'  {END}'
    )


def inject(path, lang):
    s = path.read_text()
    a, b = s.index(START), s.index(END) + len(END)
    path.write_text(s[:a] + render(lang) + s[b:])


if __name__ == '__main__':
    inject(ROOT / 'reserver.html', 'fr')
    print('✓ formulaire FR injecté dans reserver.html')
