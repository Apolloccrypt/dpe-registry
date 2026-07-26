---
name: HollowNo
slug: hollowno
family: consent
first_named: 2026-07-26
schema_version: "1.0"
status: active
provisions:
  - eu-gdpr-6-1-a
  - nl-tw-11-7a
caselaw:
  - cjeu-planet49
related:
  - frontrun
  - onedoor
  - sideload
observations: 3
---

# HollowNo

**Weigeren verandert niet wat de browser verlaat.**

Er staat een banner. Je klikt weigeren. Het scherm bevestigt je keuze. En op de
lijn gebeurt precies hetzelfde als daarvoor.

## Wat het is

Een site vraagt toestemming en registreert de weigering, maar de tags die de
weigering zou moeten tegenhouden zitten er niet achter. Meestal omdat ze
hardgecodeerd in de pagina staan in plaats van achter de consent-gate, soms omdat
de consent-tool het laden van een container niet blokkeert, ook al blokkeert hij
het plaatsen van cookies.

Dit is geen theoretisch gebrek. Het is direct te meten, en de meting is
interpretatievrij.

## Waarom dit patroon apart telt

HollowNo bewijst iets wat Frontrun niet bewijst. Frontrun gaat over het moment:
er werd gemeten voordat er iets gevraagd was. HollowNo gaat over het effect: er
werd gevraagd, er werd geantwoord, en het antwoord deed niets.

Dat verschil is juridisch wezenlijk. Toestemming die niet kan worden geweigerd,
is volgens artikel 4 lid 11 en artikel 7 van de AVG geen vrije toestemming. En
een intrekking die het gedrag niet verandert, maakt artikel 7 lid 3 tot een lege
huls. Een partij kan Frontrun repareren en HollowNo laten staan, of andersom.
Daarom zijn het twee records.

## De meting: een vergelijking, geen waarneming

Dit is het sterkste bewijstype in het hele register, en de reden is dat er niets
te interpreteren valt.

```
  opname A   pagina geladen, niets aangeklikt        set hosts A
  opname B   pagina geladen, expliciet geweigerd     set hosts B

  A == B  of  B bevat nog meethosts   ->   de weigering deed niets
```

Twee opnames onder gelijke condities, met één verschil: de weigering. Vergelijk
de verzamelingen. Er is geen derde lezing.

Waar het wél mis kan gaan, en waarom de regel dat als eerste toetst: de
weigering moet daadwerkelijk zijn geregistreerd. Een klik die niet aankwam meet
je als een hollow no, terwijl je een mislukte klik hebt gemeten. Daarom leest de
regel de consent-status terug voordat hij vergelijkt.

## Hoe je het vaststelt

Zie [`repro/hollowno/`](../repro/hollowno/). Met de hand komt het hierop neer:

1. Privé-venster, devtools open op Network, **Preserve log** aan.
2. Laad de pagina, klik niets. Sla op als HAR. Dat is opname A.
3. Nieuw privé-venster. Laad de pagina, klik **weigeren**. Sla op als HAR. Dat
   is opname B.
4. Vergelijk de hosts. Staan er in B nog meethosts, dan heb je het.

Twee losse vensters, geen tabbladen: een gedeeld profiel draagt de keuze mee en
dan vergelijk je twee keer dezelfde toestand.

## Wat het weerlegt

- **De weigering is niet geregistreerd.** Getoetst door de consent-status na de
  klik terug te lezen. Dit is de belangrijkste, want hij maakt van een bevinding
  een meetfout.
- **De banner blokkeert wel, maar later dan het meetvenster.** Uit te sluiten met
  een langere wachttijd, en met de constatering of de tag hardgecodeerd in de
  bron staat: dan is er geen gate om later alsnog dicht te gaan.
- **De overgebleven verzoeken zijn strikt noodzakelijk.** Dit is een oordeel per
  host, geen meting, en het wordt daarom nooit automatisch uitgesloten. Een
  record mag met deze conditie op `untested` gepubliceerd worden, mits het dat
  zichtbaar vermeldt. Zie `DPE-2026-0008`.

## De standaardtegenwerpingen

**"Onze consent-tool regelt dit."**
Meten, niet aannemen. Cassatieblog.nl was het enige gemeten domein met een
Cookiebot-implementatie, en juist daar bleven na weigeren vijf trackers en een
script actief. De tool voorkwam cookieplaatsing vóór toestemming, maar niet het
laden van de container erachter. Een tool die één van de twee doet, doet niet
wat de bezoeker denkt dat hij doet.

**"De banner is er, dus de bezoeker heeft een keuze."**
De keuze bestaat op het scherm en niet op de lijn. Dat is precies het verwijt.
Planet49 vestigde dat toestemming een actieve handeling van de gebruiker vereist;
een handeling zonder gevolg is geen handeling in die zin.

**"Dit gaat om analytics, dat mag zonder toestemming."**
Dan zou de banner die tags niet moeten noemen, en dan is er ook geen weigering om
te honoreren. Een partij kan niet tegelijk zeggen dat iets toestemmingsplichtig
is, ervoor vragen, en de weigering negeren.

## Wat een HollowNo-record niet zegt

Het zegt niets over opzet. Een niet-werkende weigering is meestal een bouwfout en
geen kwade wil, en het record beweert het tegendeel niet. Het zegt ook niets over
de accepteer-modus: dat is een derde opname en zou een eigen record zijn.

## Records

| Record | Doelwit | Datum | Ernst | Bijzonderheid |
|---|---|---|---|---|
| [DPE-2026-0002](../observations/DPE-2026-0002.json) | pgwoo.nl | 27-05-2026 | high | banner sinds 2022, niet gekoppeld aan de tags |
| [DPE-2026-0005](../observations/DPE-2026-0005.json) | pgawb.nl | 27-05-2026 | high | banner sinds 2017, geen weigeroptie |
| [DPE-2026-0008](../observations/DPE-2026-0008.json) | cassatieblog.nl | 27-05-2026 | high | Cookiebot aanwezig, vijf trackers overleven de weigering |
