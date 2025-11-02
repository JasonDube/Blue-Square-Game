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
        
        # Check structure buttons
        if not self.game_state.build_mode and self._check_structure_buttons(mouse_x, mouse_y):
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
        
        for hut in self.game_state.hut_list:
            if building_rect.colliderect(pygame.Rect(hut.x, hut.y, hut.size, hut.size)):
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
            self.game_state.iron_mine_list
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
                if option == "harvest":
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
                                if human.job == "lumberjack":
                                    from systems.resource_system import ResourceType
                                    # Find appropriate lumber yard
                                    for lumber_yard in self.game_state.lumber_yard_list:
                                        if lumber_yard.can_accept_resource():
                                            human.target_building = lumber_yard
                                            human.resource_type = ResourceType.LOG
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
                                if human.carrying_resource and human.job == "lumberjack":
                                    # If they're carrying the wrong resource type, drop it
                                    if human.resource_type != ResourceType.LOG:
                                        human.carrying_resource = False
                                        human.resource_type = ResourceType.LOG
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
                if option == "auto":
                    # Set to automated behavior (work if employed, wander if not)
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "female":
                            if human.is_employed:
                                human.state = "employed"
                                # Restore harvest_target from work_target if work_target exists
                                if human.work_target and not human.harvest_target:
                                    human.harvest_target = human.work_target
                                    # Reset harvest position so it gets recalculated
                                    human.harvest_position = None
                                    human.harvest_timer = 0.0
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
            elif option == "build_hut":
                self.game_state.build_mode = True
                self.game_state.build_mode_type = "hut"
            self.game_state.show_player_context_menu = False
            return True
        return False
    
    def _check_structure_buttons(self, mouse_x, mouse_y):
        """Check if clicking on structure toggle buttons"""
        # Check pen buttons
        for pen in self.game_state.pen_list:
            button_rect = pen.get_button_rect()
            if button_rect.collidepoint(mouse_x, mouse_y):
                pen.collision_enabled = not pen.collision_enabled
                return True
        
        # Check townhall buttons
        for townhall in self.game_state.townhall_list:
            button_rect = townhall.get_button_rect()
            if button_rect.collidepoint(mouse_x, mouse_y):
                townhall.collision_enabled = not townhall.collision_enabled
                return True
        
        # Check lumber yard buttons
        for lumber_yard in self.game_state.lumber_yard_list:
            button_rect = lumber_yard.get_button_rect()
            if button_rect.collidepoint(mouse_x, mouse_y):
                lumber_yard.collision_enabled = not lumber_yard.collision_enabled
                return True
        
        # Check stone yard buttons
        for stone_yard in self.game_state.stone_yard_list:
            button_rect = stone_yard.get_button_rect()
            if button_rect.collidepoint(mouse_x, mouse_y):
                stone_yard.collision_enabled = not stone_yard.collision_enabled
                return True
        
        # Check iron yard buttons
        for iron_yard in self.game_state.iron_yard_list:
            button_rect = iron_yard.get_button_rect()
            if button_rect.collidepoint(mouse_x, mouse_y):
                iron_yard.collision_enabled = not iron_yard.collision_enabled
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
            townhall_x = mouse_x - TOWNHALL_WIDTH // 2
            townhall_y = mouse_y - TOWNHALL_HEIGHT // 2
            townhall_x = max(0, min(townhall_x, SCREEN_WIDTH - TOWNHALL_WIDTH))
            townhall_y = max(PLAYABLE_AREA_TOP, min(townhall_y, PLAYABLE_AREA_BOTTOM - TOWNHALL_HEIGHT))
            
            if self._check_placement_valid(townhall_x, townhall_y, TOWNHALL_WIDTH, TOWNHALL_HEIGHT):
                self.game_state.townhall_list.append(TownHall(townhall_x, townhall_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "lumberyard":
            lumberyard_x = mouse_x - LUMBERYARD_WIDTH // 2
            lumberyard_y = mouse_y - LUMBERYARD_HEIGHT // 2
            lumberyard_x = max(0, min(lumberyard_x, SCREEN_WIDTH - LUMBERYARD_WIDTH))
            lumberyard_y = max(PLAYABLE_AREA_TOP, min(lumberyard_y, PLAYABLE_AREA_BOTTOM - LUMBERYARD_HEIGHT))
            
            if self._check_placement_valid(lumberyard_x, lumberyard_y, LUMBERYARD_WIDTH, LUMBERYARD_HEIGHT):
                self.game_state.lumber_yard_list.append(LumberYard(lumberyard_x, lumberyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "stoneyard":
            stoneyard_x = mouse_x - STONEYARD_WIDTH // 2
            stoneyard_y = mouse_y - STONEYARD_HEIGHT // 2
            stoneyard_x = max(0, min(stoneyard_x, SCREEN_WIDTH - STONEYARD_WIDTH))
            stoneyard_y = max(PLAYABLE_AREA_TOP, min(stoneyard_y, PLAYABLE_AREA_BOTTOM - STONEYARD_HEIGHT))
            
            if self._check_placement_valid(stoneyard_x, stoneyard_y, STONEYARD_WIDTH, STONEYARD_HEIGHT):
                self.game_state.stone_yard_list.append(StoneYard(stoneyard_x, stoneyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
        elif self.game_state.build_mode_type == "ironyard":
            ironyard_x = mouse_x - IRONYARD_WIDTH // 2
            ironyard_y = mouse_y - IRONYARD_HEIGHT // 2
            ironyard_x = max(0, min(ironyard_x, SCREEN_WIDTH - IRONYARD_WIDTH))
            ironyard_y = max(PLAYABLE_AREA_TOP, min(ironyard_y, PLAYABLE_AREA_BOTTOM - IRONYARD_HEIGHT))
            
            if self._check_placement_valid(ironyard_x, ironyard_y, IRONYARD_WIDTH, IRONYARD_HEIGHT):
                self.game_state.iron_yard_list.append(IronYard(ironyard_x, ironyard_y, self.game_state.pen_rotation))
                self.game_state.build_mode = False
                self.game_state.build_mode_type = None
                self.game_state.pen_rotation = 0
            
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
        # First check if clicking on a town hall (but not if in build mode)
        if not self.game_state.build_mode:
            clicked_townhall = None
            for townhall in self.game_state.townhall_list:
                if townhall.contains_point(mouse_x, mouse_y):
                    clicked_townhall = townhall
                    break
            
            if clicked_townhall and self.employment_menu:
                # Show employment menu for this town hall
                self.employment_menu.show(clicked_townhall, mouse_x, mouse_y)
                # Hide all other context menus
                self.game_state.show_context_menu = False
                self.game_state.show_male_human_context_menu = False
                self.game_state.show_female_human_context_menu = False
                self.game_state.show_player_context_menu = False
                return
        
        any_sheep_selected = self.game_state.any_sheep_selected()
        any_male_human_selected = self.game_state.any_male_human_selected()
        any_female_human_selected = self.game_state.any_female_human_selected()
        
        if any_sheep_selected or any_male_human_selected or any_female_human_selected:
            # Calculate how many menus we'll show
            current_x_offset = mouse_x
            
            # Calculate maximum menu height (in case Auto option appears)
            max_menu_height = 120  # Maximum height if Auto appears
            
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
        else:
            # Show player context menu - clamp to playable area
            menu_y = max(PLAYABLE_AREA_TOP + 5, min(mouse_y, PLAYABLE_AREA_BOTTOM - 190))
            self.game_state.show_context_menu = False
            self.game_state.show_male_human_context_menu = False
            self.game_state.show_female_human_context_menu = False
            self.game_state.show_player_context_menu = True
            self.game_state.player_context_menu_x = mouse_x
            self.game_state.player_context_menu_y = menu_y
        
        # Hide employment menu when showing other context menus
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
        context_menu_height = 120  # Follow, Stay, Harvest, Auto (always shown)
        context_menu_width = 100
        x = self.game_state.male_human_context_menu_x
        y = self.game_state.male_human_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Title area is y to y+20
            # Follow: y+20 to y+50
            # Stay: y+50 to y+77
            # Harvest: y+77 to y+104
            # Auto: y+104 to y+120
            if y + 20 <= my <= y + 50:
                return "follow"
            elif y + 50 <= my <= y + 77:
                return "stay"
            elif y + 77 <= my <= y + 104:
                return "harvest"
            elif y + 104 <= my <= y + context_menu_height:
                return "auto"
        return None
    
    def _check_female_human_context_menu_click(self, mx, my, game_state):
        """Check if clicking on female human context menu"""
        context_menu_height = 100  # Follow, Stay, Auto (always shown)
        context_menu_width = 100
        x = self.game_state.female_human_context_menu_x
        y = self.game_state.female_human_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Title area is y to y+20
            # Follow: y+20 to y+50
            # Stay: y+50 to y+77
            # Auto: y+77 to y+100
            if y + 20 <= my <= y + 50:
                return "follow"
            elif y + 50 <= my <= y + 77:
                return "stay"
            elif y + 77 <= my <= y + context_menu_height:
                return "auto"
        return None
    
    def _check_player_menu_click(self, mx, my):
        """Check if clicking on player context menu"""
        context_menu_width = 160
        context_menu_height = 180  # Increased for 6 options (including hut)
        x = self.game_state.player_context_menu_x
        y = self.game_state.player_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            if y <= my <= y + 30:
                return "build_pen"
            elif y + 30 <= my <= y + 60:
                return "build_townhall"
            elif y + 60 <= my <= y + 90:
                return "build_lumberyard"
            elif y + 90 <= my <= y + 120:
                return "build_stoneyard"
            elif y + 120 <= my <= y + 150:
                return "build_ironyard"
            elif y + 150 <= my <= y + context_menu_height:
                return "build_hut"
        return None
