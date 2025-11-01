"""
TownHall entity - rectangular building structure
"""
import pygame
from constants import *


class TownHall:
    """Town hall building with toggle-able collision"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.width = TOWNHALL_WIDTH
        self.height = TOWNHALL_HEIGHT
        self.collision_enabled = True
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
    
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
        """Check if a point is inside the town hall boundaries"""
        return (self.x < px < self.x + self.width and 
                self.y < py < self.y + self.height)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the town hall"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        townhall_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(townhall_rect)
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the town hall"""
        if not self.collision_enabled:
            return False
        
        sheep_rect = pygame.Rect(sx, sy, sw, sh)
        townhall_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return sheep_rect.colliderect(townhall_rect)
    
    def draw(self, screen, preview=False, resource_system=None):
        """Draw the town hall"""
        color = TAN if not preview else GRAY
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw stored resources if not preview and resource system exists
        if not preview and resource_system:
            self._draw_stored_resources(screen, resource_system)
        
        # Draw dot button on front wall
        button_x, button_y = self.get_button_pos()
        button_color = RED if self.collision_enabled else DARKER_GREEN
        pygame.draw.circle(screen, button_color, (button_x, button_y), 5)
    
    def _draw_stored_resources(self, screen, resource_system):
        """Draw visual representation of stored resources"""
        from systems.resource_system import ResourceVisualizer
        
        resources = resource_system.get_all_resources()
        positions = ResourceVisualizer.calculate_storage_positions(self, resources)
        
        for resource_type, x, y, visual in positions:
            if visual['shape'] == 'rect':
                pygame.draw.rect(screen, visual['color'], 
                               (x, y, visual['width'], visual['height']))
            elif visual['shape'] == 'circle':
                radius = visual['width'] // 2
                pygame.draw.circle(screen, visual['color'], 
                                 (x + radius, y + radius), radius)