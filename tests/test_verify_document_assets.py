from pathlib import Path

import verify_document_assets as documents


def test_danish_guide_uses_current_v3_module_set():
    modules = documents.expected_guide_modules(Path("assets/da"))

    assert modules == documents.ITALIAN_GUIDE_MODULES
    assert "guida_03_ricerca_assistita_ai.html" in modules
    assert "guida_09_supporto_faq.html" in modules
    assert "guida_03_visualizzazione_immagini.html" not in modules

