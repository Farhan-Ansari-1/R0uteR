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


def test_run_mission_tracks_current_and_next_phase(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "target": target,
            "summary": "Open ports: 22, 80",
            "next_steps": ["Review SSH", "Inspect web service"],
            "raw_output": "PORT 22 open ssh\nPORT 80 open http",
        },
    )
    monkeypatch.setattr("modules.missions.gather_osint", lambda target: {"success": True, "target": target, "results": ["intel ready"]})
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("127.0.0.1")

    assert result["phase"] == "recon"
    assert result["next_phase"] in {"service_validation", "vulnerability_review"}
    assert result["agent"]["phase"] == "recon"
    assert result["agent"]["next_phase"] in {"service_validation", "vulnerability_review"}


def test_run_mission_includes_discovery_summary(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "target": target,
            "summary": "Open ports: 80, 443",
            "next_steps": ["Review web exposure"],
            "raw_output": "https://example.com\nhttps://api.example.com",
        },
    )
    monkeypatch.setattr("modules.missions.gather_osint", lambda target: {"success": True, "target": target, "results": ["intel ready"]})
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("example.com")

    assert result["success"] is True
    assert result["discovery"]["status"] == "success"
    assert "example.com" in result["discovery"]["live_hosts"]


def test_run_mission_reports_agent_next_step(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "target": target,
            "summary": "Open ports: 22, 80",
            "next_steps": ["Review SSH", "Inspect web service"],
            "raw_output": "PORT 22 open ssh\nPORT 80 open http",
        },
    )
    monkeypatch.setattr("modules.missions.gather_osint", lambda target: {"success": True, "target": target, "results": ["intel ready"]})
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("127.0.0.1")

    assert result["success"] is True
    assert result["agent"]["next_tool"] == "nmap"
    assert result["agent"]["goal"] == "recon"


def test_run_mission_does_not_treat_nmap_banner_as_live_host(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "target": target,
            "summary": "Open ports: 22",
            "next_steps": ["Review SSH"],
            "raw_output": "Starting Nmap 7.99 ( https://nmap.org ) at 2026-09-26\nNmap scan report for localhost (127.0.0.1)\nPORT 22 open ssh",
        },
    )
    monkeypatch.setattr("modules.missions.gather_osint", lambda target: {"success": True, "target": target, "results": []})
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("127.0.0.1", include_osint=False)

    assert result["success"] is True
    assert "nmap.org" not in result["discovery"]["live_hosts"]
    assert "127.0.0.1" not in result["discovery"]["live_hosts"]


def test_run_mission_returns_agent_metadata_when_recon_is_blocked(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": False,
            "message": "Approval required before leaking this task.",
            "target": target,
        },
    )

    result = run_mission("127.0.0.1")

    assert result["success"] is False
    assert result["agent"]["status"] == "blocked"
    assert result["agent"]["next_tool"] == "nmap"


def test_run_mission_builds_structured_findings_and_priority(monkeypatch):
    monkeypatch.setattr(
        "modules.missions.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "target": target,
            "summary": "Open ports: 22, 80",
            "next_steps": ["Review SSH", "Inspect web service"],
            "raw_output": "PORT 22 open ssh\nPORT 80 open http",
        },
    )
    monkeypatch.setattr("modules.missions.gather_osint", lambda target: {"success": True, "target": target, "results": ["intel ready"]})
    monkeypatch.setattr("modules.missions.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    result = run_mission("127.0.0.1")

    assert result["success"] is True
    assert len(result["findings"]) >= 2
    assert result["findings"][0]["severity"] in {"high", "medium", "low", "critical"}
    assert "Prioritized findings:" in result["report"]
