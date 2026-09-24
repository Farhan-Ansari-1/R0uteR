from modules.menu import show_menu


def test_show_menu_handles_saved_evidence(monkeypatch, capsys):
    inputs = iter(["2"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    class FakeStore:
        def list_entries(self):
            return [{
                "id": 1,
                "target": "127.0.0.1",
                "task": "nmap",
                "summary": "SSH is exposed",
                "next_steps": ["Review ssh"],
            }]

    monkeypatch.setattr("modules.menu.EvidenceStore", FakeStore)

    show_menu()
    captured = capsys.readouterr()
    assert "127.0.0.1" in captured.out
    assert "SSH is exposed" in captured.out


def test_show_menu_exports_report_and_local_review(monkeypatch, capsys, tmp_path):
    inputs = iter(["1", "127.0.0.1", "nmap", "-sV"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))
    monkeypatch.setenv("ROUTER_AI_PROVIDER", "ollama")

    monkeypatch.setattr(
        "modules.menu.execute_recon_pipeline",
        lambda target, task, extra_args: {
            "success": True,
            "summary": "Open ports: 22",
            "next_steps": ["Review SSH"],
            "raw_output": "22/tcp open ssh",
        },
    )

    class FakeStore:
        def save_entry(self, **kwargs):
            return 9

        def get_entry(self, entry_id):
            return {
                "id": entry_id,
                "target": "127.0.0.1",
                "task": "nmap",
                "summary": "Open ports: 22",
                "next_steps": ["Review SSH"],
                "raw_output": "22/tcp open ssh",
            }

    monkeypatch.setattr("modules.menu.EvidenceStore", FakeStore)
    monkeypatch.setattr("modules.menu.LLMAdapter.summarize", lambda self, text: "SSH only")
    monkeypatch.chdir(tmp_path)

    show_menu()

    captured = capsys.readouterr()
    assert "Local model review:" in captured.out
    assert "reports" in captured.out
