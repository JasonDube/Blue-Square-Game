"""
SaltYard entity - building for storing harvested salt
"""
import pygame
from constants import *


class SaltYard:
    """Salt yard building for storing harvested salt"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        # For rotations 1 and 3 (90/270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            self.width = SALTYARD_HEIGHT
            self.height = SALTYARD_WIDTH
        else:
            self.width = SALTYARD_WIDTH
            self.height = SALTYARD_HEIGHT
        self.collision_enabled = False  # Passable - no collision
        self.salt_count = 0  # Per-building resource tracking
    
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
        """Check if a point is inside the salt yard boundaries"""
        return (self.x < px < self.x + self.width and 
                self.y < py < self.y + self.height)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the salt yard (always False - passable)"""
        return False
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the salt yard (always False - passable)"""
        return False
    
    def can_accept_resource(self):
        """Check if salt yard can accept more salt"""
        return self.salt_count < SALTYARD_CAPACITY
    
    def add_salt(self):
        """Add salt to storage"""
        if self.salt_count < SALTYARD_CAPACITY:
            self.salt_count += 1
            return True
        return False
    
    def draw(self, screen, preview=False):
        """Draw the salt yard"""
        floor_color = GRAY if not preview else GRAY  # Grey floor
        
        # Draw filled grey rectangle (floor)
        pygame.draw.rect(screen, floor_color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw stored salt if not preview
        if not preview:
            self._draw_stored_salt(screen)
    
    def _draw_stored_salt(self, screen):
        """Draw visual representation of stored salt"""
        margin = 5
        storage_x = self.x + margin
        storage_y = self.y + margin
        storage_width = self.width - (margin * 2)
        storage_height = self.height - (margin * 2)
        
        # Salt crystal size
        salt_size = 6
        
        # Current position tracker
        current_x = storage_x
        current_y = storage_y
        
        # Stack all salt
        for i in range(self.salt_count):
            # Check if we need to move to next row
            if current_x + salt_size > storage_x + storage_width:
                current_x = storage_x
                current_y += salt_size + 2
            
            # Check if we're out of vertical space
            if current_y + salt_size > storage_y + storage_height:
                break
            
            # Draw salt crystal (small white circle)
            pygame.draw.circle(screen, WHITE, (current_x + salt_size//2, current_y + salt_size//2), salt_size//2)
            pygame.draw.circle(screen, (200, 200, 200), (current_x + salt_size//2, current_y + salt_size//2), salt_size//2, 1)
            
            current_x += salt_size + 1

