# Flight data fetching for Interstate 75 W
# Uses FlightRadar24 API with airplanes.live as fallback

import time
import math
import json

from utilities.https import https_get_json, https_get, http_get_json

# Configuration
try:
    from config import MIN_ALTITUDE, MAX_ALTITUDE, FLIGHT_POLL_INTERVAL
except ImportError:
    MIN_ALTITUDE = 0       # feet
    MAX_ALTITUDE = 45000   # feet
    FLIGHT_POLL_INTERVAL = 30  # seconds

try:
    from config import ZONE_HOME, LOCATION_HOME
    ZONE_DEFAULT = ZONE_HOME
    LOCATION_DEFAULT = LOCATION_HOME
except ImportError:
    # Default zone: UK
    ZONE_DEFAULT = {"tl_y": 52.0, "tl_x": -2.0, "br_y": 51.0, "br_x": 0.0}
    LOCATION_DEFAULT = [51.509865, -0.118092, 6371]  # London


# Constants
MAX_FLIGHT_LOOKUP = 5
EARTH_RADIUS_KM = 6371
BLANK_FIELDS = ["", "N/A", "NONE", None]

# FlightRadar24 API
FR24_HOST = "data-cloud.flightradar24.com"
FR24_PATH = "/zones/fcgi/feed.js"

# Airplanes.live API (free, 1 req/sec rate limit, ADS-B Exchange v2 compatible)
AIRPLANES_HOST = "api.airplanes.live"
AIRPLANES_PATH = "/v2/point"  # /lat/lon/radius format



def meters_to_feet(meters):
    """Convert meters to feet"""
    if meters is None:
        return 0
    return int(meters * 3.28084)


def distance_from_flight_to_home(flight_data, home=None):
    """Calculate distance from flight to home location in km"""
    if home is None:
        home = LOCATION_DEFAULT

    def polar_to_cartesian(lat, lon, alt):
        DEG2RAD = math.pi / 180
        return [
            alt * math.cos(DEG2RAD * lat) * math.sin(DEG2RAD * lon),
            alt * math.sin(DEG2RAD * lat),
            alt * math.cos(DEG2RAD * lat) * math.cos(DEG2RAD * lon),
        ]

    def feet_to_km_plus_earth(altitude_ft):
        altitude_km = 0.0003048 * altitude_ft
        return altitude_km + EARTH_RADIUS_KM

    try:
        lat = flight_data.get("lat", 0)
        lon = flight_data.get("lon", 0)
        alt = flight_data.get("altitude", 0)

        x0, y0, z0 = polar_to_cartesian(lat, lon, feet_to_km_plus_earth(alt))
        x1, y1, z1 = polar_to_cartesian(*home)

        dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2)
        return dist
    except Exception:
        return 1e6  # Return far away on error


