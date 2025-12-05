# Date scene - displays date when no flights
# Ported from FlightTracker for Interstate 75 W

import machine

from utilities.animator import Animator
from setup import colours, fonts, frames

# Layout constants - matching original project
# Original uses fonts.small (5x8) at baseline y=31
DATE_FONT = fonts.SMALL
DATE_FONT_SCALE = fonts.SMALL_SCALE
DATE_POSITION = (1, 25)  # PicoGraphics uses top of text; 31 - 6 = 25
DATE_COLOUR = colours.PINK_DARKER  # Original uses PINK_DARKER


class DateScene:
    def __init__(self):
        super().__init__()
        self._last_date = None

    def _get_current_date(self):
        """Get current date as string matching original format: d-m-YYYY"""
        rtc = machine.RTC()
        dt = rtc.datetime()
        # datetime format: (year, month, day, weekday, hour, minute, second, subsecond)
        year = dt[0]
        month = dt[1]
        day = dt[2]
        return f"{day}-{month}-{year}"

    @Animator.KeyFrame.add(0)
    def date_display(self):
        """Draw date when no flight data"""
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_date = None
            return

        # Get current date
        current_date = self._get_current_date()

        # Only draw if date has changed
        if self._last_date != current_date:
            # Undraw previous date if different
            if self._last_date is not None:
                self.display.set_font(DATE_FONT)
                black_pen = self.display.create_pen(0, 0, 0)
                self.display.set_pen(black_pen)
                self.display.text(
                    self._last_date,
                    DATE_POSITION[0],
                    DATE_POSITION[1],
                    scale=DATE_FONT_SCALE
                )

            self._last_date = current_date

            # Draw new date
            self.display.set_font(DATE_FONT)
            pen = self.display.create_pen(
                DATE_COLOUR.red,
                DATE_COLOUR.green,
                DATE_COLOUR.blue
            )
            self.display.set_pen(pen)
            self.display.text(
                current_date,
                DATE_POSITION[0],
                DATE_POSITION[1],
                scale=DATE_FONT_SCALE
            )
