from modules import lab_bridge


def test_run_recon_task_accepts_allowed_nmap(monkeypatch):
    monkeypatch.setattr(lab_bridge, "require_user_approval", lambda *args, **kwargs: (True, "Approved"))

    class FakeStdout:
        def read(self):
            return b"PORT   STATE SERVICE\n22/tcp open ssh\n"

    class FakeStderr:
        def read(self):
            return b""

    class FakeClient:
        def exec_command(self, command, timeout=90):
            return None, FakeStdout(), FakeStderr()

        def close(self):
            pass

    monkeypatch.setattr(lab_bridge, "_create_ssh_client", lambda: FakeClient())

    result = lab_bridge.run_recon_task("nmap", "127.0.0.1", extra_args="-sV --top-ports 20")

    assert "nmap" in result.lower()
    assert "127.0.0.1" in result
    assert "ssh" in result.lower()


def test_run_recon_task_rejects_unknown_action():
    result = lab_bridge.run_recon_task("unknown_task", "127.0.0.1")

    assert "unsupported task" in result.lower()
    assert "allowed tasks" in result.lower()


def test_run_recon_task_rejects_shell_syntax_in_extra_args(monkeypatch):
    monkeypatch.setattr(lab_bridge, "require_user_approval", lambda *args, **kwargs: (True, "Approved"))

    result = lab_bridge.run_recon_task("nmap", "127.0.0.1", extra_args="-sV; whoami")

    assert "blocked shell syntax" in result.lower()


def test_run_recon_task_rejects_extra_target_arguments(monkeypatch):
    monkeypatch.setattr(lab_bridge, "require_user_approval", lambda *args, **kwargs: (True, "Approved"))

    result = lab_bridge.run_recon_task("nmap", "127.0.0.1", extra_args="-sV 10.0.0.1")

    assert "extra targets" in result.lower()
