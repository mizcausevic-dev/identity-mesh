"""Workload - agent identity holder with cached/refreshed SVIDs."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import jwt as pyjwt

from .broker import IdentityBroker
from .spiffe_id import SPIFFEID


@dataclass
class Workload:
    name: str
    broker: IdentityBroker
    spiffe_id: SPIFFEID = field(init=False)
    _cached: Dict[str, Tuple[str, float]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.spiffe_id = self.broker.register_workload(self.name)

    def get_svid(self, audience: str, refresh_before: int = 60) -> str:
        """Return cached SVID if not within refresh_before seconds of expiry, else mint fresh."""
        now = time.time()
        cached = self._cached.get(audience)
        if cached is not None:
            token, exp = cached
            if exp - now > refresh_before:
                return token

        token = self.broker.issue_svid(self.name, audience)
        claims = pyjwt.decode(token, options={"verify_signature": False})
        self._cached[audience] = (token, float(claims["exp"]))
        return token

    def invalidate(self, audience: Optional[str] = None) -> None:
        if audience is None:
            self._cached.clear()
        else:
            self._cached.pop(audience, None)
