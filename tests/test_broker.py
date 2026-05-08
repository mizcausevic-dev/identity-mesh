import time
import pytest
from identity_mesh import IdentityBroker, Verifier, InvalidSVID


def test_issue_and_verify_round_trip():
    broker = IdentityBroker(trust_domain="example.org")
    broker.register_workload("agent-1")
    token = broker.issue_svid("agent-1", audience="api.example.org")

    verifier = Verifier(trust_domain="example.org", trust_bundle=broker.trust_bundle())
    spiffe_id = verifier.verify(token, expected_audience="api.example.org")
    assert str(spiffe_id) == "spiffe://example.org/workload/agent-1"


def test_unregistered_workload_rejected():
    broker = IdentityBroker(trust_domain="example.org")
    with pytest.raises(ValueError):
        broker.issue_svid("ghost", audience="api")


def test_audience_mismatch_rejected():
    broker = IdentityBroker(trust_domain="example.org")
    broker.register_workload("agent-1")
    token = broker.issue_svid("agent-1", audience="api.example.org")
    verifier = Verifier(trust_domain="example.org", trust_bundle=broker.trust_bundle())
    with pytest.raises(InvalidSVID):
        verifier.verify(token, expected_audience="wrong.audience")


def test_expired_token_rejected():
    broker = IdentityBroker(trust_domain="example.org")
    broker.register_workload("agent-1")
    token = broker.issue_svid("agent-1", audience="api", ttl=1)
    time.sleep(2)
    verifier = Verifier(trust_domain="example.org", trust_bundle=broker.trust_bundle(), leeway=0)
    with pytest.raises(InvalidSVID):
        verifier.verify(token, expected_audience="api")


def test_wrong_trust_bundle_rejected():
    broker_a = IdentityBroker(trust_domain="prod.example.org")
    broker_a.register_workload("agent-1")
    token = broker_a.issue_svid("agent-1", audience="api")

    broker_b = IdentityBroker(trust_domain="prod.example.org")
    verifier = Verifier(trust_domain="prod.example.org", trust_bundle=broker_b.trust_bundle())
    with pytest.raises(InvalidSVID):
        verifier.verify(token, expected_audience="api")


def test_invalid_workload_name():
    broker = IdentityBroker(trust_domain="example.org")
    with pytest.raises(ValueError):
        broker.register_workload("bad/name")
    with pytest.raises(ValueError):
        broker.register_workload("")
