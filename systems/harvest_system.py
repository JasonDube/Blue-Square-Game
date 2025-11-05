"""
Harvest system - handles human harvesting of resources
"""
import pygame
import math
from constants import *
from utils.geometry import distance
from systems.resource_system import ResourceType


class HarvestSystem:
    """Manages harvesting behavior for humans"""
    
    def __init__(self, resource_system):
        self.harvest_cursor_active = False
        self.show_select_target_msg = False
        self.select_target_timer = 0.0
        self.error_message = None
        self.error_message_timer = 0.0
        self.resource_system = resource_system
    
    def activate_harvest_cursor(self):
        """Activate harvest cursor mode"""
        self.harvest_cursor_active = True
        self.show_select_target_msg = True
        self.select_target_timer = 1.0
    
    def deactivate_harvest_cursor(self):
        """Deactivate harvest cursor mode"""
        self.harvest_cursor_active = False
        self.show_select_target_msg = False
        self.select_target_timer = 0.0
        pygame.mouse.set_visible(True)
    
    def show_error(self, message, duration=3.0):
        """Show an error message"""
        self.error_message = message
        self.error_message_timer = duration
    
    def update(self, dt, game_state):
        """Update harvest system timers"""
        if self.show_select_target_msg:
            self.select_target_timer -= dt
            if self.select_target_timer <= 0:
                self.show_select_target_msg = False
        
        if self.error_message:
            self.error_message_timer -= dt
            if self.error_message_timer <= 0:
                self.error_message = None
        
        for human in game_state.human_list:
            if human.state == "harvest":
                self._update_harvesting_human(human, dt, game_state)
    
    def _update_harvesting_human(self, human, dt, game_state):
        """Update a human that is harvesting"""
        if human.harvest_target and human.harvest_target.is_depleted():
            human.state = "stay"
            human.harvest_target = None
            human.harvest_timer = 0.0
            human.carrying_resource = False
            human.target_building = None
            human.resource_type = None
            human.harvest_position = None
            return
        
        if human.carrying_resource:
            self._return_to_building(human, dt, game_state)
        elif human.harvest_target:
            self._harvest_resource(human, dt, game_state)
    
    def _harvest_resource(self, human, dt, game_state):
        """Human harvests the resource"""
        resource = human.harvest_target
        
        target_x = human.harvest_position[0] if human.harvest_position else resource.x
        target_y = human.harvest_position[1] if human.harvest_position else resource.y
        
        dist = distance(human.x + human.size/2, human.y + human.size/2, target_x, target_y)
        
        if dist > 5:
            self._move_toward_target_with_roads(human, target_x, target_y, dt, game_state, arrival_distance=5)
        else:
            resource.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                resource.harvest()
                resource.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_building(self, human, dt, game_state):
        """Human returns to building to deposit resource"""
        building = human.target_building
        
        if not building:
            human.state = "stay"
            human.harvest_target = None
            human.carrying_resource = False
            human.target_building = None
            human.resource_type = None
            human.harvest_position = None
            return
        
        dist = distance(human.x + human.size/2, human.y + human.size/2,
                       building.x + building.width/2, building.y + building.height/2)
        
        if dist > 20:
            building_center_x = building.x + building.width/2
            building_center_y = building.y + building.height/2
            self._move_toward_target_with_roads(human, building_center_x, building_center_y, dt, game_state, arrival_distance=20)
        else:
            deposited = False
            
            if human.resource_type == ResourceType.LOG:
                if building.add_log():
                    self.resource_system.add_resource(ResourceType.LOG, 1)
                    deposited = True
            elif human.resource_type == ResourceType.STONE:
                if building.add_stone():
                    self.resource_system.add_resource(ResourceType.STONE, 1)
                    deposited = True
            elif human.resource_type == ResourceType.IRON:
                if building.add_iron():
                    self.resource_system.add_resource(ResourceType.IRON, 1)
                    deposited = True
            elif human.resource_type == ResourceType.SALT:
                if building.add_salt():
                    self.resource_system.add_resource(ResourceType.SALT, 1)
                    deposited = True
            
            if deposited:
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                if human.harvest_target and not human.harvest_target.is_depleted():
                    pass
                else:
                    human.state = "stay"
                    human.harvest_target = None
                    human.target_building = None
                    human.resource_type = None
                    human.harvest_position = None
            else:
                human.state = "stay"
                human.harvest_target = None
                human.carrying_resource = False
                human.target_building = None
                human.resource_type = None
                human.harvest_position = None
                self.show_error("Storage building is full")
    
    def _check_collisions(self, human, game_state):
        """Simple collision check for harvesting humans"""
        for pen in game_state.pen_list:
            if pen.check_collision_player(human.x, human.y):
                return True
        for townhall in game_state.townhall_list:
            if townhall.check_collision_player(human.x, human.y):
                return True
        for lumber_yard in game_state.lumber_yard_list:
            if lumber_yard.check_collision_player(human.x, human.y):
                return True
        for stone_yard in game_state.stone_yard_list:
            if stone_yard.check_collision_player(human.x, human.y):
                return True
        for iron_yard in game_state.iron_yard_list:
            if iron_yard.check_collision_player(human.x, human.y):
                return True
        return False
    
    def _find_nearest_road(self, pos_x, pos_y, game_state, max_distance=100):
        """Find nearest road segment to a position"""
        if not hasattr(game_state, 'road_list') or not game_state.road_list:
            return None, float('inf')
        
        nearest_road = None
        nearest_dist = float('inf')
        
        for road in game_state.road_list:
            road_center_x = road.x + road.width / 2
            road_center_y = road.y + road.height / 2
            dist = distance(pos_x, pos_y, road_center_x, road_center_y)
            
            if dist < nearest_dist and dist < max_distance:
                nearest_dist = dist
                nearest_road = road
        
        return nearest_road, nearest_dist
    
    def _is_on_road(self, pos_x, pos_y, game_state):
        """Check if a position is on a road"""
        if not hasattr(game_state, 'road_list') or not game_state.road_list:
            return False
        
        for road in game_state.road_list:
            if road.contains_point(pos_x, pos_y):
                return True
        return False
    
    def _get_connected_roads(self, road, game_state):
        """Get all roads connected to this road (within snap distance)"""
        if not hasattr(game_state, 'road_list') or not game_state.road_list:
            return []
        
        connected = []
        snap_distance = 65  # Reduced from 80. Max segment length is 60, so this prevents skipping.
        
        road_center_x = road.x + road.width / 2
        road_center_y = road.y + road.height / 2
        
        for other_road in game_state.road_list:
            if other_road == road:
                continue
            
            other_center_x = other_road.x + other_road.width / 2
            other_center_y = other_road.y + other_road.height / 2
            dist = distance(road_center_x, road_center_y, other_center_x, other_center_y)
            
            if dist < snap_distance:
                connected.append(other_road)
        
        return connected
    
    def _find_path_between_roads(self, start_road, target_road, game_state, max_path_length=50):
        """Find the shortest path of connected roads from start_road to target_road using BFS."""
        if not start_road or not target_road:
            return []
        
        if start_road == target_road:
            return [start_road]
        
        from collections import deque
        
        # BFS to find path from start to target
        queue = deque([(start_road, [start_road])])
        visited = {start_road}
        
        while queue:
            current_road, path = queue.popleft()
            
            if len(path) >= max_path_length:
                continue
            
            connected = self._get_connected_roads(current_road, game_state)
            for next_road in connected:
                if next_road == target_road:
                    return path + [next_road]  # Path found
                
                if next_road not in visited:
                    visited.add(next_road)
                    new_path = path + [next_road]
                    queue.append((next_road, new_path))
        
        return []  # No path found
    
    def _find_road_path_toward_destination(self, start_road, dest_x, dest_y, game_state, max_path_length=50):
        """Find a path of connected roads leading toward destination"""
        if not start_road:
            return []
        
        # Use A*-like algorithm to find complete path
        from collections import deque
        
        # BFS to find path to target road
        target_road, _ = self._find_nearest_road(dest_x, dest_y, game_state, max_distance=200)
        if not target_road:
            # No target road found, return path toward destination
            print(f"[HARVEST] No target road found, using greedy path")
            path = self._find_path_toward_point(start_road, dest_x, dest_y, game_state, max_path_length)
            print(f"[HARVEST] Greedy path length: {len(path)}")
            return path
        
        if start_road == target_road:
            print(f"[HARVEST] Start and target are same road, returning single segment")
            return [start_road]
        
        print(f"[HARVEST] BFS: start_road at ({start_road.x}, {start_road.y}), target_road at ({target_road.x}, {target_road.y})")
        
        # BFS to find path from start to target road
        queue = deque([(start_road, [start_road])])
        visited = {start_road}
        
        while queue:
            current_road, path = queue.popleft()
            
            # Check path length limit
            if len(path) >= max_path_length:
                continue
            
            if current_road == target_road:
                print(f"[HARVEST] BFS found path with {len(path)} segments")
                return path
            
            connected = self._get_connected_roads(current_road, game_state)
            print(f"[HARVEST] Road at ({current_road.x}, {current_road.y}) has {len(connected)} connected roads")
            for next_road in connected:
                if next_road not in visited:
                    visited.add(next_road)
                    new_path = path + [next_road]
                    queue.append((next_road, new_path))
        
        # If no direct path found, return path toward target
        print(f"[HARVEST] BFS failed, using greedy fallback")
        path = self._find_path_toward_point(start_road, dest_x, dest_y, game_state, max_path_length)
        print(f"[HARVEST] Greedy fallback path length: {len(path)}")
        return path
    
    def _find_path_toward_point(self, start_road, dest_x, dest_y, game_state, max_path_length=50):
        """Find a greedy path toward a point (fallback when no target road found)"""
        path = [start_road]
        visited = {start_road}
        current_road = start_road
        
        for _ in range(max_path_length):
            connected = self._get_connected_roads(current_road, game_state)
            
            best_road = None
            best_dist = float('inf')
            
            for next_road in connected:
                if next_road in visited:
                    continue
                
                next_center_x = next_road.x + next_road.width / 2
                next_center_y = next_road.y + next_road.height / 2
                dist_to_dest = distance(next_center_x, next_center_y, dest_x, dest_y)
                
                if dist_to_dest < best_dist:
                    best_dist = dist_to_dest
                    best_road = next_road
            
            if best_road:
                current_center_x = current_road.x + current_road.width / 2
                current_center_y = current_road.y + current_road.height / 2
                current_dist = distance(current_center_x, current_center_y, dest_x, dest_y)
                
                if best_dist < current_dist:
                    path.append(best_road)
                    visited.add(best_road)
                    current_road = best_road
                else:
                    break
            else:
                break
        
        return path
    
    def _move_toward_target_with_roads(self, human, target_x, target_y, dt, game_state, arrival_distance=20):
        """Move human toward target, using roads when available."""
        human_center_x = human.x + human.size / 2
        human_center_y = human.y + human.size / 2

        # --- Path Calculation (only if target has changed) ---
        if (target_x, target_y) != human.pathing_target_pos:
            human.pathing_target_pos = (target_x, target_y)
            human.road_path = []
            human.current_road_index = 0
            human.start_road = None
            human.target_road = None

            if hasattr(game_state, 'road_list') and game_state.road_list:
                start_road, _ = self._find_nearest_road(human_center_x, human_center_y, game_state, max_distance=float('inf'))
                human.start_road = start_road

                final_target_x, final_target_y = target_x, target_y
                if hasattr(human, 'target_building') and human.target_building:
                    building = human.target_building
                    if hasattr(building, 'width') and hasattr(building, 'height'):
                        final_target_x = building.x + building.width / 2
                        final_target_y = building.y + building.height / 2
                    elif hasattr(building, 'radius'):
                        final_target_x = building.x + building.radius
                        final_target_y = building.y + building.radius
                
                target_road, _ = self._find_nearest_road(final_target_x, final_target_y, game_state, max_distance=float('inf'))
                human.target_road = target_road

                if human.start_road and human.target_road:
                    human.road_path = self._find_path_between_roads(human.start_road, human.target_road, game_state)

        # --- Movement Logic ---
        move_target_x, move_target_y = target_x, target_y
        is_on_road_path = False

        if human.road_path:
            is_on_road_path = True
            if human.current_road_index >= len(human.road_path):
                # Path is complete, move to the final destination
                is_on_road_path = False
            else:
                # Get current road segment from path
                current_segment = human.road_path[human.current_road_index]
                move_target_x = current_segment.x + current_segment.width / 2
                move_target_y = current_segment.y + current_segment.height / 2
                
                dist_to_segment_center = distance(human_center_x, human_center_y, move_target_x, move_target_y)
                
                if dist_to_segment_center < 15: # Arrival at segment center
                    human.current_road_index += 1
        
        # --- Actual Movement ---
        dist_to_final_target = distance(human_center_x, human_center_y, target_x, target_y)
        if not is_on_road_path and dist_to_final_target < arrival_distance:
            return  # Arrived at final destination

        dist_to_move_target = distance(human_center_x, human_center_y, move_target_x, move_target_y)
        
        if dist_to_move_target > 1:
            dx = move_target_x - human_center_x
            dy = move_target_y - human_center_y
            norm = dist_to_move_target
            dx = (dx / norm) * human.speed
            dy = (dy / norm) * human.speed
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
    
    def _calculate_harvest_positions(self, resource, game_state):
        """Calculate positions around a resource for multiple workers"""
        assigned_count = 0
        for human in game_state.human_list:
            if human.harvest_target == resource:
                assigned_count += 1
        
        positions = []
        radius = 30
        
        for i in range(assigned_count):
            angle = (2 * math.pi * i) / max(assigned_count, 1)
            pos_x = resource.x + radius * math.cos(angle)
            pos_y = resource.y + radius * math.sin(angle)
            positions.append((pos_x, pos_y))
        
        return positions
    
    def assign_harvest_target(self, human, resource, game_state):
        """Assign a resource as harvest target for a human"""
        resource_type = None
        available_building = None
        
        from entities.tree import Tree
        from entities.rock import Rock
        from entities.ironmine import IronMine
        from entities.salt import Salt
        
        if isinstance(resource, Tree):
            resource_type = ResourceType.LOG
            for lumber_yard in game_state.lumber_yard_list:
                if lumber_yard.can_accept_resource():
                    available_building = lumber_yard
                    break
            if not available_building:
                self.show_error("No lumber yard with space")
                return False
        
        elif isinstance(resource, Rock):
            resource_type = ResourceType.STONE
            for stone_yard in game_state.stone_yard_list:
                if stone_yard.can_accept_resource():
                    available_building = stone_yard
                    break
            if not available_building:
                self.show_error("No stone yard with space")
                return False
        
        elif isinstance(resource, IronMine):
            resource_type = ResourceType.IRON
            for iron_yard in game_state.iron_yard_list:
                if iron_yard.can_accept_resource():
                    available_building = iron_yard
                    break
            if not available_building:
                self.show_error("No iron yard with space")
                return False
        
        elif isinstance(resource, Salt):
            resource_type = ResourceType.SALT
            for salt_yard in game_state.salt_yard_list:
                if salt_yard.can_accept_resource():
                    available_building = salt_yard
                    break
            if not available_building:
                self.show_error("No salt yard with space")
                return False
        
        else:
            return False
        
        if human.gender != "male":
            return False
        
        positions = self._calculate_harvest_positions(resource, game_state)
        
        worker_index = 0
        for h in game_state.human_list:
            if h.harvest_target == resource and h != human:
                worker_index += 1
        
        if worker_index < len(positions):
            harvest_position = positions[worker_index]
        else:
            harvest_position = (resource.x, resource.y)
        
        human.state = "harvest"
        human.harvest_target = resource
        human.target_building = available_building
        human.resource_type = resource_type
        human.harvest_timer = 0.0
        human.carrying_resource = False
        human.harvest_position = harvest_position
        
        return True
    
    def get_hovered_resource(self, mouse_x, mouse_y, tree_list, rock_list, iron_mine_list, salt_list=None):
        """Get any harvestable resource under mouse cursor"""
        for tree in tree_list:
            if not tree.is_depleted() and tree.contains_point(mouse_x, mouse_y):
                return tree
        
        for rock in rock_list:
            if not rock.is_depleted() and rock.contains_point(mouse_x, mouse_y):
                return rock
        
        for iron_mine in iron_mine_list:
            if not iron_mine.is_depleted() and iron_mine.contains_point(mouse_x, mouse_y):
                return iron_mine
        
        if salt_list:
            for salt in salt_list:
                if not salt.is_depleted() and salt.contains_point(mouse_x, mouse_y):
                    return salt
        
        return None
    
    def draw_harvest_ui(self, screen):
        """Draw harvest-related UI elements"""
        if self.show_select_target_msg:
            font = pygame.font.Font(None, 36)
            text = "Select Target"
            text_surface = font.render(text, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, YELLOW, bg_rect, 2)
            screen.blit(text_surface, text_rect)
        
        if self.error_message:
            font = pygame.font.Font(None, 32)
            text_surface = font.render(self.error_message, True, RED)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, BLACK, bg_rect)
            pygame.draw.rect(screen, RED, bg_rect, 2)
            screen.blit(text_surface, text_rect)
    
    def draw_harvest_cursor(self, screen):
        """Draw crosshair cursor"""
        if not self.harvest_cursor_active:
            return
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        crosshair_size = 15
        
        pygame.draw.line(screen, WHITE, 
                        (mouse_x - crosshair_size, mouse_y), 
                        (mouse_x + crosshair_size, mouse_y), 2)
        pygame.draw.line(screen, WHITE, 
                        (mouse_x, mouse_y - crosshair_size), 
                        (mouse_x, mouse_y + crosshair_size), 2)
        pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 3, 1)
    
    def draw_harvesting_human(self, screen, human):
        """Draw tool when human is harvesting"""
        if human.state != "harvest" or not human.harvest_target:
            return
        
        resource = human.harvest_target
        
        if not human.carrying_resource:
            harvest_pos = human.harvest_position if human.harvest_position else (resource.x, resource.y)
            dist = distance(human.x + human.size/2, human.y + human.size/2,
                           harvest_pos[0], harvest_pos[1])
            
            if dist <= 10:
                tool_x = int(human.x + human.size/2 + (resource.x - human.x) * 0.5)
                tool_y = int(human.y + human.size/2 + (resource.y - human.y) * 0.5)
                pygame.draw.circle(screen, GRAY, (tool_x, tool_y), HARVEST_TOOL_SIZE // 2)
