#!/usr/bin/env python3
"""Rendert de catalogus: de fouten, zonder doelwitten."""
import glob, html, json, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "site" / "catalogus.html"
FAM = {"consent": "Consent", "data": "Data", "chain": "Chain", "transfer": "Transfer",
       "transparency": "Transparency", "retention": "Retention", "telemetry": "Telemetry",
       "method": "Method"}
SYS = {"web": "web", "mobile-app": "app", "firmware": "firmware", "iot": "IoT",
       "vehicle": "vehicle", "desktop": "desktop", "api": "API", "network-device": "network device"}
TIER = {"manual": "by hand", "bookmarklet": "bookmarklet", "script": "script", "suite": "suite"}


def e(s):
    return html.escape(str(s), quote=True)


def build():
    ent = [json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
           for f in sorted(glob.glob(str(ROOT / "catalogue" / "*.json")))]
    law, case = {}, {}
    try:
        import yaml
        for d, b in ((ROOT / "law", law), (ROOT / "caselaw", case)):
            for f in d.glob("*.yaml"):
                x = yaml.safe_load(f.read_text(encoding="utf-8"))
                b[x["id"]] = x
    except ImportError:
        pass

    fams = {}
    for x in ent:
        fams.setdefault(x["family"], []).append(x)

    nav = []
    for fam in sorted(fams, key=lambda f: -len(fams[f])):
        nav.append(f'<div class="ng"><div class="ng-h">{e(FAM.get(fam, fam))}'
                   f'<span class="cnt">{len(fams[fam])}</span></div><ul>')
        for x in sorted(fams[fam], key=lambda y: y["id"]):
            nav.append(f'<li><button class="nb" data-id="{e(x["id"])}">'
                       f'<span class="nn">{e(x["name"])}</span>'
                       f'<span class="nid">{e(x["id"].replace("DPE-", ""))}</span></button></li>')
        nav.append("</ul></div>")

    panes = []
    for x in ent:
        m, d = x["mechanism"], x["detection"]
        sys_ = "".join(f'<span class="sys">{e(SYS.get(s, s))}</span>' for s in x["applies_to"])
        causes = "".join(f"<li>{e(c)}</li>" for c in m.get("common_causes", []))
        fals = "".join(
            f'<li><span class="fk fk-{e(f["checkable"])}">{e({"automated": "automated", "manual": "by hand", "not-from-capture": "not from the capture"}[f["checkable"]])}</span>'
            f'<span class="fc">{e(f["condition"])}</span>'
            + (f'<span class="fn">{e(f["note"])}</span>' if f.get("note") else "")
            + (f'<span class="fi">{e({"drop": "finding falls", "reclassify": "reclassify", "weaken": "weakens"}[f["if_true"]])}</span>' if f.get("if_true") else "")
            + "</li>" for f in x["falsifiers"])
        caps = "".join(f"<li>{e(c)}</li>" for c in d.get("capture_requirements", []))
        meth = "".join(f'<li><span class="tier">{e(TIER.get(t["tier"], t["tier"]))}</span>'
                       f'<code>{e(t["path"])}</code>'
                       + (f'<span class="exp">{e(t["expect"])}</span>' if t.get("expect") else "")
                       + "</li>" for t in x["reproduction"]["methods"])
        scan = "".join(f'<span class="sc">{e(s)}</span>'
                       for s in x["reproduction"].get("public_scanners", []))
        rebut = "".join(f'<div class="rb"><p class="rq">{e(r["objection"])}</p>'
                        f'<p class="ra">{e(r["answer"])}</p></div>'
                        for r in x["legal"].get("rebuttals", []))
        prov = "".join(
            f'<li><span class="jur">{e(law[p]["jurisdiction"])}</span><b>{e(law[p]["reference"])}</b>'
            f'<span class="pt">{e(law[p].get("title", ""))}</span></li>'
            if p in law else f"<li><code>{e(p)}</code></li>" for p in x["legal"]["provisions"])
        cl = "".join(
            f'<li><span class="jur">{e(case[c].get("jurisdiction", "EU"))}</span>'
            f'<b>{e(case[c]["case"])}</b><code>{e(case[c].get("ecli", ""))}</code>'
            f'<span class="pt">{e(case[c].get("relevance", "")[:160])}</span></li>'
            if c in case else f"<li><code>{e(c)}</code></li>" for c in x["legal"].get("caselaw", []))
        nav_ = f'<div class="nav-note">{e(x["not_a_vulnerability"])}</div>' if x.get("not_a_vulnerability") else ""
        rel = "".join(f'<button class="relb" data-id="{e(r)}">{e(r)}</button>' for r in x.get("related", []))
        ip = x.get("in_practice") or {}
        prac = ""
        if ip:
            rows = "".join(
                f'<div class="pr"><div class="pr-h">{e(h)}</div><p>{e(ip[k])}</p></div>'
                for k, h in (("dpia", "In a DPIA, verify this"),
                             ("procurement", "As a procurement clause"),
                             ("complaint", "With a complaint, hand over")) if ip.get(k))
            q = f'<div class="askq"><span>The one question that surfaces it</span><b>{e(ip["audit_question"])}</b></div>' if ip.get("audit_question") else ""
            prac = f'<section class="prac"><h3>Where this plugs into existing processes</h3>{q}<div class="prg">{rows}</div></section>' 

        panes.append(f'''<article class="pane" id="p-{e(x["id"])}" hidden>
  <header class="ph">
    <div><div class="pid">{e(x["id"])}</div>
      <h2>{e(x["name"])}</h2>
      <p class="psum">{e(x["summary"])}</p></div>
    <div class="pmeta"><span class="fam">{e(FAM.get(x["family"], x["family"]))}</span>{sys_}</div>
  </header>
  {nav_}
  <section><h3>What it is</h3><p>{e(m["what"])}</p></section>
  <section><h3>Why it is a separate entry</h3><p>{e(m["why_it_matters"])}</p></section>
  {f'<section><h3>How it arises</h3><ul class="pl">{causes}</ul></section>' if causes else ''}
  {f'<section><h3>Not to be confused with</h3><p>{e(m["not_this"])}</p></section>' if m.get("not_this") else ''}
  <section><h3>How to establish it</h3>
    <div class="ind">{e(d["indicator"])}</div>
    <div class="qod"><span>method</span><b>{e(d["method"])}</b><span>QoD</span><b>{d["qod"]}</b></div>
    {f'<h4>Requirements on the measurement</h4><ul class="pl">{caps}</ul>' if caps else ''}
  </section>
  <section><h3>What would refute it</h3><ul class="fals">{fals}</ul></section>
  {prac}
  <section><h3>Reproduction</h3><ul class="meths">{meth}</ul>
    {f'<h4>Third parties that can confirm it</h4><div class="scans">{scan}</div>' if scan else ''}</section>
  <section><h3>Legal framing</h3><ul class="prov">{prov}</ul>
    {f'<h4>Case law</h4><ul class="prov">{cl}</ul>' if cl else ''}
    {f'<h4>Objections, and the answer</h4>{rebut}' if rebut else ''}</section>
  <section><h3>What this does not establish</h3>
    <ul class="pl">{"".join(f"<li>{e(l)}</li>" for l in x["does_not_establish"])}</ul></section>
  {f'<section><h3>Related</h3><div class="rels">{rel}</div></section>' if rel else ''}
</article>''')

    page = TPL.replace("{n}", str(len(ent))).replace("{nf}", str(len(fams)))
    page = page.replace("{nav}", "\n".join(nav)).replace("{panes}", "\n".join(panes))
    page = page.replace("{first}", ent[0]["id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"{len(ent)} fouten gerenderd naar {OUT}")


TPL = r"""<title>DPE Catalogue</title>
<style>
:root{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;--ink-3:#8B8B97;
 --line:#E9E9F0;--line-2:#F3F3F8;--blue:#4269D0;--green:#3CA951;--gold:#EFB118;--coral:#FF725C;
 --accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;--ok:#3CA951;--ok-bg:#EAF6EE;--ok-line:#CDE9D6;
 --warn-bg:#FBF3DD;--warn-line:#EFDFAE;--warn-ink:#8A6200;--crit-bg:#FDECE9;--crit-line:#F6C9C1;--crit-ink:#B3392A;
 --shadow:0 1px 2px rgba(20,20,50,.04),0 14px 34px -20px rgba(20,20,50,.16);
 --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 --mono:"DM Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
 --serif:"Iowan Old Style",Georgia,serif;}
@media(prefers-color-scheme:dark){:root{--bg:#111118;--surface:#181820;--surface-2:#1E1E28;--ink:#ECECF2;
 --ink-2:#AEAEBC;--ink-3:#7E7E8E;--line:#2A2A36;--line-2:#22222C;--accent:#7C9BE8;--soft:#1B2340;--aline:#2E3A63;
 --ok:#5FC177;--ok-bg:#16281C;--ok-line:#274A31;--warn-bg:#2E2513;--warn-line:#4A3D1D;--warn-ink:#E8C05A;
 --crit-bg:#2E1A17;--crit-line:#4C2A24;--crit-ink:#FF9A88;}}
:root[data-theme=dark]{--bg:#111118;--surface:#181820;--surface-2:#1E1E28;--ink:#ECECF2;--ink-2:#AEAEBC;
 --ink-3:#7E7E8E;--line:#2A2A36;--line-2:#22222C;--accent:#7C9BE8;--soft:#1B2340;--aline:#2E3A63;
 --ok:#5FC177;--ok-bg:#16281C;--ok-line:#274A31;--warn-bg:#2E2513;--warn-line:#4A3D1D;--warn-ink:#E8C05A;}
:root[data-theme=light]{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;
 --ink-3:#8B8B97;--line:#E9E9F0;--line-2:#F3F3F8;--accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6}
.wrap{max-width:1320px;margin:0 auto;padding:0 24px 80px}
.top{border-bottom:1px solid var(--line);padding:36px 0 24px;margin-bottom:26px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}
h1{font-size:clamp(28px,4vw,40px);font-weight:600;letter-spacing:-.022em;margin:0;line-height:1.1;text-wrap:balance}
.sub{font-size:17px;color:var(--ink-2);max-width:66ch;margin:12px 0 0}
.pill{display:inline-block;font-family:var(--mono);font-size:11px;padding:3px 9px;border-radius:999px;
 background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink);margin-left:10px;vertical-align:middle}
.notice{margin-top:20px;background:var(--surface);border:1px solid var(--line);border-radius:10px;
 padding:16px 19px;max-width:78ch;box-shadow:var(--shadow)}
.notice p{font-size:14.5px;color:var(--ink-2);margin:0 0 9px}
.notice p:last-child{margin:0}
.notice b{color:var(--ink)}
.stats{display:flex;gap:30px;margin-top:22px;flex-wrap:wrap}
.stat span{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3)}
.stat b{font-size:28px;font-weight:600;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.cols{display:grid;grid-template-columns:250px minmax(0,1fr);gap:34px;align-items:start}
@media(max-width:900px){.cols{grid-template-columns:1fr}}
.idx{position:sticky;top:16px;max-height:calc(100vh - 40px);overflow-y:auto}
@media(max-width:900px){.idx{position:static;max-height:none}}
.ng{margin-bottom:18px}
.ng-h{display:flex;align-items:center;font-family:var(--mono);font-size:10px;letter-spacing:.13em;
 text-transform:uppercase;color:var(--ink-3);padding-bottom:6px;border-bottom:1px solid var(--line);margin-bottom:7px}
.cnt{margin-left:auto;font-variant-numeric:tabular-nums}
.ng ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1px}
.nb{display:flex;align-items:baseline;gap:8px;width:100%;text-align:left;background:none;border:1px solid transparent;
 border-radius:7px;padding:6px 9px;cursor:pointer;color:inherit;font:inherit;transition:background .12s}
.nb:hover{background:var(--surface)}
.nb[aria-current=true]{background:var(--soft);border-color:var(--aline)}
.nn{font-weight:500;font-size:14px;line-height:1.35}
.nid{margin-left:auto;font-family:var(--mono);font-size:10.5px;color:var(--ink-3);font-variant-numeric:tabular-nums}
.pane{background:var(--surface);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);padding:30px 32px}
@media(max-width:600px){.pane{padding:20px}}
.ph{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;padding-bottom:18px;border-bottom:1px solid var(--line)}
.pid{font-family:var(--mono);font-size:12px;color:var(--accent);letter-spacing:.05em;margin-bottom:3px}
.ph h2{margin:0;font-size:31px;font-weight:600;letter-spacing:-.025em;line-height:1.1;text-wrap:balance}
.pen{margin:3px 0 0;font-family:var(--mono);font-size:12.5px;color:var(--ink-3);letter-spacing:.01em}
.psum{margin:6px 0 0;font-size:17px;color:var(--ink-2);max-width:60ch}
.pmeta{display:flex;gap:6px;flex-wrap:wrap;align-items:flex-start}
.fam,.sys{font-family:var(--mono);font-size:10px;letter-spacing:.06em;padding:3px 9px;border-radius:999px;white-space:nowrap}
.fam{background:var(--soft);border:1px solid var(--aline);color:var(--accent)}
.sys{background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.nav-note{margin-top:18px;background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:9px;
 padding:13px 16px;font-size:14px;color:var(--warn-ink)}
.nav-note:before{content:"Not a vulnerability. ";font-weight:600}
section{padding:20px 0;border-bottom:1px solid var(--line-2)}
section:last-child{border-bottom:0;padding-bottom:0}
h3{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);margin:0 0 10px;font-weight:600}
h4{font-family:var(--mono);font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3);margin:18px 0 8px;font-weight:600}
p{margin:0 0 10px;max-width:74ch}
.pl{margin:0;padding-left:18px;color:var(--ink-2);font-size:14.5px}
.pl li{margin-bottom:4px}
code{font-family:var(--mono);font-size:12px;background:var(--line-2);padding:1px 6px;border-radius:4px}
.ind{font-family:var(--mono);font-size:13px;line-height:1.65;background:var(--surface-2);border:1px solid var(--line);
 border-left:3px solid var(--accent);padding:13px 15px;border-radius:0 8px 8px 0}
.qod{display:flex;gap:8px;align-items:baseline;margin-top:11px;font-family:var(--mono);font-size:12px;flex-wrap:wrap}
.qod span{color:var(--ink-3);font-size:9px;letter-spacing:.1em;text-transform:uppercase}
.qod b{font-weight:500;margin-right:14px}
.fals,.meths{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:9px}
.fals li{display:grid;grid-template-columns:auto 1fr;gap:5px 10px;align-items:baseline;
 padding-bottom:9px;border-bottom:1px dotted var(--line)}
.fals li:last-child{border-bottom:0}
.fk{font-family:var(--mono);font-size:9px;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:999px;white-space:nowrap}
.fk-automated{background:var(--ok-bg);border:1px solid var(--ok-line);color:var(--ok)}
.fk-manual{background:var(--soft);border:1px solid var(--aline);color:var(--accent)}
.fk-not-from-capture{background:var(--warn-bg);border:1px solid var(--warn-line);color:var(--warn-ink)}
.fc{font-size:14.5px}
.fn,.fi{grid-column:2;font-size:12.5px;color:var(--ink-3)}
.fi{font-family:var(--mono);font-size:10px;letter-spacing:.05em;text-transform:uppercase}
.meths li{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap;font-size:13px}
.tier{font-family:var(--mono);font-size:9px;letter-spacing:.07em;text-transform:uppercase;padding:2px 7px;
 border-radius:999px;background:var(--soft);border:1px solid var(--aline);color:var(--accent);white-space:nowrap}
.exp{color:var(--ink-3);font-size:12.5px;flex:1;min-width:200px}
.scans{display:flex;gap:6px;flex-wrap:wrap}
.sc{font-family:var(--mono);font-size:11px;padding:3px 9px;border-radius:999px;background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2)}
.prov{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}
.prov li{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap;font-size:14px}
.jur{font-family:var(--mono);font-size:9px;letter-spacing:.07em;padding:2px 7px;border-radius:999px;
 background:var(--soft);border:1px solid var(--aline);color:var(--accent);flex:none}
.prov b{font-weight:600}
.pt{color:var(--ink-3);font-size:13px}
.rb{border-left:2px solid var(--line);padding-left:14px;margin-bottom:14px}
.rq{font-weight:600;font-size:14.5px;margin:0 0 3px}
.rq:before{content:"\201C"}.rq:after{content:"\201D"}
.ra{font-family:var(--serif);font-size:15px;color:var(--ink-2);margin:0;line-height:1.6}
.prac .askq{background:var(--soft);border:1px solid var(--aline);border-radius:9px;padding:14px 17px;margin-bottom:14px}
.askq span{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;text-transform:uppercase;color:var(--accent);margin-bottom:4px}
.askq b{font-size:16.5px;font-weight:600;line-height:1.4}
.prg{display:grid;grid-template-columns:repeat(auto-fit,minmax(232px,1fr));gap:1px;background:var(--line);
 border:1px solid var(--line);border-radius:9px;overflow:hidden}
.pr{background:var(--surface);padding:13px 15px}
.pr-h{font-family:var(--mono);font-size:9px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-bottom:5px}
.pr p{margin:0;font-size:13.5px;color:var(--ink-2);line-height:1.55}
.rels{display:flex;gap:7px;flex-wrap:wrap}
.relb{font-family:var(--mono);font-size:11px;padding:5px 11px;border-radius:999px;background:var(--surface-2);
 border:1px solid var(--line);color:var(--ink-2);cursor:pointer}
.relb:hover{background:var(--soft);border-color:var(--aline);color:var(--accent)}
button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
footer{margin-top:44px;padding-top:20px;border-top:1px solid var(--line);color:var(--ink-3);font-size:13px;max-width:80ch}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
<div class="wrap">
<div class="top">
  <p class="eyebrow">Data Protection Exposures</p>
  <h1>The catalogue<span class="pill">draft</span></h1>
  <p class="sub">Numbered faults in how systems handle personal data, so that researchers, regulators and
  suppliers can refer to the same thing. Not vulnerabilities: there is nothing to exploit, the system does
  what its builder intended, and that intention is the objection. Which is why no CVE exists for any of this.</p>
  <div class="notice">
    <p><b>What the number is for.</b> Referability. A fault with a title and a number does not need
    explaining again in every publication, and two researchers who find the same thing now call it the
    same thing.</p>
    <p><b>What is deliberately absent.</b> No severity, no score, no judgement of harm. CVE does not weigh
    either; NVD does that, separately. How heavily a concrete case weighs depends on that case and belongs
    to whoever applies the entry. No company and no product appears here: whoever establishes that a system
    exhibits one of these faults publishes that themselves and cites the number.</p>
  </div>
  <div class="stats">
    <div class="stat"><span>Faults</span><b>{n}</b></div>
    <div class="stat"><span>Families</span><b>{nf}</b></div>
    <div class="stat"><span>Schema</span><b>2.0</b></div>
  </div>
</div>
<div class="cols">
  <nav class="idx">{nav}</nav>
  <main>{panes}</main>
</div>
<footer>
  <p>Every entry describes the behaviour of a system, not the behaviour of an organisation, and the
  catalogue assigns no severity. Whether a concrete case is unlawful, and how heavily it weighs, is for a
  supervisory authority or a court. The catalogue names the provisions in play per jurisdiction, so an
  entry is usable outside one country: the behaviour is the same across the EEA and only the citation
  differs.</p>
</footer>
</div>
<script>
const panes=[...document.querySelectorAll('.pane')];
const btns=[...document.querySelectorAll('.nb')];
function show(id){
  panes.forEach(p=>p.hidden=p.id!=='p-'+id);
  btns.forEach(b=>b.setAttribute('aria-current',String(b.dataset.id===id)));
}
document.addEventListener('click',ev=>{
  const b=ev.target.closest('.nb,.relb'); if(!b) return;
  show(b.dataset.id);
  if(b.classList.contains('relb')||window.matchMedia('(max-width:900px)').matches)
    document.querySelector('main').scrollIntoView({behavior:'smooth',block:'start'});
});
show('{first}');
</script>
"""

if __name__ == "__main__":
    build()
