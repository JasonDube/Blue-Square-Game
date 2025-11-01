"""
Human entity - controllable character that can follow player
"""
import pygame
from constants import *
from utils.geometry import distance


class Human:
    """Human character that can follow or stay"""
    
    def __init__(self, x, y, gender="male"):
        self.x = x
        self.y = y
        self.size = HUMAN_SIZE
        self.state = "stay"  # "follow", "stay", or "harvest"
        self.selected = False
        self.speed = HUMAN_SPEED
        self.gender = gender  # "male" or "female"
        
        # Harvest-related attributes
        self.harvest_target = None  # Tree being harvested
        self.harvest_timer = 0.0  # Time spent harvesting current tree
        self.carrying_log = False  # Whether human is carrying a log to town hall
    
    def draw(self, screen, debug_mode):
        """Draw the human based on gender"""
        if self.gender == "male":
            # Blue unfilled square
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size), 2)
        else:
            # Pink unfilled circle
            pygame.draw.circle(
                screen, PINK, 
                (int(self.x + self.size/2), int(self.y + self.size/2)), 
                self.size//2, 2
            )
        
        # Draw selection indicator
        if self.selected:
            pygame.draw.circle(
                screen, YELLOW, 
                (int(self.x + self.size/2), int(self.y + self.size/2)), 
                10, 1
            )
        
        # Draw debug info
        if debug_mode:
            self._draw_debug_info(screen)
    
    def _draw_debug_info(self, screen):
        """Draw state indicator"""
        font_small = pygame.font.Font(None, 16)
        
        state_map = {
            "follow": ("F", GREEN),
            "stay": ("S", RED),
            "harvest": ("H", YELLOW)
        }
        
        state_text, state_color = state_map.get(self.state, ("S", RED))
        text_surface = font_small.render(state_text, True, state_color)
        screen.blit(text_surface, (int(self.x + self.size + 2), int(self.y - 2)))
    
    def move_towards(self, target_x, target_y, other_humans, pen_list, townhall_list, sheep_list=None):
        """Move towards target position"""
        if self.state != "follow":
            return
        
        # Calculate direction to target
        dx = target_x - (self.x + self.size/2)
        dy = target_y - (self.y + self.size/2)
        dist = distance(self.x + self.size/2, self.y + self.size/2, target_x, target_y)
        
        # Only move if not too close
        if dist > HUMAN_MIN_FOLLOW_DISTANCE:
            self._apply_movement(dx, dy, dist, other_humans, pen_list, townhall_list)
    
    def _apply_movement(self, dx, dy, dist, other_humans, pen_list, townhall_list):
        """Apply movement with collision detection"""
        dx = (dx / dist) * self.speed
        dy = (dy / dist) * self.speed
        
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy
        
        # Check collision with structures
        if self._check_structure_collisions(pen_list, townhall_list):
            self.x, self.y = old_x, old_y
        
        # Check collision with other humans
        if other_humans:
            for other in other_humans:
                if other != self and self.check_human_collision(other):
                    self.x, self.y = old_x, old_y
                    break
    
    def _check_structure_collisions(self, pen_list, townhall_list):
        """Check if human collides with any structure"""
        for pen in pen_list:
            if pen.check_collision_player(self.x, self.y):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_player(self.x, self.y):
                return True
        return False
    
    def check_human_collision(self, other_human):
        """Simple distance-based collision with another human"""
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        other_center_x = other_human.x + other_human.size / 2
        other_center_y = other_human.y + other_human.size / 2
        
        dist = distance(center_x, center_y, other_center_x, other_center_y)
        return dist < HUMAN_COLLISION_RADIUS
    
    def contains_point(self, px, py):
        """Check if a point is inside the human"""
        return self.x <= px <= self.x + self.size and self.y <= py <= self.y + self.size
