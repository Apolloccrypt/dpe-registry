#!/usr/bin/env python3
"""Gedeelde onderdelen van de registersite.

Eén navigatie, één opmaak, één voettekst. Elke pagina die hier doorheen gaat
ziet er hetzelfde uit, en een wijziging aan de navigatie hoeft maar op een plek.

Hier staat ook het geraamte van het document: doctype, taal, tekenset en
viewport. Die stonden nergens, waardoor de pagina's op een telefoon als
verkleinde bureaubladpagina's werden getekend en een verkeerd geraden tekenset
de accenten kon slopen.

De doelserver draait script-src 'self'. Er staat daarom nooit een inline
<script> in een pagina; alles wat JavaScript nodig heeft, laadt een eigen
.js-bestand.
"""
import html

BASE = "https://totaledigitalewaarborging.nl/register"
SITE = "https://totaledigitalewaarborging.nl/"
METHODE = "1.0"

NAV = [("", "Database", "Zoek en filter alle fouten"),
       ("uitleg.html", "Van symptoom naar nummer", "Voor wie niet meet"),
       ("methode.html", "Meetmethode", "Hoe je ernaar zoekt"),
       ("over.html", "Over dit register", "Wat het is en hoe je meedoet")]

# Eén set Nederlandse labels voor alle generatoren. Stond eerst drie keer los,
# waarvan één keer in het Engels.
FAM = {"consent": "Toestemming", "data": "Gegevens", "chain": "Keten",
       "transfer": "Doorgifte", "transparency": "Transparantie",
       "retention": "Bewaring", "telemetry": "Telemetrie", "method": "Methode"}
SYS = {"web": "web", "mobile-app": "app", "firmware": "firmware", "iot": "IoT",
       "vehicle": "voertuig", "desktop": "desktop", "api": "API",
       "network-device": "netwerkapparaat", "installation": "opstelling",
       "backend": "achterliggend systeem"}
STATUS = {"active": "actief", "superseded": "vervangen", "deprecated": "ingetrokken",
          "draft": "concept"}
METHOD = {"network-with-identifier": "netwerkopname met identifier",
          "network-observed": "netwerkopname",
          "differential": "vergelijking van twee opnames",
          "document-comparison": "meting naast de eigen verklaring",
          "static-source": "broncode of pakketinhoud",
          "third-party-confirmed": "bevestigd met een stuk van een derde",
          "archival-continuous": "doorlopende waarneming uit een archief"}


def e(s):
    return html.escape(str(s), quote=True)


def head(title, desc="", up="", cur=None, css="", extra=""):
    """up is het pad terug naar de registerwortel, leeg of '../'.

    cur is de href uit NAV die op deze pagina hoort, of None voor een pagina
    die onder de database hangt maar er niet zelf een tabblad van is.
    """
    mark = ' aria-current="page"'
    nav = "".join(f'<a href="{up}{h}"{mark if h == cur else ""}>{e(t)}</a>'
                  for h, t, _ in NAV)
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="color-scheme" content="light">
<style>{CSS}{css}</style>{extra}
</head>
<body>
<a class="skip" href="#inhoud">Naar de inhoud</a>
<div class="topbar"><div class="tb">
  <a class="brand" href="{SITE}">
    <span class="bm">TDW</span><span class="bt">Totale Digitale Waarborging</span></a>
  <nav class="mainnav" aria-label="Register">{nav}</nav>
</div></div>
<main id="inhoud">
"""


def foot(up="", scripts=()):
    """scripts is een lijst bestandsnamen; altijd extern, nooit inline, want de
    doelserver blokkeert inline script en doet dat zonder zichtbare fout."""
    js = "".join(f'<script src="{up}{s}"></script>' for s in scripts)
    return f"""</main>
<footer class="sitefoot"><div class="in">
  <div class="ff">
    <div>
      <b>DPE-register</b>
      <p>Genummerde fouten in de omgang met persoonsgegevens, voor wat geen kwetsbaarheid is en
      daarom geen CVE krijgt. Onderdeel van Totale Digitale Waarborging, as 04.</p>
    </div>
    <div>
      <b>Pagina's</b>
      <p><a href="{up}">de database</a><br>
      <a href="{up}uitleg.html">van symptoom naar nummer</a><br>
      <a href="{up}methode.html">de meetmethode</a><br>
      <a href="{up}over.html">over dit register</a></p>
    </div>
    <div>
      <b>Machineleesbaar</b>
      <p><a href="{up}all.json">de hele database als JSON</a><br>
      <a href="{up}sitemap.xml">sitemap</a><br>
      <a href="https://github.com/Apolloccrypt/dpe-registry">bron en bijdragen</a></p>
    </div>
    <div>
      <b>Voorwaarden</b>
      <p>Elke fout beschrijft gedrag van een systeem, niet van een organisatie. Er wordt geen ernst
      toegekend. Of een concreet geval onrechtmatig is, stelt de Autoriteit Persoonsgegevens of de
      rechter vast. Nummers zijn permanent en worden nooit hergebruikt.</p>
    </div>
  </div>
  <p class="fl">Database onder CC BY 4.0, gereedschap onder MIT.</p>
