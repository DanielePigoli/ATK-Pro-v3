# Legenda risultati AI

- **Provider**: il servizio AI che ha generato la risposta (es. Claude, Gemini, ecc.)
- **Slot**: la posizione della chiave usata nel caveau per quel provider
- **Tabella**: ogni colonna corrisponde a un'informazione richiesta dal prompt (es. Portale, Motivazione, Query di esempio, Periodo, Tipo atti, Filtri/Strategie)
- Se la modalità 'tutte le risposte' è attiva, vedrai una sezione per ogni provider che ha restituito risultati utili

---

## Tabella riepilogativa provider

| Provider  | Raw                                                                      | Results | Slot |
|-----------|--------------------------------------------------------------------------|---------|------|
| Gemini    | [ERRORE]: Tutti i modelli Gemini esauriti per questa chiave (text-only). | []      | 1    |
| Gemini    | *(vedi dettagli sotto)*                                                  | [dati]  | 2    |
| Gemini    | *(vedi dettagli sotto)*                                                  | [dati]  | 2    |
| DeepSeek  | [ERRORE]: Client.__init__() got an unexpected keyword argument 'proxies' | []      | 1    |
| Claude    | *(vedi dettagli sotto)*                                                  | [dati]  | 1    |

---

## Dettaglio risposte Gemini

### 1. FamilySearch

- **Motivazione:** È il portale più importante e completo per questa ricerca. Offre accesso gratuito alle immagini digitalizzate dei registri parrocchiali di Poschiavo, microfilmati decenni fa. È la fonte primaria digitale per eccellenza.
- **Query di esempio:**  
  1. Vai su `Cerca > Catalogo`  
  2. In "Luogo", digita: `Poschiavo, Switzerland`  
  3. Clicca su `Church records` o `Registri ecclesiastici`  
  4. Seleziona la collezione: `Kirchenbuch, 1563-1937`
- **Periodo:** 1563-1937 (copre interamente il periodo richiesto)
- **Tipologia atti:**  
  - Battesimi (Taufen)  
  - Matrimoni (Heiraten, Ehen)  
  - Morti/Sepolture (Tote, Bestattungen)  
  - Cresime (Firmungen)

### 2. Archivio di Stato dei Grigioni (Staatsarchiv Graubünden)

- **Motivazione:** È l'archivio ufficiale del Cantone. Il suo portale è la fonte autorevole per sapere quali fondi esistono, anche se non tutti sono digitalizzati. Può contenere duplicati dei registri parrocchiali e, dal 1876, i registri di stato civile.
- **Query di esempio:**  
  Cerca termini come:  
  - `Registri parrocchiali Poschiavo`  
  - `Kirchenbücher Puschlav`  
  - `Zivilstandsregister Poschiavo`
- **Periodo:** Potenzialmente 1563-1900 e oltre.  
  La disponibilità online è limitata; potrebbe essere necessario consultare l'inventario per poi richiedere i documenti.
- **Tipologia atti:**  
  - Duplicati dei registri parrocchiali  
  - Registri di stato civile (nascite, matrimoni, decessi) a partire dal 1876  
  - Altri fondi archivistici (es. protocolli notarili)

### 3. Ancestry

- **Motivazione:** Grande portale commerciale con un potente motore di ricerca. Spesso indicizza record che su FamilySearch sono solo in formato immagine. Utile per trovare "agganci" rapidi, ma richiede un abbonamento per la visualizzazione completa.
- **Query di esempio:**  
  - Cognome: `Pesci*` (il `*` funge da jolly per Pescio, Pescijs, etc.)  
  - Luogo di nascita/residenza: `Poschiavo, Grigioni, Svizzera`  
  - Intervallo di anni: `1700 +/- 20`
- **Periodo:** Variabile, dipende dalle collezioni indicizzate. Spesso si sovrappone a FamilySearch, ma con il vantaggio dell'indicizzazione testuale.
- **Tipologia atti:**  
  - Registri parrocchiali e civili indicizzati  
  - Alberi genealogici di altri utenti (molto utili per trovare ricerche già fatte)  
  - Registri di emigrazione (es. verso l'America o l'Australia)

