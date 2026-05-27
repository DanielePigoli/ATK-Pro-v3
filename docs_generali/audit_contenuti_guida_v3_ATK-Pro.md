# Audit contenutistico guida ATK-Pro v3.0.0

Data audit: 2026-05-26

Nota successiva 2026-05-26: la sotto-guida italiana `assets/it/testuali/guida_09_ricerca_assistita_ai.html` e' stata aggiunta e collegata dall'indice italiano. La guida italiana `assets/it/testuali/guida_06_traduzione.html` e' stata riallineata al dialog v3 di Traduzione OCR. La guida italiana `assets/it/testuali/guida_07_esportazione_gedcom.html` e' stata riscritta per descrivere il flusso reale di analisi genealogica/GEDCOM. La guida principale italiana e `assets/it/testuali/guida_02_operazioni_base.html` sono state aggiornate nella sezione Servizi per descrivere i sei moduli v3 come operativi. I percorsi menu residui in guida 03, 04 e 05 sono stati aggiornati al menu attuale, e le FAQ italiane sono state ripulite dai riferimenti obsoleti individuati. Il file esempio `input_link_base_v2.0.txt` e' stato documentato come nome storico mantenuto per compatibilita'. Resta da valutare la propagazione multilingue.

Nota successiva 2026-05-27: `assets/it/testuali/guida.html` e' stato riportato alla funzione corretta di indice modulare. Il corpo operativo duplicato e' stato rimosso dalla guida principale, lasciando il contenuto dettagliato nei file `guida_01...guida_09`. Il verificatore `verify_italian_guide_content.py` ora controlla che l'indice linki tutti i moduli italiani e non torni a contenere blocchi estesi duplicati.

## Esito sintetico aggiornato

La verifica strutturale dei documenti del menu Documenti e dei link locali e' verde. Dopo gli interventi successivi all'audit iniziale, la guida italiana copre ora i tre blocchi che erano release blocker immediati: Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM.

La scansione dei marker critici sulla guida italiana non trova piu' riferimenti obsoleti nei file trattati. Per una RC tecnica la guida italiana puo' essere trattata come fonte v3 primaria; restano da valutare una revisione editoriale di OCR Avanzato e FAQ, e soprattutto la propagazione o dichiarazione di stato per le altre lingue prima di una release pubblica multilingue completa.

## Fonti di confronto

- Menu reale applicazione: `src/main_gui_qt.py`, azioni dei menu File, Output, Servizi, Documenti e Impostazioni.
- Ricerca assistita AI: `src/RicercaAssistitaAI.py`.
- Analisi genealogica / GEDCOM: `src/genealogy_dialog.py`, `src/genealogy_prompts.py`.
- OCR avanzato: modulo aperto da `src/main_gui_qt.py` tramite `advanced_ocr`.
- Traduzione OCR: `src/translation_dialog.py`.
- Viewer immagini e metadati: `src/image_metadata_viewer.py`.
- Verifica asset/link: `verify_document_assets.py`.

## Stato dei blocchi iniziali

1. Guida principale `assets/it/testuali/guida.html`.
   - Riallineata come indice/portale della guida italiana.
   - Linka i nove moduli sezionali e contiene solo sommari brevi, stato guida e perimetro v3.
   - Il corpo operativo resta nei file sezionali dedicati, evitando duplicazioni.

2. Ricerca assistita AI.
   - Fatto per la guida italiana con `assets/it/testuali/guida_09_ricerca_assistita_ai.html`.
   - Il menu reale espone `Servizi -> Ricerca assistita AI`.
   - Il dialog consente query genealogica, scelta provider, modello opzionale, prompt standard, elaborazione multi-provider, note personali, salvataggio risultati testuali e HTML, e gestione del caveau chiavi.

