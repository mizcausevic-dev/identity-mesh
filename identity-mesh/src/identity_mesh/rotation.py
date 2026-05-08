"""Background rotator - refresh credentials on an interval."""
from __future__ import annotations
import threading
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Rotator:
    """Run callback every interval seconds in a daemon thread."""
    interval: float
    callback: Callable[[], None]
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _thread: Optional[threading.Thread] = field(default=None, init=False)

    def start(self) -> None:
        if self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 1.0) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            try:
                self.callback()
            except Exception:
                # In production, route this to your logger/observer.
                pass
