# -*- coding: utf-8 -*-

from src.main_gui_qt import _is_bdt_direct_pdf_full_record_allowed


def test_bdt_testi_a_stampa_pdf_only_allows_full_record_without_range():
    record = {
        "modalita": "R",
        "url": "https://bdt.bibcom.trento.it/Testi-a-stampa/113",
    }

    assert _is_bdt_direct_pdf_full_record_allowed(
        "biblioteca_digitale_trentina",
        ["PDF"],
        record,
    )


def test_bdt_testi_a_stampa_with_images_still_requires_range():
    record = {
        "modalita": "R",
        "url": "https://bdt.bibcom.trento.it/Testi-a-stampa/113",
    }

    assert not _is_bdt_direct_pdf_full_record_allowed(
        "biblioteca_digitale_trentina",
        ["PDF", "PNG"],
        record,
    )


def test_bdt_iconografia_pdf_only_still_requires_range():
    record = {
        "modalita": "R",
        "url": "https://bdt.bibcom.trento.it/Iconografia/4052#page/n0",
    }

    assert not _is_bdt_direct_pdf_full_record_allowed(
        "biblioteca_digitale_trentina",
        ["PDF"],
        record,
    )


def test_non_bdt_pdf_only_still_uses_portal_policy():
    record = {
        "modalita": "R",
        "url": "https://example.org/Testi-a-stampa/113",
    }

    assert not _is_bdt_direct_pdf_full_record_allowed("antenati", ["PDF"], record)
