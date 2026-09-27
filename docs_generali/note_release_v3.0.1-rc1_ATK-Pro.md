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
- pull request e controlli GitHub: da completare sul commit da taggare.

## Compilazione e collaudo

Il tag `v3.0.1-rc1` avvia le build Windows, Linux e macOS. I workflow devono
produrre sei asset e relativi digest:

- installer e portable ZIP Windows;
- pacchetto DEB e tarball Linux;
- DMG macOS Intel e Apple Silicon.

La release deve restare contrassegnata come pre-release. Dopo le build vanno
eseguiti gli smoke sugli artefatti esatti; run, SHA-256 ed esiti saranno
registrati in questo documento senza rinominare o ricostruire manualmente gli
asset.

Gli smoke manuali mantengono come valori predefiniti il tag e i digest della
stabile gia' certificata: per questa RC devono essere forniti esplicitamente
`v3.0.1-rc1`, i digest appena prodotti oppure il relativo `build_run_id` dove
supportato.

## Limitazioni note

- le build macOS sono firmate ad-hoc e non notarizzate;
- i servizi IA richiedono credenziali dell'utente e restano soggetti a quota,
  disponibilita' e cambiamenti dei provider;
- le policy dei portali sono applicate item-level e devono essere ricontrollate
  periodicamente.
