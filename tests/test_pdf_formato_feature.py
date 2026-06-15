# -*- coding: utf-8 -*-
"""
Test per la feature: PDF come formato nella maschera scelta formati.
Copre:
  - _normalize_format('PDF')
  - _make_placeholder_image() con e senza localizzazione
  - ask_image_formats() con checkbox PDF
  - _generate_register_pdf() con image_dir opzionale
  - _process_document() in modalita only_pdf, pdf+immagini, nessun pdf
  - _process_register() in modalita only_pdf, pdf+immagini
"""

import os
import pytest
from unittest.mock import MagicMock, patch, call
from PIL import Image

import src.elaborazione as elab_mod
from src.elaborazione import (
    _normalize_format,
    _make_placeholder_image,
    Elaborazione,
)
import src.user_prompts as up


# =============================================================================
# 1. _normalize_format
# =============================================================================

class TestNormalizeFormat:
    def test_pdf_uppercase(self):
        assert _normalize_format('PDF') == 'PDF'

    def test_pdf_lowercase(self):
        assert _normalize_format('pdf') == 'PDF'

    def test_jpg(self):
        assert _normalize_format('JPG') == 'JPEG'

    def test_tif(self):
        assert _normalize_format('TIF') == 'TIFF'

    def test_png(self):
        assert _normalize_format('PNG') == 'PNG'


# =============================================================================
# 2. _make_placeholder_image
# =============================================================================

class TestMakePlaceholderImage:
    def test_returns_pil_image(self):
        img = _make_placeholder_image("https://example.com/iiif/resource")
        assert isinstance(img, Image.Image)
        assert img.size == (800, 1200)

    def test_with_localization_en(self):
        glossario = {"messaggi_dialogo": [
            {"messaggio": "Download fallito", "IT": "Download fallito", "EN": "Download failed"},
            {"messaggio": "Riprova usando il seguente link:", "IT": "Riprova...", "EN": "Retry using the following link:"},
        ]}
        img = _make_placeholder_image("https://example.com/service", glossario_data=glossario, lingua="EN")
        assert isinstance(img, Image.Image)

    def test_with_no_glossario(self):
        img = _make_placeholder_image("https://example.com/service", glossario_data=None, lingua="IT")
        assert isinstance(img, Image.Image)

    def test_long_url_wraps(self):
        long_url = "https://example.com/" + "a" * 300
        img = _make_placeholder_image(long_url)
        assert isinstance(img, Image.Image)


# =============================================================================
# 3. ask_image_formats() con PDF
# =============================================================================

class TestAskImageFormatsPDF:
    def test_format_vars_with_pdf_selected(self):
        """Modalita mock: PDF selezionato."""
        format_vars = {
            "JPG": MagicMock(get=lambda: False),
            "PNG": MagicMock(get=lambda: False),
            "TIFF": MagicMock(get=lambda: False),
            "PDF": MagicMock(get=lambda: True),
        }
        result = up.ask_image_formats(format_vars=format_vars)
        assert result == ["pdf"]

    def test_format_vars_pdf_and_png(self):
        format_vars = {
            "JPG": MagicMock(get=lambda: False),
            "PNG": MagicMock(get=lambda: True),
            "TIFF": MagicMock(get=lambda: False),
            "PDF": MagicMock(get=lambda: True),
        }
        result = up.ask_image_formats(format_vars=format_vars)
        assert sorted(result) == ["pdf", "png"]

    def test_format_vars_no_pdf(self):
        format_vars = {
            "JPG": MagicMock(get=lambda: True),
            "PNG": MagicMock(get=lambda: False),
            "TIFF": MagicMock(get=lambda: False),
            "PDF": MagicMock(get=lambda: False),
        }
        result = up.ask_image_formats(format_vars=format_vars)
        assert result == ["jpg"]


# =============================================================================
# 4. _generate_register_pdf con image_dir opzionale
# =============================================================================

