# FlightTracker for Interstate 75 W (RP2350)

A real-time flight tracking display for HUB75 LED matrices, running on the Pimoroni Interstate 75 W with RP2350.

This is a port of the original Raspberry Pi FlightTracker project, adapted for MicroPython on the Interstate 75 W board.

## Hardware Requirements

- [Pimoroni Interstate 75 W (RP2350)](https://shop.pimoroni.com/products/interstate-75-w)
- HUB75 LED Matrix Panel (64x32 recommended, other sizes supported)
- USB-C cable for power and programming

## Features

- Real-time flight tracking using FlightRadar24 data
- Displays flight callsign, origin/destination airports, and aircraft type
- Scrolling text for aircraft information
- Clock and date display when no flights overhead
- Temperature display with colour-coded values
- Loading indicator during data fetch
- Onboard RGB LED status indicator

## Installation

### 1. Install Pimoroni MicroPython Firmware

Download the latest Pimoroni MicroPython firmware for Interstate 75 W from:
https://github.com/pimoroni/interstate75/releases

Flash the firmware:
1. Hold the BOOT button on the Interstate 75 W
2. Connect USB-C cable to your computer
3. Release BOOT button - the board appears as a USB drive
4. Copy the `.uf2` firmware file to the drive
5. The board will reboot automatically

### 2. Copy Files to the Board

Copy all files from this `interstate75` directory to your Interstate 75 W.

You can use Thonny, rshell, or mpremote:

```bash
# Using mpremote
mpremote cp -r . :

# Or using rshell
rshell -p /dev/ttyACM0 rsync . /pyboard/
```

### 3. Configure WiFi

Edit `secrets.py` with your WiFi credentials:

```python
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"
```

### 4. Configure Location

Edit `config.py` with your location settings:

```python
# Geographic zone for tracking (lat/lon bounds)
ZONE_HOME = {
    "tl_y": 52.0,   # North boundary
    "tl_x": -2.5,   # West boundary
    "br_y": 51.0,   # South boundary
    "br_x": -0.5    # East boundary
}

# Your home location [lat, lon, altitude_km]
LOCATION_HOME = [51.509865, -0.118092, 6371]

# Weather location
WEATHER_LOCATION = "London"

# Your local airport code to highlight
JOURNEY_CODE_SELECTED = "LHR"
```

### 5. Run

The tracker starts automatically when the board powers on (if main.py is present).

Or run manually via Thonny/REPL:
```python
import main
main.main()
```

## Display Layout (64x32)

```
+--------------------------------+
| LHR  ->  JFK          |  15C  |  <- Journey + Temperature
+--------------------------------+
| BA178 -------- 1/3    | [*]   |  <- Callsign + Counter + Loading
+--------------------------------+
| Boeing 777-300ER              |  <- Scrolling aircraft type
+--------------------------------+
```

When no flights are overhead:
```
+--------------------------------+
| 14:35                 |  15C  |  <- Clock + Temperature
+--------------------------------+
|                               |
+--------------------------------+
| Mon 1/12                      |  <- Date
+--------------------------------+
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `ZONE_HOME` | Geographic bounds for tracking | UK |
| `LOCATION_HOME` | Your location for distance calc | London |
| `WEATHER_LOCATION` | City for weather API | London |
| `OPENWEATHER_API_KEY` | Optional OpenWeather key | None |
| `TEMPERATURE_UNITS` | "metric" or "imperial" | metric |
| `MIN_ALTITUDE` | Ignore flights below (feet) | 0 |
| `BRIGHTNESS` | Display brightness (0-100) | 50 |
| `JOURNEY_CODE_SELECTED` | Airport code to highlight | LHR |
| `DISPLAY_TYPE` | Panel size: 32x32, 64x32, etc. | 64x32 |

## Supported Display Sizes

- 32x32
- 64x32 (recommended)
- 64x64
- 128x64

## LED Status Indicator

The onboard RGB LED indicates system status:

| Colour | Meaning |
|--------|---------|
| Blue | No flights / Idle |
| Green | Flights detected |
| Yellow | Fetching data |
| Red (flashing) | WiFi connection error |

## Differences from Raspberry Pi Version

This port has some differences due to MicroPython limitations:

1. **Synchronous data fetching** - No background threads; data is fetched between display updates
2. **Simplified fonts** - Uses PicoGraphics built-in bitmap fonts instead of BDF fonts
3. **Direct HTTP requests** - Uses urequests instead of FlightRadar24API library
4. **No GPIO LED scene** - Uses onboard RGB LED instead

## Troubleshooting

### WiFi Connection Issues
- Check SSID and password in `secrets.py`
- Ensure 2.4GHz network (5GHz not supported)
- Try power cycling the board

### No Flights Showing
- Verify your `ZONE_HOME` coordinates are correct
- Check you have flights in your area (use FlightRadar24 website)
- Ensure `MIN_ALTITUDE` isn't filtering out all flights

### Display Issues
- Check panel is connected correctly to HUB75 header
- Verify `DISPLAY_TYPE` matches your panel
- Try reducing `BRIGHTNESS` if display looks washed out

## License

GPL v3.0 - See LICENSE file

## Credits

Original FlightTracker project for Raspberry Pi.
Ported for Pimoroni Interstate 75 W (RP2350).
