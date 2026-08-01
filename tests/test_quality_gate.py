from scripts import quality_gate
from scripts import verify_release_hygiene as hygiene


def test_smoke_gate_uses_targeted_test_subset():
    commands = quality_gate.commands_for("smoke")

    assert commands[-1] == quality_gate.SMOKE_TESTS
    assert "tests/test_manifest_utils.py" in commands[-1]
    assert [quality_gate.PYTHON, "scripts/verify_release_hygiene.py"] in commands


def test_release_gate_uses_full_pytest_suite():
    commands = quality_gate.commands_for("release")

    assert commands[-1] == [quality_gate.PYTHON, "-m", "pytest", "-q"]
    assert quality_gate.COMPILE_CHECK in commands


def test_gate_stops_at_first_failed_command(monkeypatch):
    calls = []

    class Result:
        def __init__(self, returncode):
            self.returncode = returncode

    def fake_run(command, **_kwargs):
        calls.append(command)
        return Result(7 if len(calls) == 2 else 0)

    monkeypatch.setattr(quality_gate.subprocess, "run", fake_run)

    assert quality_gate.run_gate("smoke") == 7
    assert len(calls) == 2


def test_hygiene_generated_path_classification():
    assert hygiene._looks_generated("build/ATK-Pro/app.exe")
    assert hygiene._looks_generated("atkpro_debug.log.2")
    assert hygiene._looks_generated("outputs/smoke/manifest.json")
    assert not hygiene._looks_generated("src/main.py")
    assert not hygiene._looks_generated("docs_generali/roadmap_portali_ATK-Pro.md")
