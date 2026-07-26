#!/usr/bin/env python3
"""Bouwt de databasepagina: zoeken, filteren, tabel.

Zoals NVD: een zoekveld, filters, en een tabel met alles erin. Geen uitleg
bovenaan, want wie hier komt zoekt iets op. De uitleg staat op /uitleg.html
voor wie hem nodig heeft.

Het filteren gebeurt client-side op de rijen zelf, in een apart script omdat de
doelserver script-src 'self' draait en inline scripts blokkeert. De hele
filterstand staat in de URL, zodat een uitkomst te delen en te bookmarken is en
een onbekende filterwaarde netjes op het lege resultaat uitkomt. Zonder
JavaScript blijft de volledige tabel staan; er verdwijnt dan niets, er valt
alleen niets te filteren.
"""
import glob, importlib.util, json, pathlib

# site.py heet net zo als een module van Python zelf, en die staat bij het
# starten al in sys.modules. Een gewone import levert dus de verkeerde op.
_p = pathlib.Path(__file__).resolve().parent / "site.py"
_spec = importlib.util.spec_from_file_location("dpe_site", _p)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "register"
e, FAM, SYS = S.e, S.FAM, S.SYS


def build():
    ent = [json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
           for f in sorted(glob.glob(str(ROOT / "catalogue" / "DPE-*.json")))]
    rows = [{"id": x["id"], "t": x.get("name_nl") or x["name"], "e": x["name"],
             "s": x.get("summary_nl") or x["summary"], "f": x["family"],
             "y": x["applies_to"], "st": x["status"],
             "d": x["changes"][-1]["at"][:10],
             "q": (x.get("in_practice") or {}).get("audit_question_nl", "")} for x in ent]

    fams = sorted({r["f"] for r in rows}, key=lambda f: (-sum(1 for r in rows if r["f"] == f), f))
    syss = sorted({s for r in rows for s in r["y"]},
                  key=lambda s: (-sum(1 for r in rows if s in r["y"]), s))

    fchips = "".join(
        f'<button class="chip" type="button" aria-pressed="false" data-f="{e(f)}">'
        f'{e(FAM.get(f, f))}<span>{sum(1 for r in rows if r["f"] == f)}</span></button>'
        for f in fams)
    schips = "".join(
        f'<button class="chip" type="button" aria-pressed="false" data-s="{e(s)}">'
        f'{e(SYS.get(s, s))}<span>{sum(1 for r in rows if s in r["y"])}</span></button>'
        for s in syss)

    tbody = "".join(
        f'<tr data-id="{e(r["id"])}" data-f="{e(r["f"])}" data-y="{e(" ".join(r["y"]))}" '
        f'data-q="{e((r["id"] + " " + r["t"] + " " + r["e"] + " " + r["s"] + " " + r["q"]).lower())}">'
        f'<td class="c-id"><a href="{e(r["id"])}/">{e(r["id"])}</a></td>'
        f'<td class="c-t"><a href="{e(r["id"])}/">{e(r["t"])}</a>'
        f'<span class="c-s">{e(r["s"])}</span></td>'
        f'<td class="c-f"><span class="fam f-{e(r["f"])}">{e(FAM.get(r["f"], r["f"]))}</span></td>'
        f'<td class="c-y">{"".join(f"<span>{e(SYS.get(s, s))}</span>" for s in r["y"])}</td>'
        f"</tr>" for r in rows)

    # Laatst gewijzigd: de datum komt uit de entry zelf, dus dit blok blijft
    # kloppen als er later iets bijkomt. Bij gelijke datum wint het hoogste
    # nummer, want dat is de volgorde waarin ze zijn toegekend.
    recent = sorted(rows, key=lambda r: (r["d"], r["id"]), reverse=True)[:5]
    rec = "".join(
        f'<li><a href="{e(r["id"])}/"><code>{e(r["id"])}</code>'
        f'<b>{e(r["t"])}</b></a><time datetime="{e(r["d"])}">{e(nl_date(r["d"]))}</time></li>'
        for r in recent)

    # "48 fouten" naast "48 actief" zei twee keer hetzelfde en las als een fout.
    # De laatste telling verschijnt pas zodra zij iets toevoegt.
    weg = sum(1 for r in rows if r["st"] != "active")
    stats = (f'<div class="stat"><b>{len(rows)}</b><span>fouten</span></div>'
             f'<div class="stat"><b>{len(fams)}</b><span>soorten</span></div>'
             f'<div class="stat"><b>{len(syss)}</b><span>soorten systeem</span></div>'
             + (f'<div class="stat"><b>{weg}</b><span>ingetrokken of vervangen</span></div>'
                if weg else ""))

    page = (S.head("DPE-database · genummerde fouten in de omgang met persoonsgegevens",
                   "Doorzoekbare database van genummerde fouten in de omgang met "
                   "persoonsgegevens. Zoek op trefwoord, filter op soort en op systeem.",
                   up="", cur="", css=CSS)
            + BODY.replace("{n}", str(len(rows))).replace("{fchips}", fchips)
                  .replace("{schips}", schips).replace("{tbody}", tbody)
                  .replace("{recent}", rec).replace("{stats}", stats)
            + S.foot(up="", scripts=["db.js"]))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "db.js").write_text(JS, encoding="utf-8")
    print(f"database met {len(rows)} fouten -> {OUT / 'index.html'}")


