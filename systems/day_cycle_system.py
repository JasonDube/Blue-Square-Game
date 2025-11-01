"""
Day/night cycle system
"""
import random
from constants import *


class DayCycleSystem:
    """Manages day/night progression and time tracking"""
    
    def __init__(self):
        self.current_day = 1
        self.elapsed_time = 0.0
        self.day_duration = DAY_DURATION
    
    def update(self, dt, game_state):
        """Update time and handle day transitions"""
        self.elapsed_time += dt
        
        if self.elapsed_time >= self.day_duration:
            self._transition_to_new_day(game_state)
    
    def _transition_to_new_day(self, game_state):
        """Handle day transition logic"""
        self.elapsed_time = 0.0
        self.current_day += 1
        game_state.current_day = self.current_day
        
        # Handle reproduction
        from systems.reproduction_system import ReproductionSystem
        ReproductionSystem.process_reproduction(game_state)
        
        # Handle grass regrowth
        self._regrow_grass(game_state.eaten_pixels)
    
    def _regrow_grass(self, eaten_pixels):
        """Regrow 10-20% of eaten grass"""
        if len(eaten_pixels) == 0:
            return
        
        regrowth_percentage = random.uniform(GRASS_REGROWTH_MIN, GRASS_REGROWTH_MAX)
        pixels_to_regrow = max(1, int(len(eaten_pixels) * regrowth_percentage))
        
        # Convert to list, sample random pixels, remove from eaten set
        eaten_list = list(eaten_pixels)
        pixels_to_remove = random.sample(eaten_list, min(pixels_to_regrow, len(eaten_list)))
        for pixel in pixels_to_remove:
            eaten_pixels.discard(pixel)
    
    def get_time_of_day(self):
        """Get current time in 12-hour format"""
        day_progress = self.elapsed_time / self.day_duration
        hours_into_day = (day_progress * 24) % 24
        current_hour_24 = (START_HOUR + hours_into_day) % 24
        current_minute = int((hours_into_day % 1) * 60)
        
        # Convert to 12-hour format
        if current_hour_24 == 0:
            display_hour = 12
            am_pm = "AM"
        elif current_hour_24 < 12:
            display_hour = int(current_hour_24)
            am_pm = "AM"
        elif current_hour_24 == 12:
            display_hour = 12
            am_pm = "PM"
        else:
            display_hour = int(current_hour_24 - 12)
            am_pm = "PM"
        
        return display_hour, current_minute, am_pm
