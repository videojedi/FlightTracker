# Plane details scene - scrolling aircraft type display
# Ported from FlightTracker for Interstate 75 W

from utilities.animator import Animator
from setup import colours, fonts, screen

# Layout constants - matching original project
# Original: fonts.regular (6x12) at baseline y=30
PLANE_DETAILS_COLOUR = colours.PINK
PLANE_DISTANCE_FROM_TOP = 33  # Dropped 3 pixels
PLANE_TEXT_HEIGHT = 9
PLANE_FONT = fonts.REGULAR
PLANE_FONT_SCALE = fonts.REGULAR_SCALE

# Compass directions (8 directions, 45 deg each)
COMPASS_DIRECTIONS = ["North", "NE", "East", "SE", "South", "SW", "West", "NW"]

# Aircraft type code to friendly name lookup
# Common commercial aircraft types
AIRCRAFT_NAMES = {
    # Boeing
    "B731": "Boeing 737-100",
    "B732": "Boeing 737-200",
    "B733": "Boeing 737-300",
    "B734": "Boeing 737-400",
    "B735": "Boeing 737-500",
    "B736": "Boeing 737-600",
    "B737": "Boeing 737-700",
    "B738": "Boeing 737-800",
    "B739": "Boeing 737-900",
    "B37M": "Boeing 737 MAX 7",
    "B38M": "Boeing 737 MAX 8",
    "B39M": "Boeing 737 MAX 9",
    "B3XM": "Boeing 737 MAX 10",
    "B741": "Boeing 747-100",
    "B742": "Boeing 747-200",
    "B743": "Boeing 747-300",
    "B744": "Boeing 747-400",
    "B748": "Boeing 747-8",
    "B752": "Boeing 757-200",
    "B753": "Boeing 757-300",
    "B762": "Boeing 767-200",
    "B763": "Boeing 767-300",
    "B764": "Boeing 767-400",
    "B772": "Boeing 777-200",
    "B773": "Boeing 777-300",
    "B77L": "Boeing 777-200LR",
    "B77W": "Boeing 777-300ER",
    "B778": "Boeing 777-8",
    "B779": "Boeing 777-9",
    "B788": "Boeing 787-8 Dreamliner",
    "B789": "Boeing 787-9 Dreamliner",
    "B78X": "Boeing 787-10 Dreamliner",
    # Airbus
    "A124": "Antonov An-124",
    "A139": "AgustaWestland AW139",
    "A140": "Antonov An-140",
    "A148": "Antonov An-148",
    "A158": "Antonov An-158",
    "A19N": "Airbus A319neo",
    "A20N": "Airbus A320neo",
    "A21N": "Airbus A321neo",
    "A221": "Airbus A220-100",
    "A223": "Airbus A220-300",
    "A306": "Airbus A300-600",
    "A310": "Airbus A310",
    "A318": "Airbus A318",
    "A319": "Airbus A319",
    "A320": "Airbus A320",
    "A321": "Airbus A321",
    "A332": "Airbus A330-200",
    "A333": "Airbus A330-300",
    "A338": "Airbus A330-800neo",
    "A339": "Airbus A330-900neo",
    "A342": "Airbus A340-200",
    "A343": "Airbus A340-300",
    "A345": "Airbus A340-500",
    "A346": "Airbus A340-600",
    "A359": "Airbus A350-900",
    "A35K": "Airbus A350-1000",
    "A380": "Airbus A380",
    "A388": "Airbus A380-800",
    # Embraer
    "E135": "Embraer ERJ-135",
    "E145": "Embraer ERJ-145",
    "E170": "Embraer E170",
    "E175": "Embraer E175",
    "E190": "Embraer E190",
    "E195": "Embraer E195",
    "E290": "Embraer E190-E2",
    "E295": "Embraer E195-E2",
    # Bombardier/De Havilland
    "CRJ1": "Bombardier CRJ-100",
    "CRJ2": "Bombardier CRJ-200",
    "CRJ7": "Bombardier CRJ-700",
    "CRJ9": "Bombardier CRJ-900",
    "CRJX": "Bombardier CRJ-1000",
    "DH8A": "De Havilland Dash 8-100",
    "DH8B": "De Havilland Dash 8-200",
    "DH8C": "De Havilland Dash 8-300",
    "DH8D": "De Havilland Dash 8-400",
    # ATR
    "AT43": "ATR 42-300",
    "AT45": "ATR 42-500",
    "AT46": "ATR 42-600",
    "AT72": "ATR 72-200",
    "AT75": "ATR 72-500",
    "AT76": "ATR 72-600",
    # Other commercial
    "B461": "BAe 146-100",
    "B462": "BAe 146-200",
    "B463": "BAe 146-300",
    "RJ85": "Avro RJ85",
    "RJ1H": "Avro RJ100",
    "F100": "Fokker 100",
    "F70": "Fokker 70",
    "MD11": "McDonnell Douglas MD-11",
    "MD80": "McDonnell Douglas MD-80",
    "MD82": "McDonnell Douglas MD-82",
    "MD83": "McDonnell Douglas MD-83",
    "MD87": "McDonnell Douglas MD-87",
    "MD88": "McDonnell Douglas MD-88",
    "MD90": "McDonnell Douglas MD-90",
    "DC10": "McDonnell Douglas DC-10",
    # Business jets
    "C525": "Cessna CitationJet",
    "C550": "Cessna Citation II",
    "C560": "Cessna Citation V",
    "C56X": "Cessna Citation Excel",
    "C680": "Cessna Citation Sovereign",
    "C750": "Cessna Citation X",
    "CL30": "Bombardier Challenger 300",
    "CL35": "Bombardier Challenger 350",
    "CL60": "Bombardier Challenger 600",
    "GL5T": "Bombardier Global 5000",
    "GL7T": "Bombardier Global 7500",
    "GLEX": "Bombardier Global Express",
    "G150": "Gulfstream G150",
    "G280": "Gulfstream G280",
    "GLF4": "Gulfstream G-IV",
    "GLF5": "Gulfstream G-V",
    "GLF6": "Gulfstream G650",
    "LJ35": "Learjet 35",
    "LJ45": "Learjet 45",
    "LJ60": "Learjet 60",
    "FA7X": "Dassault Falcon 7X",
    "F900": "Dassault Falcon 900",
    "F2TH": "Dassault Falcon 2000",
    "PC12": "Pilatus PC-12",
    "PC24": "Pilatus PC-24",
    "PRM1": "Beechcraft Premier I",
    "BE40": "Beechcraft Beechjet 400",
    # Military/cargo
    "C17": "Boeing C-17 Globemaster",
    "C130": "Lockheed C-130 Hercules",
    "C5": "Lockheed C-5 Galaxy",
    "A400": "Airbus A400M Atlas",
    "KC10": "McDonnell Douglas KC-10",
    "KC35": "Boeing KC-135 Stratotanker",
    "E3CF": "Boeing E-3 Sentry AWACS",
    "P8": "Boeing P-8 Poseidon",
    # Helicopters
    "S92": "Sikorsky S-92",
    "S76": "Sikorsky S-76",
    "EC35": "Eurocopter EC135",
    "EC45": "Eurocopter EC145",
    "AS32": "Eurocopter AS332 Super Puma",
    "H160": "Airbus H160",
    "R44": "Robinson R44",
    "R66": "Robinson R66",
}

