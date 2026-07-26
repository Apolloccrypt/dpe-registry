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
import glob, importlib.util, json, pathlib

# site.py heet net zo als een module van Python zelf, en die staat bij het
# starten al in sys.modules. Een gewone import levert dus de verkeerde op.
_p = pathlib.Path(__file__).resolve().parent / "site.py"
_spec = importlib.util.spec_from_file_location("dpe_site", _p)
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "register" / "uitleg.html"
e = S.e


# Symptomen zoals een jurist of functionaris ze tegenkomt, niet zoals een meter
# ze ziet. De formulering komt uit wat er in een DPIA of een gesprek staat.
GEBOUWD = "26 juli 2026"

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
    ("Er zit advertentieverkoop op de site of in de app", ["DPE-2026-0015", "DPE-2026-0016", "DPE-2026-0020"],
     "Bij een advertentieveiling gaat een bezoek naar tientallen partijen tegelijk, niet naar een. Vraag om de lijst met wie er mag meebieden."),
    ("Er wordt een identiteitsbewijs of BSN verwerkt", ["DPE-2026-0017", "DPE-2026-0018"],
     "Vraag wat er van het document wordt vastgelegd en hoe lang. Vaak is de vraag ja of nee, en gaat het hele document mee."),
    ("Het gaat om zorg, geloof, seksualiteit of een uitkering", ["DPE-2026-0019", "DPE-2026-0006"],
     "Bijzondere gegevens hoeven niet ingetypt te zijn om te vertrekken. De naam van een pagina of een gebeurtenis kan het al verraden."),
    ("Er wordt betaald of een transactie afgerond", ["DPE-2026-0025", "DPE-2026-0006"],
     "Vraag wie er in de keten zit die niet nodig is om de betaling uit te voeren."),
    ("Een meter, camera of sensor levert metingen aan", ["DPE-2026-0022", "DPE-2026-0024", "DPE-2026-0023"],
     "Niet de meting zelf is het punt maar hoe vaak en hoe herkenbaar. Een reeks per kwartier laat zien wanneer iemand thuis is."),
    ("Ik lees een onderzoeksrapport van iemand anders", ["DPE-2026-0026", "DPE-2026-0027", "DPE-2026-0028", "DPE-2026-0029"],
     "Vier fouten die onderzoekers zelf maken. Staat er hoe is toegeschreven, van wanneer de landendatabase is, en of er echt is gemeten of alleen in de code gekeken?"),
    ("Er staat geen cookiebanner, maar wel meetverkeer", ["DPE-2026-0011", "DPE-2026-0007", "DPE-2026-0021"],
     "Wat je niet in de broncode ziet, kan er wel zijn. Vraag om de versiegeschiedenis van de tagcontainer."),
    ("De cookies blijven heel lang staan", ["DPE-2026-0004"],
     "Kijk naar de bewaartermijn, niet naar het aantal. Een jaar of langer vraagt om een reden die verder gaat dan de standaardinstelling."),
    ("Er gaat een nieuwsbrief of mailing uit", ["DPE-2026-0030", "DPE-2026-0031"],
     "Vraag of er wordt bijgehouden wie een bericht opent, en of het e-mailadres ook naar andere diensten gaat."),
    ("Mensen loggen in op een account", ["DPE-2026-0032", "DPE-2026-0033"],
     "Achter een login gebeurt vaak meer dan ervoor. Vraag of het account aan het volgprofiel wordt gekoppeld, en wat er wordt gedeeld bij inloggen via een andere partij."),
    ("Er worden logbestanden of back-ups bewaard", ["DPE-2026-0034", "DPE-2026-0035"],
     "Vraag wat er in de logs staat en of een verwijderverzoek ook de back-up bereikt. Een gegeven dat terugkomt bij een herstel is niet gewist."),
    ("Het gaat om medewerkers en hun werkapparatuur", ["DPE-2026-0036", "DPE-2026-0037", "DPE-2026-0038"],
     "In een gezagsverhouding is toestemming zelden vrij. Vraag wat er per persoon wordt geteld, of het scherm wordt opgenomen, en of een dienstvoertuig ook buiten werktijd wordt gevolgd."),
    ("Het gaat om onderwijs of examens", ["DPE-2026-0039", "DPE-2026-0019"],
     "Vraag bij toezichtsoftware wat er wordt waargenomen, welk oordeel daaruit volgt, en hoe lang dat oordeel de uitslag overleeft."),
    ("Bezoekers moeten betalen of accepteren", ["DPE-2026-0040", "DPE-2026-0003"],
     "Een weigeroptie die geld kost is een andere vraag dan een weigeroptie die ontbreekt. Vraag wat de prijs is en waarop die is gebaseerd."),
    ("Er wordt een AI-dienst gebruikt", ["DPE-2026-0041", "DPE-2026-0034"],
     "Vraag of wat gebruikers invoeren standaard wordt bewaard om het model te verbeteren, en of dat uit te zetten is zonder de dienst te verliezen."),
    ("Medewerkers gebruiken browseruitbreidingen", ["DPE-2026-0042", "DPE-2026-0013"],
     "Vraag welke rechten de uitbreiding vraagt en welke functie die rechten nodig heeft. Verklaarde toegang bestaat ook als er nog niets is verstuurd."),
    ("Twee overheidsregistraties worden gekoppeld", ["DPE-2026-0043", "DPE-2026-0017"],
     "Beide instanties mogen het persoonsnummer hebben. De vraag is of de koppeling zelf een grondslag heeft."),
    ("Er staat een chatvenster of chatbot op de site", ["DPE-2026-0006", "DPE-2026-0005", "DPE-2026-0009"],
     "Een chatvenster is meestal een venster van een andere partij. Alles wat de bezoeker daar intypt komt daar terecht, en het venster staat er ook als er niemand chat."),
    ("De site is gebouwd of wordt beheerd door een extern bureau", ["DPE-2026-0011", "DPE-2026-0010", "DPE-2026-0009"],
     "Vraag wie er meetcode mag toevoegen zonder de site te wijzigen, en wie de privacyverklaring bijhoudt. Dat zijn bijna nooit dezelfde mensen, en daar ontstaat het gat."),
    ("Er staat een video, een kaart of een lettertype van een andere partij op de site", ["DPE-2026-0009", "DPE-2026-0020"],
     "Voor de bezoeker is het een onderdeel van uw pagina. Voor de partij aan de andere kant is elke paginaweergave een bezoek, ook als niemand op de video klikt."),
    ("Wij hebben laten scannen en er kwam niets uit", ["DPE-2026-0029", "DPE-2026-0020", "DPE-2026-0011"],
     "Een schone uitkomst en een mislukte meting zien er hetzelfde uit. Vraag hoeveel geldige metingen eronder liggen en wat de scan niet kon zien."),
    ("Wij zijn een zorg-, welzijns- of gemeentelijke organisatie", ["DPE-2026-0019", "DPE-2026-0048", "DPE-2026-0006"],
     "Bij deze organisaties verraadt de naam van een pagina vaak al waarom iemand er is, en binnen de muren is de vraag wie er bij een dossier kan."),
    ("Er wordt een app uitgedeeld aan medewerkers of clienten", ["DPE-2026-0013", "DPE-2026-0028", "DPE-2026-0046"],
     "Vraag om de lijst met meegeleverde onderdelen en om een opname van de eerste keer opstarten. Wat in het pakket zit en wat er verstuurt zijn twee vragen."),
    ("Wij kopen iets in en moeten er eisen over opschrijven", ["DPE-2026-0001", "DPE-2026-0002", "DPE-2026-0014", "DPE-2026-0010"],
     "Dit is de goedkoopste plek om het te regelen. Elke entry bevat een inkoopeis die op de oplevering te toetsen is, en die hoeft u niet zelf te toetsen."),
    ("Iemand heeft een inzageverzoek gedaan en wij weten niet wat we hebben", ["DPE-2026-0010", "DPE-2026-0035", "DPE-2026-0016"],
     "Wat er over iemand bestaat, staat deels bij partijen die u niet hebt aangewezen en deels in kopieen die een verwijdering niet bereikt hebben."),
    ("De leverancier zegt dat alles binnen de EU blijft", ["DPE-2026-0009", "DPE-2026-0020", "DPE-2026-0027"],
     "Waar iets staat, waar een bedrijf gevestigd is en waar het verkeer heen gaat zijn drie verschillende dingen. Vraag welke van de drie is gemeten en met welke landendatabase."),
    ("De cookiebanner heeft twee knoppen, maar weigeren kost meer moeite", ["DPE-2026-0044", "DPE-2026-0003", "DPE-2026-0040"],
     "Tel de handelingen aan beide kanten en meet de knoppen. Dat is geen mening maar een telling, en u kunt hem zelf doen."),
    ("Er staat een camera aan de gevel of bij de deur", ["DPE-2026-0047", "DPE-2026-0024"],
     "Vraag wat de camera in beeld heeft en welk deel daarvan nodig was. Zodra het beeld verder reikt dan het eigen terrein, verandert de vraag."),
    ("Wij bewaren logbestanden en niemand weet hoe lang", ["DPE-2026-0045", "DPE-2026-0034"],
     "Vraag om de oudste regel die er nog staat en om de termijn die zegt dat hij er mag staan. Die twee liggen zelden bij dezelfde persoon."),
]


