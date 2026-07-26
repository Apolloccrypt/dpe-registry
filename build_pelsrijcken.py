#!/usr/bin/env python3
"""
Genereert de eerste DPE-records uit het Pels Rijcken-dossier.

Bron: addendum-tijdlijn-tracking-pelsrijcken.html (metingen 18, 21 en 27 mei 2026,
Wayback-tijdlijn, publieke verklaring Pels Rijcken 22 mei 2026).

Discipline: elk veld hieronder is terug te voeren op dat addendum. Waar het
addendum iets niet vaststelt, staat het veld er niet. Er wordt niets aangevuld.
"""
import json, pathlib, re

OUT = pathlib.Path(__file__).parent / "observations"
ADDENDUM = "https://mickbeer.com/n/addendum-tijdlijn-tracking-pelsrijcken"

# ---------------------------------------------------------------- severity 1.0

def severity(vector):
    ax = dict(p.split(":", 1) for p in vector.split("/")[1:])
    ev, cs, rc, ju = ax["EV"], ax["CS"], ax["RC"], ax["JU"]
    dc = ax["DC"].split("+")
    if ev != "M":
        return "unrated"
    sensitive = bool({"SPC", "IDD"} & set(dc))
    unconsented = cs in ("PRE", "REJ")
    external = rc in ("3P", "UND")
    if sensitive and unconsented and external:
        return "critical"
    if (unconsented and external) or (sensitive and ju in ("3C", "HR")):
        return "high"
    if unconsented or ju in ("3C", "HR"):
        return "medium"
    return "low"

# ---------------------------------------------------------------- shared parts

FIRM = "Pels Rijcken & Droogleever Fortuijn N.V."

def wp_target(domain, sector="juridische dienstverlening"):
    return {"kind": "website", "name": domain, "domain": domain,
            "operator": FIRM, "sector": sector}

def repro(tier_script_path, expect, manual_path="repro/MANUAL.md"):
    """Reproductie zonder de eigen scanner. Commit wordt bij commit gevuld."""
    return {
        "methods": [
            {"tier": "manual", "label": "Browser devtools, met de hand",
             "repo": "https://github.com/Apolloccrypt/dpe-registry",
             "path": manual_path,
             "expect": expect},
            {"tier": "script", "label": "Standalone Playwright, geen registertooling",
             "repo": "https://github.com/Apolloccrypt/dpe-registry",
             "path": tier_script_path, "language": "javascript",
             "command": "npm i playwright && node " + tier_script_path.split("/")[-1],
             "runner": {"service": "github-codespaces",
                        "url": "https://codespaces.new/Apolloccrypt/dpe-registry",
                        "exit_country": "NL",
                        "caveat": "Kies een EU-regio. Een US-egress kan een andere consent-flow krijgen, waardoor CS:PRE niet reproduceert."},
             "environment": {"browser": "chromium", "exit_country": "NL",
                             "headless": True, "profile": "clean"},
             "expect": expect},
        ],
        # Nog leeg: hier komen echte permanente URL's van derden. Niet invullen
        # zonder de scan daadwerkelijk te hebben laten lopen.
        "independent_confirmation": [],
    }

# Wederhoor liep op dossierniveau, niet per bevinding: Pels Rijcken heeft op
# 22 mei 2026 publiek gereageerd op het onderzoek. Elk record erft dat spoor.
# De exacte notificatiedatum per bevinding volgt niet uit het addendum en is
# daarom niet opgenomen; zie OPEN.md.
PR_STATEMENT = ("Publieke verklaring 22 mei 2026: het ging om enkele slordigheden met "
                "YouTube-embeds, opgelost door de Cookiebot-scanfrequentie van maandelijks "
                "naar dagelijks te verhogen, en Hotjar voldoet aan de AVG omdat de servers "
                "in de EU staan. Twee bevindingen zijn erkend en verwijderd.")

def disc(response, extra=None):
    d = {"channel": "onderzoekspublicatie; partij heeft publiek gereageerd",
         "response": response, "response_on": "2026-05-22",
         "response_text": PR_STATEMENT if extra is None else PR_STATEMENT + " " + extra}
    return d

def changes(created, entries_extra=None):
    base = [{"at": created + "T00:00:00Z", "actor": "import/pelsrijcken",
             "entries": ["Record created from published addendum.",
                         "Pattern linked.", "Vector created.",
                         "Sources created.", "Falsifier imported.",
                         "Severity derived (dpe-severity-1.0)."]}]
    if entries_extra:
        base.append(entries_extra)
    return base

