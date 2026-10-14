#!/usr/bin/env python3
"""Bouwt de statische website van de Arnhemse Luchtvaart Club in ../docs.

De teksten per pagina staan in bron/content/<naam>.html (overgenomen van de
oude WordPress-site). Dit script zet er de gedeelde kop, menu en voettekst
omheen. Gebruik:  python3 bron/build.py
"""
import html
import os
import re

from bs4 import BeautifulSoup, NavigableString
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "bron", "content")
OUT = os.path.join(ROOT, "docs")

SITE = "Arnhemse Luchtvaart Club"
TAGLINE = "De modelbouw vliegclub van Arnhem"
MAPS = "https://maps.app.goo.gl/RViMQKregH4zYKxs8"

# Volgorde en titels gelijk aan het menu "Overig" op de oude site.
OVERIG = [
    ("geweldige-vliegavond", "Geweldige vliegavond!"),
    ("indoor-vliegen-split-stik", "Indoor vliegen met Split Stik"),
    ("dlg-clinic", "DLG clinic"),
    ("spirit-100-maiden", "Spirit 100 Maiden"),
    ("vliegdag-8-mei-2023", "Vliegdag ALC 8 mei 2023"),
    ("prowing-international-2023", "ProWing International 2023"),
    ("res-vliegen", "RES Vliegen"),
    ("res-clinic-duiven-2022", "RES Clinic Duiven 2022"),
    ("bouwverslag-hi-fly", "Bouwverslag Hi Fly"),
    ("brevet-vliegen", "Brevet vliegen"),
    ("vliegterrein", "Vliegterrein"),
    ("boerenkool-dag", "Boerenkool dag"),
    ("thomas-cup", "Thomas CUP"),
]
MAIN = [
    ("index", "Home"),
    ("modelvliegen", "Modelvliegen"),
    ("sponsoren", "Sponsoren"),
    ("overig", "Overig"),
    ("links", "Links"),
    ("contact", "Contact"),
]

SPONSORS = [
    ("it2grow", "https://it2grow.nl/", "it2grow_logo_klein.jpg.png"),
    ("Engelen & de Vrind", "https://www.endv.nl/", "Engelen-en-De-Vrind.png"),
    ("CCV", "https://www.ccv.eu/nl", "CCV.png"),
    ("Der Himmlische Höllein", "https://www.hoelleinshop.com/", "Der-Himmlische-Hoellein.png"),
    ("Quartel Modelbouw", "https://quartel.nl/", "Quartel.png"),
    ("Arnhemse Borduur Centrale", "https://arnhemseborduurcentrale.nl/", "Arnhemse-Borduur-Centrale-Logo.png"),
]

ICON = {
    "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "file": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M9 14h6M9 17h4"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "chev": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>',
}


def esc(s):
    return html.escape(s, quote=True)


def read(name):
    with open(os.path.join(SRC, name + ".html"), encoding="utf-8") as f:
        return f.read()


def img_size(src):
    try:
        with Image.open(os.path.join(OUT, src)) as im:
            return im.size
    except Exception:
        return None


# ---------------------------------------------------------------- layout

def nav(active):
    items = []
    for slug, title in MAIN:
        cur = slug == active or (slug == "overig" and active in dict(OVERIG))
        aria = ' aria-current="page"' if slug == active else ""
        cls = ' class="active"' if cur else ""
        if slug == "overig":
            sub = "".join(
                f'<li><a href="{s}.html"{" aria-current=\"page\"" if s == active else ""}>{esc(t)}</a></li>'
                for s, t in OVERIG
            )
            items.append(
                f'<li class="has-sub{" active" if cur else ""}">'
                f'<a href="overig.html"{aria}>Overig</a>'
                f'<button class="sub-toggle" aria-expanded="false" aria-label="Submenu Overig tonen">{ICON["chev"]}</button>'
                f'<ul class="sub">{sub}</ul></li>'
            )
        else:
            items.append(f'<li{cls}><a href="{slug}.html"{aria}>{title}</a></li>')
    return "".join(items)


