#!/usr/bin/env python3
"""Bouwt de publiceerbare site: een pagina per fout, met een eigen URL.

Uitgangspunt is citeerbaarheid. Wie naar DPE-2026-0001 verwijst moet over tien
jaar nog op een pagina uitkomen, ook als de index er dan anders uitziet, ook als
er geen JavaScript draait, en ook als deze generator allang vervangen is. Daarom:

  - een statische pagina per entry, zonder afhankelijkheid van JavaScript
  - dezelfde inhoud als JSON ernaast, voor wie het machinaal leest
  - een citeerblok op elke pagina, zodat verwijzen geen denkwerk kost
  - een index die alleen navigatie is, nooit de enige plek waar iets staat

De navigatie, de opmaak en de voettekst komen uit tools/site.py, zodat elke
pagina van dit register er hetzelfde uitziet en een wijziging maar op één plek
hoeft.

Uitvoer in site/register/, klaar om onder een pad op de site te hangen.
"""
import glob, importlib.util, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "site" / "register"

# site.py heet net zo als een module van Python zelf, en die staat bij het
# starten al in sys.modules. Een gewone import levert dus de verkeerde op.
_spec = importlib.util.spec_from_file_location("dpe_site", ROOT / "tools" / "site.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

BASE = S.BASE
TODAY = "2026-07-26"
e, FAM, SYS, STATUS, METHOD = S.e, S.FAM, S.SYS, S.STATUS, S.METHOD

TIER = {"manual": "met de hand", "bookmarklet": "bookmarklet", "script": "script",
        "suite": "gereedschapskist"}
CHK = {"automated": "automatisch te toetsen", "manual": "met de hand te toetsen",
       "not-from-capture": "niet uit de opname te halen"}
IFT = {"drop": "dan vervalt de bevinding", "reclassify": "dan hoort hij ergens anders",
       "weaken": "dan wordt hij zwakker"}
MAAND = ["", "januari", "februari", "maart", "april", "mei", "juni", "juli",
         "augustus", "september", "oktober", "november", "december"]


def datum(iso):
    y, m, d = iso[:10].split("-")
    return f"{int(d)} {MAAND[int(m)]} {y}"


CSS = """
.wrap{padding-bottom:20px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--accent);margin:26px 0 8px}
h1{font-size:clamp(26px,4vw,36px);margin:0;letter-spacing:-.022em}
.sum{font-size:18px;color:var(--ink-2);margin:10px 0 0;max-width:62ch}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:16px}
.tag{font-family:var(--mono);font-size:10px;letter-spacing:.06em;padding:3px 9px;border-radius:999px;
 background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.tag.fam{background:var(--soft);border-color:var(--aline);color:var(--accent)}
.nv{margin:22px 0 0;background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:9px;
 padding:14px 17px;font-size:14px;color:var(--warn-ink)}
.nv b{display:block;margin-bottom:3px}
section{padding:22px 0;border-bottom:1px solid var(--line-2)}
section h2{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--ink-3);margin:0 0 10px;font-weight:600}
section p{margin:0 0 10px;max-width:70ch}
section ul{margin:0;padding-left:18px;color:var(--ink-2);font-size:14.5px}
section li{margin-bottom:4px}
.ind{font-family:var(--mono);font-size:13px;line-height:1.65;background:var(--surface-2);
 border:1px solid var(--line);border-left:3px solid var(--accent);padding:13px 15px;
 border-radius:0 8px 8px 0}
.qod{margin-top:11px;font-size:12.5px;color:var(--ink-2);display:flex;gap:18px;flex-wrap:wrap}
.qod b{font-family:var(--mono);font-size:11px;color:var(--ink-3);font-weight:600;
 letter-spacing:.05em;text-transform:uppercase;margin-right:6px}
.fal{list-style:none;padding:0}
.fal li{display:grid;grid-template-columns:auto 1fr;gap:5px 10px;padding-bottom:9px;
 border-bottom:1px dotted var(--line);align-items:baseline}
.fal li:last-child{border-bottom:0}
.k{font-family:var(--mono);font-size:9px;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;
 border-radius:999px;white-space:nowrap}
.k-automated{background:var(--ok-bg);border:1px solid var(--ok-line);color:var(--ok)}
.k-manual{background:var(--soft);border:1px solid var(--aline);color:var(--accent)}
.k-not-from-capture{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink)}
.fal .c{font-size:14.5px;color:var(--ink)}
.n,.i{grid-column:2;font-size:12.5px;color:var(--ink-3)}
.i{font-family:var(--mono);font-size:10px;letter-spacing:.05em;text-transform:uppercase}
@media(max-width:560px){.fal li{grid-template-columns:1fr}.n,.i{grid-column:1}}
.askq{background:var(--soft);border:1px solid var(--aline);border-radius:9px;padding:15px 18px;margin-bottom:14px}
.askq span{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;text-transform:uppercase;
 color:var(--accent);margin-bottom:4px}
.askq b{font-size:16.5px;font-weight:600;line-height:1.4}
.prg{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:1px;background:var(--line);
 border:1px solid var(--line);border-radius:9px;overflow:hidden}
.pr{background:var(--surface);padding:13px 15px}
.pr-h{font-family:var(--mono);font-size:9px;letter-spacing:.09em;text-transform:uppercase;
 color:var(--ink-3);margin-bottom:5px}
.pr p{margin:0;font-size:13.5px;color:var(--ink-2);line-height:1.55}
.rb{border-left:2px solid var(--line);padding-left:14px;margin-bottom:14px}
.rq{font-weight:600;font-size:14.5px;margin:0 0 3px}
.ra{font-family:var(--serif);font-size:15px;color:var(--ink-2);margin:0;line-height:1.6}
.cite{background:var(--surface-2);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-top:26px}
.cite h2{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--ink-3);margin:0 0 12px;font-weight:600}
.cite dl{display:grid;grid-template-columns:auto 1fr;gap:8px 16px;margin:0;font-size:13.5px}
@media(max-width:560px){.cite dl{grid-template-columns:1fr;gap:2px 0}
 .cite dd{margin-bottom:10px}}
.cite dt{font-family:var(--mono);font-size:9.5px;letter-spacing:.09em;text-transform:uppercase;
 color:var(--ink-3);padding-top:3px}
.cite dd{margin:0;font-family:var(--mono);font-size:12.5px;overflow-wrap:anywhere}
.cite .plain{font-family:var(--sans);font-size:14px}
.rel{display:flex;gap:7px;flex-wrap:wrap;margin-top:4px}
.rel a{font-family:var(--mono);font-size:11px;padding:5px 11px;border-radius:999px;background:var(--surface-2);
 border:1px solid var(--line);color:var(--ink-2);text-decoration:none}
.rel a:hover{background:var(--soft);border-color:var(--aline);color:var(--accent)}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:26px}
@media(max-width:560px){.pn{grid-template-columns:1fr}}
.pn a{display:block;border:1px solid var(--line);border-radius:10px;padding:13px 16px;
 background:var(--surface);text-decoration:none;color:inherit}
.pn a:hover{border-color:var(--accent);background:var(--soft)}
.pn .lbl{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;
 text-transform:uppercase;color:var(--ink-3);margin-bottom:4px}
.pn .nr{font-family:var(--mono);font-size:11px;color:var(--accent);display:block}
.pn b{font-weight:600;font-size:14.5px;line-height:1.35;display:block;margin-top:2px}
.pn .next{text-align:right}
.entryfoot{margin-top:26px;padding-top:16px;border-top:1px solid var(--line);
 color:var(--ink-3);font-size:12.5px;max-width:80ch}
.laws{list-style:none;padding:0;margin:0}
.laws .law{padding:12px 0;border-bottom:1px dotted var(--line)}
.laws .law:last-child{border-bottom:0}
.lref{font-family:var(--mono);font-size:11px;color:var(--ink-3)}
.lcore,.lwhy,.lsrc{margin:6px 0 0;font-size:13.5px;color:var(--ink-2);max-width:74ch}
.lwhy{color:var(--ink-3)}
.lsrc{font-size:12.5px}
.lnote,.lwarn{margin:8px 0;padding:9px 12px;border-radius:7px;font-size:13px;max-width:74ch}
.lnote{background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.lwarn{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink)}
"""


def _nl(o, k, default=""):
    """Nederlands als het er is, anders het origineel. De catalogus wordt
    vertaald; tot dat af is mag een pagina niet halverwege leeglopen."""
    return o.get(k + "_nl") or o.get(k) or default


def naam(x):
    return x.get("name_nl") or x["name"]


def _bronnen():
    """De inhoud van law/ en caselaw/, zodat er meer op de pagina staat dan een
    code. Wie aan die sectie het meeste heeft, is juist degene die de code niet
    kent. En een aantekening dat een verwijzing nog niet tegen de brontekst is
    gecontroleerd, hoort mee te reizen naar de plek waar zij wordt gebruikt in
    plaats van achter te blijven in een bestand dat niemand opent."""
    try:
        import yaml
    except ImportError:
        return {}
    out = {}
    for base in ("law", "caselaw"):
        for f in sorted((ROOT / base).glob("*.yaml")):
            try:
                d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            if isinstance(d, dict) and d.get("id"):
                out[d["id"]] = d
    return out


BRON = _bronnen()


def bronregel(code):
    d = BRON.get(code)
    if not d:
        return f'<li><code>{e(code)}</code></li>'
    titel = d.get("title") or d.get("case") or code
    ref = d.get("reference_nl") or d.get("reference") or d.get("court") or ""
    kern = (d.get("core") or d.get("holding") or "").strip()
    waarom = (d.get("relevance") or d.get("why_it_matters") or "").strip()
    r = [f'<li class="law"><b>{e(titel)}</b>']
    if ref:
        r.append(f' <span class="lref">{e(ref)}</span>')
    r.append(f' <code>{e(code)}</code>')
    if kern:
        r.append(f'<p class="lcore">{e(kern)}</p>')
    if waarom:
        r.append(f'<p class="lwhy">{e(waarom)}</p>')
    if d.get("weight") == "illustrative":
        r.append('<p class="lwarn">Illustratie, geen grondslag. Deze uitspraak bindt niemand; '
                 'citeer haar naast de bepaling of het arrest waarop de bevinding rust.</p>')
    if d.get("verified") is False:
        r.append('<p class="lwarn">Deze verwijzing is nog niet tegen de brontekst gecontroleerd. '
                 'Controleer artikel en formulering voordat een publicatie erop steunt.</p>')
    if d.get("url"):
        r.append(f'<p class="lsrc"><a href="{e(d["url"])}">brontekst</a></p>')
    r.append("</li>")
    return "".join(r)


def entry_page(x, ents, order):
    m, d = x["mechanism"], x["detection"]
    url = f'{BASE}/{x["id"]}'
    ip = x.get("in_practice") or {}
    nm = naam(x)

    falsi = "".join(
        f'<li><span class="k k-{e(f["checkable"])}">{e(CHK[f["checkable"]])}</span>'
        f'<span class="c">{e(_nl(f, "condition"))}</span>'
        + (f'<span class="n">{e(_nl(f, "note"))}</span>' if f.get("note") else "")
        + (f'<span class="i">{e(IFT[f["if_true"]])}</span>' if f.get("if_true") else "")
        + "</li>" for f in x["falsifiers"])
    caps = "".join(f"<li>{e(c)}</li>"
                   for c in (d.get("capture_requirements_nl") or d.get("capture_requirements", [])))
    causes = "".join(f"<li>{e(c)}</li>"
                     for c in (m.get("common_causes_nl") or m.get("common_causes", [])))
    meth = "".join(f'<li><code>{e(t["path"])}</code> &middot; {e(TIER.get(t["tier"], t["tier"]))}'
                   + (f' &middot; {e(_nl(t, "expect"))}' if t.get("expect") else "") + "</li>"
                   for t in x["reproduction"]["methods"])
    scan = ", ".join(x["reproduction"].get("public_scanners", []))
    rebut = "".join(f'<div class="rb"><p class="rq">&ldquo;{e(_nl(r, "objection"))}&rdquo;</p>'
                    f'<p class="ra">{e(_nl(r, "answer"))}</p></div>'
                    for r in x["legal"].get("rebuttals", []))

    # Niet elke fout heeft een wettelijk kader: de fouten in de familie Methode
    # gaan over onderzoek dat niet deugt, niet over een verwerking. Die kregen
    # eerder een lege kop met niets eronder, of lieten de generator vastlopen.
    prov = x["legal"].get("provisions", [])
    case = x["legal"].get("caselaw", [])
    bevinding = x["legal"].get("applies") == "to-a-finding"
    # Een fout in een bevinding kent geen bepaling die op de onderzoeker slaat.
    # Dat hoort er te staan, anders leest een lege sectie als een omissie.
    naar_wie = ('<p class="lnote">Deze entry beschrijft een fout in een bevinding, niet in een '
                'verwerking. Er is geen bepaling die op de onderzoeker van toepassing is. Wat op '
                'het spel staat, is of de bevinding een geschil overleeft.</p>') if bevinding else ""
    juridisch = ""
    if prov or case:
        juridisch = ('<section><h2>Wettelijk kader</h2>' + naar_wie + '<ul class="laws">'
                     + "".join(bronregel(p) for p in prov) + "</ul>"
                     + (f'<h2 style="margin-top:16px">Jurisprudentie</h2><ul class="laws">'
                        + "".join(bronregel(c) for c in case) + "</ul>"
                        if case else "")
                     + (f'<h2 style="margin-top:18px">Tegenwerpingen en het antwoord</h2>{rebut}'
                        if rebut else "") + "</section>")
    elif rebut or bevinding:
        kop = "Wat je hoort als je hierop wijst" if bevinding else "Tegenwerpingen en het antwoord"
        juridisch = f'<section><h2>{e(kop)}</h2>{naar_wie}{rebut}</section>'
    limits = "".join(f"<li>{e(l)}</li>"
                     for l in (x.get("does_not_establish_nl") or x["does_not_establish"]))

    # Ook tonen als het veld false is. Een empirische claim die niet is
    # onderbouwd, hoort zichtbaar te zijn op de pagina en niet alleen in de JSON.
    w = x.get("seen_in_the_wild") or {}
    refs = w.get("references") or []
    if refs:
        wild = ('<p>Onderbouwd met gepubliceerd onderzoek:</p><ul>' + "".join(
            f'<li><a href="{e(r["url"])}">{e(r["title"])}</a>'
            + (f' &middot; {e(r["author"])}' if r.get("author") else "")
            + (f' &middot; {e(r["date"])}' if r.get("date") else "") + "</li>" for r in refs) + "</ul>")
    else:
        wild = ('<p>Nog niet onderbouwd met gepubliceerd onderzoek. Dat de fout voorkomt, is de '
                'ervaring van de opsteller; wie hem gepubliceerd heeft aangetroffen, kan hier een '
                'verwijzing aandragen.</p>')
    rel = "".join(f'<a href="../{e(r)}/">{e(r)} &middot; {e(naam(ents[r]))}</a>'
                  for r in x.get("related", []) if r in ents)

    prac = ""
    if ip:
        rows = "".join(f'<div class="pr"><div class="pr-h">{e(h)}</div>'
                       f'<p>{e(ip.get(k + "_nl") or ip[k])}</p></div>'
                       for k, h in (("dpia", "In een DPIA toets je dit"),
                                    ("procurement", "Als inkoopeis"),
                                    ("complaint", "Bij een klacht lever je"))
                       if ip.get(k + "_nl") or ip.get(k))
        q = (f'<div class="askq"><span>De vraag die dit boven tafel haalt</span>'
             f'<b>{e(ip.get("audit_question_nl") or ip.get("audit_question", ""))}</b></div>'
             ) if ip.get("audit_question") else ""
        prac = f'<section><h2>Waar dit in bestaande processen past</h2>{q}<div class="prg">{rows}</div></section>'

    # Vorige en volgende, op nummer. Wie de catalogus doorleest hoeft niet
    # steeds terug naar de index, en de nummers lopen door families heen.
    i = order.index(x["id"])
    pn = ""
    if len(order) > 1:
        vorige = order[i - 1] if i > 0 else None
        volgende = order[i + 1] if i + 1 < len(order) else None
        cel = []
        cel.append(f'<a href="../{e(vorige)}/"><span class="lbl">Vorige fout</span>'
                   f'<span class="nr">{e(vorige)}</span><b>{e(naam(ents[vorige]))}</b></a>'
                   if vorige else "<div></div>")
        cel.append(f'<a class="next" href="../{e(volgende)}/"><span class="lbl">Volgende fout</span>'
                   f'<span class="nr">{e(volgende)}</span><b>{e(naam(ents[volgende]))}</b></a>'
                   if volgende else "<div></div>")
        pn = f'<nav class="pn" aria-label="Vorige en volgende fout">{"".join(cel)}</nav>'

    crumb = S.crumb(("Database", "../"), x["id"])
    body = f'''<div class="wrap">
{crumb}
<p class="eyebrow">{e(x["id"])} &middot; {e(FAM.get(x["family"], x["family"]))}</p>
<h1>{e(nm)}</h1>
<p class="sum">{e(_nl(x, "summary"))}</p>
<div class="tags"><span class="tag fam">{e(FAM.get(x["family"], x["family"]))}</span>
  {"".join(f'<span class="tag">{e(SYS.get(s, s))}</span>' for s in x["applies_to"])}
  <span class="tag">status {e(STATUS.get(x["status"], x["status"]))}</span></div>

{f'<div class="nv"><b>Dit is geen kwetsbaarheid</b>{e(_nl(x, "not_a_vulnerability"))}</div>' if x.get("not_a_vulnerability") else ""}

<section><h2>Wat het is</h2><p>{e(_nl(m, "what"))}</p></section>
<section><h2>Waarom dit een eigen fout is</h2><p>{e(_nl(m, "why_it_matters"))}</p></section>
{f'<section><h2>Hoe het ontstaat</h2><ul>{causes}</ul></section>' if causes else ""}
{f'<section><h2>Niet te verwarren met</h2><p>{e(_nl(m, "not_this"))}</p></section>' if m.get("not_this") else ""}
<section><h2>Hoe je het vaststelt</h2>
  <div class="ind">{e(_nl(d, "indicator"))}</div>
  <p class="qod"><span><b>Meetwijze</b>{e(METHOD.get(d["method"], d["method"]))}</span>
   <span><b>Zekerheid</b>{d["qod"]} van 100</span></p>
  {f'<h2 style="margin-top:16px">Eisen aan de meting</h2><ul>{caps}</ul>' if caps else ""}
</section>
<section><h2>Wat dit zou ontkrachten</h2><ul class="fal">{falsi}</ul></section>
{prac}
<section><h2>Hoe je het naspeelt</h2><ul>{meth}</ul>
  {f'<p style="margin-top:10px;font-size:13.5px;color:var(--ink-3)">Derden die het kunnen bevestigen: {e(scan)}</p>' if scan else ""}
</section>
{juridisch}
<section><h2>In de praktijk aangetroffen</h2>{wild}</section>
<section><h2>Wat dit niet vaststelt</h2><ul>{limits}</ul></section>
{f'<section><h2>Verwante fouten</h2><div class="rel">{rel}</div></section>' if rel else ""}

<div class="cite"><h2>Hoe je hiernaar verwijst</h2>
  <dl>
    <dt>In lopende tekst</dt><dd class="plain">{e(x["id"])} ({e(nm)})</dd>
    <dt>Adres</dt><dd>{e(url)}</dd>
    <dt>Machineleesbaar</dt><dd>{e(url)}/index.json</dd>
    <dt>Volledig</dt><dd class="plain">DPE-catalogus. {e(x["id"])}: {e(nm)}. Schema {e(x["schema_version"])},
      status {e(STATUS.get(x["status"], x["status"]))}, laatst gewijzigd {e(datum(x["changes"][-1]["at"]))}.
      Beschikbaar op {e(url)}</dd>
    <dt>Bij een meting</dt><dd class="plain">Noem de methodeversie naast het nummer:
      &ldquo;{e(x["id"])}, vastgesteld volgens <a href="../methode.html">DPE-meetmethode {S.METHODE}</a>&rdquo;</dd>
  </dl>
  <p style="margin:14px 0 0;font-size:13px;color:var(--ink-3)">Nummers zijn permanent en worden nooit
  hergebruikt. Een ingetrokken fout houdt zijn nummer en zijn adres, met de reden erbij, omdat er
  elders naar verwezen wordt.</p>
</div>

{pn}

<p class="entryfoot">Deze fout beschrijft gedrag van een systeem, niet van een organisatie, en krijgt
geen ernst toegekend. Of een concreet geval onrechtmatig is, stelt de Autoriteit Persoonsgegevens of
de rechter vast. Laatst gewijzigd op {e(datum(x["changes"][-1]["at"]))}.
<a href="index.json">Deze fout als JSON</a>.</p>
</div>'''

    return (S.head(f'{x["id"]}: {nm} · DPE-register', _nl(x, "summary"), up="../", cur=None, css=CSS)
            + body + S.foot(up="../"))


def main():
    ents = {}
    for f in sorted(glob.glob(str(ROOT / "catalogue" / "*.json"))):
        x = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        ents[x["id"]] = x
    order = sorted(ents)
    OUT.mkdir(parents=True, exist_ok=True)
    for x in ents.values():
        page = entry_page(x, ents, order)
        blob = json.dumps(x, ensure_ascii=False, indent=2) + "\n"
        # Als map met index, zodat /register/DPE-2026-0001 werkt zonder dat de
        # webserver impliciete .html-extensies hoeft te kennen. De permanente URL
        # mag niet afhangen van een serverinstelling die iemand later wijzigt.
        d = OUT / x["id"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page, encoding="utf-8")
        (d / "index.json").write_text(blob, encoding="utf-8")
        # Bewust geen platte kopie ernaast: twee adressen voor dezelfde entry
        # betekent twee dingen om te citeren en een van de twee raakt achter.
    # De databasepagina komt uit tools/build_db.py, de symptomenpagina uit
    # tools/build_triage.py, en de twee tekstpagina's uit tools/build_docs.py.
    # Hier stond ooit een tweede indexgenerator; die gaf een verouderde,
    # half-Engelse pagina terug en is verwijderd om te voorkomen dat iemand hem
    # weer aanroept.

    (OUT / "all.json").write_text(json.dumps({
        "catalogue": "Data Protection Exposures", "schema_version": "2.0",
        "generated": TODAY, "base_url": BASE, "count": len(ents),
        "licence": "CC BY 4.0", "entries": list(ents.values())},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # sitemap, zodat de permanente adressen vindbaar zijn en blijven
    paths = ["/", "/uitleg.html", "/methode.html", "/over.html"] + [f"/{i}" for i in order]
    urls = "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in paths)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")
    print(f"{len(ents)} entrypagina's, JSON, all.json en sitemap in {OUT}")


if __name__ == "__main__":
    main()
