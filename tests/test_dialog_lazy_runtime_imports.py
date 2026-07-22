import ast
from pathlib import Path


def _top_level_import_from_modules(source_path):
    tree = ast.parse(Path(source_path).read_text(encoding="utf-8"))
    modules = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            modules.append(node.module)
    return modules


def test_ocr_dialog_defers_ocr_processor_import_to_runtime():
    source = Path("src/ocr_dialog.py").read_text(encoding="utf-8")
    modules = _top_level_import_from_modules("src/ocr_dialog.py")

    assert "ocr_processor" not in modules
    assert "def _get_advanced_ocr_worker_class()" in source


def test_translation_dialog_defers_translation_worker_import_to_runtime():
    source = Path("src/translation_dialog.py").read_text(encoding="utf-8")
    modules = _top_level_import_from_modules("src/translation_dialog.py")

    assert "translation_processor" not in modules
    assert "def _get_translation_worker_class()" in source


def test_ai_search_dialog_defers_provider_handler_import_to_runtime():
    source = Path("src/RicercaAssistitaAI.py").read_text(encoding="utf-8")
    modules = _top_level_import_from_modules("src/RicercaAssistitaAI.py")

    assert "multi_provider_handlers" not in modules
    assert "def _get_handler_factory()" in source