# GA4/UA pre-consent op de WP Engine-omgeving: identieke falsifiers.
FALS_PRECONSENT = {
    "attribution": "har-pageref",
    "conditions": [
        {"condition": "de meethost is een first-party CNAME naar het doeldomein",
         "tested": True, "outcome": "excluded",
         "evidence": "requests gaan naar google-analytics.com respectievelijk region1.google-analytics.com"},
        {"condition": "het request draagt geen identifier en zet geen cookie",
         "tested": True, "outcome": "excluded",
         "evidence": "_ga-cookie gezet bij paginalaad, POST naar measurement-endpoint in HAR"},
        {"condition": "toestemming was in een eerdere sessie op hetzelfde profiel gegeven",
         "tested": True, "outcome": "excluded",
         "evidence": "meting in drie afzonderlijke modi met schoon profiel per mode"},
    ],
}

# ---------------------------------------------------------------- de records

R = []

# Detectiemethode per patroon. De QoD beschrijft de methode, niet de ernst.
# 'basis' zegt waar de bevinding op rust: een eigenschap van het verkeer weegt
# zwaarder dan een lijst van ons, en de eigen documenten van de partij wegen
# het zwaarst.
DETECTION = {
    "frontrun":     ("network-with-identifier", 95, "traffic-property",
                     "GA-request met identifier-parameter en gezette _ga-cookie, voor het consent-event"),
    "hollowno":     ("differential", 97, "set-comparison",
                     "verzameling third-party hosts in mode reject vergeleken met mode noop"),
    "maxstay":      ("network-with-identifier", 95, "traffic-property",
                     "Set-Cookie met een bewaartermijn van 399 dagen voor het consent-event"),
    "overshoulder": ("network-with-identifier", 95, "traffic-property",
                     "request naar het session-recording-endpoint van de vendor, site-id 4942343"),
    "offbooks":     ("document-comparison", 97, "own-documents",
                     "gemeten ontvangers vergeleken met de ontvangers genoemd in de eigen privacyverklaring van dezelfde datum"),
    "sideload":     ("differential", 97, "set-comparison",
                     "property-ID aanwezig in het netwerkverkeer en ontbrekend in de opgehaalde HTML"),
    "hotlink":      ("network-observed", 90, "traffic-property",
                     "subresource-request naar een andere registrable domain in het initiele document"),
    "silhouette":   ("network-observed", 90, "traffic-property",
                     "uitlezen van navigator-eigenschappen en tijdzone in scripts van derden"),
    "handover":     ("network-with-identifier", 95, "traffic-property",
                     "Set-Cookie op een host onder een andere registrable domain dan de gastheer"),
}

CREDIT = [{"name": "Mick Beer", "role": "measured", "date": "2026-05-27"}]

def rec(**kw):
    kw["schema_version"] = "1.0"
    kw.setdefault("credit", CREDIT)
    kw.setdefault("tlp", "CLEAR")
    if kw["pattern"] in DETECTION and "detection" not in kw:
        m, q, b, ind = DETECTION[kw["pattern"]]
        d = {"rule": kw["pattern"], "rule_version": 1, "method": m, "qod": q,
             "basis": b, "indicator": ind}
        # Archiefcontinuiteit verhoogt de zekerheid over de duur, niet over het
        # huidige gedrag. Daarom wel vastgelegd, niet als hogere QoD verkocht.
        if "continuity" in kw:
            d["indicator"] += (f"; duur onafhankelijk bevestigd via {kw['continuity']['source']}"
                               f" op marker {kw['continuity'].get('marker', 'n.v.t.')}")
        # n van m: elk record uit dit dossier rust op de metingen van 18, 21 en
        # 27 mei. Waar maar een van die drie het patroon raakt, staat dat hier.
        d["samples"] = kw.pop("_samples", {"taken": 1, "positive": 1,
                                           "dates": [kw["last_seen"]],
                                           "vantage_points": ["NL"]})
        kw["detection"] = d
    # Het wederhoorspoor is dossierbreed en geldt dus voor elk record uit dit
    # dossier. Records die iets specifiekers te melden hebben, geven hun eigen
    # disclosure mee. Publiceren zonder spoor blokkeert het schema.
    if kw.get("status") in ("published", "resolved", "disputed", "corrected"):
        kw.setdefault("disclosure", disc("contested"))
    kw["severity"] = {"label": severity(kw["vector"]), "rule": "dpe-severity-1.0"}
    R.append(kw)

