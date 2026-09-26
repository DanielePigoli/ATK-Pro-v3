"""
Test coverage per resilienza download manifest
Verifica exponential backoff, timeout, errori transitori, JSONDecodeError
"""
import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock, call
import requests
from src import manifest_utils as mu


class TestManifestRetryBackoff:
    """Test exponential backoff nel download manifest."""

    def test_exponential_backoff_on_500_error(self, monkeypatch, tmp_path):
        """Verifica che retry avvenga su errori 500."""
        call_count = {'n': 0}

        def fake_get(url, headers=None, timeout=None):
            call_count['n'] += 1
            # Ritorna 500 per tutti i tentativi
            resp = Mock()
            resp.status_code = 500
            resp.ok = False
            return resp

        monkeypatch.setattr(mu.requests, 'get', fake_get)

        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')

        # Deve fare 3 tentativi (max_retries internamente)
        assert call_count['n'] == 3
        
        # Risultato deve essere None (fallimento definitivo)
        assert result is None

    def test_retry_on_timeout(self, monkeypatch, tmp_path):
        """Verifica retry se requests.get() timeout."""
        attempt_count = {'n': 0}

        def fake_get(url, headers=None, timeout=None):
            attempt_count['n'] += 1
            if attempt_count['n'] < 3:
                raise requests.exceptions.Timeout("Connection timeout")
            # Successo al 3° tentativo
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {"canvases": []}
            return resp

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')

        assert result == {"canvases": []}
        assert attempt_count['n'] == 3


class TestManifestJSONErrors:
    """Test gestione errori JSON manifest corrotto."""

    def test_json_decode_error_returns_none(self, monkeypatch, tmp_path):
        """Se manifest JSON non decodificabile → ritorna None (no crash)."""
        resp = Mock()
        resp.status_code = 200
        resp.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        monkeypatch.setattr(mu.requests, 'get', lambda *a, **k: resp)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        assert result is None

    def test_malformed_json_from_server(self, monkeypatch, tmp_path):
        """Se server ritorna HTML instead di JSON → JSONDecodeError → None."""
        resp = Mock()
        resp.status_code = 200
        resp.text = "<html>Server error</html>"
        resp.json.side_effect = json.JSONDecodeError("Invalid JSON", resp.text, 0)
        
        monkeypatch.setattr(mu.requests, 'get', lambda *a, **k: resp)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        assert result is None


class TestManifestHTTPErrors:
    """Test gestione specifica HTTP errors."""

    def test_403_forbidden_returns_none_immediately(self, monkeypatch, tmp_path):
        """HTTP 403 → ritorna None senza retry."""
        call_count = {'n': 0}

        def fake_get(url, headers=None, timeout=None):
            call_count['n'] += 1
            resp = Mock()
            resp.status_code = 403
            return resp

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        # Must be called exactly once (no retry for 403)
        assert call_count['n'] == 1
        assert result is None

    def test_503_service_unavailable_retries(self, monkeypatch, tmp_path):
        """HTTP 503 (Service Unavailable) → retry automatico."""
        attempt_count = {'n': 0}

        def fake_get(url, headers=None, timeout=None):
            attempt_count['n'] += 1
            if attempt_count['n'] < 3:
                resp = Mock()
                resp.status_code = 503
                return resp
            # Success on 3rd attempt
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {"canvases": []}
            return resp

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        assert result == {"canvases": []}
        assert attempt_count['n'] == 3

    def test_all_retries_exhausted_returns_none(self, monkeypatch, tmp_path):
        """Se tutti i retry falliscono → None (no exception)."""
        def fake_get(url, headers=None, timeout=None):
            raise requests.exceptions.ConnectionError("Network unreachable")

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        assert result is None


