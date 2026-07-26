#!/usr/bin/env python3
"""Bouwt de ingang voor wie niet meet.

De catalogus is geschreven voor wie een opname kan lezen. De meeste mensen die
met gegevensbescherming werken zijn jurist of functionaris en zien nooit een
netwerkopname. Zij komen een fout tegen in een verklaring, in een DPIA of in een
gesprek, en moeten van wat ze horen naar het nummer kunnen.

Deze pagina draait de catalogus om: van symptoom naar entry, met per fout de ene
vraag die je stelt, waaraan je een deugdelijk antwoord herkent, en waaraan je een
ontwijkend antwoord herkent. Dat laatste is wat een niet-technicus het hardst
nodig heeft, want daar wordt hij afgeserveerd.
"""
import glob, html, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "register" / "start.html"


def e(s):
    return html.escape(str(s), quote=True)


# Symptomen zoals een jurist of functionaris ze tegenkomt, niet zoals een meter
# ze ziet. De formulering komt uit wat er in een DPIA of een gesprek staat.
SYMPTOMS = [
    ("Er staat een cookiebanner op de site", ["DPE-2026-0001", "DPE-2026-0002", "DPE-2026-0003"],
     "Een banner zegt niets over wat hij tegenhoudt. Deze drie gaan over het moment, het effect van de keuze, en of er uberhaupt geweigerd kan worden."),
    ("De DPIA zegt dat er geen persoonsgegevens worden verwerkt", ["DPE-2026-0010", "DPE-2026-0009"],
     "Toets die zin tegen wat er werkelijk vertrekt. IP-adressen en identifiers tellen mee, ook als de leverancier ze technisch noemt."),
    ("De leverancier noemt een verwerker die niet in de verklaring staat", ["DPE-2026-0010"],
     "De vergelijking tussen de meting en de eigen verklaring is de sterkste toets die er is: beide bronnen zijn van de partij zelf."),
    ("Er wordt een consent-tool of cookiebanner-product gebruikt", ["DPE-2026-0002", "DPE-2026-0001"],
     "Een tool die cookies tegenhoudt kan het laden van scripts ongemoeid laten. Dat een product is aangeschaft, zegt niets over wat het doet."),
    ("Bezoekers vullen een formulier in dat bij een andere partij staat", ["DPE-2026-0008", "DPE-2026-0006"],
     "Kijk naar het adres in de adresbalk van dat formulier. Staat daar een ander domein, dan is de bezoeker ergens anders dan hij denkt."),
    ("Er wordt gemeten hoe bezoekers zich op de pagina gedragen", ["DPE-2026-0005"],
     "Vraag door of het om bezoekcijfers gaat of om opnames van sessies. Dat verschil is groot en wordt zelden uit zichzelf genoemd."),
    ("Het gaat om een apparaat: router, camera, televisie, auto, meter", ["DPE-2026-0012", "DPE-2026-0014", "DPE-2026-0013"],
     "Hier bestaat geen browser om in te kijken en meestal ook geen toestemmingsvraag. Vraag wat het apparaat doet als niemand het gebruikt."),
    ("Er is een app in het spel", ["DPE-2026-0013", "DPE-2026-0012"],
     "Vraag naar de lijst met meegeleverde componenten. Veel ontwikkelaars weten zelf niet wat hun bibliotheken versturen."),
    ("De verwerkersovereenkomst noemt een partij buiten de EU", ["DPE-2026-0009", "DPE-2026-0008"],
     "Waar een bedrijf gevestigd is, is iets anders dan waar de gegevens heen gaan. Beide zijn relevant, maar het zijn twee vragen."),
    ("Iemand zegt dat het niet uitgezet kan worden", ["DPE-2026-0014", "DPE-2026-0012"],
     "Noodzaak is een bewering die te toetsen is: zet het uit en kijk wat er stukgaat."),
]


