"""
Input handling system
"""
import pygame
from constants import *
from entities.pen import Pen
from entities.townhall import TownHall


class InputSystem:
    """Handles all user input (keyboard and mouse)"""
    
    def __init__(self, game_state, harvest_system=None):
        self.game_state = game_state
        self.harvest_system = harvest_system
    
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
        
        # Check context menus first
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
            # Start box selection
            self.game_state.box_selecting = True
            self.game_state.box_start_x = mouse_x
            self.game_state.box_start_y = mouse_y
            self.game_state.box_end_x = mouse_x
            self.game_state.box_end_y = mouse_y
    
    def _handle_harvest_target_selection(self, mouse_x, mouse_y):
        """Handle clicking on a target while in harvest cursor mode"""
        if not self.harvest_system:
            return
        
        # Find tree under cursor
        tree = self.harvest_system.get_hovered_tree(mouse_x, mouse_y, self.game_state.tree_list)
        
        if tree:
            # Assign tree to all selected male humans
            assigned_any = False
            for human in self.game_state.human_list:
                if human.selected and human.gender == "male":
                    if self.harvest_system.assign_harvest_target(human, tree, self.game_state):
                        assigned_any = True
            
            if not assigned_any and self.game_state.any_human_selected():
                # Selected humans but couldn't assign (probably all female)
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
            option = self._check_male_human_context_menu_click(mouse_x, mouse_y)
            if option:
                if option == "harvest":
                    # Activate harvest cursor mode
                    if self.harvest_system:
                        self.harvest_system.activate_harvest_cursor()
                        # Hide system cursor
                        pygame.mouse.set_visible(False)
                else:
                    # Apply follow/stay command to selected male humans
                    for human in self.game_state.human_list:
                        if human.selected and human.gender == "male":
                            human.state = option
                            # Cancel harvest if switching states
                            if hasattr(human, 'harvest_target') and human.harvest_target:
                                human.harvest_target = None
                                human.harvest_timer = 0.0
                                human.carrying_log = False
                clicked_menu = True
                self.game_state.show_male_human_context_menu = False
        
        if self.game_state.show_female_human_context_menu:
            option = self._check_female_human_context_menu_click(mouse_x, mouse_y)
            if option:
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
        
        return False
    
    def _place_structure(self, mouse_x, mouse_y):
        """Place a structure in build mode"""
        if self.game_state.build_mode_type == "pen":
            pen_x = mouse_x - PEN_SIZE // 2
            pen_y = mouse_y - PEN_SIZE // 2
            pen_x = max(0, min(pen_x, SCREEN_WIDTH - PEN_SIZE))
            pen_y = max(0, min(pen_y, SCREEN_HEIGHT - PEN_SIZE))
            self.game_state.pen_list.append(Pen(pen_x, pen_y, PEN_SIZE, self.game_state.pen_rotation))
        elif self.game_state.build_mode_type == "townhall":
            townhall_x = mouse_x - TOWNHALL_WIDTH // 2
            townhall_y = mouse_y - TOWNHALL_HEIGHT // 2
            townhall_x = max(0, min(townhall_x, SCREEN_WIDTH - TOWNHALL_WIDTH))
            townhall_y = max(0, min(townhall_y, SCREEN_HEIGHT - TOWNHALL_HEIGHT))
            self.game_state.townhall_list.append(TownHall(townhall_x, townhall_y, self.game_state.pen_rotation))
        
        self.game_state.build_mode = False
        self.game_state.build_mode_type = None
        self.game_state.pen_rotation = 0
    
    def _handle_right_click(self, mouse_x, mouse_y):
        """Handle right click - show context menus"""
        any_sheep_selected = self.game_state.any_sheep_selected()
        any_male_human_selected = self.game_state.any_male_human_selected()
        any_female_human_selected = self.game_state.any_female_human_selected()
        
        if any_sheep_selected or any_male_human_selected or any_female_human_selected:
            # Calculate how many menus we'll show
            current_x_offset = mouse_x
            
            # Show sheep menu if sheep selected
            if any_sheep_selected:
                self.game_state.show_context_menu = True
                self.game_state.context_menu_x = current_x_offset
                self.game_state.context_menu_y = mouse_y
                current_x_offset += 145  # Width of sheep menu + spacing
            else:
                self.game_state.show_context_menu = False
            
            # Show male human menu if male humans selected
            if any_male_human_selected:
                self.game_state.show_male_human_context_menu = True
                self.game_state.male_human_context_menu_x = current_x_offset
                self.game_state.male_human_context_menu_y = mouse_y
                current_x_offset += 125  # Width of human menu + spacing
            else:
                self.game_state.show_male_human_context_menu = False
            
            # Show female human menu if female humans selected
            if any_female_human_selected:
                self.game_state.show_female_human_context_menu = True
                self.game_state.female_human_context_menu_x = current_x_offset
                self.game_state.female_human_context_menu_y = mouse_y
            else:
                self.game_state.show_female_human_context_menu = False
            
            self.game_state.show_player_context_menu = False
        else:
            # Show player context menu
            self.game_state.show_context_menu = False
            self.game_state.show_male_human_context_menu = False
            self.game_state.show_female_human_context_menu = False
            self.game_state.show_player_context_menu = True
            self.game_state.player_context_menu_x = mouse_x
            self.game_state.player_context_menu_y = mouse_y
    
    def _handle_mouse_up(self, event):
        """Handle mouse button release"""
        if event.button == 1 and self.game_state.box_selecting:
            self._complete_box_selection()
    
    def _complete_box_selection(self):
        """Complete box selection and select entities"""
        self.game_state.box_selecting = False
        
        min_x = min(self.game_state.box_start_x, self.game_state.box_end_x)
        max_x = max(self.game_state.box_start_x, self.game_state.box_end_x)
        min_y = min(self.game_state.box_start_y, self.game_state.box_end_y)
        max_y = max(self.game_state.box_start_y, self.game_state.box_end_y)
        
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
    
    def _check_male_human_context_menu_click(self, mx, my):
        """Check if clicking on male human context menu"""
        context_menu_height = 90  # Males have harvest option
        context_menu_width = 100
        x = self.game_state.male_human_context_menu_x
        y = self.game_state.male_human_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Title area is y to y+20
            # Follow: y+20 to y+50
            # Stay: y+50 to y+77
            # Harvest: y+77 to y+90
            if y + 20 <= my <= y + 50:
                return "follow"
            elif y + 50 <= my <= y + 77:
                return "stay"
            elif y + 77 <= my <= y + context_menu_height:
                return "harvest"
        return None
    
    def _check_female_human_context_menu_click(self, mx, my):
        """Check if clicking on female human context menu"""
        context_menu_height = 70  # Females don't have harvest option
        context_menu_width = 100
        x = self.game_state.female_human_context_menu_x
        y = self.game_state.female_human_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            # Title area is y to y+20
            # Follow: y+20 to y+50
            # Stay: y+50 to y+70
            if y + 20 <= my <= y + 50:
                return "follow"
            elif y + 50 <= my <= y + context_menu_height:
                return "stay"
        return None
    
    def _check_player_menu_click(self, mx, my):
        """Check if clicking on player context menu"""
        context_menu_width = 140
        context_menu_height = 60
        x = self.game_state.player_context_menu_x
        y = self.game_state.player_context_menu_y
        
        if x <= mx <= x + context_menu_width:
            if y <= my <= y + 30:
                return "build_pen"
            elif y + 30 <= my <= y + context_menu_height:
                return "build_townhall"
        return None
