#!/usr/bin/env python3
"""Bouwt de twee tekstpagina's van het register: methode.html en over.html.

Waarom hier en niet als omgezette markdown: METHOD.md, README.md, CONTRIBUTING.md
en GOVERNANCE.md zijn Engelstalige repositorydocumenten, geschreven voor wie de
bron leest. Het publiek van deze site is Nederlands en zit niet op GitHub. Een
geplakte omzetting zou dus een Engelse pagina opleveren met koppen die naar
bestandsnamen verwijzen.

De inhoud komt uit die documenten, de volgorde ook, en de nummering van de
stappen is dezelfde, zodat "stap 4 van de methode" op beide plekken hetzelfde
betekent. De Engelse brontekst blijft de vindplaats voor wie citeert, en staat
onderaan gelinkt.
"""
import importlib.util, pathlib

# site.py heet net zo als een module van Python zelf, en die staat bij het
# starten al in sys.modules. Een gewone import levert dus de verkeerde op.
_p = pathlib.Path(__file__).resolve().parent / "site.py"
_spec = importlib.util.spec_from_file_location("dpe_site", _p)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "register"
GH = "https://github.com/Apolloccrypt/dpe-registry"
e = S.e

CSS = r"""
.wrap{padding-bottom:20px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--accent);margin:26px 0 8px}
h1{font-size:clamp(27px,4.2vw,40px);margin:0;letter-spacing:-.025em}
.lede{font-size:18px;color:var(--ink-2);max-width:64ch;margin:14px 0 0}
h2{font-size:23px;margin:46px 0 10px;letter-spacing:-.02em}
h3{font-size:16.5px;margin:0 0 6px}
p{max-width:70ch}
.note{color:var(--ink-2);max-width:70ch}
.stap{display:grid;grid-template-columns:auto 1fr;gap:0 20px;padding:22px 0;
 border-top:1px solid var(--line-2)}
@media(max-width:560px){.stap{grid-template-columns:1fr;gap:0}}
.stap .nr{font-family:var(--mono);font-size:12px;color:var(--accent);padding-top:4px;
 white-space:nowrap;font-weight:600}
.stap h3{font-size:19px;font-weight:600;letter-spacing:-.015em;margin:0 0 8px}
.stap p{margin:0 0 10px;color:var(--ink-2);font-size:15px}
.stap ul{margin:0 0 10px;padding-left:18px;color:var(--ink-2);font-size:14.5px}
.stap li{margin-bottom:5px}
.stap .kern{background:var(--soft);border:1px solid var(--aline);border-radius:8px;
 padding:11px 14px;font-size:14px;color:var(--ink);margin:0 0 10px}
.stap .kern b{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;
 text-transform:uppercase;color:var(--accent);margin-bottom:3px;font-weight:600}
.grens{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:11px;
 padding:20px 22px;margin-top:26px}
.grens h3{color:var(--warn-ink);font-size:17px}
.grens p{color:var(--warn-ink);margin:0 0 10px;font-size:14.5px}
.grens ul{margin:0;padding-left:18px;color:var(--warn-ink);font-size:14.5px}
.tab{width:100%;border-collapse:collapse;margin:8px 0 0;font-size:14.5px}
.tab th{text-align:left;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;
 text-transform:uppercase;color:var(--ink-3);font-weight:600;padding:0 16px 8px 0;
 border-bottom:1px solid var(--line)}
.tab td{padding:11px 16px 11px 0;border-bottom:1px solid var(--line-2);vertical-align:top;
 color:var(--ink-2)}
.tab td:first-child{color:var(--ink);font-weight:500;width:34%}
@media(max-width:620px){.tab td:first-child{width:40%}}
.kaarten{display:grid;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));gap:16px;margin-top:8px}
.kaart{background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:18px 20px;
 box-shadow:var(--shadow)}
.kaart .tijd{font-family:var(--mono);font-size:9.5px;letter-spacing:.09em;text-transform:uppercase;
 color:var(--ink-3);display:block;margin-bottom:6px}
.kaart p{font-size:14px;color:var(--ink-2);margin:0}
.kaart p+p{margin-top:9px}
.check{list-style:none;padding:0;margin:8px 0 0;max-width:70ch}
.check li{padding:9px 0 9px 26px;border-bottom:1px solid var(--line-2);position:relative;
 font-size:14.5px;color:var(--ink-2)}
.check li:before{content:"";position:absolute;left:4px;top:15px;width:9px;height:9px;
 border:1.5px solid var(--accent);border-radius:2px}
.niet{border-left:3px solid var(--line);padding-left:16px;margin:8px 0 0;max-width:70ch}
.niet li{font-size:14.5px;color:var(--ink-2);margin-bottom:8px}
.niet b{color:var(--ink)}
.versie{background:var(--surface-2);border:1px solid var(--line);border-radius:10px;
 padding:16px 20px;margin-top:26px;font-size:14px;color:var(--ink-2)}
.versie b{color:var(--ink)}
.bron{margin-top:26px;font-size:13.5px;color:var(--ink-3);max-width:70ch}
blockquote{margin:0 0 12px;padding:12px 16px;background:var(--surface-2);border:1px solid var(--line);
 border-radius:8px;font-size:14px;color:var(--ink-2);max-width:70ch}
"""

