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
            
            # Draw relationship status below job
            relationship_display = human.relationship_status.capitalize()
            relationship_surface = name_font.render(relationship_display, True, BLACK)
            relationship_y = job_y + job_surface.get_height() + 3  # Below job
            screen.blit(relationship_surface, (name_x, relationship_y))
            
            # Draw family tree square to the right of stats
            tree_square_x = name_x + max(name_surface.get_width(), happiness_surface.get_width(), 
                                         job_surface.get_width(), relationship_surface.get_width()) + 20
            tree_square_y = profile_y
            tree_square_size = profile_size
            
            # Store square position for click detection
            game_state.family_tree_square_rect = pygame.Rect(tree_square_x, tree_square_y, tree_square_size, tree_square_size)
            
            # Draw grey filled square
            pygame.draw.rect(screen, GRAY, (tree_square_x, tree_square_y, tree_square_size, tree_square_size))
            pygame.draw.rect(screen, BLACK, (tree_square_x, tree_square_y, tree_square_size, tree_square_size), 2)
            
            # Draw hierarchical family tree design inside the square
            self._draw_family_tree_design(screen, tree_square_x, tree_square_y, tree_square_size)
        
        # Draw border
        pygame.draw.rect(screen, BLACK, (profile_x - 2, profile_y - 2, profile_size + 4, profile_size + 4), 2)
        
        # Store profile picture rect for click detection (only for humans)
        if selected_humans:
            game_state.profile_picture_rect = pygame.Rect(profile_x, profile_y, profile_size, profile_size)
        
        # Draw based on entity type
        if selected_sheep:
            sheep = selected_sheep[0]
            # Draw sheep stats to the right of profile picture
            sheep_label_surface = name_font.render("Sheep", True, BLACK)
            sheep_label_x = profile_x + profile_size + 10
            sheep_label_y = hud_y_pos + 5
            screen.blit(sheep_label_surface, (sheep_label_x, sheep_label_y))
            
            # Draw gender below "Sheep"
            gender_display = sheep.gender.capitalize()
            gender_surface = name_font.render(gender_display, True, BLACK)
            gender_y = sheep_label_y + sheep_label_surface.get_height() + 3
            screen.blit(gender_surface, (sheep_label_x, gender_y))
            
            # Draw sheep profile picture
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
    
    def _draw_family_tree_design(self, screen, x, y, size):
        """Draw a hierarchical family tree design with lines and branches"""
        # Use a darker color for the tree lines
        tree_color = (80, 80, 80)  # Dark grey for tree lines
        line_width = 2
        
        # Calculate positions for the tree nodes (circles) and connecting lines
        # This will be a simple 3-level family tree design
        
        # Bottom level (current person) - center bottom
        bottom_x = x + size // 2
        bottom_y = y + size - 8
        
        # Middle level (parents) - left and right of center
        left_parent_x = x + size // 3
        left_parent_y = y + size // 2 + 5
        right_parent_x = x + 2 * size // 3
        right_parent_y = y + size // 2 + 5
        
        # Top level (grandparents) - four positions
        top_left_x = x + size // 4
        top_left_y = y + 8
        top_left_mid_x = x + size // 2 - 5
        top_left_mid_y = y + 8
        top_right_mid_x = x + size // 2 + 5
        top_right_mid_y = y + 8
        top_right_x = x + 3 * size // 4
        top_right_y = y + 8
        
        # Draw connecting lines (branches)
        # From top to middle (grandparents to parents)
        pygame.draw.line(screen, tree_color, (top_left_x, top_left_y), (left_parent_x, left_parent_y), line_width)
        pygame.draw.line(screen, tree_color, (top_left_mid_x, top_left_mid_y), (left_parent_x, left_parent_y), line_width)
        pygame.draw.line(screen, tree_color, (top_right_mid_x, top_right_mid_y), (right_parent_x, right_parent_y), line_width)
        pygame.draw.line(screen, tree_color, (top_right_x, top_right_y), (right_parent_x, right_parent_y), line_width)
        
        # Horizontal line connecting grandparents on each side
        pygame.draw.line(screen, tree_color, (top_left_x, top_left_y), (top_left_mid_x, top_left_mid_y), line_width)
        pygame.draw.line(screen, tree_color, (top_right_mid_x, top_right_mid_y), (top_right_x, top_right_y), line_width)
        
        # From middle to bottom (parents to current person)
        pygame.draw.line(screen, tree_color, (left_parent_x, left_parent_y), (bottom_x, bottom_y), line_width)
        pygame.draw.line(screen, tree_color, (right_parent_x, right_parent_y), (bottom_x, bottom_y), line_width)
        
        # Draw nodes (small circles representing people in the tree)
        node_radius = 3
        
        # Top level nodes (grandparents)
        pygame.draw.circle(screen, BLACK, (top_left_x, top_left_y), node_radius)
        pygame.draw.circle(screen, BLACK, (top_left_mid_x, top_left_mid_y), node_radius)
        pygame.draw.circle(screen, BLACK, (top_right_mid_x, top_right_mid_y), node_radius)
        pygame.draw.circle(screen, BLACK, (top_right_x, top_right_y), node_radius)
        
        # Middle level nodes (parents)
        pygame.draw.circle(screen, BLACK, (left_parent_x, left_parent_y), node_radius)
        pygame.draw.circle(screen, BLACK, (right_parent_x, right_parent_y), node_radius)
        
        # Bottom level node (current person) - slightly larger
        pygame.draw.circle(screen, BLACK, (bottom_x, bottom_y), node_radius + 1)
    
    def _draw_family_tree_dialogue(self, screen, game_state):
        """Draw the family tree dialogue box"""
        from constants import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Dialogue box dimensions
        dialog_width = 500
        dialog_height = 600
        dialog_x = game_state.family_tree_dialogue_x
        dialog_y = game_state.family_tree_dialogue_y
        
        # Clamp to screen bounds
        dialog_x = max(0, min(dialog_x, SCREEN_WIDTH - dialog_width))
        dialog_y = max(HUD_TOP_HEIGHT, min(dialog_y, SCREEN_HEIGHT - HUD_BOTTOM_HEIGHT - dialog_height))
        
        # Update position in game state
        game_state.family_tree_dialogue_x = dialog_x
        game_state.family_tree_dialogue_y = dialog_y
        
        # Draw grey filled rectangle
        pygame.draw.rect(screen, GRAY, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, BLACK, (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Draw title "Family Tree"
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render("Family Tree", True, BLACK)
        title_x = dialog_x + 10
        title_y = dialog_y + 8
        screen.blit(title_text, (title_x, title_y))
        
        # Draw close button (X) in top right corner
        close_button_size = 20
        close_button_x = dialog_x + dialog_width - close_button_size - 5
        close_button_y = dialog_y + 5
        
        # Draw close button background
        pygame.draw.rect(screen, WHITE, (close_button_x, close_button_y, close_button_size, close_button_size))
        pygame.draw.rect(screen, BLACK, (close_button_x, close_button_y, close_button_size, close_button_size), 1)
        
        # Draw X (two diagonal lines)
        line_margin = 5
        pygame.draw.line(screen, BLACK, 
                         (close_button_x + line_margin, close_button_y + line_margin),
                         (close_button_x + close_button_size - line_margin, close_button_y + close_button_size - line_margin), 2)
        pygame.draw.line(screen, BLACK,
                         (close_button_x + close_button_size - line_margin, close_button_y + line_margin),
                         (close_button_x + line_margin, close_button_y + close_button_size - line_margin), 2)
        
        # Draw horizontal bar for dragging (same width as close button, positioned left of it)
        drag_bar_width = close_button_size
        drag_bar_height = close_button_size
        drag_bar_x = close_button_x - drag_bar_width - 5  # 5 pixels gap between bar and close button
        drag_bar_y = close_button_y
        
        # Draw drag bar background (slightly darker grey to be visible)
        drag_bar_color = (160, 160, 160)  # Slightly darker than GRAY
        pygame.draw.rect(screen, drag_bar_color, (drag_bar_x, drag_bar_y, drag_bar_width, drag_bar_height))
        pygame.draw.rect(screen, BLACK, (drag_bar_x, drag_bar_y, drag_bar_width, drag_bar_height), 1)
        
        # Draw three horizontal lines to indicate it's draggable
        line_spacing = drag_bar_height // 4
        for i in range(3):
            line_y = drag_bar_y + line_spacing * (i + 1)
            pygame.draw.line(screen, BLACK, 
                           (drag_bar_x + 5, line_y), 
                           (drag_bar_x + drag_bar_width - 5, line_y), 1)
        
        # Store close button, drag bar, and dialog rect for click detection
        game_state.family_tree_dialogue_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        game_state.family_tree_dialogue_close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
        game_state.family_tree_dialogue_drag_bar_rect = pygame.Rect(drag_bar_x, drag_bar_y, drag_bar_width, drag_bar_height)
    
    def _draw_profile_info_dialogue(self, screen, game_state):
        """Draw the profile info dialogue box (same design as family tree dialogue)"""
        from constants import SCREEN_WIDTH, SCREEN_HEIGHT
        
        # Dialogue box dimensions (same as family tree dialogue)
        dialog_width = 500
        dialog_height = 600
        dialog_x = game_state.profile_info_dialogue_x
        dialog_y = game_state.profile_info_dialogue_y
        
        # Clamp to screen bounds
        dialog_x = max(0, min(dialog_x, SCREEN_WIDTH - dialog_width))
        dialog_y = max(HUD_TOP_HEIGHT, min(dialog_y, SCREEN_HEIGHT - HUD_BOTTOM_HEIGHT - dialog_height))
        
        # Update position in game state
        game_state.profile_info_dialogue_x = dialog_x
        game_state.profile_info_dialogue_y = dialog_y
        
        # Draw grey filled rectangle
        pygame.draw.rect(screen, GRAY, (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, BLACK, (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Draw title "Character Profile"
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render("Character Profile", True, BLACK)
        title_x = dialog_x + 10
        title_y = dialog_y + 8
        screen.blit(title_text, (title_x, title_y))
        
        # Draw close button (X) in top right corner
        close_button_size = 20
        close_button_x = dialog_x + dialog_width - close_button_size - 5
        close_button_y = dialog_y + 5
        
        # Draw close button background
        pygame.draw.rect(screen, WHITE, (close_button_x, close_button_y, close_button_size, close_button_size))
        pygame.draw.rect(screen, BLACK, (close_button_x, close_button_y, close_button_size, close_button_size), 1)
        
        # Draw X (two diagonal lines)
        line_margin = 5
        pygame.draw.line(screen, BLACK, 
                         (close_button_x + line_margin, close_button_y + line_margin),
                         (close_button_x + close_button_size - line_margin, close_button_y + close_button_size - line_margin), 2)
        pygame.draw.line(screen, BLACK,
                         (close_button_x + close_button_size - line_margin, close_button_y + line_margin),
                         (close_button_x + line_margin, close_button_y + close_button_size - line_margin), 2)
        
        # Draw horizontal bar for dragging (same width as close button, positioned left of it)
        drag_bar_width = close_button_size
        drag_bar_height = close_button_size
        drag_bar_x = close_button_x - drag_bar_width - 5  # 5 pixels gap between bar and close button
        drag_bar_y = close_button_y
        
        # Draw drag bar background (slightly darker grey to be visible)
        drag_bar_color = (160, 160, 160)  # Slightly darker than GRAY
        pygame.draw.rect(screen, drag_bar_color, (drag_bar_x, drag_bar_y, drag_bar_width, drag_bar_height))
        pygame.draw.rect(screen, BLACK, (drag_bar_x, drag_bar_y, drag_bar_width, drag_bar_height), 1)
        
        # Draw three horizontal lines to indicate it's draggable
        line_spacing = drag_bar_height // 4
        for i in range(3):
            line_y = drag_bar_y + line_spacing * (i + 1)
            pygame.draw.line(screen, BLACK, 
                           (drag_bar_x + 5, line_y), 
                           (drag_bar_x + drag_bar_width - 5, line_y), 1)
        
        # Store close button, drag bar, and dialog rect for click detection
        game_state.profile_info_dialogue_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        game_state.profile_info_dialogue_close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
        game_state.profile_info_dialogue_drag_bar_rect = pygame.Rect(drag_bar_x, drag_bar_y, drag_bar_width, drag_bar_height)

