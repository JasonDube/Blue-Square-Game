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
        # Draw dark grey bar background
        from constants import DARK_GREY
        pygame.draw.rect(screen, DARK_GREY, (0, 0, SCREEN_WIDTH, self.bar_height))
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, self.bar_height), 1)
        
        # Draw sheep counter on left
        self._draw_sheep_counter(screen, game_state)
        
        # Draw human counters after sheep
        self._draw_human_counters(screen, game_state)
        
        # Draw average happiness (heart icon)
        self._draw_average_happiness(screen, game_state)
        
        # Draw resources (logs, stone, etc.) in middle-left (with tooltips)
        self._draw_resources(screen, resource_system)
        
        # Draw day/time on right
        self._draw_day_time(screen, day_cycle)
        
        # Draw tooltips for resource icons if mouse is hovering
        self._draw_resource_tooltips(screen, resource_system)
    
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
        
        # Store icon position for tooltip detection
        sheep_icon_rect = pygame.Rect(sheep_icon_x, sheep_icon_y, 6 + count_surface.get_width() + 5, 4)
        if not hasattr(self, '_icon_rects'):
            self._icon_rects = {}
        self._icon_rects['sheep'] = (sheep_icon_rect, "Sheep")
    
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
        
        # Store male icon position for tooltip detection
        male_icon_rect = pygame.Rect(male_icon_x, male_icon_y, icon_size + male_count_surface.get_width() + 5, icon_size)
        if not hasattr(self, '_icon_rects'):
            self._icon_rects = {}
        self._icon_rects['male'] = (male_icon_rect, "Males")
        
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
        
        # Store female icon position for tooltip detection
        female_icon_rect = pygame.Rect(female_icon_x, female_icon_y, icon_size + female_count_surface.get_width() + 5, icon_size)
        self._icon_rects['female'] = (female_icon_rect, "Females")
        
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
        
        # Store happiness icon position for tooltip detection
        happiness_icon_rect = pygame.Rect(heart_x, heart_y - heart_size // 2, heart_size + happiness_surface.get_width() + 5, heart_size)
        if not hasattr(self, '_icon_rects'):
            self._icon_rects = {}
        self._icon_rects['happiness'] = (happiness_icon_rect, "Happiness")
        
        # Update end position for resources
        self._happiness_end_x = happiness_x + happiness_surface.get_width() + 15
    
    def _draw_resources(self, screen, resource_system):
        """Draw resource icons and counts"""
        from systems.resource_system import ResourceType, ResourceVisualizer
        
        # Initialize resource icon rects dictionary
        self._resource_icon_rects = {}
        
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
            (ResourceType.MEAT, "Meat"),
            (ResourceType.BARLEY, "Barley"),
            (ResourceType.FLOUR, "Flour"),
            (ResourceType.MALT, "Malt")
        ]
        
        for resource_type, label in resources_to_show:
            count = resource_system.get_resource_count(resource_type)
            
            # Always show all resources (even if 0)
            visual = ResourceVisualizer.get_resource_visual(resource_type)
            
            # Draw resource icon (scaled down to fit in HUD)
            icon_y = (self.bar_height - visual['height']) // 2
            
            # Special case: Draw malt as a barrel icon (like in the mill)
            if resource_type == ResourceType.MALT:
                # Draw barrel icon with horizontal bands
                barrel_x = current_x
                barrel_y = icon_y
                barrel_width = visual['width']
                barrel_height = visual['height']
                # Draw filled barrel rectangle
                pygame.draw.rect(screen, visual['color'], 
                               (barrel_x, barrel_y, barrel_width, barrel_height))
                # Draw barrel outline
                pygame.draw.rect(screen, BLACK, (barrel_x, barrel_y, barrel_width, barrel_height), 1)
                # Draw top horizontal line (barrel band)
                pygame.draw.line(screen, BLACK, (barrel_x, barrel_y + 1), 
                               (barrel_x + barrel_width, barrel_y + 1), 1)
                # Draw bottom horizontal line (barrel band)
                pygame.draw.line(screen, BLACK, (barrel_x, barrel_y + barrel_height - 1), 
                               (barrel_x + barrel_width, barrel_y + barrel_height - 1), 1)
            elif visual['shape'] == 'rect':
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
            
            # Store icon position for tooltip detection
            icon_rect = pygame.Rect(current_x, icon_y, visual['width'] + count_surface.get_width() + 5, visual['height'])
            if not hasattr(self, '_icon_rects'):
                self._icon_rects = {}
            self._icon_rects[resource_type] = (icon_rect, label)
            
            # Move to next resource position
            current_x += visual['width'] + count_surface.get_width() + 20
    
    def _draw_day_time(self, screen, day_cycle):
        """Draw year number and current time"""
        display_hour, current_minute, am_pm = day_cycle.get_time_of_day()
        day_text = f"Year {day_cycle.current_day}: {display_hour}:{current_minute:02d} {am_pm}"
        
        day_surface = self.font.render(day_text, True, WHITE)
        day_rect = day_surface.get_rect()
        day_x = SCREEN_WIDTH - day_rect.width - 10
        screen.blit(day_surface, (day_x, self.bar_height // 2 - day_rect.height // 2))
    
    def _draw_resource_tooltips(self, screen, resource_system):
        """Draw tooltips when mouse hovers over any HUD icon (resources, sheep, humans, happiness)"""
        if not hasattr(self, '_icon_rects'):
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Check if mouse is over any icon (resources, sheep, humans, happiness)
        for icon_key, (icon_rect, label) in self._icon_rects.items():
            if icon_rect.collidepoint(mouse_x, mouse_y):
                # Draw tooltip above the icon
                tooltip_font = pygame.font.Font(None, 20)
                tooltip_text = tooltip_font.render(label, True, WHITE)
                tooltip_bg_width = tooltip_text.get_width() + 10
                tooltip_bg_height = tooltip_text.get_height() + 6
                tooltip_x = mouse_x
                tooltip_y = mouse_y - tooltip_bg_height - 5
                
                # Clamp tooltip to screen bounds
                if tooltip_x + tooltip_bg_width > SCREEN_WIDTH:
                    tooltip_x = SCREEN_WIDTH - tooltip_bg_width
                if tooltip_y < 0:
                    tooltip_y = mouse_y + 20
                
                # Draw tooltip background
                pygame.draw.rect(screen, BLACK, 
                               (tooltip_x, tooltip_y, tooltip_bg_width, tooltip_bg_height))
                pygame.draw.rect(screen, WHITE, 
                               (tooltip_x, tooltip_y, tooltip_bg_width, tooltip_bg_height), 1)
                
                # Draw tooltip text
                screen.blit(tooltip_text, (tooltip_x + 5, tooltip_y + 3))
                break  # Only show one tooltip at a time
    
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
