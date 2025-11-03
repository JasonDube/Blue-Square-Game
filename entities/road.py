"""
Road entity - 30x60 road segment with stones packed in
"""
import pygame
from constants import *


class Road:
    """Road segment - 30x60 filled light grey rectangle with stones"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation  # 0 = horizontal (wide), 1 = vertical (tall)
        # For rotation 0: width=60, height=30 (horizontal)
        # For rotation 1: width=30, height=60 (vertical)
        if rotation == 0:
            self.width = 60
            self.height = 30
        else:
            self.width = 30
            self.height = 60
        self.collision_enabled = False
    
    def draw(self, screen, preview=False):
        """Draw the road segment"""
        # Draw light grey filled rectangle
        road_color = LIGHT_GREY
        pygame.draw.rect(screen, road_color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 1)
        
        if not preview:
            # Draw stones packed in the road
            self._draw_stones(screen)
    
    def _draw_stones(self, screen):
        """Draw stones packed in the road"""
        # Stone size from resource system (8x8 circle, radius 4)
        stone_radius = 4
        stone_color = GRAY
        
        # Calculate spacing for stones
        margin = 4  # Margin from edges
        stone_area_x = self.x + margin
        stone_area_y = self.y + margin
        stone_area_width = self.width - (margin * 2)
        stone_area_height = self.height - (margin * 2)
        
        # Calculate grid layout
        stones_per_row = max(1, int(stone_area_width / (stone_radius * 2 + 2)))
        stones_per_col = max(1, int(stone_area_height / (stone_radius * 2 + 2)))
        
        # Spacing between stones
        if stones_per_row > 1:
            spacing_x = (stone_area_width - stones_per_row * stone_radius * 2) / (stones_per_row - 1)
        else:
            spacing_x = 0
        
        if stones_per_col > 1:
            spacing_y = (stone_area_height - stones_per_col * stone_radius * 2) / (stones_per_col - 1)
        else:
            spacing_y = 0
        
        # Draw stones in a grid pattern
        for row in range(stones_per_col):
            for col in range(stones_per_row):
                stone_x = stone_area_x + col * (stone_radius * 2 + spacing_x) + stone_radius
                stone_y = stone_area_y + row * (stone_radius * 2 + spacing_y) + stone_radius
                
                # Draw stone as circle
                pygame.draw.circle(screen, stone_color, (int(stone_x), int(stone_y)), stone_radius)
    
    def get_bounds(self):
        """Get bounding box for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, px, py):
        """Check if point is within road bounds"""
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)