MAAND = ["", "januari", "februari", "maart", "april", "mei", "juni", "juli",
         "augustus", "september", "oktober", "november", "december"]


def nl_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MAAND[int(m)]} {y}"


JS = r"""// Filteren gebeurt op de rijen zelf: geen framework, geen ophaalactie. De hele
// stand staat in de URL, dus een gefilterde uitkomst is te delen en te
// bookmarken. Bewust replaceState en geen pushState: anders zou elke aanslag in
// het zoekveld een stap in de geschiedenis worden en kom je met de terugknop
// niet meer van deze pagina af.
const q = document.getElementById('q');
const rows = [...document.querySelectorAll('tbody tr')];
const chips = [...document.querySelectorAll('.chip')];
const count = document.getElementById('count');
const clear = document.getElementById('clear');
const leeg = document.getElementById('leeg');
const leegTerm = document.getElementById('leeg-term');
const tabel = document.getElementById('tabel');
const fam = new Set(), sys = new Set();

function schrijfUrl(term) {
  const u = new URL(location);
  const zet = (k, v) => v ? u.searchParams.set(k, v) : u.searchParams.delete(k);
  zet('q', term);
  zet('soort', [...fam].join(','));
  zet('waar', [...sys].join(','));
  history.replaceState(null, '', u.searchParams.toString() ? u : u.pathname);
}

function apply(schrijf = true) {
  const term = q.value.trim().toLowerCase();
  let n = 0;
  for (const r of rows) {
    const okQ = !term || r.dataset.q.includes(term);
    const okF = !fam.size || fam.has(r.dataset.f);
    const okS = !sys.size || r.dataset.y.split(' ').some(s => sys.has(s));
    const toon = okQ && okF && okS;
    r.hidden = !toon;
    if (toon) n++;
  }
  const gefilterd = term || fam.size || sys.size;
  count.textContent = n === rows.length
    ? rows.length + ' fouten'
    : n + ' van ' + rows.length + (n === 1 ? ' fout' : ' fouten');
  clear.hidden = !gefilterd;
  leeg.hidden = n > 0;
  tabel.hidden = n === 0;
  if (n === 0) leegTerm.textContent = term ? '“' + q.value.trim() + '”' : 'deze combinatie van filters';
  if (schrijf) schrijfUrl(term);
}

q.addEventListener('input', () => apply());
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

// Alles wissen kan ook vanuit het lege resultaat, want daar sta je als je
// jezelf hebt vastgefilterd.
document.getElementById('leeg-wis').addEventListener('click', () => clear.click());

// Schuine streep springt naar het zoekveld, zoals in de meeste databases.
document.addEventListener('keydown', ev => {
  if (ev.key === '/' && document.activeElement !== q && !ev.metaKey && !ev.ctrlKey) {
    ev.preventDefault(); q.focus(); q.select();
  }
  if (ev.key === 'Escape' && document.activeElement === q && q.value) {
    q.value = ''; apply();
  }
});

// De stand uit de URL terugzetten, zodat een gedeelde link hetzelfde toont.
const p = new URL(location).searchParams;
if (p.get('q')) q.value = p.get('q');
for (const [param, set] of [['soort', fam], ['waar', sys]]) {
  (p.get(param) || '').split(',').filter(Boolean).forEach(v => set.add(v));
}
chips.forEach(c => {
  const set = c.dataset.f ? fam : sys;
  const key = c.dataset.f || c.dataset.s;
  if (set.has(key)) c.setAttribute('aria-pressed', 'true');
});
apply(false);
"""

