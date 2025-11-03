"""
BarleyFarm entity - building for growing barley
"""
import pygame
from constants import *


class BarleyFarm:
    """Barley farm building where farmers work"""
    
    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.rotation = rotation  # 0 = top, 1 = right, 2 = bottom, 3 = left
        # For rotations 1 and 3 (90/270 degrees), swap width and height
        if rotation == 1 or rotation == 3:
            self.width = BARLEYFARM_HEIGHT
            self.height = BARLEYFARM_WIDTH
        else:
            self.width = BARLEYFARM_WIDTH
            self.height = BARLEYFARM_HEIGHT
        self.collision_enabled = True
        
        # Crop growth tracking
        self.planted_day = None  # Day when crops were planted (None if not planted)
        self.has_crops = False  # Whether crops are ready to harvest
        self.crops_ready_day = None
        
        # Farm plot system (10x10 brown squares where farmer has worked)
        self.plot_size = 10
        self.worked_plots = set()  # Set of (plot_x, plot_y) tuples for plots that have been worked (dirt)
        self.barley_plots = set()  # Set of (plot_x, plot_y) tuples for plots with barley squares (3x3 dark brown)
        self._initialize_plots()
    
    def is_point_inside(self, px, py):
        """Check if a point is inside the farm boundaries"""
        return (self.x < px < self.x + self.width and 
                self.y < py < self.y + self.height)
    
    def check_collision_player(self, px, py):
        """Check if player collides with the farm"""
        if not self.collision_enabled:
            return False
        
        player_rect = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        farm_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(farm_rect)
    
    def check_collision_sheep(self, sx, sy, sw, sh):
        """Check if sheep collides with the farm"""
        if not self.collision_enabled:
            return False
        
        sheep_rect = pygame.Rect(sx, sy, sw, sh)
        farm_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return sheep_rect.colliderect(farm_rect)
    
    def plant_crops(self, current_day):
        """Plant crops on the farm"""
        if self.planted_day is None:
            self.planted_day = current_day
            self.has_crops = False
            self.crops_ready_day = None
    
    def update_crops(self, current_day):
        """Update crop growth - crops ready after 1 day (testing: was 3 days)"""
        if self.planted_day is not None and not self.has_crops:
            days_since_planted = current_day - self.planted_day
            if days_since_planted >= 1:  # Changed from 3 to 1 for testing
                self.has_crops = True
                self.crops_ready_day = current_day
    
    def _initialize_plots(self):
        """Initialize the grid of plots in the farm - exactly 24 plots (8x3)"""
        # Target: 24 plots total (8 columns x 3 rows)
        self.plots_x = 8
        self.plots_y = 3
        
        # Calculate starting position to center the plots
        total_plot_width = self.plots_x * self.plot_size
        total_plot_height = self.plots_y * self.plot_size
        margin_x = (self.width - total_plot_width) / 2
        margin_y = (self.height - total_plot_height) / 2
        
        self.plot_start_x = self.x + margin_x
        self.plot_start_y = self.y + margin_y
    
    def get_plot_position(self, plot_x, plot_y):
        """Get the world position of a plot (center of plot)"""
        plot_world_x = self.plot_start_x + (plot_x * self.plot_size) + (self.plot_size / 2)
        plot_world_y = self.plot_start_y + (plot_y * self.plot_size) + (self.plot_size / 2)
        return plot_world_x, plot_world_y
    
    def get_plot_at_position(self, x, y):
        """Get the plot coordinates at a given world position"""
        rel_x = x - self.plot_start_x
        rel_y = y - self.plot_start_y
        plot_x = int(rel_x // self.plot_size)
        plot_y = int(rel_y // self.plot_size)
        
        # Clamp to valid range
        plot_x = max(0, min(plot_x, self.plots_x - 1))
        plot_y = max(0, min(plot_y, self.plots_y - 1))
        
        return plot_x, plot_y
    
    def is_plot_worked(self, plot_x, plot_y):
        """Check if a plot has been worked"""
        return (plot_x, plot_y) in self.worked_plots
    
    def work_plot(self, plot_x, plot_y):
        """Mark a plot as worked (add 10x10 brown dirt square and 3x3 dark brown barley square)"""
        if 0 <= plot_x < self.plots_x and 0 <= plot_y < self.plots_y:
            self.worked_plots.add((plot_x, plot_y))
            # Also add a barley square in the middle of the plot
            self.barley_plots.add((plot_x, plot_y))
            # Check if all plots are worked - if so, plant crops
            total_plots = self.plots_x * self.plots_y
            if len(self.worked_plots) >= total_plots and self.planted_day is None:
                # All plots worked, ready to plant (will be planted when farmer checks)
                pass
    
    def has_barley_at_plot(self, plot_x, plot_y):
        """Check if a plot has barley that can be harvested"""
        return (plot_x, plot_y) in self.barley_plots and self.has_crops
    
    def harvest_one_barley(self, plot_x, plot_y):
        """Harvest one unit of barley from a specific plot"""
        if (plot_x, plot_y) in self.barley_plots:
            self.barley_plots.remove((plot_x, plot_y))
            return True
        return False
    
    def has_any_barley_to_harvest(self):
        """Check if there are any plots with barley ready to harvest"""
        return len(self.barley_plots) > 0 and self.has_crops
    
    def harvest(self):
        """Harvest all crops and reset (deprecated - use harvest_one_barley instead)"""
        if self.has_crops:
            self.planted_day = None
            self.has_crops = False
            self.crops_ready_day = None
            self.worked_plots.clear()  # Clear worked plots so farmer can work again
            self.barley_plots.clear()  # Clear barley plots
            return True
        return False
    
    def is_fully_harvested(self):
        """Check if all barley has been harvested"""
        return self.has_crops and len(self.barley_plots) == 0
    
    def reset_after_harvest(self):
        """Reset farm after all barley is harvested"""
        if self.is_fully_harvested():
            self.planted_day = None
            self.has_crops = False
            self.crops_ready_day = None
            self.worked_plots.clear()  # Clear worked plots so farmer can work again
            self.barley_plots.clear()  # Clear barley plots
    
    def draw(self, screen, preview=False):
        """Draw the barley farm"""
        if preview:
            # Draw preview (handled by build mode)
            return
        
        # Draw unfilled rectangle (black outline)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 1)
        
        # Draw worked plots (10x10 filled brown dirt squares)
        for plot_x, plot_y in self.worked_plots:
            plot_world_x = self.plot_start_x + (plot_x * self.plot_size)
            plot_world_y = self.plot_start_y + (plot_y * self.plot_size)
            # Draw filled brown square (10x10) - dirt plot
            pygame.draw.rect(screen, BROWN, (plot_world_x, plot_world_y, self.plot_size, self.plot_size))
        
        # Draw barley squares (3x3 dark brown) in the middle of plots that have barley
        from constants import DARK_BROWN
        barley_size = 3
        for plot_x, plot_y in self.barley_plots:
            plot_world_x = self.plot_start_x + (plot_x * self.plot_size)
            plot_world_y = self.plot_start_y + (plot_y * self.plot_size)
            # Draw 3x3 dark brown square in the center of the 10x10 plot
            barley_offset = (self.plot_size - barley_size) / 2
            barley_x = plot_world_x + barley_offset
            barley_y = plot_world_y + barley_offset
            pygame.draw.rect(screen, DARK_BROWN, (barley_x, barley_y, barley_size, barley_size))

