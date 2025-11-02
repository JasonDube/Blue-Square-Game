"""
Build mode UI component
"""
import pygame
from constants import *
from entities.pen import Pen
from entities.townhall import TownHall
from entities.lumberyard import LumberYard
from entities.stoneyard import StoneYard
from entities.ironyard import IronYard
from entities.hut import Hut


class BuildModeRenderer:
    """Handles build mode preview and UI"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
    
    def draw(self, screen, game_state):
        """Draw build mode preview and instructions"""
        if not game_state.build_mode:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Check if placement is valid
        is_valid = self._check_placement_valid(mouse_x, mouse_y, game_state)
        
        # Draw preview with appropriate color
        if game_state.build_mode_type == "pen":
            self._draw_pen_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "townhall":
            self._draw_townhall_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "lumberyard":
            self._draw_lumberyard_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "stoneyard":
            self._draw_stoneyard_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "ironyard":
            self._draw_ironyard_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "hut":
            self._draw_hut_preview(screen, mouse_x, mouse_y, is_valid)
        
        # Draw instructions
        self._draw_instructions(screen, game_state.build_mode_type, game_state.pen_rotation, is_valid)
    
    def _check_placement_valid(self, mouse_x, mouse_y, game_state):
        """Check if building can be placed at this location"""
        build_type = game_state.build_mode_type
        
        # Get building dimensions
        if build_type == "pen":
            width = height = PEN_SIZE
            preview_x = mouse_x - PEN_SIZE // 2
            preview_y = mouse_y - PEN_SIZE // 2
        elif build_type == "townhall":
            width = TOWNHALL_WIDTH
            height = TOWNHALL_HEIGHT
            preview_x = mouse_x - TOWNHALL_WIDTH // 2
            preview_y = mouse_y - TOWNHALL_HEIGHT // 2
        elif build_type == "lumberyard":
            width = LUMBERYARD_WIDTH
            height = LUMBERYARD_HEIGHT
            preview_x = mouse_x - LUMBERYARD_WIDTH // 2
            preview_y = mouse_y - LUMBERYARD_HEIGHT // 2
        elif build_type == "stoneyard":
            width = STONEYARD_WIDTH
            height = STONEYARD_HEIGHT
            preview_x = mouse_x - STONEYARD_WIDTH // 2
            preview_y = mouse_y - STONEYARD_HEIGHT // 2
        elif build_type == "ironyard":
            width = IRONYARD_WIDTH
            height = IRONYARD_HEIGHT
            preview_x = mouse_x - IRONYARD_WIDTH // 2
            preview_y = mouse_y - IRONYARD_HEIGHT // 2
        elif build_type == "hut":
            width = HUT_SIZE
            height = HUT_SIZE
            preview_x = mouse_x - HUT_SIZE // 2
            preview_y = mouse_y - HUT_SIZE // 2
        else:
            return True
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - height))
        
        # Create rect for the building
        building_rect = pygame.Rect(preview_x, preview_y, width, height)
        
        # Check collision with trees
        for tree in game_state.tree_list:
            if not tree.is_depleted():
                tree_bounds = tree.get_bounds()
                if building_rect.colliderect(tree_bounds):
                    return False
        
        # Check collision with rocks
        for rock in game_state.rock_list:
            if not rock.is_depleted():
                rock_bounds = rock.get_bounds()
                if building_rect.colliderect(rock_bounds):
                    return False
        
        # Check collision with iron mines
        for iron_mine in game_state.iron_mine_list:
            if not iron_mine.is_depleted():
                mine_bounds = iron_mine.get_bounds()
                if building_rect.colliderect(mine_bounds):
                    return False
        
        # Check collision with existing pens
        for pen in game_state.pen_list:
            pen_rect = pygame.Rect(pen.x, pen.y, pen.size, pen.size)
            if building_rect.colliderect(pen_rect):
                return False
        
        # Check collision with town halls
        for townhall in game_state.townhall_list:
            townhall_rect = pygame.Rect(townhall.x, townhall.y, townhall.width, townhall.height)
            if building_rect.colliderect(townhall_rect):
                return False
        
        # Check collision with lumber yards
        for lumber_yard in game_state.lumber_yard_list:
            lumber_rect = pygame.Rect(lumber_yard.x, lumber_yard.y, lumber_yard.width, lumber_yard.height)
            if building_rect.colliderect(lumber_rect):
                return False
        
        # Check collision with stone yards
        for stone_yard in game_state.stone_yard_list:
            stone_rect = pygame.Rect(stone_yard.x, stone_yard.y, stone_yard.width, stone_yard.height)
            if building_rect.colliderect(stone_rect):
                return False
        
        # Check collision with iron yards
        for iron_yard in game_state.iron_yard_list:
            iron_rect = pygame.Rect(iron_yard.x, iron_yard.y, iron_yard.width, iron_yard.height)
            if building_rect.colliderect(iron_rect):
                return False
        
        # Check collision with huts (circular, but check bounding box)
        for hut in game_state.hut_list:
            hut_rect = pygame.Rect(hut.x, hut.y, hut.size, hut.size)
            if building_rect.colliderect(hut_rect):
                return False
        
        return True
    
    def _draw_pen_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of pen placement"""
        preview_x = mouse_x - PEN_SIZE // 2
        preview_y = mouse_y - PEN_SIZE // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - PEN_SIZE))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - PEN_SIZE))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw preview with appropriate color
        pygame.draw.line(screen, color, (preview_x, preview_y), (preview_x + PEN_SIZE, preview_y), 2)
        pygame.draw.line(screen, color, (preview_x + PEN_SIZE, preview_y), (preview_x + PEN_SIZE, preview_y + PEN_SIZE), 2)
        pygame.draw.line(screen, color, (preview_x + PEN_SIZE, preview_y + PEN_SIZE), (preview_x, preview_y + PEN_SIZE), 2)
        pygame.draw.line(screen, color, (preview_x, preview_y + PEN_SIZE), (preview_x, preview_y), 2)
        
        # Draw button position indicator
        preview_pen = Pen(preview_x, preview_y, PEN_SIZE, rotation)
        button_x, button_y = preview_pen.get_button_pos()
        pygame.draw.circle(screen, color, (button_x, button_y), 5)
    
    def _draw_townhall_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of town hall placement"""
        preview_x = mouse_x - TOWNHALL_WIDTH // 2
        preview_y = mouse_y - TOWNHALL_HEIGHT // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - TOWNHALL_WIDTH))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - TOWNHALL_HEIGHT))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (preview_x, preview_y, TOWNHALL_WIDTH, TOWNHALL_HEIGHT))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, TOWNHALL_WIDTH, TOWNHALL_HEIGHT), 2)
        
        # Draw button position indicator
        preview_townhall = TownHall(preview_x, preview_y, rotation)
        button_x, button_y = preview_townhall.get_button_pos()
        pygame.draw.circle(screen, color, (button_x, button_y), 5)
    
    def _draw_lumberyard_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of lumber yard placement"""
        preview_x = mouse_x - LUMBERYARD_WIDTH // 2
        preview_y = mouse_y - LUMBERYARD_HEIGHT // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - LUMBERYARD_WIDTH))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - LUMBERYARD_HEIGHT))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (preview_x, preview_y, LUMBERYARD_WIDTH, LUMBERYARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, LUMBERYARD_WIDTH, LUMBERYARD_HEIGHT), 2)
        
        # Draw button position indicator
        preview_lumberyard = LumberYard(preview_x, preview_y, rotation)
        button_x, button_y = preview_lumberyard.get_button_pos()
        pygame.draw.circle(screen, color, (button_x, button_y), 5)
    
    def _draw_stoneyard_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of stone yard placement"""
        preview_x = mouse_x - STONEYARD_WIDTH // 2
        preview_y = mouse_y - STONEYARD_HEIGHT // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - STONEYARD_WIDTH))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - STONEYARD_HEIGHT))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (preview_x, preview_y, STONEYARD_WIDTH, STONEYARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, STONEYARD_WIDTH, STONEYARD_HEIGHT), 2)
        
        # Draw button position indicator
        preview_stoneyard = StoneYard(preview_x, preview_y, rotation)
        button_x, button_y = preview_stoneyard.get_button_pos()
        pygame.draw.circle(screen, color, (button_x, button_y), 5)
    
    def _draw_hut_preview(self, screen, mouse_x, mouse_y, is_valid):
        """Draw hut preview"""
        preview_color = GREEN if is_valid else RED
        
        # Clamp position to playable area
        preview_x = mouse_x - HUT_SIZE // 2
        preview_y = mouse_y - HUT_SIZE // 2
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - HUT_SIZE))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - HUT_SIZE))
        
        # Draw circle preview
        center_x = int(preview_x + HUT_SIZE // 2)
        center_y = int(preview_y + HUT_SIZE // 2)
        radius = HUT_SIZE // 2
        
        # Draw filled circle with transparency
        preview_surface = pygame.Surface((HUT_SIZE, HUT_SIZE), pygame.SRCALPHA)
        preview_color_alpha = (*preview_color, 128) if is_valid else (*RED, 128)
        pygame.draw.circle(preview_surface, preview_color_alpha, (radius, radius), radius)
        screen.blit(preview_surface, (preview_x, preview_y))
        
        # Draw border
        border_color = GREEN if is_valid else RED
        pygame.draw.circle(screen, border_color, (center_x, center_y), radius, 2)
    
    def _draw_ironyard_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of iron yard placement"""
        preview_x = mouse_x - IRONYARD_WIDTH // 2
        preview_y = mouse_y - IRONYARD_HEIGHT // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - IRONYARD_WIDTH))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - IRONYARD_HEIGHT))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle
        pygame.draw.rect(screen, color, (preview_x, preview_y, IRONYARD_WIDTH, IRONYARD_HEIGHT))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, IRONYARD_WIDTH, IRONYARD_HEIGHT), 2)
        
        # Draw button position indicator
        preview_ironyard = IronYard(preview_x, preview_y, rotation)
        button_x, button_y = preview_ironyard.get_button_pos()
        pygame.draw.circle(screen, color, (button_x, button_y), 5)
    
    def _draw_instructions(self, screen, build_type, rotation, is_valid):
        """Draw build mode instructions at bottom of screen"""
        rotation_names = ["Top", "Right", "Bottom", "Left"]
        build_type_names = {
            "pen": "Pen",
            "townhall": "Town Hall",
            "lumberyard": "Lumber Yard",
            "stoneyard": "Stone Yard",
            "ironyard": "Iron Yard",
            "hut": "Hut"
        }
        build_type_name = build_type_names.get(build_type, "Structure")
        
        # Show validity status
        status = "Valid" if is_valid else "INVALID - Clear space required!"
        status_color = GREEN if is_valid else RED
        
        text = f"Build Mode: {build_type_name} (Rotation: {rotation_names[rotation]}) - {status}"
        text_surface = self.font.render(text, True, status_color)
        # Position above bottom HUD
        screen.blit(text_surface, (10, PLAYABLE_AREA_BOTTOM - 45))
        
        hint = "Q/E or Mouse Wheel to rotate - ESC to cancel"
        hint_surface = self.font.render(hint, True, WHITE)
        screen.blit(hint_surface, (10, PLAYABLE_AREA_BOTTOM - 25))
