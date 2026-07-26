"""Gedeelde logica van het register.

Eén bron voor de severity-regel en het ontleden van de vector. Als dit op twee
plekken zou staan, gaan ze uit elkaar lopen en dan betekent een ernstlabel uit
2026 iets anders dan hetzelfde label uit 2027. Alles importeert hier.
"""
import hashlib, json, pathlib, re

SEVERITY_RULE = "dpe-severity-1.0"
VECTOR_RE = re.compile(
    r"^DPE:1\.0/EV:[MRTS]/CS:(PRE|REJ|ACC|NA|X)/DC:(ID|BEH|LOC|CNT|SPC|IDD)"
    r"(\+(ID|BEH|LOC|CNT|SPC|IDD))*/RC:(1P|PR|3P|UND)/JU:(EU|ADQ|3C|HR|X)/SC:(ONE|SEC|NAT|VND)$")

QOD = {"static-source": 60, "network-observed": 90, "network-with-identifier": 95,
       "document-comparison": 97, "differential": 97, "third-party-confirmed": 99,
       "archival-continuous": 99}


def axes(vector):
    return dict(p.split(":", 1) for p in vector.split("/")[1:])


def severity(vector):
    """Afgeleid uit de vector, nooit met de hand gezet. Zie schema/dpe-vector-1.0.md."""
    ax = axes(vector)
    dc = set(ax["DC"].split("+"))
    if ax["EV"] != "M":
        return "unrated"
    sensitive = bool({"SPC", "IDD"} & dc)
    unconsented = ax["CS"] in ("PRE", "REJ")
    external = ax["RC"] in ("3P", "UND")
    third_country = ax["JU"] in ("3C", "HR")
    if sensitive and unconsented and external:
        return "critical"
    if (unconsented and external) or (sensitive and third_country):
        return "high"
    if unconsented or third_country:
        return "medium"
    return "low"


def methodology_hash(root):
    """Hash over schema, vectordefinitie en rules.

    Verandert de meetmethodiek, dan verandert deze hash. Records die naar een
    oudere hash verwijzen blijven daardoor leesbaar als metingen onder de toen
    geldende methodiek, in plaats van stilzwijgend te verschuiven.
    """
    h = hashlib.sha256()
    for p in sorted(list((root / "schema").glob("*")) + list((root / "rules").glob("*.yaml"))):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def load_records(root):
    out = []
    for f in sorted((root / "observations").glob("DPE-*.json")):
        out.append((f, json.loads(f.read_text(encoding="utf-8"))))
    return out


def next_id(root, year):
    """Eerstvolgende vrije nummer. Nummers worden nooit hergebruikt, ook niet na
    intrekking, dus we tellen door op het hoogste bestaande nummer."""
    used = [int(f.stem.split("-")[2]) for f in (root / "observations").glob(f"DPE-{year}-*.json")]
    return f"DPE-{year}-{max(used, default=0) + 1:04d}"