# De tien stappen uit METHOD.md, in dezelfde volgorde en met dezelfde nummers.
STAPPEN = [
    ("1", "Leg de reikwijdte vast voordat je meet",
     ["Achteraf beslissen wat je onderzocht hebt, is hoe selectieve uitkomsten ontstaan. "
      "Schrijf dit dus eerst op."],
     ["Welke systemen, precies benoemd. Eén domein, één appversie, één firmwarebouw.",
      "Welke fouten uit de catalogus je toetst. Op alles toetsen is geen reikwijdte maar een hoop.",
      "Vanuit welk land je meet, en waarom. Toestemmingsschermen en telemetrie verschillen per "
      "regio, en een Nederlandse bevinding gemeten via een Amerikaanse uitgang is geen "
      "Nederlandse bevinding.",
      "Waaraan je zou concluderen dat de fout er niet is. Bepaal dat voordat je kijkt."],
     ""),
    ("2", "Zet de meting zo op dat hij iets betekent",
     ["Bij apparaten neem je op bij de router en niet op het apparaat zelf. Een apparaat is niet "
      "de aangewezen partij om te melden wat het verstuurt, en dat is precies waarom je meet."],
     [], "tabel"),
    ("3", "Neem eerst een nulmeting",
     ["Leg vast wat het systeem doet als je er niets mee doet. Bij een website is dat de opname "
      "zonder enige aanraking: laad de pagina, raak niets aan, wacht lang genoeg voor tags die "
      "later vuren, bewaar. Bij een apparaat is dat het stille venster: laat het aan staan en "
      "onaangeraakt, en neem lang genoeg op dat terugkerend gedrag zichtbaar wordt. "
      "Vierentwintig uur is niet overdreven voor iets met een dagritme.",
      "De meeste bevindingen komen hiervandaan, omdat dit laat zien wat er gebeurt zonder dat "
      "iemand ergens om vroeg."],
     [], ""),
    ("4", "Verander één ding tegelijk",
     ["Het sterkste bewijs in deze hele methode is een vergelijking, niet een waarneming. Eén "
      "opname met verkeer erin nodigt uit tot een discussie over de uitleg. Twee opnames die in "
      "precies één opzicht verschillen, laten daar geen ruimte voor.",
      "Voor toestemming zijn dat drie aparte opnames, elk met een vers profiel: niets aanraken, "
      "uitdrukkelijk weigeren, uitdrukkelijk aanvaarden. Lees de toestemmingsstand daarna terug, "
      "want een klik die niet is geregistreerd meet een mislukte klik en geen holle weigering.",
      "Bij apparaten meet je met de instelling aan, dan uit, dan opnieuw na een herstart en na een "
      "update. Een instelling die een update niet overleeft, is een andere bevinding dan een "
      "instelling die nooit werkte."],
     [], ""),
    ("5", "Loop de catalogus af, niet je onderbuik",
     ["Toets voor elke fout in je reikwijdte de indicator tegen de opname. Gebruik de meetwijze "
      "die bij de fout staat, en niet een variant die je halverwege zelf bedacht."],
     ["Schrijf verkeer toe via de pageref in de HAR of via de keten van initiatoren. Nooit via de "
      "referer-header: die is te vervalsen en meetgereedschap vervalst hem standaard. Deze ene "
      "regel voorkomt de meest gemaakte fout in dit vakgebied.",
      "Leg ook vast wat je niet vond. “Getoetst, niet aangetroffen” is informatie, en een "
      "onderzoek waarin alleen treffers voorkomen zegt niets over de dekking."],
     ""),
    ("6", "Probeer je eigen bevinding onderuit te halen",
     ["Bij elke fout staat wat hem zou ontkrachten. Werk die lijst af en noteer per punt de "
      "uitkomst: uitgesloten, niet uitgesloten, of niet getoetst met de reden erbij.",
      "Dit is de stap die een bevinding onderscheidt van een beschuldiging, en het is de stap die "
      "wordt overgeslagen. Een niet getoetste ontkrachting is geen tekortkoming zolang je hem "
      "noemt; een verzwegen ontkrachting wel.",
      "Kun je iets niet uit de opname afmaken, schrijf dan op wat het wél zou afmaken. Vaak is dat "
      "een vraag die alleen de beheerder kan beantwoorden, en die vraag hoort in je verzoek om "
      "wederhoor."],
     [], ""),
    ("7", "Stel de duur vast waar dat kan",
     ["Eén opname is een moment. Gearchiveerde broncode, momentopnamediensten en "
      "versiegeschiedenissen maken van dat moment een periode, en een periode is een andere soort "
      "bewering: een ononderbroken reeks van jaren valt niet met terugwerkende kracht te "
      "herstellen.",
      "Rapporteer de strikt ononderbroken reeks, en meld oudere losse sporen apart. Continuïteit "
      "overdrijven is de makkelijkste manier om een verder solide bevinding te verliezen."],
     [], ""),
    ("8", "Laat iemand anders het naspelen",
     ["Onafhankelijke herhaling is meer waard dan hoeveel extra metingen van jezelf ook. Er zijn "
      "twee routes en beide zijn goedkoop."],
     ["Vraag een derde de reproductie bij de fout te draaien en te melden wat hij zag.",
      "Draai een openbare scanner die een blijvend resultaatadres onder eigen beheer bewaart. Dat "
      "resultaat is niet van jou, kan achteraf niet door de beheerder worden aangepast, en "
      "overleeft een opruimactie na publicatie."],
     ""),
    ("9", "Vraag wederhoor voordat je publiceert",
     ["Geef de beheerder de bevinding, het ruwe meetbestand en de reproductie, met een termijn. "
      "Vraag uitdrukkelijk of er iets ontbreekt of verkeerd gelezen is; een fout die vóór "
      "publicatie boven tafel komt, kost niemand iets.",
      "Laat een partij publicatie niet blokkeren door te zwijgen, en laat niemand een meting "
      "intrekken omdat het inmiddels is opgelost. Noteer de oplossing met de datum erbij. Een "
      "meting stelt een moment vast, en dat moment blijft bestaan.",
      "Leg de reactie woordelijk vast, ook als die uitblijft. Dat een partij niet reageerde is "
      "zelf een feit, en een reactie samenvatten is hoe ruzies beginnen."],
     [], "termijn"),
    ("10", "Publiceer zo dat het na te kijken is",
     ["Vermeld elke keer:"],
     [], "check"),
]

