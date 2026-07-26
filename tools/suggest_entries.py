#!/usr/bin/env python3
"""Stelt per artikel voor welke catalogus-entries erin voorkomen.

Bedoeld om te zien waar het loont om nummers toe te voegen, niet om ze
automatisch toe te kennen. Het script herkent woorden, geen bevindingen: het
kan niet zien of een artikel een fout constateert of hem juist weerlegt. Elk
voorstel is dus een leestip, en de beslissing blijft bij de schrijver.

    python3 tools/suggest_entries.py
    python3 tools/suggest_entries.py --min 2 --path /pad/naar/teksten
"""
import argparse, html, json, pathlib, re, sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRONNEN = [
    pathlib.Path("/home/mit/Desktop/manuscript/bron/volledige_artikelen"),
    pathlib.Path("/home/mit/Desktop/manuscript/n"),
    pathlib.Path("/home/mit/Desktop/sporen-bron"),
]

# Signaalwoorden per entry, Nederlands en Engels door elkaar omdat de bronnen
# dat ook zijn. Bewust smal gehouden: een term die overal voorkomt levert ruis
# en ruis maakt het overzicht waardeloos.
SIGNALS = {
    "DPE-2026-0001": ["voor toestemming", "pre-consent", "voordat de bezoeker", "zonder toestemming",
                      "voor de vraag", "vuurt", "vuren", "before consent", "geen actie"],
    "DPE-2026-0002": ["weigeren", "geweigerd", "blijven actief", "blijft actief", "verandert niets",
                      "niet gekoppeld", "honoreert", "afwijzen"],
    "DPE-2026-0003": ["geen weigeroptie", "alleen accepteren", "niet weigeren", "weigeren mogelijk",
                      "geen mogelijkheid om te weigeren"],
    "DPE-2026-0004": ["399", "bewaartermijn", "geldigheidsduur", "bewaartermijnen", "expires"],
    "DPE-2026-0005": ["session recording", "sessieopname", "hotjar", "clarity", "muisbeweging",
                      "opname van de sessie", "schermopname"],
    "DPE-2026-0006": ["zoekterm", "zoekopdracht", "zoekwoord", "ingevulde", "query", "triage"],
    "DPE-2026-0007": ["fingerprint", "vingerafdruk", "canvas", "tijdzone", "navigator-eigenschappen",
                      "apparaatkenmerken"],
    "DPE-2026-0008": ["nieuwsbrief", "aanmeldformulier", "formulier op", "crm", "landingspagina",
                      "interesseprofiel"],
    "DPE-2026-0009": ["google fonts", "jquery", "hotlink", "gstatic", "googleapis", "ingeladen van",
                      "cdn van"],
    "DPE-2026-0010": ["privacyverklaring", "niet genoemd", "ontbreekt in de", "verklaring stelde",
                      "niet vermeld"],
    "DPE-2026-0011": ["tag manager", "gtm-", "container", "niet in de broncode", "raw html",
                      "uit de html verdwijnt"],
    "DPE-2026-0012": ["firmware", "router", "omvormer", "telemetrie", "belt naar huis", "apparaat stuurt",
                      "camera stuurt", "naar china", "naar rusland"],
    "DPE-2026-0013": ["sdk", "bibliotheek", "library", "apk", "in de app", "meegeleverde component"],
    "DPE-2026-0014": ["uit te zetten", "uitschakelen", "opt-out", "instelling ontbreekt",
                      "niet uitzetten", "geen instelling"],
}


def tekst(p):
    raw = p.read_text(encoding="utf-8", errors="replace")
    if p.suffix in (".html", ".htm"):
        raw = re.sub(r"(?s)<(script|style).*?</\1>", " ", raw)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw)


def titels():
    out = {}
    for f in sorted((ROOT / "catalogue").glob("DPE-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[d["id"]] = d["name"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=2, help="minimaal aantal treffers per entry")
    ap.add_argument("--path", action="append", help="extra map om te doorzoeken")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    dirs = [pathlib.Path(p) for p in (a.path or [])] or BRONNEN
    namen = titels()
    onbekend = [k for k in SIGNALS if k not in namen]
    if onbekend:
        print(f"let op: signaalwoorden voor {', '.join(onbekend)} maar die entry bestaat niet "
              f"(meer). Werk SIGNALS bij.\n", file=sys.stderr)

    files = []
    for d in dirs:
        if not d.exists():
            print(f"overgeslagen, bestaat niet: {d}", file=sys.stderr)
            continue
        files += [f for f in d.rglob("*") if f.suffix in (".html", ".htm", ".md", ".txt")]

    if not files:
        print("geen bronbestanden gevonden")
        return 2

    resultaat, per_entry = [], defaultdict(int)
    for f in sorted(files):
        t = tekst(f).lower()
        if len(t) < 400:
            continue
        hits = {}
        for eid, words in SIGNALS.items():
            found = [w for w in words if w in t]
            if len(found) >= a.min:
                hits[eid] = found
                per_entry[eid] += 1
        if hits:
            resultaat.append({"file": str(f), "name": f.stem[:70], "hits": hits})

    if a.json:
        print(json.dumps(resultaat, ensure_ascii=False, indent=2))
        return 0

    print(f"{len(files)} bestanden doorzocht, {len(resultaat)} met een voorstel "
          f"(drempel: {a.min} signaalwoorden)\n")
    for r in sorted(resultaat, key=lambda x: -len(x["hits"]))[:40]:
        print(f"{r['name']}")
        for eid, found in sorted(r["hits"].items(), key=lambda kv: -len(kv[1])):
            print(f"   {eid}  {namen.get(eid, '?'):34s} {', '.join(found[:4])}")
        print()

    print("Per entry, in hoeveel stukken hij lijkt voor te komen:")
    for eid, n in sorted(per_entry.items(), key=lambda kv: -kv[1]):
        print(f"   {n:3d}x  {eid}  {namen.get(eid, '?')}")

    print("""
Dit herkent woorden, geen bevindingen. Een stuk dat uitlegt waarom iets juist
GEEN probleem is, scoort hier hetzelfde als een stuk dat het constateert. Lees
het voorstel na voor je een nummer toevoegt, en begin bij de stukken die het
meest gelezen worden: met terugwerkende kracht je hele archief nummeren kost
dagen en levert weinig.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
