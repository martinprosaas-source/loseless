#!/usr/bin/env python3
"""Génère la version anglaise du site (en/index.html, en/reserver.html)
à partir des pages françaises et de la table de traduction ci-dessous.

Usage : python3 tools/build_en.py

Si un texte français a changé et n'est plus trouvé, le script s'arrête
et indique lequel : il faut alors mettre à jour la paire correspondante.
"""
import html
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import apply_form  # noqa: E402  (textes du formulaire, FR + EN)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'en'

# ---------------------------------------------------------------------------
# Commun aux deux pages (header, footer, liens)
# ---------------------------------------------------------------------------
COMMON = [
    ('<html lang="fr">', '<html lang="en">'),
    ('<a class="skip" href="#contenu">Aller au contenu</a>', '<a class="skip" href="#contenu">Skip to content</a>'),
    ('aria-label="Navigation principale"', 'aria-label="Main navigation"'),
    ('>La boucle</a>', '>The loop</a>'),
    ('>Simulateur</a>', '>Simulator</a>'),
    ('>Le modèle</a>', '>The model</a>'),
    ('<nav class="lang" aria-label="Langue">', '<nav class="lang" aria-label="Language">'),
    ('<span class="lbl-long">Réserver un appel</span><span class="lbl-short">Réserver</span>',
     '<span class="lbl-long">Book a call</span><span class="lbl-short">Book</span>'),
    ('data-text="Réserver un appel">Réserver un appel</span>', 'data-text="Book a call">Book a call</span>'),
    ('aria-label="Liens légaux"', 'aria-label="Legal links"'),
    ('>Mentions légales</a>', '>Legal notice</a>'),
    ('<span class="sr-only"> (s\'ouvre dans un nouvel onglet)</span>', '<span class="sr-only"> (opens in a new tab)</span>'),
]

