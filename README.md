# DPE · Data Protection Exposures

Een openbaar register van gemeten privacybevindingen, opgezet zoals CVE dat voor
softwarekwetsbaarheden doet.

Het idee erachter is simpel. Wie onderzoek doet naar tracking vindt telkens
dezelfde soorten bevindingen, maar ze hebben geen naam. Daardoor begint elke
publicatie opnieuw bij nul: dezelfde uitleg, dezelfde juridische onderbouwing,
dezelfde tegenwerpingen. Met een naam hoeft dat één keer.

```
 PATROON     Frontrun                een naam die je onthoudt en kunt citeren
             "een tag vuurt voordat de toestemmingsvraag is beantwoord"

 RECORD      DPE-2026-0001           een nummer dat je kunt opzoeken
             pgwoo.nl · 27-05-2026 · gemeten · ernst hoog
```

Zo lees je een bevinding: *"pgwoo.nl vertoont Frontrun, HollowNo en MaxStay."*
Drie woorden, en wie de patronen kent weet meteen wat er aan de hand is.

## Wat er anders is dan bij CVE

Drie dingen, en ze komen allemaal voort uit hetzelfde: bij ons is het bewijs
machineleesbaar en bij CVE is het proza.

**Elk record is na te spelen zonder onze tooling.** Met de hand in de browser,
of met een standalone script. Wie ons niet vertrouwt, hoeft dat ook niet.

**Elk record zegt wat het zou ontkrachten.** Het veld `falsifier` staat verplicht
in elk record: wat zou er waar moeten zijn om ons ongelijk te geven, en hebben we
dat nagekeken. Een record zonder getoetste falsifier komt er niet in.

**Elk record heeft een openbaar wijzigingsspoor.** Append-only. Een stille
correctie is technisch onmogelijk, en dat is precies de bedoeling.

## Meedoen

Zie [CONTRIBUTING.md](CONTRIBUTING.md). Vier manieren, van vijf minuten tot een
middag:

| Wat | Tijd | Waarom het telt |
|---|---|---|
| Een bestaand record naspelen | 5 min | tilt de bewijskracht naar de hoogste trede |
| Een nieuwe meting insturen | 20 min | met de bookmarklet, geen installatie nodig |
| Een patroon uitschrijven | een middag | elk volgend record erft die onderbouwing |
| Een record betwisten | | ook, en juist, als je organisatie erin staat |

Je naam blijft aan het record hangen, met de rol die je had. Anoniem mag ook.

**Jij levert een meting, het register draagt de publicatie.** Wie iets meldt, is
niet de uitgever. Krijgt een record tegenwind, dan komt die bij ons terecht.

## Hoe het in elkaar zit

```
 schema/          het recordformaat, de vector en de severity-regel, versioned
 rules/           de detectielogica per patroon, machineleesbaar
 registry/        de patronen, uitgeschreven voor mensen
 observations/    de records
 repro/           handleidingen, standalone scripts, de bookmarklet
 tools/           poortwachter, nummertoekenning, narekenen
 site/            de gegenereerde leeskant
```

Bij elke inzending draait `tools/validate.py`. Die toetst het schema, herberekent
de ernst uit de vector, controleert of er een wederhoorspoor is, of de falsifiers
zijn nagekeken, en of de reproductie buiten onze eigen tooling om kan. Zit er een
HAR bij, dan rekent `tools/replay.py` de bevinding na op dat bewijs. Wat rood
wordt, komt er niet in.

## Stand van zaken

Dit register is in opbouw. Eerlijk over wat er wel en niet af is:

| | |
|---|---|
| Records | 15, alle gevalideerd, uit één dossier |
| Patronen met een volledige pagina | 1 van 10 (`frontrun`) |
| Regels | 2 volledig, 7 stubs met openstaande TODO's |
| Onafhankelijke bevestiging gekoppeld | nog geen |

De negen andere patronen hebben wel records en een werkende regel, maar nog geen
uitgeschreven pagina. Tot die er is, staat er bij het patroon dat het nog niet af
is. Zie [OPEN.md](OPEN.md) voor de volledige lijst.

## Wat een record niet is

Een record beschrijft gemeten gedrag op een genoemd moment. Het stelt geen
onrechtmatigheid vast; dat is aan de Autoriteit Persoonsgegevens of aan de
rechter. Het register benoemt welke bepalingen in het geding zijn, per
jurisdictie, en houdt het daarbij.

## Licentie

Records, patronen en schema onder CC BY 4.0. Scripts en tooling onder MIT.
Overname en voortzetting door anderen is uitdrukkelijk toegestaan, inclusief de
nummerreeks: een verwijzing naar een record hoort over tien jaar nog iets te
betekenen, ook als de mensen erachter verdwenen zijn.
