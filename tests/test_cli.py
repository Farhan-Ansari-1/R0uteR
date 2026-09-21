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
