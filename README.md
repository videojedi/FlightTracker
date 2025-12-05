# FlightTracker for Interstate 75 W

A real-time flight tracking display for HUB75 LED matrices, running on the Pimoroni Interstate 75 W with RP2350/RP2040.

## Credits

This project is a MicroPython port of the original [FlightTracker](https://github.com/ColinWaddell/FlightTracker) by [Colin Waddell](https://github.com/ColinWaddell), designed for Raspberry Pi with RGB LED matrices.

Ported for Pimoroni Interstate 75 W by [Richard Burford](https://github.com/videojedi).

## Hardware Requirements

- [Pimoroni Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w) (RP2350 or RP2040 version)
- HUB75 LED Matrix Panel (64x32 recommended, other sizes supported)
- USB-C cable for power and programming
- Optional: Speaker/buzzer on GP2 for audio notifications

## Features

- Real-time flight tracking using FlightRadar24 API (with airplanes.live fallback)
- Displays flight number, origin/destination airports
- Aircraft type lookup with friendly names (e.g., "Boeing 787-8 Dreamliner")
- Scrolling weather information with colour-coded values
- Clock and date display when no flights overhead
- Bing-bong audio notification for new flights
- Button A triggers audio notification
- Fallback WiFi network support
- Onboard RGB LED status indicator

## Installation

### 1. Flash Pimoroni MicroPython Firmware

Download the latest Pimoroni MicroPython firmware for Interstate 75 W from:
https://github.com/pimoroni/pimoroni-pico/releases

Flash the firmware:
1. Hold the BOOT button and press RST on the Interstate 75 W
2. The board appears as a USB drive
3. Copy the `.uf2` firmware file to the drive
4. The board will reboot automatically

### 2. Copy Files to the Board

Copy all project files to your Interstate 75 W using Thonny, rshell, or mpremote:

```bash
# Using mpremote
mpremote cp -r . :

# Or using rshell
rshell -p /dev/ttyACM0 rsync . /pyboard/
```

### 3. Configure WiFi

Create `secrets.py` with your WiFi credentials:

```python
# Primary WiFi
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

# Fallback WiFi (optional)
WIFI_SSID_FALLBACK = "BackupNetwork"
WIFI_PASSWORD_FALLBACK = "BackupPassword"
```

### 4. Configure Location

Create or edit `config.py` with your location settings:

```python
# Geographic zone for tracking (lat/lon bounds)
ZONE_HOME = {
    "tl_y": 56.5,   # North boundary
    "tl_x": -5.0,   # West boundary
    "br_y": 55.5,   # South boundary
    "br_x": -3.5    # East boundary
}

# Your home location [lat, lon, altitude_km]
LOCATION_HOME = [55.8642, -4.2518, 6371]

# Weather location (lat, lon)
WEATHER_LAT = 55.8642
WEATHER_LON = -4.2518

# Your local airport code to highlight
JOURNEY_CODE_SELECTED = "GLA"

# Temperature units: "metric" or "imperial"
TEMPERATURE_UNITS = "metric"

# Display brightness (0-100)
BRIGHTNESS = 50

# Altitude filter (feet)
MIN_ALTITUDE = 0
MAX_ALTITUDE = 45000

# Audio pin (optional)
AUDIO_PIN = 2
```

### 5. Run

The tracker starts automatically when the board powers on.

Or run manually via Thonny/REPL:
```python
import main
main.main()
```

## Display Layout (64x32)

When flights are overhead:
```
┌────────────────────────────────┐
│ GLA  ────>  LHR         12°C   │  Route + Temperature
├────────────────────────────────┤
│ BA1234 ──────────────── 1/3    │  Flight number + Counter
├────────────────────────────────┤
│ Airbus A320  450kts  ↑32000ft  │  Scrolling aircraft info
└────────────────────────────────┘
```

When no flights are overhead:
```
┌────────────────────────────────┐
│ 14:35                   12°C   │  Clock + Temperature
├────────────────────────────────┤
│ Partly Cloudy  15km/h SW  65%  │  Scrolling weather
├────────────────────────────────┤
│ Thu 5 Dec                      │  Date
└────────────────────────────────┘
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `ZONE_HOME` | Geographic bounds for flight tracking | Glasgow area |
| `LOCATION_HOME` | Your location for distance calculation | Glasgow |
| `WEATHER_LAT/LON` | Coordinates for weather API | Glasgow |
| `TEMPERATURE_UNITS` | "metric" or "imperial" | metric |
| `MIN_ALTITUDE` | Ignore flights below this (feet) | 0 |
| `MAX_ALTITUDE` | Ignore flights above this (feet) | 45000 |
| `BRIGHTNESS` | Display brightness (0-100) | 50 |
| `JOURNEY_CODE_SELECTED` | Airport code to highlight | GLA |
| `AUDIO_PIN` | GPIO pin for speaker | 2 |

## Supported Display Sizes

Set `DRIVER_TYPE` in `setup/screen.py`:

- `32x32`
- `64x32` (recommended)
- `64x64`
- `128x64`

## LED Status Indicator

The onboard RGB LED indicates system status:

| Colour | Meaning |
|--------|---------|
| Blue | No flights / Idle |
| Green | Flights detected |
| Yellow | Fetching data |

## Button Controls

| Button | Action |
|--------|--------|
| A (GP14) | Play bing-bong notification |

## Data Sources

- **FlightRadar24** - Primary source for flight data (includes origin/destination)
- **airplanes.live** - Fallback ADS-B data (used only if FR24 fails)
- **Open-Meteo** - Weather data (free, no API key required)

## Differences from Original Raspberry Pi Version

This MicroPython port has some differences:

1. **Synchronous operation** - No background threads; data fetched between display updates
2. **Built-in fonts** - Uses PicoGraphics bitmap fonts instead of BDF files
3. **Direct HTTPS** - Custom TLS implementation for MicroPython
4. **Simplified audio** - PWM tone generation instead of WAV playback
5. **No external dependencies** - All code runs standalone on the microcontroller

## Troubleshooting

### WiFi Connection Issues
- Check SSID and password in `secrets.py`
- Ensure 2.4GHz network (5GHz not supported by Pico W)
- Try adding a fallback network

### No Flights Showing
- Verify your `ZONE_HOME` coordinates are correct
- Check flights in your area using [FlightRadar24](https://www.flightradar24.com)
- Ensure `MIN_ALTITUDE` isn't filtering out all flights

### Display Issues
- Check panel is connected correctly to HUB75 header
- Verify `DRIVER_TYPE` in `setup/screen.py` matches your panel
- Try reducing `BRIGHTNESS` if display looks washed out

### Audio Issues
- Check speaker is connected to correct GPIO pin (default GP2)
- Verify `AUDIO_PIN` in config.py matches your wiring

## License

GPL v3.0 - Same as original project.

## Links

- [Original FlightTracker by Colin Waddell](https://github.com/ColinWaddell/FlightTracker)
- [Pimoroni Interstate 75 W](https://shop.pimoroni.com/products/interstate-75-w)
- [Pimoroni MicroPython Releases](https://github.com/pimoroni/pimoroni-pico/releases)
