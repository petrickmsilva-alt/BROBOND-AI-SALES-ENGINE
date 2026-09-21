"""Domain rule tests."""

import pytest

from app.domain.entities.lead import Lead, LeadStatus


def test_apply_score_qualifies_lead() -> None:
    lead = Lead(name="Ana", email="ana@acme.com")
    lead.apply_score(80, "Strong ICP fit")
    assert lead.status is LeadStatus.QUALIFIED
    assert lead.score == 80


def test_apply_score_rejects_out_of_range() -> None:
    lead = Lead(name="Ana", email="ana@acme.com")
    with pytest.raises(ValueError, match="between 0 and 100"):
        lead.apply_score(150)
