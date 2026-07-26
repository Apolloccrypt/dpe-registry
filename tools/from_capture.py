#!/usr/bin/env python3
"""Zet een set opnames om in uitspraken per catalogus-entry.

Het koppelvlak is bewust een HAR en niet een tool. Wie met een scanner meet
levert HAR's; wie met de browser meet slaat er een op; beide komen hier binnen
en krijgen dezelfde behandeling. Daarmee hangt geen enkele uitspraak van dit
register af van gereedschap dat het register zelf bezit, en dat is precies wat
een uitspraak overeind houdt als iemand hem aanvecht.

    python3 tools/from_capture.py runs/example.nl/
    python3 tools/from_capture.py noop.har reject.har --domain example.nl

Een map wordt doorzocht op *.har. De consent-mode wordt afgeleid uit de
bestandsnaam: noop of pre voor geen interactie, reject of deny voor weigeren,
accept voor accepteren. Wat niet te herleiden is, telt als noop en dat wordt
gemeld, want een verkeerd toegewezen mode levert een zelfverzekerd fout antwoord.
"""
import argparse, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import replay

MODES = [("noop", r"noop|no-?action|pre|geen"), ("reject", r"reject|deny|refus|weiger"),
         ("accept", r"accept|allow|akkoord")]

# Welke entry welke regel gebruikt, en welke modes daarvoor nodig zijn.
ENTRIES = {
    "DPE-2026-0001": ("frontrun", ["noop"], "Tracking before consent"),
    "DPE-2026-0002": ("hollowno", ["noop", "reject"], "Refusal without effect"),
    "DPE-2026-0004": ("maxstay", ["noop"], "Maximum cookie lifetime"),
    "DPE-2026-0009": ("hotlink", ["noop"], "Third-party resource loading"),
    "DPE-2026-0011": ("sideload", ["noop"], "Tag loaded outside the source"),
}


def mode_of(name):
    n = name.lower()
    for mode, pat in MODES:
        if re.search(pat, n):
            return mode
    return None


def load(paths):
    caps = {}
    unknown = []
    for p in paths:
        p = pathlib.Path(p)
        files = sorted(p.glob("*.har")) if p.is_dir() else [p]
        for f in files:
            m = mode_of(f.name)
            if m is None:
                unknown.append(f.name)
                m = "noop"
            caps.setdefault(m, []).append(f)
    return caps, unknown


def hosts(har):
    entries, root, _ = replay.parse(json.loads(pathlib.Path(har).read_text(encoding="utf-8")))
    return {e["host"] for e in entries if replay.registrable(e["host"]) != root}, root


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="HAR-bestanden of een map met opnames")
    ap.add_argument("--domain", help="alleen ter labeling van de uitvoer")
    ap.add_argument("--json", action="store_true", help="machineleesbare uitvoer")
    a = ap.parse_args()

    caps, unknown = load(a.paths)
    if not caps:
        print("geen HAR-bestanden gevonden")
        return 2
    if unknown:
        print(f"let op: consent-mode niet af te leiden uit {', '.join(unknown[:5])};"
              f" behandeld als noop. Hernoem het bestand om dit te sturen.\n")

    out = {"domain": a.domain or "", "modes": {k: [f.name for f in v] for k, v in caps.items()},
           "results": []}

    for eid, (rule, need, title) in ENTRIES.items():
        missing = [m for m in need if m not in caps]
        if missing:
            out["results"].append({"entry": eid, "title": title, "verdict": "not-assessed",
                                   "reason": f"opname ontbreekt voor mode: {', '.join(missing)}"})
            continue

        if rule == "hollowno":
            # Verzamelingsvergelijking. De regel zelf is de vergelijking, niet
            # een waarneming in een van beide opnames.
            hn, _ = hosts(caps["noop"][0])
            hr, root = hosts(caps["reject"][0])
            survivors = sorted(h for h in hr if any(h.endswith(k) for k in replay.KNOWN))
            hit = bool(survivors) or hr >= hn
            out["results"].append({
                "entry": eid, "title": title, "verdict": "present" if hit else "not-found",
                "method": "differential", "qod": 97,
                "detail": {"hosts_noop": len(hn), "hosts_reject": len(hr), "survivors": survivors}})
            continue

        har = json.loads(caps["noop"][0].read_text(encoding="utf-8"))
        entries, root, doc = replay.parse(har)
        hit, stats = replay.RULES[rule](entries, root, doc)
        out["results"].append({"entry": eid, "title": title,
                               "verdict": "present" if hit else "not-found",
                               "method": {"frontrun": "network-with-identifier",
                                          "maxstay": "network-with-identifier",
                                          "hotlink": "network-observed",
                                          "sideload": "differential"}[rule],
                               "qod": {"frontrun": 95, "maxstay": 95, "hotlink": 90, "sideload": 97}[rule],
                               "detail": stats})

    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(f"opnames: " + ", ".join(f"{k} ({len(v)})" for k, v in sorted(caps.items())))
    print(f"{'entry':16s} {'verdict':12s} {'qod':>4s}  detail")
    print("-" * 78)
    for r in out["results"]:
        if r["verdict"] == "not-assessed":
            print(f"{r['entry']:16s} {'niet getoetst':12s} {'':>4s}  {r['reason']}")
        else:
            d = r.get("detail", {})
            print(f"{r['entry']:16s} {r['verdict']:12s} {r.get('qod',''):>4}  "
                  f"{json.dumps(d, ensure_ascii=False)[:60]}")
    print(f"""
Wat hier staat is de uitkomst van een regel op een opname, niet een oordeel.
Of de bevinding standhoudt hangt ook af van de condities waaronder is gemeten:
schoon profiel, geen interactie, en het land van waaruit. Die staan niet in het
bestand en moet je er zelf bij vermelden. Zie de falsifiers per entry.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
