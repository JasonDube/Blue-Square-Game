"""
Tree entity - harvestable resource
"""
import pygame
from constants import *


class Tree:
    """Harvestable tree with trunk and crown"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.trunk_width = TREE_TRUNK_WIDTH
        self.trunk_height = TREE_TRUNK_HEIGHT
        self.crown_radius = TREE_CROWN_RADIUS
        self.health = TREE_INITIAL_HEALTH  # 20 logs per tree
        self.being_harvested = False
        self.selected = False  # Selection state
    
    def draw(self, screen, show_health=False):
        """Draw the tree with trunk and crown"""
        from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM
        
        if self.health <= 0:
            return  # Don't draw depleted trees
        
        # Check if tree is within playable area bounds
        tree_top = self.y - self.trunk_height - self.crown_radius
        tree_bottom = self.y
        
        # Only draw if tree is within playable area (not in HUD areas)
        if tree_top < PLAYABLE_AREA_TOP or tree_bottom > PLAYABLE_AREA_BOTTOM:
            return  # Tree is in HUD area, don't draw
        
        # Draw trunk (brown rectangle)
        trunk_rect = pygame.Rect(
            self.x - self.trunk_width // 2, 
            self.y - self.trunk_height, 
            self.trunk_width, 
            self.trunk_height
        )
        pygame.draw.rect(screen, BROWN, trunk_rect)
        
        # Draw crown (dark green circle on top)
        crown_y = self.y - self.trunk_height
        pygame.draw.circle(screen, DARK_GREEN, (self.x, crown_y), self.crown_radius)
        
        # Draw selection indicator if selected
        if self.selected:
            # Draw yellow outline around tree
            pygame.draw.circle(screen, YELLOW, (self.x, crown_y), self.crown_radius + 2, 2)
            pygame.draw.rect(screen, YELLOW, trunk_rect.inflate(4, 4), 2)
        
        # Draw health number if in harvest mode (only if within bounds)
        if show_health:
            health_text_y = crown_y - self.crown_radius - 10
            if health_text_y >= PLAYABLE_AREA_TOP:
                font = pygame.font.Font(None, 20)
                health_text = f"{int(self.health)}"
                text_surface = font.render(health_text, True, WHITE)
                text_rect = text_surface.get_rect(center=(self.x, health_text_y))
                # Draw black background for readability
                bg_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(screen, BLACK, bg_rect)
                screen.blit(text_surface, text_rect)
    
    def get_bounds(self):
        """Get bounding box for collision detection"""
        return pygame.Rect(
            self.x - self.crown_radius, 
            self.y - self.trunk_height - self.crown_radius, 
            self.crown_radius * 2, 
            self.trunk_height + self.crown_radius * 2
        )
    
    def is_depleted(self):
        """Check if tree is fully harvested"""
        return self.health <= 0
    
    def harvest(self):
        """Remove health from tree and return success"""
        if self.health > 0:
            self.health -= TREE_HEALTH_PER_HARVEST
            return True
        return False
    
    def contains_point(self, px, py):
        """Check if point is within tree bounds"""
        bounds = self.get_bounds()
        return bounds.collidepoint(px, py)