# --- pgwoo.nl -------------------------------------------------------------

rec(id="DPE-2026-0001", pattern="frontrun", target=wp_target("pgwoo.nl", "Wet open overheid"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    destinations=[{"country": "US", "host": "google-analytics.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "GA4-stream G-M0EYEXG6PF vuurt bij paginalaad, voordat de bezoeker de cookie-notice heeft kunnen beantwoorden. POST naar het Google measurement-endpoint bevestigd in de HAR. Cookie _ga gezet.",
              "artefact": ADDENDUM},
             {"source": "archival-corroboration", "date": "2026-05-27",
              "description": "Dezelfde stream-ID staat sinds oktober 2022 onafgebroken in de gearchiveerde broncode. Wat in de Wayback-broncode staat, vuurt vandaag daadwerkelijk.",
              "artefact": ADDENDUM}],
    continuity={"source": "wayback", "continuous_since": "2022-10", "duration_months": 41,
                "marker": "G-M0EYEXG6PF",
                "note": "Geen Cookiebot of vergelijkbare consent-vendor zichtbaar in de gearchiveerde broncode."},
    reproduction=repro("repro/frontrun/frontrun.mjs",
                       "minstens een request naar een Google-meethost voordat er met de banner is geinterageerd, plus een gezette _ga-cookie"),
    falsifier=FALS_PRECONSENT,
    products=[{"vendor": "Google", "product": "Analytics 4", "state": "known_affected",
               "configuration": "hardgecodeerd in de pagina, buiten enige consent-gate"},
              {"vendor": "WP Engine", "product": "WordPress hosting", "state": "known_affected",
               "configuration": "gedeeld IP 35.189.124.151, toebehorend aan Google LLC"}],
    legal_context={"provisions": [{"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 6(1)(a)"}]},
    disclosure=disc("contested", "Op pgwoo.nl zijn op het moment van publicatie geen sporen van een opruimactie aangetroffen."),
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0002", pattern="hollowno", target=wp_target("pgwoo.nl", "Wet open overheid"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Een cookie-notice-banner is aanwezig sinds 2022, maar is niet gekoppeld aan de tracking. De GA4-tag is hardgecodeerd en laadt los van de banner, dus de keuze van de bezoeker verandert het netwerkverkeer niet. Een weigeroptie wordt niet aangeboden.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/hollowno/hollowno.mjs",
                       "identieke verzameling third-party requests in de modi geen-actie en weigeren"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de banner blokkeert wel, maar pas na een vertraging die de meting mist",
         "tested": True, "outcome": "excluded",
         "evidence": "de tag is hardgecodeerd in de broncode, niet via een consent-gate ingeladen"},
        {"condition": "er is een weigeroptie op een tweede laag van de banner",
         "tested": True, "outcome": "excluded", "evidence": "meting van de bannerinterface, 27 mei 2026"}]},
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 7(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 4(11)"}]},
    disclosure=disc("contested", "Op pgawb.nl zijn op het moment van publicatie geen sporen van een opruimactie aangetroffen."),
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0003", pattern="maxstay", target=wp_target("pgwoo.nl", "Wet open overheid"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID/RC:3P/JU:3C/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Cookie-bewaartermijn van 399 dagen per bezoeker, gezet voordat er een toestemmingsinteractie heeft plaatsgevonden. 399 dagen is de maximale termijn die Chrome voor een cookie accepteert.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/maxstay/maxstay.mjs",
                       "cookie _ga met een expiry van circa 399 dagen, gezet voor enige interactie"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de cookie is strikt noodzakelijk voor een door de bezoeker gevraagde dienst",
         "tested": True, "outcome": "excluded",
         "evidence": "_ga is een analytics-identifier, geen functionele cookie"}]},
    legal_context={"provisions": [{"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 5(1)(e)"}]},
    changes=changes("2026-05-27"))

# --- pgawb.nl -------------------------------------------------------------

