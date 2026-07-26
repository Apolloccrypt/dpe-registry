#!/usr/bin/env python3
"""Zet ontbrekende regelbestanden op uit wat de records al vastleggen.

Let op de richting: normaal is de regel de bron en het record het gevolg. Hier
gaat het andersom, omdat de eerste records zijn ingelezen uit een dossier dat er
al lag. Dit script is dus eenmalig bedoeld, als startpunt.

Wat het oplevert is een stub met de indicator, de QoD en de falsifiers die in de
records voorkomen. Wat een mens daarna nog moet toevoegen staat als TODO in het
bestand: de opnamecondities en wat de regel niet mag concluderen. Zolang die
TODO's erin staan, is de regel niet af.
"""
import json, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dpe

ROOT = pathlib.Path(__file__).resolve().parent.parent

TEMPLATE = """# DPE detection rule (stub, opgezet uit bestaande records)
#
# TODO voor een mens: vul requires_capture en does_not_establish aan, en
# controleer of de indicator hieronder scherp genoeg is om zonder oordeel
# toegepast te kunnen worden. Zolang deze regel er staat, is de rule niet af.

id: {slug}
rule_version: 1
pattern: {slug}
info:
  name: {name}
  family: {family}
  authors: [dpe-registry]

requires_capture:
  profile: clean
  interaction: none
  artefact: har
  attribution: [{attribution}]
  forbidden_attribution:
    - referer   # spoofbaar, en meetinstrumentatie doet dat ook

match:
  indicator: >
    {indicator}

qod:
  method: {method}
  value: {qod}
  basis: {basis}

falsifiers:
{falsifiers}
does_not_establish:
  - lawfulness; that is for a supervisory authority or a court
  - absence: no detection in one capture is not evidence of absence
  # TODO: wat deze regel specifiek niet kan zien

reproduction:
  manual: repro/{slug}/MANUAL.md      # TODO: schrijven
  script: repro/{slug}/{slug}.mjs     # TODO: schrijven
  independent:
    - urlscan.io
    - webbkoll
"""

NAMES = {
    "maxstay": ("MaxStay", "consent"), "overshoulder": ("Overshoulder", "data"),
    "offbooks": ("OffBooks", "transparency"), "sideload": ("Sideload", "method"),
    "hotlink": ("Hotlink", "transfer"), "silhouette": ("Silhouette", "data"),
    "handover": ("Handover", "chain"), "onedoor": ("OneDoor", "consent"),
}


def main():
    made = []
    by_pattern = {}
    for _, r in dpe.load_records(ROOT):
        by_pattern.setdefault(r["pattern"], []).append(r)

    for slug, recs in sorted(by_pattern.items()):
        out = ROOT / "rules" / f"{slug}.yaml"
        if out.exists():
            continue
        r = recs[0]
        d = r.get("detection", {})
        name, family = NAMES.get(slug, (slug.title(), "unclassified"))

        # falsifiers ontdubbeld over alle records van dit patroon
        seen, lines = set(), []
        for rec in recs:
            for c in rec.get("falsifier", {}).get("conditions", []):
                if c["condition"] in seen:
                    continue
                seen.add(c["condition"])
                lines.append(f"  - condition: {c['condition']}\n"
                             f"    check: {'automated' if c['tested'] else 'manual'}\n"
                             f"    on_true: {'drop' if c['outcome'] == 'excluded' else 'reclassify'}")
        out.write_text(TEMPLATE.format(
            slug=slug, name=name, family=family,
            attribution=r.get("falsifier", {}).get("attribution", "har-pageref"),
            indicator=d.get("indicator", "TODO"), method=d.get("method", "network-observed"),
            qod=d.get("qod", 90), basis=d.get("basis", "traffic-property"),
            falsifiers="\n".join(lines) + "\n"), encoding="utf-8")
        made.append(slug)

    print(f"{len(made)} regel(s) opgezet: {', '.join(made) or 'geen'}")
    if made:
        print("Deze zijn nog stubs. Zie de TODO's erin.")


if __name__ == "__main__":
    main()