# ---------------------------------------------------------------------------
# Landing
# ---------------------------------------------------------------------------
INDEX = [
    # <head>
    ('<title>Loseless — Vos « pas le budget » rapportent aussi.</title>',
     '<title>Loseless — Your “no budget” leads still pay.</title>'),
    ('<meta name="description" content="Loseless installe une offre à petit prix pour les leads qui n\'ont pas le budget de votre accompagnement. Vous encaissez une commission, ils restent dans votre écosystème. Zéro coût d\'entrée.">',
     '<meta name="description" content="Loseless sets up a low-ticket offer for leads who can’t afford your program. You earn a commission, and they stay in your ecosystem. Zero upfront cost.">'),
    ('<meta property="og:title" content="Loseless — Vos « pas le budget » rapportent aussi.">',
     '<meta property="og:title" content="Loseless — Your “no budget” leads still pay.">'),
    ('<meta property="og:description" content="Chaque lead est étiqueté, chaque refus devient une commission.">',
     '<meta property="og:description" content="Every lead gets tagged. Every no becomes a commission.">'),
    ('aria-label="Loseless, retour en haut"', 'aria-label="Loseless, back to top"'),

    # Hero
    ('<p class="hero__tag">Agence d\'affiliation pour business high-ticket</p>',
     '<p class="hero__tag">Affiliate agency for high-ticket businesses</p>'),
    ('<h1 class="hero__title">Vos «&nbsp;pas le budget&nbsp;»<br class="br-desk"> rapportent aussi.</h1>',
     '<h1 class="hero__title">Your <span class="nobr">“no budget”</span> leads<br class="br-desk"> still pay.</h1>'),
    ('Chaque lead est étiqueté, chaque refus devient une commission.',
     'Every lead gets tagged. Every no becomes a commission.'),
    ('Après chaque appel, vos leads sont triés automatiquement. Ceux qui n\'ont pas le budget reçoivent une offre partenaire à leur portée. Vous touchez la commission, et ils reviennent vers votre accompagnement quand ils sont prêts.',
     'After every call, your leads are sorted automatically. Those who can’t afford your program get a partner offer within their budget. You earn the commission, and they come back to your program when they’re ready.'),
    ('>Calculer ce que je perds</a>', '>See what I’m losing</a>'),

    # 01 — Le problème
    ('01 — Le problème', '01 — The problem'),
    ('Un <span class="nobr">«&nbsp;pas le budget&nbsp;»</span> n\'est pas un&nbsp;non.',
     '<span class="nobr">“No budget”</span> doesn’t mean&nbsp;no.'),
    ('<span class="stat__num" data-count="" data-suffix="&nbsp;%">80&nbsp;%</span>',
     '<span class="stat__num" data-count="" data-suffix="%">80%</span>'),
    ('des leads en appel de vente repartent sans rien acheter, dont <span class="stat__y">70&nbsp;%</span> pour une question de budget.',
     'of leads on sales calls leave without buying anything, <span class="stat__y">70%</span> of them because of budget.'),
    ('Vous avez payé pour les faire venir&nbsp;: publicité, contenu, temps de closing. Quand ils disent «&nbsp;pas le budget&nbsp;», l\'appel se termine et tout cet investissement repart avec eux. Le mois suivant, ils achètent une formation moins chère. Chez quelqu\'un d\'autre, qui touche la commission à votre place.',
     'You paid to bring them in: ads, content, closing time. When they say “no budget”, the call ends and your whole investment walks out the door with them. The next month, they buy a cheaper course. From someone else, who pockets the commission instead of you.'),
    ('>Leads acquis</span>', '>Leads acquired</span>'),
    ('funnel__l--call">Appel de vente</span>', 'funnel__l--call">Sales call</span>'),
    ('Repartent<br class="br-mob"> sans rien', 'Leave<br class="br-mob"> with nothing'),
    ('funnel__l--sale">Vente</span>', 'funnel__l--sale">Sale</span>'),
    ('Illustration&nbsp;: des leads entrent dans un entonnoir de vente. Juste après l\'appel de vente, environ huit sur dix en sortent par les côtés sans rien acheter&nbsp;; seuls quelques-uns vont jusqu\'à la vente.',
     'Illustration: leads enter a sales funnel. Right after the sales call, about eight in ten drop out the sides without buying anything; only a few make it to the sale.'),

    # 02 — La boucle
    ('02 — La boucle', '02 — The loop'),
    ('Une boucle, pas un entonnoir.', 'A loop, not a funnel.'),
    ('<h3>Lead</h3><p>Il a vu votre contenu, il a rempli le formulaire. Vous avez payé pour qu\'il arrive jusqu\'ici.</p>',
     '<h3>Lead</h3><p>They saw your content and filled in the form. You paid to get them this far.</p>'),
    ('<h3>Qualification</h3><p>Formulaire ou appel&nbsp;: il vous dit s\'il a le budget pour votre accompagnement.</p>',
     '<h3>Qualification</h3><p>Form or call: they tell you whether they have the budget for your program.</p>'),
    ('<h3>«&nbsp;Pas le budget&nbsp;»</h3><p>Aujourd\'hui, c\'est ici qu\'il disparaît. Avec loseless, il est redirigé vers votre offre low-ticket.</p>',
     '<h3>“No budget”</h3><p>Today, this is where they disappear. With loseless, they’re redirected to your low-ticket offer.</p>'),
    ('<h3>Offre low-ticket</h3><p>Une page et une vidéo dédiées lui présentent une offre à sa portée. Nos setters l\'appellent et concluent la vente.</p>',
     '<h3>Low-ticket offer</h3><p>A dedicated page and video present an offer they can afford. Our setters call them and close the sale.</p>'),
    ('<h3>Vente encaissée</h3><p>Il achète. Vous gardez au moins 65&nbsp;% de chaque vente, sans avoir à vous en occuper.</p>',
     '<h3>Cash collected</h3><p>They buy. You keep at least 65% of every sale, without lifting a finger.</p>'),
    ('<h3>Nurturing</h3><p>Il reste dans votre écosystème. Il progresse, et vous gardez le lien.</p>',
     '<h3>Nurturing</h3><p>They stay in your ecosystem. They make progress, and you stay connected.</p>'),
    ('<h3>Upsell high-ticket</h3><p>Quand il est prêt, il revient vers votre accompagnement. Cette fois, avec le budget.</p>',
     '<h3>High-ticket upsell</h3><p>When they’re ready, they come back to your program. This time, with the budget.</p>'),
    ('>«&nbsp;Pas le budget&nbsp;»</li>', '>“No budget”</li>'),
    ('>Offre low-ticket</li>', '>Low-ticket offer</li>'),
    ('>Vente encaissée</li>', '>Cash collected</li>'),
    ('>Upsell high-ticket</li>', '>High-ticket upsell</li>'),
    ('Rien ne sort de la boucle.', 'Nothing leaks out of the loop.'),

    # 03 — Ce que ça change
    ('03 — Ce que ça change', '03 — What changes'),
    ('Chaque lead mène quelque part.', 'Every lead goes somewhere.'),
    ('>Aujourd\'hui</p>', '>Today</p>'),
    ('>Avec loseless</p>', '>With loseless</p>'),
    ('>Le lead sans budget</p>', '>The no-budget lead</p>'),
    ('>Votre revenu</p>', '>Your revenue</p>'),
    ('>La suite</p>', '>What happens next</p>'),
    ('>Il repart.</p>', '>They walk away.</p>'),
    ('>Il achète.</p>', '>They buy.</p>'),
    ('<p class="curtain__big">0&nbsp;€</p>', '<p class="curtain__big">€0</p>'),
    ('<p class="curtain__big">65&nbsp;%</p>', '<p class="curtain__big">65%</p>'),
    ('>Il achète ailleurs.</p>', '>They buy elsewhere.</p>'),
    ('>Il revient chez vous.</p>', '>They come back to&nbsp;you.</p>'),
    ('Votre offre low&#8209;ticket, présentée par nos setters.', 'Your low&#8209;ticket offer, pitched by our setters.'),
    ('minimum sur chaque vente. Vous n\'avez rien à gérer.', 'minimum on every sale. Nothing for you to manage.'),
    ('Quand il est prêt, pour votre high&#8209;ticket.', 'When they’re ready, for your high&#8209;ticket program.'),
    ('aria-label="Comparer aujourd\'hui et avec loseless"', 'aria-label="Compare today with loseless"'),
    ('aria-valuetext="Moitié-moitié"', 'aria-valuetext="Half and half"'),
    ('>Combien ça représente pour vous&nbsp;?</a>', '>How much is that worth to you?</a>'),

    # 04 — Installation
    ('04 — Comment on l\'installe', '04 — How we set it up'),
    ('On installe. Vous encaissez.', 'We set it up. You get paid.'),
    ('<h3>Cadrage</h3>\n            <p>On étudie votre écosystème&nbsp;: votre audience, vos leads, votre offre high-ticket. Ensemble, on définit votre offre low-ticket et le seuil de budget qui déclenche la redirection.</p>',
     '<h3>Scoping</h3>\n            <p>We study your ecosystem: your audience, your leads, your high-ticket offer. Together, we define your low-ticket offer and the budget threshold that triggers the redirect.</p>'),
    ('<h3>Branchement</h3>\n            <p>On se branche sur votre formulaire. Sous votre seuil de budget, le lead est redirigé vers votre page low-ticket et sa vidéo, puis transmis directement à nos setters.</p>',
     '<h3>Integration</h3>\n            <p>We plug into your application form. Below your budget threshold, the lead is redirected to your low-ticket page and its video, then handed straight to our setters.</p>'),
    ('<h3>Lancement</h3>\n            <p>Nos setters appellent chaque lead et concluent les ventes. Si vous voulez accélérer, une story avec le lien suffit.</p>',
     '<h3>Launch</h3>\n            <p>Our setters call every lead and close the sales. Want to speed things up? One story with the link is all it takes.</p>'),
    ('<h3>Suivi et remontée</h3>\n            <p>On suit les résultats avec vous et on ajuste. Les acheteurs prêts pour votre accompagnement vous sont renvoyés.</p>',
     '<h3>Tracking &amp; hand-back</h3>\n            <p>We track the results with you and fine-tune. Buyers who are ready for your program are sent back to you.</p>'),

    # 05 — Simulateur
    ('05 — Simulateur', '05 — Simulator'),
    ('Ceux que vous laissez partir.', 'The ones you let walk away.'),
    ('Deux chiffres de votre activité suffisent.', 'Two numbers from your business are all it takes.'),
    ('>Leads qualifiés par mois</label>', '>Qualified leads per month</label>'),
    ('>Part qui n\'a pas le budget</label>', '>Share without the budget</label>'),
    ('<output id="o-nobudget" for="s-nobudget">50&nbsp;%</output>', '<output id="o-nobudget" for="s-nobudget">50%</output>'),
    ('Repartent sans rien / mois', 'Leave with nothing / month'),
    ('soit 1&#8239;200 leads par an.', 'that’s 1,200 leads a year.'),
    ('1 point = 5 leads', '1 dot = 5 leads'),
    ('Chaque point orange est une personne qui voulait votre accompagnement. Aujourd\'hui, elle repart sans rien acheter.',
     'Every orange dot is someone who wanted your program. Today, they leave without buying anything.'),
    ('Combien ils pourraient vous rapporter&nbsp;? Ça dépend de votre audience et de votre offre. On le calcule avec vous, sur vos vrais chiffres.',
     'How much could they bring in? It depends on your audience and your offer. We’ll work it out with you, using your real numbers.'),
    ('data-text="Calculer mon potentiel">Calculer mon potentiel</span>', 'data-text="Calculate my potential">Calculate my potential</span>'),

    # 06 — La preuve
    ('06 — La preuve', '06 — Proof'),
    ('Déjà en place chez Gaspard Grosjean.', 'Already live with Gaspard Grosjean.'),
    ('Fondateur d\'ECOM&nbsp;BOSS, l\'un des plus gros infopreneurs e-commerce français. Plus de 70&nbsp;000 abonnés sur Instagram.',
     'Founder of ECOM&nbsp;BOSS, one of France’s biggest e-commerce educators. Over 70,000 followers on Instagram.'),
    ('>ventes low-ticket</span>', '>low-ticket sales</span>'),
    ('<span class="proof__suffix">&nbsp;jours</span>', '<span class="proof__suffix">&nbsp;days</span>'),
    ('>pour y arriver</span>', '>to get there</span>'),
    ('>setter recruté de son côté</span>', '>setters hired on his end</span>'),
    ('«&nbsp;[Citation de Gaspard, 2 phrases maximum]&nbsp;»', '“[Gaspard’s quote, 2 sentences max]”'),
    ('<span>Gaspard Grosjean, fondateur d\'ECOM&nbsp;BOSS</span>', '<span>Gaspard Grosjean, founder of ECOM&nbsp;BOSS</span>'),

    # 07 — Le modèle
    ('07 — Le modèle', '07 — The model'),
    ('Zéro coût d\'entrée.', 'Zero upfront cost.'),
    ('On gagne seulement si vous gagnez.', 'We only win when you win.'),
    ('<span class="model__big">65&nbsp;%</span><span class="model__small">pour vous, sur chaque vente</span>',
     '<span class="model__big">65%</span><span class="model__small">for you, on every sale</span>'),
    ('model__tag--you">Vous</span>', 'model__tag--you">You</span>'),
    ('loseless<br class="br-desk"> et setters', 'loseless<br class="br-desk"> &amp; setters'),
    ('Aucun coût pour démarrer. Ensuite, sur chaque vente&nbsp;: 65&nbsp;% pour vous, 35&nbsp;% pour loseless et les setters.',
     'Nothing to pay to get started. After that, on every sale: 65% for you, 35% for loseless and the setters.'),
    ('<dt>Ce qu\'on prend en charge</dt><dd>La page, la vidéo, les setters et le suivi. Vous n\'avez rien à recruter ni à gérer.</dd>',
     '<dt>What we handle</dt><dd>The page, the video, the setters and the follow-up. Nothing for you to hire or manage.</dd>'),
    ('<dt>Votre image</dt><dd>L\'offre est vendue sous votre nom. Vous validez tout avant le lancement&nbsp;: l\'offre, la page et le discours des setters.</dd>',
     '<dt>Your brand</dt><dd>The offer is sold under your name. You approve everything before launch: the offer, the page and the setters’ script.</dd>'),
    ('<dt>Si l\'offre ne vend pas</dt><dd>On ne gagne rien, et vous ne perdez rien.</dd>',
     '<dt>If the offer doesn’t sell</dt><dd>We earn nothing, and you lose nothing.</dd>'),

    # 08 — FAQ
    ('Vos questions, sans détour.', 'Your questions, straight answers.'),
    ('<p class="faq__more">Une autre question&nbsp;?</p>', '<p class="faq__more">Another question?</p>'),
    ('Ça cannibalise mon high&#8209;ticket&nbsp;?', 'Will it cannibalize my high&#8209;ticket sales?'),
    ('Non. Seuls les leads sous votre seuil de budget sont redirigés. Ceux qui peuvent se payer votre accompagnement continuent vers votre équipe, comme aujourd\'hui. Et les acheteurs du low&#8209;ticket deviennent vos meilleurs prospects pour votre high&#8209;ticket.',
     'No. Only leads below your budget threshold are redirected. Those who can afford your program keep going to your team, just like today. And your low&#8209;ticket buyers become your best prospects for your high&#8209;ticket offer.'),
    ('Combien de temps pour l\'installer&nbsp;?', 'How long does setup take?'),
    ('[À COMPLÉTER&nbsp;: délai de mise en place]', '[TO BE COMPLETED: setup time]'),
    ('Qu\'est-ce que je dois faire, moi&nbsp;?', 'What do I actually have to do?'),
    ('Presque rien. Vous validez l\'offre, la page et le discours des setters avant le lancement. Ensuite, si vous voulez accélérer, une story avec le lien suffit.',
     'Almost nothing. You approve the offer, the page and the setters’ script before launch. After that, if you want to speed things up, one story with the link is all it takes.'),
    ('Qui sont les setters&nbsp;?', 'Who are the setters?'),
    ('Des setters formés par nous, qui appellent vos leads et concluent les ventes. Ils sont payés à la commission&nbsp;: ils ne gagnent que s\'ils vendent.',
     'Setters we train ourselves, who call your leads and close the sales. They’re paid on commission: they only earn when they sell.'),
    ('Qui crée l\'offre low&#8209;ticket&nbsp;?', 'Who creates the low&#8209;ticket offer?'),
    ('Comment vous êtes rémunérés&nbsp;?', 'How do you get paid?'),
    ('Uniquement sur les ventes. Rien à payer pour démarrer, et vous gardez au moins 65&nbsp;% de chaque vente. Si ça ne vend pas, on ne gagne rien.',
     'Only on sales. Nothing to pay upfront, and you keep at least 65% of every sale. If it doesn’t sell, we earn nothing.'),
    ('Est-ce que je m\'engage sur une durée&nbsp;?', 'Is there a minimum commitment?'),
    ('Pour quels infopreneurs ça marche&nbsp;?', 'Who is it for?'),
    ('Ceux qui vendent un accompagnement high&#8209;ticket et reçoivent régulièrement des leads qui n\'ont pas le budget.',
     'Coaches and course creators who sell a high&#8209;ticket program and regularly get leads who can’t afford it.'),
    ('[À COMPLÉTER&nbsp;: critère minimum, par exemple un nombre de leads par mois]',
     '[TO BE COMPLETED: minimum requirement, e.g. number of leads per month]'),
    ('[À COMPLÉTER]', '[TO BE COMPLETED]'),

    # CTA final
    ('Fermez la boucle.', 'Close the loop.'),
    ('Un appel suffit pour savoir si Loseless est fait pour votre business.',
     'One call is all it takes to know if Loseless is right for your business.'),
]

