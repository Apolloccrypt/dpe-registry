# Wettelijk kader

Bepalingen en uitspraken hangen aan het **patroon**, niet aan het record. Een
patroon wordt één keer juridisch onderbouwd en elk record erft die onderbouwing.
Alleen wat zaakspecifiek is, staat in het record zelf.

```
 law/       bepalingen, per jurisdictie
 caselaw/   uitspraken en besluiten, met ECLI waar die bestaat
```

## Waarom bepalingen een datum en een versie hebben

Wetten veranderen. Een record uit mei 2026 hoort te verwijzen naar de tekst
zoals die op de meetdatum gold, niet naar de tekst van vandaag. Een register dat
naar de huidige versie linkt, vertelt onbedoeld iets onwaars over het verleden.

Voor Nederlands recht lossen we dat op met de git-spiegel op vrijewetgeving.nl:
die heeft per artikel een versiegeschiedenis, dus een verwijzing kan een commit
meenemen. Voor EU-recht en buitenlandse bepalingen noteren we de versie met de
datum waarop we hem hebben opgehaald.

## Verificatiestatus

Elk bestand heeft een veld `verified`. Staat dat op `false`, dan is de verwijzing
opgeschreven maar nog niet tegen de bron gecontroleerd. Zulke verwijzingen worden
op de site zichtbaar als ongecontroleerd getoond en tellen niet mee als
onderbouwing. Dat is dezelfde discipline als bij de records: liever een zichtbaar
gat dan een onzichtbare aanname.
