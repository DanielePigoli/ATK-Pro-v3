from pathlib import Path

import verify_document_assets as documents


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
