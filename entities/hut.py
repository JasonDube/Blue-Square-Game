"""
Hut entity - circular dwelling for employed workers
"""
import pygame
from constants import *


class Hut:
    """Hut building - circular dwelling that can be claimed by employed workers"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = HUT_SIZE  # 50x50 square
        self.radius = HUT_SIZE // 2  # Circle fits within square
        self.collision_enabled = True
        self.owner = None  # The human who owns this hut (None if unclaimed)
    
    def contains_point(self, px, py):
        """Check if a point is inside the hut (circular boundary)"""
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        dist = ((px - center_x) ** 2 + (py - center_y) ** 2) ** 0.5
        return dist <= self.radius
    
    def check_collision_player(self, px, py):
        """Check if player collides with the hut"""
        if not self.collision_enabled:
            return False
        # Check if player position is inside the circular hut
        player_center_x = px + PLAYER_SIZE / 2
        player_center_y = py + PLAYER_SIZE / 2
        return self.contains_point(player_center_x, player_center_y)
    
    def is_available(self):
        """Check if hut is available for claiming"""
        return self.owner is None
    
    def claim(self, human):
        """Claim this hut for a human (only if available)"""
        if self.is_available() and human.is_employed:
            self.owner = human
            return True
        return False
    
    def release(self):
        """Release the hut (make it available again)"""
        self.owner = None
    
    def draw(self, screen, preview=False):
        """Draw the hut as a circle"""
        center_x = int(self.x + self.size / 2)
        center_y = int(self.y + self.size / 2)
        
        if preview:
            # Preview mode - draw with transparency
            preview_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(preview_surface, (*BROWN, 128), (self.radius, self.radius), self.radius)
            screen.blit(preview_surface, (self.x, self.y))
        else:
            # Normal mode - draw brown circle
            pygame.draw.circle(screen, BROWN, (center_x, center_y), self.radius)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), self.radius, 2)  # Border
        
        # Draw indicator if claimed (small dot or color change)
        if self.owner:
            # Draw a small colored dot to show it's claimed
            owner_color = BLUE if self.owner.gender == "male" else PINK
            pygame.draw.circle(screen, owner_color, (center_x, center_y), 5)

