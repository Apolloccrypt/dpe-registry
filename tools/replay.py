#!/usr/bin/env python3
"""Draait een detectieregel opnieuw op een meegeleverde HAR.

Dit is wat CVE niet kan. Een CVE-beschrijving is proza; een HAR is data. Dus als
iemand een record inzendt met het ruwe bewijs erbij, kan de CI narekenen of de
regel op dat bewijs echt oplevert wat het record beweert.

    python3 tools/replay.py bewijs.har [--rule frontrun] [--expect hit]

Let op: dezelfde regels staan ook in site/verify.html, in JavaScript, zodat een
lezer ze in de browser kan draaien zonder iets te installeren. Twee
implementaties van dezelfde logica is een risico; daarom staan hier alleen de
kale indicatoren en toetst tests/test_replay.py beide op hetzelfde bestand.
"""
import argparse, json, pathlib, re, sys
from urllib.parse import urlparse

TWO = {"co.uk", "org.uk", "ac.uk", "com.au", "co.jp", "com.br", "co.nz"}
KNOWN = {
    "google-analytics.com": "Google Analytics", "analytics.google.com": "Google Analytics",
    "googletagmanager.com": "Google Tag Manager", "doubleclick.net": "Google Ads",
    "googlesyndication.com": "Google Ads", "googleadservices.com": "Google Ads",
    "hotjar.com": "Hotjar", "hotjar.io": "Hotjar", "clarity.ms": "Microsoft Clarity",
    "facebook.net": "Meta Pixel", "facebook.com": "Meta", "licdn.com": "LinkedIn",
    "ajax.googleapis.com": "Google Hosted Libraries", "gstatic.com": "Google",
    "fonts.googleapis.com": "Google Fonts",
}
ID_RE = re.compile(r"(?:^|[?&])(cid|tid|_ga|uid|sid|dl|en|gtm|fbp|hjid)=", re.I)
TAG_RE = re.compile(r"\b(G-[A-Z0-9]{6,}|UA-\d{4,}-\d+|GTM-[A-Z0-9]{4,})\b")


def registrable(host):
    p = host.split(".")
    if len(p) < 3:
        return host
    return ".".join(p[-3:]) if ".".join(p[-2:]) in TWO else ".".join(p[-2:])


def parse(har):
    entries, doc, root = [], "", ""
    for en in har["log"]["entries"]:
        try:
            host = urlparse(en["request"]["url"]).hostname or ""
        except Exception:
            continue
        host = host.removeprefix("www.")
        content = en.get("response", {}).get("content", {}) or {}
        mime = content.get("mimeType", "") or ""
        vendor = next((v for k, v in KNOWN.items() if host.endswith(k)), None)
        cookies = []
        for h in en.get("response", {}).get("headers", []) or []:
            if h["name"].lower() == "set-cookie":
                m = re.search(r"max-age=(\d+)", h["value"], re.I)
                cookies.append({"name": h["value"].split("=")[0].strip(),
                                "days": round(int(m.group(1)) / 86400) if m else None})
        if not root and "text/html" in mime:
            root, doc = registrable(host), content.get("text", "") or ""
        entries.append({"host": host, "url": en["request"]["url"], "mime": mime,
                        "vendor": vendor, "id": bool(ID_RE.search(en["request"]["url"])),
                        "cookies": cookies})
    if not root and entries:
        root = registrable(entries[0]["host"])
    return entries, root, doc


def rule_frontrun(entries, root, doc):
    third = [e for e in entries if registrable(e["host"]) != root]
    meas = [e for e in third if e["vendor"] or e["id"]]
    return bool(meas), {"third_party": len(third), "measurement": len(meas),
                        "with_identifier": sum(1 for e in third if e["id"])}


def rule_maxstay(entries, root, doc):
    long = [(e["host"], c["name"], c["days"]) for e in entries for c in e["cookies"]
            if c["days"] and c["days"] >= 390]
    return bool(long), {"cookies_over_390d": len(long),
                        "names": [c[1] for c in long][:8]}


def rule_hotlink(entries, root, doc):
    ext = [e for e in entries if registrable(e["host"]) != root
           and re.search(r"script|css|font|image", e["mime"] or "", re.I)]
    return bool(ext), {"external_subresources": len(ext),
                       "hosts": sorted({e["host"] for e in ext})[:8]}


def rule_sideload(entries, root, doc):
    ids = {m for e in entries for m in TAG_RE.findall(e["url"])}
    missing = sorted(i for i in ids if doc and i not in doc)
    return bool(missing), {"ids_found": len(ids), "not_in_html": missing}


RULES = {"frontrun": rule_frontrun, "maxstay": rule_maxstay,
         "hotlink": rule_hotlink, "sideload": rule_sideload}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("har", nargs="+")
    ap.add_argument("--rule", choices=sorted(RULES), help="standaard: alle regels")
    ap.add_argument("--expect", choices=["hit", "miss"],
                    help="exitcode 1 als de uitkomst hier niet mee overeenkomt")
    a = ap.parse_args()

    failed = False
    for path in a.har:
        har = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        entries, root, doc = parse(har)
        print(f"\n{path}  ·  doeldomein {root}  ·  {len(entries)} verzoeken")
        for name in ([a.rule] if a.rule else sorted(RULES)):
            hit, stats = RULES[name](entries, root, doc)
            print(f"  {name:10s} {'AANGETROFFEN' if hit else 'niet aangetroffen':20s} {stats}")
            if a.expect and a.rule == name and hit != (a.expect == "hit"):
                print(f"  ! verwacht was '{a.expect}'")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
