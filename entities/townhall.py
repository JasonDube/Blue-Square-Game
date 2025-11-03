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
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        # For rotations 1 and 3 (90/270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            self.width = TOWNHALL_HEIGHT
            self.height = TOWNHALL_WIDTH
        else:
            self.width = TOWNHALL_WIDTH
            self.height = TOWNHALL_HEIGHT
        self.collision_enabled = False  # Passable for testing purposes
        
        # Employment tracking
        self.employed_humans = []  # List of humans employed at this town hall
        self.job_slots = {
            'lumberjack': {'max': 5, 'filled': 0},  # Can have up to 5 lumberjacks
            'miner': {'max': 5, 'filled': 0},  # Can have up to 5 miners
            'stoneworker': {'max': 5, 'filled': 0},  # Can have up to 5 stoneworkers
            'saltworker': {'max': 5, 'filled': 0},  # Can have up to 5 saltworkers
            'shearer': {'max': 5, 'filled': 0},  # Can have up to 5 shearers (female only)
            'barleyfarmer': {'max': 5, 'filled': 0},  # Can have up to 5 barley farmers
            'miller': {'max': 5, 'filled': 0},  # Can have up to 5 millers
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
        human.is_employed = True  # FIXED: Set employment flag
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
        human.is_employed = False  # Clear employment flag
        human.state = "wander"  # Set to wander (unemployed) state
        # Release hut if they had one
        if human.home_hut:
            human.home_hut.release()
            human.home_hut = None
        return True
    
    def contains_point(self, px, py):
        """Check if a point is inside the town hall"""
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def get_bench_rect(self):
        """Get the rectangle for the bench on the front side of the town hall"""
        bench_thickness = 12
        if self.rotation == 0:  # Front wall is top
            bench_x = self.x
            bench_y = self.y - bench_thickness
            bench_width = self.width
            bench_height = bench_thickness
        elif self.rotation == 1:  # Front wall is right
            bench_x = self.x + self.width
            bench_y = self.y
            bench_width = bench_thickness
            bench_height = self.height
        elif self.rotation == 2:  # Front wall is bottom
            bench_x = self.x
            bench_y = self.y + self.height
            bench_width = self.width
            bench_height = bench_thickness
        else:  # Front wall is left (rotation == 3)
            bench_x = self.x - bench_thickness
            bench_y = self.y
            bench_width = bench_thickness
            bench_height = self.height
        return pygame.Rect(bench_x, bench_y, bench_width, bench_height)
    
    def get_bench_sitting_positions(self, human_size):
        """Get list of positions where humans can sit on the bench (with 2px spacing)"""
        bench_rect = self.get_bench_rect()
        spacing = 2
        positions = []
        
        if self.rotation == 0 or self.rotation == 2:  # Horizontal bench
            # Calculate how many humans can fit
            total_space = bench_rect.width
            space_per_human = human_size + spacing
            num_humans = int(total_space / space_per_human)
            start_x = bench_rect.x + (total_space - (num_humans * space_per_human - spacing)) / 2
            
            for i in range(num_humans):
                x = start_x + i * space_per_human
                y = bench_rect.y + (bench_rect.height - human_size) / 2
                positions.append((x, y))
        else:  # Vertical bench (rotation == 1 or 3)
            # Calculate how many humans can fit
            total_space = bench_rect.height
            space_per_human = human_size + spacing
            num_humans = int(total_space / space_per_human)
            start_y = bench_rect.y + (total_space - (num_humans * space_per_human - spacing)) / 2
            
            for i in range(num_humans):
                x = bench_rect.x + (bench_rect.width - human_size) / 2
                y = start_y + i * space_per_human
                positions.append((x, y))
        
        return positions
    
    def draw(self, screen, preview=False, resource_system=None):
        """Draw the town hall"""
        color = TAN if not preview else GRAY
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw brown bench on front side (only if not preview)
        if not preview:
            bench_rect = self.get_bench_rect()
            pygame.draw.rect(screen, BROWN, bench_rect)
            pygame.draw.rect(screen, BLACK, bench_rect, 1)
        
        # Draw stored resources if not preview and resource system exists
        # Town halls only store meat (logs/stones/iron/wool have dedicated buildings)
        if not preview and resource_system:
            self._draw_stored_resources(screen, resource_system)
    
    def _draw_stored_resources(self, screen, resource_system):
        """Draw visual representation of stored resources"""
        from systems.resource_system import ResourceVisualizer, ResourceType
        
        # Town halls only store resources WITHOUT dedicated buildings (meat only now, wool goes to wool sheds)
        # Logs, stones, iron, and wool have their own storage buildings
        all_resources = resource_system.get_all_resources()
        townhall_resources = {
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
