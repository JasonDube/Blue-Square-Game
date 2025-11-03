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
        self.is_transitioning = False
        self.day_has_incremented = False  # Track if day has been incremented for current transition
    
    def update(self, dt, game_state):
        """Update time and handle day transitions"""
        self.elapsed_time += dt
        
        # Check if we're in the dusk period (last DUSK_FADE_DURATION seconds of day)
        time_until_day_end = self.day_duration - self.elapsed_time
        if time_until_day_end <= DUSK_FADE_DURATION and time_until_day_end > 0:
            # Entering dusk - mark transition start
            if not self.is_transitioning:
                self.is_transitioning = True
                self.day_has_incremented = False
        
        # Handle day transition at end of day (exactly at day_duration)
        if self.elapsed_time >= self.day_duration and not self.day_has_incremented:
            self._transition_to_new_day(game_state)
        
        # Check if we've completed the full transition cycle
        if self.is_transitioning:
            transition_elapsed = self.elapsed_time - (self.day_duration - DUSK_FADE_DURATION)
            # Dusk fade (0-DUSK_FADE_DURATION) + wait (DUSK_FADE_DURATION-2*DUSK_FADE_DURATION) + dawn fade (2*DUSK_FADE_DURATION-3*DUSK_FADE_DURATION) = 3*DUSK_FADE_DURATION seconds total (halved)
            if transition_elapsed >= DUSK_FADE_DURATION * 3:
                # Transition complete - reset for new day
                self.is_transitioning = False
                self.day_has_incremented = False
                self.elapsed_time = 0.0
    
    def _transition_to_new_day(self, game_state):
        """Handle day transition logic"""
        # Increment day at end of day duration (before wait period)
        # This happens once per transition
        if not self.day_has_incremented:
            self.current_day += 1
            game_state.current_day = self.current_day
            self.day_has_incremented = True
            
            # Handle reproduction
            from systems.reproduction_system import ReproductionSystem
            ReproductionSystem.process_reproduction(game_state)
            
            # Handle grass regrowth
            self._regrow_grass(game_state.eaten_pixels)
            
            # Handle wool regrowth (every day/night cycle)
            self._regrow_wool(game_state)
        
        # Note: elapsed_time continues past day_duration during transition
        # It will be reset after the full transition completes (in update method)
    
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
        # During transition, clamp elapsed_time to day_duration for time calculation
        effective_time = min(self.elapsed_time, self.day_duration)
        day_progress = effective_time / self.day_duration
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
    
    def get_darkness_overlay_alpha(self):
        """Calculate alpha value for darkness overlay during dusk/dawn transition"""
        # Calculate time remaining in day
        time_until_day_end = self.day_duration - self.elapsed_time
        
        # Last DUSK_FADE_DURATION seconds: fade to dark (alpha 0 to 255)
        if time_until_day_end <= DUSK_FADE_DURATION and time_until_day_end > 0:
            # Fade to dark during dusk
            fade_progress = 1.0 - (time_until_day_end / DUSK_FADE_DURATION)
            return int(fade_progress * 200)  # Max alpha 200 (not completely black)
        
        # After day ends, handle transition phases
        if self.elapsed_time >= self.day_duration:
            transition_elapsed = self.elapsed_time - (self.day_duration - DUSK_FADE_DURATION)
            
            # Phase 1: Dusk fade (0 to DUSK_FADE_DURATION) - already handled above
            # Phase 2: Wait in dark (DUSK_FADE_DURATION to DUSK_FADE_DURATION * 2)
            if DUSK_FADE_DURATION <= transition_elapsed < DUSK_FADE_DURATION * 2:
                return 200  # Full dark
            
            # Phase 3: Dawn fade (DUSK_FADE_DURATION * 2 to DUSK_FADE_DURATION * 3)
            if DUSK_FADE_DURATION * 2 <= transition_elapsed < DUSK_FADE_DURATION * 3:
                dawn_progress = (transition_elapsed - DUSK_FADE_DURATION * 2) / DUSK_FADE_DURATION
                return int(200 * (1.0 - dawn_progress))  # Fade from dark to light
        
        return 0  # No overlay needed
    
    def _regrow_wool(self, game_state):
        """Regrow wool on sheep after each day/night cycle (1 day)"""
        for sheep in game_state.sheep_list:
            if not sheep.has_wool and sheep.wool_regrowth_day is not None:
                # Regrow after 1 day (each day/night cycle)
                days_since_sheared = self.current_day - sheep.wool_regrowth_day
                if days_since_sheared >= 1:
                    sheep.has_wool = True
                    sheep.wool_regrowth_day = None
