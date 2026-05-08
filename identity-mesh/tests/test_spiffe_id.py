import pytest
from identity_mesh import SPIFFEID


def test_parse_basic():
    s = SPIFFEID.parse("spiffe://example.org/workload/agent-1")
    assert s.trust_domain == "example.org"
    assert s.path == "/workload/agent-1"


def test_parse_root_path():
    s = SPIFFEID.parse("spiffe://example.org/")
    assert s.path == "/"


def test_invalid_scheme():
    with pytest.raises(ValueError):
        SPIFFEID.parse("https://example.org/foo")


def test_missing_trust_domain():
    with pytest.raises(ValueError):
        SPIFFEID.parse("spiffe:///path")


def test_str_round_trip():
    original = "spiffe://prod.kineticgain.com/workload/agent-x"
    assert str(SPIFFEID.parse(original)) == original


def test_matches_trust_domain():
    s = SPIFFEID.parse("spiffe://prod.kineticgain.com/x")
    assert s.matches_trust_domain("prod.kineticgain.com")
    assert not s.matches_trust_domain("staging.kineticgain.com")


def test_is_under():
    s = SPIFFEID.parse("spiffe://prod.kineticgain.com/workload/research-agent-1")
    assert s.is_under("/workload/research-")
    assert not s.is_under("/workload/admin-")
