#!/usr/bin/env python3
"""Rendert het register naar een doorbladerbare pagina.

Leest observations/*.json en registry/*.md en bouwt daar een statische pagina
van. Geen build-stap, geen afhankelijkheden. Dit is de renderer die het register
sowieso nodig heeft; dat hij nu ook dient om het te beoordelen is meegenomen.
"""
import json, glob, html, pathlib, re

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "site" / "register.html"

AX = {
    "EV": ("Bewijs", {"M": "gemeten", "R": "gereconstrueerd", "T": "melding van derde", "S": "vermoed"}),
    "CS": ("Toestemming", {"PRE": "voor de vraag", "REJ": "na weigeren", "ACC": "na accepteren",
                           "NA": "geen mechanisme", "X": "niet bepaald"}),
    "DC": ("Gegevens", {"ID": "identifier", "BEH": "gedrag", "LOC": "locatie", "CNT": "invoer",
                        "SPC": "bijzondere categorie", "IDD": "identiteitsbewijs"}),
    "RC": ("Ontvanger", {"1P": "eigen", "PR": "verwerker", "3P": "derde partij", "UND": "onbepaald publiek"}),
    "JU": ("Jurisdictie", {"EU": "EER", "ADQ": "adequaatheidsbesluit", "3C": "derde land",
                           "HR": "hoogrisicoland", "X": "niet bepaald"}),
    "SC": ("Reikwijdte", {"ONE": "een deployment", "SEC": "sector", "NAT": "landelijk", "VND": "vendorproduct"}),
}
STATUS_NL = {"draft": "concept", "disclosure": "wederhoor loopt", "published": "gepubliceerd",
             "disputed": "betwist", "corrected": "gecorrigeerd", "resolved": "verholpen",
             "withdrawn": "ingetrokken"}
SEV_NL = {"critical": "kritiek", "high": "hoog", "medium": "middel", "low": "laag", "unrated": "niet gerateerd"}
RESP_NL = {"acknowledged": "erkend", "fixed": "verholpen", "contested": "betwist",
           "silent": "geen reactie", "refused-contact": "contact geweigerd"}


def e(s):
    return html.escape(str(s), quote=True)


def decode(vector):
    out = []
    for part in vector.split("/")[1:]:
        k, v = part.split(":", 1)
        label, table = AX[k]
        vals = " en ".join(table.get(x, x) for x in v.split("+"))
        out.append((k, v, label, vals))
    return out


def patterns():
    """Kop en samenvatting per pattern uit registry/*.md."""
    out = {}
    for f in sorted(glob.glob(str(ROOT / "registry" / "*.md"))):
        txt = pathlib.Path(f).read_text(encoding="utf-8")
        slug = pathlib.Path(f).stem
        name = re.search(r"^name:\s*(.+)$", txt, re.M)
        fam = re.search(r"^family:\s*(.+)$", txt, re.M)
        one = re.search(r"^\*\*(.+?)\*\*", txt, re.M)
        out[slug] = {"name": name.group(1).strip() if name else slug,
                     "family": fam.group(1).strip() if fam else "",
                     "oneline": one.group(1).strip() if one else "",
                     "written": True}
    return out


# Patronen die wel records hebben maar nog geen uitgeschreven pagina.
STUB = {
    "hollowno": ("HollowNo", "consent", "Weigeren verandert niet wat de browser verlaat."),
    "maxstay": ("MaxStay", "consent", "Bewaartermijn maximaal opgerekt, gezet voor de vraag."),
    "overshoulder": ("Overshoulder", "data", "De sessie zelf wordt opgenomen, niet alleen de paginaweergave."),
    "offbooks": ("OffBooks", "transparency", "Een ontvanger die in de eigen privacyverklaring ontbreekt."),
    "sideload": ("Sideload", "method", "De tag komt uit een container, niet uit de broncode."),
    "hotlink": ("Hotlink", "transfer", "Een bron van een derde inladen is bij elke weergave een doorgifte."),
    "silhouette": ("Silhouette", "data", "Herkenning aan apparaatkenmerken, zonder identifier."),
    "handover": ("Handover", "chain", "Het formulier staat bij een derde, met eigen profilering."),
}


def legal():
    """Bepalingen en uitspraken, gegroepeerd per patroon.

    Ze hangen aan het patroon en niet aan het record, zodat de onderbouwing een
    keer wordt geschreven en elk record hem erft."""
    try:
        import yaml
    except ImportError:
        return {}, {}
    laws, cases = {}, {}
    for d, bucket in ((ROOT / "law", laws), (ROOT / "caselaw", cases)):
        for f in sorted(d.glob("*.yaml")):
            item = yaml.safe_load(f.read_text(encoding="utf-8"))
            for pat in item.get("patterns", []):
                bucket.setdefault(pat, []).append(item)
    return laws, cases


