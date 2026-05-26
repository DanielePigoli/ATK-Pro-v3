# Audit contenutistico guida ATK-Pro v3.0.0

Data audit: 2026-05-26

Nota successiva 2026-05-26: la sotto-guida italiana `assets/it/testuali/guida_09_ricerca_assistita_ai.html` e' stata aggiunta e collegata dall'indice italiano. La guida italiana `assets/it/testuali/guida_06_traduzione.html` e' stata riallineata al dialog v3 di Traduzione OCR. La guida italiana `assets/it/testuali/guida_07_esportazione_gedcom.html` e' stata riscritta per descrivere il flusso reale di analisi genealogica/GEDCOM. La guida principale italiana e `assets/it/testuali/guida_02_operazioni_base.html` sono state aggiornate nella sezione Servizi per descrivere i sei moduli v3 come operativi. I percorsi menu residui in guida 03, 04 e 05 sono stati aggiornati da "Strumenti" a "Servizi", e le FAQ italiane sono state ripulite da riferimenti a servizi placeholder e versioni v2.x. Restano da valutare la propagazione multilingue e l'eventuale rinomina/documentazione del file esempio `input_link_base_v2.0.txt`.

## Esito sintetico

La verifica strutturale dei documenti del menu Documenti e dei link locali e' verde, ma la guida italiana non e' ancora pronta per una RC v3.0.0 dal punto di vista contenutistico.

La documentazione principale e alcune sotto-guide descrivono ancora lo stato v2.0-v2.2.x, indicano funzioni come pianificate o placeholder e usano in piu' punti il vecchio percorso di menu "Strumenti", mentre nella v3 i moduli sono esposti dal menu "Servizi". La release candidate deve quindi restare bloccata finche' almeno la guida italiana non sara' riallineata alle funzioni effettive.

## Fonti di confronto

- Menu reale applicazione: `src/main_gui_qt.py`, azioni dei menu File, Output, Servizi, Documenti e Impostazioni.
- Ricerca assistita AI: `src/RicercaAssistitaAI.py`.
- Analisi genealogica / GEDCOM: `src/genealogy_dialog.py`, `src/genealogy_prompts.py`.
- OCR avanzato: modulo aperto da `src/main_gui_qt.py` tramite `advanced_ocr`.
- Traduzione OCR: `src/translation_dialog.py`.
- Viewer immagini e metadati: `src/image_metadata_viewer.py`.
- Verifica asset/link: `verify_document_assets.py`.

## Release blocker prima di RC

1. Aggiornare la guida principale `assets/it/testuali/guida.html`.
   - La sezione Servizi e' stata riallineata ai sei moduli operativi v3.
   - Restano da ripulire riferimenti sparsi non ancora trattati, in particolare FAQ/supporto e voci storiche.
   - Cita l'esempio `input_link_base_v2.0.txt`, da valutare se mantenere come compatibilita' o rinominare/documentare meglio.

2. Documentare la Ricerca assistita AI.
   - Fatto per la guida italiana con `assets/it/testuali/guida_09_ricerca_assistita_ai.html`.
   - Il menu reale espone `Servizi -> Ricerca assistita AI`.
   - Il dialog consente query genealogica, scelta provider, modello opzionale, prompt standard, elaborazione multi-provider, note personali, salvataggio risultati testuali e HTML, e gestione del caveau chiavi.

3. Riscrivere `assets/it/testuali/guida_07_esportazione_gedcom.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il dialog di analisi genealogica con input universale, base GEDCOM/CSV opzionale, note paleografiche, provider IA, caveau chiavi e output `genealogia_*.ged`.

4. Riallineare i percorsi di menu nelle sotto-guide operative.
   - Fatto per la guida italiana: guida 03, guida 04 e guida 05 usano ora il menu `Servizi`.
   - `guida_06_traduzione.html` cita `Strumenti -> Traduzione`; nella v3 e' `Servizi -> Traduzione OCR`.

5. Aggiornare `assets/it/testuali/guida_06_traduzione.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il percorso `Servizi -> Traduzione OCR`, tipologia documento, modello opzionale, Cassaforte chiavi, pulsante `Traduci Testo ORA` e salvataggio TXT/DOCX.

