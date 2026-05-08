"""SPIFFE ID parsing and validation per spec."""
from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SPIFFEID:
    """spiffe://<trust-domain><path>"""
    trust_domain: str
    path: str

    def __str__(self) -> str:
        return f"spiffe://{self.trust_domain}{self.path}"

    @classmethod
    def parse(cls, spiffe_id: str) -> "SPIFFEID":
        if not isinstance(spiffe_id, str) or not spiffe_id.startswith("spiffe://"):
            raise ValueError(f"Not a SPIFFE ID: {spiffe_id!r}")
        parsed = urlparse(spiffe_id)
        if parsed.scheme != "spiffe":
            raise ValueError(f"Invalid scheme: {parsed.scheme!r}")
        if not parsed.netloc:
            raise ValueError("Missing trust domain")
        path = parsed.path or "/"
        return cls(trust_domain=parsed.netloc, path=path)

    def matches_trust_domain(self, trust_domain: str) -> bool:
        return self.trust_domain == trust_domain

    def is_under(self, prefix: str) -> bool:
        """Path-prefix check, e.g. /workload/research-* match."""
        return self.path.startswith(prefix)
