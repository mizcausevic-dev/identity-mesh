import time
import threading
from identity_mesh import Rotator


def test_rotator_invokes_callback():
    counter = {"n": 0}
    lock = threading.Lock()

    def bump():
        with lock:
            counter["n"] += 1

    r = Rotator(interval=0.05, callback=bump)
    r.start()
    time.sleep(0.18)
    r.stop()
    assert counter["n"] >= 2


def test_rotator_swallows_callback_errors():
    def boom():
        raise RuntimeError("nope")

    r = Rotator(interval=0.02, callback=boom)
    r.start()
    time.sleep(0.08)
    r.stop()  # Should not have crashed the thread
