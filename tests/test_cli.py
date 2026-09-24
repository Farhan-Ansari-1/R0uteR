from cli import main


def test_cli_runs_and_prints_report(monkeypatch, capsys):
    def fake_execute_recon_pipeline(target, task_name, extra_args=""):
        return {
            "success": True,
            "target": target,
            "summary": "Open ports: 22, 80",
            "next_steps": ["Review SSH", "Inspect web service"],
            "raw_output": "PORT 22 open ssh\nPORT 80 open http",
        }

    monkeypatch.setattr("cli.execute_recon_pipeline", fake_execute_recon_pipeline)
    monkeypatch.setattr("cli.EvidenceStore.save_entry", lambda *args, **kwargs: 1)

    import sys
    monkeypatch.setattr(sys, "argv", ["cli.py", "--target", "127.0.0.1"])

    main()

    captured = capsys.readouterr()
    assert "127.0.0.1" in captured.out
    assert "Review SSH" in captured.out


def test_cli_uses_local_model_when_configured(monkeypatch, capsys):
    monkeypatch.setenv("ROUTER_AI_PROVIDER", "ollama")
    monkeypatch.setattr(
        "cli.execute_recon_pipeline",
        lambda target, task_name, extra_args="": {
            "success": True,
            "summary": "Open ports: 22",
            "next_steps": ["Review SSH"],
            "raw_output": "22/tcp open ssh",
        },
    )
    monkeypatch.setattr("cli.EvidenceStore.save_entry", lambda *args, **kwargs: 1)
    monkeypatch.setattr("cli.EvidenceStore.get_entry", lambda *args, **kwargs: {
        "id": 1, "target": "127.0.0.1", "task": "nmap", "summary": "Open ports: 22",
        "next_steps": ["Review SSH"], "raw_output": "22/tcp open ssh",
    })
    monkeypatch.setattr("cli.LLMAdapter.summarize", lambda self, text: "Local review: SSH only")

    import sys
    monkeypatch.setattr(sys, "argv", ["cli.py", "--target", "127.0.0.1"])
    main()

    assert "Local model review:" in capsys.readouterr().out
