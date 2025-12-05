# Clock scene - displays time when no flights
# Ported from FlightTracker for Interstate 75 W

import time
import machine

from utilities.animator import Animator
from setup import colours, fonts, frames

# Layout constants - matching original project
# Original uses fonts.regular (6x12) at baseline y=8
CLOCK_FONT = fonts.REGULAR
CLOCK_FONT_SCALE = fonts.REGULAR_SCALE
CLOCK_POSITION = (1, 1)  # PicoGraphics uses top of text, not baseline
CLOCK_COLOUR = colours.BLUE_DARK


class ClockScene:
    def __init__(self):
        super().__init__()
        self._last_time = None

    def _get_current_time(self):
        """Get current time as HH:MM string"""
        rtc = machine.RTC()
        datetime = rtc.datetime()
        # datetime format: (year, month, day, weekday, hour, minute, second, subsecond)
        hour = datetime[4]
        minute = datetime[5]
        return f"{hour:02d}:{minute:02d}"

    @Animator.KeyFrame.add(frames.PER_SECOND * 1)
    def clock(self, count):
        """Draw clock when no flight data"""
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_time = None
            return

        # Get current time
        current_time = self._get_current_time()

        # Only draw if time has changed
        if self._last_time != current_time:
            # Undraw previous time if different
            if self._last_time is not None:
                self.display.set_font(CLOCK_FONT)
                black_pen = self.display.create_pen(0, 0, 0)
                self.display.set_pen(black_pen)
                self.display.text(
                    self._last_time,
                    CLOCK_POSITION[0],
                    CLOCK_POSITION[1],
                    scale=CLOCK_FONT_SCALE
                )

            self._last_time = current_time

            # Draw new time
            self.display.set_font(CLOCK_FONT)
            pen = self.display.create_pen(
                CLOCK_COLOUR.red,
                CLOCK_COLOUR.green,
                CLOCK_COLOUR.blue
            )
            self.display.set_pen(pen)
            self.display.text(
                current_time,
                CLOCK_POSITION[0],
                CLOCK_POSITION[1],
                scale=CLOCK_FONT_SCALE
            )
