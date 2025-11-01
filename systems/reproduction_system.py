"""
Sheep reproduction system
"""
import random
from constants import *
from entities.sheep import Sheep


class ReproductionSystem:
    """Handles sheep reproduction at end of day"""
    
    @staticmethod
    def process_reproduction(game_state):
        """Process sheep reproduction for new day"""
        sheep_list = game_state.sheep_list
        pen_list = game_state.pen_list
        player_x = game_state.player_x
        player_y = game_state.player_y
        
        # Get males and females
        males = [s for s in sheep_list if s.gender == "male"]
        females = [s for s in sheep_list if s.gender == "female"]
        
        # Filter to only sheep outside active pens
        active_pens = [pen for pen in pen_list if pen.collision_enabled]
        males_outside = [s for s in males if not s.is_inside_pen(active_pens)]
        females_outside = [s for s in females if not s.is_inside_pen(active_pens)]
        
        # Only allow reproduction if there are both males and females outside
        if len(males_outside) > 0 and len(females_outside) > 0:
            new_sheep = ReproductionSystem._reproduce(females_outside, player_x, player_y)
            sheep_list.extend(new_sheep)
    
    @staticmethod
    def _reproduce(females_outside, player_x, player_y):
        """Generate new sheep from females"""
        new_sheep = []
        
        for female in females_outside:
            if random.random() < REPRODUCTION_CHANCE:
                # 50% chance male or female
                new_gender = "male" if random.random() < 0.5 else "female"
                
                # Spawn near player
                spawn_x = player_x + random.randint(-REPRODUCTION_SPAWN_OFFSET, REPRODUCTION_SPAWN_OFFSET)
                spawn_y = player_y + random.randint(-REPRODUCTION_SPAWN_OFFSET, REPRODUCTION_SPAWN_OFFSET)
                
                # Keep within screen bounds
                spawn_x = max(0, min(spawn_x, SCREEN_WIDTH - SHEEP_WIDTH))
                spawn_y = max(0, min(spawn_y, SCREEN_HEIGHT - SHEEP_HEIGHT))
                
                new_sheep.append(Sheep(spawn_x, spawn_y, new_gender))
        
        return new_sheep