def page(slug, title, body, description=""):
    full_title = SITE if slug == "index" else f"{title} | {SITE}"
    desc = description or f"{SITE}: {TAGLINE.lower()}, opgericht in 1930."
    foot_links = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, t in MAIN)
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="img/alc-logo-big.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
</head>
<body class="page-{slug}">
<a class="skip" href="#inhoud">Naar de inhoud</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="index.html">
      <img src="img/alc-logo-big.jpg" alt="Logo Arnhemse Luchtvaart Club" width="64" height="64">
      <span><strong>{SITE}</strong><small>{TAGLINE}</small></span>
    </a>
    <button class="menu-toggle" aria-expanded="false" aria-controls="hoofdmenu" aria-label="Menu openen"><span></span><span></span><span></span></button>
    <nav id="hoofdmenu" class="main-nav" aria-label="Hoofdmenu"><ul>{nav(slug)}</ul></nav>
  </div>
</header>
<main id="inhoud">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="brand brand-footer" href="index.html">
        <img src="img/alc-logo-big.jpg" alt="" width="56" height="56">
        <span><strong>{SITE}</strong><small>Opgericht 1930</small></span>
      </a>
      <p class="muted">De oudste modelvliegclub van Nederland die ook zelf de zweefvliegtuigen bouwt.</p>
    </div>
    <div>
      <h3>Clublokaal</h3>
      <p>Spelzaal de Rietebeek<br><a href="{MAPS}" target="_blank" rel="noopener">Blekerstraat 6<br>6828EW Arnhem</a></p>
    </div>
    <div>
      <h3>Bouwavonden</h3>
      <p>Dinsdag 19.00 – 22.30<br>Vrijdag 19.00 – 22.30</p>
      <p><a href="mailto:secretaris@arnhemseluchtvaartclub.nl">secretaris@arnhemseluchtvaartclub.nl</a></p>
    </div>
    <div>
      <h3>Menu</h3>
      <ul class="foot-links">{foot_links}</ul>
    </div>
  </div>
  <div class="wrap copyright">© {SITE}</div>
