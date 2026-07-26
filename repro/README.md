# Reproduceren

Elk record in dit register verwijst naar minstens één manier om de bevinding zelf
vast te stellen, en die manier mag nooit afhangen van gereedschap dat alleen het
register bezit. Een bevinding die je moet geloven, is geen bevinding.

Er zijn drie lagen. Ze doen verschillende dingen en versterken elkaar.

```
 A  ZELF NASPELEN            jij meet          repro/<pattern>/
 B  DERDE LAAT METEN         zij meten         publieke scanners, permanente URL
 C  BEWIJS INSPECTEREN       jij kijkt na      onze HAR, in jouw browser
```

## A. Zelf naspelen

Per pattern staat er een map met twee ingangen.

| Bestand | Voor wie | Wat het kost |
|---|---|---|
| `MANUAL.md` | iedereen | twee minuten, alleen een browser |
| `<pattern>.mjs` | wie een terminal heeft | `npm i playwright`, dan één commando |

### Zonder iets te installeren

**GitHub Codespaces.** Open deze repository in een Codespace en het script draait
meteen; Playwright zit in de devcontainer.

**Google Colab.** Voor wie geen terminal gebruikt. Een notebook installeert
Playwright en draait hetzelfde script in de browser.

Let bij beide op één ding, en het is geen detail: **waar de omgeving het
internet op gaat, bepaalt wat je meet.** Consent-dialogen worden vaak per regio
uitgeleverd. Een runner die vanuit de Verenigde Staten uitgaat kan een andere
banner krijgen dan een bezoeker uit Nederland, en dan reproduceert een bevinding
met `CS:PRE` mogelijk niet. Kies een EU-regio, en noteer welke. Elk record legt
in `reproduction.methods[].runner.exit_country` vast waar de meting vandaan kwam.

## B. Een derde laten meten

Dit is de sterkste laag en de meest onderschatte. Deze diensten meten zelf, en
bewaren het resultaat op een permanente URL onder hun eigen beheer. Dat levert
twee dingen die eigen metingen niet kunnen leveren.

Ten eerste: de meter is niet de klager. Het bekende verweer dat een onderzoeker
zijn eigen gereedschap heeft gebouwd om zijn eigen conclusie te vinden, houdt geen
stand tegen een scan van een onafhankelijke partij.

Ten tweede: het resultaat is niet met terugwerkende kracht op te ruimen. Wordt er
drie dagen na publicatie een tag verwijderd, dan blijft de scan van vorige week
staan waar hij staat.

| Dienst | Meet | Waarom het telt |
|---|---|---|
| [urlscan.io](https://urlscan.io) | alle requests, cookies, screenshot, HAR-download | permanent, publiek, met eigen ID |
| [Blacklight](https://themarkup.org/blacklight) | trackers, session recording, fingerprinting, cookies | van The Markup, journalistiek gezaghebbend |
| [Webbkoll](https://webbkoll.dataskydd.net) | third parties, cookies, headers, referrer policy | EU-gehost, door Dataskydd.net |
| [WebPageTest](https://www.webpagetest.org) | echte browser, waterfall plus HAR, keuze uit locaties | EU-meetpunt te kiezen |
| [securityheaders.com](https://securityheaders.com) | HSTS en overige headers | voor de headerbevindingen |
| [Wayback Machine](https://web.archive.org) | gearchiveerde broncode over de jaren | de basis onder het `continuity`-veld |

Een scan die door iemand anders dan het register is gestart, weegt zwaarder. Als
je er een doet, staat dat in het record onder `operator`.

Blacklight verdient een aparte opmerking: het is gebouwd om precies dat te
detecteren wat `overshoulder` beschrijft, session recording. Voor dat pattern is
een Blacklight-permalink de meest directe onafhankelijke bevestiging die er is.

## C. Ons bewijs inspecteren

Elke meting laat een HAR achter. Die is te openen zonder installatie:

- <https://trace.playwright.dev> voor traces en HAR-bestanden
- de netwerkpanelen van Chrome en Firefox importeren HAR direct

## Wat we niet doen

Geen enkel script in deze map vult formulieren in, meldt zich aan, logt in of
verstuurt gegevens van derden. Ze laden een pagina en kijken wat de pagina zelf
doet. Waar een bevinding over gedrag ná verzending gaat, staat het record op
evidence-niveau `R` (gereconstrueerd) en wordt het niet als meting gepresenteerd.
Zie `DPE-2026-0015` voor een voorbeeld daarvan.