3. `assets/it/testuali/guida_07_esportazione_gedcom.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il dialog di analisi genealogica con input universale, base GEDCOM/CSV opzionale, note paleografiche, provider IA, caveau chiavi e output `genealogia_*.ged`.

4. Percorsi di menu nelle sotto-guide operative.
   - Fatto per la guida italiana: guida 03, guida 04 e guida 05 usano ora il menu `Servizi`.
   - `guida_06_traduzione.html` usa ora `Servizi -> Traduzione OCR`.

5. `assets/it/testuali/guida_06_traduzione.html`.
   - Fatto per la guida italiana.
   - La pagina ora descrive il percorso `Servizi -> Traduzione OCR`, tipologia documento, modello opzionale, Cassaforte chiavi, pulsante `Traduci Testo ORA` e salvataggio TXT/DOCX.

6. `assets/it/testuali/guida_02_operazioni_base.html`.
   - Fatto per la sezione Servizi italiana.
   - La pagina descrive ora le 6 funzioni attuali: Ricerca assistita AI, Visualizzazione Immagini, Visualizzazione Metadati JSON, OCR Avanzato, Traduzione OCR, Esportazione GEDCOM.

7. `assets/it/testuali/guida_08_supporto_faq.html`.
   - Fatto per i riferimenti piu' critici nella guida italiana.
   - Rimane consigliata una revisione editoriale completa della FAQ, ma non risultano piu' riferimenti diretti ai marker obsoleti controllati.

8. Contenuti instabili su provider IA, modelli e costi.
   - Le guide OCR e Traduzione citano provider e modelli specifici.
   - Le promesse piu' specifiche su costi/modelli sono state rese piu' prudenti nei passaggi gia fatti.
   - Prima della RC resta consigliata una rilettura editoriale, evitando promesse su prezzi, disponibilita' o nomi modello soggetti a variazione.

## Stato per file italiano

| File | Stato | Problema principale | Azione prima di RC |
| --- | --- | --- | --- |
| `guida.html` | Riallineata come indice | La guida principale non duplica piu' i moduli sezionali; linka `guida_01...guida_09` | Verificare propagazione futura |
| `guida_01_installazione_configurazione.html` | Parziale | Mappa funzioni aggiornata nei marker critici; resta revisione editoriale complessiva | Rilettura finale |
| `guida_02_operazioni_base.html` | Riallineata in italiano | Sezione Servizi aggiornata ai sei moduli operativi v3 | Verificare propagazione futura |
| `guida_03_visualizzazione_immagini.html` | Riallineata in italiano | Percorso menu aggiornato | Verificare propagazione futura |
| `guida_04_visualizzazione_metadati.html` | Riallineata in italiano | Percorso menu aggiornato | Verificare propagazione futura |
| `guida_05_ocr_avanzato.html` | Parziale | Percorso menu aggiornato e note provider rese stabili; resta revisione piu' ampia del modulo OCR | Verificare caveau chiavi, provider e prompt in una passata dedicata |
| `guida_06_traduzione.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_07_esportazione_gedcom.html` | Riallineata in italiano | Copertura aggiornata al dialog v3; resta da propagare alle altre lingue quando si fara' il riallineamento multilingue | Verificare link e propagazione futura |
| `guida_08_supporto_faq.html` | Parziale | Rimossi riferimenti diretti a placeholder e versioni v2.x; resta revisione editoriale completa | Verificare FAQ v3 e supporto |

## Sequenza consigliata

1. Completare una revisione editoriale italiana di OCR Avanzato e FAQ, senza blocchi critici gia rimossi.
2. Propagare o riallineare le altre lingue, oppure dichiarare esplicitamente che la guida italiana e' la fonte v3 primaria fino alla traduzione completa.
3. Aggiungere un controllo automatico leggero per marker vietati o sospetti nella guida v3, evitando falsi positivi sui "placeholder" tecnici delle pagine non scaricabili.

## Criterio RC

La prima RC v3.0.0 puo' partire quando:

- La guida italiana non presenta piu' moduli reali come funzioni future.
- Ricerca assistita AI, Traduzione OCR e analisi genealogica/GEDCOM sono documentate nella guida italiana.
- I percorsi di menu corrispondono alla UI attuale.
- Le sezioni su provider IA evitano informazioni commerciali o tecniche non verificate.
- La guida principale resta un indice modulare e non duplica il contenuto dei file sezionali.
- E' chiaro lo stato delle altre lingue: aggiornate, oppure esplicitamente dichiarate come traduzioni da riallineare dopo la fonte italiana.
- `verify_document_assets.py`, `verify_localization.py`, `validate_glossary.py` e `verify_glossary.py` restano verdi.
