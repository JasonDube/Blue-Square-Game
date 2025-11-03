"""
Context menu UI components
"""
import pygame
from constants import *


class ContextMenuRenderer:
    """Handles rendering of all context menus"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
    
    def draw_all(self, screen, game_state):
        """Draw all active context menus"""
        if game_state.show_context_menu:
            self._draw_sheep_menu(screen, game_state.context_menu_x, game_state.context_menu_y)
        
        if game_state.show_male_human_context_menu:
            self._draw_male_human_menu(
                screen, 
                game_state.male_human_context_menu_x, 
                game_state.male_human_context_menu_y,
                game_state
            )
        
        if game_state.show_female_human_context_menu:
            self._draw_female_human_menu(
                screen, 
                game_state.female_human_context_menu_x, 
                game_state.female_human_context_menu_y,
                game_state
            )
        
        if game_state.show_player_context_menu:
            self._draw_player_menu(screen, game_state.player_context_menu_x, game_state.player_context_menu_y, game_state)
    
    def _draw_sheep_menu(self, screen, x, y):
        """Draw sheep context menu"""
        width = 140
        height = 90
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Draw options
        follow_text = self.font.render("Follow", True, BLACK)
        stay_text = self.font.render("Stay", True, BLACK)
        gender_separate_text = self.font.render("Gender Separate", True, BLACK)
        
        screen.blit(follow_text, (x + 10, y + 5))
        screen.blit(stay_text, (x + 10, y + 32))
        screen.blit(gender_separate_text, (x + 10, y + 59))
        
        # Draw separators
        pygame.draw.line(screen, BLACK, (x, y + 30), (x + width, y + 30), 1)
        pygame.draw.line(screen, BLACK, (x, y + 57), (x + width, y + 57), 1)
    
    def _draw_male_human_menu(self, screen, x, y, game_state):
        """Draw male human context menu"""
        # Calculate height based on options + fire option
        base_height = 120  # Follow, Stay, Harvest, Auto
        fire_section_height = 27  # Fire option (single line)
        # Check if selected humans are employed to show fire option
        selected_male_humans = [h for h in game_state.human_list if h.selected and h.gender == "male"]
        has_employed_selected = any(h.is_employed for h in selected_male_humans)
        height = base_height + (fire_section_height if has_employed_selected else 0)
        width = 100
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Draw title
        title_font = pygame.font.Font(None, 18)
        title_text = title_font.render("Male Humans", True, BLUE)
        screen.blit(title_text, (x + 10, y + 5))
        
        # Draw options
        follow_text = self.font.render("Follow", True, BLACK)
        stay_text = self.font.render("Stay", True, BLACK)
        harvest_text = self.font.render("Harvest", True, BLACK)
        
        screen.blit(follow_text, (x + 10, y + 25))
        screen.blit(stay_text, (x + 10, y + 52))
        screen.blit(harvest_text, (x + 10, y + 79))
        
        # Draw Auto option for all humans
        auto_text = self.font.render("Auto", True, BLACK)
        screen.blit(auto_text, (x + 10, y + 106))
        pygame.draw.line(screen, BLACK, (x, y + 104), (x + width, y + 104), 1)
        
        # Draw separators
        pygame.draw.line(screen, BLACK, (x, y + 20), (x + width, y + 20), 1)
        pygame.draw.line(screen, BLACK, (x, y + 50), (x + width, y + 50), 1)
        pygame.draw.line(screen, BLACK, (x, y + 77), (x + width, y + 77), 1)
        
        # Draw "Fire" option (only if selected humans are employed)
        fire_y = y + base_height
        selected_male_humans = [h for h in game_state.human_list if h.selected and h.gender == "male"]
        has_employed_selected = any(h.is_employed for h in selected_male_humans)
        
        if has_employed_selected:
            fire_text = self.font.render("Fire", True, BLACK)
            screen.blit(fire_text, (x + 10, fire_y + 3))
            # Draw separator before fire option
            pygame.draw.line(screen, BLACK, (x, fire_y), (x + width, fire_y), 2)
    
    def _draw_female_human_menu(self, screen, x, y, game_state):
        """Draw female human context menu"""
        # Calculate height based on options + fire option
        base_height = 100  # Follow, Stay, Auto
        fire_section_height = 27  # Fire option (single line)
        # Check if selected humans are employed to show fire option
        selected_female_humans = [h for h in game_state.human_list if h.selected and h.gender == "female"]
        has_employed_selected = any(h.is_employed for h in selected_female_humans)
        height = base_height + (fire_section_height if has_employed_selected else 0)
        width = 100
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Draw title
        title_font = pygame.font.Font(None, 18)
        title_text = title_font.render("Female Humans", True, PINK)
        screen.blit(title_text, (x + 10, y + 5))
        
        # Draw options
        follow_text = self.font.render("Follow", True, BLACK)
        stay_text = self.font.render("Stay", True, BLACK)
        
        screen.blit(follow_text, (x + 10, y + 25))
        screen.blit(stay_text, (x + 10, y + 52))
        
        # Draw Auto option for all humans
        auto_text = self.font.render("Auto", True, BLACK)
        screen.blit(auto_text, (x + 10, y + 79))
        pygame.draw.line(screen, BLACK, (x, y + 77), (x + width, y + 77), 1)
        
        # Draw separators
        pygame.draw.line(screen, BLACK, (x, y + 20), (x + width, y + 20), 1)
        pygame.draw.line(screen, BLACK, (x, y + 50), (x + width, y + 50), 1)
        
        # Draw "Fire" option (only if selected humans are employed)
        fire_y = y + base_height
        selected_female_humans = [h for h in game_state.human_list if h.selected and h.gender == "female"]
        has_employed_selected = any(h.is_employed for h in selected_female_humans)
        
        if has_employed_selected:
            fire_text = self.font.render("Fire", True, BLACK)
            screen.blit(fire_text, (x + 10, fire_y + 3))
            # Draw separator before fire option
            pygame.draw.line(screen, BLACK, (x, fire_y), (x + width, fire_y), 2)
    
    def _draw_player_menu(self, screen, x, y, game_state):
        """Draw player context menu (build menu when nothing selected)"""
        width = 160
        num_build_options = 11
        height = num_build_options * 27  # 27 pixels per option
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Draw build options
        build_pen_text = self.font.render("Build Pen", True, BLACK)
        build_townhall_text = self.font.render("Build Town Hall", True, BLACK)
        build_lumberyard_text = self.font.render("Build Lumber Yard", True, BLACK)
        build_stoneyard_text = self.font.render("Build Stone Yard", True, BLACK)
        build_ironyard_text = self.font.render("Build Iron Yard", True, BLACK)
        build_saltyard_text = self.font.render("Build Salt Yard", True, BLACK)
        build_woolshed_text = self.font.render("Build Wool Shed", True, BLACK)
        build_barleyfarm_text = self.font.render("Build Barley Farm", True, BLACK)
        build_silo_text = self.font.render("Build Silo", True, BLACK)
        build_mill_text = self.font.render("Build Mill", True, BLACK)
        build_hut_text = self.font.render("Build Hut", True, BLACK)
        
        screen.blit(build_pen_text, (x + 10, y + 5))
        screen.blit(build_townhall_text, (x + 10, y + 32))
        screen.blit(build_lumberyard_text, (x + 10, y + 59))
        screen.blit(build_stoneyard_text, (x + 10, y + 86))
        screen.blit(build_ironyard_text, (x + 10, y + 113))
        screen.blit(build_saltyard_text, (x + 10, y + 140))
        screen.blit(build_woolshed_text, (x + 10, y + 167))
        screen.blit(build_barleyfarm_text, (x + 10, y + 194))
        screen.blit(build_silo_text, (x + 10, y + 221))
        screen.blit(build_mill_text, (x + 10, y + 248))
        screen.blit(build_hut_text, (x + 10, y + 275))
        
        # Draw separators for build options
        for i in range(num_build_options):
            pygame.draw.line(screen, BLACK, (x, y + 30 + i * 27), (x + width, y + 30 + i * 27), 1)
