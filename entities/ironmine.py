"""
IronMine entity - harvestable iron resource
"""
import pygame
from constants import *


class IronMine:
    """Harvestable iron mine with health"""
    
    def __init__(self, x, y, health=None):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.health = health if health is not None else IRONMINE_INITIAL_HEALTH  # 500 iron per mine
        self.being_harvested = False
    
    def draw(self, screen, show_health=False):
        """Draw the iron mine"""
        if self.health <= 0:
            return  # Don't draw depleted mines
        
        # Draw dark gray mine structure
        pygame.draw.rect(screen, (80, 80, 80), (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        # Draw border
        pygame.draw.rect(screen, GRAY, (self.x - self.width//2, self.y - self.height//2, self.width, self.height), 2)
        
        # Draw some details (ore)
        pygame.draw.circle(screen, (200, 100, 50), (self.x - 5, self.y - 5), 3)
        pygame.draw.circle(screen, (200, 100, 50), (self.x + 5, self.y + 5), 3)
        
        # Draw health if requested
        if show_health:
            font = pygame.font.Font(None, 16)
            health_text = f"{int(self.health)}"
            text_surface = font.render(health_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.x, self.y - self.height//2 - 10))
            # Draw black background
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, BLACK, bg_rect)
            screen.blit(text_surface, text_rect)
    
    def get_bounds(self):
        """Get bounding box for collision detection"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def is_depleted(self):
        """Check if mine is fully harvested"""
        return self.health <= 0
    
    def harvest(self):
        """Remove health from mine and return success"""
        if self.health > 0:
            self.health -= IRONMINE_HEALTH_PER_HARVEST
            return True
        return False
    
    def contains_point(self, px, py):
        """Check if point is within mine bounds"""
        bounds = self.get_bounds()
        return bounds.collidepoint(px, py)
