"""
Game constants - colors, sizes, and settings
"""

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600

# Colors
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
DARK_GREEN = (0, 180, 0)
DARKER_GREEN = (0, 120, 0)
PINK = (255, 192, 203)
TAN = (210, 180, 140)

# Player settings
PLAYER_SIZE = 10
PLAYER_SPEED = 5

# Sheep settings
SHEEP_WIDTH = 6
SHEEP_HEIGHT = 4
SHEEP_SPEED = 3
SHEEP_GRAZE_SPEED = 1
SHEEP_GRAZE_MIN_TIME = 5
SHEEP_GRAZE_MAX_TIME = 10
SHEEP_MIN_FOLLOW_DISTANCE = 20
SHEEP_COLLISION_RADIUS = 6

# Human settings
HUMAN_SIZE = PLAYER_SIZE
HUMAN_SPEED = 5
HUMAN_MIN_FOLLOW_DISTANCE = 20
HUMAN_COLLISION_RADIUS = PLAYER_SIZE + 2

# Structure settings
PEN_SIZE = 100
PEN_GATE_SIZE = 20
TOWNHALL_WIDTH = 120
TOWNHALL_HEIGHT = 100

# Herd settings
HERD_BOUNDARY_SIZE = 100

# Tree settings
TREE_TRUNK_WIDTH = 8
TREE_TRUNK_HEIGHT = 20
TREE_CROWN_RADIUS = 15
NUM_TREES = 30
MIN_TREE_DISTANCE = 50
MIN_TREE_PEN_DISTANCE = 100

# Day/night cycle
DAY_DURATION = 60  # seconds
START_HOUR = 6  # 6:00 AM

# Reproduction settings
REPRODUCTION_CHANCE = 0.5
REPRODUCTION_SPAWN_OFFSET = 50

# Grass settings
GRASS_REGROWTH_MIN = 0.10
GRASS_REGROWTH_MAX = 0.20

# Gender separation
GENDER_SEPARATION_DISTANCE = 30

# Harvest settings
HARVEST_TIME = 30  # seconds to harvest a tree
HARVEST_TOOL_SIZE = 6  # size of harvest tool pixel
TREE_INITIAL_HEALTH = 100  # percentage
TREE_HEALTH_PER_HARVEST = 1  # percentage lost per harvest

# FPS
FPS = 60

# Resource settings
HARVEST_TIME = 3.0  # Seconds to harvest a tree
HARVEST_TOOL_SIZE = 4  # Size of harvest tool visual