</footer>
<div class="lightbox" hidden><button class="lb-close" aria-label="Sluiten">×</button><button class="lb-prev" aria-label="Vorige">‹</button><figure><img alt=""><figcaption></figcaption></figure><button class="lb-next" aria-label="Volgende">›</button></div>
<script src="js/site.js"></script>
</body>
</html>
"""


def page_head(title, kicker=None, crumbs=None):
    k = f'<p class="kicker">{esc(kicker)}</p>' if kicker else ""
    c = ""
    if crumbs:
        parts = ['<a href="index.html">Home</a>'] + [f'<a href="{h}">{esc(t)}</a>' for h, t in crumbs]
        c = '<nav class="crumbs" aria-label="Kruimelpad">' + " <span>/</span> ".join(parts) + "</nav>"
    return f'<section class="page-head"><div class="wrap">{c}{k}<h1>{esc(title)}</h1></div></section>'


# ---------------------------------------------------------- content tidy

def tidy(fragment):
    """Maakt de overgenomen WordPress-HTML netjes voor de nieuwe opmaak."""
    s = BeautifulSoup(fragment, "html.parser")
    for im in s.find_all("img"):
        size = img_size(im["src"])
        if size:
            im["width"], im["height"] = size
            if size[0] < 420:
                im["class"] = ["small"]
        # Afbeelding als link naar zichzelf of groot genoeg: klikbaar via lightbox
        if size and size[0] >= 420 and not im.find_parent("a"):
            im["data-zoom"] = ""
    # Losse opeenvolgende afbeeldingen (galerijen) groeperen.
    top = [c for c in s.contents if not (isinstance(c, NavigableString) and not c.strip())]
    run = []

    def flush():
        if len(run) >= 2:
            g = s.new_tag("div", attrs={"class": "gallery"})
            run[0].insert_before(g)
            for el in run:
                g.append(el.extract())
        run.clear()

    for el in top:
        is_img = getattr(el, "name", None) == "img" or (
            getattr(el, "name", None) == "figure" and el.find("img") and not el.find("p")
        )
        if is_img:
            run.append(el)
        else:
            flush()
    flush()
    # Losse afbeelding op topniveau in een figure zetten.
    for im in s.find_all("img", recursive=False):
        fig = s.new_tag("figure")
        im.wrap(fig)
    # Paragrafen die alleen een (kleine) afbeelding bevatten markeren.
    for p in s.find_all("p"):
        text = p.get_text(strip=True)
        if p.find("img") and not text:
            p["class"] = ["media"]
        elif p.find("img", class_="small"):
            p["class"] = ["with-logo"]
        elif p.find("img"):
            p["class"] = ["with-photo"]
    for v in s.find_all("video"):
        v["playsinline"] = ""
    return str(s)


def first_image(fragment):
    m = re.search(r'<img[^>]*src="(img/[^"]+\.(?:jpe?g|png))"', fragment)
    return m.group(1) if m else "img/banner.png"


def excerpt(fragment, n=150):
    text = BeautifulSoup(fragment, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0] + "…"


def card(slug, title, frag, eager=False):
    img = first_image(frag)
    load = "" if eager else ' loading="lazy"'
    return (
        f'<a class="card" href="{slug}.html"><div class="card-img"><img src="{img}" alt=""{load}></div>'
        f'<div class="card-body"><h3>{esc(title)}</h3><p>{esc(excerpt(strip_title(frag, dict(OVERIG).get(slug, title))))}</p>'
        f'<span class="more">Lees meer {ICON["arrow"]}</span></div></a>'
    )


def strip_title(frag, title):
    # Sommige pagina's herhalen de titel als eerste kop: weghalen.
    return re.sub(r"^\s*<h2>\s*" + re.escape(title) + r"\s*</h2>", "", frag)


# ------------------------------------------------------------------ pages

def build_home():
    frag = {s: read(s) for s, _ in OVERIG}
    logos = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" title="{esc(n)}"><img src="img/{f}" alt="{esc(n)}" loading="lazy"></a>'
        for n, u, f in SPONSORS
    )
    check = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 5 5 9-10"/></svg>'
    faq = [
        ("Wanneer en waar bouwen jullie?",
         "<p>Bouwen doen we in ons clubgebouw, gevestigd in zaalsport “De Rietebeek”, "
         f'<a href="{MAPS}" target="_blank" rel="noopener">Blekerstraat 6 in Arnhem</a>, op dinsdag- en vrijdagavond van 19.00 tot 22.30 uur. '
         "Iedereen is welkom om kennis te komen maken, rond te kijken, en lid te worden.</p>"
         "<p>Op de parkeerplaats is er na 20 meter een groen hek aan de linkerkant, daarachter mogen leden/bezoekers van de ALC gratis parkeren. "
         "Let op, de openbare parkeerplaatsen zijn betaald tot 23:00 u! Aan het einde van de parkeerplaats staat op links een gymzaal (sport- en spelzaal “de Rietebeek”), "
         "in dit gebouw zit de ALC. In de lange kant van het gebouw bevindt zich een stalen hek, hierachter zit de deur naar het lokaal. "
         "Als u aanbelt komt één van de leden u halen.</p>"),
        ("Waar vliegen jullie?",
         "<p>Op twee locaties mogen we vliegen met onze vliegtuigen, de heide op de Posbank en bij een boer in Duiven. "
         'Lees meer over ons <a href="vliegterrein.html">vliegterrein</a>.</p>'),
        ("Heb ik ervaring nodig?",
         "<p>Afhankelijk van je bouw-ervaring, bepaal je zelf wat voor model je wilt bouwen, vanaf een tekening of met een bouwdoos, dat maakt niet uit! "
         "In alle klassen zijn verschillende beginners- en gevorderden modellen voor handen.<br>"
         "Actieve leden met veel ervaring helpen en begeleiden nieuwe leden om ervoor te zorgen dat je eerste model ook echt vliegt.</p>"),
        ("Wat kost het bouwen?",
         "<p>De kosten voor de materialen variëren van een paar euro voor een eenvoudig werpmodel tot ….<br>"
         "Voor radiobesturing heb je behalve het vliegtuig ook een zender, een ontvanger, servo’s en accu’s nodig. "
         "Bij beginners helpen we je met de eerste aanzet, ook met deze apparatuur totdat je zelf een keuze gemaakt hebt wat je zelf wilt aanschaffen.</p>"),
        ("Wat is RES vliegen?",
         "<p>We spelen in op nieuwe disciplines zoals bijvoorbeeld nu het RES (Rudder, Elevator, Spoiler) vliegen. "
         "Dit zijn modelzwevers met een spanwijdte van 2 meter, maar zo licht mogelijk gebouwd om onder minimale windsterkte te kunnen vliegen. "
         '<a href="res-vliegen.html">Lees meer over RES vliegen</a>.</p>'),
    ]
    faq_html = "".join(
        f'<details class="x-faq-item"{" open" if i == 0 else ""}><summary>{esc(q)}<span class="x-plus" aria-hidden="true"></span></summary><div>{a}</div></details>'
        for i, (q, a) in enumerate(faq)
    )
    body = f"""