CSS = r"""
.in{padding-bottom:10px}
.tools{position:sticky;top:56px;background:var(--bg);padding:12px 0 14px;
 border-bottom:1px solid var(--line);z-index:5}
@media(max-width:520px){.tools{position:static}}
.srch{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
#q{flex:1;min-width:200px;padding:11px 14px;border:1px solid var(--line);border-radius:8px;
 font:inherit;background:var(--surface);color:inherit}
#q:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:var(--accent)}
#count{font-family:var(--mono);font-size:12.5px;color:var(--ink-3);white-space:nowrap}
#clear{background:none;border:1px solid var(--line);border-radius:8px;padding:9px 13px;
 cursor:pointer;font:inherit;font-size:13px;color:var(--ink-2)}
#clear:hover{border-color:var(--accent);color:var(--accent)}
.kbd{font-family:var(--mono);font-size:11px;color:var(--ink-3);white-space:nowrap}
.kbd b{border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;padding:1px 5px;
 background:var(--surface);font-weight:400}
@media(max-width:720px){.kbd{display:none}}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.chips>b{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
 color:var(--ink-3);align-self:center;margin-right:2px;font-weight:600;min-width:34px}
.chip{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:5px 11px;
 cursor:pointer;font:inherit;font-size:12.5px;color:var(--ink-2);display:flex;gap:6px;align-items:center}
.chip span{font-family:var(--mono);font-size:10.5px;color:var(--ink-3)}
.chip:hover{border-color:var(--accent)}
.chip[aria-pressed=true]{background:var(--soft);border-color:var(--accent);color:var(--accent);font-weight:500}
.chip[aria-pressed=true] span{color:var(--accent)}
table{border-collapse:collapse;width:100%;margin-top:6px}
th{text-align:left;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;
 color:var(--ink-3);font-weight:600;padding:14px 14px 8px 0;border-bottom:1px solid var(--line)}
td{padding:12px 14px 12px 0;border-bottom:1px solid var(--line-2);vertical-align:top}
tbody tr:hover{background:var(--surface-2)}
.c-id{font-family:var(--mono);font-size:12px;white-space:nowrap;width:1%}
.c-id a{color:var(--accent);text-decoration:none}
.c-t a{font-weight:600;font-size:15.5px;color:inherit;text-decoration:none;display:block}
.c-t a:hover{color:var(--accent)}
.c-s{display:block;font-size:13.5px;color:var(--ink-2);line-height:1.5;max-width:62ch}
td.c-f{width:1%}
.fam{font-family:var(--mono);font-size:10px;letter-spacing:.05em;padding:3px 9px;border-radius:999px;
 white-space:nowrap;background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.f-consent{background:var(--soft);border-color:var(--aline);color:var(--accent)}
td.c-y{width:1%;white-space:nowrap}
.c-y span{display:inline-block;font-family:var(--mono);font-size:10px;color:var(--ink-3);
 border:1px solid var(--line-2);border-radius:4px;padding:2px 6px;margin:0 3px 3px 0}
tr[hidden]{display:none}
@media(max-width:820px){.c-y{display:none}}
@media(max-width:620px){.c-f{display:none}.c-t a{font-size:15px}
 td{padding:11px 0}.c-id{padding-right:12px}}
.leeg{border:1px dashed var(--line);border-radius:11px;padding:30px 24px;margin-top:18px;
 background:var(--surface);text-align:center}
.leeg b{display:block;font-size:17px;margin-bottom:6px}
.leeg p{color:var(--ink-2);max-width:56ch;margin:0 auto 14px}
.leeg button{background:var(--accent);color:#fff;border:0;border-radius:8px;padding:9px 16px;
 cursor:pointer;font:inherit;font-size:13.5px}
.stats{display:flex;gap:26px;flex-wrap:wrap;margin:0 0 20px;padding:14px 0 0;border-top:1px solid var(--line-2)}
.stat b{font-family:var(--mono);font-size:19px;font-weight:600;display:block;line-height:1.2}
.stat span{font-size:12px;color:var(--ink-3)}
@media(max-width:620px){.stats{gap:18px;margin-bottom:14px;padding-top:12px}
 .stat b{font-size:16px}.stat span{font-size:11px}
 .chips{gap:5px;margin-top:8px}.chip{padding:4px 9px;font-size:12px}}
.na{display:grid;grid-template-columns:1.4fr 1fr;gap:34px;margin-top:34px;padding-top:26px;
 border-top:1px solid var(--line)}
@media(max-width:820px){.na{grid-template-columns:1fr;gap:26px}}
.na h2{font-size:15px;margin:0 0 10px}
.na p{font-size:14px;color:var(--ink-2);max-width:66ch}
.rec{list-style:none;margin:0;padding:0}
.rec li{display:flex;gap:10px;align-items:baseline;justify-content:space-between;
 padding:8px 0;border-bottom:1px solid var(--line-2)}
.rec a{text-decoration:none;color:inherit;display:flex;gap:10px;align-items:baseline;min-width:0}
.rec code{font-size:11px;background:none;padding:0;color:var(--accent);white-space:nowrap}
.rec b{font-weight:500;font-size:14px}
.rec a:hover b{color:var(--accent)}
.rec time{font-family:var(--mono);font-size:10.5px;color:var(--ink-3);white-space:nowrap}
"""

