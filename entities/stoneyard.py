"""
StoneYard entity - building for storing harvested stones
"""
import pygame
from constants import *


class StoneYard:
    """Stone yard building for storing harvested stones"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        # For rotations 1 and 3 (90/270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            self.width = STONEYARD_HEIGHT
            self.height = STONEYARD_WIDTH
        else:
            self.width = STONEYARD_WIDTH
            self.height = STONEYARD_HEIGHT
        self.collision_enabled = False  # Collision disabled for prototype
        self.stone_count = 0  # Per-building resource tracking
    
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
        """Check if a point is inside the stone yard boundaries"""
        return (self.x < px < self.x + self.width and 
                self.y < py < self.y + self.height)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the stone yard"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        stoneyard_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(stoneyard_rect)
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the stone yard"""
        if not self.collision_enabled:
            return False
        
        sheep_rect = pygame.Rect(sx, sy, sw, sh)
        stoneyard_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return sheep_rect.colliderect(stoneyard_rect)
    
    def can_accept_resource(self):
        """Check if stone yard can accept more stones"""
        return self.stone_count < STONEYARD_CAPACITY
    
    def add_stone(self):
        """Add a stone to storage"""
        if self.stone_count < STONEYARD_CAPACITY:
            self.stone_count += 1
            return True
        return False
    
    def draw(self, screen, preview=False):
        """Draw the stone yard"""
        color = (160, 160, 160) if not preview else GRAY  # Light gray for stone
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw stored stones if not preview
        if not preview:
            self._draw_stored_stones(screen)
    
    def _draw_stored_stones(self, screen):
        """Draw visual representation of stored stones"""
        margin = 5
        storage_x = self.x + margin
        storage_y = self.y + margin
        storage_width = self.width - (margin * 2)
        storage_height = self.height - (margin * 2)
        
        # Stone size
        stone_size = 8
        
        # Current position tracker
        current_x = storage_x
        current_y = storage_y
        
        # Stack all stones
        for i in range(self.stone_count):
            # Check if we need to move to next row
            if current_x + stone_size > storage_x + storage_width:
                current_x = storage_x
                current_y += stone_size + 2
            
            # Check if we're out of vertical space
            if current_y + stone_size > storage_y + storage_height:
                break
            
            # Draw stone
            pygame.draw.circle(screen, (100, 100, 100), (current_x + stone_size//2, current_y + stone_size//2), stone_size//2)
            
            current_x += stone_size + 1
