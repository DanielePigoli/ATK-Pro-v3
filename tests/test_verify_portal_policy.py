from __future__ import annotations

import json
import sys

import verify_portal_policy as vpp


def test_write_template_mode_writes_local_policy_file(tmp_path, monkeypatch, capsys):
    output_path = tmp_path / "portal_policy_overrides.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_portal_policy.py", "--local-policy", str(output_path), "--write-template"],
    )

    exit_code = vpp.main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert "portals" in data
    assert "antenati" in data["portals"]
    assert "Template written:" in captured.out


def test_strict_mode_fails_when_static_policies_are_stale(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_portal_policy.py", "--strict", "--today", "2027-12-31"],
    )

    exit_code = vpp.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "RECHECK" in captured.out
    assert "portal policies need re-check" in captured.out


def test_invalid_local_policy_json_returns_error(tmp_path, monkeypatch, capsys):
    invalid_path = tmp_path / "portal_policy_overrides.json"
    invalid_path.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_portal_policy.py", "--local-policy", str(invalid_path)],
    )

    exit_code = vpp.main()

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "not valid JSON" in captured.out
