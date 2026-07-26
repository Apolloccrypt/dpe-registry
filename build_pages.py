#!/usr/bin/env python3
"""Bouwt de publiceerbare site: een pagina per fout, met een eigen URL.

Uitgangspunt is citeerbaarheid. Wie naar DPE-2026-0001 verwijst moet over tien
jaar nog op een pagina uitkomen, ook als de index er dan anders uitziet, ook als
er geen JavaScript draait, en ook als deze generator allang vervangen is. Daarom:

  - een statische pagina per entry, zonder afhankelijkheid van JavaScript
  - dezelfde inhoud als JSON ernaast, voor wie het machinaal leest
  - een citeerblok op elke pagina, zodat verwijzen geen denkwerk kost
  - een index die alleen navigatie is, nooit de enige plek waar iets staat

Uitvoer in site/register/, klaar om onder een pad op de site te hangen.
"""
import glob, html, json, pathlib, datetime

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "site" / "register"
BASE = "https://totaledigitalewaarborging.nl/register"
TODAY = "2026-07-26"

FAM = {"consent": "Consent", "data": "Data", "chain": "Chain", "transfer": "Transfer",
       "transparency": "Transparency", "retention": "Retention", "telemetry": "Telemetry",
       "method": "Method"}
SYS = {"web": "web", "mobile-app": "app", "firmware": "firmware", "iot": "IoT",
       "vehicle": "vehicle", "desktop": "desktop", "api": "API", "network-device": "network device"}
TIER = {"manual": "by hand", "bookmarklet": "bookmarklet", "script": "script", "suite": "suite"}
CHK = {"automated": "automated", "manual": "by hand", "not-from-capture": "not from the capture"}
IFT = {"drop": "finding falls", "reclassify": "reclassify", "weaken": "weakens"}


def e(s):
    return html.escape(str(s), quote=True)


