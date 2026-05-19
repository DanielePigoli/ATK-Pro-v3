# Changelog

Tutte le modifiche rilevanti al progetto ATK-Pro saranno documentate in questo file.

## [3.0.0] - 2026-05-10
Questa release trasforma profondamente ATK-Pro, facendolo evolvere da un downloader specifico per il Portale Antenati a un **Motore Genealogico Universale** (sia per il download di immagini IIIF da archivi internazionali, sia per l'estrazione AI multi-provider).

### ✨ Nuove Funzionalità (New Features)
* **Downloader IIIF Universale**: ATK-Pro ora supporta nativamente lo scaricamento da oltre 15 portali genealogici e archivistici internazionali:
  * *Francia*: Gallica (BnF) con bypass TLS/Playwright.
  * *Regno Unito*: Bodleian Libraries (Oxford).
  * *Europa Centrale*: Matricula Online (AT/DE/PL) e Findbuch (Südtirol).
  * *Vaticano*: DigiVatLib (Archivio Apostolico Vaticano).
  * *Svizzera*: e-codices, e-rara, e-manuscripta.
  * *Italia/ICCU*: Biblioteca Estense, BNC Roma, Brixiana, Memooria, Museo Galileo.
  * *Internazionale*: Europeana IIIF, Internet Archive.
* **Architettura AI Multi-Provider**: Il motore di intelligenza artificiale non è più limitato a OpenAI e Gemini. Ora supporta:
  * **DeepSeek** (Integrazione nativa V3/R1).
  * **Anthropic** (Claude 3.5 Sonnet/Opus).
  * **Modelli Locali/Privati**: Ollama e HuggingFace Inference API.
  * **Provider alternativi**: Mistral, xAI (Grok), Groq.
* **Sistema "Cassaforte" (Key Manager) Intelligente**: 
  * Possibilità di inserire **chiavi API multiple** per lo stesso provider nel file `api_keys.csv`.
  * **Rotazione automatica (Auto-Fallback)**: se una chiave esaurisce il limite di quota (Errore 429), ATK-Pro passa istantaneamente e in modo silente alla chiave successiva, annullando le interruzioni durante batch massivi.
* **Override Manuale dei Modelli AI**: L'utente può ora forzare il nome esatto del modello da utilizzare (es. digitando `gemini-2.5-pro` o `deepseek-chat`) direttamente dall'interfaccia, disabilitando l'auto-discovery. Questo protegge il sistema dai continui cambi di nomenclatura dei provider.
* **Nuovo Menu Impostazioni Portale**: Aggiunto un menu a tendina permanente nelle impostazioni della GUI per selezionare il "Portale IIIF attivo", la cui preferenza viene salvata in `config.json`.
* **Traduzione Paleografica Assistita**: Nuovo modulo che sfrutta l'AI per tradurre i testi (latino, dialetti ottocenteschi) in 20 lingue moderne, usando dizionari utente e istruzioni dinamiche (Few-Shot).

### 🐛 Bug Fixes
* **Risoluzione blocchi TLS/Geo-blocking**: Implementato un bridge basato su *Playwright* per recuperare i manifest IIIF dai portali che applicano rigidi controlli anti-bot (Cloudflare/TLS fingerprinting), come Gallica BnF.
* **macOS UI/Path Fix**: Risolti svariati problemi di rendering dei percorsi di sistema e delle icone su sistemi operativi macOS.
* **Gestione Rate-Limiting IIIF**: Implementato un sistema di attesa asincrona (`max_workers` configurabile) e retry per i portali storici che impongono limiti severi ai download paralleli (es. Heidelberg UB).
* **Fix Troncamento JSON (Auto-Close)**: Il modulo OCR ora implementa una robusta regex `_cleanup_json_response` capace di auto-chiudere tabelle troncate dalle AI per limite di token.

### ⚡ Ottimizzazioni (Improvements)
* **Gestione dinamica v1.1 vs v3.0 IIIF**: Il downloader analizza e converte nativamente la sintassi obsoleta delle vecchie API IIIF Image (es. `native.jpg`) ai formati conformi.
* Aumentata la sovrapposizione tra i ritagli immagine nello splitting genealogico ("Full-Width" strip method) per prevenire mutilazioni di righe nei registri di stato civile.
* Il formato di output CSV elimina ora in automatico citazioni errate e simboli di ripetizione, garantendo una perfetta importazione su Microsoft Excel.
