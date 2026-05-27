"""
Test veloce per action_view_previous_elaborations - localizzazione e glossario
"""

import os
import json
import pytest
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main_gui_qt import carica_glossario, get_msg


def test_glossario_carica_correttamente():
    """Verifica che il glossario si carica senza errori."""
    glossario = carica_glossario("IT")
    assert glossario is not None
    assert len(glossario) > 0
    assert "messaggi_dialogo" in glossario or "etichette_gui" in glossario


def test_stringhe_localizzate_presenti():
    """Verifica che tutte le stringhe necessarie siano nel glossario."""
    glossario = carica_glossario("IT")
    
    stringhe_richieste = [
        "Nessuna cartella output configurata",
        "Visualizza elaborazioni precedenti",
        "Elaborazioni precedenti trovate",
        "Nessuna elaborazione trovata",
        "Chiudi"
    ]
    
    # Raccogli tutti i messaggi dal glossario
    tutti_i_messaggi = []
    for sezione in glossario.values():
        if isinstance(sezione, list):
            for voce in sezione:
                if isinstance(voce, dict) and "messaggio" in voce:
                    tutti_i_messaggi.append(voce["messaggio"])
    
    for stringa in stringhe_richieste:
        assert stringa in tutti_i_messaggi, f"Stringa '{stringa}' non trovata nel glossario"


@pytest.mark.parametrize("lingua", ["IT", "EN", "ES", "DE", "FR", "PT", "NL", "AR", "HE", "RU",
                                     "DA", "EL", "JA", "NO", "PL", "RO", "SV", "TR", "VI", "ZH"])
def test_get_msg_funziona_tutte_lingue(lingua):
    """Verifica che get_msg funziona per tutte le lingue."""
    glossario = carica_glossario(lingua)
    
    # Testa una stringa che sicuramente è tradotta
    msg = get_msg(glossario, "Elaborazioni precedenti trovate", lingua)
    assert msg is not None
    assert len(msg) > 0


def test_glossario_json_valido():
    """Verifica che il file glossario.json sia valido."""
    glossario_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs_generali", "glossario_multilingua_ATK-Pro.json"
    )
    
    with open(glossario_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert data
    messages = [
        entry.get("messaggio")
        for entries in data.values()
        if isinstance(entries, list)
        for entry in entries
        if isinstance(entry, dict)
    ]
    assert "Elaborazioni precedenti trovate" in messages
    for entries in data.values():
        assert isinstance(entries, list)
        for entry in entries:
            assert isinstance(entry, dict)
            assert "IT" in entry
