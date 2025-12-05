# Animation framework for Interstate 75 W
# Adapted from original FlightTracker for MicroPython

import time

DELAY_DEFAULT = 0.1  # 100ms default delay

# Global registry for keyframe metadata
# MicroPython can have issues setting attributes on functions
_keyframe_registry = {}


def keyframe(divisor, offset=0):
    """
    Decorator to mark a method as a keyframe.

    Args:
        divisor: Run method every N frames (0 = run once on reset)
        offset: Frame offset before first run
    """
    def decorator(func):
        # Use function name as key for the registry
        key = func.__name__
        _keyframe_registry[key] = {
            "divisor": divisor,
            "offset": offset,
            "count": 0
        }
        return func
    return decorator


class Animator:
    """
    Keyframe-based animation system for MicroPython.

    Uses decorator pattern to register methods that run at specific intervals.
    Divisor determines how often a method runs (every N frames).
    """

    # Alias for backwards compatibility with @Animator.KeyFrame.add syntax
    class KeyFrame:
        add = staticmethod(keyframe)

    def __init__(self):
        self.keyframes = []
        self.frame = 0
        self._delay = DELAY_DEFAULT
        self._reset_scene = True

        self._register_keyframes()

    def _register_keyframes(self):
        """Find and register all methods that are keyframes"""
        for methodname in dir(self):
            if methodname in _keyframe_registry:
                method = getattr(self, methodname)
                if callable(method):
                    self.keyframes.append((methodname, method))

    def _get_props(self, name):
        """Get keyframe properties by method name"""
        return _keyframe_registry.get(name, {"divisor": 1, "offset": 0, "count": 0})

    def reset_scene(self):
        """Reset all keyframes with divisor == 0"""
        for name, method in self.keyframes:
            props = self._get_props(name)
            if props["divisor"] == 0:
                method()

    def play(self):
        """Main animation loop - runs forever"""
        while True:
            for name, method in self.keyframes:
                props = self._get_props(name)

                # If divisor == 0 then only run once on first loop
                if self.frame == 0:
                    if props["divisor"] == 0:
                        method()

                # Otherwise perform normal operation
                if (
                    self.frame > 0
                    and props["divisor"]
                    and not (
                        (self.frame - props["offset"])
                        % props["divisor"]
                    )
                ):
                    result = method(props["count"])
                    if result:
                        props["count"] = 0
                    else:
                        props["count"] += 1

            self._reset_scene = False
            self.frame += 1
            time.sleep(self._delay)

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        self._delay = value