def fetch_flights_fr24(zone):
    """
    Fetch flights within a geographic zone from FlightRadar24.

    Args:
        zone: Dict with tl_y, tl_x, br_y, br_x (top-left, bottom-right lat/lon)

    Returns:
        Tuple of (flights list, success bool)
        - flights: List of flight dictionaries
        - success: True if API call succeeded (even if 0 flights), False on error
    """
    # FR24 bounds format: y1,y2,x1,x2 (tl_y, br_y, tl_x, br_x)
    bounds = f"{zone['tl_y']},{zone['br_y']},{zone['tl_x']},{zone['br_x']}"

    path = (
        f"{FR24_PATH}"
        f"?bounds={bounds}"
        f"&faa=1&satellite=1&mlat=1&flarm=1&adsb=1"
        f"&gnd=0&air=1&vehicles=0&estimated=1&gliders=1"
        f"&stats=0"
    )

    flights = []

    try:
        data = https_get_json(FR24_HOST, path, timeout=15)
        if data is None:
            print("FR24 error: no response")
            return ([], False)

        # FR24 returns dict with flight IDs as keys
        # Each flight is an array: [icao24, lat, lon, track, altitude, speed,
        #   squawk, radar, type, registration, timestamp, origin, destination,
        #   flight_number, on_ground, vertical_speed, callsign, ...]
        for key, val in data.items():
            # Skip non-flight keys (like 'full_count', 'version', etc)
            if not isinstance(val, list) or len(val) < 17:
                continue

            try:
                lat = val[1]
                lon = val[2]
                altitude_ft = val[4] or 0
                vertical_speed = val[15] or 0
                callsign = (val[16] or "").strip()
                flight_number = (val[13] or "").strip()
                origin = (val[11] or "").strip()
                destination = (val[12] or "").strip()
                aircraft_type = (val[8] or "").strip()
                registration = (val[9] or "").strip()

                # Skip if on ground or no position
                if val[14] or lat is None or lon is None:
                    continue

                flight = {
                    "id": key,
                    "icao": val[0] or "",
                    "lat": float(lat),
                    "lon": float(lon),
                    "altitude": int(altitude_ft),
                    "callsign": callsign,
                    "flight_number": flight_number,
                    "origin": origin,
                    "destination": destination,
                    "aircraft_type": aircraft_type,
                    "registration": registration,
                    "vertical_speed": int(vertical_speed),
                    "velocity": val[5] or 0,
                    "heading": val[3] or 0,
                    "squawk": val[6] or "",
                }
                flights.append(flight)
            except (ValueError, TypeError, IndexError):
                continue

        print(f"FR24 returned {len(flights)} aircraft")
        return (flights, True)

    except Exception as e:
        print(f"FR24 error: {e}")
        return ([], False)


def fetch_flights_airplanes_live(zone):
    """
    Fetch flights from airplanes.live API (ADS-B Exchange v2 compatible).
    Free tier, rate limited to 1 request/second.
    Uses HTTP (not HTTPS) which works with MicroPython.

    Args:
        zone: Dict with tl_y, tl_x, br_y, br_x (top-left, bottom-right lat/lon)

    Returns:
        List of flight dictionaries
    """
    # Calculate center point and radius from zone
    center_lat = (zone['tl_y'] + zone['br_y']) / 2
    center_lon = (zone['tl_x'] + zone['br_x']) / 2

    # Approximate radius in nautical miles (max 250nm)
    lat_diff = abs(zone['tl_y'] - zone['br_y'])
    lon_diff = abs(zone['br_x'] - zone['tl_x'])
    # Rough conversion: 1 degree lat = 60nm, 1 degree lon = 60nm * cos(lat)
    radius_nm = max(lat_diff * 60, lon_diff * 60 * math.cos(math.radians(center_lat))) / 2
    radius_nm = min(radius_nm, 250)  # Cap at 250nm

    path = f"{AIRPLANES_PATH}/{center_lat}/{center_lon}/{int(radius_nm)}"

    flights = []

    try:
        # Use HTTPS - airplanes.live now requires it
        data = https_get_json(AIRPLANES_HOST, path, timeout=15)
        if data and "ac" in data:
            # ADS-B Exchange v2 format
            for ac in data["ac"]:
                try:
                    lat = ac.get("lat")
                    lon = ac.get("lon")

                    # Skip if no position or on ground
                    if lat is None or lon is None:
                        continue
                    if ac.get("ground", False) or ac.get("gnd", False):
                        continue

                    # Get altitude (baro or geometric)
                    alt_baro = ac.get("alt_baro", 0)
                    if alt_baro == "ground":
                        continue
                    altitude = int(alt_baro) if alt_baro else ac.get("alt_geom", 0) or 0

                    callsign = (ac.get("flight") or ac.get("r") or "").strip()
                    vertical_rate = ac.get("baro_rate") or ac.get("geom_rate") or 0

                    flight = {
                        "id": ac.get("hex", ""),
                        "icao": ac.get("hex", ""),
                        "lat": float(lat),
                        "lon": float(lon),
                        "altitude": altitude,
                        "callsign": callsign,
                        "vertical_speed": int(vertical_rate),
                        "velocity": ac.get("gs", 0) or 0,  # ground speed
                        "heading": ac.get("track", 0) or 0,
                        "squawk": ac.get("squawk", ""),
                        "aircraft_type": ac.get("t", ""),  # aircraft type code
                        "registration": ac.get("r", ""),
                        # ADS-B doesn't provide origin/destination
                        "origin": "",
                        "destination": "",
                    }
                    flights.append(flight)
                except (ValueError, TypeError, KeyError):
                    continue

            print(f"airplanes.live returned {len(flights)} aircraft")

    except Exception as e:
        print(f"airplanes.live error: {e}")

    return flights


