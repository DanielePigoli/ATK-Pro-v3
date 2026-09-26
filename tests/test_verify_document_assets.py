from pathlib import Path

import verify_document_assets as documents


def test_all_ocr_guides_document_current_openai_and_deepseek_models():
    language_dirs = sorted(
        path for path in Path("assets").iterdir()
        if path.is_dir() and path.name != "common"
    )

    assert len(language_dirs) == 20
    for language_dir in language_dirs:
        guide = language_dir / "testuali" / "guida_06_ocr_avanzato.html"
        content = guide.read_text(encoding="utf-8")
        assert "<code>gpt-4.1</code>" in content, language_dir.name
        assert "<code>deepseek-flash</code>" in content, language_dir.name


def test_danish_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/da"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

def test_norwegian_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/no"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

def test_swedish_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/sv"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

def test_romanian_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/ro"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/ro/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()


def test_polish_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/pl"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/pl/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_greek_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/el"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/el/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_russian_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/ru"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/ru/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_turkish_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/tr"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/tr/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_vietnamese_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/vi"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/vi/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_chinese_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/zh"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/zh/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_japanese_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/ja"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/ja/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_arabic_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/ar"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/ar/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()

def test_hebrew_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/he"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

    text_dir = Path("assets/he/testuali")
    for obsolete_module in documents.BASE_GUIDE_MODULES[2:]:
        assert not (text_dir / obsolete_module).exists()
