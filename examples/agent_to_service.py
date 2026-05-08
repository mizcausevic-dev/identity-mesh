"""End-to-end example: broker mints an SVID, agent presents it, service verifies."""
from identity_mesh import IdentityBroker, Workload, Verifier


def main() -> None:
    # 1. Security platform team operates the broker
    broker = IdentityBroker(trust_domain="prod.kineticgain.com")

    # 2. Each agent is registered as a workload
    research_agent = Workload(name="research-agent-1", broker=broker)

    # 3. Downstream service is bootstrapped with the trust bundle (public keys)
    service = Verifier(
        trust_domain="prod.kineticgain.com",
        trust_bundle=broker.trust_bundle(),
    )

    # 4. Agent calls a service - gets a fresh, audience-bound SVID
    audience = "https://api.kineticgain.com/v1"
    svid = research_agent.get_svid(audience)
    print(f"Agent SVID (truncated): {svid[:48]}...")

    # 5. Service verifies the caller's identity cryptographically
    caller = service.verify(svid, expected_audience=audience)
    print(f"OK Verified caller: {caller}")

    # 6. Path-prefix authorization - only research-* may call this endpoint
    if caller.is_under("/workload/research-"):
        print("OK Authorized: research workload allowed on this endpoint")
    else:
        print("DENIED: not a research workload")


if __name__ == "__main__":
    main()