OPZET = [
    ("Vers profiel per opname",
     "Een gebruikt profiel kan toestemming van eerder meedragen, en dan is elke bewering over het "
     "moment vóór de toestemming waardeloos"),
    ("Eén variabele per opname",
     "Verschillen er twee dingen tussen twee opnames, dan bewijst het verschil niets"),
    ("Het land van uitgang vastleggen",
     "Toestemmingsschermen zijn vaak op regio gericht; noteer het ook als het niet uit lijkt te maken"),
    ("Versies vastleggen",
     "Browser, scanner, firmware, appbouw. Gedrag verandert tussen versies"),
    ("Het ruwe bestand bewaren",
     "HAR, PCAP of trace. Een samenvatting is geen bewijs"),
    ("Alles van een tijdstempel voorzien",
     "Zowel de opname als de toestemmingsgebeurtenis, zodat de volgorde vast te stellen is"),
]

PUBLICEER = [
    "welke fouten uit de catalogus je aantrof, met hun nummers",
    "de versie van de methode, en de versie van het gereedschap dat je gebruikte",
    "de meetdatum en het land van waaruit je mat",
    "welke ontkrachtingen je hebt uitgesloten en welke niet",
    "waar het ruwe meetbestand te krijgen is",
]

NIET_VASTGESTELD = [
    ("Onrechtmatigheid", "dat stelt de Autoriteit Persoonsgegevens of de rechter vast"),
    ("Opzet", "dat is vrijwel nooit te meten en meestal een bouwbesluit, geen plan"),
    ("Afwezigheid", "dat je het in één opname niet aantrof, is geen bewijs dat het er niet is"),
]


