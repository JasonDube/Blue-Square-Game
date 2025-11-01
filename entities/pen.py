"""
Pen entity - square enclosure for sheep
"""
import pygame
from constants import *


class Pen:
    """Square pen structure with toggle-able collision"""
    
    def __init__(self, x, y, size=PEN_SIZE, rotation=0):
        self.x = x
        self.y = y
        self.size = size
        self.collision_enabled = True
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
    
    def get_button_pos(self):
        """Get the position of the red dot button on the front wall"""
        if self.rotation == 0:  # Front wall is top
            return (self.x + self.size // 2, self.y)
        elif self.rotation == 1:  # Front wall is right
            return (self.x + self.size, self.y + self.size // 2)
        elif self.rotation == 2:  # Front wall is bottom
            return (self.x + self.size // 2, self.y + self.size)
        else:  # Front wall is left
            return (self.x, self.y + self.size // 2)
    
    def get_button_rect(self):
        """Get the clickable rectangle for the button"""
        button_x, button_y = self.get_button_pos()
        return pygame.Rect(button_x - 5, button_y - 5, 10, 10)
    
    def is_point_inside(self, px, py):
        """Check if a point is inside the pen boundaries"""
        return (self.x < px < self.x + self.size and 
                self.y < py < self.y + self.size)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the pen"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        walls = self._get_walls()
        for wall in walls:
            if player_rect.colliderect(wall):
                return True
        return False
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the pen"""
        if not self.collision_enabled:
            return False
        
        sheep_rect = pygame.Rect(sx, sy, sw, sh)
        walls = self._get_walls()
        for wall in walls:
            if sheep_rect.colliderect(wall):
                return True
        return False
    
    def _get_walls(self):
        """Get all wall rectangles (complete square)"""
        walls = [
            pygame.Rect(self.x, self.y, self.size, 2),  # Top
            pygame.Rect(self.x + self.size, self.y, 2, self.size),  # Right
            pygame.Rect(self.x, self.y + self.size, self.size, 2),  # Bottom
            pygame.Rect(self.x, self.y, 2, self.size)  # Left
        ]
        return walls
    
    def draw(self, screen, preview=False):
        """Draw the pen"""
        color = BROWN if not preview else GRAY
        
        # Draw complete square - all 4 walls
        pygame.draw.line(screen, color, (self.x, self.y), (self.x + self.size, self.y), 2)
        pygame.draw.line(screen, color, (self.x + self.size, self.y), (self.x + self.size, self.y + self.size), 2)
        pygame.draw.line(screen, color, (self.x + self.size, self.y + self.size), (self.x, self.y + self.size), 2)
        pygame.draw.line(screen, color, (self.x, self.y + self.size), (self.x, self.y), 2)
        
        # Draw dot button on front wall
        button_x, button_y = self.get_button_pos()
        button_color = RED if self.collision_enabled else DARKER_GREEN
        pygame.draw.circle(screen, button_color, (button_x, button_y), 5)
