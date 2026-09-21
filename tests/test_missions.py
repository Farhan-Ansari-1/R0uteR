from modules.missions import run_mission


def test_run_mission_completes_with_recon_and_report(monkeypatch):
    def fake_execute_recon_pipeline(target, task_name, extra_args=""):
        return {
            "success": True,
            "target": target,
            "summary": "Open ports: 22, 80",
            "next_steps": ["Review SSH", "Inspect web service"],
            "raw_output": "PORT 22 open ssh\nPORT 80 open http",
        }

    monkeypatch.setattr("modules.missions.execute_recon_pipeline", fake_execute_recon_pipeline)
    monkeypatch.setattr("modules.missions.gather_osint", lambda target: {"success": True, "target": target, "results": ["public intel ready"]})
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("127.0.0.1")

    assert result["success"] is True
    assert result["target"] == "127.0.0.1"
    assert "Open ports" in result["report"]
    assert "Review SSH" in result["report"]


def test_run_mission_can_skip_osint(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "target": target,
            "summary": "Open ports: 22",
            "next_steps": ["Review SSH"],
            "raw_output": "PORT 22 open ssh",
        },
    )
    monkeypatch.setattr(
        "modules.missions.gather_osint",
        lambda target: (_ for _ in ()).throw(AssertionError("OSINT should be skipped")),
    )
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("127.0.0.1", include_osint=False)

    assert result["success"] is True
    assert result["osint"]["skipped"] is True
