"""
WoolShed entity - building for storing wool
"""
import pygame
from constants import *


class WoolShed:
    """Wool shed building for storing harvested wool"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        # For rotations 1 and 3 (90/270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            self.width = WOOLSHED_HEIGHT
            self.height = WOOLSHED_WIDTH
        else:
            self.width = WOOLSHED_WIDTH
            self.height = WOOLSHED_HEIGHT
        self.collision_enabled = True
        self.wool_count = 0  # Per-building resource tracking (starts at 0!)
    
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
        """Check if a point is inside the wool shed boundaries"""
        return (self.x < px < self.x + self.width and 
                self.y < py < self.y + self.height)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the wool shed"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        woolshed_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(woolshed_rect)
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the wool shed"""
        if not self.collision_enabled:
            return False
        
        sheep_rect = pygame.Rect(sx, sy, sw, sh)
        woolshed_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return sheep_rect.colliderect(woolshed_rect)
    
    def can_accept_resource(self):
        """Check if wool shed can accept more wool"""
        return self.wool_count < WOOLSHED_CAPACITY
    
    def add_wool(self):
        """Add wool to storage"""
        if self.wool_count < WOOLSHED_CAPACITY:
            self.wool_count += 1
            return True
        return False
    
    def draw(self, screen, preview=False):
        """Draw the wool shed"""
        # Dark grey floor (dark grey = (64, 64, 64))
        DARK_GREY = (64, 64, 64)
        color = DARK_GREY if not preview else GRAY
        
        # Draw filled rectangle (dark grey floor)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw stored wool if not preview
        if not preview:
            self._draw_stored_wool(screen)
    
    def _draw_stored_wool(self, screen):
        """Draw visual representation of stored wool"""
        margin = 5
        storage_x = self.x + margin
        storage_y = self.y + margin
        storage_width = self.width - (margin * 2)
        storage_height = self.height - (margin * 2)
        
        # Wool size
        wool_width = 6
        wool_height = 6
        
        # Current position tracker
        current_x = storage_x
        current_y = storage_y
        row_height = 0
        
        # Stack all wool
        for i in range(self.wool_count):
            # Check if we need to move to next row
            if current_x + wool_width > storage_x + storage_width:
                current_x = storage_x
                current_y += row_height + 2
                row_height = 0
            
            # Check if we're out of vertical space
            if current_y + wool_height > storage_y + storage_height:
                break
            
            # Draw wool (white circle)
            center_x = current_x + wool_width // 2
            center_y = current_y + wool_height // 2
            pygame.draw.circle(screen, WHITE, (center_x, center_y), wool_width // 2)
            
            current_x += wool_width + 1
            row_height = max(row_height, wool_height)

