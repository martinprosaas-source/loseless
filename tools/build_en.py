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
    ('>Comment ça marche</a>', '>How it works</a>'),
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
     '<h1 class="hero__title">Your <span class="nobr">“no budget”</span><br class="br-desk"> leads still pay.</h1>'),
    ('Nos setters leur vendent une offre <span class="nobr">low-ticket</span>, sous votre nom. Vous touchez 65&nbsp;% de chaque vente.</p>',
     'Our setters sell them a <span class="nobr">low-ticket</span> offer, under your name. You get 65% of every sale.</p>'),
    ('>Calculer ce que je perds</a>', '>See what I’m losing</a>'),
    ('<!-- Film : boucle muette dans le hero ; « Activer le son » le relance au début, avec le son -->',
     '<!-- Film: muted loop in the hero; “Turn on sound” restarts it from the beginning, with sound -->'),
    ('aria-label="Film Loseless (55 secondes)"', 'aria-label="Loseless film (55 seconds, in French)"'),
    ('data-on="Couper le son" data-off="Activer le son">Activer le son</span>',
     'data-on="Mute" data-off="Turn on sound (French)">Turn on sound (French)</span>'),

    # Chiffres (après le hero)
    ('>Loseless en chiffres</h2>', '>Loseless in numbers</h2>'),
    ('<span data-count="150000" data-suffix="&nbsp;€">150&nbsp;000&nbsp;€</span>',
     '<span data-count="150000" data-prefix="€">€150,000</span>'),
    ('>Chiffre d\'affaires généré</span>', '>Revenue generated</span>'),
    ('>pour nos partenaires, avec leur offre low&#8209;ticket.</span>', '>for our partners, with their low&#8209;ticket offer.</span>'),
    ('<span class="figure__kicker">Ventes</span>', '<span class="figure__kicker">Sales</span>'),
    ('>ventes low&#8209;ticket conclues par nos setters.</span>', '>low&#8209;ticket sales closed by our setters.</span>'),
    ('<span class="figure__kicker">Partenaires</span>', '<span class="figure__kicker">Partners</span>'),
    ('>business high&#8209;ticket nous font déjà confiance.</span>', '>high&#8209;ticket businesses already trust us.</span>'),
    ('Dont notre premier partenaire, Gaspard Grosjean, fondateur d\'ECOM&nbsp;BOSS.',
     'Including our first partner, Gaspard Grosjean, founder of ECOM&nbsp;BOSS.'),
    ('Chiffres au 23&nbsp;octobre 2026', 'Figures as of October 23, 2026'),
    ('data-text="Devenir le prochain partenaire">Devenir le prochain partenaire</span>',
     'data-text="Become our next partner">Become our next partner</span>'),

    # 01 — Le problème
    ('01 — Le problème', '01 — The problem'),
    ('Un <span class="nobr">«&nbsp;pas le budget&nbsp;»</span> n\'est pas un&nbsp;non.',
     '<span class="nobr">“No budget”</span> doesn’t mean&nbsp;no.'),
    ('<span class="stat__num" data-count="" data-suffix="&nbsp;%">80&nbsp;%</span>',
     '<span class="stat__num" data-count="" data-suffix="%">80%</span>'),
    ('des leads en appel de vente repartent sans rien acheter. Et le prix est l\'une des premières raisons de refus.',
     'of leads on sales calls leave without buying anything. And price is one of the top reasons they say no.'),
    ('Taux de closing moyen de 20&nbsp;%, tous secteurs confondus. Source&nbsp;: <a', 'Average close rate of 20%, across all industries. Source: <a'),
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
    ('04 — Ce que ça change', '04 — What changes'),
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
    ('Une offre à sa portée, construite pour votre audience et présentée par nos setters.', 'An offer within their budget, built for your audience and pitched by our setters.'),
    ('minimum sur chaque vente. Vous n\'avez rien à gérer.', 'minimum on every sale. Nothing for you to manage.'),
    ('Quand il est prêt, pour votre high&#8209;ticket.', 'When they’re ready, for your high&#8209;ticket program.'),
    ('aria-label="Comparer aujourd\'hui et avec loseless"', 'aria-label="Compare today with loseless"'),
    ('aria-valuetext="Moitié-moitié"', 'aria-valuetext="Half and half"'),
    ('>Combien ça représente pour vous&nbsp;?</a>', '>How much is that worth to you?</a>'),

    # 04 — Installation
    ('05 — Comment on l\'installe', '05 — How we set it up'),
    ('On installe. Vous encaissez.', 'We set it up. You get paid.'),
    ('<h3>Cadrage</h3>\n            <p>On étudie votre audience, vos leads et votre offre high-ticket. Puis on construit votre offre low-ticket&nbsp;: l\'offre, la page, la vidéo, l\'outil et le workshop. Vous validez tout.</p>',
     '<h3>Scoping</h3>\n            <p>We study your audience, your leads and your high-ticket offer. Then we build your low-ticket offer: the offer, the page, the video, the tool and the workshop. You approve everything.</p>'),
    ('<h3>Branchement</h3>\n            <p>On se branche sur votre formulaire, ou vos pubs, votre VSL et vos influenceurs envoient directement vers votre page low-ticket, avec un lien suivi par source. Chaque lead arrive chez nos setters avec sa provenance.</p>',
     '<h3>Integration</h3>\n            <p>We plug into your application form, or your ads, your VSL and your influencers send people straight to your low-ticket page, with a tracked link for each source. Every lead reaches our setters with its origin.</p>'),
    ('<h3>Lancement</h3>\n            <p>Nos setters, recrutés, formés et managés par nous, appellent chaque lead et concluent les ventes. Si vous voulez accélérer, une story avec le lien suffit.</p>',
     '<h3>Launch</h3>\n            <p>Our setters, hired, trained and managed by us, call every lead and close the sales. Want to speed things up? One story with the link is all it takes.</p>'),
    ('<h3>Suivi et remontée</h3>\n            <p>On suit les résultats avec vous et on ajuste. Les acheteurs prêts pour votre accompagnement vous sont renvoyés.</p>',
     '<h3>Tracking &amp; hand-back</h3>\n            <p>We track the results with you and fine-tune. Buyers who are ready for your program are sent back to you.</p>'),

    # 05 — Simulateur
    ('06 — Simulateur', '06 — Simulator'),
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
    ('Combien ils pourraient vous rapporter&nbsp;? Chez ECOM&nbsp;BOSS, ces leads ont déjà généré 100&#8239;000&nbsp;€ de chiffre d\'affaires. On calcule votre potentiel avec vous, sur vos vrais chiffres.',
     'How much could they bring in? At ECOM&nbsp;BOSS, these leads have already generated €100,000 in revenue. We’ll work out your potential with you, using your real numbers.'),
    ('data-text="Calculer mon potentiel">Calculer mon potentiel</span>', 'data-text="Calculate my potential">Calculate my potential</span>'),

    # 06 — La preuve
    ('07 — La preuve', '07 — Proof'),
    ('Déjà en place chez Gaspard Grosjean.', 'Already live with Gaspard Grosjean.'),
    ('Fondateur d\'ECOM&nbsp;BOSS, l\'un des plus gros infopreneurs e-commerce français. Plus de 70&nbsp;000 abonnés sur Instagram.',
     'Founder of ECOM&nbsp;BOSS, one of France’s biggest e-commerce educators. Over 70,000 followers on Instagram.'),
    ('>ventes low-ticket</span>', '>low-ticket sales</span>'),
    ('<span class="proof__count" data-to="100000">100&#8239;000</span><span class="proof__suffix">&nbsp;€</span></span><span class="proof__label">de chiffre d\'affaires généré</span>',
     '<span class="proof__suffix">€</span><span class="proof__count" data-to="100000">100,000</span></span><span class="proof__label">in revenue generated</span>'),
    ('>setter recruté de son côté</span>', '>setters hired on his end</span>'),
    ('«&nbsp;[Citation de Gaspard, 2 phrases maximum]&nbsp;»', '“[Gaspard’s quote, 2 sentences max]”'),
    ('<span>Gaspard Grosjean, fondateur d\'ECOM&nbsp;BOSS</span>', '<span>Gaspard Grosjean, founder of ECOM&nbsp;BOSS</span>'),

    # 07 — Le modèle
    ('08 — Le modèle', '08 — The model'),
    ('Zéro coût d\'entrée.', 'Zero upfront cost.'),
    ('On gagne seulement si vous gagnez.', 'We only win when you win.'),
    ('<span class="model__big">65&nbsp;%</span><span class="model__small">pour vous, sur chaque vente</span>',
     '<span class="model__big">65%</span><span class="model__small">for you, on every sale</span>'),
    ('model__tag--you">Vous</span>', 'model__tag--you">You</span>'),
    ('Loseless<br class="br-desk"> et setters', 'Loseless<br class="br-desk"> &amp; setters'),
    ('Aucun coût pour démarrer. Ensuite, sur chaque vente&nbsp;: 65&nbsp;% pour vous, 35&nbsp;% pour loseless et les setters.',
     'Nothing to pay to get started. After that, on every sale: 65% for you, 35% for loseless and the setters.'),
    ('<dt>Ce qu\'on prend en charge</dt><dd>L\'offre, la page, la vidéo, le recrutement et le management des setters, et le suivi. Vous n\'avez rien à recruter ni à gérer.</dd>',
     '<dt>What we handle</dt><dd>The offer, the page, the video, hiring and managing the setters, and the follow-up. Nothing for you to hire or manage.</dd>'),
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
    ('Ceux qui vendent un accompagnement high&#8209;ticket&nbsp;: pour récupérer les leads qui n\'ont pas le budget, ou pour faire entrer plus de clients par une offre low&#8209;ticket.',
     'Coaches and course creators who sell a high&#8209;ticket program: to recover the leads who can’t afford it, or to bring in more customers through a low&#8209;ticket offer.'),
    ('[À COMPLÉTER]', '[TO BE COMPLETED]'),

    # ------------------------------------------------------------------
    # Deux modes : rattrapage / porte d'entrée (brief du 18/10/2026)
    # ------------------------------------------------------------------
    ('aria-label="Façon de brancher Loseless"', 'aria-label="How to plug in Loseless"'),
    ('>En rattrapage</button>', '>Safety net</button>'),
    ('>En porte d\'entrée</button>', '>Front door</button>'),
    # boucle, mode porte d'entrée
    ('data-alt-h="Contenu et pubs" data-alt-p="Vos pubs, votre VSL et vos influenceurs attirent l\'attention, avec un lien suivi pour chacun."',
     'data-alt-h="Content and ads" data-alt-p="Your ads, your VSL and your influencers get attention, each with its own tracked link."'),
    ('data-alt-h="Lead" data-alt-p="Il remplit le formulaire de votre page low-ticket."',
     'data-alt-h="Lead" data-alt-p="They fill in the form on your low-ticket page."'),
    ('data-alt-h="Appel setter" data-alt-p="Un de nos setters l\'appelle rapidement."',
     'data-alt-h="Setter call" data-alt-p="One of our setters calls them quickly."'),
    ('data-alt-h="Vente encaissée" data-alt-p="Il achète votre offre low-ticket. Vous encaissez directement."',
     'data-alt-h="Cash collected" data-alt-p="They buy your low-ticket offer. The money goes straight to you."'),
    ('data-alt-h="Workshop 7 jours" data-alt-p="Il construit son outil jour après jour, avec un coach IA."',
     'data-alt-h="7-day workshop" data-alt-p="They build their tool day by day, with an AI coach."'),
    ('data-alt-h="Nurturing" data-alt-p="On reste en contact et on repère ceux qui sont prêts à aller plus loin."',
     'data-alt-h="Nurturing" data-alt-p="We stay in touch and spot those who are ready to go further."'),
    ('data-alt-h="Upsell high-ticket" data-alt-p="Les acheteurs prêts montent vers votre accompagnement."',
     'data-alt-h="High-ticket upsell" data-alt-p="Buyers who are ready move up to your coaching program."'),
    ('data-alt="Contenu et pubs"', 'data-alt="Content and ads"'),
    ('data-alt="Appel setter"', 'data-alt="Setter call"'),
    ('data-alt="Vente encaissée"', 'data-alt="Cash collected"'),
    ('data-alt="Workshop 7 jours"', 'data-alt="7-day workshop"'),
    ('data-alt="Upsell high-ticket"', 'data-alt="High-ticket upsell"'),
    # 03 — Deux façons
    ('03 — Deux façons', '03 — Two ways'),
    ('Derrière votre offre. Ou devant.', 'Behind your offer. Or in front of it.'),
    ('</span>En rattrapage</p>', '</span>As a safety net</p>'),
    ('Rien ne change dans votre funnel.', 'Nothing changes in your funnel.'),
    ('Votre offre principale reste en place. Les leads qui n\'ont pas le budget sont redirigés vers votre offre low-ticket, et nos setters les rappellent.',
     'Your main offer stays as it is. Leads who can’t afford it are redirected to your low-ticket offer, and our setters call them back.'),
    ('<li>Votre formulaire</li>', '<li>Your form</li>'),
    ('<li>«&nbsp;Pas le budget&nbsp;»</li>', '<li>“No budget”</li>'),
    ('<li>Offre low-ticket</li>', '<li>Low-ticket offer</li>'),
    ('<li>Upsell high-ticket</li>', '<li>High-ticket upsell</li>'),
    ('Comme chez Gaspard Grosjean, ECOM&nbsp;BOSS.', 'Like at Gaspard Grosjean’s ECOM&nbsp;BOSS.'),
    ('Afficher la page en mode rattrapage', 'Show the page in safety-net mode'),
    ('</span>En porte d\'entrée</p>', '</span>As the front door</p>'),
    ('Le premier achat de vos clients.', 'Your customers’ first purchase.'),
    ('Votre offre low-ticket devient l\'entrée de votre funnel. Vos pubs, votre VSL et vos influenceurs envoient vers elle, nos setters la vendent, et les meilleurs acheteurs montent vers votre high-ticket.',
     'Your low-ticket offer becomes the entry point of your funnel. Your ads, your VSL and your influencers send people to it, our setters sell it, and the best buyers move up to your high-ticket.'),
    ('<li>Pubs, VSL, influenceurs</li>', '<li>Ads, VSL, influencers</li>'),
    ('<li>Workshop 7&nbsp;jours</li>', '<li>7-day workshop</li>'),
    ('En place chez un deuxième partenaire e-commerce.', 'Live with a second e-commerce partner.'),
    ('Afficher la page en mode porte d\'entrée', 'Show the page in front-door mode'),
    ('Cliquez sur une carte&nbsp;: la boucle et le simulateur s\'adaptent à votre cas.', 'Click a card: the loop and the simulator adapt to your case.'),
    # 07 — Simulateur, mode porte d'entrée
    ('data-alt="Combien entrent chez vous&nbsp;?"', 'data-alt="How many come in?"'),
    ('data-alt="Deux hypothèses suffisent."', 'data-alt="Two assumptions are enough."'),
    ('data-alt="Leads par mois"', 'data-alt="Leads per month"'),
    ('data-alt="Part qui achète l\'offre low-ticket"', 'data-alt="Share who buy the low-ticket offer"'),
    ('data-alt="Acheteurs / mois"', 'data-alt="Buyers / month"'),
    ('data-alt="Chaque point orange est un client qui entre chez vous par un premier achat, et qui peut monter vers votre high-ticket."',
     'data-alt="Each orange dot is a customer who comes in through a first purchase, and who can move up to your high-ticket."'),
    ('Hypothèses à ajuster. Ce n\'est pas une promesse de résultat.', 'Assumptions to adjust. Not a promise of results.'),
    # FAQ, nouvelles questions et réponses
    ('En rattrapage ou en porte d\'entrée&nbsp;: comment choisir&nbsp;?', 'Safety net or front door: how do I choose?'),
    ('Si votre offre principale vend déjà bien, on se place derrière elle pour récupérer les «&nbsp;pas le budget&nbsp;». Si vous lancez votre funnel ou que vous voulez faire entrer plus de monde, l\'offre low-ticket devient votre porte d\'entrée. On en parle ensemble pendant l\'appel.',
     'If your main offer already sells well, we sit behind it to recover the people who can’t afford it. If you’re launching your funnel or want to bring more people in, the low-ticket offer becomes your front door. We’ll decide together on the call.'),
    ('Nous. On construit votre offre low&#8209;ticket de A à Z&nbsp;: l\'offre, la page, la vidéo, l\'outil et le workshop, sous votre nom. Vous validez tout avant le lancement.',
     'We do. We build your low&#8209;ticket offer from start to finish: the offer, the page, the video, the tool and the workshop, under your name. You approve everything before launch.'),
    ('Qu\'est-ce que reçoit l\'acheteur&nbsp;?', 'What does the buyer get?'),
    ('Un workshop de 7&nbsp;jours, un outil qu\'il construit lui-même, un coach IA sur WhatsApp et un espace membre avec les vidéos de votre méthode.',
     'A 7-day workshop, a tool they build themselves, an AI coach on WhatsApp and a member area with the videos of your method.'),
    ('Sur quels outils vous appuyez-vous&nbsp;?', 'Which tools do you use?'),
    ('L\'outil de vos acheteurs est construit sur Base44, dont Loseless est partenaire. Vous n\'avez rien à installer.',
     'Your buyers’ tool is built on Base44, and Loseless is a Base44 partner. You have nothing to set up.'),
    ('Questions masquées tant que la réponse n\'est pas fournie', 'Hidden questions until the answer is provided'),

    # 09 — Pour qui
    ('10 — Pour qui', '10 — Who it’s for'),
    ('On ne travaille pas avec tout le monde.', 'We don’t work with everyone.'),
    ('Loseless s\'adresse aux business high&#8209;ticket qui font plus de 10&#8239;000&nbsp;€ de CA par mois. En dessous, votre volume de leads ne suffit pas pour que le système soit rentable pour vous.',
     'Loseless is for high-ticket businesses doing over €10,000 in monthly revenue. Below that, your lead volume isn’t enough for the system to pay off for you.'),

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
    (r'(href|src|poster)="(styles\.css|main\.js|reserver\.js|favicon\.svg|vendor/|assets/)', r'\1="../\2'),
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
    attrs = ' '.join(re.findall(r'(?:aria-label|aria-valuetext|content|data-text|title|data-alt|data-alt-h|data-alt-p)="([^"]*)"', visible))
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