class TestGenerateRegisterPdfImageDir:
    def _make_elab(self, tmp_path):
        elab = Elaborazione('R', 'https://example.com/ark:/dummy/1', str(tmp_path))
        elab.nome_file = 'regtest'
        elab.output_dir = str(tmp_path)
        return elab

    def test_default_image_dir_uses_output_dir(self, tmp_path, monkeypatch):
        elab = self._make_elab(tmp_path)
        png = tmp_path / 'regtest_canvas_1.png'
        img = Image.new('RGB', (10, 10), color='red')
        img.save(str(png))

        captured = {}
        def fake_create(paths, outpath, resolution_dpi=400):
            captured['paths'] = paths
            open(outpath, 'wb').write(b'%PDF-1.4 %%EOF')
            return outpath

        monkeypatch.setattr('src.elaborazione.create_pdf_from_images', fake_create)
        monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata', lambda *a, **k: None)

        result = elab._generate_register_pdf(['regtest_canvas_1.png'])
        assert result is not None
        assert any(str(tmp_path) in p for p in captured['paths'])

    def test_custom_image_dir(self, tmp_path, monkeypatch):
        elab = self._make_elab(tmp_path)
        tmpdir = tmp_path / '_tmp_pdf_images'
        tmpdir.mkdir()
        png = tmpdir / 'regtest_canvas_1_pdftmp.png'
        img = Image.new('RGB', (10, 10), color='blue')
        img.save(str(png))

        captured = {}
        def fake_create(paths, outpath, resolution_dpi=400):
            captured['paths'] = paths
            open(outpath, 'wb').write(b'%PDF-1.4 %%EOF')
            return outpath

        monkeypatch.setattr('src.elaborazione.create_pdf_from_images', fake_create)
        monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata', lambda *a, **k: None)

        result = elab._generate_register_pdf(
            ['regtest_canvas_1_pdftmp.png'], image_dir=str(tmpdir))
        assert result is not None
        assert str(tmpdir) in captured['paths'][0]


# =============================================================================
# 5. _process_document() — integrazione (mocked)
# =============================================================================

FAKE_MANIFEST = {
    "sequences": [{"canvases": [
        {
            "@id": "https://example.com/canvas/1",
            "label": "Pagina 1",
            "images": [{"resource": {"service": {"@id": "https://iiif.example.com/image/1"}}}]
        }
    ]}],
    "metadata": {}
}


def _fake_info():
    return {
        "width": 100, "height": 100,
        "tiles": [{"width": 256, "height": 256, "scaleFactors": [1]}],
        "@id": "https://iiif.example.com/image/1"
    }


def _make_document_elab(tmp_path, formats):
    elab = Elaborazione('D', 'https://example.com/ark:/12657/an_ua123456', str(tmp_path))
    elab.nome_file = 'doctest'
    elab.output_dir = str(tmp_path)
    elab.manifest_path = None
    elab.formats = formats
    elab.glossario_data = None
    elab.lingua = 'IT'
    return elab


