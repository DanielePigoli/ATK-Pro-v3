# Registro riscontri tester ATK-Pro v3.0.1 RC2

Data di preparazione: 2026-10-18

Stato: **preparazione tecnica; beta non ancora aperta**.

Canale centrale:
[#385 - Beta testing ATK-Pro v3.0.1-rc2](https://github.com/DanielePigoli/ATK-Pro-v3/issues/385).

## Origine della candidata

La RC2 corregge i riscontri `BETA-001`, `BETA-002`, `BETA-003` e
`BETA-005`-`BETA-008` della RC1. `BETA-004` era gia' stato chiuso. La PR
[#384](https://github.com/DanielePigoli/ATK-Pro-v3/pull/384) e' stata integrata
nel commit `0f46f29`.

## Baseline pre-tag

| Controllo | Stato | Evidenza |
| --- | --- | --- |
| Gate release locale | PASS | 12/12 step, 917 test passati e 3 skip attesi. |
| Gate GitHub PR | PASS | Run `39115507721`. |
| Audit dipendenze | PASS | PyMuPDF 1.27.2.3, urllib3 2.8.0 e pypdf 6.19.0. |
| Glossario e documenti | PASS | 20 lingue complete, asset e collegamenti locali validi. |
| Build Windows/Linux/macOS | Da eseguire | Richiede tag `v3.0.1-rc2`. |
| Smoke artefatti esatti | Da eseguire | Il ciclo beta resta chiuso fino al PASS. |

## Copertura beta richiesta

| Area | Priorita' | Stato esterno | Evidenza attesa |
| --- | ---: | --- | --- |
| Windows installer e portable | Alta | Da eseguire | Installazione/estrazione, versione, avvio e chiusura. |
| Disclaimer e documenti | Alta | Da eseguire | Stile HTML del disclaimer e contenuti RC2 aggiornati. |
| BDL multipagina | Alta | Da eseguire | Item 10527 e 10530 controllati pagina per pagina; incompletezza segnalata se restano placeholder. |
| Pulizia temporanei | Alta | Da eseguire | Nessuna directory vuota `_tmp_pdf_images` o `tiles_canvas_*`. |
| OCR PDF | Alta | Da eseguire | Calibrazione attiva/disattiva senza i due errori RC1. |
| Linux | Media | Da eseguire | Installazione/estrazione, avvio e rimozione. |
| macOS fisico | Media | Da eseguire | Mount, avvio, Gatekeeper e chiusura su Intel o Apple Silicon. |

## Riscontri ricevuti

Nessun riscontro RC2: il ciclo non e' ancora aperto.

## Criteri di apertura e uscita

Il ciclo puo' essere aperto solo dopo build dei sei pacchetti dal tag RC2,
pubblicazione dei digest e smoke verdi sugli asset esatti. Puo' essere proposto
per la chiusura quando non restano difetti bloccanti o alti, ogni altro
riscontro e' chiuso o rinviato consapevolmente e viene assunta una decisione
esplicita separata sulla release stabile `v3.0.1`.
