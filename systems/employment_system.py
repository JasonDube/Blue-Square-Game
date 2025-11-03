"""
Employment system - manages automatic work behavior for employed humans
"""
import random
import math
from constants import *
from utils.geometry import distance
from utils.pathfinding import get_road_path_target


class EmploymentSystem:
    """Handles automatic work behavior for employed humans"""
    
    def __init__(self, resource_system):
        self.resource_system = resource_system
    
    def update(self, dt, game_state):
        """Update all employed humans"""
        for human in game_state.human_list:
            if human.state == "employed" and human.job:
                # Check if in downtime mode
                if human.is_downtime:
                    self._update_downtime(human, dt, game_state)
                else:
                    self._update_employed_human(human, dt, game_state)
    
    def _update_employed_human(self, human, dt, game_state):
        """Update a single employed human"""
        if human.job == "lumberjack":
            self._update_lumberjack(human, dt, game_state)
        elif human.job == "miner":
            self._update_miner(human, dt, game_state)
        elif human.job == "stoneworker":
            self._update_stoneworker(human, dt, game_state)
        elif human.job == "saltworker":
            self._update_saltworker(human, dt, game_state)
        elif human.job == "shearer":
            self._update_shearer(human, dt, game_state)
        elif human.job == "barleyfarmer":
            self._update_barleyfarmer(human, dt, game_state)
        elif human.job == "miller":
            self._update_miller(human, dt, game_state)
        # Future jobs: elif human.job == "farmer": ...
    
    def _update_lumberjack(self, human, dt, game_state):
        """Update a lumberjack - automatically harvests trees"""
        # Check if work is available
        has_trees = any(not tree.is_depleted() for tree in game_state.tree_list)
        has_space = any(ly.can_accept_resource() for ly in game_state.lumber_yard_list)
        if not has_trees or not has_space:
            self._enter_downtime(human, game_state)
            return
        
        # If carrying resource, return to lumber yard
        if human.carrying_resource:
            self._return_to_lumber_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_tree(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_tree_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_tree_target(human, game_state)
    
    def _find_tree_target(self, human, game_state):
        """Find nearest tree to harvest"""
        nearest_tree = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for tree in game_state.tree_list:
            if tree.is_depleted():
                continue
            
            dist = distance(human_x, human_y, tree.x, tree.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's a lumber yard with space
                has_space = any(ly.can_accept_resource() for ly in game_state.lumber_yard_list)
                if has_space:
                    nearest_tree = tree
                    nearest_dist = dist
        
        if nearest_tree:
            # Assign the tree
            human.work_target = nearest_tree
            human.harvest_target = nearest_tree
            human.harvest_timer = 0.0
            
            # Calculate harvest position around tree
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_tree.x + radius * math.cos(angle),
                nearest_tree.y + radius * math.sin(angle)
            )
            
            # Find lumber yard
            from systems.resource_system import ResourceType
            for lumber_yard in game_state.lumber_yard_list:
                if lumber_yard.can_accept_resource():
                    human.target_building = lumber_yard
                    human.resource_type = ResourceType.LOG
                    break
    
    def _harvest_tree(self, human, dt, game_state):
        """Harvest the assigned tree"""
        # Use harvest_target if available, otherwise fall back to work_target
        tree = human.harvest_target if human.harvest_target else human.work_target
        
        if not tree:
            # No tree assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                tree.x + radius * math.cos(angle),
                tree.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else tree.x
        target_y = human.harvest_position[1] if human.harvest_position else tree.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the tree
            tree.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                tree.harvest()
                tree.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_lumber_yard(self, human, game_state):
        """Return to lumber yard to deposit log"""
        from entities.lumberyard import LumberYard
        
        building = human.target_building
        
        # Validate that building is actually a lumber yard
        if not building or not isinstance(building, LumberYard):
            # Find a valid lumber yard
            for lumber_yard in game_state.lumber_yard_list:
                if lumber_yard.can_accept_resource():
                    building = lumber_yard
                    human.target_building = lumber_yard
                    break
            
            if not building or not isinstance(building, LumberYard):
                # No valid lumber yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            building_x = building.x + building.width/2
            building_y = building.y + building.height/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, building_x, building_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_log():
                self.resource_system.add_resource(ResourceType.LOG, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if tree still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to tree
                    pass
                else:
                    # Tree depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                    # Building full - stop working
                    self._reset_worker(human)
    
    def _update_miner(self, human, dt, game_state):
        """Update a miner - automatically harvests iron mines"""
        # Check if work is available
        has_mines = any(not mine.is_depleted() for mine in game_state.iron_mine_list)
        has_space = any(iy.can_accept_resource() for iy in game_state.iron_yard_list)
        if not has_mines or not has_space:
            self._enter_downtime(human, game_state)
            return
        
        # If carrying resource, return to iron yard
        if human.carrying_resource:
            self._return_to_iron_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_iron_mine(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_iron_mine_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_iron_mine_target(human, game_state)
    
    def _find_iron_mine_target(self, human, game_state):
        """Find nearest iron mine to harvest"""
        nearest_mine = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for iron_mine in game_state.iron_mine_list:
            if iron_mine.is_depleted():
                continue
            
            dist = distance(human_x, human_y, iron_mine.x, iron_mine.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's an iron yard with space
                has_space = any(iy.can_accept_resource() for iy in game_state.iron_yard_list)
                if has_space:
                    nearest_mine = iron_mine
                    nearest_dist = dist
        
        if nearest_mine:
            # Assign the mine
            human.work_target = nearest_mine
            human.harvest_target = nearest_mine
            human.harvest_timer = 0.0
            
            # Calculate harvest position around mine
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_mine.x + radius * math.cos(angle),
                nearest_mine.y + radius * math.sin(angle)
            )
            
            # Find iron yard
            from systems.resource_system import ResourceType
            for iron_yard in game_state.iron_yard_list:
                if iron_yard.can_accept_resource():
                    human.target_building = iron_yard
                    human.resource_type = ResourceType.IRON
                    break
    
    def _harvest_iron_mine(self, human, dt, game_state):
        """Harvest the assigned iron mine"""
        # Use harvest_target if available, otherwise fall back to work_target
        mine = human.harvest_target if human.harvest_target else human.work_target
        
        if not mine:
            # No mine assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                mine.x + radius * math.cos(angle),
                mine.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else mine.x
        target_y = human.harvest_position[1] if human.harvest_position else mine.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the mine
            mine.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                mine.harvest()
                mine.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_iron_yard(self, human, game_state):
        """Return to iron yard to deposit iron"""
        from entities.ironyard import IronYard
        
        building = human.target_building
        
        # Validate that building is actually an iron yard
        if not building or not isinstance(building, IronYard):
            # Find a valid iron yard
            for iron_yard in game_state.iron_yard_list:
                if iron_yard.can_accept_resource():
                    building = iron_yard
                    human.target_building = iron_yard
                    break
            
            if not building or not isinstance(building, IronYard):
                # No valid iron yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            building_x = building.x + building.width/2
            building_y = building.y + building.height/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, building_x, building_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_iron():
                self.resource_system.add_resource(ResourceType.IRON, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if mine still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to mine
                    pass
                else:
                    # Mine depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _update_stoneworker(self, human, dt, game_state):
        """Update a stoneworker - automatically harvests rocks"""
        # Check if work is available
        has_rocks = any(not rock.is_depleted() for rock in game_state.rock_list)
        has_space = any(sy.can_accept_resource() for sy in game_state.stone_yard_list)
        if not has_rocks or not has_space:
            self._enter_downtime(human, game_state)
            return
        
        # If carrying resource, return to stone yard
        if human.carrying_resource:
            self._return_to_stone_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_rock(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_rock_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_rock_target(human, game_state)
    
    def _find_rock_target(self, human, game_state):
        """Find nearest rock to harvest"""
        nearest_rock = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for rock in game_state.rock_list:
            if rock.is_depleted():
                continue
            
            dist = distance(human_x, human_y, rock.x, rock.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's a stone yard with space
                has_space = any(sy.can_accept_resource() for sy in game_state.stone_yard_list)
                if has_space:
                    nearest_rock = rock
                    nearest_dist = dist
        
        if nearest_rock:
            # Assign the rock
            human.work_target = nearest_rock
            human.harvest_target = nearest_rock
            human.harvest_timer = 0.0
            
            # Calculate harvest position around rock
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_rock.x + radius * math.cos(angle),
                nearest_rock.y + radius * math.sin(angle)
            )
            
            # Find stone yard
            from systems.resource_system import ResourceType
            for stone_yard in game_state.stone_yard_list:
                if stone_yard.can_accept_resource():
                    human.target_building = stone_yard
                    human.resource_type = ResourceType.STONE
                    break
    
    def _harvest_rock(self, human, dt, game_state):
        """Harvest the assigned rock"""
        # Use harvest_target if available, otherwise fall back to work_target
        rock = human.harvest_target if human.harvest_target else human.work_target
        
        if not rock:
            # No rock assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                rock.x + radius * math.cos(angle),
                rock.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else rock.x
        target_y = human.harvest_position[1] if human.harvest_position else rock.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the rock
            rock.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                rock.harvest()
                rock.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_stone_yard(self, human, game_state):
        """Return to stone yard to deposit stone"""
        from entities.stoneyard import StoneYard
        
        building = human.target_building
        
        # Validate that building is actually a stone yard
        if not building or not isinstance(building, StoneYard):
            # Find a valid stone yard
            for stone_yard in game_state.stone_yard_list:
                if stone_yard.can_accept_resource():
                    building = stone_yard
                    human.target_building = stone_yard
                    break
            
            if not building or not isinstance(building, StoneYard):
                # No valid stone yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            building_x = building.x + building.width/2
            building_y = building.y + building.height/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, building_x, building_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_stone():
                self.resource_system.add_resource(ResourceType.STONE, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if rock still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to rock
                    pass
                else:
                    # Rock depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _update_saltworker(self, human, dt, game_state):
        """Update a saltworker - automatically harvests salt deposits"""
        # If carrying resource, return to salt yard
        if human.carrying_resource:
            self._return_to_salt_yard(human, game_state)
            return
        
        # If has a target and it's still valid, continue harvesting
        if human.work_target and not human.work_target.is_depleted():
            self._harvest_salt(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_salt_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_salt_target(human, game_state)
    
    def _find_salt_target(self, human, game_state):
        """Find nearest salt deposit to harvest"""
        nearest_salt = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for salt in game_state.salt_list:
            if salt.is_depleted():
                continue
            
            dist = distance(human_x, human_y, salt.x, salt.y)
            if dist < AUTO_WORK_SEARCH_RADIUS and dist < nearest_dist:
                # Check if there's a salt yard with space
                has_space = any(sy.can_accept_resource() for sy in game_state.salt_yard_list)
                if has_space:
                    nearest_salt = salt
                    nearest_dist = dist
        
        if nearest_salt:
            # Assign the salt
            human.work_target = nearest_salt
            human.harvest_target = nearest_salt
            human.harvest_timer = 0.0
            
            # Calculate harvest position around salt
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                nearest_salt.x + radius * math.cos(angle),
                nearest_salt.y + radius * math.sin(angle)
            )
            
            # Find salt yard
            from systems.resource_system import ResourceType
            for salt_yard in game_state.salt_yard_list:
                if salt_yard.can_accept_resource():
                    human.target_building = salt_yard
                    human.resource_type = ResourceType.SALT
                    break
    
    def _harvest_salt(self, human, dt, game_state):
        """Harvest the assigned salt deposit"""
        # Use harvest_target if available, otherwise fall back to work_target
        salt = human.harvest_target if human.harvest_target else human.work_target
        
        if not salt:
            # No salt assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 30
            human.harvest_position = (
                salt.x + radius * math.cos(angle),
                salt.y + radius * math.sin(angle)
            )
        
        # Move to harvest position
        target_x = human.harvest_position[0] if human.harvest_position else salt.x
        target_y = human.harvest_position[1] if human.harvest_position else salt.y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at harvest position yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At harvest position, harvest the salt
            salt.being_harvested = True
            human.harvest_timer += dt
            
            if human.harvest_timer >= HARVEST_TIME:
                # Finished harvesting
                salt.harvest()
                salt.being_harvested = False
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_salt_yard(self, human, game_state):
        """Return to salt yard to deposit salt"""
        from entities.saltyard import SaltYard
        
        building = human.target_building
        
        # Validate that building is actually a salt yard
        if not building or not isinstance(building, SaltYard):
            # Find a valid salt yard
            for salt_yard in game_state.salt_yard_list:
                if salt_yard.can_accept_resource():
                    building = salt_yard
                    human.target_building = salt_yard
                    break
            
            if not building or not isinstance(building, SaltYard):
                # No valid salt yard - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            building_x = building.x + building.width/2
            building_y = building.y + building.height/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, building_x, building_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_salt():
                self.resource_system.add_resource(ResourceType.SALT, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working if salt still has health
                if human.work_target and not human.work_target.is_depleted():
                    # Go back to salt
                    pass
                else:
                    # Salt depleted, find new one
                    human.work_target = None
                    human.harvest_target = None
                    human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _update_shearer(self, human, dt, game_state):
        """Update a shearer - automatically shears sheep"""
        # Check if work is available
        has_sheep = any(sheep.has_wool for sheep in game_state.sheep_list)
        has_space = any(ws.can_accept_resource() for ws in game_state.wool_shed_list)
        if not has_sheep or not has_space:
            self._enter_downtime(human, game_state)
            return
        
        # If carrying resource, return to wool shed
        if human.carrying_resource:
            self._return_to_wool_shed(human, game_state)
            return
        
        # If has a target and it's still valid (has wool), continue shearing
        if human.work_target and hasattr(human.work_target, 'has_wool') and human.work_target.has_wool:
            self._shear_sheep(human, dt, game_state)
            return
        
        # Need to find a new target - check immediately first, then use interval
        if human.work_timer == 0.0:
            # First check - try to find target immediately
            self._find_sheep_target(human, game_state)
            if human.work_target:
                # Found target, start working
                return
        
        # If no target found, wait and try again
        human.work_timer += dt
        if human.work_timer >= AUTO_WORK_INTERVAL:
            human.work_timer = 0.0
            self._find_sheep_target(human, game_state)
    
    def _find_sheep_target(self, human, game_state):
        """Find nearest unsheared sheep"""
        nearest_sheep = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        # Check if there's at least one wool shed built (need somewhere to deposit)
        if len(game_state.wool_shed_list) == 0:
            return  # No wool sheds built yet, can't work
        
        for sheep in game_state.sheep_list:
            if not sheep.has_wool:
                continue  # Skip sheep without wool
            
            dist = distance(human_x, human_y, sheep.x + sheep.width/2, sheep.y + sheep.height/2)
            # No proximity limit - can find sheep at any distance
            if dist < nearest_dist:
                # Find nearest sheep with wool (can find even if sheds are full)
                nearest_sheep = sheep
                nearest_dist = dist
        
        if nearest_sheep:
            # Assign the sheep
            human.work_target = nearest_sheep
            human.harvest_target = nearest_sheep
            human.harvest_timer = 0.0
            
            # Calculate harvest position near sheep
            angle = random.uniform(0, 2 * math.pi)
            radius = 10  # Close to sheep
            human.harvest_position = (
                nearest_sheep.x + nearest_sheep.width/2 + radius * math.cos(angle),
                nearest_sheep.y + nearest_sheep.height/2 + radius * math.sin(angle)
            )
            
            # Find wool shed (if available)
            from systems.resource_system import ResourceType
            for wool_shed in game_state.wool_shed_list:
                if wool_shed.can_accept_resource():
                    human.target_building = wool_shed
                    human.resource_type = ResourceType.WOOL
                    break
    
    def _shear_sheep(self, human, dt, game_state):
        """Shear the assigned sheep"""
        # Use harvest_target if available, otherwise fall back to work_target
        sheep = human.harvest_target if human.harvest_target else human.work_target
        
        if not sheep:
            # No sheep assigned - reset and find new one
            self._reset_worker(human)
            return
        
        # Restore harvest_target if it was cleared but work_target exists
        if not human.harvest_target and human.work_target:
            human.harvest_target = human.work_target
        
        # Check if sheep still has wool
        if not sheep.has_wool:
            # Sheep already sheared, find new one
            human.work_target = None
            human.harvest_target = None
            human.harvest_position = None
            return
        
        # Calculate harvest position if not set
        if not human.harvest_position:
            angle = random.uniform(0, 2 * math.pi)
            radius = 10
            human.harvest_position = (
                sheep.x + sheep.width/2 + radius * math.cos(angle),
                sheep.y + sheep.height/2 + radius * math.sin(angle)
            )
        
        # Move to shear position
        target_x = human.harvest_position[0] if human.harvest_position else sheep.x + sheep.width/2
        target_y = human.harvest_position[1] if human.harvest_position else sheep.y + sheep.height/2
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 5:  # Not at shear position yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At shear position, shear the sheep (1-2 seconds)
            human.harvest_timer += dt
            
            # Shear time is 1-2 seconds (use 1.5 seconds average)
            shear_time = 1.5
            if human.harvest_timer >= shear_time:
                # Finished shearing
                sheep.has_wool = False
                sheep.wool_regrowth_day = game_state.current_day  # Track when sheared
                human.harvest_timer = 0.0
                human.carrying_resource = True
    
    def _return_to_wool_shed(self, human, game_state):
        """Return to wool shed to deposit wool"""
        from entities.woolshed import WoolShed
        
        building = human.target_building
        
        # Validate that building is actually a wool shed
        if not building or not isinstance(building, WoolShed):
            # Find a valid wool shed
            for wool_shed in game_state.wool_shed_list:
                if wool_shed.can_accept_resource():
                    building = wool_shed
                    human.target_building = wool_shed
                    break
            
            if not building or not isinstance(building, WoolShed):
                # No valid wool shed - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            building.x + building.width/2,
            building.y + building.height/2
        )
        
        if dist > 20:  # Not at building yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            building_x = building.x + building.width/2
            building_y = building.y + building.height/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, building_x, building_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At building, deposit resource
            from systems.resource_system import ResourceType
            if building.add_wool():
                self.resource_system.add_resource(ResourceType.WOOL, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                
                # Continue working - find next unsheared sheep
                human.work_target = None
                human.harvest_target = None
                human.harvest_position = None
            else:
                # Building full - stop working
                self._reset_worker(human)
    
    def _update_barleyfarmer(self, human, dt, game_state):
        """Update a barley farmer - works in farm, waits for crops, then harvests"""
        # Check if work is available
        has_farm_work = False
        for farm in game_state.barley_farm_list:
            if farm.has_crops and farm.has_any_barley_to_harvest():
                has_farm_work = True
                break
            total_plots = farm.plots_x * farm.plots_y
            if len(farm.worked_plots) < total_plots:
                has_farm_work = True
                break
        has_space = any(silo.can_accept_resource() for silo in game_state.silo_list)
        if not has_farm_work or not has_space:
            self._enter_downtime(human, game_state)
            return
        
        # If carrying resource, return to silo
        if human.carrying_resource:
            self._return_to_silo(human, game_state)
            return
        
        # Find assigned farm (stored in work_target)
        farm = human.work_target
        
        # If no farm assigned, find one
        if not farm or not hasattr(farm, 'planted_day'):
            self._find_farm(human, game_state)
            return
        
        # Check if crops are ready to harvest
        if farm.has_crops and farm.has_any_barley_to_harvest():
            # Move to farm and harvest one barley at a time
            self._harvest_barley_one_by_one(human, dt, game_state, farm)
            return
        
        # Check if all barley has been harvested - reset farm
        if farm.is_fully_harvested():
            farm.reset_after_harvest()
            return
        
        # Work plots in farm (moves between plots, works each for 3 seconds)
        self._work_in_farm(human, dt, farm, game_state)
        
        # If all plots are worked and crops not planted yet, plant them
        total_plots = farm.plots_x * farm.plots_y
        if len(farm.worked_plots) >= total_plots and farm.planted_day is None:
            farm.plant_crops(game_state.current_day)
    
    def _find_farm(self, human, game_state):
        """Find a barley farm for the farmer"""
        nearest_farm = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for farm in game_state.barley_farm_list:
            # Check if farm already has a farmer assigned
            has_farmer = any(
                h.work_target == farm and h.job == "barleyfarmer" 
                for h in game_state.human_list 
                if h.is_employed and h != human
            )
            if has_farmer:
                continue  # Farm already has a farmer
            
            # Calculate distance to farm center
            farm_center_x = farm.x + farm.width / 2
            farm_center_y = farm.y + farm.height / 2
            dist = distance(human_x, human_y, farm_center_x, farm_center_y)
            
            # No distance limit - farmer can work at any distance
            if dist < nearest_dist:
                # Check if there's a silo to deposit in
                if len(game_state.silo_list) > 0:
                    nearest_farm = farm
                    nearest_dist = dist
        
        if nearest_farm:
            human.work_target = nearest_farm
            # Find silo
            from systems.resource_system import ResourceType
            for silo in game_state.silo_list:
                if silo.can_accept_resource():
                    human.target_building = silo
                    human.resource_type = ResourceType.BARLEY
                    break
    
    def _work_in_farm(self, human, dt, farm, game_state):
        """Farmer works plots in farm - moves to next unworked plot, works for 3 seconds"""
        # Initialize current plot if not set
        if not hasattr(human, 'current_plot_x') or human.current_plot_x is None:
            # Find first unworked plot
            found_plot = False
            for plot_y in range(farm.plots_y):
                for plot_x in range(farm.plots_x):
                    if not farm.is_plot_worked(plot_x, plot_y):
                        human.current_plot_x = plot_x
                        human.current_plot_y = plot_y
                        human.plot_work_timer = 0.0
                        found_plot = True
                        break
                if found_plot:
                    break
            
            if not found_plot:
                # All plots worked - plant crops if not already planted
                if farm.planted_day is None:
                    farm.plant_crops(game_state.current_day)
                return
        
        # Check if current plot is already worked, find next unworked plot
        if farm.is_plot_worked(human.current_plot_x, human.current_plot_y):
            # Find next unworked plot
            found_plot = False
            for plot_y in range(farm.plots_y):
                for plot_x in range(farm.plots_x):
                    if not farm.is_plot_worked(plot_x, plot_y):
                        human.current_plot_x = plot_x
                        human.current_plot_y = plot_y
                        human.plot_work_timer = 0.0
                        found_plot = True
                        break
                if found_plot:
                    break
            
            if not found_plot:
                # All plots worked - plant crops if not already planted
                if farm.planted_day is None:
                    farm.plant_crops(game_state.current_day)
                return
        
        # Get target position for current plot (center of plot)
        target_x, target_y = farm.get_plot_position(human.current_plot_x, human.current_plot_y)
        
        # Move to plot position
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 3:  # Not at plot center yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At plot center - work for 3 seconds
            human.plot_work_timer += dt
            
            if human.plot_work_timer >= 3.0:
                # Finished working this plot - mark it as worked
                farm.work_plot(human.current_plot_x, human.current_plot_y)
                human.plot_work_timer = 0.0
                # Move to next plot (will be found on next update)
                human.current_plot_x = None
                human.current_plot_y = None
    
    def _harvest_barley_one_by_one(self, human, dt, game_state, farm):
        """Harvest barley from the farm one plot at a time"""
        # Initialize harvest plot if not set
        if not hasattr(human, 'harvest_plot_x') or human.harvest_plot_x is None:
            # Find first plot with barley
            found_plot = False
            for plot_y in range(farm.plots_y):
                for plot_x in range(farm.plots_x):
                    if farm.has_barley_at_plot(plot_x, plot_y):
                        human.harvest_plot_x = plot_x
                        human.harvest_plot_y = plot_y
                        human.harvest_timer = 0.0
                        found_plot = True
                        break
                if found_plot:
                    break
            
            if not found_plot:
                # No more barley to harvest - reset farm
                farm.reset_after_harvest()
                return
        
        # Get target position for current harvest plot (center of plot)
        target_x, target_y = farm.get_plot_position(human.harvest_plot_x, human.harvest_plot_y)
        
        # Move to plot position
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            target_x,
            target_y
        )
        
        if dist > 3:  # Not at plot center yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, target_x, target_y, game_state, human.previous_road
            )
            
            # Update previous_road tracking - only update if we've clearly transitioned
            from utils.pathfinding import is_on_road
            from utils.geometry import distance
            import pygame
            current_road = is_on_road(current_x, current_y, game_state, preferred_road=human.previous_road)
            # Only update if we've clearly moved to a different road
            if current_road and current_road != human.previous_road:
                # Check distance to center of new road to confirm transition
                current_rect = pygame.Rect(current_road.x, current_road.y,
                                          current_road.width, current_road.height)
                dist_to_new_road_center = distance(current_x, current_y, 
                                                   current_rect.centerx, current_rect.centery)
                # Only switch if we're closer to the center of the new road than old road
                if human.previous_road:
                    old_rect = pygame.Rect(human.previous_road.x, human.previous_road.y,
                                          human.previous_road.width, human.previous_road.height)
                    dist_to_old_road_center = distance(current_x, current_y,
                                                      old_rect.centerx, old_rect.centery)
                    if dist_to_new_road_center < dist_to_old_road_center:
                        human.previous_road = current_road
                else:
                    human.previous_road = current_road
            elif not current_road:
                # Not on any road - clear previous
                human.previous_road = None
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                # Simple collision check
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At plot center - harvest one unit (takes a moment)
            human.harvest_timer += dt
            
            harvest_time = 1.0  # 1 second to harvest one unit
            if human.harvest_timer >= harvest_time:
                # Finished harvesting this plot - get 1 unit
                if farm.harvest_one_barley(human.harvest_plot_x, human.harvest_plot_y):
                    human.harvest_timer = 0.0
                    human.carrying_resource = True
                    human.barley_amount = 1  # Carrying 1 unit
                    # Clear harvest plot so we can find next one after depositing
                    human.harvest_plot_x = None
                    human.harvest_plot_y = None
                else:
                    # This plot doesn't have barley anymore, find next one
                    human.harvest_plot_x = None
                    human.harvest_plot_y = None
                    human.harvest_timer = 0.0
    
    def _return_to_silo(self, human, game_state):
        """Return to silo to deposit barley"""
        from entities.silo import Silo
        from constants import BARLEY_HARVEST_AMOUNT
        from systems.resource_system import ResourceType
        
        building = human.target_building
        
        # Validate that building is actually a silo
        if not building or not isinstance(building, Silo):
            # Find a valid silo
            for silo in game_state.silo_list:
                if silo.can_accept_resource():
                    building = silo
                    human.target_building = silo
                    break
            
            if not building or not isinstance(building, Silo):
                # No valid silo - reset worker
                self._reset_worker(human)
                return
        
        # Move to building
        silo_center_x = building.x + building.radius
        silo_center_y = building.y + building.radius
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            silo_center_x,
            silo_center_y
        )
        
        if dist > 30:  # Not at silo yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, silo_center_x, silo_center_y, game_state
            )
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
            
            # Keep within playable area bounds
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At silo, deposit one barley unit
            if building.add_barley():
                self.resource_system.add_resource(ResourceType.BARLEY, 1)
                human.carrying_resource = False
                human.harvest_timer = 0.0
                if hasattr(human, 'barley_amount'):
                    delattr(human, 'barley_amount')
                
                # Continue working - go back to farm to harvest next plot
                # harvest_plot_x/y will be None, so it will find next plot with barley
            else:
                # Silo full - stop working
                self._reset_worker(human)
    
    def _update_miller(self, human, dt, game_state):
        """Update a miller - collects barley from silos and brings to mill"""
        # Check if work is available
        has_barley = any(silo.barley_count > 0 for silo in game_state.silo_list)
        mill = human.work_target
        if not mill or not hasattr(mill, 'millstone_radius'):
            # Find a mill if not assigned
            for m in game_state.mill_list:
                mill = m
                break
        has_space = (mill is not None and 
                    mill.can_accept_flour() and 
                    mill.can_accept_malt())
        if not has_barley or not has_space:
            self._enter_downtime(human, game_state)
            return
        
        # If no mill assigned, find one
        if not mill or not hasattr(mill, 'millstone_radius'):
            self._find_mill(human, game_state)
            return
        
        # If carrying barley, deliver to mill
        if human.carrying_resource and hasattr(human, 'carrying_barley') and human.carrying_barley:
            self._deliver_barley_to_mill(human, dt, mill, game_state)
            return
        
        # Otherwise, find barley in silos and collect it
        self._collect_barley_from_silo(human, dt, game_state, mill)
    
    def _find_mill(self, human, game_state):
        """Find a mill for the miller"""
        nearest_mill = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for mill in game_state.mill_list:
            # Check if mill already has a miller assigned
            has_miller = any(
                h.work_target == mill and h.job == "miller" 
                for h in game_state.human_list 
                if h.is_employed and h != human
            )
            if has_miller:
                continue  # Mill already has a miller
            
            # Calculate distance to mill center
            mill_center_x = mill.x + mill.width / 2
            mill_center_y = mill.y + mill.height / 2
            dist = distance(human_x, human_y, mill_center_x, mill_center_y)
            
            # No distance limit - miller can work at any distance
            if dist < nearest_dist:
                nearest_mill = mill
                nearest_dist = dist
        
        if nearest_mill:
            human.work_target = nearest_mill
    
    def _collect_barley_from_silo(self, human, dt, game_state, mill):
        """Miller collects barley from silos"""
        from systems.resource_system import ResourceType
        
        # Find silo with barley
        target_silo = None
        nearest_dist = float('inf')
        
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for silo in game_state.silo_list:
            if silo.barley_count > 0:
                silo_center_x = silo.x + silo.radius
                silo_center_y = silo.y + silo.radius
                dist = distance(human_x, human_y, silo_center_x, silo_center_y)
                
                if dist < nearest_dist:
                    target_silo = silo
                    nearest_dist = dist
        
        if not target_silo:
            # No barley available - just wander around mill
            self._wander_in_mill(human, dt, mill, game_state)
            return
        
        # Move to silo
        silo_center_x = target_silo.x + target_silo.radius
        silo_center_y = target_silo.y + target_silo.radius
        
        dist = distance(human_x, human_y, silo_center_x, silo_center_y)
        
        if dist > 10:  # Not close enough yet
            # Use pathfinding to get target position (may route through roads if blocked)
            path_target_x, path_target_y = get_road_path_target(
                human_x, human_y, silo_center_x, silo_center_y, game_state
            )
            
            # Move towards pathfinding target
            path_dist = distance(human_x, human_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - human_x
                dy = path_target_y - human_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
            
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
            human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
            
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
        else:
            # At silo - collect barley
            if target_silo.barley_count > 0:
                target_silo.barley_count -= 1
                self.resource_system.remove_resource(ResourceType.BARLEY, 1)
                human.carrying_resource = True
                human.carrying_barley = True
                human.resource_type = ResourceType.BARLEY
    
    def _deliver_barley_to_mill(self, human, dt, mill, game_state):
        """Miller delivers barley to mill and places on millstone"""
        # Move to millstone center
        millstone_center_x = mill.millstone_center_x
        millstone_center_y = mill.millstone_center_y
        
        dist = distance(
            human.x + human.size/2,
            human.y + human.size/2,
            millstone_center_x,
            millstone_center_y
        )
        
        if dist > 10:  # Not at millstone yet
            # Use pathfinding to get target position (may route through roads if blocked)
            from utils.geometry import clamp
            from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
            
            current_x = human.x + human.size/2
            current_y = human.y + human.size/2
            path_target_x, path_target_y = get_road_path_target(
                current_x, current_y, millstone_center_x, millstone_center_y, game_state
            )
            
            # Move towards pathfinding target
            path_dist = distance(current_x, current_y, path_target_x, path_target_y)
            if path_dist > 0:
                dx = path_target_x - current_x
                dy = path_target_y - current_y
                dx = (dx / path_dist) * human.speed
                dy = (dy / path_dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                # Keep within playable area bounds
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # At millstone - place barley
            if mill.add_barley():
                human.carrying_resource = False
                human.carrying_barley = False
                human.resource_type = None
    
    def _wander_in_mill(self, human, dt, mill, game_state):
        """Miller wanders around inside mill when not working"""
        import random
        
        # Keep miller within mill bounds
        mill_left = mill.x
        mill_right = mill.x + mill.width
        mill_top = mill.y
        mill_bottom = mill.y + mill.height
        
        margin = human.size / 2
        min_x = mill_left + margin
        max_x = mill_right - margin
        min_y = mill_top + margin
        max_y = mill_bottom - margin
        
        # Random movement inside mill (simple wander)
        if not hasattr(human, 'mill_wander_timer') or human.mill_wander_timer <= 0:
            # Pick new random target within mill
            human.mill_target_x = random.uniform(min_x, max_x - human.size)
            human.mill_target_y = random.uniform(min_y, max_y - human.size)
            human.mill_wander_timer = random.uniform(2.0, 4.0)  # Wander for 2-4 seconds
        
        human.mill_wander_timer -= dt
        
        # Move towards target
        target_x = human.mill_target_x if hasattr(human, 'mill_target_x') else human.x
        target_y = human.mill_target_y if hasattr(human, 'mill_target_y') else human.y
        
        dist = distance(human.x + human.size/2, human.y + human.size/2, target_x + human.size/2, target_y + human.size/2)
        
        if dist > 5:
            dx = target_x - human.x
            dy = target_y - human.y
            dx = (dx / max(dist, 0.1)) * human.speed * 0.5  # Slower movement inside mill
            dy = (dy / max(dist, 0.1)) * human.speed * 0.5
            
            old_x, old_y = human.x, human.y
            human.x += dx
            human.y += dy
            
            # Clamp to mill bounds
            from utils.geometry import clamp
            human.x = clamp(human.x, min_x, max_x - human.size)
            human.y = clamp(human.y, min_y, max_y - human.size)
            
            # Simple collision check
            if self._check_collisions(human, game_state):
                human.x, human.y = old_x, old_y
    
    def _reset_worker(self, human):
        """Reset worker state"""
        human.work_target = None
        human.harvest_target = None
        human.carrying_resource = False
        human.target_building = None
        human.resource_type = None
        human.harvest_position = None
        human.harvest_timer = 0.0
    
    def _enter_downtime(self, human, game_state):
        """Enter downtime mode - go to town hall and walk around"""
        # Find nearest town hall
        nearest_townhall = None
        nearest_dist = float('inf')
        human_x = human.x + human.size/2
        human_y = human.y + human.size/2
        
        for townhall in game_state.townhall_list:
            townhall_center_x = townhall.x + townhall.width / 2
            townhall_center_y = townhall.y + townhall.height / 2
            dist = distance(human_x, human_y, townhall_center_x, townhall_center_y)
            if dist < nearest_dist:
                nearest_townhall = townhall
                nearest_dist = dist
        
        if nearest_townhall:
            human.is_downtime = True
            human.downtime_townhall = nearest_townhall
            human.downtime_wander_timer = 0.0
            human.downtime_target_x = None
            human.downtime_target_y = None
            # Reset work state
            self._reset_worker(human)
    
    def _update_downtime(self, human, dt, game_state):
        """Update downtime behavior - walk around randomly inside town hall"""
        townhall = human.downtime_townhall
        
        # Check if work is available again
        if self._check_work_available(human, game_state):
            human.is_downtime = False
            human.downtime_townhall = None
            return
        
        if not townhall:
            # No town hall found, exit downtime
            human.is_downtime = False
            return
        
        # Check if inside town hall
        human_center_x = human.x + human.size/2
        human_center_y = human.y + human.size/2
        is_inside = (townhall.x < human_center_x < townhall.x + townhall.width and
                    townhall.y < human_center_y < townhall.y + townhall.height)
        
        if not is_inside:
            # Move towards town hall center
            townhall_center_x = townhall.x + townhall.width / 2
            townhall_center_y = townhall.y + townhall.height / 2
            
            dist = distance(human_center_x, human_center_y, townhall_center_x, townhall_center_y)
            if dist > 5:
                dx = townhall_center_x - human_center_x
                dy = townhall_center_y - human_center_y
                dx = (dx / dist) * human.speed
                dy = (dy / dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                from utils.geometry import clamp
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
        else:
            # Inside town hall - wander around randomly
            if human.downtime_target_x is None or human.downtime_wander_timer >= 3.0:
                # Pick new random position inside town hall
                margin = 10  # Stay away from edges
                human.downtime_target_x = random.uniform(
                    townhall.x + margin, 
                    townhall.x + townhall.width - margin - human.size
                )
                human.downtime_target_y = random.uniform(
                    townhall.y + margin, 
                    townhall.y + townhall.height - margin - human.size
                )
                human.downtime_wander_timer = 0.0
            
            # Move towards target
            dist = distance(
                human.x + human.size/2, 
                human.y + human.size/2,
                human.downtime_target_x + human.size/2,
                human.downtime_target_y + human.size/2
            )
            
            if dist > 5:
                dx = human.downtime_target_x - human.x
                dy = human.downtime_target_y - human.y
                dx = (dx / dist) * human.speed
                dy = (dy / dist) * human.speed
                
                old_x, old_y = human.x, human.y
                human.x += dx
                human.y += dy
                
                from utils.geometry import clamp
                from constants import PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM, SCREEN_WIDTH
                human.x = clamp(human.x, 0, SCREEN_WIDTH - human.size)
                human.y = clamp(human.y, PLAYABLE_AREA_TOP, PLAYABLE_AREA_BOTTOM - human.size)
                
                if self._check_collisions(human, game_state):
                    human.x, human.y = old_x, old_y
            else:
                # Reached target, stop for a moment
                human.downtime_wander_timer += dt
    
    def _check_work_available(self, human, game_state):
        """Check if work is available for the worker"""
        if human.job == "lumberjack":
            # Check if there are trees and lumberyards with space
            has_trees = any(not tree.is_depleted() for tree in game_state.tree_list)
            has_space = any(ly.can_accept_resource() for ly in game_state.lumber_yard_list)
            return has_trees and has_space
        
        elif human.job == "stoneworker":
            # Check if there are rocks and stone yards with space
            has_rocks = any(not rock.is_depleted() for rock in game_state.rock_list)
            has_space = any(sy.can_accept_resource() for sy in game_state.stone_yard_list)
            return has_rocks and has_space
        
        elif human.job == "miner":
            # Check if there are iron mines and iron yards with space
            has_mines = any(not mine.is_depleted() for mine in game_state.iron_mine_list)
            has_space = any(iy.can_accept_resource() for iy in game_state.iron_yard_list)
            return has_mines and has_space
        
        elif human.job == "miller":
            # Check if there's barley available and mill has space
            has_barley = any(silo.barley_count > 0 for silo in game_state.silo_list)
            mill = human.work_target
            if not mill or not hasattr(mill, 'can_accept_flour'):
                # Find a mill if not assigned
                for m in game_state.mill_list:
                    mill = m
                    break
            has_space = (mill is not None and 
                        mill.can_accept_flour() and 
                        mill.can_accept_malt())
            return has_barley and has_space
        
        elif human.job == "barleyfarmer":
            # Check if there's a farm with crops or work to do, and silo has space
            has_farm_work = False
            for farm in game_state.barley_farm_list:
                # Check if farm has barley to harvest or plots to work
                if farm.has_crops and farm.has_any_barley_to_harvest():
                    has_farm_work = True
                    break
                # Check if farm has unworked plots
                total_plots = farm.plots_x * farm.plots_y
                if len(farm.worked_plots) < total_plots:
                    has_farm_work = True
                    break
            has_space = any(silo.can_accept_resource() for silo in game_state.silo_list)
            return has_farm_work and has_space
        
        elif human.job == "shearer":
            # Check if there are sheep with wool and wool shed has space
            has_sheep = any(sheep.has_wool for sheep in game_state.sheep_list)
            has_space = any(ws.can_accept_resource() for ws in game_state.wool_shed_list)
            return has_sheep and has_space
        
        return True  # Default: work available
    
    def _check_collisions(self, human, game_state):
        """Simple collision check for employed workers"""
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
        # Salt yards are passable - no collision check needed
        for wool_shed in game_state.wool_shed_list:
            if wool_shed.check_collision_player(human.x, human.y):
                return True
        for silo in game_state.silo_list:
            if silo.check_collision_player(human.x, human.y):
                return True
        return False
