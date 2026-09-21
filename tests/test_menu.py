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