def stap_html(nr, kop, alinea, punten, extra):
    body = "".join(f"<p>{a}</p>" for a in alinea)
    if punten:
        body += "<ul>" + "".join(f"<li>{p}</li>" for p in punten) + "</ul>"
    if extra == "tabel":
        body += ('<table class="tab"><thead><tr><th scope="col">Eis</th>'
                 '<th scope="col">Waarom het uitmaakt</th></tr></thead><tbody>'
                 + "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in OPZET)
                 + "</tbody></table>")
    if extra == "termijn":
        body += ('<div class="kern"><b>Termijn</b>Dertig dagen is een redelijke standaard. Dat is '
                 'korter dan de negentig die voor softwarekwetsbaarheden gebruikelijk zijn, en dat '
                 'verschil is bewust: een tag uitzetten is niet hetzelfde als een patch bouwen, '
                 'testen en uitrollen. Verleng één keer als er een concreet herstelplan met een '
                 'datum tegenover staat.</div>')
    if extra == "check":
        body += '<ul class="check">' + "".join(f"<li>{e(c)}</li>" for c in PUBLICEER) + "</ul>"
        body += ('<p style="margin-top:16px">En vermeld wat je <b>niet</b> hebt vastgesteld.</p>'
                 '<ul class="niet">'
                 + "".join(f"<li><b>{e(a)}</b>: {e(b)}.</li>" for a, b in NIET_VASTGESTELD)
                 + "</ul><p>Dat kost je niets en het is de reden dat de rest van het werk "
                 "overeind blijft.</p>")
    return (f'<div class="stap"><div class="nr">{e(nr)}</div>'
            f'<div><h3>{e(kop)}</h3>{body}</div></div>')


