"""SVID verifier - validates JWT-SVIDs against a trust bundle."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

import jwt
from cryptography.hazmat.primitives import serialization

from .spiffe_id import SPIFFEID


class InvalidSVID(Exception):
    """Raised when a JWT-SVID fails verification."""


@dataclass
class Verifier:
    trust_domain: str
    trust_bundle: Dict[str, bytes]  # {kid: pem}
    leeway: int = 5  # seconds clock skew tolerance

    def verify(self, token: str, expected_audience: str) -> SPIFFEID:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as e:
            raise InvalidSVID(f"Malformed token: {e}") from e

        kid = header.get("kid")
        if not kid or kid not in self.trust_bundle:
            raise InvalidSVID(f"Unknown or missing key id: {kid!r}")

        try:
            public_key = serialization.load_pem_public_key(self.trust_bundle[kid])
            claims = jwt.decode(
                token, public_key,
                algorithms=["RS256"],
                audience=expected_audience,
                issuer=f"spiffe://{self.trust_domain}",
                leeway=self.leeway,
            )
        except jwt.InvalidTokenError as e:
            raise InvalidSVID(str(e)) from e

        sub = claims.get("sub")
        if not sub:
            raise InvalidSVID("Missing sub claim")

        spiffe_id = SPIFFEID.parse(sub)
        if not spiffe_id.matches_trust_domain(self.trust_domain):
            raise InvalidSVID(
                f"Trust domain mismatch: {spiffe_id.trust_domain} != {self.trust_domain}"
            )
        return spiffe_id
