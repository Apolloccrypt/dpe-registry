---
name: Frontrun
slug: frontrun
family: consent
first_named: 2026-07-26
schema_version: "1.0"
status: active
provisions:
  - "ePrivacy art. 5 lid 3, in Nederland Telecommunicatiewet art. 11.7a"
  - "AVG art. 6 lid 1 sub a"
  - "AVG art. 4 lid 11"
related:
  - hollowno
  - onedoor
  - maxstay
  - sideload
observations: 3
---

# Frontrun

**Een tag vuurt voordat de toestemmingsvraag is beantwoord.**

De naam komt uit de handel: frontrunning is een order uitvoeren vóór de order die
je hoort af te wachten. Hier gebeurt hetzelfde. De site vraagt om toestemming en
handelt alvast alsof die er is.

## Wat het is

Bij het laden van een pagina gaan er verzoeken naar een meet- of advertentiepartij
op een moment dat de bezoeker nog geen keuze heeft kunnen maken. Er staat een
banner, of er staat er geen, maar in beide gevallen is er al gemeten voordat er
iets is gevraagd. Meestal wordt er ook een identifier geplaatst, waarmee de
bezoeker herkenbaar wordt bij een volgend bezoek.

Frontrun is geen configuratiefout in de banner. De banner werkt vaak precies zoals
bedoeld; hij hangt alleen niet vóór de tag. Dat is een bouwkeuze, en die keuze
ligt bij de partij die de pagina publiceert.

## Waarom het telt

Toestemming die achteraf komt, is geen toestemming. Artikel 11.7a van de
Telecommunicatiewet eist toestemming vóór het plaatsen of uitlezen van gegevens op
het apparaat van de gebruiker, met een nauwe uitzondering voor wat strikt
noodzakelijk is voor een door de gebruiker gevraagde dienst. Analytics valt daar
niet onder.

De schade is niet abstract. Wie een pagina opent over een aandoening, een
juridisch conflict of een uitkering, heeft op dat moment al een signaal afgegeven
aan een derde partij, en de keuze om dat niet te doen was er niet.

## Onderscheid met naburige patronen

Deze grenzen zijn scherp, omdat een record dat het verkeerde pattern draagt
gemakkelijk te weerleggen is.

| Situatie | Pattern |
|---|---|
| Tag vuurt vóór de vraag | **frontrun** |
| Weigeren verandert het verkeer niet | [hollowno](hollowno.md) |
| Er is geen weigeroptie aangeboden | [onedoor](onedoor.md) |
| Tag vuurt via een container, niet uit de broncode | [sideload](sideload.md) |
| Bewaartermijn maximaal opgerekt | [maxstay](maxstay.md) |

Frontrun en hollowno komen vaak samen voor, maar het zijn twee bevindingen. De
eerste gaat over het moment, de tweede over het effect van de keuze. Een partij
kan de ene repareren en de andere laten staan, en dan moet het register dat
afzonderlijk kunnen tonen.

## Hoe je het vaststelt

Zie [`repro/frontrun/`](../repro/frontrun/). Met de hand duurt het twee minuten;
het script legt een HAR vast die een derde kan nakijken.

Drie eisen aan een meting die standhoudt:

1. **Schoon profiel.** Een profiel met eerdere toestemming maakt de meting
   waardeloos. Elk record legt dit vast in `environment.profile`.
2. **Geen interactie.** Niet accepteren, niet weigeren, niet wegklikken. Alles wat
   daarna gebeurt, hoort in een ander record.
3. **Attributie via de HAR-pageref of de initiator-keten.** Nooit via de
   referer-header: die is te spoofen en meetinstrumentatie doet dat ook.

## Wat het weerlegt

Een record mag pas gepubliceerd worden als deze condities getest zijn en de
uitkomst in het record staat.

- De meethost is een first-party CNAME naar het doeldomein. Dan lijkt het
  third-party maar is het dat niet, of andersom.
- Het verzoek draagt geen identifier en zet geen cookie. Dan is er verkeer, maar
  is de gevolgtrekking over persoonsgegevens zwakker.
- Toestemming was in een eerdere sessie op hetzelfde profiel gegeven.
- De tag laadt pas ná een interactie die de meting per ongeluk uitlokte, zoals een
  klik om een overlay weg te halen.

## De standaardtegenwerpingen

**"Analytics valt onder de functionele uitzondering."**
De uitzondering geldt voor wat strikt noodzakelijk is voor een door de gebruiker
gevraagde dienst. Publieksmeting is noodzakelijk voor de exploitant, niet voor de
bezoeker. De EDPB en de AP houden die lijn aan. Bij analytics van een derde partij
die de gegevens ook voor eigen doelen gebruikt, houdt het argument helemaal op.

**"De servers staan in de EU."**
Dat is een antwoord op een andere vraag. Frontrun gaat over het moment, niet over
de bestemming. De bestemming staat apart in de `JU`-as van de vector en kan `EU`
zijn zonder dat dit record verandert. Een record waarin `JU:EU` staat en dat toch
`high` haalt, laat precies zien dat het verweer langs de bevinding heen gaat.

**"Het ging om een enkele slordigheid, inmiddels opgelost."**
Toetsbaar, en daarvoor bestaat het `continuity`-veld. Gearchiveerde broncode laat
zien hoe lang de tag er stond. Een onafgebroken reeks van jaren is geen
slordigheid, en dat is niet met terugwerkende kracht te repareren.

**"Onze consent-tool regelt dit."**
Meten, niet aannemen. Een consent-tool die cookieplaatsing tegenhoudt kan het
laden van een tagcontainer ongemoeid laten. Zie `DPE-2026-0007`, waar dat precies
op het enige domein gebeurde waar de tool aanwezig was.

## Wat een Frontrun-record niet zegt

Het record stelt gemeten gedrag vast. Of dat gedrag onrechtmatig is, stelt een
toezichthouder of een rechter vast. Het register benoemt de bepalingen die in het
geding zijn, en houdt het daarbij.

## Records

| Record | Doelwit | Datum | Ernst | Status |
|---|---|---|---|---|
| [DPE-2026-0001](../observations/DPE-2026-0001.json) | pgwoo.nl | 27-05-2026 | high | published |
| [DPE-2026-0004](../observations/DPE-2026-0004.json) | pgawb.nl | 27-05-2026 | high | published |
| [DPE-2026-0007](../observations/DPE-2026-0007.json) | cassatieblog.nl | 27-05-2026 | high | published |
