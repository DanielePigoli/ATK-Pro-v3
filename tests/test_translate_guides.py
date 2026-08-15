from translate_guides import extract_html_text, recover_translations


def test_extract_html_text_includes_single_letter_conjunctions() -> None:
    html = "<table><tr><td><code>D</code> o <code>R</code></td></tr></table>"

    template, units = extract_html_text(html)

    assert list(units.values()) == ["o"]
    assert "<code>D</code> {T00000} <code>R</code>" in template


def test_extract_html_text_includes_alt_attributes_and_recovers_them() -> None:
    html = '<p><img src="window.webp" alt="Elaborazione in corso">Testo</p>'
    localized = '<p><img src="window.webp" alt="Traitement en cours">Texte</p>'

    template, units = extract_html_text(html)
    recovered = recover_translations(template, units, localized)

    assert list(units.values()) == ["Elaborazione in corso", "Testo"]
    assert list(recovered.values()) == ["Traitement en cours", "Texte"]


def test_extract_html_text_includes_meta_description() -> None:
    html = '<head><meta name="description" content="Ricerca assistita AI"></head>'
    localized = '<head><meta name="description" content="Recherche assistée par IA"></head>'

    template, units = extract_html_text(html)
    recovered = recover_translations(template, units, localized)

    assert list(units.values()) == ["Ricerca assistita AI"]
    assert list(recovered.values()) == ["Recherche assistée par IA"]
