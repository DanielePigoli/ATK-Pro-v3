"""
Test Suite per ATK-Pro v3.0 - Verifica supporto multilingue e integrità build.
"""

import os
import sys
import json
import unittest
import pytest
from pathlib import Path

# Aggiungi il percorso src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLanguageSupport(unittest.TestCase):
    """Test per verificare che tutte le 20 lingue siano presenti e configurate"""

    SUPPORTED_LANGUAGES = {
        'ar': 'العربية',
        'da': 'Dansk',
        'de': 'Deutsch',
        'el': 'Ελληνικά',
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'he': 'עברית',
        'it': 'Italiano',
        'ja': '日本語',
        'nl': 'Nederlands',
        'no': 'Norsk',
        'pl': 'Polski',
        'pt': 'Português',
        'ro': 'Română',
        'ru': 'Русский',
        'sv': 'Svenska',
        'tr': 'Türkçe',
        'vi': 'Tiếng Việt',
        'zh': '中文'
    }

    def setUp(self):
        self.workspace_root = Path(__file__).parent.parent
        self.assets_dir = self.workspace_root / 'assets'
        self.glossario_file = self.workspace_root / 'docs_generali' / 'glossario_multilingua_ATK-Pro.json'
        self.dist_dir = self.workspace_root / 'dist' / 'ATK-Pro'

    def test_01_all_languages_have_asset_directories(self):
        """Verifica che tutte le lingue abbiano directory di asset"""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            lang_dir = self.assets_dir / lang_code
            self.assertTrue(
                lang_dir.exists(),
                f"Directory di asset mancante per {lang_code}: {lang_dir}"
            )

    def test_02_all_languages_have_testuali_folder(self):
        """Verifica che tutte le lingue abbiano la cartella 'testuali'"""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            testuali_dir = self.assets_dir / lang_code / 'testuali'
            self.assertTrue(
                testuali_dir.exists(),
                f"Cartella 'testuali' mancante per {lang_code}"
            )

    def test_03_all_languages_have_grafici_folder(self):
        """Verifica che tutte le lingue abbiano la cartella 'grafici'"""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            grafici_dir = self.assets_dir / lang_code / 'grafici'
            self.assertTrue(
                grafici_dir.exists(),
                f"Cartella 'grafici' mancante per {lang_code}"
            )

    def test_04_required_text_files_present(self):
        """Verifica che i file testuali richiesti siano presenti per tutte le lingue"""
        required_files = [
            'disclaimer_legale_ATK-Pro.txt',
            'presentazione_progetto_ATK-Pro.html',
            'presentazione_autore.html',
            'guida.html',
            'input_link_base.txt',
        ]

        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            for filename in required_files:
                file_path = self.assets_dir / lang_code / 'testuali' / filename
                self.assertTrue(
                    file_path.exists(),
                    f"File '{filename}' mancante per {lang_code}"
                )

            old_file_path = self.assets_dir / lang_code / 'testuali' / 'input_link_base_v2.0.txt'
            self.assertFalse(
                old_file_path.exists(),
                f"File esempio input obsoleto ancora presente per {lang_code}: {old_file_path}"
            )

    def test_05_glossario_file_exists(self):
        """Verifica che il file glossario multilingue esista"""
        self.assertTrue(
            self.glossario_file.exists(),
            f"File glossario mancante: {self.glossario_file}"
        )

    def test_06_glossario_valid_json(self):
        """Verifica che il glossario sia un JSON valido"""
        with open(self.glossario_file, 'r', encoding='utf-8') as f:
            try:
                glossario = json.load(f)
                self.assertIsInstance(glossario, dict, "Il glossario deve essere un dizionario")
            except json.JSONDecodeError as e:
                self.fail(f"Il glossario contiene JSON non valido: {e}")

    def test_07_glossario_has_all_languages(self):
        """Verifica che il glossario contenga traduzioni per tutte le lingue"""
        with open(self.glossario_file, 'r', encoding='utf-8') as f:
            glossario = json.load(f)

        for key, entries in glossario.items():
            self.assertIsInstance(entries, list, f"Voce glossario non lista: {key}")
            for entry in entries:
                for lang_code in self.SUPPORTED_LANGUAGES.keys():
                    self.assertIn(
                        lang_code.upper(),
                        entry,
                        f"Lingua '{lang_code.upper()}' non trovata nella voce glossario '{key}'"
                    )

    def test_08_locales_folders_present(self):
        """Verifica che le cartelle locales/[lang] siano presenti per il PyInstaller"""
        locales_root = self.workspace_root / 'locales'

        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            locale_dir = locales_root / lang_code
            self.assertTrue(
                locale_dir.exists(),
                f"Cartella locales mancante per {lang_code}: {locale_dir}"
            )

    def test_09_translation_targets_match_supported_languages(self):
        """Verifica che il dialog Traduzione esponga solo le 20 lingue supportate."""
        from translation_dialog import TARGET_LANGUAGES, TARGET_LANGUAGE_BY_INTERFACE

        self.assertEqual(set(TARGET_LANGUAGES), set(self.SUPPORTED_LANGUAGES.values()))
        self.assertEqual(set(TARGET_LANGUAGE_BY_INTERFACE.keys()), set(self.SUPPORTED_LANGUAGES.keys()))


