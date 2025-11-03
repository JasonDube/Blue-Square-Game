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
from entities.saltyard import SaltYard
from entities.hut import Hut
from entities.woolshed import WoolShed
from entities.barleyfarm import BarleyFarm
from entities.silo import Silo
from entities.mill import Mill


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
        elif game_state.build_mode_type == "saltyard":
            self._draw_saltyard_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "hut":
            self._draw_hut_preview(screen, mouse_x, mouse_y, is_valid)
        elif game_state.build_mode_type == "woolshed":
            self._draw_woolshed_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "barleyfarm":
            self._draw_barleyfarm_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        elif game_state.build_mode_type == "silo":
            self._draw_silo_preview(screen, mouse_x, mouse_y, is_valid)
        elif game_state.build_mode_type == "mill":
            self._draw_mill_preview(screen, mouse_x, mouse_y, game_state.pen_rotation, is_valid)
        
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
            # Account for rotation - swap dimensions for 90/270 degree rotations
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = TOWNHALL_HEIGHT
                height = TOWNHALL_WIDTH
            else:
                width = TOWNHALL_WIDTH
                height = TOWNHALL_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "lumberyard":
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = LUMBERYARD_HEIGHT
                height = LUMBERYARD_WIDTH
            else:
                width = LUMBERYARD_WIDTH
                height = LUMBERYARD_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "stoneyard":
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = STONEYARD_HEIGHT
                height = STONEYARD_WIDTH
            else:
                width = STONEYARD_WIDTH
                height = STONEYARD_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "ironyard":
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = IRONYARD_HEIGHT
                height = IRONYARD_WIDTH
            else:
                width = IRONYARD_WIDTH
                height = IRONYARD_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "saltyard":
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = SALTYARD_HEIGHT
                height = SALTYARD_WIDTH
            else:
                width = SALTYARD_WIDTH
                height = SALTYARD_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "hut":
            width = HUT_SIZE
            height = HUT_SIZE
            preview_x = mouse_x - HUT_SIZE // 2
            preview_y = mouse_y - HUT_SIZE // 2
        elif build_type == "woolshed":
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = WOOLSHED_HEIGHT
                height = WOOLSHED_WIDTH
            else:
                width = WOOLSHED_WIDTH
                height = WOOLSHED_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "barleyfarm":
            rotation = game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                width = BARLEYFARM_HEIGHT
                height = BARLEYFARM_WIDTH
            else:
                width = BARLEYFARM_WIDTH
                height = BARLEYFARM_HEIGHT
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "mill":
            rotation = game_state.pen_rotation
            if rotation == 0 or rotation == 2:
                width = MILL_WIDTH + 100  # Include outbuildings (50 on each side)
                height = MILL_HEIGHT
            else:
                width = MILL_WIDTH
                height = MILL_HEIGHT + 100  # Include outbuildings (50 on top/bottom)
            preview_x = mouse_x - width // 2
            preview_y = mouse_y - height // 2
        elif build_type == "silo":
            width = SILO_RADIUS * 2
            height = SILO_RADIUS * 2
            preview_x = mouse_x - SILO_RADIUS
            preview_y = mouse_y - SILO_RADIUS
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
        
        # Check collision with salt yards
        for salt_yard in game_state.salt_yard_list:
            salt_rect = pygame.Rect(salt_yard.x, salt_yard.y, salt_yard.width, salt_yard.height)
            if building_rect.colliderect(salt_rect):
                return False
        
        # Check collision with huts (circular, but check bounding box)
        for hut in game_state.hut_list:
            hut_rect = pygame.Rect(hut.x, hut.y, hut.size, hut.size)
            if building_rect.colliderect(hut_rect):
                return False
        
        # Check collision with wool sheds
        for wool_shed in game_state.wool_shed_list:
            wool_rect = pygame.Rect(wool_shed.x, wool_shed.y, wool_shed.width, wool_shed.height)
            if building_rect.colliderect(wool_rect):
                return False
        
        # Check collision with barley farms
        for barley_farm in game_state.barley_farm_list:
            farm_rect = pygame.Rect(barley_farm.x, barley_farm.y, barley_farm.width, barley_farm.height)
            if building_rect.colliderect(farm_rect):
                return False
        
        # Check collision with silos (circular, but check bounding box)
        for silo in game_state.silo_list:
            silo_rect = pygame.Rect(silo.x, silo.y, silo.radius * 2, silo.radius * 2)
            if building_rect.colliderect(silo_rect):
                return False
        
        # Check collision with mills (including outbuildings)
        for mill in game_state.mill_list:
            mill_rect = pygame.Rect(mill.x, mill.y, mill.width, mill.height)
            if building_rect.colliderect(mill_rect):
                return False
            # Check outbuildings
            outbuilding_size = 50
            flour_rect = pygame.Rect(mill.flour_outbuilding_x, mill.flour_outbuilding_y, 
                                     outbuilding_size, outbuilding_size)
            malt_rect = pygame.Rect(mill.malt_outbuilding_x, mill.malt_outbuilding_y, 
                                   outbuilding_size, outbuilding_size)
            if building_rect.colliderect(flour_rect) or building_rect.colliderect(malt_rect):
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
    
    def _draw_townhall_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of town hall placement"""
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = TOWNHALL_HEIGHT
            draw_height = TOWNHALL_WIDTH
        else:
            draw_width = TOWNHALL_WIDTH
            draw_height = TOWNHALL_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, draw_width, draw_height), 2)
    
    def _draw_lumberyard_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of lumber yard placement"""
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = LUMBERYARD_HEIGHT
            draw_height = LUMBERYARD_WIDTH
        else:
            draw_width = LUMBERYARD_WIDTH
            draw_height = LUMBERYARD_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, draw_width, draw_height), 2)
    
    def _draw_stoneyard_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of stone yard placement"""
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = STONEYARD_HEIGHT
            draw_height = STONEYARD_WIDTH
        else:
            draw_width = STONEYARD_WIDTH
            draw_height = STONEYARD_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, draw_width, draw_height), 2)
    
    def _draw_saltyard_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of salt yard placement"""
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = SALTYARD_HEIGHT
            draw_height = SALTYARD_WIDTH
        else:
            draw_width = SALTYARD_WIDTH
            draw_height = SALTYARD_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity
        color = WHITE if is_valid else RED
        
        # Draw filled white rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, draw_width, draw_height), 2)
    
    def _draw_hut_preview(self, screen, mouse_x, mouse_y, is_valid):
        """Draw hut preview"""
        preview_color = WHITE if is_valid else RED
        
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
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = IRONYARD_HEIGHT
            draw_height = IRONYARD_WIDTH
        else:
            draw_width = IRONYARD_WIDTH
            draw_height = IRONYARD_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity
        color = GRAY if is_valid else RED
        
        # Draw filled rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, draw_width, draw_height), 2)
    
    def _draw_woolshed_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of wool shed placement"""
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = WOOLSHED_HEIGHT
            draw_height = WOOLSHED_WIDTH
        else:
            draw_width = WOOLSHED_WIDTH
            draw_height = WOOLSHED_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity
        DARK_GREY = (64, 64, 64)
        color = DARK_GREY if is_valid else RED
        
        # Draw filled rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, draw_width, draw_height), 2)
    
    def _draw_barleyfarm_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of barley farm placement"""
        # For rotations 1 and 3 (90 and 270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            draw_width = BARLEYFARM_HEIGHT
            draw_height = BARLEYFARM_WIDTH
        else:
            draw_width = BARLEYFARM_WIDTH
            draw_height = BARLEYFARM_HEIGHT
        
        preview_x = mouse_x - draw_width // 2
        preview_y = mouse_y - draw_height // 2
        
        # Keep within playable area bounds
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - draw_width))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - draw_height))
        
        # Choose color based on validity (unfilled rectangle)
        color = GRAY if is_valid else RED
        
        # Draw unfilled rectangle with rotated dimensions
        pygame.draw.rect(screen, color, (preview_x, preview_y, draw_width, draw_height), 1)
    
    def _draw_silo_preview(self, screen, mouse_x, mouse_y, is_valid):
        """Draw preview of silo placement"""
        from constants import SILO_RADIUS
        preview_color = GRAY if is_valid else RED
        
        # Clamp position to playable area
        preview_x = mouse_x - SILO_RADIUS
        preview_y = mouse_y - SILO_RADIUS
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - SILO_RADIUS * 2))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - SILO_RADIUS * 2))
        
        # Draw circle preview
        center_x = int(preview_x + SILO_RADIUS)
        center_y = int(preview_y + SILO_RADIUS)
        
        # Draw filled circle
        pygame.draw.circle(screen, preview_color, (center_x, center_y), SILO_RADIUS)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), SILO_RADIUS, 2)
    
    def _draw_mill_preview(self, screen, mouse_x, mouse_y, rotation, is_valid):
        """Draw preview of mill placement with outbuildings (supports rotation)"""
        from constants import MILL_WIDTH, MILL_HEIGHT, WOOD_BROWN
        color = GRAY if is_valid else RED
        wood_color = WOOD_BROWN if is_valid else RED
        preview_x = mouse_x - MILL_WIDTH / 2
        preview_y = mouse_y - MILL_HEIGHT / 2
        
        # Clamp position to playable area
        preview_x = max(0, min(preview_x, SCREEN_WIDTH - MILL_WIDTH))
        preview_y = max(PLAYABLE_AREA_TOP, min(preview_y, PLAYABLE_AREA_BOTTOM - MILL_HEIGHT))
        
        outbuilding_size = 50
        
        # Calculate outbuilding positions based on rotation
        if rotation == 0 or rotation == 2:
            # Horizontal: flour left, malt right (or reversed for rotation 2)
            if rotation == 0:
                flour_x = preview_x - outbuilding_size
                malt_x = preview_x + MILL_WIDTH
            else:
                flour_x = preview_x + MILL_WIDTH
                malt_x = preview_x - outbuilding_size
            flour_y = preview_y + (MILL_HEIGHT - outbuilding_size) / 2
            malt_y = preview_y + (MILL_HEIGHT - outbuilding_size) / 2
        else:  # rotation == 1 or 3
            # Vertical: flour top, malt bottom (or reversed for rotation 3)
            if rotation == 1:
                flour_y = preview_y - outbuilding_size
                malt_y = preview_y + MILL_HEIGHT
            else:
                flour_y = preview_y + MILL_HEIGHT
                malt_y = preview_y - outbuilding_size
            flour_x = preview_x + (MILL_WIDTH - outbuilding_size) / 2
            malt_x = preview_x + (MILL_WIDTH - outbuilding_size) / 2
        
        # Draw outbuildings preview
        pygame.draw.rect(screen, wood_color, (flour_x, flour_y, outbuilding_size, outbuilding_size))
        pygame.draw.rect(screen, BLACK, (flour_x, flour_y, outbuilding_size, outbuilding_size), 2)
        
        pygame.draw.rect(screen, wood_color, (malt_x, malt_y, outbuilding_size, outbuilding_size))
        pygame.draw.rect(screen, BLACK, (malt_x, malt_y, outbuilding_size, outbuilding_size), 2)
        
        # Draw main mill building
        pygame.draw.rect(screen, color, (preview_x, preview_y, MILL_WIDTH, MILL_HEIGHT))
        pygame.draw.rect(screen, BLACK, (preview_x, preview_y, MILL_WIDTH, MILL_HEIGHT), 2)
    
    def _draw_instructions(self, screen, build_type, rotation, is_valid):
        """Draw build mode instructions at bottom of screen"""
        rotation_names = ["Top", "Right", "Bottom", "Left"]
        build_type_names = {
            "pen": "Pen",
            "townhall": "Town Hall",
            "lumberyard": "Lumber Yard",
            "stoneyard": "Stone Yard",
            "ironyard": "Iron Yard",
            "saltyard": "Salt Yard",
            "woolshed": "Wool Shed",
            "barleyfarm": "Barley Farm",
            "silo": "Silo",
            "mill": "Mill",
            "hut": "Hut"
        }
        build_type_name = build_type_names.get(build_type, "Structure")
        
        # Show validity status
        status = "Valid" if is_valid else "INVALID - Clear space required!"
        status_color = GREEN if is_valid else RED
        
        # Mill supports rotation but doesn't change shape
        if build_type == "mill":
            text = f"Build Mode: {build_type_name} (Rotation: {rotation_names[rotation]}) - {status}"
        else:
            text = f"Build Mode: {build_type_name} (Rotation: {rotation_names[rotation]}) - {status}"
        text_surface = self.font.render(text, True, status_color)
        # Position above bottom HUD
        screen.blit(text_surface, (10, PLAYABLE_AREA_BOTTOM - 45))
        
        hint = "Q/E or Mouse Wheel to rotate - ESC to cancel"
        hint_surface = self.font.render(hint, True, WHITE)
        screen.blit(hint_surface, (10, PLAYABLE_AREA_BOTTOM - 25))
