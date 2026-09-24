from modules.llm_adapter import LLMAdapter


def test_llm_adapter_gemini_summary_is_available():
    adapter = LLMAdapter(preferred_provider="gemini")
    summary = adapter.summarize("PORT 22 open ssh, PORT 80 open http")

    assert "Summary:" in summary
    assert "ssh" in summary.lower()
    assert "http" in summary.lower()


def test_llm_adapter_local_summary_works_for_ollama_mode():
    adapter = LLMAdapter(preferred_provider="ollama")
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"message":{"content":"Local finding summary"}}'

    monkeypatch = __import__("pytest").MonkeyPatch()
    monkeypatch.setattr("modules.llm_adapter.urlopen", lambda *args, **kwargs: FakeResponse())
    try:
        summary = adapter.summarize("Service enumeration complete")
    finally:
        monkeypatch.undo()

    assert summary == "Local finding summary"


def test_llm_adapter_local_summary_falls_back_when_ollama_is_unavailable(monkeypatch):
    def fail_request(*args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr("modules.llm_adapter.urlopen", fail_request)

    summary = LLMAdapter(preferred_provider="ollama").summarize("22/tcp open ssh")

    assert "Local model unavailable" in summary
    assert "22/tcp open ssh" in summary


def test_llm_adapter_hybrid_prefers_gemini_when_available(monkeypatch):
    monkeypatch.setenv("ROUTER_AI_PROVIDER", "hybrid")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def fake_gemini(self, text):
        return "Gemini hybrid summary"

    def fake_local(self, text):
        return "Local hybrid summary"

    monkeypatch.setattr(LLMAdapter, "_gemini_summary", fake_gemini)
    monkeypatch.setattr(LLMAdapter, "_local_summary", fake_local)

    summary = LLMAdapter(preferred_provider="hybrid").summarize("Open port 443")

    assert summary == "Gemini hybrid summary"


def test_llm_adapter_hybrid_falls_back_to_local_when_gemini_unavailable(monkeypatch):
    monkeypatch.setenv("ROUTER_AI_PROVIDER", "hybrid")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    def fail_gemini(*args, **kwargs):
        raise RuntimeError("Gemini unavailable")

    monkeypatch.setattr(LLMAdapter, "_gemini_summary", fail_gemini)
    monkeypatch.setattr(LLMAdapter, "_local_summary", lambda self, text: "Local fallback summary")

    summary = LLMAdapter(preferred_provider="hybrid").summarize("Open port 80")

    assert summary == "Local fallback summary"
