# DPE · Data Protection Exposures

A catalogue of numbered faults in how systems handle personal data.

Researchers keep finding the same things, and those things have no name. So every
publication starts from nothing: the same explanation, the same legal grounding,
the same objections answered again. With a number, that happens once.

```
  DPE-2026-0001   Tracking before consent
                  A tag fires before the consent question has been answered.
```

## What this is for

**Not vulnerabilities.** There is nothing to exploit. The system does what its
builder intended, and that intention is the objection. A router phoning home to
another country gets no CVE because nothing is broken, and until now there was no
number to cite for it either. That gap is why this exists.

**Not accusations.** No company, product or domain appears in this catalogue.
Whoever establishes that a system exhibits one of these faults publishes that
themselves, under their own name, and cites the number. That keeps definitions
usable long after any individual site has been cleaned up.

**No severity.** No score, no judgement of harm, by design. CVE does not weigh
either; NVD does that, separately. How heavily a concrete case weighs depends on
that case, and belongs to whoever applies the entry.

<!-- BEGIN CATALOGUS: gegenereerd door tools/build_readme_list.py -->

## De catalogus (43 fouten)

Elke fout heeft een eigen pagina op <https://totaledigitalewaarborging.nl/register> met de indicator, de eisen
aan de meting, wat hem zou ontkrachten, en hoe je hem naspeelt.

