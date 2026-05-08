from identity_mesh import IdentityBroker, Workload


def test_workload_caches_per_audience():
    broker = IdentityBroker(trust_domain="example.org")
    w = Workload(name="agent-1", broker=broker)

    t1 = w.get_svid("api")
    t2 = w.get_svid("api")
    assert t1 == t2

    t3 = w.get_svid("other-api")
    assert t3 != t1


def test_invalidate_clears_cache():
    broker = IdentityBroker(trust_domain="example.org")
    w = Workload(name="agent-1", broker=broker)
    t1 = w.get_svid("api")
    w.invalidate("api")
    t2 = w.get_svid("api")
    assert t1 != t2  # New token after invalidate


def test_invalidate_all():
    broker = IdentityBroker(trust_domain="example.org")
    w = Workload(name="agent-1", broker=broker)
    w.get_svid("api1")
    w.get_svid("api2")
    w.invalidate()
    assert w._cached == {}
