"""Distributed Lock with Monotonic Fencing Tokens.
100% Python Standard Library.
"""

import time
from typing import Dict, Any, Optional

class DistributedLockFencingToken:
    """Distributed lock manager issuing strictly monotonic fencing tokens to prevent split-brain writes."""

    def __init__(self):
        self._lock_holder: Optional[str] = None
        self._fencing_token: int = 0
        self._expires_at: float = 0.0

    def acquire(self, client_id: str, ttl_seconds: float = 10.0) -> Dict[str, Any]:
        now = time.time()
        if self._lock_holder is not None and now < self._expires_at:
            if self._lock_holder == client_id:
                self._expires_at = now + ttl_seconds
                return {"acquired": True, "fencing_token": self._fencing_token, "client_id": client_id, "ttl": ttl_seconds}
            return {"acquired": False, "holder": self._lock_holder, "expires_in": round(max(0.0, self._expires_at - now), 2)}

        self._lock_holder = client_id
        self._fencing_token += 1
        self._expires_at = now + ttl_seconds
        return {
            "acquired": True,
            "fencing_token": self._fencing_token,
            "client_id": client_id,
            "ttl": ttl_seconds
        }

    def release(self, client_id: str, fencing_token: int) -> bool:
        if self._lock_holder == client_id and self._fencing_token == fencing_token:
            self._lock_holder = None
            self._expires_at = 0.0
            return True
        return False

    def validate_action(self, fencing_token: int) -> bool:
        return fencing_token == self._fencing_token and time.time() < self._expires_at