rec(id="DPE-2026-0004", pattern="frontrun", target=wp_target("pgawb.nl"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    destinations=[{"country": "US", "host": "google-analytics.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "GA4-stream G-RTMT1BGGHG vuurt bij paginalaad voor enige toestemmingsinteractie, met gezette _ga-cookie en POST naar het measurement-endpoint.",
              "artefact": ADDENDUM},
             {"source": "archival-corroboration", "date": "2026-05-27",
              "description": "Universal Analytics UA-18970241-6 staat onafgebroken in de archieven van december 2013 tot september 2024, opgevolgd door deze GA4-stream vanaf januari 2025.",
              "artefact": ADDENDUM}],
    continuity={"source": "wayback", "continuous_since": "2013-12", "continuous_until": "2024-09",
                "duration_months": 129, "marker": "UA-18970241-6",
                "note": "Onafgebroken UA-periode van 10 jaar en 9 maanden, met aansluitend GA4 vanaf januari 2025."},
    reproduction=repro("repro/frontrun/frontrun.mjs",
                       "minstens een request naar een Google-meethost voor interactie, plus een gezette _ga-cookie"),
    falsifier=FALS_PRECONSENT,
    products=[{"vendor": "Google", "product": "Analytics 4", "state": "known_affected",
               "configuration": "hardgecodeerd, buiten enige consent-gate"},
              {"vendor": "WP Engine", "product": "WordPress hosting", "state": "known_affected",
               "configuration": "gedeeld IP 35.189.124.151, toebehorend aan Google LLC"}],
    legal_context={"provisions": [{"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 6(1)(a)"}]},
    disclosure=disc("contested", "Op pgawb.nl zijn op het moment van publicatie geen sporen van een opruimactie aangetroffen."),
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0005", pattern="hollowno", target=wp_target("pgawb.nl"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Cookie-notice aanwezig sinds 2017, niet gekoppeld aan de tracking. De GA4-tag laadt los van de banner en er wordt geen weigeroptie aangeboden.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/hollowno/hollowno.mjs",
                       "identieke verzameling third-party requests in de modi geen-actie en weigeren"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de banner blokkeert na een vertraging die de meting mist",
         "tested": True, "outcome": "excluded", "evidence": "tag is hardgecodeerd in de broncode"}]},
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 7(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 4(11)"}]},
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0006", pattern="maxstay", target=wp_target("pgawb.nl"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID/RC:3P/JU:3C/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Cookie-bewaartermijn van 399 dagen per bezoeker, gezet voor enige toestemmingsinteractie.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/maxstay/maxstay.mjs", "cookie _ga met expiry van circa 399 dagen voor interactie"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de cookie is strikt noodzakelijk voor een gevraagde dienst",
         "tested": True, "outcome": "excluded", "evidence": "_ga is een analytics-identifier"}]},
    legal_context={"provisions": [{"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}]},
    changes=changes("2026-05-27"))

# --- cassatieblog.nl ------------------------------------------------------

rec(id="DPE-2026-0007", pattern="frontrun", target=wp_target("cassatieblog.nl"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    destinations=[{"country": "US", "host": "googletagmanager.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "In de modus zonder interactie laadt Google Tag Manager al voordat toestemming is gegeven. Cookiebot is op dit domein wel aanwezig en voorkomt cookie-plaatsing voor toestemming, maar voorkomt het laden van GTM niet.",
              "artefact": ADDENDUM},
             {"source": "archival-corroboration", "date": "2026-05-27",
              "description": "Universal Analytics UA-18970241-9 onafgebroken aanwezig in 76 opeenvolgende snapshots van mei 2014 tot maart 2026. Eerdere, niet-aansluitende sporen uit oktober 2011 tot januari 2012.",
              "artefact": ADDENDUM}],
    continuity={"source": "wayback", "continuous_since": "2014-05", "continuous_until": "2026-03",
                "duration_months": 142, "snapshots_consecutive": 76, "marker": "UA-18970241-9",
                "earlier_traces": "Google Analytics-sporen van oktober 2011 tot januari 2012, met een gat in 2013. Buiten de aangehouden onafgebroken duur gelaten.",
                "note": "11 jaar en 10 maanden strikt onafgebroken. 76 snapshots is een ondergrens, niet een schatting."},
    reproduction=repro("repro/frontrun/frontrun.mjs",
                       "een request naar googletagmanager.com voordat er met de Cookiebot-dialoog is geinterageerd"),
    falsifier=FALS_PRECONSENT,
    products=[{"vendor": "Google", "product": "Tag Manager", "state": "known_affected",
               "configuration": "laadt buiten de Cookiebot-gate om"},
              {"vendor": "Usercentrics", "product": "Cookiebot", "state": "known_affected",
               "configuration": "voorkomt cookie-plaatsing voor toestemming, maar niet het laden van GTM"}],
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 6(1)(a)"}, {"jurisdiction": "EU", "reference": "GDPR art. 7"}]},
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0008", pattern="hollowno", target=wp_target("cassatieblog.nl"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:REJ/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Na het klikken op weigeren blijven vijf trackers en een script actief. De aanwezige Cookiebot-implementatie honoreert de weigering dus onvolledig. Dit is het enige van de gemeten domeinen waar Cookiebot aanwezig is, en juist daar is de werking aantoonbaar incompleet.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/hollowno/hollowno.mjs",
                       "na een expliciete weigering blijven third-party requests uitgaan naar meethosts"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de resterende trackers zijn strikt noodzakelijk en vallen buiten de toestemmingsplicht",
         "tested": False, "outcome": "untested",
         "evidence": "per resterende tracker nog te bepalen; dit deel van het record is niet verder dan de meting"},
        {"condition": "de weigering was niet geregistreerd door een fout in de meetopzet",
         "tested": True, "outcome": "excluded",
         "evidence": "consent-status na de klik uitgelezen, weigering was geregistreerd"}]},
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 7(3)"}]},
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0009", pattern="silhouette", target=wp_target("cassatieblog.nl"),
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID/RC:3P/JU:3C/SC:SEC",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Fingerprinting via navigator-eigenschappen en tijdzone aangetroffen in twee gedownloade scripts. Op pgwoo.nl en pgawb.nl is fingerprinting via tijdzone eveneens aangetroffen.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/silhouette/silhouette.mjs",
                       "aanroepen van navigator- en tijdzone-eigenschappen in scripts van derden, voor toestemming"),
    falsifier={"attribution": "cdp-initiator", "conditions": [
        {"condition": "de uitlezing gebeurt door een script van de site zelf, niet van een derde",
         "tested": True, "outcome": "excluded",
         "evidence": "beide scripts worden geladen van een andere registrable domain dan het doeldomein"},
        {"condition": "de eigenschappen worden uitgelezen voor een functioneel doel, zoals lokalisatie",
         "tested": False, "outcome": "untested",
         "evidence": "doelbinding per script niet vastgesteld; het record stelt de uitlezing vast, niet het doel"}]},
    legal_context={"provisions": [{"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 6"}]},
    changes=changes("2026-05-27"))

