# Date scene - displays date when no flights
# Ported from FlightTracker for Interstate 75 W

import machine

from utilities.animator import Animator
from setup import colours, fonts, frames

# Layout constants
DATE_FONT = fonts.REGULAR
DATE_FONT_SCALE = fonts.REGULAR_SCALE
DATE_POSITION = (1, 16)  # Below clock (XLARGE is 14px)
DATE_COLOUR = colours.PINK_DARKER

# Day names
DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class DateScene:
    def __init__(self):
        super().__init__()
        self._last_date = None

    def _get_current_date(self):
        """Get current date as string with day of week: Day d/m"""
        rtc = machine.RTC()
        dt = rtc.datetime()
        # datetime format: (year, month, day, weekday, hour, minute, second, subsecond)
        month = dt[1]
        day = dt[2]
        weekday = dt[3]  # 0=Monday, 6=Sunday
        day_name = DAYS_OF_WEEK[weekday]
        return f"{day_name} {day}/{month}"

    @Animator.KeyFrame.add(1)
    def date_display(self, count):
        """Draw date when no flight data"""
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_date = None
            return

        # Get current date
        current_date = self._get_current_date()

        # Only draw if date has changed (or first draw)
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