### Gegevens

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0005`](https://totaledigitalewaarborging.nl/register/DPE-2026-0005) | **Sessieopname**<br>De sessie zelf wordt opgenomen, niet alleen de paginaweergave. | web |
| [`DPE-2026-0006`](https://totaledigitalewaarborging.nl/register/DPE-2026-0006) | **Invoer naar derden**<br>Wat de bezoeker intypte of zocht, bereikt een derde partij. | web |
| [`DPE-2026-0007`](https://totaledigitalewaarborging.nl/register/DPE-2026-0007) | **Apparaatherkenning**<br>Het apparaat wordt herkend aan zijn kenmerken, zonder dat er iets is opgeslagen. | web |
| [`DPE-2026-0017`](https://totaledigitalewaarborging.nl/register/DPE-2026-0017) | **Wettelijk persoonsnummer naar een derde**<br>Een nummer dat de overheid toekent voor identificatie gaat naar een partij zonder wettelijke taak die het vraagt. | app, web, API |
| [`DPE-2026-0018`](https://totaledigitalewaarborging.nl/register/DPE-2026-0018) | **Document verder uitgelezen dan de controle**<br>Een identiteitscontrole legt het hele document vast waar de vraag aan een fractie genoeg had. | app, web, API |
| [`DPE-2026-0019`](https://totaledigitalewaarborging.nl/register/DPE-2026-0019) | **Bijzondere gegevens in een gebeurtenis**<br>Een gebeurtenis naar een derde verraadt gezondheid, geloof of seksualiteit via zijn naam, pad of parameters. | web, app |
| [`DPE-2026-0021`](https://totaledigitalewaarborging.nl/register/DPE-2026-0021) | **De pagina tast je eigen apparaat af**<br>Een pagina tast de eigen machine of het thuisnetwerk van de bezoeker af om te zien wat daar draait. | web, desktop |
| [`DPE-2026-0023`](https://totaledigitalewaarborging.nl/register/DPE-2026-0023) | **Aanwezigheid via een automatisch antwoord**<br>Een systeem antwoordt uit zichzelf op een ongevraagd signaal, en dat antwoord verraadt of er iemand is. | app, API, desktop, IoT |
| [`DPE-2026-0024`](https://totaledigitalewaarborging.nl/register/DPE-2026-0024) | **Iedereen die passeert wordt herkend**<br>Een herkenningssysteem legt iedereen vast die het ziet, terwijl het doel alleen over de gezochten gaat. | IoT, firmware, netwerkapparaat, voertuig |
| [`DPE-2026-0030`](https://totaledigitalewaarborging.nl/register/DPE-2026-0030) | **Openen van een bericht wordt gemeten**<br>Een bericht meldt terug wanneer het geopend is, via een bron die bij het weergeven wordt opgehaald en de ontvanger aanwijst. | web, app, desktop |
| [`DPE-2026-0033`](https://totaledigitalewaarborging.nl/register/DPE-2026-0033) | **Inloggen vraagt meer dan inloggen nodig heeft**<br>Inloggen via een andere partij geeft in dezelfde handeling toegang tot gegevens die voor het inloggen niet nodig zijn. | web, app, API |
| [`DPE-2026-0034`](https://totaledigitalewaarborging.nl/register/DPE-2026-0034) | **Logboek met inhoud in plaats van gebeurtenissen**<br>Een logboek bewaart wat iemand invulde of te zien kreeg, terwijl vastleggen dat er iets gebeurde volstaat. | web, app, API, desktop, firmware |
| [`DPE-2026-0036`](https://totaledigitalewaarborging.nl/register/DPE-2026-0036) | **Productiviteitsmeting per medewerker**<br>Werksoftware legt activiteit per persoon per tijdvak vast en maakt daar een cijfer over die persoon van. | desktop, web, app |
| [`DPE-2026-0037`](https://totaledigitalewaarborging.nl/register/DPE-2026-0037) | **Schermopname op het werkapparaat**<br>Werksoftware neemt het scherm zelf op, met vaste tussenpozen of op een signaal, zonder dat de medewerker dat start. | desktop, web, app |
| [`DPE-2026-0038`](https://totaledigitalewaarborging.nl/register/DPE-2026-0038) | **Dienstvoertuig gevolgd buiten werktijd**<br>Een volgsysteem blijft posities vastleggen als het voertuig buiten dienst is, zonder werkende manier om privegebruik aan te geven. | voertuig, IoT, app |
| [`DPE-2026-0039`](https://totaledigitalewaarborging.nl/register/DPE-2026-0039) | **Examentoezicht met gedragsscores**<br>Examensoftware kijkt naar lichaam, geluid en scherm, en houdt per student een verdenkingsregistratie over na de uitslag. | web, desktop, app |
| [`DPE-2026-0041`](https://totaledigitalewaarborging.nl/register/DPE-2026-0041) | **Invoer wordt standaard trainingsmateriaal**<br>Wat iemand in een dienst typt, wordt bewaard om een model te verbeteren, tenzij hij een instelling vindt en uitzet. | web, app, API, desktop |
| [`DPE-2026-0042`](https://totaledigitalewaarborging.nl/register/DPE-2026-0042) | **Uitbreiding vraagt meer rechten dan haar functie**<br>Een uitbreiding claimt toegang tot alle paginas terwijl de functie die zij beschrijft over een handvol sites gaat. | web, desktop |

### Keten

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0008`](https://totaledigitalewaarborging.nl/register/DPE-2026-0008) | **Formulier bij een derde**<br>Een formulier dat bij de site lijkt te horen, staat bij een derde die voor eigen rekening profileert. | web |
| [`DPE-2026-0015`](https://totaledigitalewaarborging.nl/register/DPE-2026-0015) | **Biedverzoek naar veel partijen tegelijk**<br>Een paginaweergave gaat tegelijk naar veel biedende partijen, elk met de context en een identifier. | web, app |
| [`DPE-2026-0016`](https://totaledigitalewaarborging.nl/register/DPE-2026-0016) | **Identificatiemerken uitwisselen**<br>Twee partijen wisselen elkaars identifier uit, zodat hun aparte dossiers over dezelfde persoon te koppelen zijn. | web, app |
| [`DPE-2026-0020`](https://totaledigitalewaarborging.nl/register/DPE-2026-0020) | **Derde partij onder een eigen subdomein**<br>Een subdomein van de site zelf wijst naar een derde, zodat diens verzameling leest als die van de site. | web, API |
| [`DPE-2026-0025`](https://totaledigitalewaarborging.nl/register/DPE-2026-0025) | **Transactiegegevens buiten de betaalketen**<br>Gegevens over een betaling bereiken partijen die geen rol spelen in het uitvoeren ervan. | web, app, firmware, IoT |
| [`DPE-2026-0031`](https://totaledigitalewaarborging.nl/register/DPE-2026-0031) | **E-mailadres als sleutel tussen diensten**<br>Een adres dat voor contact is gegeven, gaat door naar andere partijen, plat of als hashwaarde, zodat zij dezelfde persoon herkennen. | web, app, API |
| [`DPE-2026-0032`](https://totaledigitalewaarborging.nl/register/DPE-2026-0032) | **Account gekoppeld aan het volgprofiel**<br>Bij het inloggen gaat de accountaanduiding van de dienst naar een partij die al een profiel van dezelfde browser had. | web, app |
| [`DPE-2026-0043`](https://totaledigitalewaarborging.nl/register/DPE-2026-0043) | **Registraties gekoppeld op persoonsnummer**<br>Gegevens die voor de ene wettelijke taak zijn verzameld, worden op het persoonsnummer gekoppeld aan die van een andere instantie. | API, web, desktop |

### Toestemming

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0001`](https://totaledigitalewaarborging.nl/register/DPE-2026-0001) | **Meten voor de toestemmingsvraag**<br>Een tag vuurt voordat de toestemmingsvraag is beantwoord. | web |
| [`DPE-2026-0002`](https://totaledigitalewaarborging.nl/register/DPE-2026-0002) | **Weigeren zonder effect**<br>Weigeren verandert niet wat de browser verlaat. | web |
| [`DPE-2026-0003`](https://totaledigitalewaarborging.nl/register/DPE-2026-0003) | **Geen weigeroptie**<br>De toestemmingsdialoog biedt accepteren en geen manier om te weigeren. | web |
| [`DPE-2026-0014`](https://totaledigitalewaarborging.nl/register/DPE-2026-0014) | **Geen werkende uitschakeling**<br>De instelling die het verzamelen zou stoppen bestaat niet, of overleeft geen herstart. | firmware, IoT, voertuig, app |
| [`DPE-2026-0040`](https://totaledigitalewaarborging.nl/register/DPE-2026-0040) | **Betalen of accepteren als enige keuze**<br>Het eerste scherm biedt betalen of instemmen met doelen van derden, en geen pad dat weigert en toch bij de inhoud komt. | web, app |

### Methode

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0011`](https://totaledigitalewaarborging.nl/register/DPE-2026-0011) | **Tag buiten de broncode**<br>Tags vuren vanuit een container terwijl ze nergens in de broncode staan. | web |
| [`DPE-2026-0026`](https://totaledigitalewaarborging.nl/register/DPE-2026-0026) | **Ontvanger toegeschreven op een spoofbare header**<br>Een bevinding wijst de veroorzakende pagina aan op basis van een header die iedereen kan zetten. | web, app |
| [`DPE-2026-0027`](https://totaledigitalewaarborging.nl/register/DPE-2026-0027) | **Land bepaald met een verouderde database**<br>Een doorgifteclaim rust op een adres-naar-landtabel die niet meer klopt met de toewijzing. | web, app, IoT, firmware |
| [`DPE-2026-0028`](https://totaledigitalewaarborging.nl/register/DPE-2026-0028) | **Aanwezigheid in de binary telt als verzending**<br>Een bevinding ziet een onderdeel in een pakket aan voor bewijs dat het ook verzendt. | app, desktop, firmware |
| [`DPE-2026-0029`](https://totaledigitalewaarborging.nl/register/DPE-2026-0029) | **Mislukte meting telt als schoon resultaat**<br>Een meting die niet werkte, wordt gerapporteerd als een onderwerp dat niets doet. | web, app, IoT, firmware |

### Telemetrie

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0012`](https://totaledigitalewaarborging.nl/register/DPE-2026-0012) | **Apparaat belt naar huis**<br>Een apparaat zoekt contact met een server in het buitenland zonder functie die dat vraagt. | firmware, IoT, netwerkapparaat, voertuig |
| [`DPE-2026-0013`](https://totaledigitalewaarborging.nl/register/DPE-2026-0013) | **Meeliftende component**<br>Een meegeleverd onderdeel verzamelt voor eigen rekening, naast wat de app zelf doet. | app, desktop, firmware |
| [`DPE-2026-0022`](https://totaledigitalewaarborging.nl/register/DPE-2026-0022) | **Meetinterval dat aanwezigheid verraadt**<br>Een apparaat rapporteert zo vaak en zo herkenbaar dat de reeks laat zien wanneer het huis leeg is. | IoT, firmware, netwerkapparaat |

### Bewaring

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0004`](https://totaledigitalewaarborging.nl/register/DPE-2026-0004) | **Maximale bewaartermijn**<br>Een identifier-cookie krijgt de maximale bewaartermijn die een browser aanvaardt, voordat de vraag is beantwoord. | web |
| [`DPE-2026-0035`](https://totaledigitalewaarborging.nl/register/DPE-2026-0035) | **Wissen dat de back-up niet bereikt**<br>Een op verzoek gewist gegeven blijft in de back-up staan en komt bij een herstel weer in het systeem terug. | web, app, API, desktop |

### Doorgifte

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0009`](https://totaledigitalewaarborging.nl/register/DPE-2026-0009) | **Externe bron inladen**<br>Een bron die rechtstreeks van een derde wordt geladen, maakt van elke paginaweergave een doorgifte. | web |

### Transparantie

| | Fout | Waar |
|---|---|---|
| [`DPE-2026-0010`](https://totaledigitalewaarborging.nl/register/DPE-2026-0010) | **Niet-vermelde ontvanger**<br>Een ontvanger van persoonsgegevens ontbreekt in de eigen privacyverklaring van de partij. | web |

<!-- END CATALOGUS -->
## What is in an entry

| | |
|---|---|
| Mechanism | how the fault arises, and the fault it is most often confused with |
| Indicator | the concrete thing that settles it, checkable without interpretation |
| Detection quality | which method establishes it and how strongly, on a fixed scale |
| Falsifiers | what would refute it, and whether that can be checked from a capture |
| Reproduction | by hand, bookmarklet, script; never requiring tooling we own |
| Legal framing | provisions per jurisdiction, case law, and the standard objections answered |
| In practice | what to verify in a DPIA, how to word a procurement clause, what to hand a regulator |

Each entry lives at its own permanent address with the same content as JSON
beside it. Identifiers are never reused; a deprecated entry keeps its number and
its address, with the reason attached, because references to it exist elsewhere.

## The method is published too

[METHOD.md](METHOD.md) sets out how to go looking for these faults: define scope
before measuring, capture clean, take a baseline, vary one thing at a time, walk
the catalogue rather than your intuition, try to break your own finding, ask
before publishing. Versioned, because a measurement taken under 1.0 is not the
same claim as one taken under 2.0.

Security has the OWASP Testing Guide for this. Data protection had nothing, which
is why no two investigations were comparable.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [WANTED.md](WANTED.md), which lists
what we are actually stuck on rather than a wish list.

The cheapest useful contribution is reproducing an entry and reporting what you
saw, including when it did not reproduce. After that: a falsifier we missed, the
national provision for your jurisdiction, a reproduction script, a better title
for something we named badly, or a fault we have not written down because you
work on hardware and we mostly measure browsers.

You get credit in the entry, permanently. Anonymous is fine. And since this
catalogue names no companies, contributing costs you nothing but time.

## Layout

```
 catalogue/    the entries, one JSON each
 schema/       the entry schema, versioned
 law/          provisions, per jurisdiction
 caselaw/      rulings and decisions, with ECLI where one exists
 repro/        manuals, standalone scripts, the bookmarklet
 tools/        replay a rule against a capture, adapt scanner output
 METHOD.md     how to conduct a measurement
```

Build with `python3 build_catalogue.py && python3 build_pages.py`, publish with
`./deploy.sh <target>`. The deploy refuses to run if a single entry fails
validation.

## Status

Draft. Forty-three entries across web, apps, firmware, IoT, vehicles, the
workplace, the classroom and public administration. Reproduction scripts exist
for a handful of them; the rest is in WANTED.md.

## Licence

Entries, schema and legal material under CC BY 4.0. Tooling under MIT. Both allow
anyone to continue this work, including the numbering, should this catalogue ever
stop. A reference made today has to still resolve in ten years.

Part of [Totale Digitale Waarborging](https://totaledigitalewaarborging.nl),
fourth axis: can you account for it in legal terms?