class TestBuildArtifacts(unittest.TestCase):
    """Test per verificare che i build artifacts siano presenti"""

    def setUp(self):
        self.workspace_root = Path(__file__).parent.parent
        self.dist_dir = self.workspace_root / 'dist' / 'ATK-Pro'
        self.exe_file = self.dist_dir / 'ATK-Pro.exe'
        self.installer_file = self.workspace_root / 'Output' / 'ATK-Pro-Setup-v3.0.0.exe'

    def require_build_artifacts(self):
        if not self.dist_dir.exists():
            pytest.skip("Build artifacts not present; run packaging build before artifact checks.")

    def require_installer_artifact(self):
        if not self.installer_file.exists():
            pytest.skip("Installer artifact not present; run Windows installer build before installer checks.")

    def test_01_exe_file_exists(self):
        """Verifica che l'eseguibile principale sia stato generato"""
        self.require_build_artifacts()
        self.assertTrue(
            self.exe_file.exists(),
            f"File eseguibile mancante: {self.exe_file}"
        )

    def test_02_exe_file_has_size(self):
        """Verifica che l'eseguibile abbia una dimensione ragionevole (>1MB)"""
        self.require_build_artifacts()
        if self.exe_file.exists():
            size = self.exe_file.stat().st_size
            self.assertGreater(
                size,
                1024 * 1024,
                f"L'eseguibile è troppo piccolo ({size} bytes)"
            )

    def test_03_dist_directory_has_assets(self):
        """Verifica che la directory dist contiene gli asset"""
        self.require_build_artifacts()
        internal_assets = self.dist_dir / '_internal' / 'assets'
        self.assertTrue(
            internal_assets.exists(),
            f"Assets non trovati in dist: {internal_assets}"
        )

    def test_04_installer_file_exists(self):
        """Verifica che l'installer sia stato generato"""
        self.require_installer_artifact()
        self.assertTrue(
            self.installer_file.exists(),
            f"File installer mancante: {self.installer_file}"
        )

    def test_05_installer_file_has_size(self):
        """Verifica che l'installer abbia una dimensione ragionevole (>50MB)"""
        self.require_installer_artifact()
        if self.installer_file.exists():
            size = self.installer_file.stat().st_size
            self.assertGreater(
                size,
                50 * 1024 * 1024,
                f"L'installer è troppo piccolo ({size} bytes)"
            )


class TestCodeIntegrity(unittest.TestCase):
    """Test per verificare l'integrità del codice"""

    def setUp(self):
        self.workspace_root = Path(__file__).parent.parent
        self.src_dir = self.workspace_root / 'src'

    def test_01_main_module_exists(self):
        """Verifica che il modulo principale esista"""
        main_file = self.src_dir / 'main.py'
        self.assertTrue(
            main_file.exists(),
            f"File main.py mancante: {main_file}"
        )

    def test_02_main_module_can_import(self):
        """Verifica che il modulo principale possa essere importato"""
        try:
            import main
            self.assertIsNotNone(main, "Il modulo main non è stato importato")
        except ImportError as e:
            self.fail(f"Impossibile importare il modulo main: {e}")

    def test_03_gui_module_exists(self):
        """Verifica che il modulo GUI esista"""
        gui_file = self.src_dir / 'main_gui_qt.py'
        self.assertTrue(
            gui_file.exists(),
            f"File main_gui_qt.py mancante: {gui_file}"
        )


class TestAssetIntegrity(unittest.TestCase):
    """Test per verificare l'integrità degli asset"""

    def setUp(self):
        self.workspace_root = Path(__file__).parent.parent
        self.assets_dir = self.workspace_root / 'assets'

    def test_01_all_asset_files_readable(self):
        """Verifica che tutti i file di asset siano leggibili"""
        for asset_file in self.assets_dir.rglob('*'):
            if asset_file.is_file():
                try:
                    with open(asset_file, 'rb') as f:
                        f.read(1)  # Leggi almeno 1 byte
                except IOError as e:
                    self.fail(f"Impossibile leggere il file: {asset_file} - {e}")

    def test_02_html_files_valid_format(self):
        """Verifica che i file HTML abbiano il tag <html>"""
        for html_file in self.assets_dir.rglob('*.html'):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                self.assertIn(
                    '<html',
                    content,
                    f"File HTML senza tag <html>: {html_file}"
                )

    def test_03_txt_files_not_empty(self):
        """Verifica che i file di testo non siano vuoti"""
        for txt_file in self.assets_dir.rglob('*.txt'):
            size = txt_file.stat().st_size
            self.assertGreater(
                size,
                0,
                f"File di testo vuoto: {txt_file}"
            )


class TestConfigurationFiles(unittest.TestCase):
    """Test per verificare la configurazione di build"""

    def setUp(self):
        self.workspace_root = Path(__file__).parent.parent
        self.spec_file = self.workspace_root / 'ATK-Pro.spec'
        self.installer_script = self.workspace_root / 'ATK-Pro-Installer.iss'

    def test_01_pyinstaller_spec_exists(self):
        """Verifica che il file spec di PyInstaller esista"""
        self.assertTrue(
            self.spec_file.exists(),
            f"File ATK-Pro.spec mancante: {self.spec_file}"
        )

    def test_02_inno_setup_script_exists(self):
        """Verifica che lo script Inno Setup esista"""
        self.assertTrue(
            self.installer_script.exists(),
            f"File ATK-Pro-Installer.iss mancante: {self.installer_script}"
        )

    def test_03_spec_file_has_all_languages(self):
        """Verifica che il file spec contenga tutte le lingue"""
        with open(self.spec_file, 'r', encoding='utf-8') as f:
            spec_content = f.read()

        languages = ['ar', 'da', 'de', 'el', 'en', 'es', 'fr', 'he', 'it', 'ja',
                     'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sv', 'tr', 'vi', 'zh']

        for lang in languages:
            self.assertIn(
                lang,
                spec_content,
                f"Lingua '{lang}' non trovata in ATK-Pro.spec"
            )


def run_tests():
    """Esegue tutte le test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Aggiungi tutti i test case
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildArtifacts))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestAssetIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationFiles))

    # Esegui con verbosità
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