CSS = """
:root{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;--ink-3:#8B8B97;
 --line:#E9E9F0;--line-2:#F3F3F8;--accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;
 --ok:#3CA951;--ok-bg:#EAF6EE;--ok-line:#CDE9D6;--warn-bg:#FBF3DD;--warn-line:#EFDFAE;--warn-ink:#8A6200;
 --shadow:0 1px 2px rgba(20,20,50,.04),0 14px 34px -20px rgba(20,20,50,.16);
 --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 --mono:"DM Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
 --serif:"Iowan Old Style",Georgia,serif;}
@media(prefers-color-scheme:dark){:root{--bg:#111118;--surface:#181820;--surface-2:#1E1E28;--ink:#ECECF2;
 --ink-2:#AEAEBC;--ink-3:#7E7E8E;--line:#2A2A36;--line-2:#22222C;--accent:#7C9BE8;--soft:#1B2340;
 --aline:#2E3A63;--ok:#5FC177;--ok-bg:#16281C;--ok-line:#274A31;--warn-bg:#2E2513;--warn-line:#4A3D1D;
 --warn-ink:#E8C05A;}}
:root[data-theme=dark]{--bg:#111118;--surface:#181820;--surface-2:#1E1E28;--ink:#ECECF2;--ink-2:#AEAEBC;
 --ink-3:#7E7E8E;--line:#2A2A36;--line-2:#22222C;--accent:#7C9BE8;--soft:#1B2340;--aline:#2E3A63;
 --ok:#5FC177;--ok-bg:#16281C;--ok-line:#274A31;--warn-bg:#2E2513;--warn-line:#4A3D1D;--warn-ink:#E8C05A;}
:root[data-theme=light]{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;
 --ink-3:#8B8B97;--line:#E9E9F0;--line-2:#F3F3F8;--accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6}
.wrap{max-width:860px;margin:0 auto;padding:0 24px 80px}
.bar{border-bottom:1px solid var(--line);padding:16px 0;margin-bottom:30px;display:flex;
 gap:14px;align-items:baseline;flex-wrap:wrap}
.bar a{color:var(--accent);text-decoration:none;font-size:13.5px}
.bar a:hover{text-decoration:underline}
.bar .sep{color:var(--ink-3)}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--accent);margin:0 0 8px}
h1{font-size:clamp(26px,4vw,36px);font-weight:600;letter-spacing:-.022em;margin:0;line-height:1.12;text-wrap:balance}
.sum{font-size:18px;color:var(--ink-2);margin:10px 0 0;max-width:62ch}
.tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:14px}
.tag{font-family:var(--mono);font-size:10px;letter-spacing:.06em;padding:3px 9px;border-radius:999px;
 background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.tag.fam{background:var(--soft);border-color:var(--aline);color:var(--accent)}
.nv{margin:22px 0 0;background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:9px;
 padding:14px 17px;font-size:14px;color:var(--warn-ink)}
.nv b{display:block;margin-bottom:3px}
h2{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);
 margin:0 0 10px;font-weight:600}
section{padding:22px 0;border-bottom:1px solid var(--line-2)}
p{margin:0 0 10px;max-width:70ch}
ul{margin:0;padding-left:18px;color:var(--ink-2);font-size:14.5px}
li{margin-bottom:4px}
code{font-family:var(--mono);font-size:12px;background:var(--line-2);padding:1px 6px;border-radius:4px}
.ind{font-family:var(--mono);font-size:13px;line-height:1.65;background:var(--surface-2);border:1px solid var(--line);
 border-left:3px solid var(--accent);padding:13px 15px;border-radius:0 8px 8px 0}
.qod{margin-top:11px;font-family:var(--mono);font-size:12px;color:var(--ink-2)}
.qod b{margin-right:16px}
.fal{list-style:none;padding:0}
.fal li{display:grid;grid-template-columns:auto 1fr;gap:5px 10px;padding-bottom:9px;
 border-bottom:1px dotted var(--line);align-items:baseline}
.fal li:last-child{border-bottom:0}
.k{font-family:var(--mono);font-size:9px;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;
 border-radius:999px;white-space:nowrap}
.k-automated{background:var(--ok-bg);border:1px solid var(--ok-line);color:var(--ok)}
.k-manual{background:var(--soft);border:1px solid var(--aline);color:var(--accent)}
.k-not-from-capture{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink)}
.n,.i{grid-column:2;font-size:12.5px;color:var(--ink-3)}
.i{font-family:var(--mono);font-size:10px;letter-spacing:.05em;text-transform:uppercase}
.askq{background:var(--soft);border:1px solid var(--aline);border-radius:9px;padding:15px 18px;margin-bottom:14px}
.askq span{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;text-transform:uppercase;
 color:var(--accent);margin-bottom:4px}
.askq b{font-size:16.5px;font-weight:600;line-height:1.4}
.prg{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:1px;background:var(--line);
 border:1px solid var(--line);border-radius:9px;overflow:hidden}
.pr{background:var(--surface);padding:13px 15px}
.pr-h{font-family:var(--mono);font-size:9px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-bottom:5px}
.pr p{margin:0;font-size:13.5px;color:var(--ink-2);line-height:1.55}
.rb{border-left:2px solid var(--line);padding-left:14px;margin-bottom:14px}
.rq{font-weight:600;font-size:14.5px;margin:0 0 3px}
.ra{font-family:var(--serif);font-size:15px;color:var(--ink-2);margin:0;line-height:1.6}
.cite{background:var(--surface-2);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin-top:26px}
.cite h2{margin-bottom:12px}
.cite dl{display:grid;grid-template-columns:auto 1fr;gap:7px 14px;margin:0;font-size:13.5px}
.cite dt{font-family:var(--mono);font-size:9.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);padding-top:2px}
.cite dd{margin:0;font-family:var(--mono);font-size:12.5px;word-break:break-all}
.cite .plain{font-family:var(--sans);font-size:14px;word-break:normal}
.rel{display:flex;gap:7px;flex-wrap:wrap;margin-top:4px}
.rel a{font-family:var(--mono);font-size:11px;padding:5px 11px;border-radius:999px;background:var(--surface-2);
 border:1px solid var(--line);color:var(--ink-2);text-decoration:none}
.rel a:hover{background:var(--soft);border-color:var(--aline);color:var(--accent)}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);color:var(--ink-3);font-size:12.5px}
a{color:var(--accent)}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""


def page(title, body, desc=""):
    return (f'<title>{e(title)}</title>\n'
            f'<meta name="description" content="{e(desc)}">\n'
            f'<style>{CSS}</style>\n{body}')


def entry_page(x, ents):
    m, d = x["mechanism"], x["detection"]
    url = f'{BASE}/{x["id"]}'
    ip = x.get("in_practice") or {}

    falsi = "".join(
        f'<li><span class="k k-{e(f["checkable"])}">{e(CHK[f["checkable"]])}</span>'
        f'<span>{e(f["condition"])}</span>'
        + (f'<span class="n">{e(f["note"])}</span>' if f.get("note") else "")
        + (f'<span class="i">{e(IFT[f["if_true"]])}</span>' if f.get("if_true") else "")
        + "</li>" for f in x["falsifiers"])
    caps = "".join(f"<li>{e(c)}</li>" for c in d.get("capture_requirements", []))
    causes = "".join(f"<li>{e(c)}</li>" for c in m.get("common_causes", []))
    meth = "".join(f'<li><code>{e(t["path"])}</code> &middot; {e(TIER.get(t["tier"], t["tier"]))}'
                   + (f' &middot; {e(t["expect"])}' if t.get("expect") else "") + "</li>"
                   for t in x["reproduction"]["methods"])
    scan = ", ".join(x["reproduction"].get("public_scanners", []))
    rebut = "".join(f'<div class="rb"><p class="rq">&ldquo;{e(r["objection"])}&rdquo;</p>'
                    f'<p class="ra">{e(r["answer"])}</p></div>'
                    for r in x["legal"].get("rebuttals", []))
    limits = "".join(f"<li>{e(l)}</li>" for l in x["does_not_establish"])
    rel = "".join(f'<a href="{e(r)}">{e(r)} &middot; {e(ents[r]["name"])}</a>'
                  for r in x.get("related", []) if r in ents)
    prac = ""
    if ip:
        rows = "".join(f'<div class="pr"><div class="pr-h">{e(h)}</div><p>{e(ip[k])}</p></div>'
                       for k, h in (("dpia", "In a DPIA, verify this"),
                                    ("procurement", "As a procurement clause"),
                                    ("complaint", "With a complaint, hand over")) if ip.get(k))
        q = (f'<div class="askq"><span>The one question that surfaces it</span>'
             f'<b>{e(ip["audit_question"])}</b></div>') if ip.get("audit_question") else ""
        prac = f'<section><h2>Where this plugs into existing processes</h2>{q}<div class="prg">{rows}</div></section>'

    body = f'''<div class="wrap">
<nav class="bar"><a href="https://totaledigitalewaarborging.nl/">TDW</a><span class="sep">/</span>
  <a href="./">DPE catalogue</a><span class="sep">/</span>
  <span>{e(x["id"])}</span><span class="sep">&middot;</span>
  <a href="{e(x["id"])}.json">JSON</a><span class="sep">&middot;</span>
  <a href="start.html">niet-technisch</a><span class="sep">&middot;</span>
  <a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/METHOD.md">method 1.0</a></nav>

<p class="eyebrow">{e(x["id"])}</p>
<h1>{e(x["name"])}</h1>
<p class="sum">{e(x["summary"])}</p>
<div class="tags"><span class="tag fam">{e(FAM.get(x["family"], x["family"]))}</span>
  {"".join(f'<span class="tag">{e(SYS.get(s, s))}</span>' for s in x["applies_to"])}
  <span class="tag">status {e(x["status"])}</span></div>

{f'<div class="nv"><b>Not a vulnerability</b>{e(x["not_a_vulnerability"])}</div>' if x.get("not_a_vulnerability") else ""}

<section><h2>What it is</h2><p>{e(m["what"])}</p></section>
<section><h2>Why it is a separate entry</h2><p>{e(m["why_it_matters"])}</p></section>
{f'<section><h2>How it arises</h2><ul>{causes}</ul></section>' if causes else ""}
{f'<section><h2>Not to be confused with</h2><p>{e(m["not_this"])}</p></section>' if m.get("not_this") else ""}
<section><h2>How to establish it</h2>
  <div class="ind">{e(d["indicator"])}</div>
  <p class="qod"><b>method {e(d["method"])}</b><b>QoD {d["qod"]}</b></p>
  {f"<h2 style='margin-top:16px'>Requirements on the measurement</h2><ul>{caps}</ul>" if caps else ""}
</section>
<section><h2>What would refute it</h2><ul class="fal">{falsi}</ul></section>
{prac}
<section><h2>Reproduction</h2><ul>{meth}</ul>
  {f"<p style='margin-top:10px;font-size:13.5px;color:var(--ink-3)'>Third parties that can confirm it: {e(scan)}</p>" if scan else ""}
</section>
<section><h2>Legal framing</h2>
  <ul>{"".join(f"<li><code>{e(p)}</code></li>" for p in x["legal"]["provisions"])}</ul>
  {f'<h2 style="margin-top:16px">Case law</h2><ul>{"".join(f"<li><code>{e(c)}</code></li>" for c in x["legal"].get("caselaw", []))}</ul>' if x["legal"].get("caselaw") else ""}
  {f'<h2 style="margin-top:18px">Objections, and the answer</h2>{rebut}' if rebut else ""}
</section>
<section><h2>What this does not establish</h2><ul>{limits}</ul></section>
{f'<section><h2>Related</h2><div class="rel">{rel}</div></section>' if rel else ""}

<div class="cite"><h2>How to cite this entry</h2>
  <dl>
    <dt>In text</dt><dd class="plain">{e(x["id"])} ({e(x["name"])})</dd>
    <dt>URL</dt><dd>{e(url)}</dd>
    <dt>Machine</dt><dd>{e(url)}.json</dd>
    <dt>Full</dt><dd class="plain">DPE Catalogue. {e(x["id"])}: {e(x["name"])}. Schema {e(x["schema_version"])}, entry status {e(x["status"])}. Retrieved from {e(url)}</dd>
    <dt>Measurement</dt><dd class="plain">When you publish a finding, cite the method version alongside the entry: &ldquo;{e(x["id"])}, established under DPE Measurement Method 1.0&rdquo;</dd>
  </dl>
  <p style="margin:14px 0 0;font-size:13px;color:var(--ink-3)">Identifiers are permanent and are never
  reused. An entry that is deprecated keeps its number and its address, with the reason attached, because
  references to it exist elsewhere.</p>
</div>

<footer>
  <p>This entry describes the behaviour of a system, not the behaviour of an organisation, and carries no
  severity. Whether a concrete case is unlawful is for a supervisory authority or a court.
  Last change {e(x["changes"][-1]["at"][:10])}. Licence CC BY 4.0.</p>
</footer>
</div>'''
    return page(f'{x["id"]}: {x["name"]} · DPE Catalogue', body, x["summary"])


def index_page(ents):
    fams = {}
    for x in ents.values():
        fams.setdefault(x["family"], []).append(x)
    blocks = []
    for fam in sorted(fams, key=lambda f: -len(fams[f])):
        rows = "".join(
            f'<tr><td><a href="{e(x["id"])}">{e(x["id"])}</a></td>'
            f'<td><a href="{e(x["id"])}">{e(x["name"])}</a></td>'
            f'<td class="sm">{e(x["summary"])}</td>'
            f'<td class="sm">{e(", ".join(SYS.get(s, s) for s in x["applies_to"]))}</td></tr>'
            for x in sorted(fams[fam], key=lambda y: y["id"]))
        blocks.append(f'<h2 style="margin-top:30px">{e(FAM.get(fam, fam))}</h2>'
                      f'<table><tbody>{rows}</tbody></table>')
    body = f'''<div class="wrap" style="max-width:1000px">
<nav class="bar"><a href="https://totaledigitalewaarborging.nl/">Totale Digitale Waarborging</a>
  <span class="sep">/</span><span>DPE catalogue</span><span class="sep">&middot;</span>
  <a href="all.json">all.json</a><span class="sep">&middot;</span>
  <a href="https://github.com/Apolloccrypt/dpe-registry">source and contributions</a></nav>
<p class="eyebrow">Totale Digitale Waarborging &middot; as 04, privacy &middot; Data Protection Exposures</p>
<h1>We measure what others assume</h1>
<p class="sum">People keep asking how a researcher finds this stuff. This is the answer, in the open:
the faults, the indicators, the conditions a measurement has to meet, and what would prove any of it
wrong. Take it and use it.</p>

<div class="routes">
  <a class="rt" href="start.html">
    <span class="rn">Ik moet erover beslissen</span>
    <span class="rd">Je werkt met gegevensbescherming en meet niet zelf. Van wat je hoort of
    leest naar het nummer, met de vraag die je kunt stellen en hoe je merkt dat je een
    ontwijkend antwoord krijgt.</span></a>
  <a class="rt" href="https://github.com/Apolloccrypt/dpe-registry/tree/main/repro">
    <span class="rn">Ik wil zelf meten</span>
    <span class="rd">Met de hand in je browser, met een bookmarklet zonder installatie, of met
    een script dat acht fouten in een keer toetst. Je hebt geen gereedschap van ons nodig.</span></a>
  <a class="rt" href="verify.html">
    <span class="rn">Ik wil een meting narekenen</span>
    <span class="rd">Sleep een opname erin en de regels draaien op je eigen computer. Er gaat
    niets naar een server. Ook voor je eigen opname.</span></a>
</div>

<div class="lede">
  <p>A declaration is a promise. The fourth axis of the standard asks whether you can account for a
  system in legal terms, and this catalogue is what makes that question testable: numbered faults in how
  systems handle personal data, so that researchers, regulators and suppliers refer to the same thing
  instead of describing it again every time. Not vulnerabilities: there is
  nothing to exploit, the system does what its builder intended, and that intention is the objection.
  A router phoning home to another country gets no CVE, because nothing is broken. That is exactly why
  there was no number for it.</p>

  <p><b>Every entry hands you the method.</b> What settles it, what the capture has to satisfy, what would
  refute it, and how to reproduce it without any tool of ours. Take it, use it on the systems you care
  about, publish what you find under your own name.</p>

  <p><b>And then help make it better.</b> This is where it works like CVE: entries improve because people
  who use them send back what they ran into. A falsifier we missed. A national provision for your country.
  A reproduction script. A better title for something we named badly. A whole fault we have not written
  down yet, because you work on hardware and we mostly measure browsers.</p>

  <p>You get credit, permanently, in the entry. Anonymous is fine too. And you are not on the hook for
  what you report: this catalogue names no companies, so contributing here costs you nothing but time.</p>

  <p><b>The method is written down too.</b> Not just what each fault is, but how to go looking for one:
  scope, clean captures, vary one thing at a time, walk the catalogue, try to break your own finding, ask
  before publishing. Versioned, so a measurement taken this year is still readable as what it meant this
  year. Security has the OWASP Testing Guide for this; data protection had nothing.</p>

  <p class="cta"><a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/METHOD.md">DPE Measurement
  Method 1.0</a> &middot; <a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/WANTED.md">What we
  are stuck on</a> &middot; <a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/CONTRIBUTING.md">How
  to contribute</a> &middot; <a href="all.json">the whole catalogue as JSON</a></p>
</div>
{"".join(blocks)}
<footer><p>{len(ents)} entries. Schema 2.0. Licence CC BY 4.0 for the entries, MIT for the tooling, so
anyone can take this further, including the numbering, if this catalogue ever stops. Identifiers are
permanent and never reused: a reference made today has to still resolve in ten years.</p></footer>
</div>
<style>table{{border-collapse:collapse;width:100%;margin-top:8px}}
td{{padding:9px 14px 9px 0;border-bottom:1px solid var(--line-2);vertical-align:top;font-size:14px}}
td:first-child{{font-family:var(--mono);font-size:12px;white-space:nowrap}}
td a{{text-decoration:none;font-weight:500}}
td a:hover{{text-decoration:underline}}
.sm{{font-size:13px;color:var(--ink-3)}}
.routes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(255px,1fr));gap:14px;margin-top:26px}}
.rt{{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;
 padding:20px 22px;text-decoration:none;color:inherit;box-shadow:var(--shadow)}}
.rt:hover{{border-color:var(--accent)}}
.rn{{display:block;font-size:17.5px;font-weight:600;color:var(--accent);margin-bottom:7px;letter-spacing:-.01em}}
.rd{{display:block;font-size:14px;color:var(--ink-2);line-height:1.55}}
.lede{{max-width:72ch;margin-top:26px;background:var(--surface);border:1px solid var(--line);
 border-radius:12px;padding:22px 26px;box-shadow:var(--shadow)}}
.lede p{{color:var(--ink-2);font-size:15px}}
.lede p:last-child{{margin-bottom:0}}
.lede b{{color:var(--ink)}}
.cta{{margin-top:16px!important;padding-top:14px;border-top:1px solid var(--line-2);font-size:14px}}
.cta a{{font-weight:500;text-decoration:none}}
.cta a:hover{{text-decoration:underline}}</style>'''
    return page("DPE Catalogue", body,
                "Numbered faults in how systems handle personal data, for what is not a vulnerability.")


def main():
    ents = {}
    for f in sorted(glob.glob(str(ROOT / "catalogue" / "*.json"))):
        x = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        ents[x["id"]] = x
    OUT.mkdir(parents=True, exist_ok=True)
    for x in ents.values():
        (OUT / f'{x["id"]}.html').write_text(entry_page(x, ents), encoding="utf-8")
        (OUT / f'{x["id"]}.json').write_text(
            json.dumps(x, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(index_page(ents), encoding="utf-8")
    (OUT / "all.json").write_text(json.dumps({
        "catalogue": "Data Protection Exposures", "schema_version": "2.0",
        "generated": TODAY, "base_url": BASE, "count": len(ents),
        "licence": "CC BY 4.0", "entries": list(ents.values())},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # sitemap, zodat de permanente adressen vindbaar zijn en blijven
    urls = "".join(f"<url><loc>{BASE}/{i}</loc><lastmod>{TODAY}</lastmod></url>" for i in sorted(ents))
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{BASE}/</loc><lastmod>{TODAY}</lastmod></url>{urls}</urlset>\n', encoding="utf-8")
    print(f"{len(ents)} entrypagina's + index, JSON, all.json en sitemap in {OUT}")


if __name__ == "__main__":
    main()
