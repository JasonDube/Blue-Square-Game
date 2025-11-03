"""
Bottom HUD component - displays information at the bottom of the screen
"""
import pygame
from constants import *


class HUDLow:
    """Displays game information at the bottom of the screen"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.bar_height = HUD_BOTTOM_HEIGHT
    
    def draw(self, screen, game_state):
        """Draw the HUD bar at bottom of screen"""
        # Draw white filled rectangle
        y_pos = SCREEN_HEIGHT - self.bar_height
        pygame.draw.rect(screen, WHITE, (0, y_pos, SCREEN_WIDTH, self.bar_height))
        pygame.draw.rect(screen, BLACK, (0, y_pos, SCREEN_WIDTH, self.bar_height), 1)
        
        # Draw entity profile picture if single entity selected
        self._draw_entity_profile(screen, game_state, y_pos)
    
    def _draw_entity_profile(self, screen, game_state, hud_y_pos):
        """Draw 50x50 profile picture of single selected entity in lower left"""
        # Check if exactly one entity is selected
        selected_sheep = [s for s in game_state.sheep_list if s.selected]
        selected_humans = [h for h in game_state.human_list if h.selected]
        total_selected = len(selected_sheep) + len(selected_humans)
        
        if total_selected != 1:
            return  # Only show for single selection
        
        # Profile picture position in lower left
        profile_size = 50
        profile_x = 10
        profile_y = hud_y_pos + (self.bar_height - profile_size) // 2
        
        # Small font for name display
        name_font = pygame.font.Font(None, 16)
        
        # Draw name to the right of profile picture, near top of HUD (for humans only, sheep don't have names)
        entity_name = None
        if selected_humans:
            entity_name = selected_humans[0].name
        
        if entity_name:
            name_surface = name_font.render(entity_name, True, BLACK)
            name_x = profile_x + profile_size + 10  # Position to the right of profile picture
            name_y = hud_y_pos + 5  # Near the top of the lower HUD
            screen.blit(name_surface, (name_x, name_y))
            
            # Draw happiness below the name
            human = selected_humans[0]
            happiness_text = f"H:{human.get_effective_happiness()}"
            happiness_surface = name_font.render(happiness_text, True, BLACK)
            happiness_y = name_y + name_surface.get_height() + 3  # Below the name
            screen.blit(happiness_surface, (name_x, happiness_y))
            
            # Draw job below happiness
            job_name = human.job if human.job else "unemployed"
            # Capitalize first letter for display
            job_display = job_name.capitalize() if job_name else "Unemployed"
            job_surface = name_font.render(job_display, True, BLACK)
            job_y = happiness_y + happiness_surface.get_height() + 3  # Below happiness
            screen.blit(job_surface, (name_x, job_y))
        
        # Draw border
        pygame.draw.rect(screen, BLACK, (profile_x - 2, profile_y - 2, profile_size + 4, profile_size + 4), 2)
        
        # Draw based on entity type
        if selected_sheep:
            # Sheep: filled white oval with 1px border in 50x50 box
            # Draw oval (wider than tall)
            oval_width = 40
            oval_height = 25
            oval_x = profile_x + (profile_size - oval_width) // 2
            oval_y = profile_y + (profile_size - oval_height) // 2
            # Draw filled white oval
            pygame.draw.ellipse(screen, WHITE, (oval_x, oval_y, oval_width, oval_height))
            # Draw 1px border around it
            pygame.draw.ellipse(screen, BLACK, (oval_x, oval_y, oval_width, oval_height), 1)
        elif selected_humans:
            human = selected_humans[0]
            if human.gender == "male":
                # Male human: 50x50 unfilled blue square
                square_size = profile_size - 4  # Slightly smaller to fit in border
                square_x = profile_x + (profile_size - square_size) // 2
                square_y = profile_y + (profile_size - square_size) // 2
                pygame.draw.rect(screen, BLUE, (square_x, square_y, square_size, square_size), 3)
            else:
                # Female human: pink unfilled circle that fits within 50x50
                center_x = profile_x + profile_size // 2
                center_y = profile_y + profile_size // 2
                radius = profile_size // 2 - 2  # Slightly smaller to fit in border
                pygame.draw.circle(screen, PINK, (center_x, center_y), radius, 3)

