# WiFi connection utilities for Interstate 75 W
import time
import network

from utilities.audio import get_player

# Try to import credentials (primary and fallback)
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
except ImportError:
    WIFI_SSID = ""
    WIFI_PASSWORD = ""

try:
    from secrets import WIFI_SSID_FALLBACK, WIFI_PASSWORD_FALLBACK
except ImportError:
    WIFI_SSID_FALLBACK = ""
    WIFI_PASSWORD_FALLBACK = ""


def _try_connect(wlan, ssid, password, max_wait):
    """Attempt to connect to a single network. Returns True on success."""
    print(f"Connecting to {ssid}...")
    wlan.connect(ssid, password)

    while max_wait > 0:
        status = wlan.status()
        if status < 0 or status >= 3:
            break
        max_wait -= 1
        print(f"Waiting for connection... ({max_wait}s)")
        time.sleep(1)

    return wlan.status() == 3


def connect_wifi(ssid=None, password=None, max_wait=10):
    """
    Connect to WiFi network with fallback support.

    Args:
        ssid: WiFi network name (uses secrets.py if not provided)
        password: WiFi password (uses secrets.py if not provided)
        max_wait: Maximum seconds to wait for connection

    Returns:
        bool: True if connected, False otherwise
    """
    if ssid is None:
        ssid = WIFI_SSID
    if password is None:
        password = WIFI_PASSWORD

    if not ssid:
        print("WiFi SSID not configured in secrets.py")
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    # Turn off power saving for better reliability
    wlan.config(pm=0xa11140)

    # Try primary network
    if _try_connect(wlan, ssid, password, max_wait):
        print(f"Connected! IP: {wlan.ifconfig()[0]}")
    elif WIFI_SSID_FALLBACK:
        # Try fallback network
        print(f"Primary network failed, trying fallback...")
        wlan.disconnect()
        time.sleep(1)
        if _try_connect(wlan, WIFI_SSID_FALLBACK, WIFI_PASSWORD_FALLBACK, max_wait):
            print(f"Connected to fallback! IP: {wlan.ifconfig()[0]}")
        else:
            print(f"Failed to connect to fallback (status: {wlan.status()})")
            return False
    else:
        print(f"Failed to connect to WiFi (status: {wlan.status()})")
        return False

    # Play bing-bong on successful connection
    try:
        player = get_player()
        player.play_bing_bong()
    except Exception as e:
        print(f"Audio notification failed: {e}")

    return True


def is_connected():
    """Check if WiFi is currently connected"""
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()


def get_ip():
    """Get current IP address"""
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    return None


def disconnect():
    """Disconnect from WiFi"""
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)
