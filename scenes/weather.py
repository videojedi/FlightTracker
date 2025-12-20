# Weather scene - displays temperature and scrolling weather conditions
# Ported from FlightTracker for Interstate 75 W

import time

from utilities.animator import Animator
from utilities.https import https_get_json
from setup import colours, fonts, screen

# Configuration
try:
    from config import LOCATION
    WEATHER_LAT = LOCATION["latitude"]
    WEATHER_LON = LOCATION["longitude"]
except ImportError:
    WEATHER_LAT = 51.509865
    WEATHER_LON = -0.118092

try:
    from config import TEMPERATURE_UNITS
except ImportError:
    TEMPERATURE_UNITS = "metric"

# Validate temperature units
if TEMPERATURE_UNITS not in ("metric", "imperial"):
    TEMPERATURE_UNITS = "metric"

# Open-Meteo API (free, no API key required)
OPENMETEO_HOST = "api.open-meteo.com"
OPENMETEO_PATH = "/v1/forecast"
WEATHER_RETRIES = 3
WEATHER_REFRESH_SECONDS = 300  # 5 minutes

# Layout constants - static temperature top right
TEMPERATURE_FONT = fonts.XLARGE
TEMPERATURE_FONT_SCALE = fonts.XLARGE_SCALE
TEMPERATURE_POSITION = (38, 1)

# Layout constants - scrolling weather middle row
SCROLL_FONT = fonts.XLARGE
SCROLL_FONT_SCALE = fonts.XLARGE_SCALE
SCROLL_Y_POS = 24  # Moved down 6 pixels from 18
SCROLL_HEIGHT = 14  # Height of XLARGE font

# Compass directions for wind
WIND_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# WMO Weather codes to condition text
WMO_CONDITIONS = {
    0: "Clear",
    1: "Mostly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Heavy Drizzle",
    56: "Freezing Drizzle",
    57: "Heavy Freezing Drizzle",
    61: "Light Rain",
    63: "Rain",
    65: "Heavy Rain",
    66: "Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Light Snow",
    73: "Snow",
    75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Showers",
    81: "Showers",
    82: "Heavy Showers",
    85: "Light Snow Showers",
    86: "Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm w/ Hail",
    99: "Heavy Thunderstorm",
}

# Wind speed colour thresholds (km/h or mph depending on units)
WIND_COLOURS = (
    (0, colours.GREEN),       # Calm
    (10, colours.YELLOW),     # Light breeze
    (25, colours.ORANGE),     # Moderate wind
    (50, colours.RED),        # Strong wind
)

# Temperature colour gradient thresholds
TEMPERATURE_COLOURS = (
    (0, colours.WHITE),
    (1, colours.BLUE_LIGHT),
    (8, colours.PINK_DARK),
    (18, colours.YELLOW),
    (30, colours.ORANGE),
)

# Cache for weather data
_weather_cache = {
    "data": None,
    "timestamp": 0,
    "ttl": 300  # 5 minutes
}


def grab_weather_data(lat, lon, units="metric"):
    """
    Get comprehensive weather data from Open-Meteo API.

    Returns dict with: temperature, temp_high, temp_low, condition, rain_probability,
                       wind_speed, wind_direction, humidity
    """
    now = time.time()

    # Return cached data if still valid
    if (_weather_cache["data"] is not None and
            now - _weather_cache["timestamp"] < _weather_cache["ttl"]):
        return _weather_cache["data"]

    # Open-Meteo uses temperature_unit parameter
    temp_unit = "celsius" if units == "metric" else "fahrenheit"
    wind_unit = "kmh" if units == "metric" else "mph"

    # Request current weather, daily high/low, and hourly precipitation probability
    path = (
        f"{OPENMETEO_PATH}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&current=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m,relative_humidity_2m"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&hourly=precipitation_probability"
        f"&forecast_days=1"
        f"&forecast_hours=1"
        f"&temperature_unit={temp_unit}"
        f"&wind_speed_unit={wind_unit}"
    )

    retries = WEATHER_RETRIES

    while retries > 0:
        try:
            data = https_get_json(OPENMETEO_HOST, path)
            if data and "current" in data:
                current = data["current"]

                # Get precipitation probability from hourly (first hour)
                rain_prob = 0
                if "hourly" in data and "precipitation_probability" in data["hourly"]:
                    probs = data["hourly"]["precipitation_probability"]
                    if probs and len(probs) > 0:
                        rain_prob = probs[0] or 0

                # Get daily high/low
                temp_high = None
                temp_low = None
                if "daily" in data:
                    daily = data["daily"]
                    if "temperature_2m_max" in daily and daily["temperature_2m_max"]:
                        temp_high = daily["temperature_2m_max"][0]
                    if "temperature_2m_min" in daily and daily["temperature_2m_min"]:
                        temp_low = daily["temperature_2m_min"][0]

                weather = {
                    "temperature": current.get("temperature_2m"),
                    "temp_high": temp_high,
                    "temp_low": temp_low,
                    "weather_code": current.get("weather_code", 0),
                    "wind_speed": current.get("wind_speed_10m", 0),
                    "wind_direction": current.get("wind_direction_10m", 0),
                    "humidity": current.get("relative_humidity_2m", 0),
                    "rain_probability": rain_prob,
                }

                _weather_cache["data"] = weather
                _weather_cache["timestamp"] = now

                condition = WMO_CONDITIONS.get(weather["weather_code"], "Unknown")
                unit_str = "km/h" if units == "metric" else "mph"
                print("Weather: " + str(weather["temperature"]) + "deg (H:" + str(temp_high) + " L:" + str(temp_low) + "), " + condition + ", Wind " + str(weather["wind_speed"]) + unit_str + ", Rain " + str(rain_prob) + "%, Humidity " + str(weather["humidity"]) + "%")

                return weather
        except Exception as e:
            print(f"Open-Meteo error: {e}")
        retries -= 1
        time.sleep(0.5)

    return None


