# Audit contenutistico guida ATK-Pro v3.0.0

Data audit: 2026-05-26

Nota successiva 2026-05-26: la sotto-guida italiana `assets/it/testuali/guida_09_ricerca_assistita_ai.html` e' stata aggiunta e collegata dall'indice italiano. Restano bloccanti il riallineamento della guida principale, Traduzione OCR, GEDCOM/analisi genealogica, FAQ e percorsi di menu.

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
   - Attualmente presenta GEDCOM come modulo futuro.
   - La funzione reale apre un dialog di analisi genealogica con input universale, base GEDCOM/CSV opzionale, note paleografiche, provider IA, caveau chiavi e output `genealogia_*.ged`.
   - Il titolo pubblico puo' restare "Esportazione GEDCOM", ma il contenuto deve chiarire che nella v3 il modulo e' operativo come estrazione/analisi genealogica assistita e generazione GEDCOM.

4. Riallineare i percorsi di menu nelle sotto-guide operative.
   - `guida_03_visualizzazione_immagini.html` e `guida_04_visualizzazione_metadati.html` citano il menu "Strumenti"; nella v3 sono in `Servizi`.
   - `guida_05_ocr_avanzato.html` cita `Strumenti -> OCR Avanzato`; nella v3 e' `Servizi -> OCR Avanzato`.
   - `guida_06_traduzione.html` cita `Strumenti -> Traduzione`; nella v3 e' `Servizi -> Traduzione OCR`.

5. Aggiornare `assets/it/testuali/guida_06_traduzione.html`.
   - Non e' un placeholder vuoto, ma non descrive ancora in modo completo il dialog v3.
   - Usa il vecchio percorso `Strumenti -> Traduzione` invece di `Servizi -> Traduzione OCR`.
   - Non documenta compiutamente tipologia documento, prompt collegati, override modello, Cassaforte chiavi, pulsante `Traduci Testo ORA` e flusso reale di salvataggio TXT/DOCX.
   - Va trattata come blocco RC insieme a Ricerca assistita AI e GEDCOM/analisi genealogica.

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
| `guida_06_traduzione.html` | Bloccante | Guida parziale: manca copertura completa del dialog v3, prompt/tipologie, modello opzionale, Cassaforte e flusso reale | Riscrivere/integrare prima della RC |
| `guida_07_esportazione_gedcom.html` | Bloccante | Placeholder/futuro, non descrive il modulo reale | Riscrivere completamente |
| `guida_08_supporto_faq.html` | Da riallineare | Riferimenti a placeholder e versioni v2.x | Aggiornare FAQ v3 e supporto |

## Sequenza consigliata

1. Aggiornare prima la guida italiana, usando il codice come fonte primaria.
2. Aggiungere una nuova sotto-guida dedicata alla Ricerca assistita AI oppure trasformare la numerazione in una sequenza v3 con 9 moduli.
3. Riscrivere/integrare la guida Traduzione OCR sulla base di `src/translation_dialog.py`.
4. Riscrivere la guida GEDCOM/analisi genealogica sulla base del dialog reale.
5. Correggere i percorsi di menu e le sezioni Servizi in guida principale, guida 01 e guida 02.
6. Aggiornare FAQ e avvertenze sui provider IA.
7. Solo dopo il via libera sui contenuti italiani, propagare o riallineare le altre lingue.
8. Aggiungere un controllo automatico leggero per marker vietati o sospetti nella guida v3, evitando falsi positivi sui "placeholder" tecnici delle pagine non scaricabili.

## Criterio RC

La prima RC v3.0.0 puo' partire solo quando:

- La guida italiana non presenta piu' moduli reali come funzioni future.
- Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM sono documentate. La Ricerca assistita AI e' gia coperta nella guida italiana; Traduzione OCR e GEDCOM/analisi genealogica restano da completare.
- I percorsi di menu corrispondono alla UI attuale.
- Le sezioni su provider IA evitano informazioni commerciali o tecniche non verificate.
- `verify_document_assets.py`, `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` restano verdi.
