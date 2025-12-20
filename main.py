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

from interstate75 import Interstate75, DISPLAY_INTERSTATE75_64X32, DISPLAY_INTERSTATE75_64X64
from setup import colours, fonts, screen

from utilities.wifi import connect_wifi, is_connected
from display import Display

# Map driver type string to Interstate75 constant
DRIVER_MAP = {
    "32x32": DISPLAY_INTERSTATE75_64X32,
    "64x32": DISPLAY_INTERSTATE75_64X32,
    "64x64": DISPLAY_INTERSTATE75_64X64,
}


def show_startup_message(i75, display, message, colour=None):
    """Display a startup message on the LED matrix"""
    if colour is None:
        colour = colours.WHITE

    # Clear display
    display.set_pen(display.create_pen(0, 0, 0))
    display.clear()

    # Draw message
    pen = display.create_pen(colour.red, colour.green, colour.blue)
    display.set_pen(pen)
    display.set_font(fonts.REGULAR)
    display.text(message, 2, 12, scale=fonts.REGULAR_SCALE)

    i75.update()


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

    # Initialize display for startup messages
    display_const = DRIVER_MAP.get(screen.DRIVER_TYPE, DISPLAY_INTERSTATE75_64X32)
    i75 = Interstate75(display=display_const)
    disp = i75.display

    # Show welcome message
    show_startup_message(i75, disp, "FlightTracker", colours.CYAN)
    time.sleep(1)

    # Show connecting message
    show_startup_message(i75, disp, "Connecting...", colours.YELLOW)

    # Connect to WiFi
    print("\nConnecting to WiFi...")
    if not connect_wifi():
        print("ERROR: Could not connect to WiFi")
        print("Check your secrets.py configuration")
        # Show error on display
        show_startup_message(i75, disp, "WiFi Failed!", colours.RED)
        # Flash red LED to indicate error
        for _ in range(10):
            i75.set_led(255, 0, 0)
            time.sleep(0.5)
            i75.set_led(0, 0, 0)
            time.sleep(0.5)
        return

    # Show connected message
    show_startup_message(i75, disp, "Connected!", colours.GREEN)
    time.sleep(1)

    # Sync time
    sync_time()

    # Small delay to let network stabilize
    time.sleep(1)

    # Show waiting message
    show_startup_message(i75, disp, "Scanning...", colours.WHITE)

    # Create and run display (pass existing i75 instance)
    print("\nStarting FlightTracker display...")
    display = Display(i75=i75)
    display.run()


# Auto-start on boot
main()