def methode():
    stappen = "".join(stap_html(*s) for s in STAPPEN)
    body = f'''<div class="wrap">
{S.crumb(("Database", "./"), "Meetmethode")}
<p class="eyebrow">DPE-meetmethode {S.METHODE}</p>
<h1>Hoe je een meting doet die een ander kan nakijken</h1>
<p class="lede">Dit is de tegenhanger van de catalogus. De catalogus zegt wát een fout is, deze
pagina zegt hoe je ernaar zoekt. Wie een bevinding publiceert, noemt de versie erbij: een meting
onder methode {S.METHODE} is een andere bewering dan een meting onder 2.0.</p>

<p class="note" style="margin-top:20px">Het versienummer staat er met opzet. Zonder versie zijn
uitkomsten uit verschillende jaren stilletjes niet meer met elkaar te vergelijken, en dat merkt
niemand. Voor beveiliging bestaat de OWASP Testing Guide die deze rol vervult. Voor
gegevensbescherming bestond niets, en dat is de reden dat geen twee onderzoeken op elkaar
aansloten.</p>

<div class="grens">
  <h3>Voordat je iets doet: waar de grens ligt</h3>
  <p>Alles in deze methode laadt een systeem zoals een gewone bezoeker dat doet, en kijkt wat het
  uit zichzelf doet. Die grens is niet alleen juridische voorzichtigheid, hij is methodisch: wat je
  alleen ziet door in te loggen, gegevens in te sturen of een beveiliging te omzeilen, kan een
  derde niet naspelen, en een bevinding die niemand kan nakijken is geen bevinding.</p>
  <ul>
    <li>niet inloggen op accounts die niet van jou zijn</li>
    <li>geen formulieren invullen met echte gegevens</li>
    <li>geen authenticatie omzeilen</li>
    <li>niet meer belasting veroorzaken dan een normaal bezoek</li>
  </ul>
  <p style="margin-top:10px">Kun je een fout alleen achter zo'n grens vaststellen, noteer hem dan
  als gereconstrueerd in plaats van gemeten, en zeg dat erbij.</p>
</div>

<h2>De tien stappen</h2>
<p class="note">In deze volgorde. De nummers zijn dezelfde als in de brontekst, zodat "stap 4 van
de methode" overal hetzelfde betekent.</p>
{stappen}

<h2>Wat je hiermee kunt vragen</h2>
<p class="note">Je hoeft de methode niet zelf uit te voeren om hem te gebruiken. Eén zin in een
opdracht of een bestek maakt de uitkomst toetsbaar:</p>
<blockquote>Wij toetsen deze verwerking tegen de DPE-catalogus. Graag een meting van de opgenomen
bevindingen volgens DPE-meetmethode {S.METHODE}, met meetdatum, land van meting en de ruwe
meetbestanden. Termijn: [datum].</blockquote>
<p class="note">Op <a href="uitleg.html">van symptoom naar nummer</a> staat wat je daarna met de
uitkomst doet, en waaraan je merkt dat je een antwoord krijgt op een andere vraag dan je stelde.</p>

<div class="versie">
  <p style="margin:0 0 8px"><b>Versiegeschiedenis</b></p>
  <p style="margin:0 0 8px"><b>{S.METHODE}</b>, 26 juli 2026. Eerste gepubliceerde versie. Citeer
  als <i>DPE-meetmethode {S.METHODE}</i>.</p>
  <p style="margin:0">Een wijziging die verandert wat een meting betekent, krijgt een nieuw
  hoofdnummer. Formuleringen en voorbeelden krijgen een subnummer. Publiceer je onder een versie,
  dan blijft die versie op zijn eigen adres bereikbaar zolang deze catalogus bestaat.</p>
</div>

<p class="bron">Deze pagina is de Nederlandse uitgave van
<a href="{GH}/blob/main/METHOD.md">METHOD.md</a> in de bron. Dat document is de Engelse brontekst
en blijft de vindplaats voor wie citeert of vertaalt; wijkt deze pagina ervan af, dan geldt de
brontekst en horen wij het graag.</p>
</div>'''
    return (S.head(f"Meetmethode {S.METHODE} · DPE-register",
                   "Hoe je een meting doet die een ander kan nakijken: reikwijdte, nulmeting, "
                   "één variabele tegelijk, je eigen bevinding onderuit halen, en wat je publiceert.",
                   up="", cur="methode.html", css=CSS) + body + S.foot(up=""))


