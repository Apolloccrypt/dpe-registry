#!/usr/bin/env python3
"""Bouwt de databasepagina: zoeken, filteren, tabel.

Zoals NVD: een zoekveld, filters, en een tabel met alles erin. Geen uitleg
bovenaan, want wie hier komt zoekt iets op. De uitleg staat op /uitleg.html
voor wie hem nodig heeft.

Het filteren gebeurt client-side op een ingesloten JSON, in een apart script
omdat de doelserver script-src 'self' draait en inline scripts blokkeert.
"""
import glob, html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "register"
FAM = {"consent": "Toestemming", "data": "Gegevens", "chain": "Keten", "transfer": "Doorgifte",
       "transparency": "Transparantie", "retention": "Bewaring", "telemetry": "Telemetrie",
       "method": "Methode"}
SYS = {"web": "web", "mobile-app": "app", "firmware": "firmware", "iot": "IoT",
       "vehicle": "voertuig", "desktop": "desktop", "api": "API",
       "network-device": "netwerkapparaat"}


def e(s):
    return html.escape(str(s), quote=True)


def build():
    ent = [json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
           for f in sorted(glob.glob(str(ROOT / "catalogue" / "DPE-*.json")))]
    rows = [{"id": x["id"], "t": x.get("name_nl") or x["name"], "e": x["name"],
             "s": x.get("summary_nl") or x["summary"], "f": x["family"],
             "y": x["applies_to"], "st": x["status"],
             "q": (x.get("in_practice") or {}).get("audit_question_nl", "")} for x in ent]

    fams = sorted({r["f"] for r in rows}, key=lambda f: -sum(1 for r in rows if r["f"] == f))
    syss = sorted({s for r in rows for s in r["y"]}, key=lambda s: -sum(1 for r in rows if s in r["y"]))

    fchips = "".join(f'<button class="chip" data-f="{e(f)}">{e(FAM.get(f, f))}'
                     f'<span>{sum(1 for r in rows if r["f"] == f)}</span></button>' for f in fams)
    schips = "".join(f'<button class="chip" data-s="{e(s)}">{e(SYS.get(s, s))}'
                     f'<span>{sum(1 for r in rows if s in r["y"])}</span></button>' for s in syss)

    tbody = "".join(
        f'<tr data-id="{e(r["id"])}" data-f="{e(r["f"])}" data-y="{e(" ".join(r["y"]))}" '
        f'data-q="{e((r["id"] + " " + r["t"] + " " + r["e"] + " " + r["s"] + " " + r["q"]).lower())}">'
        f'<td class="c-id"><a href="{e(r["id"])}/">{e(r["id"])}</a></td>'
        f'<td class="c-t"><a href="{e(r["id"])}/">{e(r["t"])}</a>'
        f'<span class="c-en">{e(r["e"])}</span>'
        f'<span class="c-s">{e(r["s"])}</span></td>'
        f'<td class="c-f"><span class="fam f-{e(r["f"])}">{e(FAM.get(r["f"], r["f"]))}</span></td>'
        f'<td class="c-y">{"".join(f"<span>{e(SYS.get(s, s))}</span>" for s in r["y"])}</td>'
        f"</tr>" for r in rows)

    page = TPL.replace("{n}", str(len(rows))).replace("{fchips}", fchips) \
              .replace("{schips}", schips).replace("{tbody}", tbody)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "db.js").write_text(JS, encoding="utf-8")
    print(f"database met {len(rows)} fouten -> {OUT / 'index.html'}")


JS = r"""// Filteren gebeurt op de rijen zelf: geen framework, geen ophaalactie, en het
// werkt met de terugknop omdat de zoekterm in de URL staat.
const q = document.getElementById('q');
const rows = [...document.querySelectorAll('tbody tr')];
const chips = [...document.querySelectorAll('.chip')];
const count = document.getElementById('count');
const clear = document.getElementById('clear');
let fam = new Set(), sys = new Set();

function apply() {
  const term = q.value.trim().toLowerCase();
  let n = 0;
  for (const r of rows) {
    const okQ = !term || r.dataset.q.includes(term);
    const okF = !fam.size || fam.has(r.dataset.f);
    const okS = !sys.size || r.dataset.y.split(' ').some(s => sys.has(s));
    const show = okQ && okF && okS;
    r.hidden = !show;
    if (show) n++;
  }
  count.textContent = n === rows.length ? `${rows.length} fouten`
    : `${n} van ${rows.length}`;
  clear.hidden = !term && !fam.size && !sys.size;
  const u = new URL(location);
  term ? u.searchParams.set('q', term) : u.searchParams.delete('q');
  history.replaceState(null, '', u);
}

q.addEventListener('input', apply);
chips.forEach(c => c.addEventListener('click', () => {
  const set = c.dataset.f ? fam : sys;
  const key = c.dataset.f || c.dataset.s;
  set.has(key) ? set.delete(key) : set.add(key);
  c.setAttribute('aria-pressed', String(set.has(key)));
  apply();
}));
clear.addEventListener('click', () => {
  q.value = ''; fam.clear(); sys.clear();
  chips.forEach(c => c.setAttribute('aria-pressed', 'false'));
  apply(); q.focus();
});
const initial = new URL(location).searchParams.get('q');
if (initial) { q.value = initial; }
apply();
"""

