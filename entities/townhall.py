"""
TownHall entity - rectangular building structure and employment center
"""
import pygame
from constants import *


class TownHall:
    """Town hall building with toggle-able collision and employment management"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.width = TOWNHALL_WIDTH
        self.height = TOWNHALL_HEIGHT
        self.collision_enabled = True
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        
        # Employment tracking
        self.employed_humans = []  # List of humans employed at this town hall
        self.job_slots = {
            'lumberjack': {'max': 5, 'filled': 0},  # Can have up to 5 lumberjacks
            # Future: 'farmer': {'max': 3, 'filled': 0}, etc.
        }
    
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
    
    def can_hire(self, job_type):
        """Check if there's room to hire for a specific job"""
        if job_type not in self.job_slots:
            return False
        job = self.job_slots[job_type]
        return job['filled'] < job['max']
    
    def hire_human(self, human, job_type):
        """Hire a human for a specific job"""
        if not self.can_hire(job_type):
            return False
        
        self.employed_humans.append(human)
        self.job_slots[job_type]['filled'] += 1
        human.job = job_type
        human.employer = self
        human.state = "employed"
        return True
    
    def fire_human(self, human):
        """Fire a human from their job"""
        if human not in self.employed_humans:
            return False
        
        self.employed_humans.remove(human)
        if human.job in self.job_slots:
            self.job_slots[human.job]['filled'] -= 1
        human.job = None
        human.employer = None
        human.state = "stay"
        return True
    
    def contains_point(self, px, py):
        """Check if a point is inside the town hall"""
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def draw(self, screen, preview=False, resource_system=None):
        """Draw the town hall"""
        color = TAN if not preview else GRAY
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw stored resources if not preview and resource system exists
        # Town halls only store wool and meat (logs/stones/iron have dedicated buildings)
        if not preview and resource_system:
            self._draw_stored_resources(screen, resource_system)
        
        # Draw dot button on front wall
        button_x, button_y = self.get_button_pos()
        button_color = RED if self.collision_enabled else DARKER_GREEN
        pygame.draw.circle(screen, button_color, (button_x, button_y), 5)
    
    def _draw_stored_resources(self, screen, resource_system):
        """Draw visual representation of stored resources"""
        from systems.resource_system import ResourceVisualizer, ResourceType
        
        # Town halls only store resources WITHOUT dedicated buildings (wool, meat)
        # Logs, stones, and iron have their own storage buildings
        all_resources = resource_system.get_all_resources()
        townhall_resources = {
            ResourceType.WOOL: all_resources.get(ResourceType.WOOL, 0),
            ResourceType.MEAT: all_resources.get(ResourceType.MEAT, 0)
        }
        
        positions = ResourceVisualizer.calculate_storage_positions(self, townhall_resources)
        
        for resource_type, x, y, visual in positions:
            if visual['shape'] == 'rect':
                pygame.draw.rect(screen, visual['color'], 
                               (x, y, visual['width'], visual['height']))
            elif visual['shape'] == 'circle':
                radius = visual['width'] // 2
                pygame.draw.circle(screen, visual['color'], 
                                 (x + radius, y + radius), radius)