BIJDRAGEN = [
    ("5 minuten", "Speel een fout na",
     ["De goedkoopste nuttige bijdrage, en degene die de catalogus betrouwbaar maakt in plaats van "
      "alleen maar stellig. Kies een fout, volg de reproductie, en meld wat je zag. Elke fout heeft "
      "een route waarvoor je niets nodig hebt behalve een browser.",
      "Een mislukte reproductie is minstens zo waardevol. Vuurt onze indicator niet waar hij zou "
      "moeten, of juist wel waar hij niet zou moeten, dan klopt de fout niet en willen wij dat "
      "weten. Noem erbij vanuit welk land je mat."]),
    ("15 minuten", "Scherp een fout aan",
     ["Lees één fout kritisch en zeg wat er ontbreekt: een ontkrachting die wij niet noemden, een "
      "indicator die losser is dan hij lijkt, een grens die wij verkeerd trokken tegenover een "
      "buurfout, of een betere titel als wij iets slecht genoemd hebben."]),
    ("30 minuten", "Voeg een rechtsgebied of een uitspraak toe",
     ["De fouten zijn in de hele EER dezelfde; alleen de verwijzing verschilt. Op dit moment staan "
      "er alleen Nederlandse en Europese bepalingen in.",
      "Stuur de nationale bepaling die in jouw land dezelfde Europese regel uitvoert. Voor "
      "jurisprudentie: de ECLI, de kern in twee zinnen, en welke fout het raakt. Uitspraken die een "
      "fout juist beperken zijn extra welkom, want die maken hem bruikbaar in een discussie in "
      "plaats van alleen in een aanklacht."]),
    ("een middag", "Schrijf een fout of een script",
     ["Een fout die wij nog niet beschreven, of een reproductiescript voor een fout die er nog geen "
      "heeft. In WANTED.md staat waar wij werkelijk op vastlopen, en dat is een beter beginpunt dan "
      "een leeg sjabloon.",
      "Wij meten vooral browsers. Werk je aan firmware, routers, televisies, auto's of apps, dan "
      "zie je dingen die wij niet kunnen zien."]),
]

INHOUD = [
    ("Het mechanisme", "hoe de fout ontstaat, technisch, zonder een leverancier te noemen"),
    ("Een indicator", "het concrete ding dat het beslecht, te controleren zonder uitleg"),
    ("Eisen aan de meting", "de voorwaarden waaraan een meting moet voldoen, anders levert zij een "
                            "zelfverzekerd verkeerd antwoord op"),
    ("Ontkrachtingen", "wat de bevinding zou weerleggen, en of dat uit een opname te halen is"),
    ("Een reproductie", "één route die geen gereedschap nodig heeft dat van dit project is"),
    ("Wettelijk kader", "welke regels het raakt, per rechtsgebied, en de standaardtegenwerpingen "
                        "met het antwoord erop"),
    ("In de praktijk", "wat je in een DPIA toetst, hoe je het in een inkoopeis formuleert, en wat "
                       "je bij een klacht meelevert"),
]

NIET_MAG = [
    ("Ernst toekennen", "die staat niet in het schema en mag er niet in zonder een nieuw "
                        "hoofdnummer. Wegen hoort bij wie de fout op een concreet geval toepast."),
    ("Een partij noemen", "geen organisatie, geen product, geen domein, nooit, in geen enkel veld. "
                          "Een fout die een merknaam nodig heeft om begrepen te worden, is nog niet "
                          "goed beschreven."),
    ("Stil iets wijzigen", "elke wijziging is een toegevoegde regel in de wijzigingslijst, en die "
                           "lijst is alleen aan te vullen. Een fout waarvan eerdere regels zijn "
                           "aangepast, wordt afgewezen."),
    ("Een nummer hergebruiken", "niet na intrekking, niet na samenvoeging. Elders bestaan "
                                "verwijzingen en die moeten blijven werken."),
    ("Een fout zonder ontkrachting aannemen", "als niets hem zou kunnen weerleggen, is het geen "
                                              "bevinding maar een mening."),
]


