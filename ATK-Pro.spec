# -*- mode: python ; coding: utf-8 -*-
r"""
ATK-Pro v3.0 PyInstaller Specification File
=============================================

Builds exe from modular source with proper path handling for:
- Program Files installation (read-only code)
- %USERPROFILE%\Documents\ATK-Pro\output (user-writable output)
- Bundled assets (en, it, ar, de, es, fr, he, nl, pt, ru)
- Glossario multilingue (i18n JSON)
- Manifest + tile caching

Build modes:
- --onedir: Development (faster builds, easier debugging)
- --onefile: Distribution (single executable, slower startup)

NOTE: Run from project root: pyinstaller ATK-Pro.spec [--onefile]
"""

import sys
import os

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/main_gui_qt.py', 'src'),
        ('src/image_metadata_viewer.py', 'src'),
        ('src/user_prompts.py', 'src'),
        # Multilingual UI assets (20 lingue)
        ('assets/en', 'assets/en'),
        ('assets/it', 'assets/it'),
        ('assets/es', 'assets/es'),
        ('assets/fr', 'assets/fr'),
        ('assets/de', 'assets/de'),
        ('assets/pt', 'assets/pt'),
        ('assets/ru', 'assets/ru'),
        ('assets/ar', 'assets/ar'),
        ('assets/nl', 'assets/nl'),
        ('assets/he', 'assets/he'),
        ('assets/ja', 'assets/ja'),
        ('assets/zh', 'assets/zh'),
        ('assets/pl', 'assets/pl'),
        ('assets/tr', 'assets/tr'),
        ('assets/da', 'assets/da'),
        ('assets/no', 'assets/no'),
        ('assets/vi', 'assets/vi'),
        ('assets/el', 'assets/el'),
        ('assets/ro', 'assets/ro'),
        ('assets/sv', 'assets/sv'),
        ('assets/common', 'assets/common'),

        # Localization files (20 lingue)
        ('locales/messages.pot', 'locales'),
        ('locales/ar', 'locales/ar'),
        ('locales/da', 'locales/da'),
        ('locales/de', 'locales/de'),
        ('locales/el', 'locales/el'),
        ('locales/en', 'locales/en'),
        ('locales/es', 'locales/es'),
        ('locales/fr', 'locales/fr'),
        ('locales/he', 'locales/he'),
        ('locales/it', 'locales/it'),
        ('locales/ja', 'locales/ja'),
        ('locales/nl', 'locales/nl'),
        ('locales/no', 'locales/no'),
        ('locales/pl', 'locales/pl'),
        ('locales/pt', 'locales/pt'),
        ('locales/ro', 'locales/ro'),
        ('locales/ru', 'locales/ru'),
        ('locales/sv', 'locales/sv'),
        ('locales/tr', 'locales/tr'),
        ('locales/vi', 'locales/vi'),
        ('locales/zh', 'locales/zh'),
        
        # Glossario JSON (CRITICAL for i18n)
        ('docs_generali/glossario_multilingua_ATK-Pro.json', 'docs_generali'),
        
        # NOTA: Playwright incluso automaticamente tramite hiddenimports
        # I browser Chromium (~150 MB) vengono scaricati on-demand al primo uso
        
        # Configuration + documentation
        # ('README.md', '.'),
        # CHANGELOG.md localizzati (20 lingue)
        ('assets/en/testuali/CHANGELOG.md', 'assets/en/testuali'),
        ('assets/it/testuali/CHANGELOG.md', 'assets/it/testuali'),
        ('assets/es/testuali/CHANGELOG.md', 'assets/es/testuali'),
        ('assets/fr/testuali/CHANGELOG.md', 'assets/fr/testuali'),
        ('assets/de/testuali/CHANGELOG.md', 'assets/de/testuali'),
        ('assets/pt/testuali/CHANGELOG.md', 'assets/pt/testuali'),
        ('assets/ru/testuali/CHANGELOG.md', 'assets/ru/testuali'),
        ('assets/ar/testuali/CHANGELOG.md', 'assets/ar/testuali'),
        ('assets/nl/testuali/CHANGELOG.md', 'assets/nl/testuali'),
        ('assets/he/testuali/CHANGELOG.md', 'assets/he/testuali'),
        ('assets/ja/testuali/CHANGELOG.md', 'assets/ja/testuali'),
        ('assets/zh/testuali/CHANGELOG.md', 'assets/zh/testuali'),
        ('assets/pl/testuali/CHANGELOG.md', 'assets/pl/testuali'),
        ('assets/tr/testuali/CHANGELOG.md', 'assets/tr/testuali'),
        ('assets/da/testuali/CHANGELOG.md', 'assets/da/testuali'),
        ('assets/no/testuali/CHANGELOG.md', 'assets/no/testuali'),
        ('assets/vi/testuali/CHANGELOG.md', 'assets/vi/testuali'),
        ('assets/el/testuali/CHANGELOG.md', 'assets/el/testuali'),
        ('assets/ro/testuali/CHANGELOG.md', 'assets/ro/testuali'),
        ('assets/sv/testuali/CHANGELOG.md', 'assets/sv/testuali'),
    ],
    hiddenimports=[
        'playwright',
        'PIL',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'requests',
        'urllib3',
        'certifi',
        'src.main_gui_qt',
        # src/ modules – explicit list to guarantee bundling on all platforms
        'asset_cache',
        'api_client',
        'browser_setup',
        'canvas_id_extractor',
        'canvas_processor',
        'cli_dispatcher',
        'config',
        'elaborazione',
        'ensure_playwright',
        'export_manager',
        'image_downloader',
        'image_metadata_viewer',
        'image_rebuilder',
        'image_saver',
        'input_loader',
        'input_parser',
        'link_editor',
        'logging_utils',
        'manifest_parser',
        'manifest_utils',
        'metadata_manager',
        'metadata_utils',
        'ocr_processor',
        'pdf_generator',
        'pdf_utils',
        'qt_worker',
        'tile_downloader',
        'tile_rebuilder',
        'translator',
        'ui_info',
        'url_utils',
        'user_prompts',
        'utils_install',
        'viewer',
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[
        'pytest',
        'pytest_cov',
        'pytest_mock',
        'pytest_timeout',
        'pycodestyle',
        'pydocstyle',
        'flake8',
        'black',
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'jupyter',
        'ipython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ATK-Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for CLI debugging, False for GUI-only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/common/grafici/ATK-Pro.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ATK-Pro',
)

# Optional: For --onefile mode
# onefile = BUNDLE(
#     exe,
#     name='ATK-Pro.exe',
#     icon='assets/common/ATK-Pro-icon.ico',
#     bundle_identifier=None,
#     info_plist={},
# )
