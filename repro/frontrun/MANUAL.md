# Frontrun met de hand vaststellen

Twee minuten, geen installatie, geen programmeerwerk. Werkt in Chrome, Edge en
Firefox. Wie dit doet, heeft de bevinding zelf gezien en hoeft niemand op zijn
woord te geloven.

## Waarom een schoon venster essentieel is

Frontrun gaat over wat er gebeurt **voordat** de bezoeker de vraag beantwoordt.
Heb je die site eerder bezocht, dan staat je toestemming al in een cookie en
gedraagt de site zich anders. Een incognitovenster is daarom geen nettigheid maar
de voorwaarde waaronder de meting iets betekent.

## Stappen

1. Open een **nieuw incognitovenster** (Ctrl+Shift+N, op Mac Cmd+Shift+N).
2. Open de ontwikkelaarsconsole met **F12** en ga naar het tabblad **Network**
   (Nederlands: Netwerk).
3. Zet **Preserve log** aan en vink **Disable cache** aan.
4. Typ nu het adres van de site en druk op enter.
5. **Raak de cookiebanner niet aan.** Niet accepteren, niet weigeren, niet
   wegklikken. Alles wat je hierna ziet, gebeurde zonder dat je iets koos.
6. Typ in het filterveld bovenin: `google-analytics|googletagmanager|doubleclick|hotjar|clarity|facebook`

Zie je regels verschijnen, dan is er meetverkeer verstuurd voordat er iets is
gevraagd. Dat is Frontrun.

## Vastleggen zodat een ander het kan nakijken

- Rechtermuisknop in de lijst, **Save all as HAR with content**. Dat bestand is
  het bewijs. Een lezer kan het openen op <https://trace.playwright.dev> zonder
  iets te installeren.
- Maak een schermafdruk waarop de cookiebanner **en** de netwerkregels samen
  zichtbaar zijn. Dat de banner nog onbeantwoord is, is de helft van de bevinding.

## De cookies erbij

Tabblad **Application** (Firefox: **Storage**), dan **Cookies**. Sta je op een
naam als `_ga`, `_gid`, `_fbp` of `_hj...`, kijk dan naar de kolom **Expires**.
Staat daar een datum ruim een jaar vooruit terwijl je nog niets hebt gekozen,
dan heb je ook `maxstay` te pakken.

## Wat dit niet aantoont

Wees hier precies in, want een overtrokken claim kost je de hele bevinding.

- **Eén pagina, één locatie, één moment.** Een banner kan zich per land anders
  gedragen en tags kunnen pas op een dieper gelegen pagina laden.
- **Niets zien is geen bewijs dat er niets is.** Tags kunnen pas bij scrollen of
  bij een klik laden.
- **Een verzoek is nog geen persoonsgegeven.** Draagt het verzoek geen
  identificerende parameter en wordt er geen cookie gezet, dan is er wel verkeer
  maar is de gevolgtrekking zwakker. Kijk of er een `cid=`, `_ga=` of `tid=` in
  de URL staat.
- **Een meethost op het eigen domein.** Sommige partijen laten meetverkeer via
  hun eigen domeinnaam lopen (een CNAME). Dan lijkt het first-party terwijl het
  dat niet is. Met de hand zie je dat niet; daarvoor is het script nodig.

## Onafhankelijk laten bevestigen

Wil je het door een derde laten meten in plaats van door jezelf, gebruik dan een
publieke scanner die het resultaat permanent bewaart. Zie `../README.md`.
