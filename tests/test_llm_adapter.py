from modules.llm_adapter import LLMAdapter


def test_llm_adapter_prefers_gemini_summary_by_default():
    adapter = LLMAdapter()
    summary = adapter.summarize("PORT 22 open ssh, PORT 80 open http")

    assert "Summary:" in summary
    assert "ssh" in summary.lower()
    assert "http" in summary.lower()


def test_llm_adapter_local_summary_works_for_ollama_mode():
    adapter = LLMAdapter(preferred_provider="ollama")
    summary = adapter.summarize("Service enumeration complete")

    assert "Local summary:" in summary
    assert "enumeration" in summary.lower()
