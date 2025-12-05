# Loading pulse scene - visual indicator during data fetch
# Ported from FlightTracker for Interstate 75 W

from utilities.animator import Animator
from setup import colours, screen

# Layout constants
LOADING_PULSE_POSITION = (screen.WIDTH - 2, 1)
LOADING_PULSE_COLOUR = colours.WHITE


class LoadingPulseScene:
    def __init__(self):
        super().__init__()

    @Animator.KeyFrame.add(1)
    def loading_pulse(self, count):
        """Flash a pixel to indicate loading activity"""
        # Only show when processing
        if not self.overhead.processing:
            # Clear the indicator
            black_pen = self.display.create_pen(0, 0, 0)
            self.display.set_pen(black_pen)
            self.display.pixel(
                LOADING_PULSE_POSITION[0],
                LOADING_PULSE_POSITION[1]
            )
            return

        # Pulse on/off
        if count % 2:
            pen = self.display.create_pen(
                LOADING_PULSE_COLOUR.red,
                LOADING_PULSE_COLOUR.green,
                LOADING_PULSE_COLOUR.blue
            )
        else:
            pen = self.display.create_pen(0, 0, 0)

        self.display.set_pen(pen)
        self.display.pixel(
            LOADING_PULSE_POSITION[0],
            LOADING_PULSE_POSITION[1]
        )