def build():
    recs = [json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
            for f in sorted(glob.glob(str(ROOT / "observations" / "*.json")))]
    pats = patterns()
    LAWS, CASES = legal()
    for slug, (n, fam, one) in STUB.items():
        pats.setdefault(slug, {"name": n, "family": fam, "oneline": one, "written": False})

    sev_count = {}
    for r in recs:
        sev_count[r["severity"]["label"]] = sev_count.get(r["severity"]["label"], 0) + 1
    targets = sorted({r["target"]["name"] for r in recs})

    # ---- index, gegroepeerd per pattern
    groups = {}
    for r in recs:
        groups.setdefault(r["pattern"], []).append(r)

    idx = []
    for slug in sorted(groups, key=lambda s: (-len(groups[s]), s)):
        p = pats[slug]
        idx.append(f'''<div class="grp">
  <div class="grp-h">
    <span class="pat">{e(p["name"])}</span>
    <span class="fam">{e(p["family"])}</span>
    <span class="cnt">{len(groups[slug])}</span>
  </div>
  <p class="grp-one">{e(p["oneline"])}{"" if p["written"] else ' <span class="todo">pagina nog niet uitgeschreven</span>'}</p>
  <ul class="recs">''')
        for r in sorted(groups[slug], key=lambda x: x["id"]):
            idx.append(
                f'''<li><button class="rec" data-id="{e(r["id"])}">
        <span class="rid">{e(r["id"])}</span>
        <span class="rtgt">{e(r["target"]["name"])}</span>
        <span class="sev s-{e(r["severity"]["label"])}">{e(SEV_NL[r["severity"]["label"]])}</span>
      </button></li>''')
        idx.append("  </ul>\n</div>")

    # ---- detailpanelen
    panes = []
    for r in recs:
        d = r.get("detection", {})
        vec = "".join(
            f'<div class="ax"><span class="axk">{k}</span><span class="axv">{e(v)}</span>'
            f'<span class="axl">{e(label)}</span><span class="axd">{e(vals)}</span></div>'
            for k, v, label, vals in decode(r["vector"]))

        src = "".join(f'''<div class="src">
      <div class="src-h"><span class="src-n">{e(s["source"])}</span><span class="src-d">{e(s["date"])}</span></div>
      <p>{e(s["description"])}</p>
    </div>''' for s in r["sources"])

        fals = "".join(
            f'<li class="f-{e(c["outcome"])}"><span class="fo">{e({"excluded": "uitgesloten", "not-excluded": "niet uitgesloten", "untested": "niet getoetst"}[c["outcome"]])}</span>'
            f'<span class="fc">{e(c["condition"])}</span>'
            + (f'<span class="fe">{e(c.get("evidence", ""))}</span>' if c.get("evidence") else "")
            + "</li>" for c in r["falsifier"]["conditions"])

        cont = ""
        if "continuity" in r:
            c = r["continuity"]
            yrs = c.get("duration_months")
            dur = f"{yrs // 12} jaar {yrs % 12} maanden" if yrs else "duur niet vastgesteld"
            cont = f'''<section><h3>Continuiteit</h3>
      <div class="cont">
        <div class="cont-big">{e(dur)}</div>
        <div class="cont-meta">onafgebroken sinds {e(c.get("continuous_since", "?"))}
          {"· " + str(c["snapshots_consecutive"]) + " opeenvolgende snapshots" if c.get("snapshots_consecutive") else ""}
          · marker <code>{e(c.get("marker", "?"))}</code></div>
        {"<p>" + e(c["note"]) + "</p>" if c.get("note") else ""}
        {"<p class=earlier>" + e(c["earlier_traces"]) + "</p>" if c.get("earlier_traces") else ""}
      </div></section>'''

        prod = ""
        if r.get("products"):
            rows = "".join(f'<tr><td>{e(p["vendor"])}</td><td>{e(p["product"])}</td>'
                           f'<td><span class="pstate p-{e(p["state"])}">{e(p["state"].replace("_", " "))}</span></td>'
                           f'<td>{e(p.get("configuration", ""))}</td></tr>' for p in r["products"])
            prod = f'<section><h3>Producten</h3><div class="tw"><table><thead><tr><th>Leverancier</th><th>Product</th><th>Staat</th><th>Configuratie</th></tr></thead><tbody>{rows}</tbody></table></div></section>'

        def _prov(x):
            if isinstance(x, str):
                return f'<li><span class="jur">EU</span>{e(x)}</li>'
            imp = f' <span class="impl">implementeert {e(x["implements"])}</span>' if x.get("implements") else ""
            return f'<li><span class="jur">{e(x["jurisdiction"])}</span>{e(x["reference"])}{imp}</li>'
        prov = "".join(_prov(x) for x in r.get("legal_context", {}).get("provisions", []))

        lw = LAWS.get(r["pattern"], [])
        cs = CASES.get(r["pattern"], [])
        legalblok = ""
        if lw or cs:
            def _law(x):
                v = "" if x.get("verified") else '<span class="unver">niet geverifieerd</span>'
                mir = f'<div class="mir">{e(x["mirror_note"])}</div>' if x.get("mirror_note") else ""
                return (f'<div class="lw"><div class="lw-h"><span class="jur">{e(x["jurisdiction"])}</span>'
                        f'<b>{e(x["reference"])}</b> {e(x.get("title", ""))}{v}</div>'
                        f'<p>{e(x.get("why_it_matters") or x.get("core", ""))}</p>{mir}</div>')
            def _case(x):
                v = "" if x.get("verified") else '<span class="unver">niet geverifieerd</span>'
                idn = x.get("ecli") or x.get("case", "")
                return (f'<div class="lw"><div class="lw-h"><span class="jur">{e(x.get("jurisdiction", "EU"))}</span>'
                        f'<b>{e(x.get("case", ""))}</b> <code>{e(idn)}</code> '
                        f'<span class="cdate">{e(x.get("date", ""))}</span>{v}</div>'
                        f'<p>{e(x.get("relevance") or x.get("holding", ""))}</p></div>')
            legalblok = (('<h4>Bepalingen bij dit patroon</h4>' + "".join(_law(x) for x in lw)) if lw else "") + \
                        (('<h4>Jurisprudentie</h4>' + "".join(_case(x) for x in cs)) if cs else "")

        rep = r["reproduction"]
        meth = "".join(f'<li><span class="tier t-{e(m["tier"])}">{e(m["tier"])}</span>'
                       f'<code>{e(m.get("path", ""))}</code>'
                       f'<span class="exp">{e(m["expect"])}</span></li>' for m in rep["methods"])
        conf = rep.get("independent_confirmation") or []
        confhtml = ("".join(f'<li>{e(c["service"])} · {e(c["date"])} · {e(c["outcome"])}</li>' for c in conf)
                    if conf else '<li class="empty">nog geen onafhankelijke scan gekoppeld</li>')

        disc = r.get("disclosure", {})
        chg = "".join(f'<li><span class="cat">{e(c["at"][:10])}</span><span class="cac">{e(c.get("actor", ""))}</span>'
                      f'<span class="cae">{e(" ".join(c["entries"]))}</span></li>' for c in r["changes"])

        panes.append(f'''<article class="pane" id="p-{e(r["id"])}" hidden>
  <header class="ph">
    <div class="ph-l">
      <div class="ph-id">{e(r["id"])}</div>
      <h2>{e(pats[r["pattern"]]["name"])} <span class="ph-at">bij</span> {e(r["target"]["name"])}</h2>
      <div class="ph-op">{e(r["target"].get("operator", ""))}</div>
    </div>
    <div class="ph-r">
      <span class="sev s-{e(r["severity"]["label"])}">{e(SEV_NL[r["severity"]["label"]])}</span>
      <span class="st st-{e(r["status"])}">{e(STATUS_NL[r["status"]])}</span>
      <span class="tlp">TLP:{e(r["tlp"])}</span>
    </div>
  </header>

  <div class="meta">
    <div><span>Eerst gezien</span><b>{e(r["first_seen"])}</b></div>
    <div><span>Laatst gezien</span><b>{e(r["last_seen"])}</b></div>
    <div><span>Detectie</span><b>{e(d.get("method", "?"))}</b></div>
    <div><span>QoD</span><b>{e(d.get("qod", "?"))}</b></div>
    <div><span>Grondslag bevinding</span><b>{e(d.get("basis", "?"))}</b></div>
    <div><span>Metingen</span><b>{e(d.get("samples", {}).get("positive", "?"))} van {e(d.get("samples", {}).get("taken", "?"))}</b></div>
  </div>

  <section><h3>Vector</h3>
    <code class="vecstr">{e(r["vector"])}</code>
    <div class="vec">{vec}</div>
    <p class="note">De vector beschrijft wat is gemeten en bevat geen oordeel. Het ernstlabel is
    afgeleid met regel <code>{e(r["severity"]["rule"])}</code>, die openbaar is.</p>
  </section>

  <section><h3>Indicator</h3><p class="ind">{e(d.get("indicator", ""))}</p></section>

  <section><h3>Bronnen</h3>{src}</section>
  {cont}

  <section><h3>Reproductie</h3>
    <ul class="meths">{meth}</ul>
    <h4>Onafhankelijke bevestiging</h4>
    <ul class="conf">{confhtml}</ul>
  </section>

  <section><h3>Wat dit zou ontkrachten</h3>
    <p class="note">Attributie via <code>{e(r["falsifier"].get("attribution", "?"))}</code>.
    Een record mag pas gepubliceerd worden als deze condities zijn afgelopen.</p>
    <ul class="fals">{fals}</ul>
  </section>
  {prod}

  <section><h3>Wettelijk kader</h3>
    <p class="note">Geen vaststelling van onrechtmatigheid. Dat is aan een toezichthouder of de rechter.
    De bepalingen hangen aan het patroon; alleen zaakspecifieke verwijzingen staan in het record zelf.</p>
    <ul class="prov">{prov}</ul>
    {legalblok}
  </section>

  <section><h3>Wederhoor</h3>
    <div class="disc">
      <div class="disc-r">reactie: <b>{e(RESP_NL.get(disc.get("response", ""), disc.get("response", "-")))}</b>
      {"op " + e(disc["response_on"]) if disc.get("response_on") else ""}</div>
      <p>{e(disc.get("response_text", ""))}</p>
    </div>
  </section>

  <section><h3>Wijzigingen</h3><ul class="chg">{chg}</ul></section>
</article>''')

    sev_bar = "".join(
        f'<div class="sb s-{k}" style="flex:{v}"><span>{SEV_NL[k]}</span><b>{v}</b></div>'
        for k, v in sorted(sev_count.items(), key=lambda kv: -kv[1]))

    page = TEMPLATE
    for k, v in {"n_rec": len(recs), "n_pat": len(groups), "n_tgt": len(targets),
                 "sev_bar": sev_bar, "index": "\n".join(idx),
                 "panes": "\n".join(panes), "first_id": recs[0]["id"]}.items():
        page = page.replace("{" + k + "}", str(v))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    (OUT.parent / "index.html").write_text(page, encoding="utf-8")

    # Permanente URL's. Dit is de kern van een register: een verwijzing moet over
    # tien jaar nog werken, ook als de indexpagina er heel anders uitziet. Elk
    # record krijgt een eigen pad met een JSON ernaast, elk patroon idem.
    site = OUT.parent
    for r in recs:
        d = site / "r" / r["id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (d / "index.html").write_text(
            page.replace(f"show('{recs[0]['id']}');", f"show('{r['id']}');"), encoding="utf-8")

    for slug in groups:
        d = site / "p" / slug
        d.mkdir(parents=True, exist_ok=True)
        first = sorted(groups[slug], key=lambda x: x["id"])[0]["id"]
        (d / "index.html").write_text(
            page.replace(f"show('{recs[0]['id']}');", f"show('{first}');"), encoding="utf-8")
        (d / "index.json").write_text(json.dumps({
            "pattern": slug, "name": pats[slug]["name"], "family": pats[slug]["family"],
            "summary": pats[slug]["oneline"], "written_up": pats[slug]["written"],
            "records": [x["id"] for x in sorted(groups[slug], key=lambda y: y["id"])],
            "law": [x.get("id") for x in LAWS.get(slug, [])],
            "caselaw": [x.get("id") for x in CASES.get(slug, [])],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (site / "all.json").write_text(json.dumps({
        "schema_version": "1.0", "count": len(recs), "records": recs,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(recs)} records gerenderd naar {OUT}")
    print(f"permanente paden: /r/<id>/ ({len(recs)}x), /p/<pattern>/ ({len(groups)}x), all.json")


TEMPLATE = r"""<title>DPE-register: Pels Rijcken</title>
<style>
:root{
  --bg:#FCFCFE; --surface:#FFFFFF; --surface-2:#F7F7FB;
  --ink:#161620; --ink-2:#54545F; --ink-3:#8B8B97;
  --line:#E9E9F0; --line-2:#F3F3F8;
  --blue:#4269D0; --green:#3CA951; --gold:#EFB118; --coral:#FF725C;
  --accent:#4269D0; --accent-soft:#EDF1FC; --accent-line:#D5E0F7;
  --ok:#3CA951; --ok-bg:#EAF6EE; --ok-line:#CDE9D6;
  --warn-bg:#FBF3DD; --warn-line:#EFDFAE; --warn-ink:#8A6200;
  --crit-bg:#FDECE9; --crit-line:#F6C9C1; --crit-ink:#B3392A;
  --shadow:0 1px 2px rgba(20,20,50,.04),0 14px 34px -20px rgba(20,20,50,.16);
  --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:"DM Mono",ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;
  --serif:"Iowan Old Style",Georgia,"Times New Roman",serif;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#111118; --surface:#181820; --surface-2:#1E1E28;
  --ink:#ECECF2; --ink-2:#AEAEBC; --ink-3:#7E7E8E;
  --line:#2A2A36; --line-2:#22222C;
  --accent:#7C9BE8; --accent-soft:#1B2340; --accent-line:#2E3A63;
  --ok:#5FC177; --ok-bg:#16281C; --ok-line:#274A31;
  --warn-bg:#2E2513; --warn-line:#4A3D1D; --warn-ink:#E8C05A;
  --crit-bg:#2E1A17; --crit-line:#4C2A24; --crit-ink:#FF9A88;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 14px 34px -20px rgba(0,0,0,.6);
}}
:root[data-theme=dark]{
  --bg:#111118; --surface:#181820; --surface-2:#1E1E28;
  --ink:#ECECF2; --ink-2:#AEAEBC; --ink-3:#7E7E8E;
  --line:#2A2A36; --line-2:#22222C;
  --accent:#7C9BE8; --accent-soft:#1B2340; --accent-line:#2E3A63;
  --ok:#5FC177; --ok-bg:#16281C; --ok-line:#274A31;
  --warn-bg:#2E2513; --warn-line:#4A3D1D; --warn-ink:#E8C05A;
  --crit-bg:#2E1A17; --crit-line:#4C2A24; --crit-ink:#FF9A88;
}
:root[data-theme=light]{
  --bg:#FCFCFE; --surface:#FFFFFF; --surface-2:#F7F7FB;
  --ink:#161620; --ink-2:#54545F; --ink-3:#8B8B97;
  --line:#E9E9F0; --line-2:#F3F3F8;
  --accent:#4269D0; --accent-soft:#EDF1FC; --accent-line:#D5E0F7;
  --ok:#3CA951; --ok-bg:#EAF6EE; --ok-line:#CDE9D6;
  --warn-bg:#FBF3DD; --warn-line:#EFDFAE; --warn-ink:#8A6200;
  --crit-bg:#FDECE9; --crit-line:#F6C9C1; --crit-ink:#B3392A;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1400px;margin:0 auto;padding:0 24px 80px}

/* ---------- kop ---------- */
.top{border-bottom:1px solid var(--line);padding:34px 0 22px;margin-bottom:26px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);margin:0 0 10px}
h1{font-family:var(--sans);font-weight:600;font-size:clamp(28px,4vw,42px);line-height:1.1;margin:0 0 6px;
  font-weight:400;letter-spacing:-.01em;text-wrap:balance}
h1 b{font-weight:400;color:var(--ink-3)}
.sub{font-family:var(--serif);font-size:17px;color:var(--ink-2);max-width:62ch;margin:10px 0 0}
.concept{display:inline-block;font-family:var(--mono);font-size:11px;letter-spacing:.06em;
  background:var(--warn-bg);border:1px solid var(--warn-line);padding:3px 9px;border-radius:999px;color:var(--warn-ink);margin-left:10px;
  vertical-align:middle}

.stats{display:flex;flex-wrap:wrap;gap:28px;margin-top:24px;align-items:flex-end}
.stat span{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:2px}
.stat b{font-family:var(--sans);font-size:29px;font-weight:600;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.bar{display:flex;gap:2px;flex:1;min-width:260px;height:38px;margin-left:auto}
.sb{display:flex;flex-direction:column;justify-content:center;padding:0 10px;border-radius:5px;
  min-width:0}
.sb span{font-size:10px;font-family:var(--mono);letter-spacing:.06em;opacity:.9;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sb b{font-size:15px;font-variant-numeric:tabular-nums}
.sb.s-critical{background:var(--crit-bg);border:1px solid var(--crit-line);color:var(--crit-ink)}
.sb.s-high{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink)}
.sb.s-medium{background:var(--accent-soft);border:1px solid var(--accent-line);color:var(--accent)}
.sb.s-low{background:var(--ok-bg);border:1px solid var(--ok-line);color:var(--ok)}
.sb.s-unrated{background:var(--surface-2);border:1px solid var(--line);color:var(--ink-3)}

/* ---------- kolommen ---------- */
.cols{display:grid;grid-template-columns:340px minmax(0,1fr);gap:34px;align-items:start}
@media(max-width:940px){.cols{grid-template-columns:1fr;gap:20px}}

.idx{position:sticky;top:16px;max-height:calc(100vh - 40px);overflow-y:auto;padding-right:6px}
@media(max-width:940px){.idx{position:static;max-height:none}}
.idx-h{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);padding-bottom:8px;border-bottom:1px solid var(--line);margin-bottom:14px}
.grp{margin-bottom:20px}
.grp-h{display:flex;align-items:baseline;gap:8px}
.pat{font-family:var(--sans);font-size:17px;font-weight:600}
.fam{font-family:var(--mono);font-size:10px;color:var(--ink-3);letter-spacing:.08em}
.cnt{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink-3);
  border:1px solid var(--line);border-radius:999px;padding:0 7px;line-height:17px}
.grp-one{margin:3px 0 8px;font-size:13px;color:var(--ink-2);line-height:1.4}
.todo{font-family:var(--mono);font-size:10px;color:var(--ink-3);border:1px dashed var(--line);
  padding:1px 5px;border-radius:2px;white-space:nowrap}
.recs{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
.rec{display:flex;align-items:center;gap:9px;width:100%;text-align:left;background:none;
  border:1px solid transparent;border-radius:7px;padding:6px 8px;cursor:pointer;color:inherit;
  font:inherit;transition:background .12s,border-color .12s}
.rec:hover{background:var(--surface);border-color:var(--line)}
.rec[aria-current=true]{background:var(--accent-soft);border-color:var(--accent-line)}
.rec:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.rid{font-family:var(--mono);font-size:11px;color:var(--ink-3);font-variant-numeric:tabular-nums}
.rtgt{font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sev{margin-left:auto;font-family:var(--mono);font-size:10px;letter-spacing:.03em;
  padding:1px 7px;border-radius:999px;border:1px solid transparent;white-space:nowrap}
.sev.s-critical{background:var(--crit-bg);border-color:var(--crit-line);color:var(--crit-ink)}
.sev.s-high{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn-ink)}
.sev.s-medium{background:var(--accent-soft);border-color:var(--accent-line);color:var(--accent)}
.sev.s-low{background:var(--ok-bg);border-color:var(--ok-line);color:var(--ok)}
.sev.s-unrated{background:var(--surface-2);border-color:var(--line);color:var(--ink-3)}

/* ---------- record ---------- */
.pane{background:var(--surface);border:1px solid var(--line);border-radius:10px;
  box-shadow:var(--shadow);padding:28px 30px}
@media(max-width:600px){.pane{padding:18px}}
.ph{display:flex;gap:18px;justify-content:space-between;align-items:flex-start;
  padding-bottom:16px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.ph-id{font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--accent);margin-bottom:4px}
.ph h2{font-family:var(--sans);font-weight:600;font-size:26px;margin:0;line-height:1.2;text-wrap:balance}
.ph-at{color:var(--ink-3)}
.ph-op{font-size:13px;color:var(--ink-3);margin-top:4px}
.ph-r{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.st{font-family:var(--mono);font-size:10px;padding:1px 7px;border-radius:999px;border:1px solid var(--line);
  color:var(--ink-2)}
.st-resolved{background:var(--ok-bg);border-color:var(--ok-line);color:var(--ok)}
.tlp{font-family:var(--mono);font-size:10px;padding:1px 7px;border-radius:999px;
  background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}

.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:14px;
  padding:16px 0;border-bottom:1px solid var(--line-2)}
.meta span{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--ink-3)}
.meta b{font-family:var(--mono);font-size:13px;font-weight:500;font-variant-numeric:tabular-nums}

section{padding:20px 0;border-bottom:1px solid var(--line-2)}
section:last-child{border-bottom:0;padding-bottom:0}
h3{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);margin:0 0 12px;font-weight:600}
h4{font-family:var(--mono);font-size:10px;letter-spacing:.11em;text-transform:uppercase;
  color:var(--ink-3);margin:16px 0 8px;font-weight:600}
p{margin:0 0 10px}
.note{font-size:13px;color:var(--ink-3);font-family:var(--serif);font-style:italic}
code{font-family:var(--mono);font-size:12px;background:var(--line-2);padding:1px 5px;border-radius:2px}

.vecstr{display:block;font-size:13px;padding:10px 12px;margin-bottom:12px;word-break:break-all;
  border-left:3px solid var(--accent);border-radius:0 6px 6px 0;background:var(--surface-2)}
.vec{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:8px;overflow:hidden}
.ax{background:var(--surface);padding:9px 11px;display:flex;flex-direction:column;gap:1px}
.axk{font-family:var(--mono);font-size:9px;color:var(--ink-3);letter-spacing:.1em}
.axv{font-family:var(--mono);font-size:14px;color:var(--accent)}
.axl{font-size:10px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.07em;margin-top:3px}
.axd{font-family:var(--serif);font-size:14px}
.ind{font-family:var(--mono);font-size:12.5px;line-height:1.6;background:var(--surface-2);
  border:1px solid var(--line);padding:12px 14px;border-radius:8px;margin:0}

.src{border-left:2px solid var(--line);padding:0 0 0 13px;margin-bottom:14px}
.src:last-child{margin-bottom:0}
.src-h{display:flex;gap:10px;align-items:baseline;margin-bottom:3px}
.src-n{font-family:var(--mono);font-size:11px;color:var(--accent);letter-spacing:.04em}
.src-d{font-family:var(--mono);font-size:11px;color:var(--ink-3);font-variant-numeric:tabular-nums}
.src p{font-family:var(--serif);font-size:15px;line-height:1.6;margin:0;color:var(--ink-2)}

.cont{background:var(--accent-soft);border:1px solid var(--accent-line);border-radius:8px;padding:16px 18px}
.cont-big{font-family:var(--sans);font-weight:600;letter-spacing:-.02em;font-size:26px;line-height:1.1;color:var(--accent)}
.cont-meta{font-family:var(--mono);font-size:11px;color:var(--ink-2);margin-top:5px}
.cont p{font-family:var(--serif);font-size:14px;margin:10px 0 0;color:var(--ink-2)}
.cont .earlier{font-size:13px;color:var(--ink-3);font-style:italic}

.meths,.conf,.fals,.prov,.chg{list-style:none;margin:0;padding:0;display:flex;
  flex-direction:column;gap:7px}
.meths li{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap;font-size:13px}
.tier{font-family:var(--mono);font-size:9px;letter-spacing:.09em;text-transform:uppercase;
  padding:2px 6px;border-radius:2px;border:1px solid var(--line);color:var(--ink-2)}
.tier.t-manual{background:var(--accent-soft);border-color:var(--accent-line);color:var(--accent)}
.exp{color:var(--ink-3);font-size:12.5px;flex:1;min-width:180px}
.conf .empty{font-family:var(--serif);font-style:italic;color:var(--ink-3);font-size:13px}

.fals li{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;align-items:baseline;
  padding-bottom:7px;border-bottom:1px dotted var(--line)}
.fals li:last-child{border-bottom:0}
.fo{font-family:var(--mono);font-size:9px;letter-spacing:.07em;text-transform:uppercase;
  padding:2px 6px;border-radius:2px;white-space:nowrap}
.f-excluded .fo{background:var(--ok-bg);color:var(--ok);border:1px solid var(--ok-line)}
.f-untested .fo{background:var(--warn-bg);color:var(--warn-ink);border:1px solid var(--warn-line)}
.fc{font-family:var(--serif);font-size:14.5px}
.fe{grid-column:2;font-size:12px;color:var(--ink-3);font-family:var(--mono);line-height:1.5}

.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13px;min-width:520px}
th{text-align:left;font-family:var(--mono);font-size:9px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;padding:0 12px 7px 0;border-bottom:1px solid var(--line)}
td{padding:8px 12px 8px 0;border-bottom:1px solid var(--line-2);vertical-align:top}
.pstate{font-family:var(--mono);font-size:10px;padding:1px 6px;border-radius:2px;white-space:nowrap;
  border:1px solid var(--line);color:var(--ink-2)}
.pstate.p-fixed{background:var(--ok-bg);border-color:var(--ok-line);color:var(--ok)}

.prov li{font-family:var(--serif);font-size:14.5px;padding-left:14px;position:relative}
.prov li:before{content:"";position:absolute}
.prov li{padding-left:0;display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}
.jur{font-family:var(--mono);font-size:9px;letter-spacing:.08em;padding:2px 6px;border-radius:999px;
  background:var(--accent-soft);border:1px solid var(--accent-line);color:var(--accent);flex:none}
.impl{font-size:12px;color:var(--ink-3);font-family:var(--sans)}
.lw{border:1px solid var(--line);border-radius:8px;padding:13px 15px;margin-top:9px;background:var(--surface-2)}
.lw-h{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;margin-bottom:5px}
.lw-h b{font-family:var(--sans);font-size:14.5px;font-weight:600}
.lw p{font-family:var(--serif);font-size:14px;line-height:1.6;color:var(--ink-2);margin:0}
.cdate{font-family:var(--mono);font-size:11px;color:var(--ink-3)}
.unver{font-family:var(--mono);font-size:9px;letter-spacing:.06em;padding:2px 6px;border-radius:999px;
  background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink)}
.mir{font-size:12px;color:var(--ink-3);margin-top:7px;font-family:var(--sans);
  border-left:2px solid var(--warn-line);padding-left:9px}

.disc{background:var(--surface-2);border:1px solid var(--line);border-radius:8px;padding:15px 17px}
.disc-r{font-family:var(--mono);font-size:11.5px;color:var(--ink-2);margin-bottom:7px}
.disc p{font-family:var(--serif);font-size:14.5px;color:var(--ink-2);margin:0;line-height:1.6}

.chg li{display:grid;grid-template-columns:78px 92px 1fr;gap:10px;font-size:12px;
  font-family:var(--mono);color:var(--ink-3);align-items:baseline}
@media(max-width:600px){.chg li{grid-template-columns:1fr}}
.cat{font-variant-numeric:tabular-nums;color:var(--ink-2)}
.cac{color:var(--accent);overflow:hidden;text-overflow:ellipsis}
.cae{line-height:1.5}

footer{margin-top:44px;padding-top:20px;border-top:1px solid var(--line);
  font-size:12.5px;color:var(--ink-3);max-width:78ch}
footer b{color:var(--ink-2);font-weight:600}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>

<div class="wrap">
<div class="top">
  <p class="eyebrow">Data Protection Exposures</p>
  <h1>Het DPE-register <b>/ dossier Pels Rijcken</b><span class="concept">concept</span></h1>
  <p class="sub">Een register van gemeten privacybevindingen, opgezet zoals CVE dat voor
  kwetsbaarheden doet: de bevinding draagt een naam die je kunt onthouden, het voorval eronder
  een nummer dat je kunt citeren. Elk record vermeldt hoe het is vastgesteld, wat het zou
  ontkrachten, en hoe je het zelf kunt naspelen zonder de tooling van de onderzoeker.</p>
  <div class="stats">
    <div class="stat"><span>Records</span><b>{n_rec}</b></div>
    <div class="stat"><span>Patronen</span><b>{n_pat}</b></div>
    <div class="stat"><span>Doelwitten</span><b>{n_tgt}</b></div>
    <div class="bar">{sev_bar}</div>
  </div>
</div>

<div class="cols">
  <nav class="idx">
    <div class="idx-h">Patronen en records</div>
    {index}
  </nav>
  <main>{panes}</main>
</div>

<footer>
  <p><b>Wat dit wel en niet is.</b> Elk record beschrijft gemeten gedrag op een genoemd moment.
  Het stelt geen onrechtmatigheid vast; dat is aan de Autoriteit Persoonsgegevens of aan de rechter.
  De vector bevat wat is gemeten, het ernstlabel is afgeleid met een openbare regel, en het
  wijzigingsspoor onderaan elk record maakt een stille correctie onmogelijk.</p>
  <p>Bron van dit dossier: het addendum bij de reactie op de publieke verklaring van 22 mei 2026,
  met metingen van 18, 21 en 27 mei 2026 en een Wayback-tijdlijn over vijf domeinen. Onderzoek en
  metingen: Mick Beer. Dit is een werkversie van het registerformaat, geen publicatie.</p>
</footer>
</div>

<script>
const panes = [...document.querySelectorAll('.pane')];
const btns  = [...document.querySelectorAll('.rec')];
function show(id){
  panes.forEach(p => p.hidden = p.id !== 'p-' + id);
  btns.forEach(b => b.setAttribute('aria-current', String(b.dataset.id === id)));
}
btns.forEach(b => b.addEventListener('click', () => {
  show(b.dataset.id);
  if (window.matchMedia('(max-width:940px)').matches)
    document.querySelector('main').scrollIntoView({behavior:'smooth', block:'start'});
}));
show('{first_id}');
</script>
"""

if __name__ == "__main__":
    build()
