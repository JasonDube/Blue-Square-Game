"""
Game constants - colors, sizes, and settings
"""

# Screen dimensions
SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 700

# HUD dimensions (define playable area boundaries)
HUD_TOP_HEIGHT = 25  # Top HUD height
HUD_BOTTOM_HEIGHT = 65  # Bottom HUD height
PLAYABLE_AREA_TOP = HUD_TOP_HEIGHT
PLAYABLE_AREA_BOTTOM = SCREEN_HEIGHT - HUD_BOTTOM_HEIGHT

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
DARKEST_GREEN = (0, 50, 0)  # Almost black green for happiness numbers
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
HUMAN_WANDER_SPEED = 2  # Slower speed when wandering
HUMAN_MIN_FOLLOW_DISTANCE = 20
HUMAN_COLLISION_RADIUS = PLAYER_SIZE + 2
HUMAN_WANDER_MIN_TIME = 2.0  # Minimum time to wander in one direction (seconds)
HUMAN_WANDER_MAX_TIME = 5.0  # Maximum time to wander in one direction (seconds)
HUMAN_STOP_MIN_TIME = 1.0  # Minimum time to stop and rest (seconds)
HUMAN_STOP_MAX_TIME = 4.0  # Maximum time to stop and rest (seconds)

# Happiness settings
HAPPINESS_UNEMPLOYED_PENALTY = 2.0  # Happiness lost per second when unemployed
HAPPINESS_HUNGER_PENALTY = 3.0  # Happiness lost per second when hungry
HAPPINESS_GAIN_RATE = 1.0  # Happiness gained per second when employed and fed

# Structure settings
PEN_SIZE = 100
PEN_GATE_SIZE = 20
TOWNHALL_WIDTH = 120
TOWNHALL_HEIGHT = 100
LUMBERYARD_WIDTH = 100
LUMBERYARD_HEIGHT = 80
STONEYARD_WIDTH = 100
STONEYARD_HEIGHT = 80
IRONYARD_WIDTH = 120
IRONYARD_HEIGHT = 100
SALTYARD_WIDTH = 50
SALTYARD_HEIGHT = 70
HUT_SIZE = 50  # 50x50 square, circle fits inside

# Building capacity (number of resources)
LUMBERYARD_CAPACITY = 89
STONEYARD_CAPACITY = 70  # Updated for visual fit
IRONYARD_CAPACITY = 90   # Updated for visual fit
SALTYARD_CAPACITY = 35   # Salt yard capacity

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
DAY_DURATION = 180  # seconds (3 minutes)
DUSK_FADE_DURATION = 30  # seconds for dusk/dawn fade
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
HARVEST_TIME = 3.0  # Seconds to harvest a resource
HARVEST_TOOL_SIZE = 4  # Size of harvest tool visual

# Resource health (number of units each resource contains)
TREE_INITIAL_HEALTH = 20       # Updated: 20 logs per tree
ROCK_INITIAL_HEALTH = 100      # Updated: 100 stones per rock
IRONMINE_INITIAL_HEALTH = 500  # Updated: 500 iron per mine
SALT_INITIAL_HEALTH = 80       # 80 salt per salt deposit
TREE_HEALTH_PER_HARVEST = 1    # 1 unit lost per harvest
ROCK_HEALTH_PER_HARVEST = 1    # 1 unit lost per harvest
IRONMINE_HEALTH_PER_HARVEST = 1  # 1 unit lost per harvest
SALT_HEALTH_PER_HARVEST = 1    # 1 unit lost per harvest

# Employment settings
AUTO_WORK_SEARCH_RADIUS = 300  # How far employed workers look for resources
AUTO_WORK_INTERVAL = 1.0  # Seconds between finding new work targets

# FPS
FPS = 60