6. Aggiornare `assets/it/testuali/guida_02_operazioni_base.html`.
   - Fatto per la sezione Servizi italiana.
   - La pagina descrive ora le 6 funzioni attuali: Ricerca assistita AI, Visualizzazione Immagini, Visualizzazione Metadati JSON, OCR Avanzato, Traduzione OCR, Esportazione GEDCOM.

7. Aggiornare `assets/it/testuali/guida_08_supporto_faq.html`.
   - Fatto per i riferimenti piu' critici nella guida italiana.
   - Rimane consigliata una revisione editoriale completa della FAQ, ma non risultano piu' riferimenti diretti a servizi placeholder o roadmap v2.x nei marker controllati.

8. Verificare i contenuti instabili su provider IA, modelli e costi.
   - Le guide OCR e Traduzione citano provider e modelli specifici.
   - Prima della RC conviene evitare promesse su prezzi, disponibilita' o nomi modello soggetti a variazione, oppure marcarli come esempi da verificare presso i fornitori.

## Stato per file italiano

| File | Stato | Problema principale | Azione prima di RC |
| --- | --- | --- | --- |
| `guida.html` | Parziale | Sezione Servizi riallineata; restano FAQ/supporto, riferimenti storici e possibile rinomina `input_link_base_v2.0.txt` | Completare pulizia contenutistica |
| `guida_01_installazione_configurazione.html` | Da riallineare | Albero funzionale include GEDCOM come previsione/interoperabilita' generica | Aggiornare mappa funzioni e menu |
| `guida_02_operazioni_base.html` | Riallineata in italiano | Sezione Servizi aggiornata ai sei moduli operativi v3 | Verificare propagazione futura |
| `guida_03_visualizzazione_immagini.html` | Riallineata in italiano | Percorso menu aggiornato | Verificare propagazione futura |
| `guida_04_visualizzazione_metadati.html` | Riallineata in italiano | Percorso menu aggiornato | Verificare propagazione futura |
| `guida_05_ocr_avanzato.html` | Parziale | Percorso menu aggiornato e note provider rese stabili; resta revisione piu' ampia del modulo OCR | Verificare caveau chiavi, provider e prompt in una passata dedicata |
| `guida_06_traduzione.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_07_esportazione_gedcom.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_08_supporto_faq.html` | Parziale | Rimossi riferimenti diretti a placeholder e versioni v2.x; resta revisione editoriale completa | Verificare FAQ v3 e supporto |

## Sequenza consigliata

1. Aggiornare prima la guida italiana, usando il codice come fonte primaria.
2. Aggiungere una nuova sotto-guida dedicata alla Ricerca assistita AI oppure trasformare la numerazione in una sequenza v3 con 9 moduli.
3. Completare una revisione editoriale italiana di OCR Avanzato e FAQ, senza bloccare i marker critici gia rimossi.
4. Solo dopo il via libera sui contenuti italiani, propagare o riallineare le altre lingue.
5. Aggiungere un controllo automatico leggero per marker vietati o sospetti nella guida v3, evitando falsi positivi sui "placeholder" tecnici delle pagine non scaricabili.

## Criterio RC

La prima RC v3.0.0 puo' partire solo quando:

- La guida italiana non presenta piu' moduli reali come funzioni future.
- Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM sono documentate nella guida italiana. Resta da completare il riallineamento della guida principale, delle sezioni base/FAQ e delle altre lingue.
- I percorsi di menu corrispondono alla UI attuale.
- Le sezioni su provider IA evitano informazioni commerciali o tecniche non verificate.
- `verify_document_assets.py`, `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` restano verdi.
