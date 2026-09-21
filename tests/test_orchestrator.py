from modules.orchestrator import execute_recon_pipeline
from modules.orchestrator import SafeReconOrchestrator


def test_execute_recon_pipeline_runs_when_authorized(monkeypatch):
    def fake_check_permission(self, action, target=""):
        return True, "Action is authorized for the current scope."

    monkeypatch.setattr(
        "modules.orchestrator.PermissionPolicy.check_permission",
        fake_check_permission,
    )
    monkeypatch.setattr(
        "modules.orchestrator.lab_bridge.run_recon_task",
        lambda task_name, target, extra_args="": "PORT 22/tcp open ssh\nPORT 80/tcp open http",
    )

    result = execute_recon_pipeline("127.0.0.1", "nmap", "-sV --top-ports 20")

    assert result["success"] is True
    assert result["target"] == "127.0.0.1"
    assert "ssh" in result["summary"].lower()
    assert "http" in result["summary"].lower()
    assert isinstance(result["next_steps"], list)


def test_execute_recon_pipeline_blocks_when_not_permitted(monkeypatch):
    def fake_check_permission(self, action, target=""):
        return False, "Target '8.8.8.8' is not in authorized scope."

    monkeypatch.setattr(
        "modules.orchestrator.PermissionPolicy.check_permission",
        fake_check_permission,
    )

    result = execute_recon_pipeline("8.8.8.8", "nmap")

    assert result["success"] is False
    assert "authorized scope" in result["message"].lower()


def test_execute_recon_pipeline_propagates_bridge_failure(monkeypatch):
    monkeypatch.setattr(
        "modules.orchestrator.PermissionPolicy.check_permission",
        lambda self, action, target="": (True, "authorized"),
    )
    monkeypatch.setattr(
        "modules.orchestrator.lab_bridge.run_recon_task",
        lambda task_name, target, extra_args="": "SSH Execution Error: connection refused",
    )

    result = execute_recon_pipeline("127.0.0.1", "nmap")

    assert result["success"] is False
    assert "connection refused" in result["message"].lower()
    assert result["next_steps"] == []


def test_extract_ports_ignores_filtered_ports():
    raw_output = "22/tcp open ssh\n80/tcp filtered http\n3389/tcp closed ms-wbt-server"

    assert SafeReconOrchestrator._extract_ports(raw_output) == ["22"]
