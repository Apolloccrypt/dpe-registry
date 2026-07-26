#!/usr/bin/env python3
"""Kent een DPE-nummer toe aan binnengekomen inzendingen.

Waarom de indiener zelf geen nummer kiest: twee mensen die op dezelfde dag een
pull request openen zouden allebei hetzelfde nummer claimen, en dan botsen ze bij
het mergen. CVE lost dat op door blokken nummers uit te delen aan uitgevers. Wij
lossen het simpeler op: een inzending komt naamloos binnen in _incoming/ en
krijgt pas een nummer op het moment dat hij wordt opgenomen.

    python3 tools/assign_id.py --year 2026 [--dry-run]

Nummers worden nooit hergebruikt, ook niet na intrekking, want elders staan
verwijzingen naar dat nummer.
"""
import argparse, json, pathlib, sys, datetime

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dpe

ROOT = pathlib.Path(__file__).resolve().parent.parent
INCOMING = ROOT / "observations" / "_incoming"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", default=str(datetime.date.today().year))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--actor", default="assign_id", help="wie de opname uitvoert")
    a = ap.parse_args()

    if not INCOMING.exists():
        print("geen _incoming/, niets te doen")
        return 0

    files = sorted(p for p in INCOMING.glob("*.json") if not p.name.startswith("."))
    if not files:
        print("geen inzendingen")
        return 0

    stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    assigned = []
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        rid = dpe.next_id(ROOT, a.year)

        rec["id"] = rid
        # Ernst wordt hier afgeleid, niet overgenomen: wat de indiener invulde
        # doet er niet toe, de vector is de meting.
        rec["severity"] = {"label": dpe.severity(rec["vector"]), "rule": dpe.SEVERITY_RULE}
        # Een inzending komt binnen als concept. De uitgever zet de status om na
        # review en wederhoor; dat is een aparte, zichtbare handeling.
        rec["status"] = "draft"
        rec.setdefault("changes", []).append({
            "at": stamp, "actor": a.actor,
            "entries": [f"Record accepted from submission {f.name}.",
                        f"Identifier {rid} assigned.",
                        f"Severity derived ({dpe.SEVERITY_RULE}): {rec['severity']['label']}.",
                        "Status set to draft pending editorial review."]})

        target = ROOT / "observations" / f"{rid}.json"
        print(f"{f.name}  ->  {rid}  ({rec['severity']['label']}, {rec['pattern']})")
        if not a.dry_run:
            target.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            f.unlink()
        assigned.append(rid)

    if a.dry_run:
        print("\n(dry run, niets geschreven)")
    else:
        print(f"\n{len(assigned)} inzending(en) opgenomen: {', '.join(assigned)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
