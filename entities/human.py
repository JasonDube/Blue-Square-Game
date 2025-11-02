"""
Human entity - controllable character that can follow player or work jobs
"""
import pygame
from constants import *
from utils.geometry import distance


class Human:
    """Human character that can follow, stay, work, or be employed"""
    
    def __init__(self, x, y, gender="male", name=None):
        self.x = x
        self.y = y
        self.size = HUMAN_SIZE
        self.state = "stay"  # "follow", "stay", "harvest", "employed", "wander", or "sleep"
        self.selected = False
        self.speed = HUMAN_SPEED
        self.gender = gender  # "male" or "female"
        self.name = name if name else "Unknown"  # Character name
        
        # Employment attributes
        self.job = None  # Type of job: "lumberjack", "farmer", etc.
        self.employer = None  # Town hall that employs this human
        
        # Happiness system
        self.happiness = 100.0  # 0-100, starts at max
        self.is_employed = False  # Whether human has a job
        self.is_hungry = False  # Whether human needs food
        
        # Harvest-related attributes (for manual harvest command)
        self.harvest_target = None  # Resource being harvested
        self.harvest_timer = 0.0  # Time spent harvesting current resource
        self.carrying_resource = False  # Whether human is carrying a resource
        self.target_building = None  # Which building to deliver to
        self.resource_type = None  # Type of resource being carried
        self.harvest_position = None  # Position around resource (to prevent overlap)
        
        # Auto-work attributes (for employed workers)
        self.work_timer = 0.0  # Timer for automatic work cycles
        self.work_target = None  # Current target for auto-work
        
        # Wandering attributes (for unemployed humans)
        self.wander_timer = 0.0  # Timer for current wander behavior phase (negative = resting)
        self.wander_duration = 0.0  # Duration of current wander phase (positive when wandering)
        self.wander_direction = None  # Current wander direction (x, y) or None if stopped
        self.wander_target_x = None  # Target x position for wandering
        self.wander_target_y = None  # Target y position for wandering
        self.is_wandering = False  # Whether currently moving or stopped
        
        # Sleep attributes
        self.sleep_target = None  # Building to sleep in (hut if available, otherwise townhall)
        self.has_home = False  # Whether human has a dedicated home (hut)
        self.home_hut = None  # The hut this human owns (None if no hut)
    
    def update_happiness(self, dt, game_state):
        """Update happiness based on employment, home status, and hunger"""
        # Check if townhall exists
        has_townhall = len(game_state.townhall_list) > 0
        
        # Check if human has a dedicated home/hut (townhall does NOT count as home for sleeping)
        # Check if this human owns a hut
        has_hut = self.home_hut is not None
        self.has_home = has_hut  # Only huts count as homes, not townhall
        
        # Calculate base happiness with static deductions
        base_happiness = 100.0
        
        # Deduct 20 if unemployed
        if not self.is_employed:
            base_happiness -= 20.0
        
        # Deduct 20 if no dedicated home/hut to sleep in (townhall does NOT count)
        if not self.has_home:
            base_happiness -= 20.0
        
        # Deduct 20 if no townhall exists at all
        if not has_townhall:
            base_happiness -= 20.0
        
        # Start from base happiness
        self.happiness = base_happiness
        
        # Apply time-based adjustments
        # Lose happiness if hungry (in addition to base deductions)
        if self.is_hungry:
            self.happiness -= HAPPINESS_HUNGER_PENALTY * dt
        
        # Gain happiness if employed and not hungry
        if self.is_employed and not self.is_hungry:
            self.happiness += HAPPINESS_GAIN_RATE * dt
        
        # Clamp happiness between 0 and 100
        self.happiness = max(0.0, min(100.0, self.happiness))
    
    def get_effective_happiness(self):
        """Get effective happiness value (with deductions applied)"""
        # This returns the current happiness, which already has deductions applied
        return int(self.happiness)
    
    def get_happiness_color(self):
        """Get color representing happiness level"""
        if self.happiness >= 80:
            return GREEN
        elif self.happiness >= 60:
            return YELLOW
        elif self.happiness >= 40:
            return (255, 165, 0)  # Orange
        else:
            return RED
    
    def draw(self, screen, debug_mode):
        """Draw the human based on gender"""
        if self.gender == "male":
            # Blue unfilled square
            pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size), 2)
        else:
            # Pink unfilled circle
            pygame.draw.circle(
                screen, PINK, 
                (int(self.x + self.size/2), int(self.y + self.size/2)), 
                self.size//2, 2
            )
        
        # Draw selection indicator
        if self.selected:
            pygame.draw.circle(
                screen, YELLOW, 
                (int(self.x + self.size/2), int(self.y + self.size/2)), 
                10, 1
            )
        
        # Draw happiness indicator (small dot above head)
        happiness_color = self.get_happiness_color()
        pygame.draw.circle(
            screen, happiness_color,
            (int(self.x + self.size/2), int(self.y - 3)),
            2
        )
        
        # Draw debug info
        if debug_mode:
            self._draw_debug_info(screen)
    
    def _draw_debug_info(self, screen):
        """Draw state and job indicators"""
        font_small = pygame.font.Font(None, 16)
        
        # Draw name in black above the entity
        name_surface = font_small.render(self.name, True, BLACK)
        name_x = int(self.x + self.size / 2 - name_surface.get_width() / 2)
        name_y = int(self.y - 18)
        screen.blit(name_surface, (name_x, name_y))
        
        # State indicator
        state_map = {
            "follow": ("F", GREEN),
            "stay": ("S", RED),
            "harvest": ("H", YELLOW),
            "employed": ("E", BLUE),
            "wander": ("W", (100, 150, 255)),  # Light blue
            "sleep": ("Z", (100, 100, 100))  # Gray
        }
        
        state_text, state_color = state_map.get(self.state, ("S", RED))
        text_surface = font_small.render(state_text, True, state_color)
        screen.blit(text_surface, (int(self.x + self.size + 2), int(self.y - 2)))
        
        # Job indicator
        if self.job:
            job_abbrev = self.job[0].upper()  # L for lumberjack, etc.
            job_surface = font_small.render(job_abbrev, True, BLUE)
            screen.blit(job_surface, (int(self.x + self.size + 2), int(self.y + 10)))
        
        # Happiness indicator (dark green almost black)
        from constants import DARKEST_GREEN
        happiness_text = f"{int(self.happiness)}"
        happiness_surface = font_small.render(happiness_text, True, DARKEST_GREEN)
        screen.blit(happiness_surface, (int(self.x + self.size + 2), int(self.y + 22)))
    
    def move_towards(self, target_x, target_y, other_humans, pen_list, townhall_list, sheep_list=None):
        """Move towards target position"""
        if self.state not in ["follow"]:
            return
        
        # Calculate direction to target
        dx = target_x - (self.x + self.size/2)
        dy = target_y - (self.y + self.size/2)
        dist = distance(self.x + self.size/2, self.y + self.size/2, target_x, target_y)
        
        # Only move if not too close
        if dist > HUMAN_MIN_FOLLOW_DISTANCE:
            self._apply_movement(dx, dy, dist, other_humans, pen_list, townhall_list)
    
    def _apply_movement(self, dx, dy, dist, other_humans, pen_list, townhall_list):
        """Apply movement with collision detection"""
        from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
        from utils.geometry import clamp
        
        dx = (dx / dist) * self.speed
        dy = (dy / dist) * self.speed
        
        old_x, old_y = self.x, self.y
        self.x += dx
        self.y += dy
        
        # Keep within playable area bounds
        self.x = clamp(self.x, 0, SCREEN_WIDTH - self.size)
        self.y = clamp(self.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - self.size)
        
        # Check collision with structures
        if self._check_structure_collisions(pen_list, townhall_list):
            self.x, self.y = old_x, old_y
            return
        
        # Check collision with other humans - with separation
        if other_humans:
            for other in other_humans:
                if other != self and self.check_human_collision(other):
                    # Push away from each other slightly
                    push_dx = self.x - other.x
                    push_dy = self.y - other.y
                    push_dist = distance(self.x, self.y, other.x, other.y)
                    if push_dist > 0:
                        push_dx = (push_dx / push_dist) * 2
                        push_dy = (push_dy / push_dist) * 2
                        self.x += push_dx
                        self.y += push_dy
                    else:
                        self.x, self.y = old_x, old_y
                    break
    
    def _check_structure_collisions(self, pen_list, townhall_list):
        """Check if human collides with any structure"""
        for pen in pen_list:
            if pen.check_collision_player(self.x, self.y):
                return True
        for townhall in townhall_list:
            if townhall.check_collision_player(self.x, self.y):
                return True
        return False
    
    def check_human_collision(self, other_human):
        """Simple distance-based collision with another human"""
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        other_center_x = other_human.x + other_human.size / 2
        other_center_y = other_human.y + other_human.size / 2
        
        dist = distance(center_x, center_y, other_center_x, other_center_y)
        return dist < HUMAN_COLLISION_RADIUS
    
    def contains_point(self, px, py):
        """Check if a point is inside the human"""
        return self.x <= px <= self.x + self.size and self.y <= py <= self.y + self.size