def build():
    ent = {}
    for f in sorted(glob.glob(str(ROOT / "catalogue" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        ent[d["id"]] = d

    sym = "".join(f'''<div class="sy">
  <h3>{e(t)}</h3><p>{e(why)}</p>
  <div class="lk">{"".join(f'<a href="{e(i)}">{e(i)} &middot; {e(ent[i]["name_nl"] if ent.get(i, {}).get("name_nl") else ent.get(i, {}).get("name", i))}</a>' for i in ids if i in ent)}</div>
</div>''' for t, ids, why in SYMPTOMS)

    rows = []
    for i, x in ent.items():
        ip = x.get("in_practice") or {}
        q = ip.get("audit_question")
        if not q:
            continue
        # het eerste rebuttal is doorgaans het antwoord dat je zult krijgen
        rb = (x["legal"].get("rebuttals") or [{}])[0]
        rows.append(f'''<div class="qa">
  <div class="qa-id"><a href="{e(i)}">{e(i)}</a><span>{e(x.get("name_nl") or x["name"])}</span></div>
  <div class="qa-q"><span class="lab">Stel deze vraag</span><b>{e(q)}</b></div>
  <div class="qa-g"><span class="lab">Een deugdelijk antwoord</span>
    <p>{e(ip.get("complaint", "Een opname of uitdraai die laat zien wat er werkelijk gebeurt, met de datum erbij."))}</p></div>
  <div class="qa-b"><span class="lab">Hier word je afgeserveerd</span>
    <p><em>&ldquo;{e(rb.get("objection", "Dat is standaardgedrag van het product."))}&rdquo;</em></p>
    <p class="ans">{e(rb.get("answer", "Vraag om de meting, niet om de toelichting."))}</p></div>
</div>''')

    page = TPL.replace("{sym}", sym).replace("{qa}", "".join(rows)).replace("{n}", str(len(ent)))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"triagepagina met {len(SYMPTOMS)} symptomen en {len(rows)} vragen -> {OUT}")


TPL = r"""<title>Start hier als je niet meet · DPE</title>
<style>
:root{--bg:#FCFCFE;--surface:#FFF;--surface-2:#F7F7FB;--ink:#161620;--ink-2:#54545F;--ink-3:#8B8B97;
 --line:#E9E9F0;--line-2:#F3F3F8;--accent:#4269D0;--soft:#EDF1FC;--aline:#D5E0F7;
 --ok:#3CA951;--ok-bg:#EAF6EE;--ok-line:#CDE9D6;--warn-bg:#FBF3DD;--warn-line:#EFDFAE;--warn-ink:#8A6200;
 --shadow:0 1px 2px rgba(20,20,50,.04),0 14px 34px -20px rgba(20,20,50,.16);
 --sans:"Inter",ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
 --mono:"DM Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;}
@media(prefers-color-scheme:dark){:root{--bg:#111118;--surface:#181820;--surface-2:#1E1E28;--ink:#ECECF2;
 --ink-2:#AEAEBC;--ink-3:#7E7E8E;--line:#2A2A36;--line-2:#22222C;--accent:#7C9BE8;--soft:#1B2340;
 --aline:#2E3A63;--ok:#5FC177;--ok-bg:#16281C;--ok-line:#274A31;--warn-bg:#2E2513;--warn-line:#4A3D1D;
 --warn-ink:#E8C05A;}}
:root[data-theme=dark]{--bg:#111118;--surface:#181820;--surface-2:#1E1E28;--ink:#ECECF2;--ink-2:#AEAEBC;
 --ink-3:#7E7E8E;--line:#2A2A36;--line-2:#22222C;--accent:#7C9BE8;--soft:#1B2340;--aline:#2E3A63;
 --ok:#5FC177;--ok-bg:#16281C;--ok-line:#274A31;--warn-bg:#2E2513;--warn-line:#4A3D1D;--warn-ink:#E8C05A;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.6}
.in{max-width:980px;margin:0 auto;padding:0 24px 80px}
.bar{border-bottom:1px solid var(--line);padding:16px 0;margin-bottom:34px;font-size:13.5px}
.bar a{color:var(--accent);text-decoration:none}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}
h1{font-size:clamp(28px,4.4vw,42px);font-weight:600;letter-spacing:-.025em;margin:0;line-height:1.1;text-wrap:balance}
.lede{font-size:18.5px;color:var(--ink-2);max-width:64ch;margin:14px 0 0}
h2{font-size:24px;font-weight:600;letter-spacing:-.02em;margin:44px 0 8px}
.note{font-size:15px;color:var(--ink-2);max-width:68ch;margin:0 0 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px}
.sy{background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:19px 21px;box-shadow:var(--shadow)}
.sy h3{font-size:16.5px;font-weight:600;margin:0 0 7px;line-height:1.3}
.sy p{font-size:14px;color:var(--ink-2);margin:0 0 12px}
.lk{display:flex;flex-direction:column;gap:5px}
.lk a{font-size:13.5px;color:var(--accent);text-decoration:none;font-family:var(--mono)}
.lk a:hover{text-decoration:underline}
.qa{background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:20px 22px;
 margin-bottom:14px;box-shadow:var(--shadow);display:grid;grid-template-columns:1fr 1fr;gap:14px 20px}
@media(max-width:720px){.qa{grid-template-columns:1fr}}
.qa-id{grid-column:1/-1;display:flex;gap:10px;align-items:baseline;padding-bottom:10px;border-bottom:1px solid var(--line-2)}
.qa-id a{font-family:var(--mono);font-size:12px;color:var(--accent);text-decoration:none}
.qa-id span{font-weight:600;font-size:16px}
.qa-q{grid-column:1/-1;background:var(--soft);border:1px solid var(--aline);border-radius:8px;padding:14px 16px}
.qa-q b{font-size:17px;font-weight:600;line-height:1.4;display:block}
.lab{display:block;font-family:var(--mono);font-size:9px;letter-spacing:.11em;text-transform:uppercase;
 color:var(--ink-3);margin-bottom:5px}
.qa-q .lab{color:var(--accent)}
.qa-g,.qa-b{border-radius:8px;padding:13px 15px}
.qa-g{background:var(--ok-bg);border:1px solid var(--ok-line)}
.qa-b{background:var(--warn-bg);border:1px solid var(--warn-line)}
.qa-g p,.qa-b p{margin:0;font-size:14px;line-height:1.55;color:var(--ink-2)}
.qa-b em{color:var(--warn-ink);font-style:italic}
.qa-b .ans{margin-top:8px;padding-top:8px;border-top:1px solid var(--warn-line)}
footer{margin-top:44px;padding-top:20px;border-top:1px solid var(--line);color:var(--ink-3);font-size:13px}
</style>
<div class="in">
<nav class="bar"><a href="./">DPE-catalogus</a> &middot; <span>Start hier als je niet meet</span></nav>
<p class="eyebrow">Voor juristen, functionarissen en inkopers</p>
<h1>Je hoeft niet te kunnen meten om te weten wat je moet vragen</h1>
<p class="lede">De catalogus staat vol netwerkopnames en indicatoren. Dat is voor wie zelf meet.
Werk je met gegevensbescherming zonder technische achtergrond, dan kom je een fout ergens anders
tegen: in een DPIA, in een verklaring van een leverancier, of gewoon in een gesprek. Deze pagina
gaat van wat je hoort naar het nummer.</p>

<h2>Waar loop je tegenaan?</h2>
<p class="note">Kies wat het dichtst in de buurt komt. Je krijgt de fouten die daarbij horen, met
per fout de vraag die je kunt stellen.</p>
<div class="grid">{sym}</div>

<h2>De vraag per fout</h2>
<p class="note">Eén vraag per fout, in gewone taal, zonder dat je hoeft te weten hoe je meet.
Daarnaast staat waaraan je een deugdelijk antwoord herkent en waaraan je merkt dat je wordt
afgeserveerd. Dat laatste is geen achterdocht: de meest gehoorde antwoorden gaan langs de vraag
heen, meestal zonder opzet, omdat de leverancier een andere vraag beantwoordt dan je stelde.</p>
{qa}

<footer>
<p>Krijg je een antwoord dat je niet kunt beoordelen, dan is dat op zichzelf informatie. Vraag om de
meting: een netwerkopname met een datum, of een uitdraai uit het beheerpaneel. Wie het goed heeft
geregeld, kan dat leveren. Wie erover moet nadenken, weet het niet.</p>
<p>Deze catalogus kent geen ernst toe en wijst niemand aan. Of een concreet geval onrechtmatig is,
stelt de Autoriteit Persoonsgegevens of de rechter vast.</p>
</footer>
</div>
"""

if __name__ == "__main__":
    build()
