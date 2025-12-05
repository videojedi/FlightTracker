# Screen dimensions for Interstate 75 W
# Default: 64x32 panel

try:
    from config import DISPLAY_TYPE
except ImportError:
    DISPLAY_TYPE = "64x32"

# Parse display type
# Note: "64x32h" is for panels that need 64x64 driver mode but are physically 32px tall
if DISPLAY_TYPE == "32x32":
    WIDTH = 32
    HEIGHT = 32
    DRIVER_TYPE = "32x32"
elif DISPLAY_TYPE == "64x32":
    WIDTH = 64
    HEIGHT = 32
    DRIVER_TYPE = "64x32"
elif DISPLAY_TYPE == "64x32h":
    # Half-height mode: use 64x64 driver but only draw to top 32 pixels
    WIDTH = 64
    HEIGHT = 32
    DRIVER_TYPE = "64x64"
elif DISPLAY_TYPE == "64x64":
    WIDTH = 64
    HEIGHT = 64
    DRIVER_TYPE = "64x64"
elif DISPLAY_TYPE == "128x64":
    WIDTH = 128
    HEIGHT = 64
    DRIVER_TYPE = "128x64"
else:
    # Default to 64x32
    WIDTH = 64
    HEIGHT = 32
    DRIVER_TYPE = "64x32"
