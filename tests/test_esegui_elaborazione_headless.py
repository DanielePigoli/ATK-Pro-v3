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
