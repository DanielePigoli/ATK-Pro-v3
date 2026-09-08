# Note release ATK-Pro v3.0.0

Data snapshot: 2026-09-08

ATK-Pro v3.0.0 e' la prima release stabile della serie 3. Nasce dalla RC4,
validata sui sei artefatti Windows, Linux e macOS, e viene ricostruita con
versione finale prima della pubblicazione.

## Funzioni principali

- Download e ricostruzione locale da 28 portali pubblici supportati, nel
  rispetto delle policy `R_OK`, `R_LIMITED`, `D_ONLY` e `VARIABLE`.
- Biblioteca Digitale Lombarda multipagina tramite BookReader/Cantaloupe IIIF,
  con ricostruzione PDF da tutti i canvas, retry e fallback PDF REST.
- Visualizzazione immagini e metadati, OCR avanzato, traduzione OCR, ricerca
  assistita AI ed esportazione GEDCOM.
- Interfaccia, glossario e documentazione in 20 lingue, con 9 moduli guida per
  lingua.
- Preflight adattivo dei percorsi di output e cancellazione batch
  transazionale.

## Correzioni consolidate

- Recupero BDL multipagina e riduzione dei placeholder mediante retry mirati.
- Header corretti per le immagini Antenati.
- Pulizia completa del pacchetto Debian durante `apt purge`, senza rimuovere
  file sconosciuti o configurazioni utente.
- Smoke ripetibili sugli asset pubblicati per installer e portable Windows,
  DEB e tar Linux, DMG Intel e Apple Silicon.

## Baseline verificata

Il sorgente stabile ha superato il gate release locale: 838 test passati,
39 skip attesi e 11/11 step verdi.

RC4 ha inoltre superato:

- build Windows, Linux e macOS;
- verifica dei digest di tutti i sei asset;
- installazione, avvio e disinstallazione dell'installer Windows;
- estrazione, 20 lingue/locales e avvio del portable Windows;
- installazione DEB, avvio DEB/tar e purge pulito;
- integrita', architettura e avvio dei DMG su runner nativi Intel e ARM.

Rapporto completo:
[`note_release_v3.0.0-rc4_ATK-Pro.md`](note_release_v3.0.0-rc4_ATK-Pro.md).

## Artefatti stabili

La release resta draft fino al completamento di build e smoke degli asset
`v3.0.0`. Nomi, SHA-256 e collegamenti ai run saranno aggiunti prima della
pubblicazione.

## Limitazioni note

- Le build macOS sono firmate ad-hoc e non notarizzate; macOS puo' richiedere
  una conferma esplicita dell'utente al primo avvio.
- I portali esterni possono modificare endpoint, policy o disponibilita';
  l'applicazione applica limiti prudenziali e il registro policy deve essere
  ricontrollato periodicamente.
- OCR, traduzioni e risultati AI richiedono verifica sulle fonti originali.

## Licenze e responsabilita'

Il codice e' distribuito secondo GNU AGPL v3 o successiva. La documentazione
originale e' distribuita secondo CC BY-NC-SA 4.0, salvo diversa indicazione.
Nome, logo e segni distintivi restano disciplinati da `TRADEMARKS.md`.

L'uso del software richiede l'accettazione del disclaimer legale revisione
`v3.0.0-legal-disclaimer-2026-08-02`.
