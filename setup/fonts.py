# Font configuration for Interstate 75 W
# PicoGraphics uses built-in bitmap fonts

# Font names available in PicoGraphics:
# - "bitmap6" (small)
# - "bitmap8" (regular)
# - "bitmap14_outline" (large outlined)

# Font mapping to match original project's font sizes
# Original used: 4x6, 5x8, 6x12, 8x13, 8x13B

EXTRASMALL = "bitmap6"      # ~4x6 equivalent
SMALL = "bitmap6"           # ~5x8 equivalent
REGULAR = "bitmap8"         # ~6x12 equivalent
LARGE = "bitmap8"           # ~8x13 equivalent
LARGE_BOLD = "bitmap8"      # ~8x13B equivalent (no bold in PicoGraphics)

# Font heights (approximate, for positioning calculations)
EXTRASMALL_HEIGHT = 6
SMALL_HEIGHT = 6
REGULAR_HEIGHT = 8
LARGE_HEIGHT = 8
LARGE_BOLD_HEIGHT = 8

# Scale factors for fonts
EXTRASMALL_SCALE = 1
SMALL_SCALE = 1
REGULAR_SCALE = 1
LARGE_SCALE = 1
LARGE_BOLD_SCALE = 1
