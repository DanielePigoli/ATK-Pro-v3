# Checklist release ATK-Pro v3.0.0

Data snapshot: 2026-09-01

Questa checklist raccoglie i criteri minimi per decidere se ATK-Pro puo' passare
da baseline pre-release a RC tecnica v3.0.0, e distingue quel passaggio da una
release pubblica multilingue completa.

## Decisione sintetica

| Stato | Esito | Motivazione |
| --- | --- | --- |
| RC tecnica v3.0.0 | RC3 in preparazione | Il codice sorgente, le 20 lingue, il supporto BDL multipagina e l’audit live rappresentativo dei 28 portali sono pronti; restano build multipiattaforma e smoke degli artefatti RC3. |
| Release pubblica multilingue completa | Go dopo RC3 | Le guide e i documenti previsti sono allineati nelle 20 lingue supportate; la promozione stabile resta subordinata allo smoke degli artefatti RC3. |
| Nuove integrazioni portali | Non bloccanti per RC | La roadmap portali e il registro tecnico sono pronti per evoluzioni progressive senza bloccare la prima RC. |

## Criteri go/no-go per RC tecnica

| Area | Stato | Criterio |
| --- | --- | --- |
| Git e branch | Go | `main` deve essere allineato a `origin/main`, senza modifiche pendenti. |
| Localizzazione UI | Go | `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` devono essere verdi. |
| Glossario HTML | Go | Ogni modifica al glossario JSON deve avere HTML allineato oppure nota esplicita di follow-up prima del merge release. |
| Documenti menu | Go | `verify_document_assets.py` deve confermare presenza e link locali per disclaimer, presentazioni e guida. |
| Guida italiana | Go con rilettura finale | La guida italiana e' la baseline v3; Ricerca assistita AI, Traduzione OCR, GEDCOM e capability dei nuovi portali italiani sono documentate. Resta consigliata una rilettura editoriale di OCR Avanzato e FAQ. |
| Altre lingue | Go | Il ciclo documentale e' completato nelle 20 lingue supportate e verificato dagli audit asset/localizzazione. |
| Disclaimer e policy portali | Go con consenso revisionato | Il disclaimer esclude scraping massivo, aggiramento login/paywall e portali commerciali chiusi; la revisione v3 deve essere accettata esplicitamente prima di installazione, aggiornamento automatico o avvio portable/bundle. Fino alla propagazione multilingue, il testo legale vincolante e' quello italiano. |
| Policy runtime D/R portali | Go con re-check periodico | `src/portal_registry.py` applica `R_OK`, `R_LIMITED`, `D_ONLY` e `VARIABLE`; `verify_portal_policy.py` controlla scadenza delle policy e genera `portal_policy_overrides.json` per aggiornamenti locali senza nuova release. |
| Portali esistenti | Go sorgente | Le 28 capability passano risoluzione manifest e decodifica live di immagini rappresentative; il controllo resta manuale e va completato con smoke sugli artefatti RC3. |
| Test tecnici | Go | Gate release del 2026-09-01: 834 test passati e 38 skip attesi; tutti gli 11 step di localizzazione, documenti, policy, igiene, compilazione e pytest sono verdi. |
| Packaging | In attesa RC3 | I workflow Windows, macOS Intel/Apple Silicon e Linux sono disponibili; tag, build, hash e smoke degli artefatti RC3 devono ancora essere completati. |
| File temporanei | Go | Audit automatico del 2026-08-01: 78.241 artefatti generati locali inventariati e ignorati; nessun artefatto generato tracciato o non coperto da `.gitignore`. |

## Suite smoke pre-RC

Gate rapido da eseguire sulle PR:

```powershell
python scripts\quality_gate.py smoke
```

Gate completo da eseguire su `main` pulito prima di una release:

```powershell
python scripts\quality_gate.py release
```

Controllo live portali, manuale e non sostitutivo dei test offline:

```powershell
python verify_portal_live_smoke.py --fetch-images --strict
```

Il comando richiede rete, usa `docs_generali/portal_live_smoke_samples.md` e
deve restare limitato a URL campione pubblici, no-login e coerenti con la
policy legale del portale.

## Verifiche manuali prima di RC

- Avvio dell'applicazione da build locale. Per RC1 Windows portable: eseguito,
  con disclaimer visualizzato e accettato.
- Apertura del menu Documenti: guida, disclaimer, presentazione progetto e presentazione autore.
- Apertura della guida italiana e delle sotto-guide principali.
- Smoke dei sei servizi: Ricerca assistita AI, Visualizzazione Immagini,
  Visualizzazione Metadati JSON, OCR Avanzato, Traduzione OCR, Esportazione
  GEDCOM.
- Selezione portale e verifica degli avvisi per portali a cautela o da non
  estendere.
- Compilazione degli URL campione in `docs_generali/portal_live_smoke_samples.md`
  ed esecuzione dello smoke live dei portali implementati.
- Controllo che non siano inclusi file temporanei, lock file, output di test o
  log locali.
- Conferma che gli artefatti locali ignorati non siano necessari alla build o
  alla documentazione pubblica.
- Conferma che installer Windows, portable Windows, DMG/app macOS, pacchetto
  DEB, tarball Linux e aggiornamento automatico richiedano la revisione corrente
  del disclaimer prima di procedere.

