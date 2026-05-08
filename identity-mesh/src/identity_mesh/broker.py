"""Identity broker - issues short-lived JWT-SVIDs to registered workloads."""
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from .spiffe_id import SPIFFEID


@dataclass
class IdentityBroker:
    """Mints JWT-SVIDs. One broker = one trust domain = one signing key."""
    trust_domain: str
    default_ttl: int = 300  # 5 min
    _key: Optional[RSAPrivateKey] = field(default=None, init=False, repr=False)
    _key_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    _private_pem: bytes = field(default=b"", init=False, repr=False)
    _registered: Dict[str, SPIFFEID] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if not self.trust_domain:
            raise ValueError("trust_domain is required")
        if self._key is None:
            self._key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._private_pem = self._key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    @property
    def key_id(self) -> str:
        return self._key_id

    def register_workload(self, name: str) -> SPIFFEID:
        if not name or "/" in name:
            raise ValueError(f"Invalid workload name: {name!r}")
        spiffe_id = SPIFFEID(trust_domain=self.trust_domain, path=f"/workload/{name}")
        self._registered[name] = spiffe_id
        return spiffe_id

    def issue_svid(self, workload_name: str, audience: str, ttl: Optional[int] = None) -> str:
        if workload_name not in self._registered:
            raise ValueError(f"Workload not registered: {workload_name!r}")
        if not audience:
            raise ValueError("audience is required")

        spiffe_id = self._registered[workload_name]
        now = int(time.time())
        ttl = ttl if ttl is not None else self.default_ttl

        claims = {
            "iss": f"spiffe://{self.trust_domain}",
            "sub": str(spiffe_id),
            "aud": audience,
            "iat": now,
            "exp": now + ttl,
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(
            claims, self._private_pem, algorithm="RS256",
            headers={"kid": self._key_id, "typ": "JWT"},
        )

    def public_key_pem(self) -> bytes:
        assert self._key is not None
        return self._key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def trust_bundle(self) -> Dict[str, bytes]:
        """Return {kid: public_pem} - what verifiers consume."""
        return {self._key_id: self.public_key_pem()}
