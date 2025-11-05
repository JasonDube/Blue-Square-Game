"""
Main game class and entry point
"""
import pygame
import sys
from constants import *
from managers.game_state import GameState
from systems import CollisionSystem, DayCycleSystem, InputSystem, HarvestSystem, ResourceSystem, EmploymentSystem
from systems.human_behavior_system import HumanBehaviorSystem
from ui import ContextMenuRenderer, BuildModeRenderer, HUD, HUDLow, EmploymentMenu
from utils.world_generator import WorldGenerator
from utils.geometry import clamp


class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blue Square Game")
        self.clock = pygame.time.Clock()
        
        # Initialize game state
        self.game_state = GameState()
        
        # Initialize systems
        self.collision_system = CollisionSystem()
        self.day_cycle = DayCycleSystem()
        self.resource_system = ResourceSystem()
        self.harvest_system = HarvestSystem(self.resource_system)
        self.employment_system = EmploymentSystem(self.resource_system)
        self.human_behavior_system = HumanBehaviorSystem()
        
        # Initialize UI renderers
        self.context_menu_renderer = ContextMenuRenderer()
        self.build_mode_renderer = BuildModeRenderer()
        self.hud = HUD()
        self.hud_low = HUDLow()
        self.employment_menu = EmploymentMenu()
        
        # Initialize input system (after UI so we can pass employment_menu)
        self.input_system = InputSystem(self.game_state, self.harvest_system, self.employment_menu)
        
        # Initialize world
        self._initialize_world()
    
    def _initialize_world(self):
        """Initialize game world with entities"""
        # Generate entities and buildings
        sheep_list, human_list, pen_list, lumber_yard_list, stone_yard_list, iron_yard_list, townhall_list = WorldGenerator.generate_initial_entities()
        
        self.game_state.sheep_list = sheep_list
        self.game_state.human_list = human_list
        self.game_state.pen_list = pen_list
        self.game_state.lumber_yard_list = lumber_yard_list
        self.game_state.stone_yard_list = stone_yard_list
        self.game_state.iron_yard_list = iron_yard_list
        self.game_state.townhall_list = townhall_list
        
        # Generate trees (no pen_list means trees can spawn anywhere)
        self.game_state.tree_list = WorldGenerator.generate_trees(pen_list=pen_list)
        
        # Generate rocks
        self.game_state.rock_list = WorldGenerator.generate_rocks(num_rocks=15, pen_list=pen_list, tree_list=self.game_state.tree_list)
        
        # Generate iron mine
        iron_mine = WorldGenerator.generate_iron_mine(
            pen_list=pen_list, 
            tree_list=self.game_state.tree_list,
            rock_list=self.game_state.rock_list
        )
        if iron_mine:
            self.game_state.iron_mine_list = [iron_mine]
        else:
            self.game_state.iron_mine_list = []
        
        # Generate salt deposits
        self.game_state.salt_list = WorldGenerator.generate_salt(
            num_salt=12,
            pen_list=pen_list,
            tree_list=self.game_state.tree_list,
            rock_list=self.game_state.rock_list,
            iron_mine_list=self.game_state.iron_mine_list
        )
        
        # Clear resources under the town hall
        if townhall_list:
            townhall = townhall_list[0]
            self._clear_resources_under_townhall(townhall)
    
    def _clear_resources_under_townhall(self, townhall):
        """Remove trees, rocks, mines, and salt deposits that overlap with the town hall"""
        townhall_rect = pygame.Rect(townhall.x, townhall.y, townhall.width, townhall.height)
        
        # Remove trees that overlap with town hall
        trees_to_remove = []
        for tree in self.game_state.tree_list:
            tree_bounds = tree.get_bounds()
            if townhall_rect.colliderect(tree_bounds):
                trees_to_remove.append(tree)
        for tree in trees_to_remove:
            self.game_state.tree_list.remove(tree)
        
        # Remove rocks that overlap with town hall
        rocks_to_remove = []
        for rock in self.game_state.rock_list:
            rock_bounds = rock.get_bounds()
            if townhall_rect.colliderect(rock_bounds):
                rocks_to_remove.append(rock)
        for rock in rocks_to_remove:
            self.game_state.rock_list.remove(rock)
        
        # Remove iron mines that overlap with town hall
        mines_to_remove = []
        for mine in self.game_state.iron_mine_list:
            mine_bounds = mine.get_bounds()
            if townhall_rect.colliderect(mine_bounds):
                mines_to_remove.append(mine)
        for mine in mines_to_remove:
            self.game_state.iron_mine_list.remove(mine)
        
        # Remove salt deposits that overlap with town hall
        salt_to_remove = []
        for salt in self.game_state.salt_list:
            salt_bounds = salt.get_bounds()
            if townhall_rect.colliderect(salt_bounds):
                salt_to_remove.append(salt)
        for salt in salt_to_remove:
            self.game_state.salt_list.remove(salt)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.get_time() / 1000.0
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    result = self.input_system.handle_event(event)
                    if result is True:  # Escape pressed outside build mode
                        running = False
            
            # Update game state
            self._update(dt)
            
            # Render
            self._render()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        self._cleanup()
    
    def _update(self, dt):
        """Update all game systems"""
        # Update player movement
        self._update_player()
        
        # Update day cycle
        self.day_cycle.update(dt, self.game_state)
        
        # Update crop growth in barley farms
        for barley_farm in self.game_state.barley_farm_list:
            barley_farm.update_crops(self.game_state.current_day)
        
        # Update mills (processing and millstone rotation)
        for mill in self.game_state.mill_list:
            mill.update(dt)
            # Automatically add flour and malt to resource system
            # Calculate how much was produced since last update
            flour_to_add = mill.get_total_flour_produced() - getattr(mill, '_last_flour_count', 0)
            malt_to_add = mill.get_total_malt_produced() - getattr(mill, '_last_malt_count', 0)
            
            if flour_to_add > 0:
                from systems.resource_system import ResourceType
                self.resource_system.add_resource(ResourceType.FLOUR, flour_to_add)
            if malt_to_add > 0:
                from systems.resource_system import ResourceType
                self.resource_system.add_resource(ResourceType.MALT, malt_to_add)
            
            # Track current counts for next update
            mill._last_flour_count = mill.get_total_flour_produced()
            mill._last_malt_count = mill.get_total_malt_produced()
        
        # Update harvest system
        self.harvest_system.update(dt, self.game_state)
        
        # Update employment system (must be after harvest system to avoid conflicts)
        self.employment_system.update(dt, self.game_state)
        
        # Update human behavior system (wandering, sleep)
        self.human_behavior_system.update(dt, self.game_state, self.day_cycle)
        
        # Update entities
        self._update_sheep(dt)
        self._update_humans(dt)
    
    def _update_player(self):
        """Update player position based on keyboard input"""
        keys = pygame.key.get_pressed()
        
        old_x, old_y = self.game_state.player_x, self.game_state.player_y
        
        # Move player
        if keys[pygame.K_LEFT]:
            self.game_state.player_x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.game_state.player_x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.game_state.player_y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.game_state.player_y += PLAYER_SPEED
        
        # Keep within playable area bounds (between HUDs)
        self.game_state.player_x = clamp(self.game_state.player_x, 0, SCREEN_WIDTH - PLAYER_SIZE)
        self.game_state.player_y = clamp(self.game_state.player_y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - PLAYER_SIZE)
        
        # Check collision
        if self.collision_system.check_player_collision(
            self.game_state.player_x, 
            self.game_state.player_y,
            self.game_state.pen_list,
            self.game_state.hut_list, 
            self.game_state.townhall_list
        ):
            self.game_state.player_x, self.game_state.player_y = old_x, old_y
    
    def _update_sheep(self, dt):
        """Update all sheep"""
        herd_center_x, herd_center_y = self.game_state.get_herd_center()
        
        for sheep in self.game_state.sheep_list:
            # Move towards player
            sheep.move_towards(
                self.game_state.player_x,
                self.game_state.player_y,
                self.game_state.pen_list,
                self.game_state.townhall_list,
                self.game_state.sheep_list
            )
            
            # Update grazing
            sheep.update_graze(
                dt,
                herd_center_x,
                herd_center_y,
                self.game_state.eaten_pixels,
                None,
                self.game_state.pen_list,
                self.game_state.townhall_list
            )
    
    def _update_humans(self, dt):
        """Update all humans"""
        player_center_x = self.game_state.player_x + PLAYER_SIZE / 2
        player_center_y = self.game_state.player_y + PLAYER_SIZE / 2
        
        for i, human in enumerate(self.game_state.human_list):
            other_humans = [h for j, h in enumerate(self.game_state.human_list) if j != i]
            human.move_towards(
                player_center_x,
                player_center_y,
                other_humans,
                self.game_state.pen_list,
                self.game_state.townhall_list,
                self.game_state.sheep_list
            )
            # Update happiness
            human.update_happiness(dt, self.game_state)
    
    def _render(self):
        """Render all game elements"""
        # Fill background
        self.screen.fill(GREEN)
        
        # Draw terrain
        self._draw_terrain()
        
        # Draw structures
        self._draw_structures()
        
        # Draw entities
        self._draw_entities()
        
        # Draw player
        self._draw_player()
        
        # Draw UI (includes dialogue boxes that should be on top)
        self._draw_ui()
    
    def _draw_terrain(self):
        """Draw terrain (eaten grass pixels)"""
        for pixel_x, pixel_y in self.game_state.eaten_pixels:
            pygame.draw.circle(self.screen, DARK_GREEN, (pixel_x, pixel_y), 2)
    
    def _draw_structures(self):
        """Draw all harvestable resources and buildings"""
        # Draw trees (show health if in harvest cursor mode)
        show_health = self.harvest_system.harvest_cursor_active
        for tree in self.game_state.tree_list:
            if not tree.is_depleted():
                # Only draw if tree is within playable area (above bottom HUD)
                tree_bottom = tree.y
                if tree_bottom < PLAYABLE_AREA_BOTTOM:
                    tree.draw(self.screen, show_health=show_health)
        
        # Draw rocks
        for rock in self.game_state.rock_list:
            if not rock.is_depleted():
                rock.draw(self.screen, show_health=show_health)
        
        # Draw iron mines
        for iron_mine in self.game_state.iron_mine_list:
            if not iron_mine.is_depleted():
                iron_mine.draw(self.screen, show_health=show_health)
        
        # Draw salt deposits
        for salt in self.game_state.salt_list:
            if not salt.is_depleted():
                salt.draw(self.screen, show_health=show_health)
        
        # Draw pens
        for pen in self.game_state.pen_list:
            pen.draw(self.screen, preview=False)
        
        # Draw town halls
        for townhall in self.game_state.townhall_list:
            townhall.draw(self.screen, preview=False, resource_system=self.resource_system)
        
        # Draw lumber yards
        for lumber_yard in self.game_state.lumber_yard_list:
            lumber_yard.draw(self.screen, preview=False)
        
        # Draw stone yards
        for stone_yard in self.game_state.stone_yard_list:
            stone_yard.draw(self.screen, preview=False)
        
        # Draw iron yards
        for iron_yard in self.game_state.iron_yard_list:
            iron_yard.draw(self.screen, preview=False)
        
        # Draw salt yards
        for salt_yard in self.game_state.salt_yard_list:
            salt_yard.draw(self.screen, preview=False)
        
        # Draw wool sheds
        for wool_shed in self.game_state.wool_shed_list:
            wool_shed.draw(self.screen, preview=False)
        
        # Draw barley farms
        for barley_farm in self.game_state.barley_farm_list:
            barley_farm.draw(self.screen, preview=False)
        
        # Draw silos
        for silo in self.game_state.silo_list:
            silo.draw(self.screen, preview=False)
        
        # Draw mills
        for mill in self.game_state.mill_list:
            mill.draw(self.screen, preview=False)
        
        # Draw huts
        for hut in self.game_state.hut_list:
            hut.draw(self.screen, preview=False)
        
        # Draw roads
        for road in self.game_state.road_list:
            road.draw(self.screen, preview=False)
        
        # Draw road smoothing (corner fills) if enabled
        if self.game_state.road_smoothing_mode:
            self._draw_road_smoothing()
        
        # Draw debug road path numbers (after roads so they're visible on top)
        if self.game_state.debug_mode:
            self._draw_debug_road_paths()
    
    def _draw_entities(self):
        """Draw sheep and humans"""
        # Draw debug lines first (on the ground, under entities)
        if self.game_state.debug_mode:
            self._draw_debug_target_lines()
        
        for sheep in self.game_state.sheep_list:
            sheep.draw(self.screen, self.game_state.debug_mode)
        
        for human in self.game_state.human_list:
            human.draw(self.screen, self.game_state.debug_mode)
            # Draw harvesting tool if human is harvesting
            self.harvest_system.draw_harvesting_human(self.screen, human)
    
    def _draw_debug_target_lines(self):
        """Draw lines from each AI to their targets (debug visualization)"""
        from constants import YELLOW, GREEN, BLUE, RED, WHITE
        # Define colors for debug lines
        CYAN = (0, 255, 255)
        MAGENTA = (255, 0, 255)
        
        for human in self.game_state.human_list:
            human_center_x = human.x + human.size / 2
            human_center_y = human.y + human.size / 2
            
            # Draw line to work_target (if exists)
            if human.work_target:
                target_x, target_y = self._get_target_position(human.work_target)
                if target_x is not None and target_y is not None:
                    pygame.draw.line(self.screen, YELLOW, 
                                   (int(human_center_x), int(human_center_y)),
                                   (int(target_x), int(target_y)), 2)
            
            # Draw line to harvest_target (if different from work_target)
            if human.harvest_target and human.harvest_target != human.work_target:
                target_x, target_y = self._get_target_position(human.harvest_target)
                if target_x is not None and target_y is not None:
                    pygame.draw.line(self.screen, GREEN, 
                                   (int(human_center_x), int(human_center_y)),
                                   (int(target_x), int(target_y)), 2)
            
            # Draw line to target_building (if exists)
            if human.target_building:
                target_x, target_y = self._get_target_position(human.target_building)
                if target_x is not None and target_y is not None:
                    # Check if unit is using roads - if so, show path to first road
                    if hasattr(self.game_state, 'road_list') and self.game_state.road_list:
                        # Check if we're on a road or should use roads
                        is_on_road = any(road.contains_point(human_center_x, human_center_y) for road in self.game_state.road_list)
                        
                        if not is_on_road:
                            # Not on road - find nearest road to show path
                            from utils.geometry import distance
                            nearest_road = None
                            nearest_dist = float('inf')
                            max_distance = 150
                            
                            for road in self.game_state.road_list:
                                road_center_x = road.x + road.width / 2
                                road_center_y = road.y + road.height / 2
                                dist = distance(human_center_x, human_center_y, road_center_x, road_center_y)
                                
                                if dist < nearest_dist and dist < max_distance:
                                    nearest_dist = dist
                                    nearest_road = road
                            
                            if nearest_road:
                                # Draw line to nearest road first (blue)
                                road_center_x = nearest_road.x + nearest_road.width / 2
                                road_center_y = nearest_road.y + nearest_road.height / 2
                                pygame.draw.line(self.screen, BLUE, 
                                               (int(human_center_x), int(human_center_y)),
                                               (int(road_center_x), int(road_center_y)), 2)
                                # Then draw line from road to building (lighter blue/dashed effect)
                                pygame.draw.line(self.screen, (100, 150, 255), 
                                               (int(road_center_x), int(road_center_y)),
                                               (int(target_x), int(target_y)), 1)
                                continue
                        
                        # Already on road or no road found - draw direct line to building
                        pygame.draw.line(self.screen, BLUE, 
                                       (int(human_center_x), int(human_center_y)),
                                       (int(target_x), int(target_y)), 2)
                    else:
                        # No roads - direct line
                        pygame.draw.line(self.screen, BLUE, 
                                       (int(human_center_x), int(human_center_y)),
                                       (int(target_x), int(target_y)), 2)
            
            # Draw line to harvest_position (if exists)
            if hasattr(human, 'harvest_position') and human.harvest_position:
                target_x, target_y = human.harvest_position
                pygame.draw.line(self.screen, CYAN, 
                               (int(human_center_x), int(human_center_y)),
                               (int(target_x), int(target_y)), 1)
            
            # Draw debug info for road-following (if on road)
            if hasattr(self.game_state, 'road_list') and self.game_state.road_list:
                is_on_road = any(road.contains_point(human_center_x, human_center_y) for road in self.game_state.road_list)
                if is_on_road:
                    # Draw a small green circle on the human to show they're on a road
                    pygame.draw.circle(self.screen, GREEN, 
                                     (int(human_center_x), int(human_center_y - 15)), 3)
            
                    # Draw line to current plot (for barley farmers)
            if hasattr(human, 'current_plot_x') and human.current_plot_x is not None:
                # Find the farm this human is working on
                for farm in self.game_state.barley_farm_list:
                    if hasattr(farm, 'get_plot_position'):
                        target_x, target_y = farm.get_plot_position(human.current_plot_x, human.current_plot_y)
                        pygame.draw.line(self.screen, MAGENTA, 
                                       (int(human_center_x), int(human_center_y)),
                                       (int(target_x), int(target_y)), 1)
                        break
    
    def _draw_road_smoothing(self):
        """Draw smoothed corners for L-shaped road intersections"""
        from constants import LIGHT_GREY
        
        if not hasattr(self.game_state, 'road_list') or len(self.game_state.road_list) < 2:
            return
        
        # Find all L-shaped intersections
        processed_pairs = set()
        
        for i, road1 in enumerate(self.game_state.road_list):
            for j, road2 in enumerate(self.game_state.road_list):
                if i >= j:
                    continue
                
                # Check if roads form an L-shape (one horizontal, one vertical)
                if road1.rotation == road2.rotation:
                    continue  # Both same orientation, not an L-shape
                
                # Ensure road1 is horizontal and road2 is vertical
                if road1.rotation == 1:
                    road1, road2 = road2, road1
                
                # Now road1 is horizontal (60x30) and road2 is vertical (30x60)
                # Check if they form an L-shape by checking corner connections
                l_type = self._detect_l_shape(road1, road2)
                
                if l_type and (road1, road2) not in processed_pairs:
                    processed_pairs.add((road1, road2))
                    self._draw_l_corner_smoothing(road1, road2, l_type)
    
    def _detect_l_shape(self, horizontal_road, vertical_road):
        """
        Detect if two roads form an L-shape and return the corner type.
        Returns: 'top_right', 'top_left', 'bottom_right', 'bottom_left', or None
        """
        snap_distance = 65
        h = horizontal_road
        v = vertical_road
        
        # Horizontal road corners (60x30)
        h_tl = (h.x, h.y)
        h_tr = (h.x + h.width, h.y)
        h_bl = (h.x, h.y + h.height)
        h_br = (h.x + h.width, h.y + h.height)
        
        # Vertical road corners (30x60)
        v_tl = (v.x, v.y)
        v_tr = (v.x + v.width, v.y)
        v_bl = (v.x, v.y + v.height)
        v_br = (v.x + v.width, v.y + v.height)
        
        # Check for corner connections
        def dist(p1, p2):
            return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5
        
        # Top-right L: horizontal road's top-right corner connects to vertical road's top-left corner
        if dist(h_tr, v_tl) < snap_distance:
            return 'top_right'
        # Top-left L: horizontal road's top-left corner connects to vertical road's top-right corner
        elif dist(h_tl, v_tr) < snap_distance:
            return 'top_left'
        # Bottom-right L: horizontal road's bottom-right corner connects to vertical road's bottom-left corner
        elif dist(h_br, v_bl) < snap_distance:
            return 'bottom_right'
        # Bottom-left L: horizontal road's bottom-left corner connects to vertical road's bottom-right corner
        elif dist(h_bl, v_br) < snap_distance:
            return 'bottom_left'
        
        return None
    
    def _draw_l_corner_smoothing(self, horizontal_road, vertical_road, l_type):
        """
        Draw smoothed corner fills for an L-shaped intersection based on visual guide.
        
        Outer fillet: Cut off the corner with a GREEN triangle connecting midpoint to the CLOSEST opposite corner.
        Inner curve: Fill the inner corner with a LIGHT_GREY quadrilateral.
        """
        from constants import LIGHT_GREY, GREEN
        
        h = horizontal_road  # 60x30
        v = vertical_road    # 30x60
        
        if l_type == 'top_right':
            # Inner Fill (drawn first)
            p1 = (h.x + h.width, h.y + h.height)      # h bottom-right corner
            p2 = (h.x + h.width / 2, h.y + h.height)  # Midpoint h bottom edge
            p3 = (v.x, v.y + v.height / 2)            # Midpoint v left edge
            p4 = (v.x, v.y + v.height)                # v bottom-left corner
            pygame.draw.polygon(self.screen, LIGHT_GREY, [p1, p2, p3, p4])
            
            # Outer Cut (drawn second to appear on top)
            p1 = (h.x + h.width / 2, h.y)             # Midpoint of h's top (outer) edge
            p2 = (v.x + v.width, v.y)                 # v's top-right (CLOSEST outer) corner
            p3 = (v.x + v.width, h.y)                 # The sharp outer corner
            pygame.draw.polygon(self.screen, GREEN, [p1, p2, p3])

        elif l_type == 'top_left':
            # Inner Fill
            p1 = (h.x, h.y + h.height)                # h bottom-left corner
            p2 = (h.x + h.width / 2, h.y + h.height)  # Midpoint h bottom edge
            p3 = (v.x + v.width, v.y + v.height / 2)  # Midpoint v right edge
            p4 = (v.x + v.width, v.y + v.height)      # v bottom-right corner
            pygame.draw.polygon(self.screen, LIGHT_GREY, [p1, p2, p3, p4])
            
            # Outer Cut
            p1 = (h.x + h.width / 2, h.y)             # Midpoint of h's top (outer) edge
            p2 = (v.x, v.y)                           # v's top-left (CLOSEST outer) corner
            p3 = (v.x, h.y)                           # The sharp outer corner
            pygame.draw.polygon(self.screen, GREEN, [p1, p2, p3])

        elif l_type == 'bottom_right':
            # Inner Fill
            p1 = (h.x + h.width, h.y)                 # h top-right corner
            p2 = (h.x + h.width / 2, h.y)             # Midpoint h top edge
            p3 = (v.x, v.y + v.height / 2)            # Midpoint v left edge
            p4 = (v.x, v.y)                           # v top-left corner
            pygame.draw.polygon(self.screen, LIGHT_GREY, [p1, p2, p3, p4])

            # Outer Cut
            p1 = (h.x + h.width / 2, h.y + h.height)  # Midpoint of h's bottom (outer) edge
            p2 = (v.x + v.width, v.y + v.height)      # v's bottom-right (CLOSEST outer) corner
            p3 = (v.x + v.width, h.y + h.height)      # The sharp outer corner
            pygame.draw.polygon(self.screen, GREEN, [p1, p2, p3])
            
        elif l_type == 'bottom_left':
            # Inner Fill
            p1 = (h.x, h.y)                           # h top-left corner
            p2 = (h.x + h.width / 2, h.y)             # Midpoint h top edge
            p3 = (v.x + v.width, v.y + v.height / 2)  # Midpoint v right edge
            p4 = (v.x + v.width, v.y)                 # v top-right corner
            pygame.draw.polygon(self.screen, LIGHT_GREY, [p1, p2, p3, p4])
            
            # Outer Cut
            p1 = (h.x + h.width / 2, h.y + h.height)  # Midpoint of h's bottom (outer) edge
            p2 = (v.x, v.y + v.height)                # v's bottom-left (CLOSEST outer) corner
            p3 = (v.x, h.y + h.height)                # The sharp outer corner
            pygame.draw.polygon(self.screen, GREEN, [p1, p2, p3])
    
    def _draw_debug_road_paths(self):
        """Draw 's', 't' labels and numbered road segments in path (debug visualization)"""
        from constants import WHITE, BLACK, GREEN, RED
        
        for human in self.game_state.human_list:
            # Draw numbered road segments in the single path found by BFS
            if hasattr(human, 'road_path') and human.road_path and len(human.road_path) > 1:
                for index, road in enumerate(human.road_path):
                    # Skip the first road (it has 's' label)
                    if index == 0:
                        continue
                    
                    # Skip the last road (it has 't' label)
                    if index == len(human.road_path) - 1:
                        if hasattr(human, 'target_road') and road == human.target_road:
                            continue
                    
                    # Number is the index in the path (since index 0 is 's')
                    number_to_show = index
                    
                    # Calculate center of road
                    road_center_x = road.x + road.width / 2
                    road_center_y = road.y + road.height / 2
                    
                    # Draw background circle for better visibility
                    pygame.draw.circle(self.screen, BLACK, 
                                     (int(road_center_x), int(road_center_y)), 12)
                    pygame.draw.circle(self.screen, WHITE, 
                                     (int(road_center_x), int(road_center_y)), 12, 2)
                    
                    # Draw number on road
                    font = pygame.font.Font(None, 24)
                    text_surface = font.render(str(number_to_show), True, WHITE)
                    text_rect = text_surface.get_rect(center=(int(road_center_x), int(road_center_y)))
                    self.screen.blit(text_surface, text_rect)
            
            # Draw 's' label on start road (closest to AI current position)
            # Offset to top-left of road center so it doesn't overlap with 't'
            if hasattr(human, 'start_road') and human.start_road:
                road_center_x = human.start_road.x + human.start_road.width / 2
                road_center_y = human.start_road.y + human.start_road.height / 2
                
                # Offset 's' to top-left
                label_x = road_center_x - 15
                label_y = road_center_y - 15
                
                # Draw background circle for better visibility
                pygame.draw.circle(self.screen, BLACK, 
                                 (int(label_x), int(label_y)), 15)
                pygame.draw.circle(self.screen, GREEN, 
                                 (int(label_x), int(label_y)), 15, 2)
                
                # Draw 's' text
                font = pygame.font.Font(None, 28)
                text_surface = font.render('s', True, GREEN)
                text_rect = text_surface.get_rect(center=(int(label_x), int(label_y)))
                self.screen.blit(text_surface, text_rect)
            
            # Draw 't' label on target road (closest to target)
            # Offset to bottom-right of road center so it doesn't overlap with 's'
            if hasattr(human, 'target_road') and human.target_road:
                road_center_x = human.target_road.x + human.target_road.width / 2
                road_center_y = human.target_road.y + human.target_road.height / 2
                
                # Offset 't' to bottom-right
                label_x = road_center_x + 15
                label_y = road_center_y + 15
                
                # Draw background circle for better visibility
                pygame.draw.circle(self.screen, BLACK, 
                                 (int(label_x), int(label_y)), 15)
                pygame.draw.circle(self.screen, RED, 
                                 (int(label_x), int(label_y)), 15, 2)
                
                # Draw 't' text
                font = pygame.font.Font(None, 28)
                text_surface = font.render('t', True, RED)
                text_rect = text_surface.get_rect(center=(int(label_x), int(label_y)))
                self.screen.blit(text_surface, text_rect)
    
    def _get_target_position(self, target):
        """Get the center position of a target entity/building"""
        if hasattr(target, 'x') and hasattr(target, 'y'):
            if hasattr(target, 'width') and hasattr(target, 'height'):
                # Building/entity with width/height
                return (target.x + target.width / 2, target.y + target.height / 2)
            elif hasattr(target, 'size'):
                # Human with size
                return (target.x + target.size / 2, target.y + target.size / 2)
            elif hasattr(target, 'radius'):
                # Circular entity (silo)
                return (target.x + target.radius, target.y + target.radius)
            else:
                # Just x, y
                return (target.x, target.y)
        return (None, None)
    
    def _draw_ui(self):
        """Draw all UI elements"""
        # Draw build mode preview
        self.build_mode_renderer.draw(self.screen, self.game_state)
        
        # Draw debug herd boundary
        self.hud.draw_debug_herd_boundary(self.screen, self.game_state)
        
        # Draw box selection
        self.hud.draw_box_selection(self.screen, self.game_state)
        
        # Draw context menus
        self.context_menu_renderer.draw_all(self.screen, self.game_state)
        
        # Draw employment menu
        self.employment_menu.draw(self.screen, self.game_state)
        
        # Draw harvest UI (messages and cursor)
        self.harvest_system.draw_harvest_ui(self.screen)
        self.harvest_system.draw_harvest_cursor(self.screen)
        
        # Draw HUDs (must be last to be on top)
        self.hud.draw(self.screen, self.game_state, self.day_cycle, self.resource_system)
        self.hud_low.draw(self.screen, self.game_state)
        
        # Draw dialogue boxes on top of everything (including player)
        if self.game_state.show_family_tree_dialogue:
            self.hud_low._draw_family_tree_dialogue(self.screen, self.game_state)
        if self.game_state.show_profile_info_dialogue:
            self.hud_low._draw_profile_info_dialogue(self.screen, self.game_state)
        
        # Draw darkness overlay for dusk/dawn (on top of everything)
        self._draw_darkness_overlay()
    
    def _draw_player(self):
        """Draw the player square"""
        pygame.draw.rect(
            self.screen, 
            BLUE, 
            (self.game_state.player_x, self.game_state.player_y, PLAYER_SIZE, PLAYER_SIZE)
        )
    
    def _draw_darkness_overlay(self):
        """Draw darkness overlay for dusk/dawn transition"""
        alpha = self.day_cycle.get_darkness_overlay_alpha()
        if alpha > 0:
            # Create a semi-transparent black surface
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
    
    def _cleanup(self):
        """Cleanup and exit"""
        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()