### 4. Geneanet

- **Motivazione:** Piattaforma collaborativa europea molto forte. La sua principale risorsa sono gli alberi genealogici creati dagli utenti. È molto probabile che altri ricercatori con radici a Poschiavo abbiano già pubblicato informazioni sulla famiglia Pesci.
- **Query di esempio:**  
  - Cognome: `Pescijs` (e poi `Pesci`, `Pescio`)  
  - Luogo: `Poschiavo`
- **Periodo:** Molto ampio, dal 1500 a oggi, a seconda dei dati inseriti dagli utenti.
- **Tipologia atti:**  
  - Alberi genealogici collaborativi  
  - Indici di registri parrocchiali caricati da associazioni o singoli utenti  
  - Documenti, foto e atti condivisi

---

## Dettaglio risposte Claude

### 1. Archivio di Stato dei Grigioni (StAGR) - staatsarchiv.gr.ch

- **Motivazione:** Archivio cantonale ufficiale; detiene microfilm/digitalizzazioni dei registri parrocchiali grigionesi, inclusa Poschiavo
- **Query di esempio:** `Pfarrbücher Poschiavo` oppure `San Vittore Mauro Taufbuch`
- **Periodo:** 1563-1900 (registri parrocchiali storici)
- **Tipologia atti:** Battesimi, matrimoni, decessi, cresime, stati d'anime

### 2. FamilySearch.org

- **Motivazione:** Maggiore database gratuito mondiale; partnership con archivi svizzeri; indicizzazione nomi
- **Query di esempio:** `Pescis Poschiavo Switzerland` oppure `Pesci Graubünden 1600-1800`
- **Periodo:** ~1580-1875 (parziale)
- **Tipologia atti:** Battesimi, matrimoni, sepolture (immagini + indici)

### 3. Ancestry.com

- **Motivazione:** Collezioni svizzere e emigrazione verso Italia/Americhe; utile per rami emigrati
- **Query di esempio:** `"Pescio" birth Poschiavo` oppure `Pesci Switzerland Catholic`
- **Periodo:** 1700-1900 (variabile)
- **Tipologia atti:** Registri parrocchiali, liste emigrazione, naturalizz.

### 4. Genea-Encyclopédie GR (genea.grfrq.ch/gr)

- **Motivazione:** Portale dedicato alla genealogia grigionese; trascrizioni e indici locali
- **Query di esempio:** `Pescis Poschiavo famiglia`
- **Periodo:** 1550-1850 (trascrizioni selettive)
- **Tipologia atti:** Indici battesimi, matrimoni; alberi genealogici condivisi

### 5. Portale Archivi Locali Svizzera (archivesonline.org)

- **Motivazione:** Meta-catalogo archivi svizzeri; localizza fondi specifici di Poschiavo
- **Query di esempio:** `Poschiavo Pfarrarchiv Vittore Mauro`
- **Periodo:** Guida ai fondi (non digitalizzazione diretta)
- **Tipologia atti:** Inventari, descrizioni fondi, collocazioni

### 6. Matricula Online (matricula-online.eu)

- **Motivazione:** Registri parrocchiali cattolici area alpina; alcune parrocchie grigionesi
- **Query di esempio:** `Poschiavo` (ricerca per località)
- **Periodo:** 1600-1900 (se presente)
- **Tipologia atti:** Battesimi, matrimoni, decessi (scansioni)

### 7. SSRQ - Fonti del diritto svizzero (ssrq-sds-fds.ch)

- **Motivazione:** Documenti giuridici storici; menzioni familiari in atti notarili/comunali
- **Query di esempio:** `Pescis Poschiavo Rechtsquellen`
- **Periodo:** 1400-1800
- **Tipologia atti:** Atti notarili, testamenti, contr. matrimoniali

---

## Dettaglio errori DeepSeek

- **Errore:** Client.__init__() got an unexpected keyword argument 'proxies'

---

**Nota:**  
Puoi salvare questo testo in un file `risultato_ai.md` nella stessa cartella delle note personali (`ai_search_notes.json`).  
Se vuoi includere altre sezioni o provider, puoi aggiungerle nello stesso stile.

---
