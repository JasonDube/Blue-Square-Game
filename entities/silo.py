"""
Silo entity - building for storing barley
"""
import pygame
from constants import *


class Silo:
    """Silo building for storing harvested barley"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.collision_enabled = True
        self.resource_type = ResourceType.BARLEY
        self.resource_visualizer = ResourceVisualizer(self, self.resource_type, 3, 3)
        self.barley_positions = None  # To be calculated once
        self.barley_count = 0  # Per-building resource tracking (starts at 0!)
    
    def is_point_inside(self, px, py):
        """Check if a point is inside the silo boundaries"""
        center_x = self.x + self.radius
        center_y = self.y + self.radius
        dist_squared = (px - center_x)**2 + (py - center_y)**2
        return dist_squared <= self.radius**2
    
    def check_collision_player(self, px, py):
        """Check if player collides with the silo"""
        if not self.collision_enabled:
            return False
        
        player_center_x = px + PLAYER_SIZE / 2
        player_center_y = py + PLAYER_SIZE / 2
        silo_center_x = self.x + self.radius
        silo_center_y = self.y + self.radius
        
        dist = ((player_center_x - silo_center_x)**2 + 
                (player_center_y - silo_center_y)**2)**0.5
        
        return dist < (self.radius + PLAYER_SIZE / 2)
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the silo"""
        if not self.collision_enabled:
            return False
        
        sheep_center_x = sx + sw / 2
        sheep_center_y = sy + sh / 2
        silo_center_x = self.x + self.radius
        silo_center_y = self.y + self.radius
        
        dist = ((sheep_center_x - silo_center_x)**2 + 
                (sheep_center_y - silo_center_y)**2)**0.5
        
        return dist < (self.radius + max(sw, sh) / 2)
    
    def can_accept_resource(self):
        """Check if silo can accept more barley - unlimited capacity"""
        return True  # No capacity limit
    
    def add_barley(self):
        """Add barley to storage - unlimited capacity"""
        self.barley_count += 1
        return True
    
    def draw(self, screen, preview=False):
        """Draw the silo"""
        center_x = self.x + self.radius
        center_y = self.y + self.radius
        
        # Draw red circle
        color = RED if not preview else GRAY
        pygame.draw.circle(screen, color, (center_x, center_y), self.radius)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), self.radius, 2)
        
        # Draw stored barley if not preview
        if not preview:
            self._draw_stored_barley(screen)
    
    def _draw_stored_barley(self, screen):
        """Draw visual representation of stored barley within circular silo boundaries"""
        from constants import DARK_BROWN
        import math
        
        center_x = self.x + self.radius
        center_y = self.y + self.radius
        barley_size = 3
        spacing = 4  # Spacing between barley squares (1 pixel gap)
        max_radius = self.radius - 3  # Leave small margin from edge
        
        # Pre-calculate all valid positions in a grid pattern
        # This ensures no overlaps and predictable placement
        valid_positions = []
        
        # Start from top-left and scan in a grid
        start_x = center_x - max_radius
        start_y = center_y - max_radius
        
        # Calculate grid dimensions
        grid_width = int(max_radius * 2 // spacing) + 1
        grid_height = int(max_radius * 2 // spacing) + 1
        
        for row in range(grid_height):
            for col in range(grid_width):
                # Calculate position for this grid cell
                x = start_x + col * spacing
                y = start_y + row * spacing
                
                # Check if the entire 3x3 square fits within the circle
                # We need to check all four corners of the square
                corners = [
                    (x, y),  # Top-left
                    (x + barley_size, y),  # Top-right
                    (x, y + barley_size),  # Bottom-left
                    (x + barley_size, y + barley_size)  # Bottom-right
                ]
                
                all_within = True
                for corner_x, corner_y in corners:
                    dist_from_center = math.sqrt((corner_x - center_x)**2 + (corner_y - center_y)**2)
                    # All corners must be within max_radius
                    if dist_from_center > max_radius:
                        all_within = False
                        break
                
                if all_within:
                    # Center the square in the grid cell for better visual spacing
                    centered_x = x
                    centered_y = y
                    valid_positions.append((centered_x, centered_y))
        
        # Sort positions by distance from center (closest first) for more natural filling
        valid_positions.sort(key=lambda pos: math.sqrt((pos[0] + barley_size/2 - center_x)**2 + 
                                                       (pos[1] + barley_size/2 - center_y)**2))
        
        # Draw only the number of barley units we have
        drawn_count = min(self.barley_count, len(valid_positions))
        for i in range(drawn_count):
            x, y = valid_positions[i]
            pygame.draw.rect(screen, DARK_BROWN, (x, y, barley_size, barley_size))

