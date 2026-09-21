from modules.evidence import EvidenceStore


def test_evidence_store_persists_recon_entry(tmp_path):
    store = EvidenceStore(db_path=str(tmp_path / "evidence.db"))

    entry_id = store.save_entry(
        target="127.0.0.1",
        task="nmap",
        summary="SSH and HTTP are exposed",
        next_steps=["review ssh", "inspect web"],
        raw_output="PORT 22/tcp open ssh\nPORT 80/tcp open http",
    )

    assert entry_id is not None
    assert store.list_entries()[-1]["target"] == "127.0.0.1"
    assert "ssh" in store.list_entries()[-1]["summary"].lower()


def test_evidence_store_supports_lookup_filter_and_limit(tmp_path):
    store = EvidenceStore(db_path=str(tmp_path / "evidence.db"))
    first_id = store.save_entry("127.0.0.1", "ping", "Host is reachable", [], "reply")
    store.save_entry("192.168.56.10", "nmap", "HTTP exposed", ["review web"], "80/tcp open http")

    assert store.get_entry(first_id)["task"] == "ping"
    assert store.get_entry(9999) is None
    assert len(store.list_entries(target="127.0.0.1")) == 1
    assert len(store.list_entries(limit=1)) == 1
