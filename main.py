# FlightTracker for Interstate 75 W (RP2350)
# Main entry point
#
# A real-time flight tracking display for HUB75 LED matrices
# Ported from the Raspberry Pi version for Pimoroni Interstate 75 W
# Copyright (C) 2025 Colin Waddell <colinwaddell.com>
# https://github.com/ColinWaddell/FlightTracker/tree/master
#
# Setup:
# 1. Copy all files to your Interstate 75 W
# 2. Edit secrets.py with your WiFi credentials
# 3. Edit config.py with your location and preferences
# 4. Run this file or rename to main.py for auto-start

import time
import machine
import ntptime

from utilities.wifi import connect_wifi, is_connected
from display import Display


def sync_time():
    """Sync RTC with NTP server"""
    print("Syncing time with NTP...")
    try:
        ntptime.settime()
        print("Time synced successfully")
        return True
    except Exception as e:
        print(f"Failed to sync time: {e}")
        return False


def main():
    """Main entry point"""
    print("=" * 40)
    print("FlightTracker for Interstate 75 W")
    print("=" * 40)

    # Connect to WiFi
    print("\nConnecting to WiFi...")
    if not connect_wifi():
        print("ERROR: Could not connect to WiFi")
        print("Check your secrets.py configuration")
        # Flash red LED to indicate error
        from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32
        i75 = Interstate75(display=DISPLAY_INTERSTATE75_64X32)
        for _ in range(10):
            i75.set_led(255, 0, 0)
            time.sleep(0.5)
            i75.set_led(0, 0, 0)
            time.sleep(0.5)
        return

    # Sync time
    sync_time()

    # Small delay to let network stabilize
    time.sleep(1)

    # Create and run display
    print("\nStarting FlightTracker display...")
    display = Display()
    display.run()


# Auto-start on boot
main()