def fetch_flights_in_zone(zone):
    """
    Fetch flights with fallbacks:
    1. FlightRadar24 (primary - includes origin/destination)
    2. airplanes.live (fallback - ADS-B data only, only used if FR24 errors)
    """
    # Try FR24 first (has origin/destination airports)
    flights, success = fetch_flights_fr24(zone)

    # Only fall back to airplanes.live if FR24 had an error
    # (not just 0 flights - that's a valid response)
    if not success:
        print("FR24 failed, trying airplanes.live fallback...")
        flights = fetch_flights_airplanes_live(zone)

    return flights


class Overhead:
    """
    Manages flight data retrieval and caching.

    Unlike the Raspberry Pi version, this runs synchronously
    since MicroPython has limited threading support.
    """

    def __init__(self):
        self._data = []
        self._new_data = False
        self._processing = False
        self._last_fetch = 0
        self._fetch_interval = FLIGHT_POLL_INTERVAL

    def grab_data(self):
        """Fetch flight data (synchronous version)"""
        self._processing = True
        self._new_data = False

        data = []

        try:
            # Fetch all flights in zone
            flights = fetch_flights_in_zone(ZONE_DEFAULT)
            print(f"Found {len(flights)} flights in zone")

            # If no flights from API, leave data empty (display will show clock/weather)
            if len(flights) == 0:
                print("No flights in zone - display will show clock/weather")
                self._data = []
                self._new_data = True
                self._last_fetch = time.time()
                self._processing = False
                return

            # Filter by altitude
            min_alt = MIN_ALTITUDE
            max_alt = MAX_ALTITUDE
            flights = [
                f for f in flights
                if min_alt < f.get("altitude", 0) < max_alt
            ]
            print(f"After altitude filter: {len(flights)} flights")

            # Sort by distance from home
            flights = sorted(
                flights,
                key=lambda f: distance_from_flight_to_home(f)
            )

            # Take closest flights
            for flight in flights[:MAX_FLIGHT_LOOKUP]:
                callsign = flight.get("callsign", "")
                if callsign and callsign.upper() in BLANK_FIELDS:
                    callsign = ""

                flight_number = flight.get("flight_number", "")
                if flight_number and flight_number.upper() in BLANK_FIELDS:
                    flight_number = ""

                # Use aircraft_type from FR24, fall back to ICAO code
                plane = flight.get("aircraft_type", "") or flight.get("icao", "").upper()
                origin = flight.get("origin", "")
                destination = flight.get("destination", "")

                print(f"Flight: {flight_number or callsign} {plane} {origin}->{destination} @{flight.get('altitude', 0)}ft")

                data.append({
                    "plane": plane,
                    "origin": origin,
                    "destination": destination,
                    "vertical_speed": flight.get("vertical_speed", 0),
                    "altitude": flight.get("altitude", 0),
                    "velocity": flight.get("velocity", 0),
                    "heading": flight.get("heading", 0),
                    "callsign": callsign,
                    "flight_number": flight_number,
                })

            self._data = data
            self._new_data = True
            self._last_fetch = time.time()

        except Exception as e:
            print(f"Error grabbing flight data: {e}")
            self._new_data = False

        self._processing = False

    @property
    def new_data(self):
        return self._new_data

    @property
    def processing(self):
        return self._processing

    @property
    def data(self):
        self._new_data = False
        return self._data

    @property
    def data_is_empty(self):
        return len(self._data) == 0

    def should_refresh(self):
        """Check if enough time has passed for a refresh"""
        return (time.time() - self._last_fetch) >= self._fetch_interval
