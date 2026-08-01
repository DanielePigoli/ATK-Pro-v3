import os
from pathlib import Path
from src.elaborazione import Elaborazione


def test_enrich_pdf_metadata_called(tmp_path, monkeypatch):
    outdir = tmp_path
    elab = Elaborazione('R', 'ark:/12657/an_ua12345', str(outdir))
    elab.nome_file = 'testname'
    elab.output_dir = str(outdir)

    # Create image files that _generate_register_pdf will inspect
    files = [
        'testname_canvas_1.tif',
    ]
    for f in files:
        p = outdir / f
        p.write_bytes(b'0')

    captured = {}

    def fake_create_pdf_from_images(
        paths, outpath, resolution_dpi=400, resource_profile=None
    ):
        # create a fake pdf
        Path(outpath).write_bytes(b'%PDF')
        return outpath

    def fake_enrich(pdf_path=None, title=None, subject=None, ua=None, ark=None):
        captured['pdf_path'] = pdf_path
        captured['title'] = title
        captured['ua'] = ua
        captured['ark'] = ark

    # Patch functions imported in src.elaborazione
    monkeypatch.setattr('src.elaborazione.create_pdf_from_images', fake_create_pdf_from_images)
    monkeypatch.setattr('src.elaborazione.enrich_pdf_metadata', fake_enrich)

    pdf_path = elab._generate_register_pdf(files)
    assert pdf_path is not None
    assert 'pdf_path' in captured
    assert os.path.exists(captured['pdf_path'])
    assert captured['title'] == elab.nome_file