</div></footer>
{js}
</body>
</html>
"""


def crumb(*parts):
    """Kruimelpad. Een tuple (tekst, href) wordt een link, een losse tekst niet."""
    out = []
    for p in parts:
        if isinstance(p, tuple):
            out.append(f'<a href="{e(p[1])}">{e(p[0])}</a>')
        else:
            out.append(f"<span>{e(p)}</span>")
    return '<nav class="bar" aria-label="Kruimelpad">' + '<span class="sp">/</span>'.join(out) + "</nav>"


CSS = """
:root{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;--ink-3:#8B8B97;
 --line:#E9E9F0;--line-2:#F3F3F8;--accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;
 --green:#3CA951;--gold:#EFB118;--coral:#FF725C;
 --ok:#3CA951;--ok-bg:#EAF6EE;--ok-line:#CDE9D6;--warn-bg:#FBF3DD;--warn-line:#EFDFAE;--warn-ink:#8A6200;
 --shadow:0 1px 2px rgba(20,20,50,.04),0 14px 34px -20px rgba(20,20,50,.16);
 --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 --mono:"DM Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
 --serif:"Iowan Old Style",Georgia,serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;
 line-height:1.55;overflow-wrap:break-word}
.in{max-width:1180px;margin:0 auto;padding:0 20px}
.wrap{max-width:860px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-9999px;top:0;background:var(--accent);color:#fff;padding:10px 16px;
 border-radius:0 0 8px 0;z-index:60;text-decoration:none}
.skip:focus{left:0}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.topbar{background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.tb{max-width:1180px;margin:0 auto;padding:6px 20px;display:flex;gap:18px;align-items:center;
 flex-wrap:wrap;min-height:56px}
.brand{display:flex;gap:9px;align-items:center;text-decoration:none;color:inherit}
.bm{font-family:var(--mono);font-size:11px;letter-spacing:.1em;background:var(--ink);color:var(--surface);
 padding:4px 7px;border-radius:5px}
.bt{font-weight:600;font-size:14.5px;letter-spacing:-.01em}
@media(max-width:620px){.bt{display:none}}
.mainnav{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto}
.mainnav a{padding:7px 12px;border-radius:7px;text-decoration:none;color:var(--ink-2);font-size:13.5px}
.mainnav a:hover{background:var(--surface-2);color:var(--ink)}
.mainnav a[aria-current=page]{background:var(--soft);color:var(--accent);font-weight:600}
@media(max-width:520px){.mainnav{margin-left:8px}.mainnav a{padding:6px 9px;font-size:12.5px}}
h1{font-size:clamp(24px,3.2vw,34px);font-weight:600;letter-spacing:-.024em;margin:26px 0 4px;
 line-height:1.14;text-wrap:balance}
h2{font-size:22px;font-weight:600;letter-spacing:-.018em;margin:34px 0 10px}
h3{font-size:17px;font-weight:600;margin:0 0 7px}
p{margin:0 0 12px}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
code{font-family:var(--mono);font-size:12.5px;background:var(--line-2);padding:1px 6px;border-radius:4px;
 overflow-wrap:anywhere}
.sub{color:var(--ink-2);margin:0 0 22px;max-width:72ch;font-size:15.5px}
.bar{padding:14px 0;font-size:13px;display:flex;gap:8px;flex-wrap:wrap;align-items:baseline;
 border-bottom:1px solid var(--line)}
.bar a{color:var(--accent);text-decoration:none}
.bar a:hover{text-decoration:underline}
.bar .sp{color:var(--ink-3)}
.sitefoot{margin-top:60px;background:var(--surface-2);border-top:1px solid var(--line);padding:34px 0 26px}
.ff{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:26px}
.ff b{display:block;font-size:14px;margin-bottom:6px}
.ff p{font-size:13px;color:var(--ink-3);line-height:1.6;margin:0}
.ff a{color:var(--accent)}
.fl{margin:22px 0 0;font-size:12.5px;color:var(--ink-3)}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""
