# Flight details scene - displays flight number and flight counter
# Ported from FlightTracker for Interstate 75 W

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout constants - matching original project
# Original: BAR at y=18, FLIGHT_NO at baseline y=21 (fonts.small 5x8)
# Original: DATA_INDEX at baseline y=21 (fonts.extrasmall 4x6)
BAR_STARTING_POSITION = (0, 20)  # Moved down 1 more pixel
BAR_PADDING = 2

FLIGHT_NO_POSITION = (1, 14)  # Keep text position
FLIGHT_NO_TEXT_HEIGHT = 12  # Increased by 2 more pixels
FLIGHT_NO_FONT = fonts.REGULAR  # Larger font (bitmap8)
FLIGHT_NO_FONT_SCALE = fonts.REGULAR_SCALE

FLIGHT_NUMBER_ALPHA_COLOUR = colours.ORANGE
FLIGHT_NUMBER_NUMERIC_COLOUR = colours.YELLOW

DATA_INDEX_POSITION = (52, 15)  # PicoGraphics top of text: 21 - 6 = 15
DATA_INDEX_TEXT_HEIGHT = 6
DATA_INDEX_FONT = fonts.EXTRASMALL
DATA_INDEX_FONT_SCALE = fonts.EXTRASMALL_SCALE

DIVIDING_BAR_COLOUR = colours.GREEN
DATA_INDEX_COLOUR = colours.GREY


class FlightDetailsScene:
    def __init__(self):
        super().__init__()

    @Animator.KeyFrame.add(0)
    def flight_details(self):
        """Draw flight number and index counter"""
        # Guard against no data
        if len(self._data) == 0:
            return

        # Clear the whole bar area
        self.draw_square(
            0,
            BAR_STARTING_POSITION[1] - (FLIGHT_NO_TEXT_HEIGHT // 2),
            screen.WIDTH - 1,
            BAR_STARTING_POSITION[1] + (FLIGHT_NO_TEXT_HEIGHT // 2),
            colours.BLACK,
        )

        # Set font for flight number
        self.display.set_font(FLIGHT_NO_FONT)

        # Draw flight number if available, fall back to callsign
        flight_no_text_length = 0
        flight_number = self._data[self._data_index].get("flight_number", "")
        if not flight_number or flight_number == "N/A":
            flight_number = self._data[self._data_index].get("callsign", "")

        if flight_number and flight_number != "N/A":
            # Draw each character with appropriate colour
            x_pos = FLIGHT_NO_POSITION[0]

            for ch in flight_number:
                # Select colour based on character type
                # Note: MicroPython strings don't have isnumeric(), use character check
                if ch in "0123456789":
                    colour = FLIGHT_NUMBER_NUMERIC_COLOUR
                else:
                    colour = FLIGHT_NUMBER_ALPHA_COLOUR

                pen = self.display.create_pen(colour.red, colour.green, colour.blue)
                self.display.set_pen(pen)

                self.display.text(ch, x_pos, FLIGHT_NO_POSITION[1], scale=FLIGHT_NO_FONT_SCALE)
                char_width = self.display.measure_text(ch, scale=FLIGHT_NO_FONT_SCALE)
                x_pos += char_width
                flight_no_text_length += char_width

        # Draw dividing bar and flight counter
        bar_pen = self.display.create_pen(
            DIVIDING_BAR_COLOUR.red,
            DIVIDING_BAR_COLOUR.green,
            DIVIDING_BAR_COLOUR.blue
        )
        self.display.set_pen(bar_pen)

        if len(self._data) > 1:
            # Clear area where counter goes
            self.draw_square(
                DATA_INDEX_POSITION[0] - BAR_PADDING,
                BAR_STARTING_POSITION[1] - (FLIGHT_NO_TEXT_HEIGHT // 2),
                screen.WIDTH,
                BAR_STARTING_POSITION[1] + (FLIGHT_NO_TEXT_HEIGHT // 2),
                colours.BLACK,
            )

            # Draw flight counter (N/M)
            self.display.set_font(DATA_INDEX_FONT)
            counter_pen = self.display.create_pen(
                DATA_INDEX_COLOUR.red,
                DATA_INDEX_COLOUR.green,
                DATA_INDEX_COLOUR.blue
            )
            self.display.set_pen(counter_pen)

            counter_text = f"{self._data_index + 1}/{len(self._data)}"
            # Right-align counter to prevent overflow
            counter_width = self.display.measure_text(counter_text, scale=DATA_INDEX_FONT_SCALE)
            counter_x = screen.WIDTH - counter_width - 1
            self.display.text(
                counter_text,
                counter_x,
                DATA_INDEX_POSITION[1],
                scale=DATA_INDEX_FONT_SCALE
            )

            # Draw dividing bar between callsign and counter
            self.display.set_pen(bar_pen)
            self.display.line(
                flight_no_text_length + BAR_PADDING,
                BAR_STARTING_POSITION[1],
                counter_x - BAR_PADDING - 1,
                BAR_STARTING_POSITION[1]
            )
        else:
            # Just draw the bar across
            bar_start = flight_no_text_length + BAR_PADDING if flight_no_text_length else 0
            self.display.line(
                bar_start,
                BAR_STARTING_POSITION[1],
                screen.WIDTH,
                BAR_STARTING_POSITION[1]
            )