TPL = r"""<title>DPE-database · Totale Digitale Waarborging</title>
<meta name="description" content="Doorzoekbare database van genummerde fouten in de omgang met persoonsgegevens.">
<style>
:root{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;--ink-3:#8B8B97;
 --line:#E9E9F0;--line-2:#F3F3F8;--accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;
 --green:#3CA951;--gold:#EFB118;--coral:#FF725C;
 --shadow:0 1px 2px rgba(20,20,50,.04),0 14px 34px -20px rgba(20,20,50,.16);
 --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 --mono:"DM Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.55}
.in{max-width:1180px;margin:0 auto;padding:0 20px 60px}
.bar{border-bottom:1px solid var(--line);padding:14px 0;font-size:13px;display:flex;gap:12px;flex-wrap:wrap}
.bar a{color:var(--accent);text-decoration:none}
.bar .sp{color:var(--ink-3)}
h1{font-size:clamp(24px,3.2vw,34px);font-weight:600;letter-spacing:-.024em;margin:26px 0 4px}
.sub{color:var(--ink-2);margin:0 0 22px;max-width:70ch;font-size:15.5px}
.tools{position:sticky;top:0;background:var(--bg);padding:12px 0;border-bottom:1px solid var(--line);z-index:5}
.srch{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
#q{flex:1;min-width:220px;padding:11px 14px;border:1px solid var(--line);border-radius:8px;
 font:inherit;background:var(--surface);color:inherit}
#q:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:var(--accent)}
#count{font-family:var(--mono);font-size:12.5px;color:var(--ink-3);white-space:nowrap}
#clear{background:none;border:1px solid var(--line);border-radius:8px;padding:9px 13px;
 cursor:pointer;font:inherit;font-size:13px;color:var(--ink-2)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.chips b{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
 color:var(--ink-3);align-self:center;margin-right:2px;font-weight:600}
.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 11px;
 cursor:pointer;font:inherit;font-size:12.5px;color:var(--ink-2);display:flex;gap:6px;align-items:center}
.chip span{font-family:var(--mono);font-size:10.5px;color:var(--ink-3)}
.chip:hover{border-color:var(--accent)}
.chip[aria-pressed=true]{background:var(--soft);border-color:var(--accent);color:var(--accent);font-weight:500}
.chip[aria-pressed=true] span{color:var(--accent)}
table{border-collapse:collapse;width:100%;margin-top:6px}
th{text-align:left;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
 color:var(--ink-3);font-weight:600;padding:14px 14px 8px 0;border-bottom:1px solid var(--line);
 position:sticky;top:0;background:var(--bg)}
td{padding:12px 14px 12px 0;border-bottom:1px solid var(--line-2);vertical-align:top}
.c-id{font-family:var(--mono);font-size:12px;white-space:nowrap;width:1%}
.c-id a{color:var(--accent);text-decoration:none}
.c-t a{font-weight:600;font-size:15.5px;color:inherit;text-decoration:none;display:block}
.c-t a:hover{color:var(--accent)}
.c-en{display:block;font-family:var(--mono);font-size:11px;color:var(--ink-3);margin:1px 0 3px}
.c-s{display:block;font-size:13.5px;color:var(--ink-2);line-height:1.5;max-width:62ch}
.c-f{width:1%}
.fam{font-family:var(--mono);font-size:10px;letter-spacing:.05em;padding:3px 9px;border-radius:999px;
 white-space:nowrap;background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.f-consent{background:var(--soft);border-color:var(--aline);color:var(--accent)}
.c-y{width:1%;white-space:nowrap}
.c-y span{display:inline-block;font-family:var(--mono);font-size:10px;color:var(--ink-3);
 border:1px solid var(--line-2);border-radius:4px;padding:2px 6px;margin:0 3px 3px 0}
tr[hidden]{display:none}
.empty{padding:40px 0;color:var(--ink-3);font-size:15px}
footer{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);color:var(--ink-3);font-size:12.5px;max-width:80ch}
footer a{color:var(--accent)}
@media(max-width:720px){.c-f,.c-y{display:none}}
</style>
<div class="in">
<nav class="bar"><a href="https://totaledigitalewaarborging.nl/">Totale Digitale Waarborging</a>
 <span class="sp">/</span><span>DPE-database</span><span class="sp">&middot;</span>
 <a href="uitleg.html">Wat is dit</a><span class="sp">&middot;</span>
 <a href="all.json">JSON</a><span class="sp">&middot;</span>
 <a href="https://github.com/Apolloccrypt/dpe-registry">bron en bijdragen</a></nav>

<h1>DPE-database</h1>
<p class="sub">Genummerde fouten in de omgang met persoonsgegevens. Zoek op trefwoord, filter op
soort fout of op waar hij voorkomt, en klik door voor de indicator, wat de bevinding zou
ontkrachten en hoe je hem naspeelt.</p>

<div class="tools">
  <div class="srch">
    <input id="q" type="search" placeholder="Zoek op nummer, titel, omschrijving of vraag" autocomplete="off">
    <span id="count">{n} fouten</span>
    <button id="clear" hidden>Wissen</button>
  </div>
  <div class="chips"><b>soort</b>{fchips}</div>
  <div class="chips"><b>waar</b>{schips}</div>
</div>

<table>
  <thead><tr><th>Nummer</th><th>Fout</th><th>Soort</th><th>Waar</th></tr></thead>
  <tbody>{tbody}</tbody>
</table>

<footer>
<p>Elke fout beschrijft gedrag van een systeem, niet van een organisatie, en de database kent geen ernst
toe. Of een concreet geval onrechtmatig is, stelt de Autoriteit Persoonsgegevens of de rechter vast.
Nummers zijn permanent en worden nooit hergebruikt.</p>
<p>Weet je niet welk nummer je zoekt? <a href="uitleg.html">Ga van symptoom naar nummer</a>.</p>
</footer>
</div>
<script src="db.js"></script>
"""

if __name__ == "__main__":
    build()
