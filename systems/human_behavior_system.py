"""
Human behavior system - manages wandering and sleep behaviors for humans
"""
import random
import math
from constants import *
from utils.geometry import distance


class HumanBehaviorSystem:
    """Handles automatic behaviors for humans (wandering, sleep)"""
    
    def __init__(self):
        pass
    
    def update(self, dt, game_state, day_cycle):
        """Update all human behaviors"""
        # Update hut claiming for employed workers
        self._update_hut_claiming(game_state)
        
        # Check if it's dark (darkness overlay active)
        is_dark = day_cycle.get_darkness_overlay_alpha() > 50
        
        for human in game_state.human_list:
            # Handle sleep behavior when dark
            if is_dark:
                if human.state not in ["sleep"]:
                    # Switch to sleep if not already sleeping
                    if human.state in ["wander", "employed"]:
                        human.state = "sleep"
                        human.sleep_target = None  # Will find hut or town hall
                        # Clear wander state
                        human.wander_timer = 0.0
                        human.wander_direction = None
                        human.is_wandering = False
                
                if human.state == "sleep":
                    self._update_sleep(human, dt, game_state)
            else:
                # Not dark - handle normal behaviors
                if human.state == "sleep":
                    # Wake up - return to previous behavior
                    if human.is_employed:
                        human.state = "employed"
                    else:
                        human.state = "wander"
                        human.wander_timer = 0.0
                        human.wander_direction = None
                        human.is_wandering = False
                    human.sleep_target = None
                
                if human.state == "wander":
                    self._update_wander(human, dt, game_state)
    
    def _update_wander(self, human, dt, game_state):
        """Update wandering behavior for unemployed humans"""
        # If we have a target, move towards it
        if human.wander_target_x is not None and human.wander_target_y is not None:
            human_x = human.x + human.size / 2
            human_y = human.y + human.size / 2
            
            dist = distance(human_x, human_y, human.wander_target_x, human.wander_target_y)
            
            if dist < 5:  # Reached target
                # Stop and rest
                human.is_wandering = False
                human.wander_timer = 0.0
                human.wander_duration = 0.0
                human.wander_target_x = None
                human.wander_target_y = None
                # Set random rest time (negative indicates resting)
                rest_time = random.uniform(HUMAN_STOP_MIN_TIME, HUMAN_STOP_MAX_TIME)
                human.wander_timer = -rest_time
            else:
                # Move towards target
                if human.is_wandering:
                    dx = human.wander_target_x - human_x
                    dy = human.wander_target_y - human_y
                    self._apply_wander_movement(human, dx, dy, dist, game_state)
        
        # Check if we're resting (negative timer means resting)
        if human.wander_timer < 0:
            human.wander_timer += dt
            # Check if rest is complete (timer reached 0)
            if human.wander_timer >= 0:
                # Rest complete, start wandering
                human.is_wandering = True
                human.wander_duration = random.uniform(HUMAN_WANDER_MIN_TIME, HUMAN_WANDER_MAX_TIME)
                human.wander_timer = 0.0
                self._choose_wander_target(human, game_state)
        elif human.wander_timer > 0 and human.is_wandering and human.wander_duration > 0:
            # Not resting - increment timer and check if wander duration expired
            human.wander_timer += dt
            if human.wander_timer >= human.wander_duration:
                # Stop and rest
                human.is_wandering = False
                human.wander_target_x = None
                human.wander_target_y = None
                human.wander_duration = 0.0
                rest_time = random.uniform(HUMAN_STOP_MIN_TIME, HUMAN_STOP_MAX_TIME)
                human.wander_timer = -rest_time
        elif human.wander_target_x is None:
            # No target - start wandering immediately if not resting
            if human.wander_timer >= 0:
                human.is_wandering = True
                human.wander_duration = random.uniform(HUMAN_WANDER_MIN_TIME, HUMAN_WANDER_MAX_TIME)
                human.wander_timer = 0.0
                self._choose_wander_target(human, game_state)
            else:
                # Still resting, increment timer
                human.wander_timer += dt
        elif not human.is_wandering:
            # Has target but not wandering - this shouldn't happen, but start wandering
            human.is_wandering = True
            human.wander_duration = random.uniform(HUMAN_WANDER_MIN_TIME, HUMAN_WANDER_MAX_TIME)
            human.wander_timer = 0.0
    
    def _choose_wander_target(self, human, game_state):
        """Choose a random wander target within playable area"""
        # Random position within playable area
        margin = 20
        target_x = random.uniform(margin, SCREEN_WIDTH - margin)
        target_y = random.uniform(PLAYABLE_AREA_TOP + margin, PLAYABLE_AREA_BOTTOM - margin)
        
        human.wander_target_x = target_x
        human.wander_target_y = target_y
    
    def _apply_wander_movement(self, human, dx, dy, dist, game_state):
        """Apply wander movement with collision detection"""
        from utils.geometry import clamp
        
        # Use slower wander speed
        speed = HUMAN_WANDER_SPEED
        dx = (dx / dist) * speed
        dy = (dy / dist) * speed
        
        old_x, old_y = human.x, human.y
        human.x += dx
        human.y += dy
        
        # Keep within playable area bounds
        human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
        human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
        
        # Check collision with structures
        if human._check_structure_collisions(game_state.pen_list, game_state.townhall_list):
            human.x, human.y = old_x, old_y
            # Try to pick a new target
            human.wander_target_x = None
            human.wander_target_y = None
            return
        
        # Check collision with other humans
        other_humans = [h for h in game_state.human_list if h != human]
        for other in other_humans:
            if human.check_human_collision(other):
                # Push away slightly
                push_dx = human.x - other.x
                push_dy = human.y - other.y
                push_dist = distance(human.x, human.y, other.x, other.y)
                if push_dist > 0:
                    push_dx = (push_dx / push_dist) * 2
                    push_dy = (push_dy / push_dist) * 2
                    human.x += push_dx
                    human.y += push_dy
                else:
                    human.x, human.y = old_x, old_y
                break
    
    def _update_hut_claiming(self, game_state):
        """Update hut claiming - first come first serve for employed workers"""
        # First, release huts from unemployed humans
        for human in game_state.human_list:
            if human.home_hut and not human.is_employed:
                # Human became unemployed - release their hut
                human.home_hut.release()
                human.home_hut = None
        
        # Then, claim available huts for employed workers
        for hut in game_state.hut_list:
            if hut.is_available():
                # Find nearest employed worker without a hut
                nearest_human = None
                nearest_dist = float('inf')
                
                hut_center_x = hut.x + hut.size / 2
                hut_center_y = hut.y + hut.size / 2
                
                for human in game_state.human_list:
                    # Only employed workers can claim huts
                    if not human.is_employed:
                        continue
                    
                    # Skip if human already has a hut
                    if human.home_hut is not None:
                        continue
                    
                    human_x = human.x + human.size / 2
                    human_y = human.y + human.size / 2
                    dist = distance(human_x, human_y, hut_center_x, hut_center_y)
                    
                    # Claim if within reasonable distance (50 pixels)
                    if dist < 50 and dist < nearest_dist:
                        nearest_dist = dist
                        nearest_human = human
                
                # Claim the hut for the nearest employed worker
                if nearest_human:
                    hut.claim(nearest_human)
                    nearest_human.home_hut = hut
    
    def _update_sleep(self, human, dt, game_state):
        """Update sleep behavior - move to hut (if owned) or town hall and rest"""
        # Find sleep target if not already assigned
        if human.sleep_target is None:
            # Prefer own hut if available
            if human.home_hut:
                human.sleep_target = human.home_hut
            else:
                # Fall back to nearest town hall
                nearest_townhall = None
                nearest_dist = float('inf')
                
                human_x = human.x + human.size / 2
                human_y = human.y + human.size / 2
                
                for townhall in game_state.townhall_list:
                    townhall_x = townhall.x + townhall.width / 2
                    townhall_y = townhall.y + townhall.height / 2
                    dist = distance(human_x, human_y, townhall_x, townhall_y)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_townhall = townhall
                
                if nearest_townhall:
                    human.sleep_target = nearest_townhall
        
        # Move towards sleep target (hut or town hall)
        if human.sleep_target:
            human_x = human.x + human.size / 2
            human_y = human.y + human.size / 2
            
            # Check if target is a hut or townhall
            from entities.hut import Hut
            if isinstance(human.sleep_target, Hut):
                # Moving to hut
                target_x = human.sleep_target.x + human.sleep_target.size / 2
                target_y = human.sleep_target.y + human.sleep_target.size / 2
                arrival_dist = 5  # Close enough to hut
            else:
                # Moving to town hall
                target_x = human.sleep_target.x + human.sleep_target.width / 2
                target_y = human.sleep_target.y + human.sleep_target.height / 2
                arrival_dist = 30  # Close enough to townhall
            
            dist = distance(human_x, human_y, target_x, target_y)
            
            if dist > arrival_dist:
                # Move towards it (slower than normal)
                dx = target_x - human_x
                dy = target_y - human_y
                speed = HUMAN_WANDER_SPEED  # Slower speed
                dx = (dx / dist) * speed
                dy = (dy / dist) * speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area
                from utils.geometry import clamp
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Check collision (include huts in collision check)
                if human._check_structure_collisions(game_state.pen_list, game_state.townhall_list):
                    human.x, human.y = old_x, old_y
            # If close enough, they're sleeping (no movement needed)

