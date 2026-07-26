#!/usr/bin/env python3
"""Maakt van een meting een rapport dat een functionaris kan lezen.

Dit is de brug waar het op vastloopt. De functionaris kan niet meten, de
ontwikkelaar meet niet uit zichzelf, en de uitkomst van een meting is een
JSON-bestand dat niemand zonder techniek kan beoordelen. Daardoor voelt niemand
zich eigenaar en gebeurt er niets.

Hier draait een ontwikkelaar een commando en er komt een document uit dat in een
DPIA-dossier past: wat is getoetst, wat is gevonden, wat betekent het, en wat de
volgende stap is. Geen jargon, geen hostnamen, geen JSON.

    node repro/web/check.mjs example.nl
    python3 tools/rapport.py example.nl-dpe.json > rapport.md
"""
import argparse, datetime, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://totaledigitalewaarborging.nl/register"


def entries():
    out = {}
    for f in sorted((ROOT / "catalogue").glob("DPE-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[d["id"]] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resultaat", help="het JSON-bestand uit check.mjs")
    ap.add_argument("--organisatie", default="", help="naam van de opdrachtgever, voor in de kop")
    ap.add_argument("--land", default="NL", help="land van waaruit is gemeten")
    ap.add_argument("--door", default="", help="wie de meting heeft uitgevoerd")
    a = ap.parse_args()

    r = json.loads(pathlib.Path(a.resultaat).read_text(encoding="utf-8"))
    cat = entries()
    datum = r.get("measured_at", "")[:10] or datetime.date.today().isoformat()
    res = r.get("results", [])
    gevonden = [x for x in res if x.get("verdict") == "present"]
    schoon = [x for x in res if x.get("verdict") == "not-found"]
    onbekend = [x for x in res if x.get("verdict") not in ("present", "not-found")]

    def titel(i):
        e = cat.get(i, {})
        return e.get("name_nl") or e.get("name") or i

    L = []
    w = L.append

    w(f"# Meting gegevensbescherming: {r.get('site', '?')}")
    w("")
    if a.organisatie:
        w(f"**Opdrachtgever** {a.organisatie}  ")
    w(f"**Onderzocht systeem** {r.get('site', '?')}  ")
    w(f"**Meetdatum** {datum}  ")
    w(f"**Gemeten vanuit** {a.land}  ")
    if a.door:
        w(f"**Uitgevoerd door** {a.door}  ")
    w(f"**Methode** DPE-meetmethode 1.0, {BASE}  ")
    w(f"**Getoetste bevindingen** {len(res)} van de catalogus")
    w("")
    w("---")
    w("")

    # Samenvatting eerst, want dat is wat gelezen wordt
    w("## Samenvatting")
    w("")
    if gevonden:
        w(f"Van de {len(res)} getoetste bevindingen zijn er **{len(gevonden)} aangetroffen**.")
        w("")
        for x in gevonden:
            w(f"- **{x['entry']}** · {titel(x['entry'])}")
        w("")
        w("Geen van deze bevindingen is een datalek. Er loopt dus geen meldtermijn van")
        w("72 uur. Het gaat om verwerkingen waarvan de grondslag of de informatieplicht")
        w("aandacht vraagt, en dat is herstelbaar.")
    else:
        w(f"Van de {len(res)} getoetste bevindingen is er **geen aangetroffen** op de")
        w("meetdatum. Dat is geen goedkeuring: er is naar deze bevindingen gekeken en")
        w("niet naar alles, en een site verandert.")
    if onbekend:
        w("")
        w(f"{len(onbekend)} bevinding(en) konden niet worden getoetst. Zie de laatste sectie.")
    w("")

    # Per bevinding, in taal die zonder techniek te lezen is
    if gevonden:
        w("## Wat er is gevonden")
        w("")
        for x in gevonden:
            e = cat.get(x["entry"], {})
            m = e.get("mechanism", {})
            ip = e.get("in_practice", {})
            w(f"### {x['entry']} · {titel(x['entry'])}")
            w("")
            if m.get("what"):
                w(f"{m['what']}")
                w("")
            if m.get("why_it_matters"):
                w(f"**Waarom dit telt.** {m['why_it_matters']}")
                w("")
            prov = e.get("legal", {}).get("provisions", [])
            if prov:
                w(f"**Raakt aan** {', '.join(prov)}")
                w("")
            if ip.get("audit_question"):
                w(f"**Vraag die u kunt stellen.** “{ip['audit_question']}”")
                w("")
            d = x.get("detail")
            if d:
                w("<details><summary>Technische onderbouwing van deze uitkomst</summary>")
                w("")
                w("```json")
                w(json.dumps(d, ensure_ascii=False, indent=2))
                w("```")
                w("")
                w("</details>")
                w("")
            w(f"Volledige beschrijving: {BASE}/{x['entry']}")
            w("")

    if schoon:
        w("## Niet aangetroffen")
        w("")
        w("Op de meetdatum niet gevonden. Dit veroudert: een wijziging aan de site kan")
        w("een bevinding alsnog introduceren, en dat gebeurt vaker via een marketingtag")
        w("dan via een softwarewijziging.")
        w("")
        for x in schoon:
            w(f"- {x['entry']} · {titel(x['entry'])}")
        w("")

    if onbekend:
        w("## Niet getoetst")
        w("")
        w("Hiervoor ontbrak een voorwaarde. Dit is geen uitkomst en mag niet als")
        w("“in orde” worden gelezen.")
        w("")
        for x in onbekend:
            reden = (x.get("detail") or {}).get("reason", "geen reden vastgelegd")
            w(f"- {x['entry']} · {titel(x['entry'])} — {reden}")
        w("")

    w("## Voorgestelde vervolgstappen")
    w("")
    if gevonden:
        w("1. Leg deze meting vast in het DPIA-dossier, met datum en methodeversie.")
        w("2. Vraag de verwerkingsverantwoordelijke om herstel, met een termijn. Vier")
        w("   weken is redelijk voor bevindingen die neerkomen op een instelling.")
        w("3. Laat na herstel opnieuw meten. Zonder hermeting is er alleen een toezegging.")
        w("4. Werk het verwerkingsregister bij als er een ontvanger in beeld kwam die")
        w("   daar nog niet in stond.")
        w("5. Wordt er niet hersteld, leg dan vast dat u hebt geadviseerd en wat het")
        w("   antwoord was.")
    else:
        w("1. Leg deze meting vast in het dossier, met datum en methodeversie.")
        w("2. Herhaal de meting bij een volgende wijziging aan het systeem, en anders")
        w("   periodiek. Een schone meting veroudert.")
    w("")

    w("## Over deze meting")
    w("")
    w("De uitkomsten komen uit een openbaar beschreven methode. Iedereen kan ze")
    w("nameten; de meetinstructie per bevinding staat op de registerpagina.")
    w("")
    w("**Wat deze meting niet vaststelt.** Niet of iets onrechtmatig is: dat stelt de")
    w("Autoriteit Persoonsgegevens of een rechter vast. Niet of er opzet in het spel")
    w("was. En niet dat er verder niets is: er is gekeken naar de bevindingen in de")
    w("catalogus, op één moment, vanuit één land.")
    w("")
    cond = r.get("conditions", {})
    if cond:
        w("**Meetcondities.** " + "; ".join(f"{k.replace('_', ' ')}: {v}" for k, v in cond.items()))
        w("")
    caps = r.get("captures") or []
    if caps:
        w(f"**Bewaarde meetbestanden.** {', '.join(caps)}. Deze zijn door een derde na te")
        w("lezen zonder bijzondere software.")

    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
