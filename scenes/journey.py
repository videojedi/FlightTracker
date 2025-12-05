# Journey scene - displays origin and destination airports
# Ported from FlightTracker for Interstate 75 W

from utilities.animator import Animator
from setup import colours, fonts, screen

# Configuration
try:
    from config import JOURNEY_CODE_SELECTED
except ImportError:
    JOURNEY_CODE_SELECTED = "GLA"

try:
    from config import JOURNEY_BLANK_FILLER
except ImportError:
    JOURNEY_BLANK_FILLER = " ? "

# Layout constants - matching original project
JOURNEY_POSITION = (0, 0)
JOURNEY_HEIGHT = 11  # Reduced by 1 pixel (moved up)
JOURNEY_WIDTH = 64
JOURNEY_SPACING = 16
JOURNEY_FONT = fonts.LARGE
JOURNEY_FONT_SCALE = fonts.LARGE_SCALE
JOURNEY_FONT_SELECTED = fonts.LARGE_BOLD
JOURNEY_FONT_SELECTED_SCALE = fonts.LARGE_BOLD_SCALE
JOURNEY_COLOUR = colours.YELLOW

ARROW_COLOUR = colours.ORANGE
ARROW_POINT_POSITION = (34, 6)  # Moved up 1 pixel
ARROW_WIDTH = 4
ARROW_HEIGHT = 8


class JourneyScene:
    def __init__(self):
        super().__init__()

    @Animator.KeyFrame.add(1)
    def journey(self, count):
        """Draw origin and destination airport codes (after arrow clears its area)"""
        # Guard against no data
        if len(self._data) == 0:
            return

        origin = self._data[self._data_index]["origin"]
        destination = self._data[self._data_index]["destination"]

        # Draw background
        self.draw_square(
            JOURNEY_POSITION[0],
            JOURNEY_POSITION[1],
            JOURNEY_POSITION[0] + JOURNEY_WIDTH - 1,
            JOURNEY_POSITION[1] + JOURNEY_HEIGHT - 1,
            colours.BLACK,
        )

        # Create pen for journey colour
        pen = self.display.create_pen(
            JOURNEY_COLOUR.red,
            JOURNEY_COLOUR.green,
            JOURNEY_COLOUR.blue
        )
        self.display.set_pen(pen)

        # Draw origin - use bold font if it matches selected airport
        origin_text = origin if origin else JOURNEY_BLANK_FILLER
        origin_selected = origin == JOURNEY_CODE_SELECTED
        origin_font = JOURNEY_FONT_SELECTED if origin_selected else JOURNEY_FONT
        origin_scale = JOURNEY_FONT_SELECTED_SCALE if origin_selected else JOURNEY_FONT_SCALE

        self.display.set_font(origin_font)
        self.display.text(origin_text, 1, 1, scale=origin_scale)

        # Draw destination - use bold font if it matches selected airport
        dest_text = destination if destination else JOURNEY_BLANK_FILLER
        dest_selected = destination == JOURNEY_CODE_SELECTED
        dest_font = JOURNEY_FONT_SELECTED if dest_selected else JOURNEY_FONT
        dest_scale = JOURNEY_FONT_SELECTED_SCALE if dest_selected else JOURNEY_FONT_SCALE

        self.display.set_font(dest_font)
        # Right-justify destination with 1 pixel padding on right
        dest_width = self.display.measure_text(dest_text, scale=dest_scale)
        dest_x = screen.WIDTH - dest_width - 1
        self.display.text(
            dest_text,
            dest_x,
            1,
            scale=dest_scale
        )

    @Animator.KeyFrame.add(2)
    def journey_arrow(self, count):
        """Draw arrow between origin and destination (after text is drawn)"""
        # Guard against no data
        if len(self._data) == 0:
            return

        # Clear arrow area
        self.draw_square(
            ARROW_POINT_POSITION[0] - ARROW_WIDTH,
            ARROW_POINT_POSITION[1] - (ARROW_HEIGHT // 2),
            ARROW_POINT_POSITION[0],
            ARROW_POINT_POSITION[1] + (ARROW_HEIGHT // 2),
            colours.BLACK,
        )

        # Create arrow pen
        pen = self.display.create_pen(
            ARROW_COLOUR.red,
            ARROW_COLOUR.green,
            ARROW_COLOUR.blue
        )
        self.display.set_pen(pen)

        # Starting positions for filled arrow
        x = ARROW_POINT_POSITION[0] - ARROW_WIDTH
        y1 = ARROW_POINT_POSITION[1] - (ARROW_HEIGHT // 2)
        y2 = ARROW_POINT_POSITION[1] + (ARROW_HEIGHT // 2)

        # Draw tip of arrow
        self.display.pixel(ARROW_POINT_POSITION[0], ARROW_POINT_POSITION[1])

        # Draw arrow body using columns
        for col in range(0, ARROW_WIDTH):
            self.display.line(x, y1, x, y2)
            x += 1
            y1 += 1
            y2 -= 1
