"""
Input handling system
"""
import pygame
from constants import *
from entities.pen import Pen
from entities.townhall import TownHall
from entities.lumberyard import LumberYard
from entities.stoneyard import StoneYard
from entities.ironyard import IronYard


class InputSystem:
    """Handles all user input (keyboard and mouse)"""
    
    def __init__(self, game_state, harvest_system=None, employment_menu=None):
        self.game_state = game_state
        self.harvest_system = harvest_system
        self.employment_menu = employment_menu
    
    def handle_event(self, event):
        """Handle a single pygame event"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mousewheel(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
    
    def _handle_keydown(self, event):
        """Handle keyboard press"""
        if event.key == pygame.K_ESCAPE:
            self._handle_escape()
        elif event.key == pygame.K_d:
            self.game_state.debug_mode = not self.game_state.debug_mode
        elif self.game_state.build_mode:
            self._handle_build_mode_keys(event)
    
    def _handle_escape(self):
        """Handle escape key - exit build mode or signal quit"""
        if self.game_state.build_mode:
            self.game_state.build_mode = False
            return False  # Don't quit
        return True  # Signal to quit
    
    def _handle_build_mode_keys(self, event):
        """Handle rotation keys in build mode"""
        if event.key == pygame.K_q:
            self.game_state.pen_rotation = (self.game_state.pen_rotation - 1) % 4
        elif event.key == pygame.K_e:
            self.game_state.pen_rotation = (self.game_state.pen_rotation + 1) % 4
    
    def _handle_mousewheel(self, event):
        """Handle mouse wheel rotation"""
        if self.game_state.build_mode:
            if event.y > 0:
                self.game_state.pen_rotation = (self.game_state.pen_rotation + 1) % 4
            else:
                self.game_state.pen_rotation = (self.game_state.pen_rotation - 1) % 4
    
    def _handle_mouse_down(self, event):
        """Handle mouse button press"""
        mouse_x, mouse_y = event.pos
        
        if event.button == 1:  # Left click
            self._handle_left_click(mouse_x, mouse_y)
        elif event.button == 3:  # Right click
            self._handle_right_click(mouse_x, mouse_y)
    
    def _handle_left_click(self, mouse_x, mouse_y):
        """Handle left click actions"""
        # Check if in harvest cursor mode
        if self.harvest_system and self.harvest_system.harvest_cursor_active:
            self._handle_harvest_target_selection(mouse_x, mouse_y)
            return
        
        # Check employment menu first (if active)
        if self.employment_menu and self.employment_menu.handle_click(mouse_x, mouse_y, self.game_state):
            return
        
        # Check context menus
        if self._check_context_menus(mouse_x, mouse_y):
            return
        
        # Check player context menu
        if self._check_player_context_menu(mouse_x, mouse_y):
            return
        
        # Handle build mode placement
        if self.game_state.build_mode:
            self._place_structure(mouse_x, mouse_y)
        else:
            # Check for entity click first (single selection)
            if self._try_select_entity(mouse_x, mouse_y):
                return
            
            # Start box selection
            self.game_state.box_selecting = True
            self.game_state.box_start_x = mouse_x
            self.game_state.box_start_y = mouse_y
            self.game_state.box_end_x = mouse_x
            self.game_state.box_end_y = mouse_y
    
    def _check_placement_valid(self, preview_x, preview_y, width, height):
        """Check if building placement is valid"""
        building_rect = pygame.Rect(preview_x, preview_y, width, height)
        
        # Check collision with trees
        for tree in self.game_state.tree_list:
            if not tree.is_depleted():
                if building_rect.colliderect(tree.get_bounds()):
                    return False
        
        # Check collision with rocks
        for rock in self.game_state.rock_list:
            if not rock.is_depleted():
                if building_rect.colliderect(rock.get_bounds()):
                    return False
        
        # Check collision with iron mines
        for iron_mine in self.game_state.iron_mine_list:
            if not iron_mine.is_depleted():
                if building_rect.colliderect(iron_mine.get_bounds()):
                    return False
        
        # Check collision with salt deposits
        for salt in self.game_state.salt_list:
            if not salt.is_depleted():
                if building_rect.colliderect(salt.get_bounds()):
                    return False
        
        # Check collision with existing buildings
        for pen in self.game_state.pen_list:
            if building_rect.colliderect(pygame.Rect(pen.x, pen.y, pen.size, pen.size)):
                return False
        
        for townhall in self.game_state.townhall_list:
            if building_rect.colliderect(pygame.Rect(townhall.x, townhall.y, townhall.width, townhall.height)):
                return False
        
        for lumber_yard in self.game_state.lumber_yard_list:
            if building_rect.colliderect(pygame.Rect(lumber_yard.x, lumber_yard.y, lumber_yard.width, lumber_yard.height)):
                return False
        
        for stone_yard in self.game_state.stone_yard_list:
            if building_rect.colliderect(pygame.Rect(stone_yard.x, stone_yard.y, stone_yard.width, stone_yard.height)):
                return False
        
        for iron_yard in self.game_state.iron_yard_list:
            if building_rect.colliderect(pygame.Rect(iron_yard.x, iron_yard.y, iron_yard.width, iron_yard.height)):
                return False
        
        for salt_yard in self.game_state.salt_yard_list:
            if building_rect.colliderect(pygame.Rect(salt_yard.x, salt_yard.y, salt_yard.width, salt_yard.height)):
                return False
        
        for hut in self.game_state.hut_list:
            if building_rect.colliderect(pygame.Rect(hut.x, hut.y, hut.size, hut.size)):
                return False
        
        for wool_shed in self.game_state.wool_shed_list:
            if building_rect.colliderect(pygame.Rect(wool_shed.x, wool_shed.y, wool_shed.width, wool_shed.height)):
                return False
        
        for barley_farm in self.game_state.barley_farm_list:
            if building_rect.colliderect(pygame.Rect(barley_farm.x, barley_farm.y, barley_farm.width, barley_farm.height)):
                return False
        
        for silo in self.game_state.silo_list:
            silo_rect = pygame.Rect(silo.x, silo.y, silo.radius * 2, silo.radius * 2)
            if building_rect.colliderect(silo_rect):
                return False
        
        for mill in self.game_state.mill_list:
            # Check collision with main mill building
            if building_rect.colliderect(pygame.Rect(mill.x, mill.y, mill.width, mill.height)):
                return False
            # Check collision with outbuildings
            outbuilding_size = 50
            flour_rect = pygame.Rect(mill.flour_outbuilding_x, mill.flour_outbuilding_y, 
                                     outbuilding_size, outbuilding_size)
            malt_rect = pygame.Rect(mill.malt_outbuilding_x, mill.malt_outbuilding_y, 
                                   outbuilding_size, outbuilding_size)
            if building_rect.colliderect(flour_rect) or building_rect.colliderect(malt_rect):
                return False
        
        return True
    
    def _handle_harvest_target_selection(self, mouse_x, mouse_y):
        """Handle clicking on a target while in harvest cursor mode"""
        if not self.harvest_system:
            return
        
        # Find any harvestable resource under cursor
        resource = self.harvest_system.get_hovered_resource(
            mouse_x, mouse_y, 
            self.game_state.tree_list,
            self.game_state.rock_list,
            self.game_state.iron_mine_list,
            self.game_state.salt_list
        )
        
        if resource:
            # Assign resource to all selected male humans
            assigned_any = False
            for human in self.game_state.human_list:
                if human.selected and human.gender == "male":
                    if self.harvest_system.assign_harvest_target(human, resource, self.game_state):
                        assigned_any = True
            
            if not assigned_any and self.game_state.any_human_selected():
                # Selected humans but couldn't assign (probably all female or no storage)
                pass
        
        # Deactivate harvest cursor
        self.harvest_system.deactivate_harvest_cursor()
    
    def _check_context_menus(self, mouse_x, mouse_y):
        """Check and handle context menu clicks"""
        clicked_menu = False
        
        if self.game_state.show_context_menu:
            option = self._check_sheep_context_menu_click(mouse_x, mouse_y)
            if option:
                for sheep in self.game_state.sheep_list:
                    if sheep.selected:
                        sheep.state = option
                clicked_menu = True
                self.game_state.show_context_menu = False
        
        if self.game_state.show_male_human_context_menu:
            option = self._check_male_human_context_menu_click(mouse_x, mouse_y, self.game_state)
            if option:
                if option == "fire":
                    # Fire selected male humans (only if they are employed)
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "male" and human.is_employed:
                            if human.employer:
                                human.employer.fire_human(human)
                                # Reset human to unemployed state
                                human.state = "wander"
                                human.wander_timer = 0.0
                                human.wander_target_x = None
                                human.wander_target_y = None
                                human.is_wandering = False
                    clicked_menu = True
                    self.game_state.show_male_human_context_menu = False
                elif option == "harvest":
                    # Activate harvest cursor mode
                    if self.harvest_system:
                        self.harvest_system.activate_harvest_cursor()
                        # Hide system cursor
                        pygame.mouse.set_visible(False)
                elif option == "auto":
                    # Set to automated behavior (work if employed, wander if not)
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "male":
                            if human.is_employed:
                                human.state = "employed"
                                
                                # Reset target building and resource type to match job
                                from systems.resource_system import ResourceType
                                if human.job == "lumberjack":
                                    # Find appropriate lumber yard
                                    for lumber_yard in self.game_state.lumber_yard_list:
                                        if lumber_yard.can_accept_resource():
                                            human.target_building = lumber_yard
                                            human.resource_type = ResourceType.LOG
                                            break
                                elif human.job == "miner":
                                    # Find appropriate iron yard
                                    for iron_yard in self.game_state.iron_yard_list:
                                        if iron_yard.can_accept_resource():
                                            human.target_building = iron_yard
                                            human.resource_type = ResourceType.IRON
                                            break
                                elif human.job == "stoneworker":
                                    # Find appropriate stone yard
                                    for stone_yard in self.game_state.stone_yard_list:
                                        if stone_yard.can_accept_resource():
                                            human.target_building = stone_yard
                                            human.resource_type = ResourceType.STONE
                                            break
                                elif human.job == "saltworker":
                                    # Find appropriate salt yard
                                    for salt_yard in self.game_state.salt_yard_list:
                                        if salt_yard.can_accept_resource():
                                            human.target_building = salt_yard
                                            human.resource_type = ResourceType.SALT
                                            break
                                elif human.job == "barleyfarmer":
                                    # Find appropriate silo
                                    for silo in self.game_state.silo_list:
                                        if silo.can_accept_resource():
                                            human.target_building = silo
                                            human.resource_type = ResourceType.BARLEY
                                            break
                                
                                # Restore harvest_target from work_target if work_target exists
                                if human.work_target and not human.harvest_target:
                                    human.harvest_target = human.work_target
                                    # Reset harvest position so it gets recalculated
                                    human.harvest_position = None
                                    human.harvest_timer = 0.0
                                # Clear any manual harvest assignments (not work assignments)
                                # Only clear if there's a conflict (harvest_target different from work_target)
                                if (human.harvest_target and human.work_target and 
                                    human.harvest_target != human.work_target):
                                    human.harvest_target = None
                                    human.harvest_position = None
                                    human.harvest_timer = 0.0
                                
                                # Clear any wrong resource types if carrying something
                                if human.carrying_resource:
                                    # If they're carrying the wrong resource type, drop it
                                    expected_type = None
                                    if human.job == "lumberjack":
                                        expected_type = ResourceType.LOG
                                    elif human.job == "miner":
                                        expected_type = ResourceType.IRON
                                    elif human.job == "stoneworker":
                                        expected_type = ResourceType.STONE
                                    elif human.job == "saltworker":
                                        expected_type = ResourceType.SALT
                                    elif human.job == "barleyfarmer":
                                        expected_type = ResourceType.BARLEY
                                    
                                    if expected_type and human.resource_type != expected_type:
                                        human.carrying_resource = False
                                        human.resource_type = expected_type
                            else:
                                # Unemployed - set to wander
                                human.state = "wander"
                                human.wander_timer = 0.0
                                human.wander_duration = 0.0
                                human.wander_direction = None
                                human.wander_target_x = None
                                human.wander_target_y = None
                                human.is_wandering = False
                else:
                    # Apply follow/stay command to selected male humans
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "male":
                            human.state = option
                            # Cancel harvest if switching states
                            if hasattr(human, 'harvest_target') and human.harvest_target:
                                human.harvest_target = None
                                human.harvest_timer = 0.0
                                human.carrying_resource = False
                                human.harvest_position = None
                clicked_menu = True
                self.game_state.show_male_human_context_menu = False
        
        if self.game_state.show_female_human_context_menu:
            option = self._check_female_human_context_menu_click(mouse_x, mouse_y, self.game_state)
            if option:
                if option == "fire":
                    # Fire selected female humans (only if they are employed)
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "female" and human.is_employed:
                            if human.employer:
                                human.employer.fire_human(human)
                                # Reset human to unemployed state
                                human.state = "wander"
                                human.wander_timer = 0.0
                                human.wander_target_x = None
                                human.wander_target_y = None
                                human.is_wandering = False
                    clicked_menu = True
                    self.game_state.show_female_human_context_menu = False
                elif option == "auto":
                    # Set to automated behavior (work if employed, wander if not)
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "female":
                            if human.is_employed:
                                human.state = "employed"
                                
                                # Reset target building and resource type to match job
                                from systems.resource_system import ResourceType
                                if human.job == "shearer":
                                    # Find appropriate wool shed
                                    for wool_shed in self.game_state.wool_shed_list:
                                        if wool_shed.can_accept_resource():
                                            human.target_building = wool_shed
                                            human.resource_type = ResourceType.WOOL
                                            break
                                
                                # Restore harvest_target from work_target if work_target exists
                                if human.work_target and not human.harvest_target:
                                    human.harvest_target = human.work_target
                                    # Reset harvest position so it gets recalculated
                                    human.harvest_position = None
                                    human.harvest_timer = 0.0
                                # Clear any manual harvest assignments (not work assignments)
                                # Only clear if there's a conflict (harvest_target different from work_target)
                                if (human.harvest_target and human.work_target and 
                                    human.harvest_target != human.work_target):
                                    human.harvest_target = None
                                    human.harvest_position = None
                                    human.harvest_timer = 0.0
                                
                                # Clear any wrong resource types if carrying something
                                if human.carrying_resource:
                                    # If they're carrying the wrong resource type, drop it
                                    expected_type = None
                                    if human.job == "shearer":
                                        expected_type = ResourceType.WOOL
                                    
                                    if expected_type and human.resource_type != expected_type:
                                        human.carrying_resource = False
                                        human.resource_type = expected_type
                            else:
                                # Unemployed - set to wander
                                human.state = "wander"
                                human.wander_timer = 0.0
                                human.wander_duration = 0.0
                                human.wander_direction = None
                                human.wander_target_x = None
                                human.wander_target_y = None
                                human.is_wandering = False
                else:
                    # Apply follow/stay command to selected female humans
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "female":
                            human.state = option
                clicked_menu = True
                self.game_state.show_female_human_context_menu = False
        
        return clicked_menu
    
    def _check_player_context_menu(self, mouse_x, mouse_y):
        """Check and handle player context menu clicks"""
        if self.game_state.show_player_context_menu:
            option = self._check_player_menu_click(mouse_x, mouse_y)
            if option == "build_pen":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "pen"
            elif option == "build_townhall":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "townhall"
            elif option == "build_lumberyard":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "lumberyard"
            elif option == "build_stoneyard":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "stoneyard"
            elif option == "build_ironyard":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "ironyard"
            elif option == "build_saltyard":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "saltyard"
            elif option == "build_woolshed":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "woolshed"
            elif option == "build_barleyfarm":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "barleyfarm"
            elif option == "build_silo":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "silo"
            elif option == "build_mill":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "mill"
            elif option == "build_hut":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "hut"
            self.game_state.show_player_context_menu = False
            return True
        return False
    
    def _place_structure(self, mouse_x, mouse_y):
        """Place a structure in build mode (only if valid placement)"""
        if self.game_state.build_mode_type == "pen":
            pen_x = mouse_x - PEN_SIZE // 2
            pen_y = mouse_y - PEN_SIZE // 2
            pen_x = max(0, min(pen_x, SCREEN_WIDTH - PEN_SIZE))
            pen_y = max(PLAYABLE_AREA_TOP, min(pen_y, PLAYABLE_AREA_BOTTOM - PEN_SIZE))
            
            if self._check_placement_valid(pen_x, pen_y, PEN_SIZE, PEN_SIZE):
                self.game_state.pen_list.append(Pen(pen_x, pen_y, PEN_SIZE, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "townhall":
            # Account for rotation - swap dimensions for 90/270 degree rotations
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = TOWNHALL_HEIGHT
                draw_height = TOWNHALL_WIDTH
            else:
                draw_width = TOWNHALL_WIDTH
                draw_height = TOWNHALL_HEIGHT
            
            townhall_x = mouse_x - draw_width // 2
            townhall_y = mouse_y - draw_height // 2
            townhall_x = max(0, min(townhall_x, SCREEN_WIDTH - draw_width))
            townhall_y = max(PLAYABLE_AREA_TOP, min(townhall_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(townhall_x, townhall_y, draw_width, draw_height):
                self.game_state.townhall_list.append(TownHall(townhall_x, townhall_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "lumberyard":
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = LUMBERYARD_HEIGHT
                draw_height = LUMBERYARD_WIDTH
            else:
                draw_width = LUMBERYARD_WIDTH
                draw_height = LUMBERYARD_HEIGHT
            
            lumberyard_x = mouse_x - draw_width // 2
            lumberyard_y = mouse_y - draw_height // 2
            lumberyard_x = max(0, min(lumberyard_x, SCREEN_WIDTH - draw_width))
            lumberyard_y = max(PLAYABLE_AREA_TOP, min(lumberyard_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(lumberyard_x, lumberyard_y, draw_width, draw_height):
                self.game_state.lumber_yard_list.append(LumberYard(lumberyard_x, lumberyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "stoneyard":
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = STONEYARD_HEIGHT
                draw_height = STONEYARD_WIDTH
            else:
                draw_width = STONEYARD_WIDTH
                draw_height = STONEYARD_HEIGHT
            
            stoneyard_x = mouse_x - draw_width // 2
            stoneyard_y = mouse_y - draw_height // 2
            stoneyard_x = max(0, min(stoneyard_x, SCREEN_WIDTH - draw_width))
            stoneyard_y = max(PLAYABLE_AREA_TOP, min(stoneyard_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(stoneyard_x, stoneyard_y, draw_width, draw_height):
                self.game_state.stone_yard_list.append(StoneYard(stoneyard_x, stoneyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "ironyard":
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = IRONYARD_HEIGHT
                draw_height = IRONYARD_WIDTH
            else:
                draw_width = IRONYARD_WIDTH
                draw_height = IRONYARD_HEIGHT
            
            ironyard_x = mouse_x - draw_width // 2
            ironyard_y = mouse_y - draw_height // 2
            ironyard_x = max(0, min(ironyard_x, SCREEN_WIDTH - draw_width))
            ironyard_y = max(PLAYABLE_AREA_TOP, min(ironyard_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(ironyard_x, ironyard_y, draw_width, draw_height):
                self.game_state.iron_yard_list.append(IronYard(ironyard_x, ironyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "saltyard":
            from entities.saltyard import SaltYard
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = SALTYARD_HEIGHT
                draw_height = SALTYARD_WIDTH
            else:
                draw_width = SALTYARD_WIDTH
                draw_height = SALTYARD_HEIGHT
            
            saltyard_x = mouse_x - draw_width // 2
            saltyard_y = mouse_y - draw_height // 2
            saltyard_x = max(0, min(saltyard_x, SCREEN_WIDTH - draw_width))
            saltyard_y = max(PLAYABLE_AREA_TOP, min(saltyard_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(saltyard_x, saltyard_y, draw_width, draw_height):
                self.game_state.salt_yard_list.append(SaltYard(saltyard_x, saltyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "woolshed":
            from entities.woolshed import WoolShed
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = WOOLSHED_HEIGHT
                draw_height = WOOLSHED_WIDTH
            else:
                draw_width = WOOLSHED_WIDTH
                draw_height = WOOLSHED_HEIGHT
            
            woolshed_x = mouse_x - draw_width // 2
            woolshed_y = mouse_y - draw_height // 2
            woolshed_x = max(0, min(woolshed_x, SCREEN_WIDTH - draw_width))
            woolshed_y = max(PLAYABLE_AREA_TOP, min(woolshed_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(woolshed_x, woolshed_y, draw_width, draw_height):
                self.game_state.wool_shed_list.append(WoolShed(woolshed_x, woolshed_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "barleyfarm":
            from entities.barleyfarm import BarleyFarm
            rotation = self.game_state.pen_rotation
            if rotation == 1 or rotation == 3:
                draw_width = BARLEYFARM_HEIGHT
                draw_height = BARLEYFARM_WIDTH
            else:
                draw_width = BARLEYFARM_WIDTH
                draw_height = BARLEYFARM_HEIGHT
            
            barleyfarm_x = mouse_x - draw_width // 2
            barleyfarm_y = mouse_y - draw_height // 2
            barleyfarm_x = max(0, min(barleyfarm_x, SCREEN_WIDTH - draw_width))
            barleyfarm_y = max(PLAYABLE_AREA_TOP, min(barleyfarm_y, PLAYABLE_AREA_BOTTOM - draw_height))
            
            if self._check_placement_valid(barleyfarm_x, barleyfarm_y, draw_width, draw_height):
                self.game_state.barley_farm_list.append(BarleyFarm(barleyfarm_x, barleyfarm_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "silo":
            from entities.silo import Silo
            silo_x = mouse_x - SILO_RADIUS
            silo_y = mouse_y - SILO_RADIUS
            silo_x = max(0, min(silo_x, SCREEN_WIDTH - SILO_RADIUS * 2))
            silo_y = max(PLAYABLE_AREA_TOP, min(silo_y, PLAYABLE_AREA_BOTTOM - SILO_RADIUS * 2))
            
            if self._check_placement_valid(silo_x, silo_y, SILO_RADIUS * 2, SILO_RADIUS * 2):
                self.game_state.silo_list.append(Silo(silo_x, silo_y))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
            
        elif self.game_state.build_mode_type == "mill":
            from entities.mill import Mill
            from constants import MILL_WIDTH, MILL_HEIGHT
            outbuilding_size = 50
            rotation = self.game_state.pen_rotation
            
            # Calculate mill position based on rotation
            mill_x = mouse_x - MILL_WIDTH / 2
            mill_y = mouse_y - MILL_HEIGHT / 2
            
            # Adjust for outbuildings based on rotation
            if rotation == 0:  # Horizontal: outbuildings left/right
                mill_x = max(outbuilding_size, min(mill_x, SCREEN_WIDTH - MILL_WIDTH - outbuilding_size))
            elif rotation == 2:  # Horizontal reversed
                mill_x = max(outbuilding_size, min(mill_x, SCREEN_WIDTH - MILL_WIDTH - outbuilding_size))
            elif rotation == 1:  # Vertical: outbuildings top/bottom
                mill_y = max(PLAYABLE_AREA_TOP + outbuilding_size, min(mill_y, PLAYABLE_AREA_BOTTOM - MILL_HEIGHT - outbuilding_size))
            else:  # rotation == 3
                mill_y = max(PLAYABLE_AREA_TOP + outbuilding_size, min(mill_y, PLAYABLE_AREA_BOTTOM - MILL_HEIGHT - outbuilding_size))
            
            mill_x = max(0, min(mill_x, SCREEN_WIDTH - MILL_WIDTH))
            mill_y = max(PLAYABLE_AREA_TOP, min(mill_y, PLAYABLE_AREA_BOTTOM - MILL_HEIGHT))
            
            # Check placement including outbuildings
            # Calculate bounding box including outbuildings
            if rotation == 0 or rotation == 2:
                check_x = mill_x - outbuilding_size
                check_width = MILL_WIDTH + outbuilding_size * 2
                check_y = mill_y
                check_height = MILL_HEIGHT
            else:
                check_x = mill_x
                check_width = MILL_WIDTH
                check_y = mill_y - outbuilding_size
                check_height = MILL_HEIGHT + outbuilding_size * 2
            
            if self._check_placement_valid(check_x, check_y, check_width, check_height):
                self.game_state.mill_list.append(Mill(mill_x, mill_y, rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0  # Reset rotation
            
        elif self.game_state.build_mode_type == "hut":
            from entities.hut import Hut
            hut_x = mouse_x - HUT_SIZE // 2
            hut_y = mouse_y - HUT_SIZE // 2
            hut_x = max(0, min(hut_x, SCREEN_WIDTH - HUT_SIZE))
            hut_y = max(PLAYABLE_AREA_TOP, min(hut_y, PLAYABLE_AREA_BOTTOM - HUT_SIZE))
            
            if self._check_placement_valid(hut_x, hut_y, HUT_SIZE, HUT_SIZE):
                self.game_state.hut_list.append(Hut(hut_x, hut_y))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
    
    def _handle_right_click(self, mouse_x, mouse_y):
        """Handle right click - show context menus"""
        # Check for selected entities first - player menu takes priority over town hall menu
        any_sheep_selected = self.game_state.any_sheep_selected()
        any_male_human_selected = self.game_state.any_male_human_selected()
        any_female_human_selected = self.game_state.any_female_human_selected()
        
        # Check if clicking on a town hall
        clicked_townhall = None
        if not self.game_state.build_mode:
            for townhall in self.game_state.townhall_list:
                if townhall.contains_point(mouse_x, mouse_y):
                    clicked_townhall = townhall
                    break
        
        # If entities are selected AND clicking on a town hall, show player menu instead of employment menu
        if (any_sheep_selected or any_male_human_selected or any_female_human_selected) and clicked_townhall:
            # Show player context menu - clamp to playable area
            menu_y = max(PLAYABLE_AREA_TOP + 5, min(mouse_y, PLAYABLE_AREA_BOTTOM - 284))
            self.game_state.show_context_menu = False
            self.game_state.show_male_human_context_menu = False
            self.game_state.show_female_human_context_menu = False
            self.game_state.show_player_context_menu = True
            self.game_state.player_context_menu_x = mouse_x
            self.game_state.player_context_menu_y = menu_y
            
            # Hide employment menu when entities are selected (player menu takes priority)
            if self.employment_menu:
                self.employment_menu.hide()
        elif any_sheep_selected or any_male_human_selected or any_female_human_selected:
            # Entities selected but NOT clicking on town hall - show entity menus as normal
            # Calculate how many menus we'll show
            current_x_offset = mouse_x
            
            # Calculate maximum menu height (in case Auto option and Fire option appear)
            max_menu_height = 147  # Maximum height: base menu (120) + fire option (27)
            
            # Clamp menu Y position to playable area
            menu_y = max(PLAYABLE_AREA_TOP + 5, min(mouse_y, PLAYABLE_AREA_BOTTOM - max_menu_height))
            
            # Show sheep menu if sheep selected
            if any_sheep_selected:
                self.game_state.show_context_menu = True
                self.game_state.context_menu_x = current_x_offset
                self.game_state.context_menu_y = menu_y
                current_x_offset += 145  # Width of sheep menu + spacing
            else:
                self.game_state.show_context_menu = False
            
            # Show male human menu if male humans selected
            if any_male_human_selected:
                self.game_state.show_male_human_context_menu = True
                self.game_state.male_human_context_menu_x = current_x_offset
                self.game_state.male_human_context_menu_y = menu_y
                current_x_offset += 125  # Width of human menu + spacing
            else:
                self.game_state.show_male_human_context_menu = False
            
            # Show female human menu if female humans selected
            if any_female_human_selected:
                self.game_state.show_female_human_context_menu = True
                self.game_state.female_human_context_menu_x = current_x_offset
                self.game_state.female_human_context_menu_y = menu_y
            else:
                self.game_state.show_female_human_context_menu = False
            
            self.game_state.show_player_context_menu = False
            
            # Hide employment menu when showing entity menus
            if self.employment_menu:
                self.employment_menu.hide()
        else:
            # No entities selected - check if clicking on a town hall for employment menu
            if not self.game_state.build_mode and clicked_townhall and self.employment_menu:
                # Show employment menu for this town hall (only when no entities are selected)
                self.employment_menu.show(clicked_townhall, mouse_x, mouse_y)
                # Hide all other context menus
                self.game_state.show_context_menu = False
                self.game_state.show_male_human_context_menu = False
                self.game_state.show_female_human_context_menu = False
                self.game_state.show_player_context_menu = False
                return
            
            # Show player context menu - clamp to playable area
            menu_y = max(PLAYABLE_AREA_TOP + 5, min(mouse_y, PLAYABLE_AREA_BOTTOM - 284))
            self.game_state.show_context_menu = False
            self.game_state.show_male_human_context_menu = False
            self.game_state.show_female_human_context_menu = False
            self.game_state.show_player_context_menu = True
            self.game_state.player_context_menu_x = mouse_x
            self.game_state.player_context_menu_y = menu_y
            
            # Hide employment menu when showing player menu
            if self.employment_menu:
                self.employment_menu.hide()
    
    def _handle_mouse_up(self, event):
        """Handle mouse button release"""
        if event.button == 1 and self.game_state.box_selecting:
            self._complete_box_selection()
    
    def _try_select_entity(self, mouse_x, mouse_y):
        """Try to select a single entity at the click position. Returns True if an entity was clicked."""
        # Check humans first (they're typically on top)
        for human in reversed(self.game_state.human_list):  # Reverse to check top entities first
            if human.contains_point(mouse_x, mouse_y):
                # Single click selection - deselect all, then select this one
                for h in self.game_state.human_list:
                    h.selected = False
                for s in self.game_state.sheep_list:
                    s.selected = False
                human.selected = True
                return True
        
        # Check sheep
        for sheep in reversed(self.game_state.sheep_list):
            if sheep.contains_point(mouse_x, mouse_y):
                # Single click selection - deselect all, then select this one
                for h in self.game_state.human_list:
                    h.selected = False
                for s in self.game_state.sheep_list:
                    s.selected = False
                sheep.selected = True
                return True
        
        return False
    
    def _complete_box_selection(self):
        """Complete box selection and select entities"""
        # Check if this was a click vs drag (very small box = click)
        min_x = min(self.game_state.box_start_x, self.game_state.box_end_x)
        max_x = max(self.game_state.box_start_x, self.game_state.box_end_x)
        min_y = min(self.game_state.box_start_y, self.game_state.box_end_y)
        max_y = max(self.game_state.box_start_y, self.game_state.box_end_y)
        box_width = max_x - min_x
        box_height = max_y - min_y
        
        # If box is very small (click, not drag), try single entity selection
        if box_width < 5 and box_height < 5:
            if self._try_select_entity(min_x, min_y):
                self.game_state.box_selecting = False
                return
        
        self.game_state.box_selecting = False
        
        # Select sheep in box
        for sheep in self.game_state.sheep_list:
            sheep_center_x = sheep.x + sheep.width / 2
            sheep_center_y = sheep.y + sheep.height / 2
            sheep.selected = (min_x <= sheep_center_x <= max_x and 
                            min_y <= sheep_center_y <= max_y)
        
        # Select humans in box
        for human in self.game_state.human_list:
            human_center_x = human.x + human.size / 2
            human_center_y = human.y + human.size / 2
            human.selected = (min_x <= human_center_x <= max_x and 
                            min_y <= human_center_y <= max_y)
    
    def _handle_mouse_motion(self, event):
        """Handle mouse movement"""
        if self.game_state.box_selecting:
            self.game_state.box_end_x, self.game_state.box_end_y = event.pos
    
    def _check_sheep_context_menu_click(self, mx, my):
        """Check if clicking on sheep context menu"""
        context_menu_width = 140
        context_menu_height = 90
        x = self.game_state.context_menu_x
        y = self.game_state.context_menu_y
        
        if x <= mx <= x + context_menu_width:
            if y <= my <= y + 30:
                return "follow"
            elif y + 30 <= my <= y + 57:
                return "stay"
            elif y + 57 <= my <= y + context_menu_height:
                return "gender_separate"
        return None
    
    def _check_male_human_context_menu_click(self, mx, my, game_state):
        """Check if clicking on male human context menu"""
        base_height = 120  # Follow, Stay, Harvest, Auto
        fire_section_start = base_height
        total_height = base_height + 50  # Include fire section
        context_menu_width = 100
        x = self.game_state.male_human_context_menu_x
        y = self.game_state.male_human_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Title area is y to y+20
            # Follow: y+20 to y+50
            # Stay: y+50 to y+77
            # Harvest: y+77 to y+104
            # Auto: y+104 to y+base_height
            if y + 20 <= my <= y + 50:
                return "follow"
            elif y + 50 <= my <= y + 77:
                return "stay"
            elif y + 77 <= my <= y + 104:
                return "harvest"
            elif y + 104 <= my <= y + fire_section_start:
                return "auto"
            elif y + fire_section_start <= my <= y + fire_section_start + 27:
                # Check if fire option is shown (only if selected humans are employed)
                selected_male_humans = [h for h in game_state.human_list if h.selected and h.gender == "male"]
                has_employed_selected = any(h.is_employed for h in selected_male_humans)
                if has_employed_selected:
                    return "fire"
        return None
    
    def _check_female_human_context_menu_click(self, mx, my, game_state):
        """Check if clicking on female human context menu"""
        base_height = 100  # Follow, Stay, Auto
        fire_section_start = base_height
        total_height = base_height + 50  # Include fire section
        context_menu_width = 100
        x = self.game_state.female_human_context_menu_x
        y = self.game_state.female_human_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Title area is y to y+20
            # Follow: y+20 to y+50
            # Stay: y+50 to y+77
            # Auto: y+77 to y+base_height
            if y + 20 <= my <= y + 50:
                return "follow"
            elif y + 50 <= my <= y + 77:
                return "stay"
            elif y + 77 <= my <= y + fire_section_start:
                return "auto"
            elif y + fire_section_start <= my <= y + fire_section_start + 27:
                # Check if fire option is shown (only if selected humans are employed)
                selected_female_humans = [h for h in game_state.human_list if h.selected and h.gender == "female"]
                has_employed_selected = any(h.is_employed for h in selected_female_humans)
                if has_employed_selected:
                    return "fire"
        return None
    
    def _check_player_menu_click(self, mx, my):
        """Check if clicking on player context menu"""
        context_menu_width = 160
        num_build_options = 11
        context_menu_height = num_build_options * 27  # Height without fire section
        x = self.game_state.player_context_menu_x
        y = self.game_state.player_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Check build options
            if y <= my <= y + 30:
                return "build_pen"
            elif y + 30 <= my <= y + 57:
                return "build_townhall"
            elif y + 57 <= my <= y + 84:
                return "build_lumberyard"
            elif y + 84 <= my <= y + 111:
                return "build_stoneyard"
            elif y + 111 <= my <= y + 138:
                return "build_ironyard"
            elif y + 138 <= my <= y + 165:
                return "build_saltyard"
            elif y + 165 <= my <= y + 192:
                return "build_woolshed"
            elif y + 192 <= my <= y + 219:
                return "build_barleyfarm"
            elif y + 219 <= my <= y + 246:
                return "build_silo"
            elif y + 246 <= my <= y + 273:
                return "build_mill"
            elif y + 273 <= my <= y + context_menu_height:
                return "build_hut"
        return None