## RC1 artefatti pubblicati

Artefatto portable generato e validato:

- `ATK-Pro_v3.0.0-rc1_windows-portable.zip`
- SHA256:
  `52F05680C8FD0030AF8D55A58234B8B40FDF72403D9CC1FFD4A9A0C8CACAE111`

Installer Windows generato:

- `ATK-Pro-Setup-v3.0.0-rc1.exe`
- SHA256:
  `A60B4FEC0BF38C453BA39A96D64D63F6A75AE60FF47A7028CB37FBD2D2555DA9`

DMG macOS pubblicati:

- `ATK-Pro-macOS-Intel-v3.0.0-rc1.dmg`
- SHA256:
  `C1DC01CDF5FA907044CDE12C7479FF8EA8409B3D0E73AC46E080B077A5EA6979`
- `ATK-Pro-macOS-AppleSilicon-v3.0.0-rc1.dmg`
- SHA256:
  `99AB294F390A1694C24A1036405715B56CF4198013E2F8CF82BCDC25A4CC4307`

Artefatti Linux pubblicati:

- `ATK-Pro-Linux.deb`
- SHA256:
  `B26A536861ED308711519D5916533B3896C0BB532628E3440A00F32F79579408`
- `ATK-Pro-Linux.tar.gz`
- SHA256:
  `AC6A399265052A580717E2DAC0D98B03FC518631FE8743C8E9C40976EA6751EA`

Smoke manuale superato su:

- Antenati documento.
- BUB Castenaso 1933 con range limitato.
- Biblioteca Digitale Lombarda PDF.
- Biblioteca Digitale Trentina PDF.

Documento collegato: `docs_generali/note_release_v3.0.0-rc1_ATK-Pro.md`.

## RC2 hotfix

RC2 aggiorna la RC1 con:

- correzione dell'errore Ricerca Assistita AI `cannot access local variable 'json'`;
- merge OCR Gemini TOP/BOTTOM piu' robusto contro doppioni nell'area
  sovrapposta e perdita di colonne finali.

## Consolidamento tecnico eseguito dopo RC2

Verifica interna rieseguita il 2026-06-30:

- `python -m pytest tests\test_effective_record_portal_policy.py tests\test_translation_processor.py tests\test_ai_ocr_regressions.py tests\test_portal_live_smoke_matrix.py tests\test_bub_technical_probe.py tests\test_ficlit_technical_probe.py tests\test_bdt_technical_probe.py tests\test_bdl_technical_probe.py tests\test_rovereto_technical_probe.py -q`
  -> `50 passed`
- `python verify_portal_policy.py` -> esito OK
- `python verify_portal_live_smoke.py --fetch-manifest --strict --only antenati --only bub_digitale --only dl_ficlit --only biblioteca_digitale_trentina --only biblioteca_digitale_lombarda --only rovereto_digital_library`
  -> tutti PASS:
  - Antenati: 34 canvas
  - BUB: 32 canvas
  - FICLIT: 239 canvas
  - BDT: 508 canvas (manifest sintetico)
  - BDL: 1 canvas/documento PDF sintetico
  - Rovereto: 129 canvas (manifest sintetico)

Questo chiude il perimetro tecnico interno della Fase 1 punto 5. Eventuali
conferme manuali esterne sui casi Gemini gia' registrati restano utili ma non
sono piu' considerate prerequisito di avanzamento.

Documento collegato: `docs_generali/note_release_v3.0.0-rc2_ATK-Pro.md`.

Registro riscontri tester collegato:
`docs_generali/registro_riscontri_tester_v3.0.0-rc2_ATK-Pro.md`.

## Preparazione RC3 e bloccanti per la stabile

Il consolidamento RC3 include BDL multipagina via BookReader/Cantaloupe con
fallback PDF REST, completamento delle 20 lingue, preflight adattivo dei
percorsi, correzioni di resilienza e audit live con immagini reali. Il
2026-09-01 l'audit ha verificato 28/28 portali: manifest valido e campioni
inizio/centro/fine decodificabili e distinti quando il volume e' multipagina.

Restano bloccanti per la promozione a `v3.0.0` stabile:

- build RC3 Windows installer/portable, macOS Intel/Apple Silicon e Linux;
- hash e smoke degli artefatti, con nota esplicita per piattaforme non provate
  su hardware reale;
- tag e pacchetti generati da `main` pulito dopo CI verde;
- nessun regressivo bloccante emerso nel ciclo di prova RC3.

## Documenti collegati

- `docs_generali/audit_contenuti_guida_v3_ATK-Pro.md`
- `docs_generali/audit_post_localizzazione_ATK-Pro.md`
- `docs_generali/roadmap_portali_ATK-Pro.md`
- `docs_generali/matrice_portali_esistenti_ATK-Pro.md`
- `docs_generali/matrice_portali_candidati_ATK-Pro.md`
- `docs_generali/portal_live_smoke_samples.md`
- `docs_generali/piano_consolidamento_post_rc_v3_ATK-Pro.md`
- `tests/roadmap_tests.md`
- `docs_generali/note_release_v3.0.0-rc1_ATK-Pro.md`
- `docs_generali/note_release_v3.0.0-rc2_ATK-Pro.md`
- `docs_generali/note_release_v3.0.0-rc3_ATK-Pro.md`
