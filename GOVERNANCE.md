# Bestuur van het register

Een register is pas een register als het niet van één persoon afhangt. Dit
document beschrijft wie wat mag, en het is expliciet geschreven om zichzelf
overbodig te maken als enige-uitgeversregeling.

## Rollen

**Bijdrager.** Iedereen. Meldt voorvallen, reproduceert bestaande records,
schrijft patronen uit, betwist. Heeft geen rechten nodig en geen account bij
wie dan ook behalve GitHub. Wordt gecrediteerd, of anoniem als hij dat wil.

**Uitgever.** Mag een inzending opnemen, de status naar `published` zetten, en
een record intrekken. Doet het wederhoor bij de betrokken partij. Uitgevers
worden benoemd door het bestuur en staan met naam in `UITGEVERS.md`, zodat
zichtbaar is wie het register vult.

**Bestuur.** Benoemt uitgevers, beslist over wijzigingen aan het schema en aan
de severity-regel, en behandelt bezwaren tegen een besluit van een uitgever.

Bij de start is er één uitgever. Dat is geen ideale toestand maar een
beginsituatie, en dit document staat er om die te kunnen verlaten.

## Wat een uitgever niet mag

Deze grenzen zijn er zodat de uitkomst niet van een persoon afhangt.

- **Een ernstlabel met de hand zetten.** Ernst wordt afgeleid uit de vector met
  `dpe-severity-1.0`. Wie een andere ernst wil, moet de meting veranderen, en dat
  is zichtbaar in het wijzigingsspoor.
- **Een record stil aanpassen.** Elke wijziging is een regel in `changes`, en die
  lijst is append-only. De CI weigert een record waarin oudere regels zijn
  gewijzigd.
- **Publiceren zonder wederhoor.** Zie `DISCLOSURE.md`. Geen uitzonderingen, ook
  niet als de bevinding evident is.
- **Een record verwijderen.** Een onjuist record wordt ingetrokken en blijft
  staan met de status `withdrawn` en de reden erbij. Wat weg is, is niet te
  controleren.
- **Een eigen inzending zelf opnemen zonder tweede paar ogen**, zodra er meer dan
  één uitgever is.

## Wijzigingen aan het schema

Het schema en de severity-regel zijn gepinde versies. Een wijziging die de
betekenis van bestaande records verandert, vereist een nieuw versienummer; oude
records blijven verwijzen naar de versie waaronder ze zijn gemaakt.

Dat is geen formaliteit. Zou de severity-regel stilletjes veranderen, dan zou een
label uit 2026 iets anders betekenen dan hetzelfde label uit 2027, en dan is het
register waardeloos als tijdreeks. `tools/dpe.py` berekent daarom een
methodiek-hash over schema, vectordefinitie en regels, en die hash staat in de
uitvoer van elke validatieronde.

## Belangenverstrengeling

Een uitgever neemt geen records op over een organisatie waarvoor hij werkt of
heeft gewerkt, of waarmee hij een financiële band heeft. Doet die situatie zich
voor, dan gaat het naar een andere uitgever, en bij één uitgever wordt het
opgeschort tot er een tweede is.

Metingen aan de eigen infrastructuur van het register zijn wel toegestaan en
worden aangemoedigd. Wie anderen meet, hoort zichzelf te meten.

## Toetreden als uitgever

Organisaties met een aantoonbaar belang bij dit veld kunnen uitgever worden:
onderzoeksinstellingen, belangenorganisaties, redacties, en toezichthouders.
Voorwaarden: onderschrijving van dit document en van het disclosurebeleid, en
minstens vijf opgenomen records of tien reproducties als bijdrager.

Dat laatste is bewust laag. De drempel is bedoeld om te weten dat iemand de
methode kent, niet om de deur dicht te houden.

## Als het register ophoudt

Alle records, het schema, de regels en de reproductiescripts staan onder een
open licentie in een publieke repository. Houdt dit register op te bestaan, dan
kan iedereen het voortzetten of overnemen, inclusief de nummerreeks. De
identifiers blijven daarmee bruikbaar, ook als de mensen erachter verdwijnen.
Dat is de bedoeling: een verwijzing naar een record moet over tien jaar nog iets
betekenen.