def over():
    kaarten = "".join(
        f'<div class="kaart"><span class="tijd">{e(t)}</span><h3>{e(k)}</h3>'
        + "".join(f"<p>{e(a)}</p>" for a in al) + "</div>" for t, k, al in BIJDRAGEN)
    inhoud = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in INHOUD)
    nietmag = "".join(f"<li><b>{e(a)}</b> {e(b)}</li>" for a, b in NIET_MAG)

    body = f'''<div class="wrap">
{S.crumb(("Database", "./"), "Over dit register")}
<p class="eyebrow">Over dit register</p>
<h1>Een nummer voor wat geen kwetsbaarheid is</h1>
<p class="lede">Onderzoekers vinden steeds dezelfde dingen, en die dingen hebben geen naam. Dus
begint elke publicatie opnieuw: dezelfde uitleg, dezelfde juridische onderbouwing, dezelfde
tegenwerpingen nog eens beantwoord. Met een nummer gebeurt dat één keer.</p>

<h2>Waar het gat zat</h2>
<p class="note">Een router die uit zichzelf contact zoekt met een server in een ander land, krijgt
geen CVE. Er valt niets te misbruiken: het systeem doet wat de bouwer bedoelde, en juist die
bedoeling is het bezwaar. Er was tot nu toe ook geen nummer om naar te verwijzen. Dat gat is de
reden dat dit register bestaat.</p>
<p class="note">Elke fout hier beschrijft gedrag van een systeem, met een indicator die zonder
interpretatie te controleren is, en met de lijst van wat de bevinding zou ontkrachten erbij. Dat
laatste is het verschil tussen een bevinding en een beschuldiging.</p>

<h2>Wat er in een fout staat</h2>
<table class="tab"><thead><tr><th scope="col">Onderdeel</th><th scope="col">Waarvoor</th></tr>
</thead><tbody>{inhoud}</tbody></table>
<p class="note" style="margin-top:16px">Elke fout staat op een eigen permanent adres, met dezelfde
inhoud als JSON ernaast. Nummers worden nooit hergebruikt: een ingetrokken fout houdt zijn nummer
en zijn adres, met de reden erbij, omdat er elders naar verwezen wordt.</p>

<h2>Wat dit uitdrukkelijk niet is</h2>
<ul class="niet">
  <li><b>Geen kwetsbaarhedenlijst.</b> Er valt niets te misbruiken. Wie een kwetsbaarheid vindt,
  moet bij CVE zijn en niet hier.</li>
  <li><b>Geen aanklacht.</b> Er staat geen organisatie, geen product en geen domein in dit
  register. Wie vaststelt dat een concreet systeem een van deze fouten vertoont, publiceert dat
  zelf, onder eigen naam, met het nummer erbij. Daardoor blijven de definities bruikbaar lang
  nadat een individuele site is opgeruimd.</li>
  <li><b>Geen ernstscore.</b> Geen cijfer, geen weging van schade, met opzet. CVE weegt ook niet;
  dat doet NVD apart. Hoe zwaar een concreet geval weegt, hangt van dat geval af en hoort bij wie
  de fout toepast.</li>
  <li><b>Geen oordeel over rechtmatigheid.</b> Of een concreet geval onrechtmatig is, stelt de
  Autoriteit Persoonsgegevens of de rechter vast.</li>
</ul>

<h2>Hoe je meedoet</h2>
<p class="note">Je hoeft geen onderzoeker te zijn en je hebt geen toestemming nodig. Wat je ook
bijdraagt, je naam blijft aan de fout hangen, permanent en citeerbaar. Anoniem mag ook en verandert
niets aan de behandeling.</p>
<p class="note">Omdat hier geen enkele organisatie bij naam staat, kost meedoen je niets: je
beschrijft een soort fout, je beschuldigt niemand. Op alles geldt dezelfde grens als in de methode:
laden zoals een gewone bezoeker, niet inloggen, niets insturen, niets omzeilen.</p>
<div class="kaarten">{kaarten}</div>
<p class="note" style="margin-top:18px">Sturen doe je via een issue. Een pull request mag, maar
wordt niet verwacht; losse aantekeningen in een issue zijn ook goed, dan schrijven wij het uit en
sta jij als bijdrager vermeld. Reken op antwoord binnen vijf werkdagen, ook als het antwoord nee
is, met de reden erbij. Een inzending die blijft hangen is onze fout en daar mag je ons aan
houden.</p>
<p class="note"><a href="{GH}/issues">Een fout of correctie melden</a> &middot;
<a href="{GH}/blob/main/CONTRIBUTING.md">de volledige bijdragehandleiding</a> &middot;
<a href="{GH}/blob/main/WANTED.md">waar wij op vastlopen</a></p>

<h2>Wie beslist wat</h2>
<p class="note">Een catalogus die van één persoon afhangt, is geen standaard. Dat is nu de
werkelijkheid en dit onderdeel bestaat om die afhankelijkheid zichtbaar en op termijn overbodig te
maken. Er zijn twee rollen. Een <b>bijdrager</b> is iedereen: die stelt fouten voor, speelt ze na,
scherpt een ontkrachting aan of betoogt dat een fout niet klopt. Een <b>redacteur</b> mag een
voorstel aannemen, een nummer toekennen en een fout intrekken, en staat bij naam in de bron zodat
zichtbaar is wie de catalogus vormt.</p>
<p class="note">Redacteur worden kan: onderzoeksgroepen, maatschappelijke organisaties, redacties
en toezichthouders met een aantoonbaar belang. De voorwaarden zijn onderschrijving van de
spelregels en drie aangenomen fouten of tien reproducties. Die drempel is laag met opzet: hij moet
vaststellen dat iemand de methode kent, niet de deur dichthouden.</p>

<h3 style="margin-top:26px">Wat een redacteur niet mag</h3>
<ul class="niet">{nietmag}</ul>
<p class="note" style="margin-top:14px">Een redacteur beslist niet over een fout die werk raakt
waarvoor hij betaald is. Die situatie is niet denkbeeldig: wie een standaard onderhoudt, is
meestal ook degene die gevraagd wordt hem toe te passen. Waar er diensten bovenop worden verkocht,
horen die in een aparte rechtspersoon te zitten, en het hoort zichtbaar te zijn welke welke is.
Onze eigen infrastructuur meten is uitdrukkelijk aangemoedigd: wie anderen meet, hoort zichzelf te
meten.</p>

<h2>Als dit ophoudt</h2>
<p class="note">De fouten, het schema en het juridische materiaal staan onder CC BY 4.0, het
gereedschap onder MIT, in een openbare bron. Iedereen mag dit register voortzetten of overnemen,
inclusief de nummering. Dat is geen noodplan maar het punt: een verwijzing die vandaag wordt
gemaakt, moet over tien jaar nog iets betekenen, of de mensen erachter er nu nog zijn of niet.</p>
<p class="note">Onderdeel van
<a href="https://totaledigitalewaarborging.nl/">Totale Digitale Waarborging</a>, vierde as: kun je
het juridisch verantwoorden?</p>

<p class="bron">Deze pagina vat samen wat in de bron staat in
<a href="{GH}/blob/main/README.md">README.md</a>,
<a href="{GH}/blob/main/CONTRIBUTING.md">CONTRIBUTING.md</a> en
<a href="{GH}/blob/main/GOVERNANCE.md">GOVERNANCE.md</a>. Die documenten zijn Engelstalig en
gelden bij verschil.</p>
</div>'''
    return (S.head("Over dit register · DPE",
                   "Wat het DPE-register is, waarom het bestaat, hoe je bijdraagt en onder welke "
                   "voorwaarden.", up="", cur="over.html", css=CSS) + body + S.foot(up=""))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "methode.html").write_text(methode(), encoding="utf-8")
    (OUT / "over.html").write_text(over(), encoding="utf-8")
    print(f"methode.html en over.html -> {OUT}")


if __name__ == "__main__":
    build()