class WeatherScene:
    def __init__(self):
        super().__init__()
        self._weather_data = None
        self._weather_position = screen.WIDTH
        self._last_weather_fetch = 0
        self._last_temperature_str = None

    def colour_gradient(self, colour_A, colour_B, ratio):
        """Interpolate between two colours"""
        r = colour_A.red + int((colour_B.red - colour_A.red) * ratio)
        g = colour_A.green + int((colour_B.green - colour_A.green) * ratio)
        b = colour_A.blue + int((colour_B.blue - colour_A.blue) * ratio)
        return colours.Color(r, g, b)

    def temperature_to_colour(self, temp):
        """Map temperature to colour"""
        min_temp = TEMPERATURE_COLOURS[0][0]
        max_temp = TEMPERATURE_COLOURS[1][0]
        min_colour = TEMPERATURE_COLOURS[0][1]
        max_colour = TEMPERATURE_COLOURS[1][1]

        for i in range(1, len(TEMPERATURE_COLOURS) - 1):
            if temp > TEMPERATURE_COLOURS[i][0]:
                min_temp = TEMPERATURE_COLOURS[i][0]
                max_temp = TEMPERATURE_COLOURS[i + 1][0]
                min_colour = TEMPERATURE_COLOURS[i][1]
                max_colour = TEMPERATURE_COLOURS[i + 1][1]

        if temp > max_temp:
            ratio = 1
        elif temp > min_temp:
            ratio = (temp - min_temp) / (max_temp - min_temp)
        else:
            ratio = 0

        return self.colour_gradient(min_colour, max_colour, ratio)

    def wind_to_colour(self, speed):
        """Map wind speed to colour"""
        for i in range(len(WIND_COLOURS) - 1, -1, -1):
            if speed >= WIND_COLOURS[i][0]:
                return WIND_COLOURS[i][1]
        return WIND_COLOURS[0][1]

    def _draw_weather_segment(self, text, x, y, colour, font, scale):
        """Draw a text segment and return its width"""
        pen = self.display.create_pen(
            int(colour.red),
            int(colour.green),
            int(colour.blue)
        )
        self.display.set_pen(pen)
        self.display.set_font(font)
        self.display.text(text, x, y, scale=scale)
        return self.display.measure_text(text, scale=scale)

    @Animator.KeyFrame.add(1)
    def temperature_static(self, count):
        """Draw static current temperature in top right"""
        # Only show when no flight data
        if len(self._data):
            self._last_temperature_str = None
            return

        # Refresh weather data periodically
        now = time.time()
        if self._weather_data is None or (now - self._last_weather_fetch) > WEATHER_REFRESH_SECONDS:
            self._weather_data = grab_weather_data(WEATHER_LAT, WEATHER_LON, TEMPERATURE_UNITS)
            self._last_weather_fetch = now

        if self._weather_data is None:
            return

        temp = self._weather_data.get("temperature")
        if temp is None:
            return

        temp_str = f"{round(temp)}C"

        # Only redraw if changed
        if temp_str == self._last_temperature_str:
            return

        # Clear old temperature
        if self._last_temperature_str is not None:
            self.display.set_font(TEMPERATURE_FONT)
            black_pen = self.display.create_pen(0, 0, 0)
            self.display.set_pen(black_pen)
            self.display.text(
                self._last_temperature_str,
                TEMPERATURE_POSITION[0],
                TEMPERATURE_POSITION[1],
                scale=TEMPERATURE_FONT_SCALE
            )

        # Draw new temperature
        temp_colour = self.temperature_to_colour(temp)
        pen = self.display.create_pen(
            int(temp_colour.red),
            int(temp_colour.green),
            int(temp_colour.blue)
        )
        self.display.set_pen(pen)
        self.display.set_font(TEMPERATURE_FONT)
        self.display.text(
            temp_str,
            TEMPERATURE_POSITION[0],
            TEMPERATURE_POSITION[1],
            scale=TEMPERATURE_FONT_SCALE
        )

        self._last_temperature_str = temp_str

    @Animator.KeyFrame.add(1)
    def weather_scroll(self, count):
        """Draw scrolling weather information in middle row"""
        # Only show when no flight data
        if len(self._data):
            self._weather_position = screen.WIDTH
            return

        if self._weather_data is None:
            return

        # Clear the scrolling area (middle row only)
        self.draw_square(
            0,
            SCROLL_Y_POS,
            screen.WIDTH - 1,
            SCROLL_Y_POS + SCROLL_HEIGHT - 1,
            colours.BLACK,
        )

        self.display.set_font(SCROLL_FONT)
        x_pos = self._weather_position
        y_pos = SCROLL_Y_POS

        # Build and draw weather segments with different colours
        total_width = 0
        spacing = self.display.measure_text("  ", scale=SCROLL_FONT_SCALE)

        # Condition (white)
        weather_code = self._weather_data.get("weather_code", 0)
        condition = WMO_CONDITIONS.get(weather_code, "")
        if condition:
            width = self._draw_weather_segment(condition, x_pos, y_pos, colours.WHITE, SCROLL_FONT, SCROLL_FONT_SCALE)
            x_pos += width + spacing
            total_width += width + spacing

        # High/Low temperatures
        temp_high = self._weather_data.get("temp_high")
        temp_low = self._weather_data.get("temp_low")
        if temp_high is not None and temp_low is not None:
            # High in orange/red
            high_text = f"H:{round(temp_high)}"
            high_colour = self.temperature_to_colour(temp_high)
            width = self._draw_weather_segment(high_text, x_pos, y_pos, high_colour, SCROLL_FONT, SCROLL_FONT_SCALE)
            x_pos += width + spacing
            total_width += width + spacing

            # Low in blue
            low_text = f"L:{round(temp_low)}"
            low_colour = self.temperature_to_colour(temp_low)
            width = self._draw_weather_segment(low_text, x_pos, y_pos, low_colour, SCROLL_FONT, SCROLL_FONT_SCALE)
            x_pos += width + spacing
            total_width += width + spacing

        # Rain probability (blue)
        rain_prob = self._weather_data.get("rain_probability", 0)
        rain_text = f"{rain_prob}%Rain"
        width = self._draw_weather_segment(rain_text, x_pos, y_pos, colours.BLUE_LIGHT, SCROLL_FONT, SCROLL_FONT_SCALE)
        x_pos += width + spacing
        total_width += width + spacing

        # Wind speed and direction (colour based on speed)
        wind_speed = self._weather_data.get("wind_speed", 0)
        wind_dir = self._weather_data.get("wind_direction", 0)
        # Convert degrees to compass direction
        dir_index = int((wind_dir + 22.5) / 45) % 8
        wind_compass = WIND_DIRECTIONS[dir_index]
        wind_unit = "km/h" if TEMPERATURE_UNITS == "metric" else "mph"
        wind_text = str(int(wind_speed)) + wind_unit + " " + wind_compass
        wind_colour = self.wind_to_colour(wind_speed)
        width = self._draw_weather_segment(wind_text, x_pos, y_pos, wind_colour, SCROLL_FONT, SCROLL_FONT_SCALE)
        x_pos += width + spacing
        total_width += width + spacing

        # Humidity (cyan)
        humidity = self._weather_data.get("humidity", 0)
        humidity_text = f"{humidity}%RH"
        width = self._draw_weather_segment(humidity_text, x_pos, y_pos, colours.CYAN, SCROLL_FONT, SCROLL_FONT_SCALE)
        total_width += width

        # Handle scrolling
        self._weather_position -= 1

        if self._weather_position + total_width < 0:
            self._weather_position = screen.WIDTH