<section class="x-hero">
  <div class="x-grid" aria-hidden="true"></div>
  <div class="x-glow" aria-hidden="true"></div>
  <canvas class="x-sky" aria-hidden="true"></canvas>
  <div class="wrap x-hero-inner">
    <a class="x-badge" href="overig.html"><span class="x-dot"></span>Opgericht in 1930 · Arnhem <span class="x-badge-link">Verslagen {ICON["arrow"]}</span></a>
    <h1>De modelbouw vliegclub <span class="x-grad">van Arnhem</span></h1>
    <p class="x-lead">Wij, de Arnhemse Luchtvaartclub (ALC), zijn op zoek naar nieuwe leden. Wij zijn de oudste modelvliegclub die ook zelf de zweefvliegtuigen bouwt van Nederland.</p>
    <div class="x-actions">
      <a class="x-btn x-btn-dark" href="contact.html">Kom kennismaken {ICON["arrow"]}</a>
      <a class="x-btn x-btn-light" href="modelvliegen.html">Over modelvliegen</a>
    </div>
    <p class="x-meta">{ICON["clock"]} Bouwavonden dinsdag &amp; vrijdag 19.00 – 22.30 <span>·</span> {ICON["pin"]} Blekerstraat 6, Arnhem</p>
  </div>
  <div class="wrap x-shot-wrap">
    <div class="x-shot">
      <div class="x-shot-bar"><i></i><i></i><i></i><span>clublokaal · Spijkerkwartier, Arnhem</span></div>
      <img src="img/banner.png" alt="ALC Werkplaats" width="1093" height="216" data-zoom>
    </div>
    <div class="x-float x-float-a"><strong>4 m</strong><span>spanwijdte, zelf gebouwd</span></div>
    <div class="x-float x-float-b"><strong>94 jaar</strong><span>Wij bestaan 94 jaar.</span></div>
  </div>
</section>

<section class="x-logos">
  <div class="wrap">
    <p>Gesteund door onze sponsoren</p>
    <div class="x-logo-row">{logos}</div>
  </div>
</section>

<section class="x-section">
  <div class="wrap">
    <div class="x-head">
      <span class="x-pill">Wat we doen</span>
      <h2>Bouwen, vliegen en <span class="x-grad">samen leren</span></h2>
      <p>In ons eigen clublokaal in het Arnhemse Spijkerkwartier bouwen we model zweefvliegtuigen met een spanwijdte tot wel 4 meter.</p>
    </div>
    <div class="x-bento">
      <article class="x-tile x-tile-wide x-tile-photo">
        <img src="img/WhatsApp-Image-2024-05-02-at-11.14.38-1-Copy.jpeg" alt="Ready for take-off" loading="lazy">
        <div><span class="x-tag">Bouwen</span><h3>Een eigen bouwruimte</h3><p>De ALC is één van de weinige modelvliegclubs in Nederland die in het bezit van een eigen bouwruimte. Hier zijn alle gereedschappen en materialen aanwezig, die nodig zijn om modelvliegtuigen te kunnen bouwen.</p></div>
      </article>
      <article class="x-tile x-tile-blue">
        <span class="x-tag">Vliegen</span><h3>Rozendaalse Veld, Posbank en Duiven</h3><p>Naast de bouwavonden op dinsdag en vrijdag, gaan we ook regelmatig vliegen op het Rozendaalse Veld, bij de boer of we gaan naar wedstrijden.</p>
        <a class="x-more" href="vliegterrein.html">Vliegterrein {ICON["arrow"]}</a>
      </article>
      <article class="x-tile">
        <span class="x-tag">Leren</span><h3>Les van ervaren leden</h3><p>Ervaren leden van onze club geven les wat je moet doen om goed te leren vliegen.</p>
        <a class="x-more" href="brevet-vliegen.html">Brevet vliegen {ICON["arrow"]}</a>
      </article>
      <article class="x-tile">
        <span class="x-tag">Stiltesport</span><h3>Zweefmodellen hebben onze voorkeur</h3><p>Wij starten deze modellen met een lijn: met de hand, een rubber of een lier opgetrokken. Electromodellen worden zo gebouwd dat de herrie van de motor tot een minimum beperkt blijft.</p>
      </article>
      <article class="x-tile x-tile-photo x-tile-tall">
        <img src="img/Thomas-Cup-2018-start-vintage-zweefmodel.jpg" alt="Start vintage zweefmodel" loading="lazy">
        <div><span class="x-tag">Wedstrijden &amp; uitstapjes</span><h3>Thomas Cup, Eifel en Maasvlakte</h3><p>Ook maken we uitstapjes om helling te vliegen in de Eifel, of aan de kust bij de Maasvlakte 2.</p><a class="x-more" href="thomas-cup.html">Thomas CUP {ICON["arrow"]}</a></div>
      </article>
    </div>
  </div>