# ---------------------------------------------------------------------------
# Page « Réserver un appel »
# ---------------------------------------------------------------------------
BOOK = [
    ('<title>Réserver un appel — Loseless</title>', '<title>Book a call — Loseless</title>'),
    ('<meta name="description" content="Réservez un appel découverte de 30 minutes avec loseless : on regarde vos chiffres ensemble et on calcule votre potentiel.">',
     '<meta name="description" content="Book a 30-minute discovery call with loseless: we go through your numbers together and calculate your potential.">'),
    ('<meta property="og:title" content="Réserver un appel — Loseless">', '<meta property="og:title" content="Book a call — Loseless">'),
    ('<meta property="og:description" content="On calcule votre potentiel, sur vos vrais chiffres.">',
     '<meta property="og:description" content="We calculate your potential, using your real numbers.">'),
    ('aria-label="Loseless, retour à l\'accueil"', 'aria-label="Loseless, back to home"'),
    ('<p class="eyebrow">02 — Votre créneau</p>', '<p class="eyebrow">02 — Your time slot</p>'),
    ('Calculons votre potentiel.', 'Let’s calculate your potential.'),
    ('Choisissez un créneau. On regarde vos chiffres ensemble et on vous dit franchement si loseless peut fonctionner chez vous.',
     'Pick a time slot. We’ll go through your numbers together and tell you honestly whether loseless can work for you.'),
    ('aria-label="Agenda de réservation"', 'aria-label="Booking calendar"'),
    ('Chargement de l\'agenda…', 'Loading the calendar…'),
    ('L\'agenda ne s\'affiche pas&nbsp;?', 'Calendar not showing?'),
    ('>Réserver directement sur Cal.com<', '>Book directly on Cal.com<'),
]

