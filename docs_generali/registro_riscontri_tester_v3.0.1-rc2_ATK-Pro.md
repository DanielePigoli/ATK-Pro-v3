# Registro riscontri tester ATK-Pro v3.0.1 RC2

Data di preparazione: 2026-10-18

Stato: **beta aperta il 2026-10-18**.

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
| Build Windows/Linux/macOS | PASS | Windows `39116175957`; Linux `39116175927`; Apple Silicon `39116175937`; Intel `39142108315`. |
| Smoke artefatti esatti | PASS | Windows `39140405180`; Linux `39139836881`; macOS Intel e Apple Silicon `39143937457`. |

## Copertura beta richiesta

| Area | Priorita' | Stato esterno | Evidenza attesa |
| --- | ---: | --- | --- |
| Windows installer e portable | Alta | CI PASS; prova tester richiesta | Installazione/estrazione, versione, avvio, chiusura e disinstallazione. |
| Disclaimer e documenti | Alta | Da eseguire | Stile HTML del disclaimer e contenuti RC2 aggiornati. |
| BDL multipagina | Alta | Da eseguire | Item 10527 e 10530 controllati pagina per pagina; incompletezza segnalata se restano placeholder. |
| Pulizia temporanei | Alta | Da eseguire | Nessuna directory vuota `_tmp_pdf_images` o `tiles_canvas_*`. |
| OCR PDF | Alta | Runtime frozen Windows PASS; prova funzionale richiesta | Calibrazione attiva/disattiva senza i due errori RC1. |
| Linux | Media | CI PASS; prova tester facoltativa | Installazione/estrazione, avvio e rimozione. |
| macOS fisico | Media | CI Intel/Apple Silicon PASS; prova fisica richiesta | Mount, avvio, Gatekeeper e chiusura su Intel o Apple Silicon. |

## Riscontri ricevuti

Nessun riscontro RC2 al momento dell'apertura del ciclo.

## Artefatti pubblicati

| Asset | SHA-256 |
| --- | --- |
| `ATK-Pro-Setup-v3.0.1-rc2.exe` | `18d2c5819cbb1c8fb1cac2626a433b43392ffa7ab1c99cd87eb5b7325cc08bbf` |
| `ATK-Pro-v3.0.1-rc2-Windows-Portable.zip` | `5672b2a5b01a95e8d44cb647e4d9f707c3188389f0c9a0ffbc2eb822f547b51b` |
| `ATK-Pro-Linux.deb` | `5318b0b28736bff4c165f1a5a1cf8e109ad6ea98c4d5a676257d146fdd72938e` |
| `ATK-Pro-Linux.tar.gz` | `ba26ee9ce713f81f556e9dbe768c3bf832b77e6049620c280280250d9580d853` |
| `ATK-Pro-macOS-Intel-v3.0.1-rc2.dmg` | `12348449c37ca781f2b54dc71e8e0bea5d86c8b83b5e7c45f25e9d0f18936e30` |
| `ATK-Pro-macOS-AppleSilicon-v3.0.1-rc2.dmg` | `f8d865856cd3aaba8af6671063eeff94acd15423af9749b3294098da0f2165a2` |

## Criteri di apertura e uscita

Il criterio di apertura e' soddisfatto: i sei pacchetti sono stati costruiti
dal tag RC2, i digest sono pubblicati e gli smoke sugli asset esatti sono
verdi. Il ciclo puo' essere proposto per la chiusura quando non restano difetti
bloccanti o alti, ogni altro
riscontro e' chiuso o rinviato consapevolmente e viene assunta una decisione
esplicita separata sulla release stabile `v3.0.1`.
