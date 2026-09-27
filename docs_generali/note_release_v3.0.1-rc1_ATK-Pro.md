# Note release ATK-Pro v3.0.1 RC1

Data snapshot: 2026-09-27

Questa candidata di manutenzione raccoglie le correzioni e l'hardening
realizzati dopo la pubblicazione stabile di `v3.0.0`. Non introduce nuovi
portali e non modifica la revisione del disclaimer legale.

## Contenuto della candidata

- supporto BDL multipagina tramite BookReader REST e Cantaloupe IIIF, con PDF
  ricostruito da tutti i canvas e fallback PDF REST diretto;
- recupero piu' robusto dei placeholder BDL e delle immagini IIIF v3;
- correzioni pratiche nei flussi OCR, genealogia e download dei portali;
- visualizzazione del disclaimer coerente con lo stile ATK-Pro;
- integrazioni IA ricertificate, discovery dinamica dei modelli e fallback
  conservativi;
- persistenza della configurazione irrobustita;
- gate pre-release, dipendenze e controlli di igiene consolidati.

## Perimetro escluso

SAG, Biblioteca Statale di Cremona e ASTi sono candidati della prossima
release funzionale, indicativamente `v3.1.0`. Anche le ottimizzazioni IA
strutturali restano nel relativo piano. La cassaforte per credenziali di
portali autenticati e' rinviata alla release ancora successiva.

## Versione e disclaimer

- versione applicativa e pacchetti: `3.0.1-rc1`;
- versione mostrata nell'app: `ATK-Pro v3.0.1 RC1`;
- revisione legale invariata: `v3.0.0-legal-disclaimer-2026-08-02`.

## Verifiche pre-tag

Verifiche concluse il 2026-09-27:

- `python scripts/quality_gate.py release`: PASS, 12/12 step, `907 passed` e
  `3 skipped` attesi;
- matrice Markdown/XLSX: PASS, 28 portali supportati e 38 candidati;
- coerenza versione tra applicazione, installer e workflow: PASS;
- pull request [#376](https://github.com/DanielePigoli/ATK-Pro-v3/pull/376)
  e quality gate GitHub: PASS; merge `a189817`.

## Compilazione e collaudo

Il tag annotato `v3.0.1-rc1` punta al commit `a189817` e ha prodotto sei asset:

| Piattaforma | Artefatto | SHA-256 |
| --- | --- | --- |
| Windows | `ATK-Pro-Setup-v3.0.1-rc1.exe` | `e8ea95cedb14dda93d7a474b0c3384703dd269df7e30f76ae5b7e6d1483cdfb7` |
| Windows | `ATK-Pro-v3.0.1-rc1-Windows-Portable.zip` | `95701e53e20f638f9968f7ef792ff3472ff031535b8d2ef99fbfd4c274b65f35` |
| Linux | `ATK-Pro-Linux.deb` | `e90b24bfb81df623a04b0a86ca4ead1fe59fd483d11fc20f29c37f59bfeff06b` |
| Linux | `ATK-Pro-Linux.tar.gz` | `a899adf3c2ced0848bff823837b8053abc85f01716e12c396db4882258e8eded` |
| macOS Intel | `ATK-Pro-macOS-Intel-v3.0.1-rc1.dmg` | `2d25b3e75d4a446afded7e54a9754b159e4a112f4a26d18cbfe2ab661c0cd7b3` |
| macOS Apple Silicon | `ATK-Pro-macOS-AppleSilicon-v3.0.1-rc1.dmg` | `efc3c831f4daf984322fffe27f1b9d38d8b3d50d8e156c6fa4c104c80ad4092b` |

I sidecar SHA-256 del DEB e del tarball sono pubblicati insieme agli asset. La
[pre-release GitHub](https://github.com/DanielePigoli/ATK-Pro-v3/releases/tag/v3.0.1-rc1)
risulta pubblica, non draft e correttamente marcata come pre-release.

Build del tag:

- Windows [`36346694309`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/36346694309): PASS;
- Linux [`36346694343`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/36346694343): PASS, inclusi gli smoke del binario nel workflow;
- macOS Intel e Apple Silicon [`36346694319`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/36346694319): PASS.

Smoke sugli asset pubblicati esatti:

- installer e portable Windows [`36348107912`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/36348107912): PASS, inclusi hash, 20 lingue, avvio, disinstallazione e pulizia;
- DEB e tarball Linux [`36348106596`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/36348106596): PASS, inclusi hash, installazione, avvio e purge;
- DMG macOS Intel e Apple Silicon [`36348106527`](https://github.com/DanielePigoli/ATK-Pro-v3/actions/runs/36348106527): PASS, inclusi hash, mount, architettura, firma ad-hoc e avvio su runner nativi.

Gli smoke manuali mantengono come valori predefiniti il tag e i digest della
stabile gia' certificata: per questa RC devono essere forniti esplicitamente
`v3.0.1-rc1`, i digest appena prodotti oppure il relativo `build_run_id` dove
supportato.

Esito RC: **go per la distribuzione ai beta tester**. Non e' una promozione a
`v3.0.1` stabile, che richiedera' la chiusura dei riscontri beta e una nuova
decisione esplicita.

## Limitazioni note

- le build macOS sono firmate ad-hoc e non notarizzate;
- i servizi IA richiedono credenziali dell'utente e restano soggetti a quota,
  disponibilita' e cambiamenti dei provider;
- le policy dei portali sono applicate item-level e devono essere ricontrollate
  periodicamente.
- GitHub segnala che alcune azioni `upload-artifact@v4` e
  `download-artifact@v4` basate su Node 20 vengono eseguite forzatamente con
  Node 24; l'avviso non ha causato errori, ma andra' eliminato aggiornando le
  action quando disponibile una versione compatibile.
