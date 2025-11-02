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
            self._draw_player_menu(screen, game_state.player_context_menu_x, game_state.player_context_menu_y)
    
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
        # Always show Auto option for all humans
        height = 120  # Follow, Stay, Harvest, Auto
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
    
    def _draw_female_human_menu(self, screen, x, y, game_state):
        """Draw female human context menu"""
        # Always show Auto option for all humans
        height = 100  # Follow, Stay, Auto
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
    
    def _draw_player_menu(self, screen, x, y):
        """Draw player context menu"""
        width = 160
        height = 210  # Increased for 7 options (including salt yard and hut)
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Draw options
        build_pen_text = self.font.render("Build Pen", True, BLACK)
        build_townhall_text = self.font.render("Build Town Hall", True, BLACK)
        build_lumberyard_text = self.font.render("Build Lumber Yard", True, BLACK)
        build_stoneyard_text = self.font.render("Build Stone Yard", True, BLACK)
        build_ironyard_text = self.font.render("Build Iron Yard", True, BLACK)
        build_saltyard_text = self.font.render("Build Salt Yard", True, BLACK)
        build_hut_text = self.font.render("Build Hut", True, BLACK)
        
        screen.blit(build_pen_text, (x + 10, y + 5))
        screen.blit(build_townhall_text, (x + 10, y + 32))
        screen.blit(build_lumberyard_text, (x + 10, y + 59))
        screen.blit(build_stoneyard_text, (x + 10, y + 86))
        screen.blit(build_ironyard_text, (x + 10, y + 113))
        screen.blit(build_saltyard_text, (x + 10, y + 140))
        screen.blit(build_hut_text, (x + 10, y + 167))
        
        # Draw separators
        pygame.draw.line(screen, BLACK, (x, y + 30), (x + width, y + 30), 1)
        pygame.draw.line(screen, BLACK, (x, y + 57), (x + width, y + 57), 1)
        pygame.draw.line(screen, BLACK, (x, y + 84), (x + width, y + 84), 1)
        pygame.draw.line(screen, BLACK, (x, y + 111), (x + width, y + 111), 1)
        pygame.draw.line(screen, BLACK, (x, y + 138), (x + width, y + 138), 1)
        pygame.draw.line(screen, BLACK, (x, y + 165), (x + width, y + 165), 1)
