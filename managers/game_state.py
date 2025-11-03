"""
Game state manager - centralizes all game state
"""
from constants import *


class GameState:
    """Centralized game state management"""
    
    def __init__(self):
        # Player position
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        
        # Entity collections
        self.sheep_list = []
        self.human_list = []
        self.pen_list = []
        self.townhall_list = []
        self.lumber_yard_list = []
        self.stone_yard_list = []
        self.iron_yard_list = []
        self.salt_yard_list = []
        self.wool_shed_list = []
        self.barley_farm_list = []
        self.silo_list = []
        self.mill_list = []
        self.hut_list = []
        self.road_list = [] # New list for road entities
        # Road snap points for visible clickable points
        self.road_snap_points = []  # List of (road, snap_points_dict) tuples when in build mode
        self.tree_list = []
        self.rock_list = []
        self.iron_mine_list = []
        self.salt_list = []
        self.eaten_pixels = set()
        
        # Time tracking
        self.current_day = 1
        self.elapsed_time = 0.0
        
        # UI state
        self.debug_mode = False
        self.build_mode = False
        self.build_mode_type = None  # "pen", "townhall", "lumberyard", "stoneyard", "ironyard", "saltyard", "woolshed", "barleyfarm", "silo", "mill", "hut", "road"
        self.pen_rotation = 0  # 0 = top, 1 = right, 2 = bottom, 3 = left
        
        # Selection state
        self.box_selecting = False
        self.box_start_x = 0
        self.box_start_y = 0
        self.box_end_x = 0
        self.box_end_y = 0
        
        # Context menu state
        self.show_context_menu = False
        self.context_menu_x = 0
        self.context_menu_y = 0
        
        self.show_male_human_context_menu = False
        self.male_human_context_menu_x = 0
        self.male_human_context_menu_y = 0
        
        self.show_female_human_context_menu = False
        self.female_human_context_menu_x = 0
        self.female_human_context_menu_y = 0
        
        self.show_player_context_menu = False
        self.show_resource_context_menu = False
        self.resource_context_menu_x = 0
        self.resource_context_menu_y = 0
        self.player_context_menu_x = 0
        self.player_context_menu_y = 0
        
        # Family tree dialogue box state
        self.show_family_tree_dialogue = False
        self.family_tree_dialogue_x = SCREEN_WIDTH // 2 - 250  # Center initially
        self.family_tree_dialogue_y = SCREEN_HEIGHT // 2 - 300  # Center initially
        self.family_tree_dialogue_dragging = False
        self.family_tree_dialogue_drag_offset_x = 0
        self.family_tree_dialogue_drag_offset_y = 0
        
        # Profile info dialogue box state
        self.show_profile_info_dialogue = False
        self.profile_info_dialogue_x = SCREEN_WIDTH // 2 - 250  # Center initially
        self.profile_info_dialogue_y = SCREEN_HEIGHT // 2 - 300  # Center initially
        self.profile_info_dialogue_dragging = False
        self.profile_info_dialogue_drag_offset_x = 0
        self.profile_info_dialogue_drag_offset_y = 0
    
    def get_selected_sheep(self):
        """Get list of selected sheep"""
        return [sheep for sheep in self.sheep_list if sheep.selected]
    
    def get_selected_humans(self):
        """Get list of selected humans"""
        return [human for human in self.human_list if human.selected]
    
    def any_sheep_selected(self):
        """Check if any sheep are selected"""
        return any(sheep.selected for sheep in self.sheep_list)
    
    def any_human_selected(self):
        """Check if any humans are selected"""
        return any(human.selected for human in self.human_list)
    
    def any_male_human_selected(self):
        """Check if any male humans are selected"""
        return any(human.selected and human.gender == "male" for human in self.human_list)
    
    def any_female_human_selected(self):
        """Check if any female humans are selected"""
        return any(human.selected and human.gender == "female" for human in self.human_list)
    
    def any_resource_selected(self):
        """Check if any resources (trees, rocks, salt, iron mines) are selected"""
        return (any(tree.selected for tree in self.tree_list) or
                any(rock.selected for rock in self.rock_list) or
                any(salt.selected for salt in self.salt_list) or
                any(mine.selected for mine in self.iron_mine_list))
    
    def get_herd_center(self):
        """Calculate the center of the sheep herd"""
        if len(self.sheep_list) > 0:
            center_x = sum(sheep.x + sheep.width/2 for sheep in self.sheep_list) / len(self.sheep_list)
            center_y = sum(sheep.y + sheep.height/2 for sheep in self.sheep_list) / len(self.sheep_list)
            return center_x, center_y
        else:
            return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2