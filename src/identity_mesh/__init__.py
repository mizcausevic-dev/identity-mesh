"""identity-mesh: SPIFFE-style workload identity broker for AI agents."""
from .spiffe_id import SPIFFEID
from .broker import IdentityBroker
from .workload import Workload
from .verifier import Verifier, InvalidSVID
from .rotation import Rotator

__version__ = "0.1.0"
__all__ = [
    "SPIFFEID", "IdentityBroker", "Workload",
    "Verifier", "InvalidSVID", "Rotator",
]