# --- pelsrijcken.nl ------------------------------------------------------

rec(id="DPE-2026-0010", pattern="overshoulder",
    target={"kind": "website", "name": "pelsrijcken.nl", "domain": "pelsrijcken.nl",
            "operator": FIRM, "sector": "juridische dienstverlening"},
    status="resolved", first_seen="2026-05-18", last_seen="2026-05-21",
    vector="DPE:1.0/EV:M/CS:PRE/DC:BEH/RC:3P/JU:EU/SC:ONE",
    destinations=[{"country": "MT", "host": "hotjar.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-18",
              "description": "Hotjar session recording, site-id 4942343, actief vanaf april 2024 en vurend voordat toestemming was gegeven. Session recording legt het gedrag binnen de pagina vast, niet alleen de paginaweergave.",
              "artefact": ADDENDUM},
             {"source": "vendor-statement", "date": "2026-05-22",
              "description": "Pels Rijcken stelt publiekelijk dat Hotjar aan de AVG voldoet omdat de servers in de EU staan.",
              "artefact": ADDENDUM},
             {"source": "registry-note", "date": "2026-05-27",
              "description": "De serverlocatie is in dit record niet in geschil: de jurisdictie-as staat op EU. Het verwijt is dat de opname plaatsvond voordat toestemming was gegeven. Waar de servers staan verandert dat niet.",
              "artefact": ADDENDUM},
             {"source": "recheck", "date": "2026-05-21",
              "description": "Hotjar is tussen 18 en 21 mei van de homepage verwijderd. Drie dagen na een extern signaal, na ruim twee jaar aanwezigheid.",
              "artefact": ADDENDUM}],
    rechecks=[{"date": "2026-05-21", "outcome": "resolved",
               "note": "Verwijderd van de homepage. Valt buiten de Wayback-data: de laatste capture van 9 maart 2026 ligt voor de opruimactie. Vastgelegd via OTS-gestempelde rescans."}],
    continuity={"source": "wayback", "continuous_since": "2024-04", "duration_months": 25,
                "marker": "Hotjar site 4942343",
                "note": "Uitsluitend op pelsrijcken.nl aangetroffen. Op werkenbijpelsrijcken.nl in 0 van 121 snapshots. Wie Hotjar op werkenbij verdedigt, weerlegt een bevinding die nooit is gedaan."},
    reproduction=repro("repro/overshoulder/overshoulder.mjs",
                       "een request naar een session-recording-vendor voor toestemming; op dit domein sinds 21 mei 2026 niet meer reproduceerbaar"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de opname startte pas na toestemming",
         "tested": True, "outcome": "excluded", "evidence": "meting in de modus zonder interactie"},
        {"condition": "de vendor verwerkt uitsluitend geaggregeerd, zonder sessie-opname",
         "tested": True, "outcome": "excluded", "evidence": "session recording is de gemeten functionaliteit"}]},
    products=[{"vendor": "Hotjar", "product": "Session recording", "state": "fixed"}],
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 6(1)(a)"}, {"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}]},
    disclosure=disc("acknowledged", "Deze bevinding is erkend en tussen 18 en 21 mei van de homepage verwijderd."),
    changes=changes("2026-05-18", {"at": "2026-05-21T00:00:00Z", "actor": "recheck",
                                   "entries": ["Source created (recheck).", "Recheck created (resolved).",
                                               "Status -> resolved.", "Product state -> fixed."]}))

