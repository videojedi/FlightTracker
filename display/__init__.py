# Display manager for Interstate 75 W FlightTracker
# Main orchestrator class that brings together all components

from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32, DISPLAY_INTERSTATE75_32X32
from interstate75 import DISPLAY_INTERSTATE75_64X64, DISPLAY_INTERSTATE75_128X64
from interstate75 import SWITCH_A, SWITCH_B
import time

from setup import frames, colours, screen
from utilities.animator import Animator
from utilities.overhead import Overhead
from utilities.audio import play_notification, get_player

from scenes.weather import WeatherScene
from scenes.flightdetails import FlightDetailsScene
from scenes.journey import JourneyScene
from scenes.loadingpulse import LoadingPulseScene
from scenes.clock import ClockScene
from scenes.planedetails import PlaneDetailsScene
from scenes.date import DateScene

# Configuration
try:
    from config import BRIGHTNESS
except ImportError:
    BRIGHTNESS = 50

# Map driver type string to Interstate75 constant
DRIVER_MAP = {
    "32x32": DISPLAY_INTERSTATE75_32X32,
    "64x32": DISPLAY_INTERSTATE75_64X32,
    "64x64": DISPLAY_INTERSTATE75_64X64,
    "128x64": DISPLAY_INTERSTATE75_128X64,
}


def flights_match(flights_a, flights_b):
    """Check if two flight lists have the same data (callsigns and routes)"""
    def get_flight_keys(flights):
        # Include origin/destination so we update when route info becomes available
        return set(
            (f.get("callsign", ""), f.get("origin", ""), f.get("destination", ""))
            for f in flights
        )
    return get_flight_keys(flights_a) == get_flight_keys(flights_b)


