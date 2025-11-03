"""
Salt entity - harvestable salt resource
"""
import pygame
from constants import *


class Salt:
    """Harvestable salt deposit with health"""
    
    def __init__(self, x, y, health=None):
        self.x = x
        self.y = y
        self.size = 10
        self.health = health if health is not None else SALT_INITIAL_HEALTH
        self.being_harvested = False
        self.selected = False  # Selection state
    
    def draw(self, screen, show_health=False):
        """Draw the salt deposit"""
        if self.health <= 0:
            return  # Don't draw depleted salt
        
        # Draw white salt crystal
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)
        pygame.draw.circle(screen, (200, 200, 200), (self.x, self.y), self.size, 1)  # Light gray border
        
        # Draw selection indicator if selected
        if self.selected:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.size + 3, 2)
        
        # Draw health if requested
        if show_health:
            font = pygame.font.Font(None, 16)
            health_text = f"{int(self.health)}"
            text_surface = font.render(health_text, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.x, self.y - self.size - 5))
            # Draw white background
            bg_rect = text_rect.inflate(4, 2)
            pygame.draw.rect(screen, WHITE, bg_rect)
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
        """Check if salt deposit is fully harvested"""
        return self.health <= 0
    
    def harvest(self):
        """Remove health from salt deposit and return success"""
        if self.health > 0:
            self.health -= SALT_HEALTH_PER_HARVEST
            return True
        return False
    
    def contains_point(self, px, py):
        """Check if point is within salt bounds"""
        bounds = self.get_bounds()
        return bounds.collidepoint(px, py)

