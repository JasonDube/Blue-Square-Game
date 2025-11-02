"""
Rock entity - harvestable stone resource
"""
import pygame
from constants import *


class Rock:
    """Harvestable rock with health"""
    
    def __init__(self, x, y, health=None):
        self.x = x
        self.y = y
        self.size = 12
        self.health = health if health is not None else ROCK_INITIAL_HEALTH  # 100 stones per rock
        self.being_harvested = False
    
    def draw(self, screen, show_health=False):
        """Draw the rock"""
        if self.health <= 0:
            return  # Don't draw depleted rocks
        
        # Draw gray rock
        pygame.draw.circle(screen, GRAY, (self.x, self.y), self.size)
        
        # Draw health if requested
        if show_health:
            font = pygame.font.Font(None, 16)
            health_text = f"{int(self.health)}"
            text_surface = font.render(health_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.x, self.y - self.size - 5))
            # Draw black background
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, BLACK, bg_rect)
            screen.blit(text_surface, text_rect)
    
    def get_bounds(self):
        """Get bounding box for collision detection"""
        return pygame.Rect(
            self.x - self.size,
            self.y - self.size,
            self.size * 2,
            self.size * 2
        )
    
    def is_depleted(self):
        """Check if rock is fully harvested"""
        return self.health <= 0
    
    def harvest(self):
        """Remove health from rock and return success"""
        if self.health > 0:
            self.health -= ROCK_HEALTH_PER_HARVEST
            return True
        return False
    
    def contains_point(self, px, py):
        """Check if point is within rock bounds"""
        bounds = self.get_bounds()
        return bounds.collidepoint(px, py)