# Arrow dimensions for vertical speed indicator
ARROW_WIDTH = 5
ARROW_HEIGHT = 7
ARROW_UP_COLOUR = colours.GREEN
ARROW_DOWN_COLOUR = colours.ORANGE


class PlaneDetailsScene:
    def __init__(self):
        super().__init__()
        self.plane_position = screen.WIDTH
        self._data_all_looped = False

    def _draw_arrow(self, x, y, pointing_up):
        """Draw a triangular arrow at position (x, y)"""
        colour = ARROW_UP_COLOUR if pointing_up else ARROW_DOWN_COLOUR
        pen = self.display.create_pen(
            colour.red,
            colour.green,
            colour.blue
        )
        self.display.set_pen(pen)

        # Draw filled triangle arrow
        # Arrow is 5 wide, 7 tall
        if pointing_up:
            # Point at top, base at bottom
            #     *      (x+2, y)
            #    ***     (x+1 to x+3, y+1)
            #   *****    (x to x+4, y+2)
            #    ***     (x+1 to x+3, y+3) - shaft
            #    ***     (x+1 to x+3, y+4)
            #    ***     (x+1 to x+3, y+5)
            #    ***     (x+1 to x+3, y+6)
            self.display.pixel(x + 2, y)
            self.display.line(x + 1, y + 1, x + 3, y + 1)
            self.display.line(x, y + 2, x + 4, y + 2)
            for row in range(3, 7):
                self.display.line(x + 1, y + row, x + 3, y + row)
        else:
            # Point at bottom, base at top
            #    ***     (x+1 to x+3, y)
            #    ***     (x+1 to x+3, y+1)
            #    ***     (x+1 to x+3, y+2)
            #    ***     (x+1 to x+3, y+3) - shaft
            #   *****    (x to x+4, y+4)
            #    ***     (x+1 to x+3, y+5)
            #     *      (x+2, y+6)
            for row in range(0, 4):
                self.display.line(x + 1, y + row, x + 3, y + row)
            self.display.line(x, y + 4, x + 4, y + 4)
            self.display.line(x + 1, y + 5, x + 3, y + 5)
            self.display.pixel(x + 2, y + 6)

    def _build_plane_text(self, flight):
        """Build the scrolling text with plane, speed, heading, and altitude (no arrow)"""
        parts = []

        # Aircraft type - look up friendly name or use code
        plane_code = flight.get("plane", "")
        if plane_code:
            plane_name = AIRCRAFT_NAMES.get(plane_code.upper(), plane_code)
            parts.append(plane_name)

        # Speed (knots)
        speed = flight.get("velocity", 0)
        if speed:
            parts.append(f"{int(speed)}kts")

        # Heading (compass direction)
        heading = flight.get("heading", 0)
        if heading:
            # Convert degrees to compass direction (8 directions, 45 deg each)
            # Add 22.5 to center each direction, then divide by 45
            index = int((heading + 22.5) / 45) % 8
            parts.append(COMPASS_DIRECTIONS[index])

        return "  ".join(parts) if parts else ""

    def _build_altitude_text(self, flight):
        """Build altitude text (separate so we can position arrow before it)"""
        altitude = flight.get("altitude", 0)
        if altitude:
            return f"{int(altitude)}ft"
        return ""

    @Animator.KeyFrame.add(1)
    def plane_details(self, count):
        """Draw scrolling aircraft type with graphical arrows"""
        # Guard against no data
        if len(self._data) == 0:
            return

        flight = self._data[self._data_index]
        plane_text = self._build_plane_text(flight)
        altitude_text = self._build_altitude_text(flight)
        vertical_speed = flight.get("vertical_speed", 0)

        # Draw background (clear area)
        self.draw_square(
            0,
            PLANE_DISTANCE_FROM_TOP - PLANE_TEXT_HEIGHT,
            screen.WIDTH,
            screen.HEIGHT,
            colours.BLACK,
        )

        # Set font and colour
        self.display.set_font(PLANE_FONT)
        pen = self.display.create_pen(
            PLANE_DETAILS_COLOUR.red,
            PLANE_DETAILS_COLOUR.green,
            PLANE_DETAILS_COLOUR.blue
        )
        self.display.set_pen(pen)

        # Y position for text
        y_pos = PLANE_DISTANCE_FROM_TOP - PLANE_TEXT_HEIGHT + 1

        # Draw main text (plane, speed, heading)
        self.display.text(plane_text, self.plane_position, y_pos, scale=PLANE_FONT_SCALE)
        text_length = self.display.measure_text(plane_text, scale=PLANE_FONT_SCALE)

        # Calculate position for altitude section (after main text with spacing)
        alt_section_x = self.plane_position + text_length
        if plane_text:
            alt_section_x += self.display.measure_text("  ", scale=PLANE_FONT_SCALE)

        # Draw arrow if climbing or descending
        arrow_space = 0
        if vertical_speed != 0 and altitude_text:
            arrow_x = alt_section_x
            arrow_y = y_pos  # Align with text
            self._draw_arrow(arrow_x, arrow_y, vertical_speed > 0)
            arrow_space = ARROW_WIDTH + 2  # Arrow width plus gap

        # Draw altitude text after arrow
        if altitude_text:
            self.display.set_pen(pen)
            self.display.text(altitude_text, alt_section_x + arrow_space, y_pos, scale=PLANE_FONT_SCALE)
            alt_text_width = self.display.measure_text(altitude_text, scale=PLANE_FONT_SCALE)
        else:
            alt_text_width = 0

        # Calculate total width for scroll
        total_width = text_length
        if altitude_text:
            if plane_text:
                total_width += self.display.measure_text("  ", scale=PLANE_FONT_SCALE)
            total_width += arrow_space + alt_text_width

        # Handle scrolling
        self.plane_position -= 1

        if self.plane_position + total_width < 0:
            # Text has scrolled off screen
            self.plane_position = screen.WIDTH

            # Cycle to next flight if multiple
            if len(self._data) > 1:
                self._data_index = (self._data_index + 1) % len(self._data)
                self._data_all_looped = (not self._data_index) or self._data_all_looped
                self.reset_scene()

    @Animator.KeyFrame.add(0)
    def reset_scrolling(self):
        """Reset scroll position on scene reset"""
        self.plane_position = screen.WIDTH
