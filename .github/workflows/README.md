# ATK-Pro CI/CD Workflows

Workflow automatizzati per build multi-piattaforma di ATK-Pro usando GitHub Actions.

## 📋 Workflow Disponibili

### 1. Build macOS (`build-macos.yml`)
Compila l'applicazione per macOS e crea un installer DMG.

**Trigger:**
- Tag `v*` (es. `v3.0.0-rc1` o `v3.0.0`)
- Manuale (workflow_dispatch)

**Output:**
- `ATK-Pro.app` - Applicazione macOS
- `ATK-Pro-macOS-Intel-v<versione>.dmg` - DMG per Mac Intel
- `ATK-Pro-macOS-AppleSilicon-v<versione>.dmg` - DMG per Apple Silicon

**Come usare:**
1. Vai su: https://github.com/DanielePigoli/ATK-Pro-v3/actions/workflows/build-macos.yml
2. Click "Run workflow" → "Run workflow"
3. Attendi ~5-10 minuti
4. Download artifact da "Artifacts" in basso

### 2. Build Windows (`build-windows.yml`)
Compila l'eseguibile Windows e crea installer con Inno Setup.

**Trigger:**
- Tag `v*` (es. `v3.0.0-rc1` o `v3.0.0`)
- Manuale (workflow_dispatch)

**Output:**
- `dist/ATK-Pro/ATK-Pro.exe` - Eseguibile portable
- `ATK-Pro-Setup-v<versione>.exe` - Installer Inno Setup
- `ATK-Pro-v<versione>-Windows-Portable.zip` - ZIP portable

**Come usare:**
1. Vai su: https://github.com/DanielePigoli/ATK-Pro-v3/actions/workflows/build-windows.yml
2. Click "Run workflow" → "Run workflow"
3. Attendi ~5-10 minuti
4. Download artifact da "Artifacts" in basso

## 🚀 Rilascio Automatico

Per creare una release con installer automatici:

```bash
# 1. Tag la versione
git tag v3.0.0-rc1
git push origin v3.0.0-rc1

# 2. GitHub Actions compilerà automaticamente gli artifact taggati
# 3. Gli installer saranno allegati alla release su GitHub
```

Per tag contenenti `rc`, i workflow devono mantenere la release come
pre-release e non promuoverla a release stabile.

## 🔧 Test Locale Prima del Push

**Windows:**
```powershell
pyinstaller ATK-Pro.spec
.\dist\ATK-Pro\ATK-Pro.exe
```

**macOS (su Mac):**
```bash
pyinstaller \
  --name ATK-Pro \
  --windowed \
  --onefile \
  --icon=assets/common/grafici/ATK-Pro.ico \
  --add-data "assets:assets" \
  --add-data "locales:locales" \
  --add-data "docs_generali/glossario_multilingua_ATK-Pro.json:docs_generali" \
  src/main.py

open dist/ATK-Pro.app
```

## 📊 Monitoring

**Stato build:**
- macOS: ![macOS Build](https://github.com/DanielePigoli/ATK-Pro-v3/actions/workflows/build-macos.yml/badge.svg)
- Windows: ![Windows Build](https://github.com/DanielePigoli/ATK-Pro-v3/actions/workflows/build-windows.yml/badge.svg)
- Linux: ![Linux Build](https://github.com/DanielePigoli/ATK-Pro-v3/actions/workflows/build-linux.yml/badge.svg)

**Logs:**
https://github.com/DanielePigoli/ATK-Pro-v3/actions

## 🐛 Troubleshooting

**Build fallita su macOS:**
- Verifica che tutti i file assets esistano
- Controlla che `docs_generali/glossario_multilingua_ATK-Pro.json` sia committato
- Vedi log dettagliato nella sezione Actions

**Build fallita su Windows:**
- Verifica percorsi in `ATK-Pro.spec`
- Controlla che Inno Setup sia installato (automatico su GitHub Actions)

**Installer troppo grande:**
- GitHub limita upload a 2 GB per release
- Attuale: ~580 MB (OK)
- Se supera: considera compressione asset o split multi-parte

**Versione errata nel nome artifact:**
- I workflow leggono la versione da `src/atk_version.py`.
- Prima di un tag RC o finale, verificare `VERSION` e `DISPLAY_VERSION`.

## 📝 Note

- **GitHub Actions è gratis** per repository pubblici
- Limite: 2000 minuti/mese (free tier) = ~40 build complete
- Build tipica: ~5-10 minuti per piattaforma
- Artifact retention: 30 giorni (configurabile)
