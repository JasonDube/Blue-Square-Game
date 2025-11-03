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
        """Update wandering behavior for unemployed humans - they sit on the bench"""
        # Find nearest town hall
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
        
        if not nearest_townhall:
            # No town hall - don't do anything
            return
        
        # Get all unemployed humans
        unemployed_humans = [h for h in game_state.human_list if not h.is_employed and h.state == "wander"]
        
        # Get bench sitting positions
        bench_positions = nearest_townhall.get_bench_sitting_positions(human.size)
        
        # Find this human's index in unemployed list
        try:
            human_index = unemployed_humans.index(human)
        except ValueError:
            human_index = len(unemployed_humans)
        
        # If there's a spot on the bench for this human, move them there
        if human_index < len(bench_positions):
            target_x, target_y = bench_positions[human_index]
            dist = distance(human_x, human_y, target_x + human.size/2, target_y + human.size/2)
            
            if dist > 2:  # Not at position yet
                dx = target_x + human.size/2 - human_x
                dy = target_y + human.size/2 - human_y
                speed = HUMAN_WANDER_SPEED
                dx = (dx / dist) * speed
                dy = (dy / dist) * speed
                human.x += dx
                human.y += dy
                
                # Keep within playable area
                from utils.geometry import clamp
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            else:
                # At bench position - stay there
                human.x = target_x
                human.y = target_y
    
    def _move_to_townhall_edge(self, human, townhall):
        """Move human to sit at edge of town hall"""
        human_x = human.x + human.size / 2
        human_y = human.y + human.size / 2
        townhall_x = townhall.x + townhall.width / 2
        townhall_y = townhall.y + townhall.height / 2
        
        # Choose a point on the edge of the town hall
        # Pick a random angle and place human at that edge
        if not hasattr(human, 'townhall_sit_angle'):
            human.townhall_sit_angle = random.uniform(0, 2 * math.pi)
        
        # Calculate edge position
        angle = human.townhall_sit_angle
        edge_x = townhall_x + math.cos(angle) * (townhall.width / 2 + human.size / 2 + 5)
        edge_y = townhall_y + math.sin(angle) * (townhall.height / 2 + human.size / 2 + 5)
        
        dist = distance(human_x, human_y, edge_x, edge_y)
        if dist > 5:
            # Move towards edge
            dx = edge_x - human_x
            dy = edge_y - human_y
            speed = HUMAN_WANDER_SPEED
            dx = (dx / dist) * speed
            dy = (dy / dist) * speed
            human.x += dx
            human.y += dy
    
    def _choose_townhall_wander_target(self, human, townhall, max_distance):
        """Choose a wander target within max_distance pixels of town hall edge"""
        townhall_x = townhall.x + townhall.width / 2
        townhall_y = townhall.y + townhall.height / 2
        
        # Pick a random angle and distance
        angle = random.uniform(0, 2 * math.pi)
        # Distance from center: townhall_half_size + max_distance
        townhall_half_size = max(townhall.width, townhall.height) / 2
        distance_from_center = random.uniform(townhall_half_size + human.size, townhall_half_size + max_distance)
        
        target_x = townhall_x + math.cos(angle) * distance_from_center
        target_y = townhall_y + math.sin(angle) * distance_from_center
        
        # Clamp to playable area
        from utils.geometry import clamp
        target_x = clamp(target_x, human.size / 2, SCREEN_WIDTH - human.size / 2)
        target_y = clamp(target_y, PLAYABLE_AREA_TOP + human.size / 2, PLAYABLE_AREA_BOTTOM - human.size / 2)
        
        human.wander_target_x = target_x
        human.wander_target_y = target_y
        human.is_wandering = True
    
    def _constrain_to_townhall_area(self, human, townhall, max_distance):
        """Ensure human stays within max_distance pixels of town hall edge"""
        human_x = human.x + human.size / 2
        human_y = human.y + human.size / 2
        townhall_x = townhall.x + townhall.width / 2
        townhall_y = townhall.y + townhall.height / 2
        
        townhall_half_size = max(townhall.width, townhall.height) / 2
        dist_from_center = distance(human_x, human_y, townhall_x, townhall_y)
        max_dist = townhall_half_size + max_distance
        
        if dist_from_center > max_dist:
            # Move back towards town hall
            angle = math.atan2(human_y - townhall_y, human_x - townhall_x)
            target_x = townhall_x + math.cos(angle) * (max_dist - human.size / 2)
            target_y = townhall_y + math.sin(angle) * (max_dist - human.size / 2)
            human.x = target_x - human.size / 2
            human.y = target_y - human.size / 2
    
    def _choose_wander_target(self, human, game_state):
        """Choose a random wander target within playable area (legacy - not used for unemployed)"""
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
        
        # Check collision with structures (FIXED: now includes huts)
        if self._check_structure_collisions(human, game_state):
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
    
    def _check_structure_collisions(self, human, game_state):
        """Check if human collides with any structure (FIXED: now includes huts)"""
        for pen in game_state.pen_list:
            if pen.check_collision_player(human.x, human.y):
                return True
        for townhall in game_state.townhall_list:
            if townhall.check_collision_player(human.x, human.y):
                return True
        # FIXED: Add hut collision checks, but allow owner to pass through
        for hut in game_state.hut_list:
            # Allow the owner of the hut to pass through
            if hut.owner != human and hut.check_collision_player(human.x, human.y):
                return True
        return False
    
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
                    
                    # NO DISTANCE CHECK - unlimited range!
                    # Find the nearest worker (but allow any distance)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_human = human
                
                # Claim the hut for the nearest employed worker
                if nearest_human:
                    success = hut.claim(nearest_human)
                    if success:
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
                
                # Check collision (FIXED: now uses proper collision check with huts)
                if self._check_structure_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
            # If close enough, they're sleeping (no movement needed)