class TestProcessDocumentPDF:

    def _patch_common(self, monkeypatch, tmp_path, img=None):
        """Patch di tutte le dipendenze esterne di _process_document."""
        if img is None:
            img = Image.new('RGB', (100, 100), color='white')

        monkeypatch.setattr('src.elaborazione.extract_canvas_id_from_url',
                            lambda url: '1')
        monkeypatch.setattr('src.elaborazione.extract_ud_canvas_id_from_infojson_xhr',
                            lambda *a, **k: '1')
        monkeypatch.setattr('src.elaborazione.download_info_json',
                            lambda url: _fake_info())
        monkeypatch.setattr('src.elaborazione.download_tiles',
                            lambda info, tile_dir, **kwargs: ([], []))
        monkeypatch.setattr('src.elaborazione.rebuild_image',
                            lambda info, tile_dir, **kwargs: img)
        monkeypatch.setattr('src.elaborazione.build_image_metadata',
                            lambda **kw: {'_json': {}})
        monkeypatch.setattr('src.elaborazione.save_image_variants',
                            lambda *a, **k: None)
        monkeypatch.setattr('src.elaborazione.estrai_metadati_da_manifest',
                            lambda *a, **k: None)
        def _fake_create_pdf(paths, out, **k):
            open(out, 'wb').write(b'%PDF-1.4 %%EOF')
            return out
        monkeypatch.setattr('src.elaborazione.create_pdf_from_images', _fake_create_pdf)
        monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata',
                            lambda *a, **k: None)

    def test_only_pdf_creates_temp_dir_and_cleans_up(self, tmp_path, monkeypatch):
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_document_elab(tmp_path, ['PDF'])

        # Traccia le chiamate a shutil.rmtree (senza bloccarla)
        cleaned = []
        real_rmtree = elab_mod.shutil.rmtree
        def tracking_rmtree(path, **kwargs):
            cleaned.append(str(path))
            real_rmtree(path, **kwargs)
        monkeypatch.setattr('src.elaborazione.shutil.rmtree', tracking_rmtree)

        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']
        result = elab._process_document(tiles_info, {})
        assert result is True

        # Il cleanup di temp_pdf_dir deve essere stato chiamato
        temp_dir = str(tmp_path / '_tmp_pdf_images')
        assert any(temp_dir in c for c in cleaned), f"temp_pdf_dir non ripulita; chiamate: {cleaned}"
        # E non deve esistere dopo il cleanup reale
        assert not (tmp_path / '_tmp_pdf_images').exists()

    def test_pdf_plus_image_formats_no_temp_dir(self, tmp_path, monkeypatch):
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_document_elab(tmp_path, ['PNG', 'PDF'])

        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']

        save_called_formats = []
        def fake_save(img, outdir, basename, formats, meta=None):
            save_called_formats.extend(formats)

        monkeypatch.setattr('src.elaborazione.save_image_variants', fake_save)

        result = elab._process_document(tiles_info, {})
        assert result is True
        # save_image_variants NON deve ricevere 'PDF'
        assert 'PDF' not in save_called_formats

        # Nessuna cartella temp

    def test_antenati_ud_prefers_html_canvas_before_playwright(self, tmp_path, monkeypatch):
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_document_elab(tmp_path, ['PNG'])
        elab.ark_url = 'https://antenati.cultura.gov.it/ark:/12657/an_ud19467689'
        elab.portale = 'antenati'

        monkeypatch.setattr('src.elaborazione.extract_canvas_id_from_url',
                            lambda url: '1')
        monkeypatch.setattr(
            'src.elaborazione.extract_ud_canvas_id_from_infojson_xhr',
            lambda *a, **k: (_ for _ in ()).throw(
                AssertionError('Playwright should not run when HTML exposes canvasId')
            ),
        )

        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']
        assert elab._process_document(tiles_info, {}) is True
        assert not (tmp_path / '_tmp_pdf_images').exists()

    def test_no_pdf_in_formats_no_pdf_generated(self, tmp_path, monkeypatch):
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_document_elab(tmp_path, ['PNG'])

        pdf_calls = []
        monkeypatch.setattr('src.elaborazione.create_pdf_from_images',
                            lambda *a, **k: pdf_calls.append(a) or None)

        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']
        result = elab._process_document(tiles_info, {})
        assert result is True
        assert pdf_calls == []

    def test_only_pdf_with_failed_rebuild_uses_placeholder(self, tmp_path, monkeypatch):
        """Se rebuild_image restituisce None in modalita PDF, usa placeholder."""
        self._patch_common(monkeypatch, tmp_path, img=None)
        # rebuild => None
        monkeypatch.setattr('src.elaborazione.rebuild_image', lambda *a, **k: None)

        placeholder_called = []
        real_placeholder = elab_mod._make_placeholder_image
        def fake_placeholder(svc_id, **kwargs):
            placeholder_called.append(svc_id)
            return Image.new('RGB', (100, 100), color='gray')
        monkeypatch.setattr('src.elaborazione._make_placeholder_image', fake_placeholder)

        elab = _make_document_elab(tmp_path, ['PDF'])
        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']
        result = elab._process_document(tiles_info, {})
        assert result is True
        assert len(placeholder_called) == 1

    def test_no_pdf_with_failed_rebuild_returns_false(self, tmp_path, monkeypatch):
        """Se rebuild_image restituisce None senza PDF nei formati => False."""
        self._patch_common(monkeypatch, tmp_path, img=None)
        monkeypatch.setattr('src.elaborazione.rebuild_image', lambda *a, **k: None)

        elab = _make_document_elab(tmp_path, ['PNG'])
        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']
        result = elab._process_document(tiles_info, {})
        assert result is False

    def test_ask_pdf_cb_not_called_when_pdf_in_formats(self, tmp_path, monkeypatch):
        """ask_pdf_cb NON deve essere chiamata se PDF è già nei formati."""
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_document_elab(tmp_path, ['PDF'])
        cb_called = []
        elab.ask_pdf_cb = lambda nome: cb_called.append(nome) or True

        tiles_info = FAKE_MANIFEST['sequences'][0]['canvases']
        elab._process_document(tiles_info, {})
        assert cb_called == []


