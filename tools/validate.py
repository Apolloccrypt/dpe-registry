#!/usr/bin/env python3
"""De poortwachter.

Draait op elke inzending en op elke wijziging. Wat hier rood wordt, komt het
register niet in. Dat is geen moderatie maar rekenwerk: de bot zegt precies wat
er ontbreekt en daar valt niet over te discussieren.

    python3 tools/validate.py                 alles
    python3 tools/validate.py path/to.json    één bestand

Exitcode 1 bij fouten, zodat CI erop kan afgaan.
"""
import json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dpe

ROOT = pathlib.Path(__file__).resolve().parent.parent
ERRORS, WARNINGS = [], []


def err(rid, msg):
    ERRORS.append(f"{rid}: {msg}")


def warn(rid, msg):
    WARNINGS.append(f"{rid}: {msg}")


def check_schema(records):
    try:
        import jsonschema
    except ImportError:
        warn("-", "jsonschema niet beschikbaar, schemacontrole overgeslagen")
        return
    schema = json.loads((ROOT / "schema" / "dpe-record-1.0.schema.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    for f, r in records:
        for e in v.iter_errors(r):
            err(f.name, f"schema: {'/'.join(str(p) for p in e.path) or 'root'}: {e.message[:160]}")


def check_ids(records):
    seen = {}
    for f, r in records:
        rid = r.get("id", "?")
        if f.stem != rid:
            err(f.name, f"bestandsnaam wijkt af van het id ({rid})")
        if rid in seen:
            err(rid, f"dubbel id, ook in {seen[rid]}")
        seen[rid] = f.name


def check_severity(records):
    """Het ernstlabel wordt herberekend, niet geloofd. Zo kan niemand een label
    opschroeven of afzwakken zonder de vector te veranderen, en de vector is de
    meting."""
    for f, r in records:
        rid = r.get("id", f.name)
        vec = r.get("vector", "")
        if not dpe.VECTOR_RE.match(vec):
            err(rid, f"vector voldoet niet aan de notatie: {vec}")
            continue
        want = dpe.severity(vec)
        got = r.get("severity", {})
        if got.get("label") != want:
            err(rid, f"ernst '{got.get('label')}' klopt niet met de vector; afgeleid wordt '{want}'")
        if got.get("rule") != dpe.SEVERITY_RULE:
            err(rid, f"severity.rule moet {dpe.SEVERITY_RULE} zijn")


def check_detection(records):
    for f, r in records:
        rid = r["id"]
        d = r.get("detection")
        if not d:
            warn(rid, "geen detection-blok; methode en QoD zijn dan onbekend")
            continue
        if dpe.QOD.get(d["method"]) != d["qod"]:
            err(rid, f"qod {d['qod']} hoort niet bij methode {d['method']} "
                     f"(verwacht {dpe.QOD.get(d['method'])})")
        if not (ROOT / "rules" / f"{d['rule']}.yaml").exists():
            err(rid, f"verwijst naar rule '{d['rule']}' die niet bestaat")
        s = d.get("samples")
        if s and s["positive"] > s["taken"]:
            err(rid, "meer positieve metingen dan metingen")
        if s and s["taken"] == 1:
            warn(rid, "gebaseerd op een enkele meting; herhaling maakt de claim sterker")


def check_pattern(records):
    for f, r in records:
        p = ROOT / "registry" / f"{r['pattern']}.md"
        if not p.exists():
            warn(r["id"], f"pattern '{r['pattern']}' heeft nog geen uitgeschreven pagina")


def check_publication(records):
    """De regels die publicatie blokkeren. Dit is waar het register zijn eigen
    beloftes afdwingt in plaats van ze op te schrijven."""
    for f, r in records:
        rid, st = r["id"], r["status"]
        if st not in ("published", "resolved", "disputed", "corrected"):
            continue
        if not r.get("disclosure"):
            err(rid, "gepubliceerd zonder wederhoorspoor")
        conds = r.get("falsifier", {}).get("conditions", [])
        if not conds:
            err(rid, "gepubliceerd zonder falsifiers")
        if dpe.axes(r["vector"])["EV"] == "M" and not any(c["tested"] for c in conds):
            err(rid, "gemeten record zonder een enkele getoetste falsifier")
        for c in conds:
            if c["outcome"] == "untested" and not c.get("evidence"):
                err(rid, f"ongetoetste falsifier zonder toelichting: {c['condition'][:60]}")
        if r["falsifier"].get("attribution") == "referer":
            err(rid, "attributie via referer is niet toegestaan; die is te spoofen")
        if not r.get("sources"):
            err(rid, "geen bronnen")
        if dpe.axes(r["vector"])["EV"] == "S" and r["tlp"] in ("CLEAR", "GREEN"):
            err(rid, "een vermoeden (EV:S) mag niet publiek gedeeld worden")


def check_reproduction(records):
    for f, r in records:
        m = r.get("reproduction", {}).get("methods", [])
        if not any(x["tier"] in ("manual", "script") for x in m):
            err(r["id"], "geen reproductie buiten de eigen tooling om; "
                         "minstens een manual- of script-methode is verplicht")
        for x in m:
            p = x.get("path")
            if p and not (ROOT / p).exists():
                warn(r["id"], f"reproductiepad bestaat nog niet: {p}")
        if not r["reproduction"].get("independent_confirmation"):
            warn(r["id"], "nog geen onafhankelijke scan gekoppeld (urlscan, Webbkoll, Blacklight)")


def check_changes(records):
    for f, r in records:
        ch = r.get("changes", [])
        ats = [c["at"] for c in ch]
        if ats != sorted(ats):
            err(r["id"], "wijzigingsspoor staat niet op volgorde; het is append-only")


def main():
    argv = sys.argv[1:]
    if argv:
        records = [(pathlib.Path(a), json.loads(pathlib.Path(a).read_text(encoding="utf-8"))) for a in argv]
    else:
        records = dpe.load_records(ROOT)

    if not records:
        print("geen records gevonden")
        return 0

    for fn in (check_schema, check_ids, check_severity, check_detection,
               check_pattern, check_publication, check_reproduction, check_changes):
        fn(records)

    print(f"gecontroleerd: {len(records)} records")
    print(f"methodiek-hash: {dpe.methodology_hash(ROOT)[:16]}")
    if WARNINGS:
        print(f"\n{len(WARNINGS)} waarschuwing(en), blokkeren niet:")
        for w in WARNINGS:
            print(f"  · {w}")
    if ERRORS:
        print(f"\n{len(ERRORS)} FOUT(EN):")
        for e in ERRORS:
            print(f"  ✗ {e}")
        return 1
    print("\nalles in orde")
    return 0


if __name__ == "__main__":
    sys.exit(main())