def build():
    ent = {}
    for f in sorted(glob.glob(str(ROOT / "catalogue" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        ent[d["id"]] = d

    # De kaart wijst naar het vraagblok op deze pagina, niet naar de Engelse
    # detailpagina. Wie op een symptoom klikt wil eerst de vraag zien.
    sym = "".join(f'''<div class="sy">
  <h3>{e(t)}</h3><p>{e(why)}</p>
  <div class="lk">{"".join(f'<a href="#v-{e(i)}">{e(i)} &middot; {e(ent[i]["name_nl"] if ent.get(i, {}).get("name_nl") else ent.get(i, {}).get("name", i))}</a>' for i in ids if i in ent)}</div>
</div>''' for t, ids, why in SYMPTOMS)

    rows = []
    for i, x in ent.items():
        ip = x.get("in_practice") or {}
        q = ip.get("audit_question_nl") or ip.get("audit_question")
        if not q:
            continue
        # het eerste rebuttal is doorgaans het antwoord dat je zult krijgen
        rb = (x["legal"].get("rebuttals") or [{}])[0]
        rows.append(f'''<div class="qa" id="v-{e(i)}">
  <div class="qa-id"><a href="{e(i)}/">{e(i)}</a><span>{e(x.get("name_nl") or x["name"])}</span></div>
  <div class="qa-q"><span class="lab">Stel deze vraag</span><b>{e(q)}</b></div>
  <div class="qa-g"><span class="lab">Een deugdelijk antwoord</span>
    <p>{e(ip.get("complaint_nl") or "Een opname of uitdraai die laat zien wat er werkelijk gebeurt, met de datum erbij en het land van waaruit is gemeten.")}</p></div>
  <div class="qa-b"><span class="lab">Hier word je afgeserveerd</span>
    <p><em>&ldquo;{e(ip.get("objection_nl") or rb.get("objection", "Dat is standaardgedrag van het product."))}&rdquo;</em></p>
    <p class="ans">{e(ip.get("answer_nl") or rb.get("answer", "Vraag om de meting, niet om de toelichting."))}</p></div>
</div>''')

    # De volledige lijst, gegroepeerd per familie, onderaan dezelfde pagina.
    FAM, SYS = S.FAM, S.SYS
    fams = {}
    for x in ent.values():
        fams.setdefault(x["family"], []).append(x)
    lijst = []
    for fam in sorted(fams, key=lambda f: -len(fams[f])):
        lijst.append(f'<h3 class="lf">{e(FAM.get(fam, fam))}</h3><table class="lt"><tbody>')
        for x in sorted(fams[fam], key=lambda y: y["id"]):
            lijst.append(
                f'<tr><td class="li"><a href="{e(x["id"])}/">{e(x["id"])}</a></td>'
                f'<td><a class="ln" href="{e(x["id"])}/">{e(x.get("name_nl") or x["name"])}</a>'
                f'<span class="ls">{e(x.get("summary_nl") or x["summary"])}</span></td>'
                f'<td class="lw">{e(", ".join(SYS.get(s2, s2) for s2 in x["applies_to"]))}</td></tr>')
        lijst.append("</tbody></table>")

    page = (S.head("Van symptoom naar nummer · DPE-register",
                   "Van wat je in een DPIA of een leveranciersverklaring tegenkomt naar het "
                   "nummer in de DPE-catalogus, met per fout de vraag die je stelt.",
                   up="", cur="uitleg.html", css=CSS)
            + BODY.replace("{sym}", sym).replace("{qa}", "".join(rows))
                  .replace("{n}", str(len(ent))).replace("{lijst}", "".join(lijst))
                  .replace("{gebouwd}", GEBOUWD)
            + S.foot(up=""))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"triagepagina met {len(SYMPTOMS)} symptomen en {len(rows)} vragen -> {OUT}")


CSS = r"""
footer .meta{font-size:12.5px;color:var(--ink-3);margin-top:10px}
.in{max-width:980px;padding-bottom:20px;font-size:16px}
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
.lf{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
 color:var(--ink-3);margin:26px 0 8px;font-weight:600}
.lt{border-collapse:collapse;width:100%}
.lt td{padding:10px 14px 10px 0;border-bottom:1px solid var(--line-2);vertical-align:top}
.li{font-family:var(--mono);font-size:12px;white-space:nowrap;width:1%}
.li a{color:var(--accent);text-decoration:none}
.ln{font-weight:600;font-size:15.5px;color:inherit;text-decoration:none;display:block}
.ln:hover{color:var(--accent)}
.ls{display:block;font-size:13.5px;color:var(--ink-3);margin-top:2px;line-height:1.5}
.lw{font-family:var(--mono);font-size:10.5px;color:var(--ink-3);white-space:nowrap;text-align:right}
@media(max-width:640px){.lw{display:none}}
.slot{margin-top:44px;padding-top:20px;border-top:1px solid var(--line);color:var(--ink-3);font-size:13px}
.slot p{max-width:72ch}
"""

BODY = r"""<div class="in">
<nav class="bar" aria-label="Kruimelpad"><a href="./">Database</a><span class="sp">/</span><span>Van symptoom naar nummer</span></nav>
<p class="eyebrow">Data Protection Exposures &middot; as 04, privacy</p>
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

<section id="proces">
<h2>Wat je doet met een bevinding</h2>
<p class="note">Vinden is het makkelijke deel. Hier loopt het meestal vast, dus dit is de route.</p>
<div class="grid">
  <div class="sy"><h3>1 · Vraag om de meting</h3>
    <p>Niet om een toelichting maar om een uitkomst. Wie het goed geregeld heeft, levert het
    binnen een week. Wie erover moet nadenken, weet het niet, en dat is zelf een antwoord.</p>
    <p style="font-size:13.5px;color:var(--ink-3)">Wij toetsen deze verwerking tegen de
    DPE-catalogus. Graag een meting volgens DPE-meetmethode 1.0, met meetdatum, land van meting
    en de ruwe meetbestanden. Termijn: [datum].</p></div>
  <div class="sy"><h3>2 · Lees de uitkomst</h3>
    <p>Je hoeft alleen te kijken of er een datum bij staat en vanuit welk land is gemeten.
    Ontbreekt een van beide, stuur het terug. Dat is een vormvereiste, geen technisch oordeel,
    en die mag je stellen.</p>
    <p style="font-size:13.5px;color:var(--ink-3)">Aangetroffen, niet aangetroffen, of niet
    getoetst. Dat laatste is geen uitkomst.</p></div>
  <div class="sy"><h3>3 · Stel een termijn</h3>
    <p>Deze bevindingen zijn in de regel geen datalek: een datalek veronderstelt een inbreuk op de
    beveiliging en dit zijn bouwkeuzes. Er loopt dus meestal geen meldtermijn van 72 uur. Beoordeel
    dat wel apart wanneer er inloggegevens of bijzondere gegevens onbedoeld bij een derde
    terechtkomen; dan kunnen beide waar zijn. Dertig dagen is redelijk voor iets dat neerkomt op een
    instelling wijzigen.</p>
    <p style="font-size:13.5px;color:var(--ink-3)">DPE-2026-0001 herstellen voor [datum],
    aantonen met een hermeting volgens dezelfde methode.</p></div>
  <div class="sy"><h3>4 · Laat hermeten</h3>
    <p>Zonder hermeting heb je een toezegging en geen herstel. Werk daarna het
    verwerkingsregister bij als er een ontvanger in beeld kwam die er niet in stond.</p>
    <p style="font-size:13.5px;color:var(--ink-3)">Wordt er niet hersteld, leg dan vast dat je
    hebt geadviseerd en wat het antwoord was. Dat is je taak en het beschermt jou.</p></div>
</div>
<p class="note" style="margin-top:20px">De goedkoopste plek om dit te regelen is voordat er iets
gebouwd is. Eén zin in het bestek: de oplevering is vrij van de bevindingen DPE-2026-0001 tot en
met 0004, aan te tonen met een meting volgens DPE-meetmethode 1.0. Dat is toetsbaar, waar privacy
by design dat niet is, en je hoeft het niet zelf te toetsen.</p>
</section>

<footer>
<p>Krijg je een antwoord dat je niet kunt beoordelen, dan is dat op zichzelf informatie. Vraag om de
meting: een netwerkopname met een datum, of een uitdraai uit het beheerpaneel. Wie het goed heeft
geregeld, kan dat leveren. Wie erover moet nadenken, weet het niet.</p>
<p>Deze catalogus kent geen ernst toe en wijst niemand aan. Of een concreet geval onrechtmatig is,
stelt de Autoriteit Persoonsgegevens of de rechter vast.</p>
<p class="meta">Verder lezen, alles in de bron:
<a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/METHOD.md">de meetmethode</a> &middot;
<a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/WANTED.md">wat er nog niet af is</a> &middot;
<a href="https://github.com/Apolloccrypt/dpe-registry/blob/main/CONTRIBUTING.md">hoe je bijdraagt</a> &middot;
<a href="https://github.com/Apolloccrypt/dpe-registry/tree/main/repro">naspelen</a></p>
<p class="meta">Schema 2.0 &middot; gebouwd op {gebouwd} &middot; licentie CC BY 4.0 &middot;
nummers zijn permanent en worden nooit hergebruikt.</p>
</footer>
</div>
"""

if __name__ == "__main__":
    build()