BODY = r"""<div class="in">
<h1>DPE-database</h1>
<p class="sub">{n} genummerde fouten in de omgang met persoonsgegevens, elk met een eigen nummer
en een vast adres. Zoek op trefwoord of filter op soort.</p>

<div class="stats">{stats}</div>

<div class="tools">
  <div class="srch">
    <label for="q" class="vh">Zoeken in de database</label>
    <input id="q" type="search" placeholder="Zoek op nummer, titel, omschrijving of vraag" autocomplete="off">
    <span class="kbd"><b>/</b> om te zoeken</span>
    <span id="count" role="status" aria-live="polite">{n} fouten</span>
    <button id="clear" type="button" hidden>Alles wissen</button>
  </div>
  <div class="chips"><b>soort</b>{fchips}</div>
  <div class="chips"><b>waar</b>{schips}</div>
</div>

<div class="leeg" id="leeg" hidden>
  <b>Niets gevonden voor <span id="leeg-term"></span></b>
  <p>Dat betekent niet dat de fout niet bestaat: het betekent dat er geen vermelding is die aan
  deze zoekopdracht voldoet. Zoek breder, haal een filter weg, of ga van symptoom naar nummer.</p>
  <button id="leeg-wis" type="button">Filters wissen</button>
  <p style="margin-top:14px;font-size:13.5px">Weet je zeker dat er een fout ontbreekt?
  <a href="https://github.com/Apolloccrypt/dpe-registry/issues">Meld hem aan</a>, dat kost je niets
  omdat hier geen enkele organisatie bij naam staat.</p>
</div>

<table id="tabel">
  <caption class="vh">Alle fouten in de DPE-catalogus</caption>
  <thead><tr><th scope="col">Nummer</th><th scope="col">Fout</th>
   <th scope="col" class="c-f">Soort</th><th scope="col" class="c-y">Waar</th></tr></thead>
  <tbody>{tbody}</tbody>
</table>

<div class="na">
  <div>
    <h2>Wat hier niet staat</h2>
    <p>Geen enkele organisatie, geen product en geen domein. Elke fout beschrijft gedrag van een
    systeem. Er wordt geen ernst toegekend en geen oordeel geveld: of een concreet geval
    onrechtmatig is, stelt de Autoriteit Persoonsgegevens of de rechter vast.</p>
    <p>Achter elk nummer staat de indicator waarmee je de fout vaststelt, de eisen waaraan de meting
    moet voldoen, wat de bevinding zou ontkrachten, en hoe je hem naspeelt.</p>
    <p>Weet je niet welk nummer je zoekt, of meet je zelf niet?
    <a href="uitleg.html">Ga van symptoom naar nummer</a>. Wil je zelf meten?
    <a href="methode.html">Lees de meetmethode</a>.</p>
  </div>
  <div>
    <h2>Laatst gewijzigd</h2>
    <ul class="rec">{recent}</ul>
  </div>
</div>
</div>
"""

if __name__ == "__main__":
    build()
