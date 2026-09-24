from modules.risk_engine import rank_findings, score_finding


def test_score_finding_uses_severity_and_confidence_distinctly():
    score = score_finding({"severity": "critical", "confidence": "high"})
    assert score > 80

    low_score = score_finding({"severity": "low", "confidence": "low"})
    assert low_score < 50


def test_rank_findings_prioritizes_high_confidence_critical_findings():
    findings = [
        {"title": "Low confidence web issue", "severity": "medium", "confidence": "low"},
        {"title": "Critical SSH exposure", "severity": "critical", "confidence": "high"},
        {"title": "Medium web issue", "severity": "medium", "confidence": "medium"},
    ]

    ranked = rank_findings(findings)

    assert ranked[0]["title"] == "Critical SSH exposure"
    assert ranked[0]["risk_score"] >= ranked[1]["risk_score"]