rec(id="DPE-2026-0011", pattern="offbooks",
    target={"kind": "website", "name": "pelsrijcken.nl", "domain": "pelsrijcken.nl", "operator": FIRM},
    status="published", first_seen="2026-05-18", last_seen="2026-05-18",
    vector="DPE:1.0/EV:M/CS:PRE/DC:BEH/RC:3P/JU:EU/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-18",
              "description": "Hotjar session recording was bijna twee jaar actief zonder in de privacyverklaring te worden genoemd. De privacyverklaring stelde daarnaast dat er geen persoonsgegevens via de website werden verwerkt en dat ontvangers zich binnen de EER bevonden. Beide stellingen waren onjuist op het moment dat ze op de website stonden.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/offbooks/offbooks.md",
                       "vergelijking van de gemeten ontvangers met de lijst in de privacyverklaring van dezelfde datum, beide via Wayback",
                       manual_path="repro/offbooks/offbooks.md"),
    falsifier={"attribution": "vendor-statement", "conditions": [
        {"condition": "de vendor werd elders in de verklaring of in een cookieoverzicht wel genoemd",
         "tested": True, "outcome": "excluded",
         "evidence": "gearchiveerde versies van de privacyverklaring doorzocht op de vendor"},
        {"condition": "de verklaring was buiten de gemeten periode wel bijgewerkt",
         "tested": True, "outcome": "excluded", "evidence": "Wayback-versies van de verklaring per datum vergeleken"}]},
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 13(1)(e)"}, {"jurisdiction": "EU", "reference": "GDPR art. 5(1)(a)"}]},
    changes=changes("2026-05-18"))

rec(id="DPE-2026-0012", pattern="sideload",
    target={"kind": "website", "name": "pelsrijcken.nl", "domain": "pelsrijcken.nl", "operator": FIRM},
    status="published", first_seen="2026-05-18", last_seen="2026-05-18",
    vector="DPE:1.0/EV:M/CS:PRE/DC:ID+BEH/RC:3P/JU:3C/SC:ONE",
    destinations=[{"country": "US", "host": "googletagmanager.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-18",
              "description": "GA4 en Google Ads worden in de HAR aangetroffen terwijl beide ID's nergens in de broncode van de pagina staan. De GTM-container PMFWLS7 laadt ze in. De afwezigheid van een tracker-ID in de broncode is dus geen bewijs dat de tracking is gestopt; de container is de robuuste indicator.",
              "artefact": ADDENDUM}],
    continuity={"source": "wayback", "continuous_since": "2022-12", "marker": "GTM-PMFWLS7",
                "note": "GA4-property G-T7N46JF3XT verdwijnt na november 2023 uit de broncode terwijl de container onafgebroken aanwezig blijft en de property blijft vuren."},
    reproduction=repro("repro/sideload/sideload.mjs",
                       "een meethost of property-ID in het netwerkverkeer die niet in de opgehaalde HTML voorkomt"),
    falsifier={"attribution": "cdp-initiator", "conditions": [
        {"condition": "het ID staat wel in de broncode, maar dynamisch samengesteld",
         "tested": True, "outcome": "excluded",
         "evidence": "opgehaalde HTML doorzocht op het volledige en op gesplitste ID"},
        {"condition": "de initiator is niet de container maar een ander script",
         "tested": True, "outcome": "excluded", "evidence": "initiator-keten uit de HAR"}]},
    products=[{"vendor": "Google", "product": "Tag Manager", "state": "fixed",
               "configuration": "container GTM-PMFWLS7, verwijderd tussen 18 en 21 mei 2026"}],
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 5(2)"}, {"jurisdiction": "EU", "reference": "GDPR art. 24"}]},
    changes=changes("2026-05-18"))

