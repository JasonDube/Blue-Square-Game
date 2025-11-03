"""
Mill entity - building for processing barley into flour and malt
"""
import pygame
import math
import random
from constants import *


class Mill:
    """Mill building for processing barley into flour and malt"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation
        # Track last counts for resource system updates
        self._last_flour_count = 0
        self._last_malt_count = 0
        self.width = 190  # Main building (90) + 2 outbuildings (50 each)
        self.height = 90
        self.collision_enabled = True
        
        # Millstone (spinning circle)
        self.millstone_radius = 25
        self.millstone_center_x = self.x + self.width / 2
        self.millstone_center_y = self.y + self.height / 2
        self.millstone_rotation = 0.0  # Rotation angle in radians
        
        # Barley on millstone (stored as positions using same algorithm as silo)
        self.millstone_barley = []  # List of (x, y) positions for barley on millstone
        
        # Processing
        self.processing_barley = 0  # Amount of barley being processed
        self.processing_timer = 0.0  # Timer for processing
        self.barley_processed_total = 0  # Track total barley processed for malt production
        self.flour_count = 0  # Flour bags stored in flour outbuilding (cap: 64)
        self.malt_count = 0  # Malt barrels stored in malt outbuilding (cap: 25)
        self.FLOUR_CAP = 64
        self.MALT_CAP = 25
        
        # Outbuildings (50x50 brown wooden buildings attached to mill)
        self.flour_outbuilding_x = None  # Will be set based on mill position
        self.flour_outbuilding_y = None
        self.malt_outbuilding_x = None
        self.malt_outbuilding_y = None
        self._initialize_outbuildings()
    
    def _initialize_outbuildings(self):
        """Initialize outbuilding positions (attached to sides of mill based on rotation)"""
        outbuilding_size = 50
        
        # Rotation determines where outbuildings are attached:
        # 0 = top/bottom: flour on left, malt on right
        # 1 = right/left: flour on top, malt on bottom
        # 2 = bottom/top: flour on right, malt on left  
        # 3 = left/right: flour on bottom, malt on top
        
        if self.rotation == 0 or self.rotation == 2:
            # Horizontal layout: flour left, malt right
            if self.rotation == 0:
                self.flour_outbuilding_x = self.x - outbuilding_size
                self.malt_outbuilding_x = self.x + self.width
            else:  # rotation == 2
                self.flour_outbuilding_x = self.x + self.width
                self.malt_outbuilding_x = self.x - outbuilding_size
            self.flour_outbuilding_y = self.y + (self.height - outbuilding_size) / 2
            self.malt_outbuilding_y = self.y + (self.height - outbuilding_size) / 2
        else:  # rotation == 1 or 3
            # Vertical layout: flour top, malt bottom
            if self.rotation == 1:
                self.flour_outbuilding_y = self.y - outbuilding_size
                self.malt_outbuilding_y = self.y + self.height
            else:  # rotation == 3
                self.flour_outbuilding_y = self.y + self.height
                self.malt_outbuilding_y = self.y - outbuilding_size
            self.flour_outbuilding_x = self.x + (self.width - outbuilding_size) / 2
            self.malt_outbuilding_x = self.x + (self.width - outbuilding_size) / 2
        
        # Storage areas (where flour bags and malt barrels are displayed)
        # Flour bags appear in corners (not where millstone is)
        # Malt barrels appear on the floor around the millstone
    
    def can_accept_resource(self):
        """Check if mill can accept more barley"""
        return True  # Unlimited capacity for barley processing
    
    def can_accept_flour(self):
        """Check if flour outbuilding has space"""
        return self.flour_count < self.FLOUR_CAP
    
    def can_accept_malt(self):
        """Check if malt outbuilding has space"""
        return self.malt_count < self.MALT_CAP
    
    def add_barley(self):
        """Add barley to mill for processing - places on millstone"""
        # Add to millstone using same algorithm as silo
        position = self._get_next_barley_position_on_millstone()
        if position:
            self.millstone_barley.append(position)
            self.processing_barley += 1
            return True
        return False  # Millstone full
    
    def _get_next_barley_position_on_millstone(self):
        """Get next position for barley on millstone (using silo algorithm)"""
        import math
        from constants import DARK_BROWN
        
        barley_size = 3
        spacing = 4
        max_radius = self.millstone_radius - 3
        
        # Pre-calculate all valid positions
        valid_positions = []
        
        start_x = self.millstone_center_x - max_radius
        start_y = self.millstone_center_y - max_radius
        
        grid_width = int(max_radius * 2 // spacing) + 1
        grid_height = int(max_radius * 2 // spacing) + 1
        
        for row in range(grid_height):
            for col in range(grid_width):
                x = start_x + col * spacing
                y = start_y + row * spacing
                
                # Check if entire square fits within circle
                corners = [
                    (x, y),
                    (x + barley_size, y),
                    (x, y + barley_size),
                    (x + barley_size, y + barley_size)
                ]
                
                all_within = True
                for corner_x, corner_y in corners:
                    dist_from_center = math.sqrt((corner_x - self.millstone_center_x)**2 + 
                                                (corner_y - self.millstone_center_y)**2)
                    if dist_from_center > max_radius:
                        all_within = False
                        break
                
                if all_within:
                    valid_positions.append((x, y))
        
        # Sort by distance from center
        valid_positions.sort(key=lambda pos: math.sqrt((pos[0] + barley_size/2 - self.millstone_center_x)**2 + 
                                                       (pos[1] + barley_size/2 - self.millstone_center_y)**2))
        
        # Find first position not already taken
        for pos in valid_positions:
            if pos not in self.millstone_barley:
                return pos
        
        return None  # No space available
    
    def _draw_millstone_barley(self, screen):
        """Draw barley on millstone"""
        from constants import DARK_BROWN
        barley_size = 3
        for x, y in self.millstone_barley:
            pygame.draw.rect(screen, DARK_BROWN, (x, y, barley_size, barley_size))
    
    def update(self, dt):
        """Update mill processing and millstone rotation"""
        # Rotate millstone
        self.millstone_rotation += MILLSTONE_ROTATION_SPEED * dt
        if self.millstone_rotation >= 2 * math.pi:
            self.millstone_rotation -= 2 * math.pi
        
        # Process barley into flour and malt
        if self.processing_barley > 0:
            self.processing_timer += dt
            if self.processing_timer >= MILL_PROCESSING_TIME:
                # Convert 1 barley to 2 flour (respecting flour cap)
                self.processing_barley -= 1
                self.barley_processed_total += 1
                
                # Add flour, but respect the cap
                flour_to_add = min(2, self.FLOUR_CAP - self.flour_count)
                self.flour_count += flour_to_add
                
                self.processing_timer = 0.0
                
                # Remove one barley from millstone (oldest/first one)
                if len(self.millstone_barley) > 0:
                    self.millstone_barley.pop(0)
                
                # Every 2 barley units processed = 4 flour + 1 malt barrel (byproduct)
                # Since we process 1 at a time, when we've processed 2 total, create 1 malt (respecting cap)
                if self.barley_processed_total >= 2:
                    if self.malt_count < self.MALT_CAP:
                        self.malt_count += 1
                    self.barley_processed_total -= 2  # Reset counter (keep remainder if needed)
    
    def collect_flour(self, amount):
        """Collect flour from the mill"""
        collected = min(amount, self.flour_count)
        self.flour_count -= collected
        return collected
    
    def collect_malt(self, amount):
        """Collect malt from the mill"""
        collected = min(amount, self.malt_count)
        self.malt_count -= collected
        return collected
    
    def get_total_flour_produced(self):
        """Get total flour that should be in resource system"""
        return self.flour_count
    
    def get_total_malt_produced(self):
        """Get total malt that should be in resource system"""
        return self.malt_count
    
    def check_collision_player(self, px, py):
        """Check if player collides with the mill"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        mill_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(mill_rect)
    
    def is_point_inside(self, px, py):
        """Check if a point is inside the mill boundaries"""
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def get_random_position_inside(self):
        """Get a random position inside the mill (for miller to walk around)"""
        margin = 10  # Margin from edges
        x = self.x + margin + (self.width - margin * 2) * random.random()
        y = self.y + margin + (self.height - margin * 2) * random.random()
        return x, y
    
    def draw(self, screen, preview=False):
        """Draw the mill with outbuildings"""
        if preview:
            # Draw preview (handled by build mode)
            return
        
        # Draw outbuildings first (so main mill is on top)
        self._draw_outbuildings(screen)
        
        # Draw filled orange rectangle (90x90)
        pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw spinning millstone (filled light grey circle with rotation indicator)
        millstone_color = LIGHT_GREY
        center = (int(self.millstone_center_x), int(self.millstone_center_y))
        pygame.draw.circle(screen, millstone_color, center, self.millstone_radius)
        pygame.draw.circle(screen, BLACK, center, self.millstone_radius, 2)
        
        # Draw rotation indicator (spoke lines) to show rotation
        import math
        for i in range(4):  # 4 spokes
            angle = self.millstone_rotation + (i * math.pi / 2)
            end_x = self.millstone_center_x + math.cos(angle) * (self.millstone_radius - 2)
            end_y = self.millstone_center_y + math.sin(angle) * (self.millstone_radius - 2)
            pygame.draw.line(screen, BLACK, center, (int(end_x), int(end_y)), 2)
        
        # Draw barley on millstone (using same algorithm as silo)
        self._draw_millstone_barley(screen)
        
        # Draw flour bags (in flour outbuilding)
        self._draw_flour_bags(screen)
        
        # Draw malt barrels (in malt outbuilding)
        self._draw_malt_barrels(screen)
    
    def _draw_outbuildings(self, screen):
        """Draw the two brown wooden outbuildings attached to the mill"""
        from constants import WOOD_BROWN
        outbuilding_size = 50
        
        # Draw flour outbuilding (left side) - filled brown
        pygame.draw.rect(screen, WOOD_BROWN, 
                        (self.flour_outbuilding_x, self.flour_outbuilding_y, 
                         outbuilding_size, outbuilding_size))
        pygame.draw.rect(screen, BLACK, 
                        (self.flour_outbuilding_x, self.flour_outbuilding_y, 
                         outbuilding_size, outbuilding_size), 2)
        
        # Draw malt outbuilding (right side) - filled brown
        pygame.draw.rect(screen, WOOD_BROWN, 
                        (self.malt_outbuilding_x, self.malt_outbuilding_y, 
                         outbuilding_size, outbuilding_size))
        pygame.draw.rect(screen, BLACK, 
                        (self.malt_outbuilding_x, self.malt_outbuilding_y, 
                         outbuilding_size, outbuilding_size), 2)
    
    def _draw_flour_bags(self, screen):
        """Draw flour bags in the flour outbuilding - tightly packed"""
        bag_size = 4
        margin = 3
        spacing = 5  # Tighter spacing (1 pixel gap between bags)
        outbuilding_size = 50
        
        # Calculate positions within flour outbuilding
        bag_positions = []
        start_x = self.flour_outbuilding_x + margin
        start_y = self.flour_outbuilding_y + margin
        
        for row in range(int((outbuilding_size - margin * 2) // spacing)):
            for col in range(int((outbuilding_size - margin * 2) // spacing)):
                x = start_x + col * spacing
                y = start_y + row * spacing
                if x + bag_size <= self.flour_outbuilding_x + outbuilding_size - margin and \
                   y + bag_size <= self.flour_outbuilding_y + outbuilding_size - margin:
                    bag_positions.append((x, y))
        
        # Draw flour bags
        for i in range(min(self.flour_count, len(bag_positions))):
            x, y = bag_positions[i]
            pygame.draw.rect(screen, FLOUR_BAG_COLOR, (x, y, bag_size, bag_size))
            pygame.draw.rect(screen, BLACK, (x, y, bag_size, bag_size), 1)
    
    def _draw_malt_barrels(self, screen):
        """Draw malt barrels in the malt outbuilding"""
        barrel_size = 5
        margin = 5
        spacing = 7
        outbuilding_size = 50
        
        # Calculate positions within malt outbuilding
        barrel_positions = []
        start_x = self.malt_outbuilding_x + margin
        start_y = self.malt_outbuilding_y + margin
        
        for row in range(int((outbuilding_size - margin * 2) // spacing)):
            for col in range(int((outbuilding_size - margin * 2) // spacing)):
                x = start_x + col * spacing
                y = start_y + row * spacing
                if x + barrel_size <= self.malt_outbuilding_x + outbuilding_size - margin and \
                   y + barrel_size <= self.malt_outbuilding_y + outbuilding_size - margin:
                    barrel_positions.append((x, y))
        
        # Draw malt barrels
        for i in range(min(self.malt_count, len(barrel_positions))):
            x, y = barrel_positions[i]
            # Draw malt barrel (cylinder-like shape)
            pygame.draw.rect(screen, MALT_BARREL_COLOR, (x, y, barrel_size, barrel_size))
            pygame.draw.rect(screen, BLACK, (x, y, barrel_size, barrel_size), 1)
            # Draw horizontal lines to make it look like a barrel
            pygame.draw.line(screen, BLACK, (x, y + 1), (x + barrel_size, y + 1), 1)
            pygame.draw.line(screen, BLACK, (x, y + barrel_size - 1), (x + barrel_size, y + barrel_size - 1), 1)

