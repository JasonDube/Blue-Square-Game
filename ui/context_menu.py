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
                game_state.male_human_context_menu_y
            )
        
        if game_state.show_female_human_context_menu:
            self._draw_female_human_menu(
                screen, 
                game_state.female_human_context_menu_x, 
                game_state.female_human_context_menu_y
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
    
    def _draw_male_human_menu(self, screen, x, y):
        """Draw male human context menu"""
        height = 90  # Males have harvest option
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
        
        # Draw separators
        pygame.draw.line(screen, BLACK, (x, y + 20), (x + width, y + 20), 1)
        pygame.draw.line(screen, BLACK, (x, y + 50), (x + width, y + 50), 1)
        pygame.draw.line(screen, BLACK, (x, y + 77), (x + width, y + 77), 1)
    
    def _draw_female_human_menu(self, screen, x, y):
        """Draw female human context menu"""
        height = 70  # Females don't have harvest option
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
        
        # Draw separators
        pygame.draw.line(screen, BLACK, (x, y + 20), (x + width, y + 20), 1)
        pygame.draw.line(screen, BLACK, (x, y + 50), (x + width, y + 50), 1)
    
    def _draw_player_menu(self, screen, x, y):
        """Draw player context menu"""
        width = 140
        height = 60
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (x, y, width, height))
        pygame.draw.rect(screen, BLACK, (x, y, width, height), 2)
        
        # Draw options
        build_pen_text = self.font.render("Build Pen", True, BLACK)
        build_townhall_text = self.font.render("Build Town Hall", True, BLACK)
        
        screen.blit(build_pen_text, (x + 10, y + 5))
        screen.blit(build_townhall_text, (x + 10, y + 32))
        
        # Draw separator
        pygame.draw.line(screen, BLACK, (x, y + 30), (x + width, y + 30), 1)