class TestManifestHeaders:
    """Test che HEADERS_UX siano usati (User-Agent, Referer, etc)."""

    def test_download_uses_headers_ux(self, monkeypatch, tmp_path):
        """Verifica che download_manifest usi HEADERS_UX con User-Agent, Referer, etc."""
        captured_headers = {}

        def fake_get(url, headers=None, timeout=None):
            captured_headers['headers'] = headers
            resp = Mock()
            resp.status_code = 200
            resp.json.return_value = {"canvases": []}
            return resp

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        # Must have used HEADERS_UX
        assert captured_headers['headers'] is not None
        headers = captured_headers['headers']
        assert 'User-Agent' in headers
        assert 'Mozilla' in headers['User-Agent']
        assert 'Referer' in headers
        assert result == {"canvases": []}


class TestManifestFileSaving:
    """Test salvataggio manifest su disco."""

    def test_manifest_saved_with_correct_filename(self, monkeypatch, tmp_path):
        """Manifest salvato con nome manifest_<container_id>_<titolo>.json."""
        resp = Mock()
        resp.status_code = 200
        resp.json.return_value = {"canvases": [{"id": "page1"}]}
        
        monkeypatch.setattr(mu.requests, 'get', lambda *a, **k: resp)
        
        # URL con container ID "ABC123"
        manifest_url = 'https://dam-antenati.cultura.gov.it/antenati/containers/ABC123/manifest'
        result = mu.download_manifest(manifest_url, str(tmp_path), 'documento_test')
        
        assert result is not None
        
        # Verifica che file esista con pattern corretto
        import os
        files = os.listdir(tmp_path)
        assert any('manifest_ABC123' in f and 'documento_test' in f for f in files)

    def test_manifest_title_sanitized_in_filename(self, monkeypatch, tmp_path):
        """Titolo con caratteri speciali viene pulito nel filename."""
        resp = Mock()
        resp.status_code = 200
        resp.json.return_value = {"canvases": []}
        
        monkeypatch.setattr(mu.requests, 'get', lambda *a, **k: resp)
        
        # Titolo con caratteri non-filesystem-safe
        result = mu.download_manifest(
            'https://dam-antenati.cultura.gov.it/antenati/containers/XYZ/manifest',
            str(tmp_path),
            'doc/test:file|name?'
        )
        
        assert result is not None
        
        import os
        files = os.listdir(tmp_path)
        # Nessun carattere speciale nel filename
        assert any('manifest_XYZ' in f for f in files)
        for f in files:
            assert ':' not in f
            assert '|' not in f
            assert '?' not in f
            assert '<' not in f
            assert '>' not in f

    def test_remote_container_id_is_sanitized_in_filename(self, monkeypatch, tmp_path):
        resp = Mock()
        resp.status_code = 200
        resp.json.return_value = {"sequences": [{"canvases": []}]}
        monkeypatch.setattr(mu.requests, 'get', lambda *a, **k: resp)

        result = mu.download_manifest(
            'https://phaidra.unipd.it/api/object/o:327971/iiifmanifest',
            str(tmp_path),
            'documento_test',
        )

        assert result is not None
        files = list(tmp_path.iterdir())
        assert [path.name for path in files] == [
            'manifest_o_327971_documento_test.json'
        ]


class TestManifestRequestException:
    """Test gestione eccezioni requests generiche."""

    def test_connection_error_handled(self, monkeypatch, tmp_path):
        """requests.exceptions.ConnectionError → retry e fallback None."""
        def fake_get(url, headers=None, timeout=None):
            raise requests.exceptions.ConnectionError("Connection refused")

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        assert result is None

    def test_request_exception_generic(self, monkeypatch, tmp_path):
        """requests.exceptions.RequestException generico → handled."""
        def fake_get(url, headers=None, timeout=None):
            raise requests.exceptions.RequestException("Generic error")

        monkeypatch.setattr(mu.requests, 'get', fake_get)
        
        result = mu.download_manifest('http://fake/manifest.json', str(tmp_path), 'doc')
        
        assert result is None
