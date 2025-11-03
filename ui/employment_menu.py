"""
Employment menu UI for town halls
"""
import pygame
from constants import *


class EmploymentMenu:
    """Menu for hiring workers at town halls"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.active = False
        self.townhall = None
        self.x = 0
        self.y = 0
        self.width = 250
        self.height = 420  # Increased height for all job options including miller
    
    def show(self, townhall, x, y):
        """Show the employment menu for a specific town hall"""
        self.active = True
        self.townhall = townhall
        self.x = x
        self.y = y
        
        # Adjust position to keep menu within playable area
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width - 10
        # Keep menu within playable area (above bottom HUD)
        if self.y + self.height > PLAYABLE_AREA_BOTTOM:
            self.y = PLAYABLE_AREA_BOTTOM - self.height - 10
        # Keep menu below top HUD
        if self.y < PLAYABLE_AREA_TOP:
            self.y = PLAYABLE_AREA_TOP + 10
    
    def hide(self):
        """Hide the employment menu"""
        self.active = False
        self.townhall = None
    
    def draw(self, screen, game_state):
        """Draw the employment menu"""
        if not self.active or not self.townhall:
            return
        
        # Count unemployed humans
        unemployed_males = sum(1 for h in game_state.human_list 
                              if h.gender == "male" and not h.is_employed)
        unemployed_females = sum(1 for h in game_state.human_list 
                                if h.gender == "female" and not h.is_employed)
        
        # Draw background
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        title_text = self.font.render("Town Hall Employment", True, BLACK)
        screen.blit(title_text, (self.x + 10, self.y + 5))
        
        # Draw separator
        pygame.draw.line(screen, BLACK, (self.x, self.y + 30), 
                        (self.x + self.width, self.y + 30), 1)
        
        # Draw unemployed count
        unemployed_text = f"Unemployed: {unemployed_males}M / {unemployed_females}F"
        unemployed_surface = self.font_small.render(unemployed_text, True, BLACK)
        screen.blit(unemployed_surface, (self.x + 10, self.y + 35))
        
        # Draw separator
        pygame.draw.line(screen, BLACK, (self.x, self.y + 55), 
                        (self.x + self.width, self.y + 55), 1)
        
        # Draw job options
        current_y = self.y + 60
        button_spacing = 35
        
        # Lumberjack option
        lumberjack_info = self.townhall.job_slots['lumberjack']
        lumberjack_text = f"Lumberjack ({lumberjack_info['filled']}/{lumberjack_info['max']})"
        lumberjack_surface = self.font.render(lumberjack_text, True, BLACK)
        screen.blit(lumberjack_surface, (self.x + 10, current_y))
        
        # Draw hire button
        hire_button_x = self.x + self.width - 60
        hire_button_y = current_y
        hire_button_width = 50
        hire_button_height = 25
        
        # Check if can hire
        can_hire_lumberjack = (unemployed_males > 0 and 
                               self.townhall.can_hire('lumberjack'))
        
        button_color = GREEN if can_hire_lumberjack else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text = self.font_small.render("Hire", True, BLACK)
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Miner option
        current_y += button_spacing
        miner_info = self.townhall.job_slots['miner']
        miner_text = f"Miner ({miner_info['filled']}/{miner_info['max']})"
        miner_surface = self.font.render(miner_text, True, BLACK)
        screen.blit(miner_surface, (self.x + 10, current_y))
        
        hire_button_y = current_y
        can_hire_miner = (unemployed_males > 0 and 
                         self.townhall.can_hire('miner'))
        
        button_color = GREEN if can_hire_miner else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Stoneworker option
        current_y += button_spacing
        stoneworker_info = self.townhall.job_slots['stoneworker']
        stoneworker_text = f"Stoneworker ({stoneworker_info['filled']}/{stoneworker_info['max']})"
        stoneworker_surface = self.font.render(stoneworker_text, True, BLACK)
        screen.blit(stoneworker_surface, (self.x + 10, current_y))
        
        hire_button_y = current_y
        can_hire_stoneworker = (unemployed_males > 0 and 
                               self.townhall.can_hire('stoneworker'))
        
        button_color = GREEN if can_hire_stoneworker else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Saltworker option
        current_y += button_spacing
        saltworker_info = self.townhall.job_slots['saltworker']
        saltworker_text = f"Saltworker ({saltworker_info['filled']}/{saltworker_info['max']})"
        saltworker_surface = self.font.render(saltworker_text, True, BLACK)
        screen.blit(saltworker_surface, (self.x + 10, current_y))
        
        hire_button_y = current_y
        can_hire_saltworker = (unemployed_males > 0 and 
                              self.townhall.can_hire('saltworker'))
        
        button_color = GREEN if can_hire_saltworker else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Shearer option (female only)
        current_y += button_spacing
        shearer_info = self.townhall.job_slots['shearer']
        shearer_text = f"Shearer ({shearer_info['filled']}/{shearer_info['max']})"
        shearer_surface = self.font.render(shearer_text, True, BLACK)
        screen.blit(shearer_surface, (self.x + 10, current_y))
        
        hire_button_y = current_y
        can_hire_shearer = (unemployed_females > 0 and 
                           self.townhall.can_hire('shearer'))
        
        button_color = GREEN if can_hire_shearer else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Barley farmer option
        current_y += button_spacing
        barleyfarmer_info = self.townhall.job_slots['barleyfarmer']
        barleyfarmer_text = f"Barley Farmer ({barleyfarmer_info['filled']}/{barleyfarmer_info['max']})"
        barleyfarmer_surface = self.font.render(barleyfarmer_text, True, BLACK)
        screen.blit(barleyfarmer_surface, (self.x + 10, current_y))
        
        hire_button_y = current_y
        can_hire_barleyfarmer = (unemployed_males > 0 and 
                                self.townhall.can_hire('barleyfarmer'))
        
        button_color = GREEN if can_hire_barleyfarmer else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Miller option
        current_y += button_spacing
        miller_info = self.townhall.job_slots['miller']
        miller_text = f"Miller ({miller_info['filled']}/{miller_info['max']})"
        miller_surface = self.font.render(miller_text, True, BLACK)
        screen.blit(miller_surface, (self.x + 10, current_y))
        
        hire_button_y = current_y
        can_hire_miller = (unemployed_males > 0 and 
                          self.townhall.can_hire('miller'))
        
        button_color = GREEN if can_hire_miller else GRAY
        pygame.draw.rect(screen, button_color, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (hire_button_x, hire_button_y, hire_button_width, hire_button_height), 2)
        
        hire_text_rect = hire_text.get_rect(center=(hire_button_x + hire_button_width//2, 
                                                     hire_button_y + hire_button_height//2))
        screen.blit(hire_text, hire_text_rect)
        
        # Draw close button at bottom
        close_button_y = self.y + self.height - 35
        close_button_width = 80
        close_button_height = 25
        close_button_x = self.x + (self.width - close_button_width) // 2
        
        pygame.draw.rect(screen, RED, 
                        (close_button_x, close_button_y, close_button_width, close_button_height))
        pygame.draw.rect(screen, BLACK, 
                        (close_button_x, close_button_y, close_button_width, close_button_height), 2)
        
        close_text = self.font.render("Close", True, WHITE)
        close_text_rect = close_text.get_rect(center=(close_button_x + close_button_width//2,
                                                       close_button_y + close_button_height//2))
        screen.blit(close_text, close_text_rect)
    
    def handle_click(self, mouse_x, mouse_y, game_state):
        """Handle mouse click on the menu"""
        if not self.active or not self.townhall:
            return False
        
        # Check if click is outside menu - close it
        if not (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
            self.hide()
            return True
        
        # Check close button
        close_button_y = self.y + self.height - 35
        close_button_width = 80
        close_button_height = 25
        close_button_x = self.x + (self.width - close_button_width) // 2
        
        if (close_button_x <= mouse_x <= close_button_x + close_button_width and
            close_button_y <= mouse_y <= close_button_y + close_button_height):
            self.hide()
            return True
        
        # Check hire buttons
        hire_button_x = self.x + self.width - 60
        hire_button_width = 50
        hire_button_height = 25
        button_spacing = 35
        
        # Lumberjack button
        hire_button_y = self.y + 60
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_lumberjack(game_state)
            return True
        
        # Miner button
        hire_button_y = self.y + 60 + button_spacing
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_miner(game_state)
            return True
        
        # Stoneworker button
        hire_button_y = self.y + 60 + button_spacing * 2
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_stoneworker(game_state)
            return True
        
        # Saltworker button
        hire_button_y = self.y + 60 + button_spacing * 3
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_saltworker(game_state)
            return True
        
        # Shearer button
        hire_button_y = self.y + 60 + button_spacing * 4
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_shearer(game_state)
            return True
        
        # Barley farmer button
        hire_button_y = self.y + 60 + button_spacing * 5
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_barleyfarmer(game_state)
            return True
        
        # Miller button
        hire_button_y = self.y + 60 + button_spacing * 6
        if (hire_button_x <= mouse_x <= hire_button_x + hire_button_width and
            hire_button_y <= mouse_y <= hire_button_y + hire_button_height):
            self._hire_miller(game_state)
            return True
        
        return False
    
    def _hire_lumberjack(self, game_state):
        """Hire an unemployed male as a lumberjack"""
        # Find first unemployed male
        for human in game_state.human_list:
            if human.gender == "male" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'lumberjack'):
                    human.is_employed = True
                    return
    
    def _hire_miner(self, game_state):
        """Hire an unemployed male as a miner"""
        # Find first unemployed male
        for human in game_state.human_list:
            if human.gender == "male" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'miner'):
                    human.is_employed = True
                    return
    
    def _hire_stoneworker(self, game_state):
        """Hire an unemployed male as a stoneworker"""
        # Find first unemployed male
        for human in game_state.human_list:
            if human.gender == "male" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'stoneworker'):
                    human.is_employed = True
                    return
    
    def _hire_saltworker(self, game_state):
        """Hire an unemployed male as a saltworker"""
        # Find first unemployed male
        for human in game_state.human_list:
            if human.gender == "male" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'saltworker'):
                    human.is_employed = True
                    return
    
    def _hire_shearer(self, game_state):
        """Hire an unemployed female as a shearer"""
        # Find first unemployed female
        for human in game_state.human_list:
            if human.gender == "female" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'shearer'):
                    human.is_employed = True
                    return
    
    def _hire_barleyfarmer(self, game_state):
        """Hire an unemployed male as a barley farmer"""
        # Find first unemployed male
        for human in game_state.human_list:
            if human.gender == "male" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'barleyfarmer'):
                    human.is_employed = True
                    return
    
    def _hire_miller(self, game_state):
        """Hire an unemployed male as a miller"""
        # Find first unemployed male
        for human in game_state.human_list:
            if human.gender == "male" and not human.is_employed:
                # Try to hire them
                if self.townhall.hire_human(human, 'miller'):
                    human.is_employed = True
                    return
