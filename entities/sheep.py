"""
Sheep entity - autonomous grazing animal
"""
import pygame
import random
import math
from constants import *
from utils.geometry import distance


class Sheep:
    """Sheep that can follow, stay, or separate by gender"""
    
    def __init__(self, x, y, gender="male"):
        self.x = x
        self.y = y
        self.width = SHEEP_WIDTH
        self.height = SHEEP_HEIGHT
        self.state = "stay"  # "follow", "stay", or "gender_separate"
        self.selected = False
        self.speed = SHEEP_SPEED
        self.graze_timer = random.uniform(SHEEP_GRAZE_MIN_TIME, SHEEP_GRAZE_MAX_TIME)
        self.grazing = False
        self.graze_target_x = None
        self.graze_target_y = None
        self.graze_speed = SHEEP_GRAZE_SPEED
        self.gender = gender  # "male" or "female"
        
        # Wool tracking
        self.has_wool = True  # Start with wool
        self.wool_regrowth_day = None  # Day when wool was sheared (None if has wool)
    
    def draw(self, screen, debug_mode):
        """Draw the sheep with optional debug info"""
        # Draw sheep based on wool state
        if self.has_wool:
            # Draw filled white oval when has wool
            pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.width, self.height))
        else:
            # Draw unfilled oval with thin outline when sheared
            pygame.draw.ellipse(screen, WHITE, (self.x, self.y, self.width, self.height), 1)
        
        # Draw selection indicator
        if self.selected:
            pygame.draw.circle(
                screen, YELLOW, 
                (int(self.x + self.width/2), int(self.y + self.height/2)), 
                8, 1
            )
        
        # Draw debug info
        if debug_mode:
            self._draw_debug_info(screen)
    
    def _draw_debug_info(self, screen):
        """Draw state and gender indicators"""
        font_small = pygame.font.Font(None, 16)
        
        # State indicator
        state_colors = {"follow": GREEN, "gender_separate": YELLOW, "stay": RED}
        state_labels = {"follow": "F", "gender_separate": "GS", "stay": "S"}
        state_text = state_labels.get(self.state, "S")
        state_color = state_colors.get(self.state, RED)
        text_surface = font_small.render(state_text, True, state_color)
        screen.blit(text_surface, (int(self.x + self.width + 2), int(self.y - 2)))
        
        # Gender indicator
        gender_text = "M" if self.gender == "male" else "Fem"
        gender_color = BLUE if self.gender == "male" else PINK
        gender_surface = font_small.render(gender_text, True, gender_color)
        screen.blit(gender_surface, (int(self.x + self.width + 2), int(self.y + 10)))
    
    def update_graze(self, dt, herd_center_x, herd_center_y, eaten_pixels, other_sheep, pen_list, townhall_list):
        """Update grazing behavior"""
        if self.state not in ["stay"]:
            self.grazing = False
            return
        
        # Update graze timer
        self.graze_timer -= dt
        
        if not self.grazing and self.graze_timer <= 0:
            # Time to start grazing - find a target
            self.find_graze_target(herd_center_x, herd_center_y, eaten_pixels, pen_list)
            self.grazing = True
        
        if self.grazing and self.graze_target_x is not None:
            self._move_to_graze_target(eaten_pixels, pen_list, townhall_list, other_sheep)
    
    def _move_to_graze_target(self, eaten_pixels, pen_list, townhall_list, other_sheep):
        """Move toward the graze target and eat when reached"""
        dx = self.graze_target_x - self.x
        dy = self.graze_target_y - self.y
        dist = distance(self.x, self.y, self.graze_target_x, self.graze_target_y)
        
        if dist < 2:
            # Reached target, eat the pixel
            eaten_pixels.add((int(self.graze_target_x), int(self.graze_target_y)))
            # Reset for next graze
            self.graze_timer = random.uniform(SHEEP_GRAZE_MIN_TIME, SHEEP_GRAZE_MAX_TIME)
            self.grazing = False
            self.graze_target_x = None
            self.graze_target_y = None
        else:
            # Move toward target
            self._move_with_collision_check(dx, dy, dist, pen_list, townhall_list, other_sheep)
    
    def _move_with_collision_check(self, dx, dy, dist, pen_list, townhall_list, other_sheep):
        """Move with multiple collision checks along the path"""
        old_x, old_y = self.x, self.y
        step_size = self.graze_speed
        dx = (dx / dist) * step_size
        dy = (dy / dist) * step_size
        
        # Check multiple points along the path
        steps = max(1, int(math.sqrt(dx**2 + dy**2) / step_size))
        if steps > 1:
            new_x, new_y = self._move_in_steps(old_x, old_y, dx, dy, steps, pen_list, townhall_list)
        else:
            new_x, new_y = self._move_single_step(old_x, old_y, dx, dy, pen_list, townhall_list)
        
        self.x = new_x
        self.y = new_y
        
        # Final collision check
        if self._check_all_collisions(pen_list, townhall_list):
            self.x, self.y = old_x, old_y
            # Cancel this graze attempt
            self.graze_timer = random.uniform(2, 5)
            self.grazing = False
            self.graze_target_x = None
            self.graze_target_y = None
        
        # Check collision with other sheep
        if other_sheep and self.check_sheep_collision(other_sheep):
            self.x, self.y = old_x, old_y
    
    def _move_in_steps(self, old_x, old_y, dx, dy, steps, pen_list, townhall_list):
        """Move in multiple small steps to prevent passing through walls"""
        step_dx = dx / steps
        step_dy = dy / steps
        new_x, new_y = old_x, old_y
        
        for _ in range(steps):
            test_x = new_x + step_dx
            test_y = new_y + step_dy
            
            if self._check_all_collisions_at(test_x, test_y, pen_list, townhall_list):
                break  # Hit a wall, stop here
            
            new_x = test_x
            new_y = test_y
        
        return new_x, new_y
    
    def _move_single_step(self, old_x, old_y, dx, dy, pen_list, townhall_list):
        """Move in a single step"""
        test_x = old_x + dx
        test_y = old_y + dy
        
        if self._check_all_collisions_at(test_x, test_y, pen_list, townhall_list):
            return old_x, old_y
        
        return test_x, test_y
    
    def _check_all_collisions(self, pen_list, townhall_list):
        """Check if sheep collides with any structure"""
        return self._check_all_collisions_at(self.x, self.y, pen_list, townhall_list)
    
    def _check_all_collisions_at(self, x, y, pen_list, townhall_list):
        """Check if sheep would collide at given position"""
        for pen in pen_list:
            if pen.check_collision_sheep(x, y, self.width, self.height):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_sheep(x, y, self.width, self.height):
                return True
        return False
    
    def find_graze_target(self, herd_center_x, herd_center_y, eaten_pixels, pen_list):
        """Find a random uneaten pixel within herd boundary"""
        active_pens = [pen for pen in pen_list if pen.collision_enabled]
        sheep_in_pen = self.is_inside_pen(active_pens)
        
        # Try up to 100 times to find valid target
        for _ in range(100):
            offset_x = random.randint(-HERD_BOUNDARY_SIZE // 2, HERD_BOUNDARY_SIZE // 2)
            offset_y = random.randint(-HERD_BOUNDARY_SIZE // 2, HERD_BOUNDARY_SIZE // 2)
            target_x = herd_center_x + offset_x
            target_y = herd_center_y + offset_y
            
            # Validate target
            if self._is_valid_graze_target(target_x, target_y, eaten_pixels, sheep_in_pen, active_pens, pen_list):
                self.graze_target_x = target_x
                self.graze_target_y = target_y
                return
        
        # If we couldn't find target, just stay put
        self.graze_timer = random.uniform(SHEEP_GRAZE_MIN_TIME, SHEEP_GRAZE_MAX_TIME)
        self.grazing = False
    
    def _is_valid_graze_target(self, target_x, target_y, eaten_pixels, sheep_in_pen, active_pens, pen_list):
        """Check if target is valid for grazing"""
        # Check screen bounds
        if not (0 <= target_x < SCREEN_WIDTH and 0 <= target_y < SCREEN_HEIGHT):
            return False
        
        # Check if pixel is uneaten
        if (int(target_x), int(target_y)) in eaten_pixels:
            return False
        
        # Check if target is on same side of pens as sheep
        target_in_pen = self.is_point_inside_pen(target_x, target_y, active_pens)
        if sheep_in_pen != target_in_pen:
            return False
        
        # Check if path is clear
        if not self.is_path_clear(
            self.x + self.width/2, self.y + self.height/2, 
            target_x, target_y, pen_list
        ):
            return False
        
        return True
    
    def is_path_clear(self, start_x, start_y, end_x, end_y, pen_list):
        """Check if path doesn't cross through pen walls"""
        dist = distance(start_x, start_y, end_x, end_y)
        if dist < 1:
            return True
        
        active_pens = [pen for pen in pen_list if pen.collision_enabled]
        if not active_pens:
            return True
        
        start_in_pen = self.is_point_inside_pen(start_x, start_y, active_pens)
        end_in_pen = self.is_point_inside_pen(end_x, end_y, active_pens)
        
        # If on different sides, path crosses boundary
        if start_in_pen != end_in_pen:
            return False
        
        # Check intermediate points
        num_checks = max(5, int(dist / 3))
        for i in range(1, num_checks):
            t = i / num_checks
            check_x = start_x + (end_x - start_x) * t
            check_y = start_y + (end_y - start_y) * t
            check_in_pen = self.is_point_inside_pen(check_x, check_y, active_pens)
            
            if check_in_pen != start_in_pen:
                return False
        
        return True
    
    def is_inside_pen(self, pen_list):
        """Check if sheep center is inside any pen"""
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        return self.is_point_inside_pen(center_x, center_y, pen_list)
    
    def is_point_inside_pen(self, px, py, pen_list):
        """Check if a point is inside any pen boundaries"""
        for pen in pen_list:
            if pen.is_point_inside(px, py):
                return True
        return False
    
    def move_towards(self, target_x, target_y, pen_list, townhall_list, sheep_list=None):
        """Move towards target with gender separation offset"""
        if self.state not in ["follow", "gender_separate"]:
            return
        
        # Calculate offset for gender separation
        offset_x, offset_y = self._get_gender_offset()
        
        # Calculate direction to target
        target_final_x = target_x + offset_x
        target_final_y = target_y + offset_y
        dx = target_final_x - self.x
        dy = target_final_y - self.y
        dist = distance(self.x, self.y, target_final_x, target_final_y)
        
        # Only move if not too close
        if dist > SHEEP_MIN_FOLLOW_DISTANCE:
            self._apply_movement(dx, dy, dist, pen_list, townhall_list, sheep_list)
    
    def _get_gender_offset(self):
        """Get position offset based on gender separation"""
        if self.state == "gender_separate":
            if self.gender == "male":
                return -GENDER_SEPARATION_DISTANCE, 0
            else:
                return GENDER_SEPARATION_DISTANCE, 0
        return 0, 0
    
    def _apply_movement(self, dx, dy, dist, pen_list, townhall_list, sheep_list):
        """Apply movement with collision detection"""
        from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
        from utils.geometry import clamp
        
        dx = (dx / dist) * self.speed
        dy = (dy / dist) * self.speed
        
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy
        
        # Keep within playable area bounds
        self.x = clamp(self.x, 0, SCREEN_WIDTH - self.width)
        self.y = clamp(self.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - self.height)
        
        # Check collisions
        if self._check_all_collisions(pen_list, townhall_list):
            self.x, self.y = old_x, old_y
        
        # Check collision with other sheep
        if sheep_list:
            for other in sheep_list:
                if other != self and self.check_sheep_collision(other):
                    self.x, self.y = old_x, old_y
                    break
    
    def check_sheep_collision(self, other_sheep):
        """Simple distance-based collision with another sheep"""
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        other_center_x = other_sheep.x + other_sheep.width / 2
        other_center_y = other_sheep.y + other_sheep.height / 2
        
        dist = distance(center_x, center_y, other_center_x, other_center_y)
        return dist < SHEEP_COLLISION_RADIUS
    
    def contains_point(self, px, py):
        """Check if a point is inside the sheep"""
        return self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
