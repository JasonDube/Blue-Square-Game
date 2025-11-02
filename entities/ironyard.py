"""
IronYard entity - building for storing harvested iron
"""
import pygame
from constants import *


class IronYard:
    """Iron yard building for storing harvested iron"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.width = IRONYARD_WIDTH
        self.height = IRONYARD_HEIGHT
        self.collision_enabled = True
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        self.iron_count = 0  # Per-building resource tracking
    
    def get_button_pos(self):
        """Get the position of the button on the front wall"""
        if self.rotation == 0:  # Front wall is top
            return (self.x + self.width // 2, self.y)
        elif self.rotation == 1:  # Front wall is right
            return (self.x + self.width, self.y + self.height // 2)
        elif self.rotation == 2:  # Front wall is bottom
            return (self.x + self.width // 2, self.y + self.height)
        else:  # Front wall is left
            return (self.x, self.y + self.height // 2)
    
    def get_button_rect(self):
        """Get the clickable rectangle for the button"""
        button_x, button_y = self.get_button_pos()
        return pygame.Rect(button_x - 5, button_y - 5, 10, 10)
    
    def is_point_inside(self, px, py):
        """Check if a point is inside the iron yard boundaries"""
        return (self.x < px < self.x + self.width and 
                self.y < py < self.y + self.height)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the iron yard"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        ironyard_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(ironyard_rect)
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the iron yard"""
        if not self.collision_enabled:
            return False
        
        sheep_rect = pygame.Rect(sx, sy, sw, sh)
        ironyard_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return sheep_rect.colliderect(ironyard_rect)
    
    def can_accept_resource(self):
        """Check if iron yard can accept more iron"""
        return self.iron_count < IRONYARD_CAPACITY
    
    def add_iron(self):
        """Add iron to storage"""
        if self.iron_count < IRONYARD_CAPACITY:
            self.iron_count += 1
            return True
        return False
    
    def draw(self, screen, preview=False):
        """Draw the iron yard"""
        color = (120, 120, 140) if not preview else GRAY  # Steel/dark blue for iron
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw stored iron if not preview
        if not preview:
            self._draw_stored_iron(screen)
        
        # Draw dot button on front wall
        button_x, button_y = self.get_button_pos()
        button_color = RED if self.collision_enabled else DARKER_GREEN
        pygame.draw.circle(screen, button_color, (button_x, button_y), 5)
    
    def _draw_stored_iron(self, screen):
        """Draw visual representation of stored iron"""
        margin = 5
        storage_x = self.x + margin
        storage_y = self.y + margin
        storage_width = self.width - (margin * 2)
        storage_height = self.height - (margin * 2)
        
        # Iron bar size
        iron_width = 6
        iron_height = 12
        
        # Current position tracker
        current_x = storage_x
        current_y = storage_y
        
        # Stack all iron
        for i in range(self.iron_count):
            # Check if we need to move to next row
            if current_x + iron_width > storage_x + storage_width:
                current_x = storage_x
                current_y += iron_height + 2
            
            # Check if we're out of vertical space
            if current_y + iron_height > storage_y + storage_height:
                break
            
            # Draw iron bar
            pygame.draw.rect(screen, (200, 100, 50), (current_x, current_y, iron_width, iron_height))
            
            current_x += iron_width + 1