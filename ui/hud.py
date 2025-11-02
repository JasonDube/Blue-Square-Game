"""
HUD (Heads-Up Display) component
"""
import pygame
from constants import *


class HUD:
    """Displays game information like day/time and sheep count"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.bar_height = 25
    
    def draw(self, screen, game_state, day_cycle, resource_system):
        """Draw the HUD bar at top of screen"""
        # Draw black bar background
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, self.bar_height))
        pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, self.bar_height), 1)
        
        # Draw sheep counter on left
        self._draw_sheep_counter(screen, game_state)
        
        # Draw human counters after sheep
        self._draw_human_counters(screen, game_state)
        
        # Draw average happiness (heart icon)
        self._draw_average_happiness(screen, game_state)
        
        # Draw resources (logs, stone, etc.) in middle-left
        self._draw_resources(screen, resource_system)
        
        # Draw day/time on right
        self._draw_day_time(screen, day_cycle)
    
    def _draw_sheep_counter(self, screen, game_state):
        """Draw sheep icon and count"""
        # Draw sheep icon (same size as actual sheep: 6x4)
        sheep_icon_x = 10
        sheep_icon_y = (self.bar_height - 4) // 2
        pygame.draw.ellipse(screen, WHITE, (sheep_icon_x, sheep_icon_y, 6, 4))
        
        # Draw count number
        sheep_count_text = str(len(game_state.sheep_list))
        count_surface = self.font.render(sheep_count_text, True, WHITE)
        count_x = sheep_icon_x + 10
        screen.blit(count_surface, (count_x, self.bar_height // 2 - count_surface.get_height() // 2))
    
    def _draw_human_counters(self, screen, game_state):
        """Draw male and female human counters"""
        # Count humans
        male_count = sum(1 for h in game_state.human_list if h.gender == "male")
        female_count = sum(1 for h in game_state.human_list if h.gender == "female")
        
        # Position after sheep counter (sheep icon + number + spacing)
        start_x = 60
        current_x = start_x
        icon_size = 12  # Size for icons in HUD
        
        # Draw male human counter (blue unfilled square)
        male_icon_x = current_x
        male_icon_y = (self.bar_height - icon_size) // 2
        pygame.draw.rect(screen, BLUE, (male_icon_x, male_icon_y, icon_size, icon_size), 2)  # Unfilled
        
        male_count_text = str(male_count)
        male_count_surface = self.font.render(male_count_text, True, WHITE)
        male_count_x = male_icon_x + icon_size + 5
        screen.blit(male_count_surface, (male_count_x, self.bar_height // 2 - male_count_surface.get_height() // 2))
        
        # Move to next position
        current_x = male_count_x + male_count_surface.get_width() + 15
        
        # Draw female human counter (pink unfilled circle)
        female_icon_x = current_x
        female_icon_y = (self.bar_height - icon_size) // 2
        radius = icon_size // 2
        pygame.draw.circle(screen, PINK, (female_icon_x + radius, female_icon_y + radius), radius, 2)  # Unfilled
        
        female_count_text = str(female_count)
        female_count_surface = self.font.render(female_count_text, True, WHITE)
        female_count_x = female_icon_x + icon_size + 5
        screen.blit(female_count_surface, (female_count_x, self.bar_height // 2 - female_count_surface.get_height() // 2))
        
        # Update start position for next element
        self._human_counters_end_x = female_count_x + female_count_surface.get_width() + 15
    
    def _draw_average_happiness(self, screen, game_state):
        """Draw heart icon with average happiness of all humans"""
        if len(game_state.human_list) == 0:
            self._happiness_end_x = self._human_counters_end_x if hasattr(self, '_human_counters_end_x') else 60
            return
        
        # Calculate average happiness
        total_happiness = sum(h.get_effective_happiness() for h in game_state.human_list)
        avg_happiness = int(total_happiness / len(game_state.human_list))
        
        # Position after human counters
        start_x = self._human_counters_end_x if hasattr(self, '_human_counters_end_x') else 60
        heart_x = start_x
        heart_y = self.bar_height // 2
        heart_size = 12  # Size of heart icon
        
        # Draw simple heart icon (two circles + triangle)
        # Top circles
        radius = heart_size // 4
        pygame.draw.circle(screen, RED, (heart_x + radius, heart_y - radius), radius)
        pygame.draw.circle(screen, RED, (heart_x + heart_size - radius, heart_y - radius), radius)
        # Bottom triangle (inverted)
        points = [
            (heart_x, heart_y - radius),
            (heart_x + heart_size // 2, heart_y + radius),
            (heart_x + heart_size, heart_y - radius)
        ]
        pygame.draw.polygon(screen, RED, points)
        
        # Draw happiness number
        happiness_text = str(avg_happiness)
        happiness_surface = self.font.render(happiness_text, True, WHITE)
        happiness_x = heart_x + heart_size + 5
        screen.blit(happiness_surface, (happiness_x, self.bar_height // 2 - happiness_surface.get_height() // 2))
        
        # Update end position for resources
        self._happiness_end_x = happiness_x + happiness_surface.get_width() + 15
    
    def _draw_resources(self, screen, resource_system):
        """Draw resource icons and counts"""
        from systems.resource_system import ResourceType, ResourceVisualizer
        
        # Start position after human counters/happiness (or sheep counter if no humans method called)
        if hasattr(self, '_happiness_end_x'):
            start_x = self._happiness_end_x
        elif hasattr(self, '_human_counters_end_x'):
            start_x = self._human_counters_end_x
        else:
            start_x = 60
        current_x = start_x
        
        # Resource display order
        resources_to_show = [
            (ResourceType.LOG, "Logs"),
            (ResourceType.STONE, "Stone"),
            (ResourceType.IRON, "Iron"),
            (ResourceType.SALT, "Salt"),
            (ResourceType.WOOL, "Wool"),
            (ResourceType.MEAT, "Meat")
        ]
        
        for resource_type, label in resources_to_show:
            count = resource_system.get_resource_count(resource_type)
            
            # Always show resources (even if 0) for LOG, STONE, IRON, SALT
            if resource_type in [ResourceType.LOG, ResourceType.STONE, ResourceType.IRON, ResourceType.SALT] or count > 0:
                visual = ResourceVisualizer.get_resource_visual(resource_type)
                
                # Draw resource icon (scaled down to fit in HUD)
                icon_y = (self.bar_height - visual['height']) // 2
                
                if visual['shape'] == 'rect':
                    # Draw small rectangle icon
                    pygame.draw.rect(screen, visual['color'], 
                                   (current_x, icon_y, visual['width'], visual['height']))
                elif visual['shape'] == 'circle':
                    radius = visual['width'] // 2
                    pygame.draw.circle(screen, visual['color'], 
                                     (current_x + radius, icon_y + radius), radius)
                
                # Draw count next to icon
                count_text = str(count)
                count_surface = self.font.render(count_text, True, WHITE)
                count_x = current_x + visual['width'] + 5
                screen.blit(count_surface, (count_x, self.bar_height // 2 - count_surface.get_height() // 2))
                
                # Move to next resource position
                current_x += visual['width'] + count_surface.get_width() + 20
    
    def _draw_day_time(self, screen, day_cycle):
        """Draw day number and current time"""
        display_hour, current_minute, am_pm = day_cycle.get_time_of_day()
        day_text = f"Day {day_cycle.current_day}: {display_hour}:{current_minute:02d} {am_pm}"
        
        day_surface = self.font.render(day_text, True, WHITE)
        day_rect = day_surface.get_rect()
        day_x = SCREEN_WIDTH - day_rect.width - 10
        screen.blit(day_surface, (day_x, self.bar_height // 2 - day_rect.height // 2))
    
    def draw_box_selection(self, screen, game_state):
        """Draw box selection rectangle"""
        if not game_state.box_selecting:
            return
        
        rect_x = min(game_state.box_start_x, game_state.box_end_x)
        rect_y = min(game_state.box_start_y, game_state.box_end_y)
        rect_width = abs(game_state.box_end_x - game_state.box_start_x)
        rect_height = abs(game_state.box_end_y - game_state.box_start_y)
        
        pygame.draw.rect(screen, YELLOW, (rect_x, rect_y, rect_width, rect_height), 1)
    
    def draw_debug_herd_boundary(self, screen, game_state):
        """Draw herd boundary in debug mode"""
        if not game_state.debug_mode or len(game_state.sheep_list) == 0:
            return
        
        herd_center_x, herd_center_y = game_state.get_herd_center()
        
        boundary_rect = pygame.Rect(
            herd_center_x - HERD_BOUNDARY_SIZE // 2,
            herd_center_y - HERD_BOUNDARY_SIZE // 2,
            HERD_BOUNDARY_SIZE,
            HERD_BOUNDARY_SIZE
        )
        pygame.draw.rect(screen, YELLOW, boundary_rect, 1)
        
        # Draw center point
        pygame.draw.circle(screen, RED, (int(herd_center_x), int(herd_center_y)), 3)
