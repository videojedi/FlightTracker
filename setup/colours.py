# Colour definitions for Interstate 75 W
# Using RGB tuples instead of graphics.Color objects

class Color:
    """Simple color class to hold RGB values"""
    def __init__(self, r, g, b):
        self.red = int(r)
        self.green = int(g)
        self.blue = int(b)

    def as_tuple(self):
        return (self.red, self.green, self.blue)

# Colour palette
BLACK = Color(0, 0, 0)
WHITE = Color(255, 255, 255)
GREY = Color(192, 192, 192)
YELLOW = Color(255, 255, 0)
YELLOW_DARK = Color(128, 128, 0)
BLUE = Color(55, 14, 237)
BLUE_LIGHT = Color(110, 182, 255)
BLUE_DARK = Color(29, 0, 156)
BLUE_DARKER = Color(0, 0, 78)
PINK = Color(200, 0, 200)
PINK_DARK = Color(112, 0, 145)
PINK_DARKER = Color(96, 1, 125)
GREEN = Color(0, 200, 0)
ORANGE = Color(227, 110, 0)
ORANGE_DARK = Color(113, 55, 0)
RED = Color(255, 0, 0)
RED_LIGHT = Color(255, 195, 195)
CYAN = Color(0, 200, 200)