# --- werkenbijpelsrijcken.nl ---------------------------------------------

rec(id="DPE-2026-0013", pattern="hotlink",
    target={"kind": "website", "name": "werkenbijpelsrijcken.nl", "domain": "werkenbijpelsrijcken.nl",
            "operator": FIRM, "sector": "arbeidsmarktcommunicatie"},
    status="published", first_seen="2026-05-18", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:NA/DC:ID/RC:3P/JU:3C/SC:ONE",
    destinations=[{"country": "US", "host": "ajax.googleapis.com", "method": "vendor-statement"},
                  {"country": "US", "host": "fonts.gstatic.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "De pagina laadt jQuery rechtstreeks van ajax.googleapis.com en gebruikt Google Fonts. Bij elke paginaweergave gaat het IP-adres van de bezoeker naar Google in de Verenigde Staten. Dit vereist geen toestemmingsinteractie om vast te stellen en is daarmee de hardste, direct toetsbare doorgifte in het dossier.",
              "artefact": ADDENDUM},
             {"source": "archival-corroboration", "date": "2026-05-27",
              "description": "Onafgebroken aanwezig in 121 van 121 Wayback-snapshots sinds september 2012, ruim dertien jaar en vandaag nog.",
              "artefact": ADDENDUM}],
    continuity={"source": "wayback", "continuous_since": "2012-09", "duration_months": 164,
                "snapshots_consecutive": 121, "snapshots_total": 121, "marker": "ajax.googleapis.com",
                "note": "121 van 121 snapshots. Het domein draait bij een Nederlandse hoster; de doorgifte loopt via de ingeladen componenten, niet via de opslag."},
    reproduction=repro("repro/hotlink/hotlink.mjs",
                       "een request naar een Google-host bij paginalaad, zonder enige interactie, met het bezoekers-IP als afzender"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de resource wordt lokaal geserveerd via een proxy of self-host",
         "tested": True, "outcome": "excluded", "evidence": "request gaat naar ajax.googleapis.com, host in de HAR"},
        {"condition": "het IP-adres van de bezoeker is geen persoonsgegeven in deze context",
         "tested": True, "outcome": "excluded",
         "evidence": "LG Muenchen 2022 over Google Fonts: het hotlinken van een Google-resource is een doorgifte van persoonsgegevens"}]},
    products=[{"vendor": "Google", "product": "Hosted Libraries", "state": "known_affected",
               "configuration": "hotlinked in de paginabron"},
              {"vendor": "Google", "product": "Fonts", "state": "known_affected",
               "configuration": "hotlinked in de paginabron"}],
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 44"}, {"jurisdiction": "EU", "reference": "GDPR art. 6"}],
                   "decisions": [{"authority": "Landgericht Muenchen I", "reference": "3 O 17493/20",
                                  "date": "2022-01-20", "url": "https://gdprhub.eu/index.php?title=LG_M%C3%BCnchen_I_-_3_O_17493/20"}]},
    changes=changes("2026-05-18"))

# --- Vuture-landingspagina ----------------------------------------------

VUT = {"kind": "website", "name": "sites-pelsrijcken.vuturevx.com",
       "domain": "sites-pelsrijcken.vuturevx.com", "operator": FIRM,
       "sector": "legal marketing"}

