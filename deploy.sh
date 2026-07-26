#!/usr/bin/env bash
# Bouwt de catalogus en zet hem klaar voor totaledigitalewaarborging.nl.
#
# Bewust pull in plaats van push: dit script draait op de machine die al
# deployrechten heeft, zodat er geen sleutel bij een externe dienst hoeft te
# liggen. Draai het daar, niet vanaf een willekeurige werkplek.
set -euo pipefail
cd "$(dirname "$0")"

DEST="${1:-}"
[ -z "$DEST" ] && { echo "gebruik: ./deploy.sh <doelpad of host:pad>"; exit 2; }

echo "== catalogus genereren"
python3 build_catalogue.py

echo "== valideren"
if python3 -c "import jsonschema" 2>/dev/null; then
  python3 - <<'PY'
import json, glob, jsonschema, sys
v = jsonschema.Draft202012Validator(json.load(open("schema/dpe-entry-2.0.schema.json")))
bad = [f for f in glob.glob("catalogue/*.json") if list(v.iter_errors(json.load(open(f))))]
if bad:
    print("ONGELDIG:", ", ".join(bad)); sys.exit(1)
print(f"{len(glob.glob('catalogue/*.json'))} entries geldig")
PY
else
  echo "jsonschema niet aanwezig; validatie overgeslagen. Niet publiceren zonder."
  exit 1
fi

echo "== pagina's bouwen"
python3 build_pages.py
# De voorpagina (vragen + lijst) komt hiervandaan, niet uit build_pages.
python3 tools/build_triage.py
python3 tools/build_readme_list.py

echo "== overzetten naar $DEST"
# geen --delete: het register hangt onder een pad van een grotere site
rsync -av --exclude ".DS_Store" site/register/ "$DEST"

echo
echo "klaar. Controleer daarna minstens:"
echo "  - /register/               opent en toont alle entries"
echo "  - /register/DPE-2026-0001  opent rechtstreeks, ook zonder JavaScript"
echo "  - /register/all.json       is geldige JSON"
echo "  - /register/sitemap.xml    staat in robots.txt of is los ingediend"