class Display(
    WeatherScene,
    FlightDetailsScene,
    JourneyScene,
    LoadingPulseScene,
    PlaneDetailsScene,
    ClockScene,
    DateScene,
    Animator,
):
    """
    Main display controller for FlightTracker on Interstate 75 W.

    Inherits from all scene classes and the animator to provide
    a unified interface for rendering flight data on the LED matrix.
    """

    def __init__(self, i75=None):
        # Setup Interstate 75 display
        # Use DRIVER_TYPE from screen.py (may differ from logical dimensions)
        display_const = DRIVER_MAP.get(screen.DRIVER_TYPE, DISPLAY_INTERSTATE75_64X32)

        if i75 is not None:
            # Use existing Interstate75 instance
            self.i75 = i75
        else:
            # Create new Interstate75 instance
            self.i75 = Interstate75(display=display_const)

        self.display = self.i75.display

        # Use logical dimensions from screen.py (not driver dimensions)
        # This allows "64x32h" mode: 64x64 driver but 32px logical height
        self.width = screen.WIDTH
        self.height = screen.HEIGHT

        # Set onboard LED to indicate startup (don't clear display yet)
        self.i75.set_led(0, 0, 50)  # Blue

        # Data to render
        self._data_index = 0
        self._data = []
        self._data_all_looped = False

        # Initialize scene attributes (MicroPython doesn't call parent __init__ reliably)
        # From WeatherScene
        self._weather_data = None
        self._weather_position = self.width
        self._last_weather_fetch = 0
        self._last_temperature_str = None

        # From ClockScene
        self._last_time = None

        # From DateScene
        self._last_date = None

        # From PlaneDetailsScene
        self.plane_position = self.width

        # Button debounce tracking
        self._last_button_a_time = 0
        self._last_button_b_time = 0

        # Start looking for planes
        self.overhead = Overhead()

        # Initialize animator explicitly (MicroPython super() can be unreliable with MI)
        Animator.__init__(self)

        # Set frame delay
        self.delay = frames.PERIOD

    def draw_square(self, x0, y0, x1, y1, colour):
        """Draw a filled rectangle"""
        pen = self.display.create_pen(colour.red, colour.green, colour.blue)
        self.display.set_pen(pen)
        self.display.rectangle(x0, y0, x1 - x0 + 1, y1 - y0 + 1)

    def _draw_idle_screen(self):
        """Draw initial idle screen with clock and date"""
        import machine
        from scenes.clock import CLOCK_FONT, CLOCK_FONT_SCALE, CLOCK_POSITION, CLOCK_COLOUR
        from scenes.date import DATE_FONT, DATE_FONT_SCALE, DATE_POSITION, DATE_COLOUR, DAYS_OF_WEEK

        # Clear screen
        self.display.set_pen(self.display.create_pen(0, 0, 0))
        self.display.clear()

        # Get current time
        rtc = machine.RTC()
        dt = rtc.datetime()
        time_str = f"{dt[4]:02d}:{dt[5]:02d}"
        day_name = DAYS_OF_WEEK[dt[3]]
        date_str = f"{day_name} {dt[2]}/{dt[1]}"

        # Draw clock
        self.display.set_font(CLOCK_FONT)
        pen = self.display.create_pen(CLOCK_COLOUR.red, CLOCK_COLOUR.green, CLOCK_COLOUR.blue)
        self.display.set_pen(pen)
        self.display.text(time_str, CLOCK_POSITION[0], CLOCK_POSITION[1], scale=CLOCK_FONT_SCALE)

        # Draw date
        self.display.set_font(DATE_FONT)
        pen = self.display.create_pen(DATE_COLOUR.red, DATE_COLOUR.green, DATE_COLOUR.blue)
        self.display.set_pen(pen)
        self.display.text(date_str, DATE_POSITION[0], DATE_POSITION[1], scale=DATE_FONT_SCALE)

        # Draw "Scanning..." message at weather scroll position
        from scenes.weather import SCROLL_Y_POS
        pen = self.display.create_pen(colours.YELLOW.red, colours.YELLOW.green, colours.YELLOW.blue)
        self.display.set_pen(pen)
        self.display.text("Scanning...", 1, SCROLL_Y_POS, scale=CLOCK_FONT_SCALE)

        # Update display
        self.i75.update()

        # Mark that we've drawn the idle screen (don't clear on first frame)
        self._idle_screen_drawn = True

    @Animator.KeyFrame.add(0)
    def clear_screen(self):
        """Clear screen on reset"""
        # Skip clear if we just drew the idle screen
        if hasattr(self, '_idle_screen_drawn') and self._idle_screen_drawn:
            self._idle_screen_drawn = False
            return
        self.display.set_pen(self.display.create_pen(0, 0, 0))
        self.display.clear()

    @Animator.KeyFrame.add(frames.PER_SECOND * 5)
    def check_for_loaded_data(self, count):
        """Check if new flight data is available"""
        if self.overhead.new_data:
            # Check if there's existing data
            there_is_data = len(self._data) > 0 or not self.overhead.data_is_empty

            # Get new data (marks as no longer new)
            new_data = self.overhead.data

            # Check if data has changed (callsigns OR origin/destination)
            data_is_different = not flights_match(self._data, new_data)

            if data_is_different:
                self._data_index = 0
                self._data_all_looped = False
                self._data = new_data

                # Update LED to show data status
                if len(new_data) > 0:
                    self.i75.set_led(0, 50, 0)  # Green - has flights
                    # Play notification sound for new flights
                    play_notification()
                else:
                    self.i75.set_led(0, 0, 50)  # Blue - no flights

            # Reset scene if data changed and there was/is data
            reset_required = there_is_data and data_is_different

            if reset_required:
                self.reset_scene()

    @Animator.KeyFrame.add(1)
    def sync(self, count):
        """Update display every frame"""
        self.i75.update()

    @Animator.KeyFrame.add(1)
    def check_buttons(self, count):
        """Check for button presses with debouncing"""
        now = time.ticks_ms()
        debounce_ms = 300  # 300ms debounce

        if self.i75.switch_pressed(SWITCH_A):
            if time.ticks_diff(now, self._last_button_a_time) > debounce_ms:
                self._last_button_a_time = now
                play_notification()

        if self.i75.switch_pressed(SWITCH_B):
            if time.ticks_diff(now, self._last_button_b_time) > debounce_ms:
                self._last_button_b_time = now
                # Toggle audio enabled/disabled
                player = get_player()
                enabled = player.toggle()
                # Flash LED to indicate state: green=enabled, red=disabled
                if enabled:
                    self.i75.set_led(0, 50, 0)  # Green
                else:
                    self.i75.set_led(50, 0, 0)  # Red

    @Animator.KeyFrame.add(frames.PER_SECOND * 30)
    def grab_new_data(self, count):
        """Fetch new flight data periodically"""
        # Only grab if not already processing and previous data has been shown
        if not self.overhead.processing and (
            self._data_all_looped or len(self._data) <= 1
        ):
            # Show loading indicator
            self.i75.set_led(50, 50, 0)  # Yellow - fetching
            self.overhead.grab_data()

    def run(self):
        """Start the main display loop"""
        try:
            print("FlightTracker starting...")
            print("Press CTRL-C to stop")

            # Draw initial idle screen immediately (before data fetch)
            self._draw_idle_screen()

            # Initial data fetch (this may take a few seconds)
            self.overhead.grab_data()

            # Start animation loop
            self.play()

        except KeyboardInterrupt:
            print("\nExiting...")
            self.i75.set_led(0, 0, 0)
            self.display.set_pen(self.display.create_pen(0, 0, 0))
            self.display.clear()
            self.i75.update()
