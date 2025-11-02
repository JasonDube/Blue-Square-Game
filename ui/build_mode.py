"""
Build mode UI component
"""
import pygame
from constants import *
from entities.pen import Pen
from entities.townhall import TownHall
from entities.lumberyard import LumberYard


class BuildModeRenderer:
    """Handles build mode preview and UI"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
    
    def draw(self, screen, game_state):
        """Draw build mode preview and instructions"""
        if not game_state.build_mode:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Draw preview
        if game_state.build_mode_type == "pen":
            self._draw_pen_preview(screen, mouse_x, mouse_y, game_state.pen_rotation)
        elif game_state.build_mode_type == "townhall":
            self._draw_townhall_preview(screen, mouse_x, mouse_y, game_state.pen_rotation)
        elif game_state.build_mode_type == "lumberyard":
            self._draw_lumberyard_preview(screen, mouse_x, mouse_y, game_state.pen_rotation)
        
        # Draw instructions
        self._draw_instructions(screen, game_state.build_mode_type, game_state.pen_rotation)
    
    def _draw_pen_preview(self, screen, mouse_x, mouse_y, rotation):
        """Draw preview of pen placement"""
        preview_x = mouse_x - PEN_SIZE // 2
        preview_y = mouse_y - PEN_SIZE // 2
        
        # Keep within screen bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - PEN_SIZE))
        preview_y = max(0, min(preview_y, SCREEN_HEIGHT - PEN_SIZE))
        
        preview_pen = Pen(preview_x, preview_y, PEN_SIZE, rotation)
        preview_pen.draw(screen, preview=True)
    
    def _draw_townhall_preview(self, screen, mouse_x, mouse_y, rotation):
        """Draw preview of town hall placement"""
        preview_x = mouse_x - TOWNHALL_WIDTH // 2
        preview_y = mouse_y - TOWNHALL_HEIGHT // 2
        
        # Keep within screen bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - TOWNHALL_WIDTH))
        preview_y = max(0, min(preview_y, SCREEN_HEIGHT - TOWNHALL_HEIGHT))
        
        preview_townhall = TownHall(preview_x, preview_y, rotation)
        preview_townhall.draw(screen, preview=True)
    
    def _draw_lumberyard_preview(self, screen, mouse_x, mouse_y, rotation):
        """Draw preview of lumber yard placement"""
        preview_x = mouse_x - LUMBERYARD_WIDTH // 2
        preview_y = mouse_y - LUMBERYARD_HEIGHT // 2
        
        # Keep within screen bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - LUMBERYARD_WIDTH))
        preview_y = max(0, min(preview_y, SCREEN_HEIGHT - LUMBERYARD_HEIGHT))
        
        preview_lumberyard = LumberYard(preview_x, preview_y, rotation)
        preview_lumberyard.draw(screen, preview=True)
    
    def _draw_instructions(self, screen, build_type, rotation):
        """Draw build mode instructions at bottom of screen"""
        rotation_names = ["Top", "Right", "Bottom", "Left"]
        build_type_names = {
            "pen": "Pen",
            "townhall": "Town Hall",
            "lumberyard": "Lumber Yard"
        }
        build_type_name = build_type_names.get(build_type, "Structure")
        
        text = f"Build Mode: Click to place {build_type_name} (Rotation: {rotation_names[rotation]}) - Q/E or Mouse Wheel to rotate"
        text_surface = self.font.render(text, True, WHITE)
        screen.blit(text_surface, (10, SCREEN_HEIGHT - 30))