rec(id="DPE-2026-0014", pattern="handover", target=VUT,
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:M/CS:NA/DC:ID/RC:3P/JU:3C/SC:ONE",
    destinations=[{"country": "GB", "host": "aws eu-west-2", "method": "vendor-statement"},
                  {"country": "US", "host": "fonts.gstatic.com", "method": "vendor-statement"}],
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "De knop 'Houd mij op de hoogte' op pelsrijcken.nl leidt naar een aanmeldformulier op een dedicated subdomein van Vuture, een marketing-CRM voor advocatenkantoren, sinds 2021 onderdeel van Intapp Inc. (VS). Bij paginalaad worden twee cookies gezet zonder enige consent-laag: VxSessionId en ASPSESSIONIDSGDARRTB. Google Fonts wordt gehotlinked van fonts.gstatic.com. Hosting op AWS eu-west-2 plus Cloudflare-CDN.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/handover/handover.mjs",
                       "cookies gezet bij paginalaad op het formulierdomein van de derde partij, zonder consent-mechanisme"),
    falsifier={"attribution": "har-pageref", "conditions": [
        {"condition": "de cookies zijn strikt noodzakelijk voor het formulier",
         "tested": False, "outcome": "untested",
         "evidence": "sessiecookies kunnen functioneel zijn; het record stelt de plaatsing vast zonder consent-laag, niet de onrechtmatigheid"},
        {"condition": "er is wel een consent-laag die de meting miste",
         "tested": True, "outcome": "excluded", "evidence": "meting van de landingspagina, 27 mei 2026"}]},
    products=[{"vendor": "Intapp", "product": "Vuture", "state": "known_affected"}],
    legal_context={"provisions": [{"jurisdiction": "NL", "reference": "Telecommunicatiewet art. 11.7a", "implements": "ePrivacy art. 5(3)"}, {"jurisdiction": "EU", "reference": "GDPR art. 44"}]},
    changes=changes("2026-05-27"))

rec(id="DPE-2026-0015", pattern="handover", target=VUT,
    status="published", first_seen="2026-05-27", last_seen="2026-05-27",
    vector="DPE:1.0/EV:R/CS:NA/DC:ID+CNT/RC:3P/JU:3C/SC:ONE",
    sources=[{"source": "own-measurement", "date": "2026-05-27",
              "description": "Het formulier verzamelt voornaam, achternaam, bedrijf, functietitel, e-mailadres en tientallen IA_Subscription-checkboxes voor praktijkgebieden en sectoren. Dat levert een granulair interesseprofiel per persoon op, geen geaggregeerde analytics. Het formulier is niet ingevuld: de velden zijn vastgesteld, de verwerking na verzending niet.",
              "artefact": ADDENDUM},
             {"source": "registry-note", "date": "2026-05-27",
              "description": "Evidence-niveau R, gereconstrueerd. Vuture's eigen documentatie beschrijft identity-stitching tussen e-mail-engagement en sitebezoek. Die koppeling is niet zelf gemeten en wordt hier niet als meting gepresenteerd.",
              "artefact": ADDENDUM}],
    reproduction=repro("repro/handover/handover-fields.md",
                       "inventarisatie van de formuliervelden en de abonnementscategorieen, zonder het formulier te verzenden",
                       manual_path="repro/handover/handover-fields.md"),
    falsifier={"attribution": "vendor-statement", "conditions": [
        {"condition": "de checkboxes worden niet per persoon opgeslagen maar alleen gebruikt voor routering",
         "tested": False, "outcome": "untested",
         "evidence": "niet vast te stellen zonder verzending of medewerking van de verwerker. Daarom staat dit record op EV:R en is het niet gerateerd."}]},
    products=[{"vendor": "Intapp", "product": "Vuture", "state": "known_affected"}],
    legal_context={"provisions": [{"jurisdiction": "EU", "reference": "GDPR art. 13"}, {"jurisdiction": "EU", "reference": "GDPR art. 44"}]},
    changes=changes("2026-05-27"))

# ---------------------------------------------------------------- schrijven

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for r in R:
        (OUT / (r["id"] + ".json")).write_text(
            json.dumps(r, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(R)} records geschreven naar {OUT}")
    by_sev, by_pat = {}, {}
    for r in R:
        by_sev[r["severity"]["label"]] = by_sev.get(r["severity"]["label"], 0) + 1
        by_pat[r["pattern"]] = by_pat.get(r["pattern"], 0) + 1
    print("ernst:   " + ", ".join(f"{k}={v}" for k, v in sorted(by_sev.items())))
    print("patroon: " + ", ".join(f"{k}={v}" for k, v in sorted(by_pat.items())))

if __name__ == "__main__":
    main()