</section>

<section class="x-section x-alt">
  <div class="wrap">
    <div class="x-head x-head-row">
      <div><span class="x-pill">Nieuws</span><h2>Laatste verslagen</h2></div>
      <a class="x-btn x-btn-light" href="overig.html">Alle verslagen {ICON["arrow"]}</a>
    </div>
    <article class="x-feature">
      <img src="img/PromotieMateriaalVanSponsoren.jpg" alt="Promotie materiaal van sponsoren" loading="lazy" data-zoom>
      <div>
        <span class="x-tag">Sponsoren</span>
        <h3>Sponsoren verrassen ALC met mooie flyers en stickers om de club te promoten.</h3>
        <p><strong>Dank! Engelen &amp; de Vrind en it2grow</strong></p>
        <p>( <a href="https://www.endv.nl/" target="_blank" rel="noopener">Engelen &amp; de Vrind</a>, <a href="https://it2grow.nl/" target="_blank" rel="noopener">it2grow</a> )</p>
      </div>
    </article>
    <div class="cards">
      {card("geweldige-vliegavond", "1 mei 2024 Geweldige vliegavond", frag["geweldige-vliegavond"])}
      <a class="card card-radio" href="https://www.gld.nl/artikel/8059230/onze-modelvliegclub-houdt-open-dag-kom-je-ook" target="_blank" rel="noopener">
        <div class="card-img radio"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="8" width="18" height="12" rx="2"/><circle cx="8" cy="14" r="2.5"/><path d="M13 12h5M13 15h5M7 8l10-5"/></svg></div>
        <div class="card-body"><h3>Luister ook het interview op Radio Gelderland</h3><p>Onze modelvliegclub houdt open dag: kom je ook?</p><span class="more">Interview Radio Gelderland {ICON["arrow"]}</span></div>
      </a>
      {card("dlg-clinic", "Leden van ALC wonen DLG clinic bij van F3K Nederland op vliegveld Terlet 28 januari 2024", frag["dlg-clinic"])}
    </div>
  </div>
</section>

<section class="x-section">
  <div class="wrap x-quote">
    <blockquote>”Ik zit in mijn vliegstoel en ben met hulp van Ab Janssen mijn CX mini-RES aan het afstellen voor een strakke lancering aan het korte bungee lijntje. En dat lukte uiteindelijk prima alleen ging bij de landing van de laatste vlucht het kielvlak in tweeen….. “</blockquote>
    <p class="x-quote-by"><img src="img/WhatsApp-Image-2024-05-02-at-11.14.38-2-Copy.jpeg" alt="" loading="lazy"> <span><strong>Ron</strong> · <a href="geweldige-vliegavond.html">Geweldige vliegavond!</a></span></p>
  </div>
</section>

<section class="x-section x-alt">
  <div class="wrap x-member">
    <div>
      <span class="x-pill">Lidmaatschap</span>
      <h2>Probeer het <span class="x-grad">2 maanden gratis</span></h2>
      <p>Om te ervaren of onze club bij je past wordt er voor de eerste 2 maanden geen contributie gevraagd. Loop eens binnen op de club, kom een kopje koffie drinken en kijk of er iets is wat je leuk vindt om te gaan doen.</p>
      <a class="x-btn x-btn-dark" href="modelvliegen.html">Lees alles over lidmaatschap {ICON["arrow"]}</a>
    </div>
    <div class="x-price">
      <div class="x-price-top"><span>Eerste 2 maanden</span><strong>€0</strong><small>geen contributie</small></div>
      <ul>
        <li>{check}<span>Automatisch lid van de <a href="https://www.knvvl.nl/modelvliegsport/" target="_blank" rel="noopener">KNVvL</a>, en verzekerd als je eigen WA verzekering je in de steek laat</span></li>
        <li>{check}<span>Huisgenootlidmaatschap: de oudste betaalt de volle contributie en de volgende 50%</span></li>
        <li>{check}<span>Jeugdleden betalen een gereduceerd bedrag</span></li>
        <li>{check}<span>Hulp bij je eerste model, ook met de apparatuur</span></li>
        <li>{check}<span>Eigen bouwruimte met alle gereedschappen en materialen</span></li>
      </ul>
      <a class="x-btn x-btn-blue" href="contact.html">Kom kennismaken</a>
    </div>
  </div>
