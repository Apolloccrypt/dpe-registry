# Open punten

Eerlijk bijgehouden, want een register dat zijn eigen gaten verzwijgt heeft
hetzelfde probleem als de partijen die het meet.

## Blokkerend voor publicatie

- **Repo-URL's zijn placeholders.** Elk record verwijst naar
  `github.com/OWNER/dpe-registry`. Zodra de repo bestaat: vervangen en de
  reproductiepaden pinnen op commit, zodat een geciteerde snippet niet meer kan
  veranderen onder een record dat ernaar verwijst.
- **`independent_confirmation` is overal leeg.** Dat is bewust: er zijn geen
  URL's ingevuld die niet daadwerkelijk zijn gedraaid. Nog te doen op de drie
  domeinen waar de bevindingen nog actief zijn (pgwoo.nl, pgawb.nl,
  cassatieblog.nl): een urlscan.io- en een Webbkoll-scan, en de permanente URL's
  in de records zetten. Dat is de goedkoopste manier om de bevindingen los te
  koppelen van eigen gereedschap.
- **Notificatiedatum per bevinding ontbreekt.** Het wederhoorspoor staat nu op
  dossierniveau, met de publieke reactie van 22 mei 2026 als anker. Uit het
  bronmateriaal moet blijken wanneer welke bevinding bij de partij lag.
- **Domein en naam van het register.** De records leven nu lokaal. Het schema
  gebruikt `dpe.example` als `$id`. Zolang dat niet vaststaat, kan niets
  gepubliceerd worden op een permanente URL, en de permanente URL is de kern
  van de hele opzet.

## Ontwerp, nog te beslissen

- **Vendor-records.** De grootste hefboom zit in een record tegen een product in
  plaats van tegen een deployment: een CMP-configuratie die standaard te laat
  gate't is één record met honderden getroffen sites. Het schema ondersteunt het
  (`target.kind: vendor-product`, `SC:VND`), er is er nog geen.
- **Bereik.** `reach` is nergens ingevuld. Voor overheidsdomeinen is een
  onderbouwde schatting mogelijk, voor een advocatenkantoor niet zonder bron.
  Liever leeg dan geraden.
- **Governance.** Zolang er één uitgever is, is dit een lijst en geen register.
  Het governance-document en het disclosure-beleid met vaste termijn zijn de
  goedkoopste stappen met het grootste effect op institutionele adoptie.

## Bekende beperkingen die blijven

- **Registrable-domain-benadering** in de reproductiescripts is geen volledige
  public suffix list. Genoeg voor .nl en .com, niet voor alles.
- **First-party CNAME naar een meethost** leest als first-party en wordt gemist.
  Staat als falsifier in de rules, is niet automatisch te toetsen zonder
  DNS-resolutie in de meting.
- **Eén paginalaad per meting.** Tags die pas bij scrollen of op diepere
  pagina's laden, blijven buiten beeld. Afwezigheid van een detectie is geen
  bewijs van afwezigheid, en dat staat in elke rule onder
  `does_not_establish`.
- **Samples staan nu op 1 van 1.** Volgens het eigen schema is dat een zwakke
  claim over herhaalbaarheid. Voor de drie nog actieve domeinen is dat op te
  lossen met twee extra captures op andere momenten.
