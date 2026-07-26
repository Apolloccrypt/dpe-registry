# Meedoen

Dit register bestaat bij de gratie van mensen die zelf meten. Je hoeft geen
onderzoeker te zijn en geen jurist. Hieronder staan vier manieren om bij te
dragen, van twee minuten tot een middag.

Wat je in alle gevallen terugkrijgt: je naam blijft aan het record hangen, met
de rol die je had, permanent en citeerbaar. Wil je dat niet, dan word je
gecrediteerd als `anonymous` en verandert er verder niets.

---

## Eerst dit: jij levert een meting, wij dragen de publicatie

Dit is de belangrijkste afspraak en hij staat bewust bovenaan.

Wie een bevinding meldt, levert een meting aan. Het register beoordeelt die,
doet het wederhoor bij de betrokken partij, en publiceert onder eigen naam. De
melder is niet de uitgever. Krijgt een record tegenwind, dan komt die bij het
register terecht en niet bij jou.

Daarom ook: **anoniem melden mag altijd.** Werk je bij de organisatie die je
meldt, gebruik dan gerust die route. Wij vragen niet door.

Wat we wel van je vragen: meet niets wat je niet mag meten. Alle checks hier
laden een openbare pagina en kijken wat die pagina zelf doet. Niet inloggen,
geen formulieren versturen, geen systemen van een ander onderzoeken. Wie dat wel
doet, doet dat niet namens dit register.

---

## 1. Reproduceren · vijf minuten · de meest waardevolle bijdrage

Dit is wat een register een register maakt. Een bevinding die alleen de
oorspronkelijke meter kan aantonen, is een bewering. Wordt hij door iemand
anders nagespeeld, dan is het een feit.

Bovendien telt het door in het record: een bevestiging door een derde tilt de
detectiekwaliteit naar `third-party-confirmed`, de hoogste trede.

```
1  open een record, bijvoorbeeld DPE-2026-0001
2  volg repro/<pattern>/MANUAL.md, of draai het script
3  open een issue met sjabloon "reproductie" en meld wat je zag
```

Ook een mislukte reproductie is waardevol, misschien nog wel meer. Komt jouw
uitkomst niet overeen, dan willen we dat weten. Vermeld erbij vanuit welk land
je hebt gemeten: consent-dialogen worden vaak per regio anders uitgeleverd, en
dat verklaart een verschil vaker dan een fout in het record.

## 2. Een nieuwe meting insturen · twintig minuten

Nog niet gemeten domeinen staan in de issues met het label `te-meten`. Claim er
een door te reageren, dan werkt niemand dubbel.

```
1  open de site in een prive-venster
2  raak de cookiebanner niet aan
3  klik de bookmarklet (repro/bookmarklet/), of leg een HAR vast
4  controleer je eigen resultaat op /verify
5  open een issue met sjabloon "nieuw voorval" en plak de JSON erin
```

Je hoeft geen nummer te kiezen, geen ernst in te schatten en geen juridische
duiding te geven. Het nummer wordt bij opname toegekend, de ernst wordt uit de
vector afgeleid, en de juridische context hangt aan het patroon en niet aan jouw
melding.

## 3. Een patroon uitschrijven · een middag

Negen patronen hebben wel records maar nog geen pagina. Een patroonpagina legt
uit wat het is, waarom het telt, hoe je het meet, wat het zou ontkrachten en
welke tegenwerping je kunt verwachten. Zie `registry/frontrun.md` als voorbeeld
en model.

Dit is de bijdrage waar het meeste denkwerk in zit en die het langst meegaat:
één keer goed geschreven, en elk volgend record erft die onderbouwing.

## 4. Een record betwisten · ook als je erin staat

Staat jouw organisatie in het register en klopt er iets niet, gebruik dan het
sjabloon "betwisting". Dat is geen klachtenformulier maar een gewone route in
het proces.

Wat er dan gebeurt: het record krijgt zichtbaar de status `disputed`, jouw
reactie komt er letterlijk in te staan, en er volgt een hercontrole. Blijkt de
bevinding onjuist, dan wordt het record ingetrokken. Het blijft dan wel staan,
met de status `withdrawn`, want een verdwenen record is niet te controleren.

---

## Wat een inzending moet bevatten

De poortwachter (`tools/validate.py`) draait op elke inzending. Wat rood wordt,
komt er niet in. Hij is er niet om je af te wijzen maar om je te vertellen wat
er nog mist.

| Wat | Waarom |
|---|---|
| een vector | de meting zelf, in vaste notatie |
| minstens één bron met datum | zonder bron geen record |
| een falsifier, en wat ervan getoetst is | wat zou dit ontkrachten, en heb je dat geprobeerd |
| de opnamecondities | schoon profiel, geen interactie, land van meting |
| het ruwe artefact | HAR of de JSON uit de bookmarklet |

Twee dingen vul je expliciet **niet** in: het nummer en het ernstlabel. Het
eerste wordt bij opname toegekend, zodat twee gelijktijdige inzendingen niet
botsen. Het tweede wordt uit de vector afgeleid met een openbare regel, zodat
niemand een label kan opschroeven of afzwakken zonder de meting te veranderen.

## Wat je terug mag verwachten

Antwoord binnen vijf werkdagen, ook als het nee is, en dan met de reden erbij.
Een inzending die blijft hangen is een fout van ons, en daar mag je ons aan
houden.
