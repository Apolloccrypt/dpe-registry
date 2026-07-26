# Het koppelproces

> *This document is in Dutch on purpose. It describes how the paper side and the
> building side of an organisation hand work to each other, and the vocabulary,
> the roles and the procurement practice it addresses are Dutch. The catalogue
> itself is in English.*

Er zijn twee werelden en ze praten niet.

Aan de ene kant staat de papieren kant: functionarissen, juristen, inkopers.
Zij stellen eisen, beoordelen risico's en tekenen. Aan de andere kant staat de
kant die bouwt: ontwikkelaars, beheerders, leveranciers. Zij weten wat een
systeem werkelijk doet.

Wat er in de praktijk gebeurt, is dat beide kanten hun eigen document maken. De
DPIA beschrijft een systeem dat niemand heeft nagemeten. De code doet dingen die
niemand heeft opgeschreven. En beide kanten gaan ervan uit dat de ander erover
gaat.

Dat is geen kennisprobleem. Een functionaris hoeft niet te leren meten en een
ontwikkelaar hoeft de AVG niet uit zijn hoofd te kennen. Het is een
procesprobleem: er zijn drie momenten waarop iets van de ene wereld naar de
andere moet, en op alle drie ontbreekt het overdrachtsstuk.

---

## De drie overdrachten

```
  PAPIEREN KANT                                          BOUWENDE KANT
  functionaris, jurist, inkoper                ontwikkelaar, beheerder, leverancier

        │                                                      │
        │   1. DE OPDRACHT                                     │
        │   ─────────────────────────────────────────────►     │
        │   "toets deze veertien bevindingen,                  │
        │    volgens methode 1.0, voor [datum]"                │
        │                                                      │
        │   geen jargon nodig van de vrager,                   │
        │   geen interpretatie nodig van de uitvoerder         │
        │                                                      │
        │                                    2. DE UITKOMST    │
        │   ◄─────────────────────────────────────────────     │
        │   rapport: wat getoetst, wat gevonden,               │
        │   met datum, land en meetbestanden                   │
        │                                                      │
        │   leesbaar zonder techniek,                          │
        │   controleerbaar met techniek                        │
        │                                                      │
        │   3. DE EIS                                          │
        │   ─────────────────────────────────────────────►     │
        │   "DPE-2026-0001 herstellen binnen vier weken,       │
        │    daarna hermeten"                                  │
        │                                                      │
        │   een genummerde bevinding, geen beschrijving        │
        │   waar over te twisten valt                          │
        │                                                      │
```

Op elk van die drie pijlen zit nu een artefact, en dat is het hele verschil.

## 1. De opdracht

**Het probleem.** Een functionaris vraagt "houden wij ons aan de AVG?" en dat is
geen opdracht die iemand kan uitvoeren. Of hij vraagt niets, omdat hij niet weet
wat hij zou moeten vragen.

**Het artefact.** Een verzoek met een genummerde lijst en een methodeversie. De
vrager hoeft niet te weten hoe er gemeten wordt; de uitvoerder hoeft niet te
raden wat er bedoeld wordt.

> Wij toetsen deze verwerking tegen de DPE-catalogus. Graag een meting van de
> opgenomen bevindingen volgens DPE-meetmethode 1.0, met meetdatum, land van
> meting en de ruwe meetbestanden. Termijn: [datum].

Staat in [`site/register/functionaris.md`](site/register/functionaris.md), klaar
om te kopiëren.

## 2. De uitkomst

**Het probleem.** De ontwikkelaar meet en levert een JSON-bestand of een
scherminhoud met hostnamen. De functionaris kan daar niets mee, legt het opzij,
en het dossier blijft leeg. Of erger: er staat "geen bijzonderheden" in de DPIA,
terwijl er nooit iemand gekeken heeft.

**Het artefact.** Een rapport dat aan beide kanten werkt: de samenvatting is te
lezen zonder techniek, de onderbouwing staat eronder voor wie hem wil
controleren. Eén commando maakt het.

```
node repro/web/check.mjs example.nl
python3 tools/rapport.py example.nl-dpe.json --organisatie "..." > rapport.md
```

De ontwikkelaar is er tien minuten mee kwijt. De functionaris krijgt iets dat in
het dossier past en dat een collega over twee jaar nog kan lezen.

## 3. De eis

**Het probleem.** "Los de privacyproblemen op" is geen eis. Er valt over te
twisten wat het is, wanneer het klaar is en of het gelukt is. Dat is precies waar
het spoor doodloopt: iedereen is het eens dat er iets moet gebeuren, en niemand
kan vaststellen of het gebeurd is.

**Het artefact.** Een nummer, een termijn en een hermeting. Een genummerde
bevinding is niet uit te leggen als een verschil van inzicht, en de hermeting
maakt de afronding controleerbaar.

> DPE-2026-0001 herstellen voor [datum]. Aantonen met een hermeting volgens
> dezelfde methode. Bij oplevering ontvangen wij het meetbestand.

Voor nieuwe aanbestedingen hoort dezelfde zin in het bestek. Dan hoeft er
achteraf niets gerepareerd te worden.

---

## Waarom dit werkt terwijl het vorige niet werkte

**Niemand hoeft de taal van de ander te leren.** De functionaris vraagt in
nummers, de ontwikkelaar meet in techniek, en de vertaling zit in het artefact en
niet in een persoon. Dat is de reden dat het schaalt: het hangt niet af van
iemand die toevallig beide werelden kent.

**Het is controleerbaar zonder vertrouwen.** Een derde kan de meting overdoen. De
functionaris hoeft de ontwikkelaar niet te geloven en de ontwikkelaar hoeft niet
te bewijzen dat hij te vertrouwen is.

**Er valt niet over te twisten.** Een genummerde bevinding met een indicator is
aanwezig of afwezig. Bij "onvoldoende privacy waarborgen" kan iedereen zijn eigen
lezing volhouden tot de vergadering voorbij is.

**Het veroudert zichtbaar.** Elke meting heeft een datum. Een DPIA uit 2023 met
de mededeling dat alles in orde is, ziet er precies zo betrouwbaar uit als een
uit vorige week. Een meting niet.

## Wie doet wat

| | Functionaris | Ontwikkelaar of leverancier |
|---|---|---|
| Kent | de eisen en het dossier | het systeem |
| Doet | vragen, beoordelen, vastleggen | meten, herstellen, aantonen |
| Levert | de opdracht en de eis | het rapport en de hermeting |
| Hoeft niet | te meten | de wet te kennen |

De inkoper zit aan de papieren kant maar heeft de meeste invloed, want een eis in
een bestek kost niets en een herstel achteraf kost weken.

## Wat er nog steeds fout kan gaan

**De meting wordt één keer gedaan en nooit meer.** Een marketingafdeling voegt
een tag toe en de bevinding is terug zonder dat er code is gewijzigd. Herhaal bij
elke oplevering, en anders periodiek.

**De uitvoerder toetst zichzelf.** Een leverancier die zijn eigen product meet,
heeft een belang. Dat is niet meteen diskwalificerend, want de meting is na te
rekenen, maar vraag bij twijfel om de ruwe bestanden of laat het door een derde
overdoen.

**"Niet aangetroffen" wordt gelezen als goedkeuring.** Er is gekeken naar wat in
de catalogus staat, op één moment, vanuit één land. Dat staat in elk rapport en
het wordt structureel overgeslagen.
