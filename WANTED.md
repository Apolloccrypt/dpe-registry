# Gezocht

Openstaande vragen waar we niet uitkomen. Geen wenslijst en geen lege
nummerreeks: iedere regel hieronder is een concreet gat waar we vastlopen, met
erbij wat een antwoord zou zijn.

Wie er een oplost, staat als bijdrager in de entry. Dat blijft daar staan.

---

## Detectie waar we geen goede indicator voor hebben

**Homecall (DPE-2026-0012), scriptbaar maken.**
De handmatige route werkt: capture op de router, apparaat met rust laten, kijken
wat er toch uitgaat. Wat ontbreekt is een indicator die een script kan toetsen.
Waar loopt het op vast: het onderscheid tussen een update-controle die legitiem
is en telemetrie die dat niet is, valt niet uit het verkeer alleen af te leiden.

*Wat helpt:* een idle-capture van een consumentenapparaat, met vermelding van
model en firmwareversie, plus jouw redenering waarom een bepaalde stroom wel of
niet functioneel is. Ook een negatief resultaat is bruikbaar.

**Sidecar (DPE-2026-0013) bij gepinde apps.**
Componenten met certificate pinning laten zich niet zomaar meelezen. Wij willen
geen methode die neerkomt op het slopen van andermans app.

*Wat helpt:* een aanpak die binnen de grenzen blijft en toch vaststelt welke
hosts een component benadert. Statische inventarisatie plus DNS-observatie is
misschien genoeg; we weten het niet.

**Silhouette (DPE-2026-0007) zonder debugprotocol.**
Fingerprinting vaststellen vereist nu het aanhaken op property-reads via het
debugprotocol. Dat kan een gewone gebruiker niet.

*Wat helpt:* een bookmarklet-achtige route die aantoont dat een script van een
derde device-eigenschappen uitleest, zonder debugger.

## Namen waar we niet zeker over zijn

Een naam die niet blijft hangen, wordt niet gebruikt. Deze drie twijfelen wij
zelf over, en een beter voorstel is welkom.

- **Deadend** (DPE-2026-0014), de knop die er niet is of niet blijft staan. De
  naam suggereert een doodlopende weg, terwijl het gaat om een ontbrekende uitgang.
- **Telltale** (DPE-2026-0006), wat je typt bereikt een derde. Werkt in het
  Engels, maar de nuance van verklikken zit er misschien te dik op.
- **Sidecar** (DPE-2026-0013). Mooi beeld, maar het botst met bestaand jargon in
  containerarchitectuur, waar een sidecar juist iets nuttigs is.

Een voorstel is bruikbaar als het één woord is, het gedrag van het systeem
beschrijft en niet de schade bij de persoon, en uitspreekbaar is in een
telefoongesprek met een redacteur.

## Fouten die vast bestaan maar hier nog niet staan

Wij zien ze wel maar hebben ze niet scherp genoeg om een nummer te rechtvaardigen.

- Een televisie die vaststelt wat er op het scherm te zien is en dat rapporteert.
  Bestaat aantoonbaar; wij hebben geen meetopstelling.
- Een auto die locatie of rijgedrag deelt met de fabrikant, zonder een instelling
  die dat stopt. Raakt Deadend en Homecall, maar verdient waarschijnlijk een
  eigen nummer.
- Een betaalterminal of kassasysteem dat transactiegegevens doorgeeft aan derden.
- Identificatiedocumenten of biometrie die naar een verificatieleverancier gaan.
  Wij hebben hier materiaal over maar nog geen scherpe afbakening tegenover
  gewone identiteitscontrole.

*Wat helpt:* een beschrijving van het mechanisme, en vooral de grens: wanneer is
het dit en wanneer is het normaal functioneren.

## Rechtsgebieden buiten Nederland

De fouten zijn EER-breed, de verwijzingen niet. Nu staan alleen Nederlandse en
EU-bepalingen in `law/`.

*Wat helpt:* de nationale bepaling die in jouw land dezelfde EU-regel uitvoert,
in het formaat van `law/nl-tw-11-7a.yaml`. Voor Duitsland is dat vermoedelijk
§25 TDDDG, voor België een artikel in de wet elektronische communicatie, maar wij
zijn daar niet thuis en gokken liever niet.

## Jurisprudentie

Drie uitspraken staan er nu in. Er is veel meer, en juist uitspraken die een
fout **inperken** zijn welkom: die maken een entry bruikbaar in een discussie in
plaats van alleen in een aanklacht.

*Wat helpt:* ECLI, kern in twee zinnen, en welke entry het raakt.

## Reproductiescripts

Tien van de veertien entries hebben nog geen werkend script. De structuur staat
en `repro/frontrun/frontrun.mjs` is het model: standalone, één afhankelijkheid,
en het rapporteert wat het niet kan zien.

*Wat helpt:* een script voor één entry. Dat is een afgerond stuk werk van
ongeveer een uur, en het is de meest concrete bijdrage die er is.

---

## Hoe je iets aanlevert

Een issue is genoeg. Een pull request mag, hoeft niet. Losse gedachten in een
issue zijn ook welkom: wij schrijven het dan uit en jij staat als bijdrager in
de entry.

Zie [CONTRIBUTING.md](CONTRIBUTING.md).