# =============================================================================
# 6. _process_register() — integrazione (mocked)
# =============================================================================

FAKE_REGISTER_MANIFEST = {
    "sequences": [{"canvases": [
        {
            "@id": "https://example.com/canvas/1",
            "label": "Foglio 1",
            "images": [{"resource": {"service": {"@id": "https://iiif.example.com/image/reg1"}}}]
        },
        {
            "@id": "https://example.com/canvas/2",
            "label": "Foglio 2",
            "images": [{"resource": {"service": {"@id": "https://iiif.example.com/image/reg2"}}}]
        },
    ]}],
    "metadata": {}
}


def _make_register_elab(tmp_path, formats):
    elab = Elaborazione('R', 'https://example.com/ark:/12657/an_ra123456', str(tmp_path))
    elab.nome_file = 'regtest'
    elab.output_dir = str(tmp_path)
    elab.manifest_path = None
    elab.formats = formats
    elab.glossario_data = None
    elab.lingua = 'IT'
    return elab


class TestProcessRegisterPDF:

    def _patch_common(self, monkeypatch, tmp_path, img=None):
        if img is None:
            img = Image.new('RGB', (100, 100), color='white')
        monkeypatch.setattr('src.elaborazione.download_info_json',
                            lambda url: _fake_info())
        monkeypatch.setattr('src.elaborazione.download_tiles',
                            lambda info, tile_dir, **kwargs: ([], []))
        monkeypatch.setattr('src.elaborazione.rebuild_image',
                            lambda info, tile_dir, **kwargs: img)
        monkeypatch.setattr('src.elaborazione.build_image_metadata',
                            lambda **kw: {'_json': {}})
        monkeypatch.setattr('src.elaborazione.save_image_variants',
                            lambda *a, **k: None)
        monkeypatch.setattr('src.elaborazione.estrai_metadati_da_manifest',
                            lambda *a, **k: None)
        def _fake_create_pdf(paths, out, **k):
            open(out, 'wb').write(b'%PDF-1.4 %%EOF')
            return out
        monkeypatch.setattr('src.elaborazione.create_pdf_from_images', _fake_create_pdf)
        monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata',
                            lambda *a, **k: None)

    def test_only_pdf_temp_dir_cleaned(self, tmp_path, monkeypatch):
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_register_elab(tmp_path, ['PDF'])

        cleaned = []
        real_rmtree = elab_mod.shutil.rmtree
        def tracking_rmtree(path, **kwargs):
            cleaned.append(str(path))
            real_rmtree(path, **kwargs)
        monkeypatch.setattr('src.elaborazione.shutil.rmtree', tracking_rmtree)

        tiles_info = FAKE_REGISTER_MANIFEST['sequences'][0]['canvases']
        result = elab._process_register(tiles_info, {})
        assert result is True

        temp_dir = str(tmp_path / '_tmp_pdf_images')
        assert any(temp_dir in c for c in cleaned), f"temp_pdf_dir non ripulita; chiamate: {cleaned}"
        assert not (tmp_path / '_tmp_pdf_images').exists()

    def test_pdf_plus_image_save_not_called_with_pdf(self, tmp_path, monkeypatch):
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_register_elab(tmp_path, ['PNG', 'PDF'])

        saved_formats = []
        def fake_save(img, outdir, basename, formats, meta=None):
            saved_formats.extend(formats)
        monkeypatch.setattr('src.elaborazione.save_image_variants', fake_save)

        tiles_info = FAKE_REGISTER_MANIFEST['sequences'][0]['canvases']
        result = elab._process_register(tiles_info, {})
        assert result is True
        assert 'PDF' not in saved_formats

    def test_no_pdf_ask_pdf_cb_is_respected(self, tmp_path, monkeypatch):
        """Senza PDF nei formati, ask_pdf_cb determina se generare PDF."""
        self._patch_common(monkeypatch, tmp_path)
        elab = _make_register_elab(tmp_path, ['PNG'])

        pdf_calls = []
        monkeypatch.setattr('src.elaborazione.create_pdf_from_images',
                            lambda paths, out, **k: pdf_calls.append(out) or None)

        elab.ask_pdf_cb = lambda nome: False  # risponde No

        tiles_info = FAKE_REGISTER_MANIFEST['sequences'][0]['canvases']
        result = elab._process_register(tiles_info, {})
        assert result is True
        assert pdf_calls == []

    def test_canvas_with_failed_rebuild_uses_placeholder_in_only_pdf(self, tmp_path, monkeypatch):
        """Canvas falliti in only_pdf → placeholder inserito nel PDF."""
        calls_count = {'placeholder': 0}
        real_img = Image.new('RGB', (10, 10), color='white')

        call_n = [0]
        def rebuild_alternating(info, tile_dir, **kwargs):
            call_n[0] += 1
            return real_img if call_n[0] % 2 == 1 else None  # secondo canvas fallisce

        monkeypatch.setattr('src.elaborazione.download_info_json', lambda url: _fake_info())
        monkeypatch.setattr('src.elaborazione.download_tiles', lambda *a, **k: ([], []))
        monkeypatch.setattr('src.elaborazione.rebuild_image', rebuild_alternating)
        monkeypatch.setattr('src.elaborazione.build_image_metadata', lambda **kw: {'_json': {}})
        monkeypatch.setattr('src.elaborazione.save_image_variants', lambda *a, **k: None)
        monkeypatch.setattr('src.elaborazione.shutil.rmtree', lambda *a, **k: None)
        monkeypatch.setattr('src.elaborazione.estrai_metadati_da_manifest', lambda *a, **k: None)
        def _fake_create_pdf2(paths, out, **k):
            open(out, 'wb').write(b'%PDF-1.4 %%EOF')
            return out
        monkeypatch.setattr('src.elaborazione.create_pdf_from_images', _fake_create_pdf2)
        monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata', lambda *a, **k: None)

        original_placeholder = elab_mod._make_placeholder_image
        def counting_placeholder(svc_id, **kwargs):
            calls_count['placeholder'] += 1
            return Image.new('RGB', (100, 100), color='gray')
        monkeypatch.setattr('src.elaborazione._make_placeholder_image', counting_placeholder)

        elab = _make_register_elab(tmp_path, ['PDF'])
        tiles_info = FAKE_REGISTER_MANIFEST['sequences'][0]['canvases']  # 2 canvas
        result = elab._process_register(tiles_info, {})
        assert result is True
        assert calls_count['placeholder'] == 1  # solo il secondo canvas usa placeholder
