# Audit contenutistico guida ATK-Pro v3.0.0

Data audit: 2026-05-26

Nota successiva 2026-05-26: la sotto-guida italiana `assets/it/testuali/guida_09_ricerca_assistita_ai.html` e' stata aggiunta e collegata dall'indice italiano. La guida italiana `assets/it/testuali/guida_06_traduzione.html` e' stata riallineata al dialog v3 di Traduzione OCR. La guida italiana `assets/it/testuali/guida_07_esportazione_gedcom.html` e' stata riscritta per descrivere il flusso reale di analisi genealogica/GEDCOM. Restano bloccanti il riallineamento della guida principale, FAQ e percorsi di menu residui.

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
   - Contiene ancora riferimenti a funzioni future, placeholder e stato v2.0-v2.2.x.
   - Cita l'esempio `input_link_base_v2.0.txt`, da valutare se mantenere come compatibilita' o rinominare/documentare meglio.
   - La sezione Servizi non rappresenta lo stato reale della v3: oggi il menu contiene 6 funzioni operative, inclusa Ricerca assistita AI.

2. Documentare la Ricerca assistita AI.
   - Fatto per la guida italiana con `assets/it/testuali/guida_09_ricerca_assistita_ai.html`.
   - Il menu reale espone `Servizi -> Ricerca assistita AI`.
   - Il dialog consente query genealogica, scelta provider, modello opzionale, prompt standard, elaborazione multi-provider, note personali, salvataggio risultati testuali e HTML, e gestione del caveau chiavi.

3. Riscrivere `assets/it/testuali/guida_07_esportazione_gedcom.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il dialog di analisi genealogica con input universale, base GEDCOM/CSV opzionale, note paleografiche, provider IA, caveau chiavi e output `genealogia_*.ged`.

4. Riallineare i percorsi di menu nelle sotto-guide operative.
   - `guida_03_visualizzazione_immagini.html` e `guida_04_visualizzazione_metadati.html` citano il menu "Strumenti"; nella v3 sono in `Servizi`.
   - `guida_05_ocr_avanzato.html` cita `Strumenti -> OCR Avanzato`; nella v3 e' `Servizi -> OCR Avanzato`.
   - `guida_06_traduzione.html` cita `Strumenti -> Traduzione`; nella v3 e' `Servizi -> Traduzione OCR`.

5. Aggiornare `assets/it/testuali/guida_06_traduzione.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il percorso `Servizi -> Traduzione OCR`, tipologia documento, modello opzionale, Cassaforte chiavi, pulsante `Traduci Testo ORA` e salvataggio TXT/DOCX.

6. Aggiornare `assets/it/testuali/guida_02_operazioni_base.html`.
   - Descrive il menu Servizi come 5 funzioni con una pianificata.
   - Deve essere riallineata alle 6 funzioni attuali: Ricerca assistita AI, Visualizzazione Immagini, Visualizzazione Metadati JSON, OCR Avanzato, Traduzione OCR, Esportazione GEDCOM.

7. Aggiornare `assets/it/testuali/guida_08_supporto_faq.html`.
   - Contiene riferimenti a servizi placeholder e a tempi/versioni v2.1-v2.3.
   - Deve diventare una FAQ v3, con indicazione chiara delle funzioni effettive e dei limiti reali.

8. Verificare i contenuti instabili su provider IA, modelli e costi.
   - Le guide OCR e Traduzione citano provider e modelli specifici.
   - Prima della RC conviene evitare promesse su prezzi, disponibilita' o nomi modello soggetti a variazione, oppure marcarli come esempi da verificare presso i fornitori.

## Stato per file italiano

| File | Stato | Problema principale | Azione prima di RC |
| --- | --- | --- | --- |
| `guida.html` | Bloccante | Stato v2.x, placeholder/future, Servizi non allineati | Riscrivere panoramica v3 e indice |
| `guida_01_installazione_configurazione.html` | Da riallineare | Albero funzionale include GEDCOM come previsione/interoperabilita' generica | Aggiornare mappa funzioni e menu |
| `guida_02_operazioni_base.html` | Bloccante | Servizi descritti come 5 funzioni, una futura | Aggiornare sezione Servizi v3 |
| `guida_03_visualizzazione_immagini.html` | Parziale | Percorso menu vecchio | Correggere menu e verificare controlli |
| `guida_04_visualizzazione_metadati.html` | Parziale | Percorso menu vecchio | Correggere menu e verificare relazione immagine/JSON |
| `guida_05_ocr_avanzato.html` | Da verificare | Percorso menu vecchio e possibili dettagli provider/modelli instabili | Aggiornare menu, caveau chiavi, provider e disclaimer operativo |
| `guida_06_traduzione.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_07_esportazione_gedcom.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_08_supporto_faq.html` | Da riallineare | Riferimenti a placeholder e versioni v2.x | Aggiornare FAQ v3 e supporto |

## Sequenza consigliata

1. Aggiornare prima la guida italiana, usando il codice come fonte primaria.
2. Aggiungere una nuova sotto-guida dedicata alla Ricerca assistita AI oppure trasformare la numerazione in una sequenza v3 con 9 moduli.
3. Correggere i percorsi di menu e le sezioni Servizi in guida principale, guida 01 e guida 02.
4. Aggiornare FAQ e avvertenze sui provider IA.
5. Solo dopo il via libera sui contenuti italiani, propagare o riallineare le altre lingue.
6. Aggiungere un controllo automatico leggero per marker vietati o sospetti nella guida v3, evitando falsi positivi sui "placeholder" tecnici delle pagine non scaricabili.

## Criterio RC

La prima RC v3.0.0 puo' partire solo quando:

- La guida italiana non presenta piu' moduli reali come funzioni future.
- Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM sono documentate nella guida italiana. Resta da completare il riallineamento della guida principale, delle sezioni base/FAQ e delle altre lingue.
- I percorsi di menu corrispondono alla UI attuale.
- Le sezioni su provider IA evitano informazioni commerciali o tecniche non verificate.
- `verify_document_assets.py`, `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` restano verdi.