# Liens et chemins : les pages anglaises vivent dans en/
PATHS = [
    (r'(href|src)="(styles\.css|main\.js|reserver\.js|favicon\.svg|vendor/)', r'\1="../\2'),
]


def switcher(page):
    return (
        '<nav class="lang" aria-label="Language">\n'
        '      <span class="lang__thumb" aria-hidden="true"></span>\n'
        f'      <a class="lang__opt" href="../{page}" hreflang="fr" lang="fr"><span class="sr-only">Français</span><span aria-hidden="true">FR</span></a>\n'
        f'      <a class="lang__opt" href="{page}" hreflang="en" lang="en" aria-current="page"><span class="sr-only">English</span><span aria-hidden="true">EN</span></a>\n'
        '    </nav>'
    )


def build(name, pairs):
    src = (ROOT / name).read_text()
    out = src
    # le formulaire de réservation a ses propres textes FR + EN (tools/apply_form.py)
    if apply_form.START in out:
        i, j = out.index(apply_form.START), out.index(apply_form.END) + len(apply_form.END)
        out = out[:i] + apply_form.render('en') + out[j:]
    missing = []
    # les chaînes les plus longues d'abord, pour ne pas en casser une plus courte
    common = set(COMMON)
    for fr, en in sorted(COMMON + pairs, key=lambda p: -len(p[0])):
        if fr not in out:
            if (fr, en) not in common:  # les éléments communs ne sont pas tous sur chaque page
                missing.append(fr)
            continue
        out = out.replace(fr, en)
    if missing:
        print(f'\n✗ {name} : textes français introuvables (traduction à mettre à jour) :')
        for m in missing:
            print('   -', m[:110])
        sys.exit(1)

    # sélecteur de langue et balises hreflang
    out = re.sub(r'<nav class="lang" aria-label="Language">.*?</nav>', switcher(name), out, count=1, flags=re.S)
    out = out.replace(f'<link rel="alternate" hreflang="fr" href="{name}">', f'<link rel="alternate" hreflang="fr" href="../{name}">')
    out = out.replace(f'<link rel="alternate" hreflang="en" href="en/{name}">', f'<link rel="alternate" hreflang="en" href="{name}">')
    for pat, rep in PATHS:
        out = re.sub(pat, rep, out)

    # contrôle : plus aucun texte visible en français
    visible = re.sub(r'<!--.*?-->|<script.*?</script>|<style.*?</style>|<svg.*?</svg>', ' ', out, flags=re.S)
    attrs = ' '.join(re.findall(r'(?:aria-label|aria-valuetext|content|data-text|title)="([^"]*)"', visible))
    text = html.unescape(re.sub(r'<[^>]+>', ' ', visible)) + ' ' + html.unescape(attrs)
    text = text.replace('Français', '').replace('Côte d’Ivoire', '')  # noms propres
    suspects = re.findall(r"[^\s]*[éèêàçùûôî«»][^\s]*|\b(?:le|la|les|des|vous|votre|pour|avec|une|est)\b", text)
    if suspects:
        print(f'\n⚠ {name} : mots qui ressemblent à du français :', sorted(set(suspects)))

    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(out)
    print(f'✓ en/{name}')


build('index.html', INDEX)
build('reserver.html', BOOK)
