#!/usr/bin/env python3
"""Zet de catalogus als tabel in de README.

Wie op de repository landt wil de lijst zien, niet eerst een map met JSON
openen. De tabel wordt gegenereerd tussen twee markeringen, zodat hij niet kan
achterlopen op de entries en niemand hem met de hand hoeft bij te werken.

    python3 tools/build_readme_list.py
"""
import collections, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://totaledigitalewaarborging.nl/register"
FAM = {"consent": "Toestemming", "data": "Gegevens", "chain": "Keten", "transfer": "Doorgifte",
       "transparency": "Transparantie", "retention": "Bewaring", "telemetry": "Telemetrie",
       "method": "Methode"}
SYS = {"web": "web", "mobile-app": "app", "firmware": "firmware", "iot": "IoT",
       "vehicle": "voertuig", "desktop": "desktop", "api": "API",
       "network-device": "netwerkapparaat"}


def main():
    ent = [json.loads(f.read_text(encoding="utf-8"))
           for f in sorted((ROOT / "catalogue").glob("DPE-*.json"))]
    fam = collections.OrderedDict()
    for x in sorted(ent, key=lambda y: y["id"]):
        fam.setdefault(x["family"], []).append(x)

    L = ["<!-- BEGIN CATALOGUS: gegenereerd door tools/build_readme_list.py -->", "",
         f"## De catalogus ({len(ent)} fouten)", "",
         f"Elke fout heeft een eigen pagina op <{BASE}> met de indicator, de eisen",
         "aan de meting, wat hem zou ontkrachten, en hoe je hem naspeelt.", ""]
    for f in sorted(fam, key=lambda k: -len(fam[k])):
        L += [f"### {FAM.get(f, f)}", "", "| | Fout | Waar |", "|---|---|---|"]
        for x in fam[f]:
            L.append(f"| [`{x['id']}`]({BASE}/{x['id']}) | "
                     f"**{x.get('name_nl') or x['name']}**<br>"
                     f"{x.get('summary_nl') or x['summary']} | "
                     f"{', '.join(SYS.get(s, s) for s in x['applies_to'])} |")
        L.append("")
    L.append("<!-- END CATALOGUS -->")

    r = ROOT / "README.md"
    s = r.read_text(encoding="utf-8")
    block = "\n".join(L)
    if "BEGIN CATALOGUS" in s:
        s = re.sub(r"<!-- BEGIN CATALOGUS.*?<!-- END CATALOGUS -->", block, s, flags=re.S)
    else:
        s = s.replace("## What is in an entry", block + "\n## What is in an entry")
    r.write_text(s, encoding="utf-8")
    print(f"{len(ent)} fouten in de README, {len(fam)} families")


if __name__ == "__main__":
    main()
