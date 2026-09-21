from modules.permissions import PermissionPolicy


def test_recon_allows_authorized_lab_target():
    policy = PermissionPolicy.from_env(
        allowed_targets="localhost,127.0.0.1,192.168.56.0/24",
        allowed_actions="recon,osint,run_command"
    )

    allowed, reason = policy.check_permission("recon", "127.0.0.1")

    assert allowed is True
    assert "authorized" in reason.lower()


def test_recon_rejects_out_of_scope_target():
    policy = PermissionPolicy.from_env(
        allowed_targets="localhost,127.0.0.1",
        allowed_actions="recon,osint,run_command"
    )

    allowed, reason = policy.check_permission("recon", "8.8.8.8")

    assert allowed is False
    assert "not in authorized scope" in reason.lower()


def test_destructive_actions_are_blocked_by_default():
    policy = PermissionPolicy.from_env(
        allowed_targets="localhost,127.0.0.1",
        allowed_actions="recon,osint,run_command"
    )

    allowed, _ = policy.check_permission("destructive_action", "127.0.0.1")

    assert allowed is False


def test_permission_policy_uses_lab_scope_when_allowed_scope_is_unset(monkeypatch):
    monkeypatch.delenv("ROUTER_ALLOWED_TARGETS", raising=False)
    monkeypatch.setenv("ROUTER_LAB_TARGETS", "127.0.0.1,192.168.44.0/24")

    policy = PermissionPolicy(allowed_actions="recon")

    allowed, _ = policy.check_permission("recon", "192.168.44.129")

    assert allowed is True