</section>

<section class="x-section">
  <div class="wrap x-about">
    <div>
      <span class="x-pill">Over de club</span>
      <h2>Arnhemse Luchtvaart Club (ALC)</h2>
      <a class="x-btn x-btn-light" href="downloads/Folder-ALC.pdf" target="_blank" rel="noopener">{ICON["file"]} Download Folder-ALC</a>
    </div>
    <div class="x-about-text">
      <p>De ALC is opgericht in 1930 en bestaan dus bijna 100 jaar. Veel is er uit die tijd overgebleven in ons archief, misschien moeten we nog eens diep gaan graven om meer uit die tijd te weten te komen. We hebben n.l. in ons “kantoor” een grote hoeveelheid mappen staan die waardevolle informatie bevatten uit de afgelopen 90 jaar. Ook een aantal van onze leden hebben een eigen plakboek samengesteld, in de loop der jaren hebben we meermaals de krant gehaald.</p>
      <p>Vanaf het begin is er gevlogen op Het Rozendaals Veld bij de brandtoren. De eerste wedstrijd hebben we daar gevlogen in 1932.<br>We hebben nog vergunningen waar precies aangegeven staat waar brandstofmodellen mogen starten en landen, waar vrije vluchtmodellen met een lont mochten vliegen etc.</p>
      <p>Intussen is dit ondenkbaar geworden. Geluidsoverlast en brandgevaar lagen ook toen al op de loer. Als vereniging hebben we toen gekozen voor de zgn. stiltesporten, zweefmodellen hebben onze voorkeur.</p>
    </div>
  </div>
</section>

<section class="x-section x-alt">
  <div class="wrap x-faq">
    <div class="x-head">
      <span class="x-pill">Veelgestelde vragen</span>
      <h2>Goed om te weten</h2>
    </div>
    <div class="x-faq-list">{faq_html}</div>
  </div>
</section>

<section class="x-section">
  <div class="wrap">
    <div class="x-cta">
      <div class="x-grid" aria-hidden="true"></div>
      <h2>Loop eens binnen op de club</h2>
      <p>Iedereen is welkom om kennis te komen maken, rond te kijken, en lid te worden.</p>
      <div class="x-actions">
        <a class="x-btn x-btn-yellow" href="contact.html">Contact {ICON["arrow"]}</a>
        <a class="x-btn x-btn-ghost" href="https://www.sponsorkliks.com/products/shops.php?club=12273&amp;sc=dyn-bnnr-bol" target="_blank" rel="noopener">Sponsor ook de Arnhemse Luchtvaart Club</a>
      </div>
    </div>
  </div>
