# Publicatiebeleid

Dit beleid bestaat om twee redenen. De eerste: een partij hoort te weten wat er
over haar gepubliceerd wordt voordat het gebeurt. De tweede: zonder vaste
termijnen verwijst geen enkele instelling naar dit register, en dan heeft het
geen nut.

## De termijnen

```
 dag 0     bevinding gemeten en opgenomen als concept
 dag 0     partij geïnformeerd, met het volledige record en het ruwe bewijs
 dag 30    publicatie, tenzij hieronder iets anders staat
```

Dertig dagen is de standaard. Dat is korter dan bij softwarekwetsbaarheden, waar
negentig dagen gebruikelijk is, en dat verschil is opzettelijk: een tag
uitschakelen is geen patch bouwen, testen en uitrollen. Wie meer tijd nodig heeft
en dat onderbouwt, krijgt die.

**Eerder publiceren** gebeurt alleen als de bevinding al elders openbaar is, of
als de partij zelf publiek over de zaak spreekt. In dat laatste geval is er geen
reden meer om het record achter te houden.

**Later publiceren** gebeurt als de partij een concreet herstelplan met datum
levert. Dan wordt de termijn verlengd tot die datum plus zeven dagen. Eén keer.

**Geen reactie** is geen blokkade. Na dertig dagen wordt gepubliceerd, met
`response: silent` in het record. Dat de partij niet reageerde, is zelf een feit
dat in het dossier hoort.

## Wat de partij krijgt

Niet alleen een melding. Het volledige record zoals het gepubliceerd zou worden,
plus het ruwe bewijs, plus de reproductie-instructies. Wie wil controleren of wij
gelijk hebben, moet dat kunnen doen zonder ons iets te hoeven vragen.

Daar hoort ook de vraag bij of er iets ontbreekt of verkeerd is begrepen. Die
vraag is echt gemeend: een fout die vóór publicatie wordt gevonden, kost niemand
iets.

## Wat de partij niet kan

- **Publicatie tegenhouden** door niet te reageren of door te dreigen.
- **De meting laten verwijderen** omdat het inmiddels is opgelost. Dan wordt de
  status `resolved` en blijft zichtbaar dat het er was, met de datum waarop het
  verdween. Dat is de kern van een register: een tijdlijn, geen momentopname.
- **Onderhandelen over de ernst.** Die volgt uit de vector met een openbare
  regel. Wie de ernst wil veranderen, moet aantonen dat de meting niet klopt.

## Als een record onjuist blijkt

Dan wordt het ingetrokken. Het blijft staan met de status `withdrawn`, de reden
erbij en de correctie in het wijzigingsspoor. Records verdwijnen niet, want een
verdwenen record is niet te controleren en elders staan er verwijzingen naar.

Dit is geen theorie. Correcties zijn eerder voorgekomen in het onderzoek waar dit
register uit voortkomt, en de reden dat het wijzigingsspoor append-only is en de
betwistingsroute een gewoon sjabloon in plaats van een uitzondering.

## Voor melders

Wie een bevinding aanlevert, is niet de uitgever. Het register doet het
wederhoor, publiceert onder eigen naam en draagt de publicatie. Zie
`CONTRIBUTING.md`.

Meld nooit iets wat je niet mocht meten. Alle checks in dit register laden een
openbare pagina en kijken wat die pagina zelf doet: niet inloggen, geen
formulieren versturen, geen systemen van een ander onderzoeken. Dat is niet
alleen een juridische grens maar ook een methodische: wat achter een login zit,
is niet reproduceerbaar door een derde, en dan kan het geen record worden.

## Contact

Meldingen en betwistingen lopen via de sjablonen in de issues, zodat het spoor
publiek is. Moet het vertrouwelijk, gebruik dan het adres in `SECURITY.md`.
