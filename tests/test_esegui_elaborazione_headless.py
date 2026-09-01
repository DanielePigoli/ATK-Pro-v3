from src import elaborazione as elab_mod


class FakeElab:
    def __init__(self, modalita, url, out_dir, glossario_data=None, lingua='IT', **kwargs):
        self.modalita = modalita
        self.url = url
        self.output_dir = out_dir
        self.nome_file = ''
        self.resource_profile = kwargs.get("resource_profile")

    def set_nome_file(self, nome):
        self.nome_file = nome

    def run(self, formats=None):
        # simulate successful processing
        return True


def test_esegui_elaborazione_headless(tmp_path, monkeypatch):
    # Prepare state
    records = [{"modalita": "R", "url": "ark:/dummy/1", "nome_file": "rec1"}]
    formats = ['PNG']

    # Ensure an output folder exists and set it in module state
    out = tmp_path / 'out'
    out.mkdir()
    state = {
        'records': records,
        'formats': formats,
        'output_folder': str(out),
        'output_folders_doc': [],
        'output_folders_reg': [str(out)],
        'resource_profile': 'leggero',
    }

    # Patch Elaborazione with our FakeElab and ProgressDialog to avoid GUI
    monkeypatch.setattr(elab_mod, 'Elaborazione', FakeElab)

    class DummyProgress:
        def __init__(self, *a, **k):
            self.cancelled = False
        def show(self):
            pass
        def update(self, *a, **k):
            pass
        def close(self):
            pass

    # Patch ProgressDialog where it is imported from (src.user_prompts)
    monkeypatch.setattr('src.user_prompts.ProgressDialog', DummyProgress)

    risultati = elab_mod.esegui_elaborazione(state, glossario_data=None, lingua='IT', records=records, formats=formats)
    assert isinstance(risultati, list)
    assert len(risultati) == 1
    assert risultati[0]['status'] in ('SUCCESS', 'FAILED', 'CANCELLED')


def test_esegui_elaborazione_passes_resource_profile(tmp_path, monkeypatch):
    captured = {}

    class CapturingElab(FakeElab):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            captured["resource_profile"] = self.resource_profile

    records = [{"modalita": "R", "url": "ark:/dummy/1", "nome_file": "rec1"}]
    formats = ['PNG']
    out = tmp_path / 'out'
    out.mkdir()
    state = {
        'records': records,
        'formats': formats,
        'output_folder': str(out),
        'output_folders_doc': [],
        'output_folders_reg': [str(out)],
        'resource_profile': 'veloce',
    }

    monkeypatch.setattr(elab_mod, 'Elaborazione', CapturingElab)

    class DummyProgress:
        def __init__(self, *a, **k):
            self.cancelled = False
        def show(self):
            pass
        def update(self, *a, **k):
            pass
        def close(self):
            pass

    monkeypatch.setattr('src.user_prompts.ProgressDialog', DummyProgress)

    elab_mod.esegui_elaborazione(state, glossario_data=None, lingua='IT', records=records, formats=formats)
    assert captured["resource_profile"] == "veloce"



def test_esegui_elaborazione_detects_record_portal_and_passes_range(tmp_path, monkeypatch):
    captured = {}

    class CapturingElab(FakeElab):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            captured["portale"] = kwargs.get("portale")

        def run(self, formats=None):
            captured["canvas_da"] = self.canvas_da
            captured["canvas_a"] = self.canvas_a
            captured["force_gen_pdf"] = self.force_gen_pdf
            return True

    out = tmp_path / "out"
    out.mkdir()
    records = [{
        "modalita": "R",
        "url": "https://www.bdl.servizirl.it/bdl/public/rest/srv/item/12404/pdf",
        "nome_file": "registro_bdl",
        "canvas_da": 2,
        "canvas_a": 4,
        "gen_pdf": True,
    }]
    state = {
        "records": records,
        "formats": ["PDF"],
        "output_folder": str(out),
        "output_folders_doc": [],
        "output_folders_reg": [str(out)],
        "portale_attivo": "antenati",
    }
    monkeypatch.setattr(elab_mod, "Elaborazione", CapturingElab)

    result = elab_mod.esegui_elaborazione(state, records=records, formats=["PDF"])

    assert result[0]["status"] == "SUCCESS"
    assert captured == {
        "portale": "biblioteca_digitale_lombarda",
        "canvas_da": 2,
        "canvas_a": 4,
        "force_gen_pdf": True,
    }


def test_esegui_elaborazione_reports_path_preflight_error_before_processing(tmp_path, monkeypatch):
    records = [{"modalita": "R", "url": "ark:/dummy/1", "nome_file": "registro:1901"}]
    out = tmp_path / "out"
    out.mkdir()
    state = {
        "records": records,
        "formats": ["PNG"],
        "output_folder": str(out),
        "output_folders_doc": [],
        "output_folders_reg": [str(out)],
    }

    class MustNotRun(FakeElab):
        def __init__(self, *args, **kwargs):
            raise AssertionError("L'elaborazione non deve iniziare")

    monkeypatch.setattr(elab_mod, "Elaborazione", MustNotRun)
    result = elab_mod.esegui_elaborazione(state, records=records, formats=["PNG"])

    assert result[0]["status"] == "ERROR"
    assert result[0]["path_preflight"]["profile"] in {"windows_desktop", "modern_filesystem"}
    assert result[0]["path_preflight"]["issues"][0]["code"] == "invalid_character"