</section>
<script src="js/gliders.js" defer></script>
"""
    return page("index", "Home", body)


def build_article(slug, title, crumbs=None, kicker=None):
    frag = strip_title(read(slug), title)
    body = page_head(title, kicker, crumbs) + f'<article class="section"><div class="wrap narrow prose">{tidy(frag)}</div></article>'
    if crumbs:  # verslagen: navigatie naar andere verslagen
        others = [(s, t) for s, t in OVERIG if s != slug]
        i = [s for s, _ in OVERIG].index(slug)
        nxt = OVERIG[(i + 1) % len(OVERIG)]
        prv = OVERIG[(i - 1) % len(OVERIG)]
        body += (
            '<nav class="section pager-wrap" aria-label="Meer verslagen"><div class="wrap narrow pager">'
            f'<a href="{prv[0]}.html"><small>Vorige</small>{esc(prv[1])}</a>'
            f'<a href="overig.html" class="all">Alle verslagen</a>'
            f'<a href="{nxt[0]}.html" class="next"><small>Volgende</small>{esc(nxt[1])}</a>'
            "</div></nav>"
        )
    return page(slug, title, body, excerpt(frag, 155))


def build_overig():
    cards = "".join(card(s, t, read(s), eager=i < 3) for i, (s, t) in enumerate(OVERIG))
    body = page_head("Overig", "Verslagen en meer") + f'<section class="section"><div class="wrap"><div class="cards">{cards}</div></div></section>'
    return page("overig", "Overig", body, "Verslagen van vliegdagen, clinics, bouwverslagen en meer van de Arnhemse Luchtvaart Club.")


def build_sponsoren():
    s = BeautifulSoup(read("sponsoren"), "html.parser")
    paras = [p for p in s.find_all("p") if p.get_text(strip=True) or p.find("img")]
    items, logo = [], None
    for p in paras:
        a = p.find("a")
        if p.find("img") and not p.get_text(strip=True):
            logo = (a["href"], p.find("img")["src"])
            continue
        if logo:
            name = p.find("strong").get_text(strip=True)
            p.find("strong").decompose()
            inner = re.sub(r"^\s*(<br/>\s*)+", "", p.decode_contents())
            items.append(
                f'<article class="sponsor"><a class="sponsor-logo" href="{logo[0]}" target="_blank" rel="noopener"><img src="{logo[1]}" alt="{esc(name)}" loading="lazy"></a>'
                f'<div><h2>{esc(name)}</h2><p>{inner}</p><a class="more" href="{logo[0]}" target="_blank" rel="noopener">Bezoek website {ICON["arrow"]}</a></div></article>'
            )
            logo = None
    body = page_head("Sponsoren", "Met dank aan") + f'<section class="section"><div class="wrap sponsor-list">{"".join(items)}</div></section>'
    return page("sponsoren", "Sponsoren", body, "De sponsoren van de Arnhemse Luchtvaart Club.")


def build_contact():
    body = page_head("Contact", "Kom gerust langs") + f"""
<section class="section">
  <div class="wrap contact-grid">
    <div class="panel">
      <h2>{ICON["pin"]} Club locatie</h2>
      <p>Spelzaal de Rietebeek<br><a href="{MAPS}" target="_blank" rel="noopener">Blekerstraat 6</a><br><a href="{MAPS}" target="_blank" rel="noopener">6828EW Arnhem</a></p>
      <a class="btn btn-primary" href="{MAPS}" target="_blank" rel="noopener">Route plannen</a>
    </div>
    <div class="panel">
      <h2>{ICON["clock"]} Bouwavonden</h2>
      <p>Dinsdag 19.00 – 22.30<br>Vrijdag 19.00 – 22.30</p>
      <p class="note">s’avonds en in het weekend Gratis parkeren ! voor ALC leden en bezoekers</p>
    </div>
    <div class="panel">
      <h2>{ICON["mail"]} E-mail</h2>
      <dl>
        <dt>Secretariaat</dt><dd><a href="mailto:secretaris@arnhemseluchtvaartclub.nl">secretaris@arnhemseluchtvaartclub.nl</a></dd>
        <dt>Website</dt><dd><a href="mailto:webmaster@arnhemseluchtvaartclub.nl">webmaster@arnhemseluchtvaartclub.nl</a></dd>
        <dt>Functionaris Gegevensbescherming</dt><dd><a href="mailto:fg@arnhemseluchtvaartclub.nl">fg@arnhemseluchtvaartclub.nl</a></dd>
      </dl>
    </div>
    <div class="panel">
      <h2>Bestuur</h2>
      <dl class="board">
        <dt>Voorzitter</dt><dd>Hans Bakker</dd>
        <dt>Secretaris</dt><dd>Ab Janssen</dd>
        <dt>Penningmeester</dt><dd>Thijs Brilleman</dd>
        <dt>Bestuurslid</dt><dd>Richard Hengeveld</dd>
        <dt>Bestuurslid</dt><dd>Jaap Brink</dd>
      </dl>
    </div>
  </div>
</section>
"""
    return page("contact", "Contact", body, "Contactgegevens, bouwavonden en bestuur van de Arnhemse Luchtvaart Club.")


def write(name, content):
    with open(os.path.join(OUT, name + ".html"), "w", encoding="utf-8") as f:
        f.write(content)


def main():
    write("index", build_home())
    write("modelvliegen", build_article("modelvliegen", "Modelvliegen"))
    write("links", build_article("links", "Links"))
    write("sponsoren", build_sponsoren())
    write("contact", build_contact())
    write("overig", build_overig())
    for slug, title in OVERIG:
        write(slug, build_article(slug, title, crumbs=[("overig.html", "Overig")]))
    print("Klaar:", len(OVERIG) + 6, "pagina's in", OUT)


if __name__ == "__main__":
    main()
